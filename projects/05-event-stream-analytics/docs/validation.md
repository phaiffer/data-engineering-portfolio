# Local Validation

This project is intentionally reviewable without a dashboard. A reviewer should be able to inspect
the broker boundary, checkpoints, landed files, and summary outputs directly from the local
filesystem.

## Validation Command

After a local run, build a compact validation manifest:

```powershell
.\projects\05-event-stream-analytics\scripts\run_validation.ps1
```

Or run the Python entrypoint directly from the repository root:

```bash
python projects/05-event-stream-analytics/src/jobs/run_validation.py
```

The command writes:

```text
projects/05-event-stream-analytics/data/operations/latest_validation_run.json
```

This JSON file summarizes:

- validation timestamp;
- mode label: `normal`, `broker_replay`, or `offline_replay`;
- latest publisher events published;
- latest Bronze events consumed;
- Bronze JSONL batch count and row count;
- Silver Parquet file count and event dates;
- Gold summary table availability;
- checkpoint and state file paths;
- compact status: `no_bronze_batches`, `bronze_only`, `silver_ready`, or `gold_ready`.

## What To Inspect

### Publisher checkpoint

```text
data/bronze/state/publisher_checkpoint.json
```

Use this to confirm the publisher recorded the latest SSE event id and source metadata id.

### Bronze consumer checkpoint

```text
data/bronze/state/bronze_state.json
```

Use this to confirm the consumer stored the latest landed offset per topic partition and the
manifest of processed Bronze batches.

### Bronze raw landing

```text
data/bronze/raw/stream_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.jsonl
```

Open a JSONL file and verify that each line preserves broker context, consumer context, publisher
context, and the raw Wikimedia payload.

### Silver outputs

```text
data/silver/tables/recentchange_events/event_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.parquet
data/silver/state/silver_state.json
data/silver/metadata/silver_batch_YYYYMMDDTHHMMSSZ.json
```

Use these files to validate that landed Bronze batches were standardized into one row per event and
partitioned by event date.

### Gold outputs

```text
data/gold/tables/minute_event_summary/event_date=YYYY-MM-DD/minute_event_summary.parquet
data/gold/tables/event_type_summary/event_date=YYYY-MM-DD/event_type_summary.parquet
data/gold/tables/bot_vs_human_summary/event_date=YYYY-MM-DD/bot_vs_human_summary.parquet
data/gold/tables/wiki_activity_summary/event_date=YYYY-MM-DD/wiki_activity_summary.parquet
data/gold/tables/namespace_activity_summary/event_date=YYYY-MM-DD/namespace_activity_summary.parquet
```

Gold is a local analytical summary layer. It is useful for validating stream-derived metrics, not
for dashboard serving.

## Optional Parquet Inspection

DuckDB can read the local Parquet files directly:

```powershell
python -c "import duckdb; print(duckdb.sql(\"select * from read_parquet('projects/05-event-stream-analytics/data/gold/tables/event_type_summary/*/*.parquet') limit 10\").df())"
```

Use the same pattern for Silver:

```powershell
python -c "import duckdb; print(duckdb.sql(\"select event_date, wiki, event_type, count(*) as events from read_parquet('projects/05-event-stream-analytics/data/silver/tables/recentchange_events/*/*.parquet') group by 1,2,3 order by events desc limit 10\").df())"
```

## Screenshot Guidance

Useful portfolio screenshots are simple filesystem or terminal captures:

- `docker compose ps` showing Redpanda running locally;
- `publisher_checkpoint.json` with the latest SSE event id;
- `bronze_state.json` with topic partition offsets;
- a Bronze JSONL file open in an editor;
- partitioned Silver Parquet folders;
- Gold summary table folders;
- `latest_validation_run.json` after a full local run.

Avoid presenting this project as a dashboard. The validation surface is the event pipeline itself:
broker, checkpoints, landed events, replayable outputs, and metadata.
