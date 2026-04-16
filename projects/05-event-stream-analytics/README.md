# Event Stream Analytics

Local-first event-driven analytics case study built on the official Wikimedia EventStreams
RecentChange stream. The focus is broker-backed ingestion, producer and consumer separation, raw
event landing, readable local checkpoints, and replayable analytical summaries.

This is the fifth portfolio case in the repository. It is intentionally not a dashboard project,
not a read API project, not a dbt project, and not a cloud streaming platform claim. The goal is
to prove practical streaming and event-pipeline thinking in a way that stays inspectable and
reproducible on a local machine.

## What To Review First

Start here if you are evaluating the project quickly:

1. `docs/architecture.md` - producer, broker, Bronze, Silver, Gold, and replay boundaries.
2. `docs/replay.md` - the difference between broker replay and offline replay from Bronze files.
3. `docs/checkpointing.md` - readable checkpoint artifacts and resume behavior.
4. `docs/local-run.md` - local run commands, including Windows PowerShell helpers.
5. `docs/validation.md` - what to inspect after a run without using a dashboard.
6. `src/jobs/` - small CLI entrypoints for publisher, Bronze consumer, Silver, Gold, replay, and validation.

The best code path to inspect is:

```text
src/jobs/run_publisher.py
src/jobs/run_bronze_consumer.py
src/jobs/run_silver.py
src/jobs/run_gold.py
src/jobs/run_replay.py
src/jobs/run_validation.py
```

## Evaluate In 5 Minutes

From the repository root on Windows PowerShell:

```powershell
.\projects\05-event-stream-analytics\scripts\start_broker.ps1
.\projects\05-event-stream-analytics\scripts\run_publisher.ps1 -MaxEvents 100 -MaxSeconds 60
.\projects\05-event-stream-analytics\scripts\run_bronze_consumer.ps1 -MaxEvents 100 -MaxSeconds 60
.\projects\05-event-stream-analytics\scripts\run_silver.ps1
.\projects\05-event-stream-analytics\scripts\run_gold.ps1
.\projects\05-event-stream-analytics\scripts\run_validation.ps1
```

Then inspect:

```text
projects/05-event-stream-analytics/data/bronze/state/publisher_checkpoint.json
projects/05-event-stream-analytics/data/bronze/state/bronze_state.json
projects/05-event-stream-analytics/data/bronze/raw/
projects/05-event-stream-analytics/data/silver/tables/recentchange_events/
projects/05-event-stream-analytics/data/gold/tables/
projects/05-event-stream-analytics/data/operations/latest_validation_run.json
```

Stop the broker when finished:

```powershell
.\projects\05-event-stream-analytics\scripts\stop_broker.ps1
```

## Key Streaming Insights

This case proves a different engineering story from the batch-first projects:

- event-driven ingestion from a public live stream;
- a local Redpanda broker boundary between source reading and raw landing;
- explicit producer and consumer responsibilities;
- bounded local runs through `--max-events` and `--max-seconds`;
- readable publisher and consumer checkpoint artifacts;
- Bronze raw landing as the durable local replay source;
- Silver and Gold rebuilds from landed events;
- clear duplicate-risk notes for broker replay;
- operational validation through local JSON metadata and filesystem inspection.

## Why This Case Exists

The first four portfolio projects already prove complementary patterns:

- `01-hospital-analytics`: local end-to-end analytics delivery, Bronze/Silver/Gold, PostgreSQL serving, API, dashboard.
- `02-job-market-analytics`: Python medallion processing, dbt on DuckDB and PostgreSQL, marts, API, dashboard.
- `03-retail-revenue-analytics`: multi-table source handling, source-aligned Silver, Gold KPI summaries, dimensional marts, API, dashboard, Docker-assisted demo packaging.
- `04-urban-mobility-analytics`: official public-source batch ingestion, month-based incremental design, partitioned Parquet outputs, state tracking, Prefect orchestration, local-first batch operations.

Project 05 complements them by staying focused on a local streaming, broker, checkpoint, and replay
case study.

## Source Choice

This project uses the official Wikimedia EventStreams `recentchange` stream:

- stream endpoint: `https://stream.wikimedia.org/v2/stream/recentchange`
- EventStreams documentation: `https://wikitech.wikimedia.org/wiki/EventStreams`
- RecentChange schema: `https://schema.wikimedia.org/repositories/primary/jsonschema/mediawiki/recentchange/latest.yaml`

This source is public, recognized, event-oriented by design, and naturally suited to streaming
ingestion patterns. It is meaningfully different from the batch-first sources used in projects 01
through 04.

## What Is Implemented Now

- Wikimedia RecentChange stream client with bounded local execution;
- Redpanda broker setup through Docker Compose;
- Python publisher that reads the public stream and publishes to a Kafka-compatible topic;
- Bronze consumer that lands raw broker events into local JSONL batches;
- readable checkpoint artifacts for publisher and Bronze consumer progress;
- Silver row-preserving standardization into partitioned Parquet;
- Gold category and minute-bucket summaries built from Silver with DuckDB;
- offline replay workflow that rebuilds Silver and Gold from landed Bronze events;
- lightweight validation manifest built from local run metadata and output files;
- Windows PowerShell wrappers for local broker, pipeline, replay, validation, and tests;
- lightweight tests for stable pure logic and checkpoint behavior;
- a small notebook for local sample validation.

