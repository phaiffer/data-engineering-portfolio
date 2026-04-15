# Orchestration

## Tool Choice

This project uses Prefect as a simple local orchestration surface.

The goal is to show real task and flow boundaries without introducing cloud assumptions or deployment ceremony.

## Implemented Flow

Flow name:

```text
urban-mobility-analytics-flow
```

Implemented tasks:

- `plan-source-months`
- `run-ingestion`
- `run-bronze-metadata`
- `run-silver-standardization`
- `run-gold-summaries`

## Local Execution

Run the full local flow with:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

The flow returns a nested summary of:

- planned months;
- ingestion results;
- Bronze metadata results;
- Silver processing results;
- Gold output results.

## Scope Boundaries

This orchestration layer is real, but intentionally modest:

- local execution only;
- no Prefect Cloud;
- no worker pools;
- no deployed schedule claims;
- no retries or alerting policy framework yet.
