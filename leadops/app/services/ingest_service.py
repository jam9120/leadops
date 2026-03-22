from pathlib import Path
from typing import Iterable

import pandas as pd

from app.core.config import CURATED_DIR, RAW_DIR
from app.db.duckdb import get_connection

REQUIRED_COLUMNS = {
    "permits": {"permit_id", "address", "owner_name", "permit_type", "permit_subtype", "issue_date"},
    "property_records": {"property_id", "address", "owner_name", "mailing_address", "owner_occupied", "trigger_label", "trigger_date"},
    "enrichment": {"address", "owner_name", "contact_email", "contact_phone", "contact_confidence"},
}


def validate_columns(dataset_type: str, columns: Iterable[str]) -> tuple[bool, list[str]]:
    required = REQUIRED_COLUMNS[dataset_type]
    provided = set(columns)
    missing = sorted(required - provided)
    return (len(missing) == 0, missing)


def save_uploaded_csv(file_path: Path, dataset_type: str) -> Path:
    df = pd.read_csv(file_path)
    ok, missing = validate_columns(dataset_type, df.columns)
    if not ok:
        raise ValueError(f"Missing required columns for {dataset_type}: {', '.join(missing)}")

    raw_target = RAW_DIR / f"{dataset_type}.csv"
    curated_target = CURATED_DIR / f"{dataset_type}.parquet"

    df.to_csv(raw_target, index=False)
    df.to_parquet(curated_target, index=False)

    with get_connection() as conn:
        conn.execute(f"CREATE OR REPLACE TABLE {dataset_type} AS SELECT * FROM read_parquet('{curated_target.as_posix()}')")

    return curated_target