## Architecture Flow

```text
Wikimedia EventStreams RecentChange
-> Python source client / publisher
-> Redpanda topic
-> Bronze raw landing consumer
-> Silver standardized event dataset
-> Gold category and minute-bucket summaries
-> Local JSON metadata, validation manifest, and checkpoint artifacts
```

## Project Positioning

This case is:

- local-first;
- event-driven;
- broker-backed;
- bounded for reproducibility;
- checkpoint-aware;
- replay-aware;
- portfolio-grade, but intentionally modest in operational claims.

This case is not:

- a dashboard build;
- a serving API;
- a dbt project;
- a cloud deployment;
- a Spark or Flink cluster;
- a production streaming platform claim.

## Broker Role

Redpanda provides the local message broker that decouples stream capture from raw landing:

- the publisher reads the public SSE stream and publishes events to `wikimedia.recentchange.raw`;
- the Bronze consumer reads from that topic and lands raw JSONL batches;
- the broker boundary makes producer and consumer responsibilities explicit;
- broker replay is possible only while topic retention still contains the relevant offsets;
- durable downstream rebuilds come from the landed Bronze files.

## Bronze, Silver, and Gold

### Bronze

Bronze lands raw broker-consumed events without inventing business semantics:

- one JSON object per line;
- source, broker, publisher, and consumer context preserved;
- readable batch metadata and consumer checkpoint files;
- bounded local runs using `--max-events` and `--max-seconds`.

### Silver

Silver standardizes one row per event:

- safe timestamp parsing from `meta.dt`;
- stable column names;
- event date and event hour partitions;
- bot, wiki, namespace, user, title, and event type fields preserved where present;
- Parquet outputs plus quality summaries.

### Gold

Gold rebuilds category and minute-bucket summaries from landed Silver Parquet:

- `minute_event_summary`
- `event_type_summary`
- `bot_vs_human_summary`
- `wiki_activity_summary`
- `namespace_activity_summary`

These are local analytical summary tables, not dashboard-serving marts.

## Replay Modes

Replay has two distinct meanings in this project.

### Broker Replay From Retained Offsets

Command:

```bash
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --replay --max-events 50
```

PowerShell:

```powershell
.\projects\05-event-stream-analytics\scripts\run_bronze_consumer.ps1 -Replay -MaxEvents 50
```

Broker replay tells the Bronze consumer to ignore the local Bronze checkpoint, seek to the
earliest retained Redpanda offsets, and land a new Bronze JSONL batch.

Duplicate risk exists here because broker replay does not delete or replace old Bronze files. If
you run broker replay more than once over the same retained topic history, you create multiple
Bronze batch files containing the same underlying events. Silver processes each Bronze batch as a
separate input, and Gold reads all Silver files under each `event_date=` partition, so duplicated
Bronze events can inflate downstream counts.

Use broker replay for local experimentation and offset-behavior demonstration.

### Offline Replay From Landed Bronze Files

Command:

```bash
python projects/05-event-stream-analytics/src/jobs/run_replay.py
```

PowerShell:

```powershell
.\projects\05-event-stream-analytics\scripts\run_replay.ps1
```

Offline replay rebuilds Silver and Gold from the Bronze JSONL files already on disk. It does not
read the live stream, does not consume from Redpanda, and does not create new Bronze batches.

This is the recommended safe rebuild path because it is reproducible after broker retention moves
on and uses the local raw landing layer as the durable source of truth.

## Safe Rebuild Path

For a normal downstream rebuild:

```powershell
.\projects\05-event-stream-analytics\scripts\run_replay.ps1
.\projects\05-event-stream-analytics\scripts\run_validation.ps1 -Mode offline_replay
```

For a clean rebuild after accidental duplicate broker replay, reset the generated local artifacts
that were affected, keep the `.gitkeep` files, and re-run from a known Bronze set. The project does
not claim automatic deduplication or exactly-once processing.

## Local Validation Examples

Build a compact validation manifest:

```powershell
.\projects\05-event-stream-analytics\scripts\run_validation.ps1
```

Inspect the latest validation file:

```text
projects/05-event-stream-analytics/data/operations/latest_validation_run.json
```

Useful local checks:

```powershell
Get-Content projects\05-event-stream-analytics\data\bronze\state\publisher_checkpoint.json
Get-Content projects\05-event-stream-analytics\data\bronze\state\bronze_state.json
Get-ChildItem projects\05-event-stream-analytics\data\bronze\raw -Recurse -Filter *.jsonl
Get-ChildItem projects\05-event-stream-analytics\data\silver\tables -Recurse -Filter *.parquet
Get-ChildItem projects\05-event-stream-analytics\data\gold\tables -Recurse -Filter *.parquet
Get-Content projects\05-event-stream-analytics\data\operations\latest_validation_run.json
```

