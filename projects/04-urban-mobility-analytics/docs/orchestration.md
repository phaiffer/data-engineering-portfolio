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

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-02
```

The same flow can also be run through the Python entrypoint:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

The flow returns a nested summary of:

- planned months;
- ingestion results;
- Bronze metadata results;
- Silver processing results;
- Gold output results.

Each layer also writes a latest-run metadata file that records the selected month window, run timestamps, processed months, skipped months, output paths, status, and state path.

## Scope Boundaries

This orchestration layer is real, but intentionally modest:

- local execution only;
- no Prefect Cloud;
- no worker pools;
- no deployed schedule claims;
- no retries or alerting policy framework yet.
