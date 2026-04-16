# Screenshots

Use this folder for lightweight portfolio screenshots of the validated local project. Screenshots are optional, but they help reviewers quickly confirm that the case study runs end to end.

## Recommended Captures

- `dashboard-overview.png`: `http://127.0.0.1:5173` with KPI cards, API status, and page header.
- `dashboard-revenue-category.png`: dashboard daily revenue chart and category performance sections.
- `dashboard-tables.png`: dashboard seller, customer-state, order-status, and payment-type sections.
- `api-health.png`: `http://127.0.0.1:5002/health` returning healthy API metadata.
- `api-index.png`: `http://127.0.0.1:5002/api/v1` showing the endpoint index.
- `dbt-build-success.png`: terminal output from `.\scripts\dbt_build.ps1 build` showing `PASS=139 WARN=0 ERROR=0`.

## Capture Notes

- Prefer PNG exports at normal browser resolution.
- Crop browser chrome only if the URL is still clear from the caption or filename.
- Keep image exports reasonably small so the repository stays easy to clone and review.
- Do not add raw videos or very large image exports.
