# Gold

## Purpose

Gold produces category and minute-bucket summaries over standardized Silver event data.

This layer is a rebuild-oriented local analytical output. It is not a dashboard-serving mart in
this project phase. Gold tables are written as Parquet files and are intended to be read with
DuckDB or pandas for local exploration.

## Source

Gold reads from Silver Parquet files via a DuckDB glob VIEW over one `event_date=` partition at
a time. All timestamps are UTC, derived from the `event_timestamp` column in Silver (parsed from
`meta.dt` in the raw Wikimedia RecentChange payload).

## Output Layout

```text
data/gold/tables/<table_name>/event_date=YYYY-MM-DD/<table_name>.parquet
```

Each table is one Parquet file per `event_date`. Gold overwrites the output file on rebuild,
making it safe to re-run with `--force` or via `run_replay.py`.

## Gold Tables

### `minute_event_summary`

**Grain:** one row per (`event_date`, `event_minute`, `wiki`, `event_type`).

Groups all Silver events for a given day by the minute they occurred, the wiki they came from,
and their event type. Useful for seeing activity spikes within a bounded capture window.

`event_minute` is the integer minute-of-day extracted from `event_timestamp` in Silver (0–1439).

**Metrics per group:** `event_count`, `unique_user_count`, `bot_event_count`,
`non_bot_event_count`, `edit_count`, `new_page_count`, `log_event_count`.

---

### `event_type_summary`

**Grain:** one row per (`event_date`, `event_type`).

Daily counts broken down by event type (`edit`, `new`, `log`, `categorize`, or `unknown`).

**Metrics per group:** `event_count`, `unique_user_count`, `bot_event_count`,
`non_bot_event_count`.

---

### `bot_vs_human_summary`

**Grain:** one row per (`event_date`, `actor_segment`).

`actor_segment` is derived in Silver from the `is_bot` flag and the presence of a `user` field:
`bot`, `human`, or `unknown`. This table gives a daily split of automated versus human-driven
activity in the captured window.

**Metrics per group:** `event_count`, `unique_user_count`.

---

### `wiki_activity_summary`

**Grain:** one row per (`event_date`, `wiki`).

Daily counts per wiki identifier (e.g. `enwiki`, `commonswiki`, `wikidatawiki`). Useful for
seeing which wikis dominate the captured event sample.

**Metrics per group:** `event_count`, `unique_user_count`, `bot_event_count`,
`non_bot_event_count`, `edit_count`, `new_page_count`, `log_event_count`.

---

### `namespace_activity_summary`

**Grain:** one row per (`event_date`, `namespace`).

`namespace` is normalized from the integer namespace id in Silver to a readable label (`main`,
`talk`, `user`, `file`, `category`, `template`, `help`, or `unknown`).

**Metrics per group:** `event_count`, `unique_user_count`, `bot_event_count`,
`non_bot_event_count`.

---

## Core Metric Definitions

| Metric | Definition |
| ---------------------- | -------------------------------------------------------- |
| `event_count` | COUNT(*) of Silver rows in the group |
| `unique_user_count` | COUNT(DISTINCT user_text) excluding blank/null values |
| `bot_event_count` | COUNT of rows where `actor_segment = 'bot'` |
| `non_bot_event_count` | COUNT of rows where `actor_segment = 'human'` |
| `edit_count` | COUNT of rows where `event_type = 'edit'` |
| `new_page_count` | COUNT of rows where `event_type = 'new'` |
| `log_event_count` | COUNT of rows where `event_type = 'log'` |

All metrics are counts over the Silver rows that fall within the group's dimensions and
`event_date` partition. They reflect what was captured in the bounded run, not global Wikipedia
activity.
