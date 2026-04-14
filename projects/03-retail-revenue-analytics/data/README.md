# Local Data Area

This directory is reserved for local medallion-aligned artifacts for the retail revenue analytics project.

Expected local layout:

```text
data/
  bronze/
    raw/
    metadata/
  silver/
  gold/
```

Bronze raw files are landed locally from Kaggle and kept unchanged. Silver and Gold directories are reserved for future iterations; they are not implemented in the foundation phase.

Raw files and generated metadata artifacts are local outputs. Recreate them by running the ingestion and Bronze jobs from the repository root.
