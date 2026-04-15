# Checkpointing

## Why It Matters Here

Checkpointing is one of the main proof points of this case study.

The project uses readable local checkpoint artifacts so that:

- bounded publisher runs can resume from a recent stream position;
- Bronze consumption can restart without silently reprocessing everything;
- downstream layers know which Bronze batches and event dates have already been built.

## Checkpoint Layers

### Publisher Checkpoint

Stored under Bronze state, this file keeps:

- last published SSE event id;
- last observed source event timestamp;
- publisher run id;
- update timestamp.

### Bronze Consumer Checkpoint

The Bronze checkpoint keeps:

- consumer group name;
- topic name;
- last landed offset per topic partition;
- last observed broker timestamp;
- processed Bronze batch manifest.

### Silver State

Silver tracks which Bronze batch ids have already been standardized and which event dates were written.

### Gold State

Gold tracks which event dates were summarized and which tables were refreshed for each date.

## Stop and Resume Behavior

- bounded runs stop on `--max-events` or `--max-seconds`;
- the Bronze consumer resumes from the local checkpoint by default;
- `--replay` tells the Bronze consumer to ignore the local checkpoint and start from the earliest broker-retained offsets;
- downstream replay uses landed Bronze files instead of reconnecting to the source.

## Broker Replay vs. Offline Replay

These are two distinct operations with different semantics:

**Broker replay** (`run_bronze_consumer.py --replay`):

- ignores the local Bronze checkpoint and seeks to offset 0 on the topic;
- creates a **new** Bronze batch file with a new batch_id;
- does **not** delete or replace previously landed Bronze files;
- if run repeatedly over the same retained broker history, produces multiple Bronze batches
  covering the same events, which can cause inflated counts in Silver and Gold.

**Offline replay** (`run_replay.py`):

- reads the Bronze JSONL files already on disk;
- rebuilds Silver and Gold without touching the broker or live stream;
- is idempotent: overwrite-safe for Silver (batch_id in filename) and Gold (one file per table per event_date);
- is the recommended rebuild story for this project.

When in doubt, use `run_replay.py`.
