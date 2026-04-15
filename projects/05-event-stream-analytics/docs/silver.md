# Silver

## Purpose

Silver standardizes landed RecentChange events while preserving event grain.

## Design Principles

- one row per event;
- safe timestamp parsing;
- source-aware standardization without over-modeling;
- partition-friendly fields for local analytics;
- no aggregation in Silver.

## Core Columns

The standardized dataset keeps fields such as:

- `source_batch_id`
- `source_meta_id`
- `source_event_id`
- `event_timestamp`
- `event_date`
- `event_hour`
- `event_minute`
- `event_type`
- `is_bot`
- `actor_segment`
- `wiki`
- `domain`
- `namespace`
- `title`
- `user_text`
- `comment_text`
- `server_name`
- `log_type`
- `log_action`

## Output Layout

```text
data/silver/tables/recentchange_events/event_date=YYYY-MM-DD/batch_YYYYMMDDTHHMMSSZ.parquet
```

This keeps the dataset partition-friendly while preserving the link back to the Bronze batch that produced it.

## Silver Metadata

Silver metadata records:

- row count;
- event dates written;
- output file paths;
- timestamp parseability metrics;
- null-rate checks on important fields;
- event type visibility.
