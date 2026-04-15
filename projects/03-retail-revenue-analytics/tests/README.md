# Tests

This directory contains focused tests for stable helper logic.

Current tests avoid full Kaggle downloads and do not run end-to-end pipelines. They target pure behavior such as:

- Silver column-name normalization;
- Silver blank string to null handling;
- Gold item-side revenue calculations;
- Gold payment summaries.

Broader integration tests should be added later when Silver, Gold, or DBT contracts become stable enough to justify them.
