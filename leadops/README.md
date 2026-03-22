# leadops

Internal lead-ops app for insurance prospect scoring and CSV export.

## Stack

- Python 3.12
- FastAPI + Uvicorn
- DuckDB (file-based, `leadops.duckdb`)
- Parquet (via pandas + pyarrow)
- YAML scoring rules (`config/scoring.yaml`)
- Jinja2 server-rendered templates

---

## Setup

All commands run from the `leadops/` directory.

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Expected: prompt prefix changes to `(.venv)`.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Expected: all packages install without errors. Final line: `Successfully installed ...`.

### 3. Load sample data

```bash
python scripts/load_sample_data.py
```

Expected output:

```
Sample datasets loaded.
```

This writes three Parquet files to `data/curated/` and registers them as DuckDB tables.

### 4. Run the scoring pipeline

```bash
python scripts/run_pipeline.py
```

Expected output:

```
Pipeline completed: {'normalized_count': 6, 'snapshot_count': 6, 'current_count': 6}
```

This writes `lead_score_snapshot.parquet` and `lead_current.parquet` to `data/curated/`.

### 5. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

Open `http://localhost:5000` in a browser. You will be redirected to `/upload`.

### 6. Run the tests

```bash
pytest -q
```

Expected output:

```
9 passed in Xs
```

---

## Operator workflow

1. **Upload** — Go to `/upload`. Upload `data/samples/permits.csv`, `data/samples/property_records.csv`, and `data/samples/enrichment.csv` one at a time.
2. **Run** — Go to `/run`. Click "Normalize + Score". The page shows result counts on success.
3. **Review** — Go to `/leads`. Filter by tier or trigger type to review scored leads.
4. **Export** — Go to `/export`. Select rows with checkboxes and click "Export selected CSV" to download.

---

## Required CSV columns

| Dataset | Required columns |
|---|---|
| `permits` | `permit_id`, `address`, `owner_name`, `permit_type`, `permit_subtype`, `issue_date` |
| `property_records` | `property_id`, `address`, `owner_name`, `mailing_address`, `owner_occupied`, `trigger_label`, `trigger_date` |
| `enrichment` | `address`, `owner_name`, `contact_email`, `contact_phone`, `contact_confidence` |

---

## Scoring

Leads are scored using `config/scoring.yaml`. Weights are applied for:

- Trigger type (e.g. `adu_permit` = 35 pts)
- Freshness (days since trigger date)
- Contact confidence (high / medium / low)
- Owner occupancy proxy (owner-occupied / absentee / unknown)

Tiers: **Tier 1** ≥ 80 pts, **Tier 2** ≥ 60 pts, **Tier 3** below 60.

---

## Data locations

| Path | Contents |
|---|---|
| `data/raw/` | Uploaded CSV files |
| `data/curated/` | Parquet files (input datasets + pipeline outputs) |
| `data/exports/` | Downloaded CSV export files |
| `data/samples/` | Sample CSVs for testing |
| `leadops.duckdb` | DuckDB database file |
