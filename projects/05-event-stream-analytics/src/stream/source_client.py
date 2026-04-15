from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Iterator

import requests

from config import get_settings
from stream.checkpoints import should_stop_bounded_run, utc_now


@dataclass(frozen=True)
class SourceEvent:
    """Represent one streamed SSE event and its decoded payload."""

    event_name: str
    event_id: str | None
    payload: dict


@dataclass(frozen=True)
class RawSSEMessage:
    """Represent one parsed SSE message before payload decoding."""

    event_name: str
    event_id: str | None
    data: str


def parse_sse_lines(lines: Iterator[str]) -> Iterator[RawSSEMessage]:
    """Parse raw SSE lines into messages."""
    event_name = "message"
    event_id: str | None = None
    data_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\r")

        if line == "":
            if data_lines:
                yield RawSSEMessage(
                    event_name=event_name,
                    event_id=event_id,
                    data="\n".join(data_lines),
                )
            event_name = "message"
            event_id = None
            data_lines = []
            continue

        if line.startswith(":"):
            continue

        field, _, raw_value = line.partition(":")
        value = raw_value.lstrip(" ")

        if field == "event":
            event_name = value or "message"
        elif field == "id":
            event_id = value or None
        elif field == "data":
            data_lines.append(value)

    if data_lines:
        yield RawSSEMessage(event_name=event_name, event_id=event_id, data="\n".join(data_lines))


class WikimediaSourceClient:
    """Read bounded samples from the Wikimedia EventStreams RecentChange source."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def stream_recent_changes(
        self,
        *,
        max_seconds: int | None,
        last_event_id: str | None = None,
    ) -> Iterator[SourceEvent]:
        """Yield decoded recentchange events until the bounded run ends."""
        started_at = utc_now()
        current_last_event_id = last_event_id
        consecutive_failures = 0

        while True:
            stop_reason = should_stop_bounded_run(
                started_at=started_at,
                now=utc_now(),
                processed_count=0,
                max_events=None,
                max_seconds=max_seconds,
            )
            if stop_reason:
                break

            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "User-Agent": "phaiffer-data-engineering-portfolio-event-stream-analytics/1.0",
            }
            if current_last_event_id:
                headers["Last-Event-ID"] = current_last_event_id

            try:
                with requests.get(
                    self.settings.source_stream_url,
                    headers=headers,
                    stream=True,
                    timeout=(
                        self.settings.http_connect_timeout_seconds,
                        self.settings.http_read_timeout_seconds,
                    ),
                ) as response:
                    response.raise_for_status()
                    consecutive_failures = 0

                    for message in parse_sse_lines(response.iter_lines(decode_unicode=True)):
                        current_last_event_id = message.event_id or current_last_event_id
                        if message.event_name != "message" or not message.data:
                            continue

                        payload = json.loads(message.data)
                        yield SourceEvent(
                            event_name=message.event_name,
                            event_id=message.event_id,
                            payload=payload,
                        )

                        stop_reason = should_stop_bounded_run(
                            started_at=started_at,
                            now=utc_now(),
                            processed_count=0,
                            max_events=None,
                            max_seconds=max_seconds,
                        )
                        if stop_reason:
                            return

            except (requests.RequestException, json.JSONDecodeError) as exc:
                consecutive_failures += 1
                if max_seconds is None and consecutive_failures >= 3:
                    raise RuntimeError("Failed to keep the Wikimedia stream connection open.") from exc

                if max_seconds is not None:
                    stop_reason = should_stop_bounded_run(
                        started_at=started_at,
                        now=utc_now(),
                        processed_count=0,
                        max_events=None,
                        max_seconds=max_seconds,
                    )
                    if stop_reason:
                        break

                time.sleep(self.settings.stream_reconnect_seconds)
