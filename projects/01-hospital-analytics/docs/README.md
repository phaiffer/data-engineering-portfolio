# Hospital Analytics Docs

Navigation index for the hospital analytics case study documentation.

Use this directory to understand the current local architecture, how each layer works, and how to run the implemented end-to-end demo.

## Pipeline Layers

- [Bronze Layer](bronze.md): raw landing area, file inventory, main CSV selection, profiling, and metadata generation.
- [Silver Layer](silver.md): row-preserving cleaning and standardization of the patient-flow dataset.
- [Silver Plan](silver_plan.md): planning notes and assumptions that informed the Silver implementation.
- [Gold Layer](gold.md): curated analytical CSV outputs for daily patient flow, referral summaries, and demographic summaries.
- [Serving Layer](serving.md): PostgreSQL schemas, loaded Gold tables, serving views, and validation behavior.

## Consumption Layers

- [API Layer](api.md): Flask service contract, source views, endpoints, query parameters, and local run details.
- [Dashboard](../dashboard/README.md): React + Vite frontend that consumes the Flask API.

## Demo and Presentation

- [Demo / Run Guide](demo.md): concise local execution order for demos and reviewers.
- [Assets Placeholder](assets/README.md): planned location for future architecture diagrams, screenshots, and portfolio visuals.

## Related Project Entry Points

- [Project README](../README.md): case-study landing page and current status.
- [API README](../api/README.md): quick API startup notes.
- [Dashboard README](../dashboard/README.md): frontend setup, environment, and build commands.
