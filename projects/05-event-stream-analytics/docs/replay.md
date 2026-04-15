# Replay

## What Replay Means in This Project

This project distinguishes three separate run modes. Understanding the difference matters for
avoiding duplicate data in Silver and Gold.

| Mode                 | What runs                   | Where data comes from     | Creates new Bronze batch? |
| -------------------- | --------------------------- | ------------------------- | ------------------------- |
| Live bounded capture | publisher + bronze consumer | live Wikimedia SSE stream | yes                       |
| Broker replay        | bronze consumer `--replay`  | Redpanda retained offsets | yes                       |
| Offline replay       | `run_replay.py`             | landed Bronze JSONL files | no                        |

---

## Live Bounded Capture

The normal first-run flow:

```bash
python src/jobs/run_publisher.py --max-events 100 --max-seconds 60
python src/jobs/run_bronze_consumer.py --max-events 100 --max-seconds 60
```

The publisher reads from the live stream. The consumer lands the broker messages as a new Bronze
batch. Each run creates one new JSONL file in `data/bronze/raw/`.

---

## Broker Replay

```bash
python src/jobs/run_bronze_consumer.py --replay --max-events 100
```

The consumer seeks to offset 0 on the topic and consumes messages from the beginning of the
broker's retained history. **It creates a new Bronze batch file with a new batch_id.**

### Duplicate risk

**Running broker replay more than once over the same retained broker history will create multiple
Bronze batch files that cover the same underlying events.**

This is what happens downstream:

- Silver processes each batch independently. Two Bronze batches for the same event window produce
  two Parquet files under the same `event_date=` partition.
- Gold reads all Parquet files under an `event_date=` partition via a glob. If two files contain
  the same events, Gold summaries will be inflated by the duplicate count.

There is no automatic deduplication at any layer. The only way to recover a clean state after
duplicate broker replays is to remove the extra Bronze JSONL files and re-run Silver and Gold from
a clean slate, or to use `run_replay.py` (offline replay) which is idempotent by design.

Broker replay is useful for local experimentation but is not the recommended rebuild story.

---

## Offline Replay From Bronze (Recommended)

```bash
python src/jobs/run_replay.py
```

This rebuilds Silver and Gold from the Bronze JSONL files already landed locally. It does not
reconnect to the live stream or broker. It does not create new Bronze batches.

Why this is the recommended rebuild path:

- it does not depend on the live public stream being available;
- it does not depend on broker retention still holding the old messages;
- it is idempotent: running it twice produces the same Silver and Gold outputs;
- it keeps the raw landing layer meaningful instead of disposable.

Partial targets are also available:

```bash
python src/jobs/run_replay.py --target silver   # rebuild Silver only
python src/jobs/run_replay.py --target gold     # rebuild Gold only from current Silver
python src/jobs/run_replay.py --target all      # rebuild Silver then Gold (default)
```

---

## Scope of Replay in Phase One

This project keeps replay simple and honest:

- no exactly-once claims at the broker level;
- no complex backfill scheduler;
- no schema-registry-based evolution handling;
- just readable local files, deterministic downstream rebuilds, and explicit operator intent.
