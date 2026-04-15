# Bronze

## Purpose

Bronze lands raw broker events without inventing downstream business semantics.

## Output Shape

Bronze raw files are written as JSONL:

```text
data/bronze/raw/stream_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.jsonl
```

Each line keeps:

- broker metadata such as topic, partition, offset, and broker timestamp;
- publisher metadata such as publisher run id and source SSE id;
- the raw Wikimedia RecentChange payload under `event`.

## Why JSONL

JSONL keeps raw events inspectable and easy to replay locally. It is also simple to sample in the notebook without specialized tooling.

## Bronze Metadata

Bronze metadata captures:

- batch id and file path;
- bounded-run configuration;
- landed event count;
- observed topic partitions and offset ranges;
- event type counts;
- minimum and maximum source event timestamps when available.

## Bronze State

Bronze state keeps a readable consumer checkpoint:

- latest landed offset per topic partition;
- last updated timestamp;
- processed batch manifest.

The consumer does not rely only on hidden broker commits. The local state file is part of what this project proves.
