# Local Data Area

This directory is reserved for local medallion-aligned artifacts for the job market analytics project.

Expected local layout:

```text
data/
  bronze/
    raw/
    metadata/
  silver/
  gold/
```

Raw files and generated Silver/Gold artifacts are ignored by Git. Recreate them locally by running the ingestion and processing jobs from the repository root.
