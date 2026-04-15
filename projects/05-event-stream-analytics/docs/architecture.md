# Architecture

## Local-First Flow

```text
Wikimedia EventStreams RecentChange
-> source_client.py reads SSE events
-> publisher.py publishes raw envelopes to Redpanda
-> bronze_consumer.py consumes broker messages
-> Bronze raw JSONL landing
-> Silver standardization to partitioned Parquet
-> Gold category and minute-bucket summaries with DuckDB
```

## Responsibility Boundaries

### Source Stream

The public stream is the upstream event source. It is live, public, and outside local control.

### Broker

Redpanda acts as the local broker boundary:

- decouples reading from the public stream from downstream consumption;
- allows publisher and consumer to run independently;
- provides a realistic local message-broker step without introducing a large cluster.

### Publisher

The publisher:

- reads bounded windows from the live stream;
- filters canary events;
- wraps each event with source and publish metadata;
- publishes messages to the raw topic;
- keeps a readable publisher checkpoint with the last seen SSE id.

### Bronze Consumer

The Bronze consumer:

- reads from the raw topic;
- applies bounded local consumption rules;
- lands raw JSONL batches;
- tracks readable local partition offsets for restart behavior.

### Silver

Silver:

- preserves one row per event;
- standardizes field names and data types;
- parses timestamps safely;
- retains event type, bot, wiki, and namespace context;
- writes partitioned Parquet by `event_date`.

### Gold

Gold:

- reads standardized Silver Parquet files for one `event_date` partition at a time;
- builds minute-bucket and category-level daily summaries using DuckDB;
- overwrites the affected `event_date` partition outputs on each run;
- stores metadata about which event dates have been summarized.

### Checkpointing

Checkpointing keeps progress readable across layers:

- publisher checkpoint for last published SSE id;
- Bronze checkpoint for topic partition offsets;
- Silver state for processed Bronze batches;
- Gold state for processed event dates.

### Replay

This project distinguishes two separate replay operations:

- **Broker replay**: the Bronze consumer `--replay` flag seeks to the earliest retained Redpanda
  offsets and lands a new Bronze batch. Depends on broker retention still being available.
- **Offline replay**: `run_replay.py` rebuilds Silver and Gold from already-landed Bronze JSONL
  files without touching the live stream or broker. Idempotent and retention-independent.

Offline replay is the main resilience story for this portfolio case.
