from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

import requests


@dataclass(frozen=True)
class DownloadResult:
    """Represent the outcome of one downloaded source artifact."""

    output_path: str
    downloaded_bytes: int
    sha256: str
    downloaded_at_utc: str
    content_length: int | None = None
    etag: str | None = None
    last_modified: str | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        """Return a serializable version of the result."""
        return asdict(self)


def fetch_remote_metadata(url: str, *, timeout_seconds: int) -> dict[str, str | int | None]:
    """Fetch lightweight remote metadata for an official source file."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException:
        return {
            "content_length": None,
            "etag": None,
            "last_modified": None,
        }

    content_length = response.headers.get("Content-Length")
    return {
        "content_length": int(content_length) if content_length else None,
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }


def download_file(
    *,
    url: str,
    output_path: Path,
    timeout_seconds: int,
    chunk_size_bytes: int,
    downloaded_at_utc: str,
) -> DownloadResult:
    """Download a file with streaming I/O and a deterministic local checksum."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.part")

    sha256 = hashlib.sha256()
    downloaded_bytes = 0

    with requests.get(url, stream=True, timeout=timeout_seconds) as response:
        response.raise_for_status()

        with temporary_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=chunk_size_bytes):
                if not chunk:
                    continue

                handle.write(chunk)
                sha256.update(chunk)
                downloaded_bytes += len(chunk)

        content_length = response.headers.get("Content-Length")
        result = DownloadResult(
            output_path=str(output_path),
            downloaded_bytes=downloaded_bytes,
            sha256=sha256.hexdigest(),
            downloaded_at_utc=downloaded_at_utc,
            content_length=int(content_length) if content_length else None,
            etag=response.headers.get("ETag"),
            last_modified=response.headers.get("Last-Modified"),
        )

    temporary_path.replace(output_path)
    return result
