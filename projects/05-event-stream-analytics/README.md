# Event Stream Analytics

Local-first event-driven analytics case study built on the official Wikimedia EventStreams RecentChange stream, with a focus on broker-backed ingestion, producer and consumer separation, raw event landing, readable local checkpoints, and replayable analytical summaries.

This is the fifth portfolio case in the repository. It is intentionally not a dashboard project, not a read API project, and not a claim of production-grade streaming infrastructure. The goal is to prove practical streaming and event-pipeline thinking in a way that stays inspectable and reproducible on a local machine.

## Why This Case Exists

The first four portfolio projects already prove several complementary patterns:

- `01-hospital-analytics`: local end-to-end analytics delivery, Bronze/Silver/Gold, PostgreSQL serving, API, dashboard.
- `02-job-market-analytics`: Python medallion processing, DBT on DuckDB and PostgreSQL, marts, API, dashboard.
- `03-retail-revenue-analytics`: multi-table source handling, source-aligned Silver, Gold KPI summaries, dimensional marts, API, dashboard, Docker-assisted demo packaging.
- `04-urban-mobility-analytics`: official public-source batch ingestion, month-based incremental design, partitioned Parquet outputs, state tracking, Prefect orchestration, local-first batch operations.

This fifth case complements them by proving a different engineering story:

- event-driven ingestion from a public live stream;
- message-broker-based decoupling between source reading and downstream consumption;
- explicit producer and consumer boundaries;
- raw event landing that supports downstream rebuilds;
- readable local checkpoint artifacts instead of hidden broker state only;
- replay-aware Silver and Gold rebuilding from landed Bronze events;
- first-pass category and minute-bucket analytical summaries over captured events.

## Source Choice

This project uses the official Wikimedia EventStreams `recentchange` stream:

- stream endpoint: `https://stream.wikimedia.org/v2/stream/recentchange`
- EventStreams documentation: `https://wikitech.wikimedia.org/wiki/EventStreams`
- RecentChange schema: `https://schema.wikimedia.org/repositories/primary/jsonschema/mediawiki/recentchange/latest.yaml`

This source is a strong fit because it is public, recognized, event-oriented by design, and naturally suited to streaming ingestion patterns. It is meaningfully different from the batch-first sources used in projects 01 through 04.

## What Is Implemented Now

- Wikimedia RecentChange stream client with bounded local execution;
- Redpanda broker setup through Docker Compose;
- Python publisher that reads the public stream and publishes to a Kafka-compatible topic;
- Bronze consumer that lands raw broker events into local JSONL batches;
- readable checkpoint artifacts for publisher and Bronze consumer progress;
- Silver row-preserving standardization into partitioned Parquet;
- Gold category and minute-bucket summaries built from Silver with DuckDB;
- replay workflow that rebuilds Silver and Gold from landed Bronze events;
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
-> Local JSON metadata and checkpoint artifacts
```

## Project Positioning

This case is:

- local-first;
- event-driven;
- bounded for reproducibility;
- checkpoint-aware;
- replay-aware;
- portfolio-grade, but intentionally modest in operational claims.

This case is not:

- a dashboard build;
- a serving API;
- a cloud deployment;
- a Spark or Flink cluster;
- a production streaming platform claim.

## Broker Role

Redpanda provides the local message broker that decouples stream capture from raw landing:

- the publisher reads the public SSE stream and publishes events to `wikimedia.recentchange.raw`;
- the Bronze consumer reads from that topic and lands raw JSONL batches;
- the broker boundary makes producer and consumer responsibilities explicit;
- replay can happen at two levels:
  - broker replay from retained topic history while offsets still exist;
  - offline replay from landed Bronze files, which is the more durable portfolio story in this project.

## Bronze, Silver, and Gold in This Project

### Bronze

Bronze lands raw broker-consumed events without inventing business semantics:

- one JSON object per line;
- source, broker, and payload context preserved;
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

Gold builds streaming-oriented summaries from Silver:

- `minute_event_summary`
- `event_type_summary`
- `bot_vs_human_summary`
- `wiki_activity_summary`
- `namespace_activity_summary`

These are local analytical summary tables, not dashboard-serving marts.

## Checkpointing and Replay

Checkpointing is a core part of the project:

- the publisher stores the latest SSE event id it successfully published;
- the Bronze consumer stores the latest landed topic offsets per partition in a readable JSON checkpoint;
- Silver stores processed Bronze batch manifests;
- Gold stores processed event-date manifests.

Replay has two distinct modes:

- `run_bronze_consumer.py --replay` ignores the local Bronze checkpoint and seeks to the earliest
  broker-retained offsets, landing a **new** Bronze batch. Running this more than once over the
  same retained broker history will create multiple Bronze batches for the same events, which can
  inflate Silver and Gold counts. Use this for local experimentation only.
- `run_replay.py` rebuilds Silver and Gold from already-landed Bronze JSONL files without
  reconnecting to the live stream or broker. This is idempotent and is the recommended rebuild
  story for this project because it stays reproducible even after broker retention moves on.

## Environment Requirements

Create a project-compatible Python environment and install the project requirements:

```bash
python -m venv .venv
source .venv/bin/activate
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

Stop it when finished:

```bash
docker compose down
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

Useful variants:

```bash
# force reprocess a Silver or Gold layer
python projects/05-event-stream-analytics/src/jobs/run_silver.py --force
python projects/05-event-stream-analytics/src/jobs/run_gold.py --force

# rebuild only Silver or only Gold from landed Bronze
python projects/05-event-stream-analytics/src/jobs/run_replay.py --target silver
python projects/05-event-stream-analytics/src/jobs/run_replay.py --target gold

# broker replay: seek earliest retained offsets and land a new Bronze batch
# note: creates a new batch file — see the Checkpointing and Replay section for the duplicate risk
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --replay --max-events 50
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
`-- gold/
    |-- tables/
    |   |-- minute_event_summary/event_date=YYYY-MM-DD/minute_event_summary.parquet
    |   |-- event_type_summary/event_date=YYYY-MM-DD/event_type_summary.parquet
    |   |-- bot_vs_human_summary/event_date=YYYY-MM-DD/bot_vs_human_summary.parquet
    |   |-- wiki_activity_summary/event_date=YYYY-MM-DD/wiki_activity_summary.parquet
    |   `-- namespace_activity_summary/event_date=YYYY-MM-DD/namespace_activity_summary.parquet
    |-- metadata/
    `-- state/
```

The repository documents this layout, but the generated runtime artifacts remain local and inspectable.

## Current Limitations

- the live source is public internet infrastructure and can disconnect or slow down;
- broker replay depends on topic retention and is not guaranteed forever;
- the publisher keeps a lightweight source checkpoint, but the durable rebuild story is Bronze raw landing;
- the Gold layer is intentionally simple and local-first;
- this phase does not include a dashboard, API, authentication, or cloud deployment.

## Future Directions

- richer stream filters and derived metrics;
- schema-evolution handling across source changes;
- richer partition management and retention controls;
- optional serving layer only if justified later;
- cloud streaming equivalents only as a future extension, not as a claim in this phase.
