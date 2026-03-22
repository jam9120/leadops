# LeadOps

Internal lead-ops app for insurance prospect scoring and CSV export.

## Stack
- Python 3.12
- FastAPI + Uvicorn
- DuckDB (file-based, `leadops/leadops.duckdb`)
- Parquet for persisted datasets
- Jinja2 templates (server-side rendered UI)
- YAML-driven scoring rules (`leadops/config/scoring.yaml`)

## Project Layout
```
leadops/
  app/
    api/          # FastAPI route modules (ingest, pipeline, leads, exports)
    core/         # Config, models, normalization, scoring logic
    db/           # DuckDB connection helper
    services/     # Business logic (ingest, pipeline, export)
    static/       # CSS/static assets
    templates/    # Jinja2 HTML templates
  config/
    scoring.yaml  # YAML scoring rules
  data/
    raw/          # Uploaded CSV input files
    curated/      # Normalized/processed Parquet files
    exports/      # CSV exports
    samples/      # Sample data files
  scripts/        # Utility scripts (load_sample_data, run_pipeline)
  leadops.duckdb  # DuckDB database file
  requirements.txt
```

## Running
The app runs via the "Start application" workflow:
```
cd leadops && uvicorn app.main:app --host 0.0.0.0 --port 5000
```

## Features
1. Upload CSVs (permits, property records, enrichment)
2. Run normalization + scoring pipeline
3. Review leads table with filters (tier, trigger type)
4. Export selected leads to CSV

## Deployment
Configured as VM deployment (needed for local DuckDB file persistence):
```
cd leadops && gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app.main:app
```

## Dependencies
All Python packages are installed via pip from `leadops/requirements.txt`.
Gunicorn is also installed for production deployment.
