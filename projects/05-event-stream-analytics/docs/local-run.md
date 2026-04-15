# Local Run

All commands below assume you are running from the **repository root**
(`data-engineering-portfolio/`). If your shell exposes only `python3`, substitute that
interpreter.

## Quick Start

The shortest path from nothing to a working local pipeline:

```bash
# 1. activate environment
source .venv/bin/activate

# 2. start the broker
cd projects/05-event-stream-analytics && docker compose up -d && cd ../..

# 3. publish and land events
python projects/05-event-stream-analytics/src/jobs/run_publisher.py --max-events 100 --max-seconds 60
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --max-events 100 --max-seconds 60

# 4. build Silver and Gold
python projects/05-event-stream-analytics/src/jobs/run_silver.py
python projects/05-event-stream-analytics/src/jobs/run_gold.py
```

---

## 1. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r projects/05-event-stream-analytics/requirements.txt
```

## 2. Start the Broker

```bash
cd projects/05-event-stream-analytics
docker compose up -d
docker compose ps
```

Verify the broker is healthy before running the publisher.

## 3. Publish a Bounded Event Sample

Run from the repository root:

```bash
python projects/05-event-stream-analytics/src/jobs/run_publisher.py --max-events 100 --max-seconds 60
```

This connects to the live Wikimedia SSE stream, filters canary events, and publishes up to 100
events to the local Redpanda topic. Stops at whichever bound is reached first.

## 4. Land Bronze Raw Events

```bash
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --max-events 100 --max-seconds 60
```

This consumes messages from the Redpanda topic and lands them as a JSONL batch under
`data/bronze/raw/`. Updates the local Bronze consumer checkpoint.

## 5. Build Silver and Gold

```bash
python projects/05-event-stream-analytics/src/jobs/run_silver.py
python projects/05-event-stream-analytics/src/jobs/run_gold.py
```

Silver standardizes the landed Bronze batch into partitioned Parquet. Gold builds five
category and minute-bucket summary tables from Silver using DuckDB.

## 6. Offline Replay — Rebuild Silver and Gold From Landed Bronze

To rebuild Silver and Gold from already-landed Bronze files without touching the live stream
or broker:

```bash
python projects/05-event-stream-analytics/src/jobs/run_replay.py
```

Partial targets:

```bash
python projects/05-event-stream-analytics/src/jobs/run_replay.py --target silver
python projects/05-event-stream-analytics/src/jobs/run_replay.py --target gold
```

This is idempotent. It is the recommended way to rebuild downstream layers after landing new
Bronze data or after a failed downstream run.

## Note on Broker Replay

`run_bronze_consumer.py --replay` is a distinct operation from offline replay. It seeks to
offset 0 on the Redpanda topic and lands a **new** Bronze batch. It does not remove or replace
existing Bronze files. Running it repeatedly over the same retained broker history creates
multiple Bronze batches for the same events, which will inflate Silver and Gold counts.

Broker replay is for local experimentation. Offline replay (`run_replay.py`) is for safe
downstream rebuilds.

## 7. Shut Down the Broker

```bash
cd projects/05-event-stream-analytics
docker compose down
```
