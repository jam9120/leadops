# Project Rules

## Mission
Build a production-minimal lead-ops app for insurance lead scoring and export.
This is a batch pipeline and operator console, not a consumer-facing SaaS product.

## Core Principles
- KISS. No overengineering.
- Every file and function must map to monetization, reliability, or operator speed.
- Deterministic first. Rules engine first. No ML in v1.
- Keep the system modular, testable, and easy to export to GitHub.
- Prefer boring, reliable code over clever abstractions.

## Required Stack
- Python 3.11+
- FastAPI backend
- Simple frontend with Jinja templates
- DuckDB for analytics/querying
- Parquet for persisted datasets
- YAML for scoring/config
- CSV export
- Dockerfile for reproducible run
- No Kafka
- No microservices
- No Redis
- No Postgres in v1
- No external CRM dependency in v1
- No browser scraping in v1
- No ML in v1

## Functional Scope
The app must:
1. ingest CSV files for permits, property records, and enrichment
2. normalize addresses and owner names deterministically
3. classify trigger types
4. score leads using YAML-driven rules
5. generate lead_current and lead_score_snapshot outputs
6. show a review table with filters
7. export selected leads to CSV
8. include score_version and generated_at on scored leads

## Quality Rules
- Use explicit typing where practical
- Add tests for core normalization and scoring logic
- Add logging for pipeline steps
- No placeholder code
- No TODOs unless blocked by an external dependency
- No hidden magic constants; use config
- Return clear error messages
- Keep functions small and named plainly

## Acceptance Standard
The system is only done when:
- sample CSVs ingest successfully
- scoring runs end-to-end
- lead table renders correctly
- CSV export works
- tests pass
- local run instructions are accurate

## UI Rule
The UI is an internal operator console only.
It should be simple, fast, and ugly-but-clean if needed.
No design theater.

## Deployment Rule
Target Replit Reserved VM after local app works fully.
