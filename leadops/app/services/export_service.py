from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pandas as pd

from app.core.config import EXPORT_DIR
from app.db.duckdb import get_connection


def export_leads(lead_ids: Sequence[str]) -> Path:
    if not lead_ids:
        raise ValueError("No lead IDs provided for export")

    with get_connection() as conn:
        placeholders = ", ".join(["?"] * len(lead_ids))
        query = f"""
            SELECT
                lead_id,
                owner_name,
                address_normalized,
                contact_email,
                contact_phone,
                trigger_type,
                score,
                tier,
                suggested_opener,
                score_version,
                generated_at
            FROM lead_current
            WHERE lead_id IN ({placeholders})
        """
        df = conn.execute(query, list(lead_ids)).df()

        if df.empty:
            raise ValueError("No matching leads found for export")

        now = datetime.now(UTC)
        export_batch_id = now.strftime("%Y%m%d%H%M%S")
        export_path = EXPORT_DIR / f"export_batch_{export_batch_id}.csv"
        df.to_csv(export_path, index=False)

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS export_batch (
                export_batch_id VARCHAR,
                created_at VARCHAR,
                lead_count INTEGER,
                export_path VARCHAR
            )
            """
        )
        conn.execute(
            """
            INSERT INTO export_batch VALUES (?, ?, ?, ?)
            """,
            [export_batch_id, now.isoformat(), len(df), str(export_path)],
        )

    return export_path