Optional DuckDB inspection:

```powershell
python -c "import duckdb; print(duckdb.sql(\"select * from read_parquet('projects/05-event-stream-analytics/data/gold/tables/event_type_summary/*/*.parquet') limit 10\").df())"
```

## Environment Requirements

Create a project-compatible Python environment and install the project requirements:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r projects/05-event-stream-analytics/requirements.txt
```

Windows PowerShell activation:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r projects/05-event-stream-analytics/requirements.txt
```

Optional notebook kernel registration:

```bash
python -m ipykernel install --user --name event-stream-analytics --display-name "Event Stream Analytics"
```

## Local Broker Setup

Start Redpanda from the project directory:

```bash
cd projects/05-event-stream-analytics
docker compose up -d
docker compose ps
```

PowerShell wrapper from the repository root:

```powershell
.\projects\05-event-stream-analytics\scripts\start_broker.ps1
```

Stop it when finished:

```bash
cd projects/05-event-stream-analytics
docker compose down
```

PowerShell:

```powershell
.\projects\05-event-stream-analytics\scripts\stop_broker.ps1
```

## Local Run Commands

If your shell exposes only `python3`, use that interpreter with the same file paths.

Start the bounded publisher:

```bash
python projects/05-event-stream-analytics/src/jobs/run_publisher.py --max-events 100 --max-seconds 60
```

Land raw Bronze events from the broker:

```bash
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --max-events 100 --max-seconds 60
```

Standardize landed Bronze files into Silver:

```bash
python projects/05-event-stream-analytics/src/jobs/run_silver.py
```

Build Gold summaries from Silver:

```bash
python projects/05-event-stream-analytics/src/jobs/run_gold.py
```

Replay downstream layers from landed Bronze:

```bash
python projects/05-event-stream-analytics/src/jobs/run_replay.py
```

Build local validation metadata:

```bash
python projects/05-event-stream-analytics/src/jobs/run_validation.py
```

Run tests:

```bash
python -m pytest projects/05-event-stream-analytics/tests
```

## PowerShell Helper Scripts

From the repository root:

```powershell
.\projects\05-event-stream-analytics\scripts\start_broker.ps1
.\projects\05-event-stream-analytics\scripts\stop_broker.ps1
.\projects\05-event-stream-analytics\scripts\run_publisher.ps1 -MaxEvents 100 -MaxSeconds 60
.\projects\05-event-stream-analytics\scripts\run_bronze_consumer.ps1 -MaxEvents 100 -MaxSeconds 60
.\projects\05-event-stream-analytics\scripts\run_bronze_consumer.ps1 -Replay -MaxEvents 50
.\projects\05-event-stream-analytics\scripts\run_silver.ps1
.\projects\05-event-stream-analytics\scripts\run_gold.ps1
.\projects\05-event-stream-analytics\scripts\run_replay.ps1 -Target all
.\projects\05-event-stream-analytics\scripts\run_validation.ps1 -Mode normal
.\projects\05-event-stream-analytics\scripts\run_tests.ps1
```

## Local Storage Layout

```text
data/
|-- bronze/
|   |-- raw/
|   |   `-- stream_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.jsonl
|   |-- metadata/
|   `-- state/
|-- silver/
|   |-- tables/
|   |   `-- recentchange_events/event_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.parquet
|   |-- metadata/
|   `-- state/
|-- gold/
|   |-- tables/
|   |   |-- minute_event_summary/event_date=YYYY-MM-DD/minute_event_summary.parquet
|   |   |-- event_type_summary/event_date=YYYY-MM-DD/event_type_summary.parquet
|   |   |-- bot_vs_human_summary/event_date=YYYY-MM-DD/bot_vs_human_summary.parquet
|   |   |-- wiki_activity_summary/event_date=YYYY-MM-DD/wiki_activity_summary.parquet
|   |   `-- namespace_activity_summary/event_date=YYYY-MM-DD/namespace_activity_summary.parquet
|   |-- metadata/
|   `-- state/
`-- operations/
    `-- latest_validation_run.json
```

The generated runtime artifacts remain local and inspectable.

## Known Limitations / Replay Notes

- the live source is public internet infrastructure and can disconnect or slow down;
- broker replay depends on Redpanda topic retention and is not guaranteed forever;
- broker replay creates new Bronze files and can duplicate events if repeated over the same retained history;
- the durable rebuild story is offline replay from landed Bronze JSONL files;
- the publisher keeps a lightweight source checkpoint, but Bronze raw landing is the durable local replay source;
- there is no automatic cross-batch deduplication or exactly-once claim;
- the Gold layer is intentionally simple and local-first;
- this phase does not include a dashboard, API, authentication, dbt project, or cloud deployment.

## Future Directions

- richer stream filters and derived metrics;
- schema-evolution handling across source changes;
- richer partition management and retention controls;
- optional serving layer only if justified later;
- cloud streaming equivalents only as a future extension, not as a claim in this phase.
