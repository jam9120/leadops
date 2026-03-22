from datetime import datetime
from pathlib import Path

import pandas as pd

from app.core.config import CURATED_DIR, load_scoring_config
from app.core.normalize import (
    classify_trigger,
    normalize_address,
    normalize_owner_name,
    owner_occupancy_proxy,
)
from app.core.scoring import assign_tier, build_opener, compute_score
from app.db.duckdb import get_connection


def _load_parquet(name: str) -> pd.DataFrame:
    path = CURATED_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing curated dataset: {path}")
    return pd.read_parquet(path)


def run_pipeline() -> dict[str, int]:
    config = load_scoring_config()
    score_version = config["score_version"]
    generated_at = datetime.utcnow().isoformat()

    permits = _load_parquet("permits")
    property_records = _load_parquet("property_records")
    enrichment = _load_parquet("enrichment")

    permit_events = permits.copy()
    permit_events["source_type"] = "permits"
    permit_events["source_record_id"] = permit_events["permit_id"].astype(str)
    permit_events["trigger_type"] = permit_events.apply(
        lambda r: classify_trigger("", r["permit_type"], r["permit_subtype"]),
        axis=1,
    )
    permit_events["trigger_date"] = permit_events["issue_date"]

    property_events = property_records.copy()
    property_events["source_type"] = "property_records"
    property_events["source_record_id"] = property_events["property_id"].astype(str)
    property_events["trigger_type"] = property_events["trigger_label"].apply(lambda x: classify_trigger(x))
    property_events["owner_occupancy_proxy"] = property_events["owner_occupied"].apply(owner_occupancy_proxy)

    permit_events["owner_occupancy_proxy"] = "unknown"

    combined = pd.concat(
        [
            permit_events[
                ["source_type", "source_record_id", "owner_name", "address", "trigger_type", "trigger_date", "owner_occupancy_proxy"]
            ],
            property_events[
                ["source_type", "source_record_id", "owner_name", "address", "trigger_type", "trigger_date", "owner_occupancy_proxy"]
            ],
        ],
        ignore_index=True,
    )

    combined["owner_name_normalized"] = combined["owner_name"].apply(normalize_owner_name)
    combined["address_normalized"] = combined["address"].apply(normalize_address)

    enrichment_norm = enrichment.copy()
    enrichment_norm["owner_name_normalized"] = enrichment_norm["owner_name"].apply(normalize_owner_name)
    enrichment_norm["address_normalized"] = enrichment_norm["address"].apply(normalize_address)

    merged = combined.merge(
        enrichment_norm[
            ["owner_name_normalized", "address_normalized", "contact_email", "contact_phone", "contact_confidence"]
        ],
        on=["owner_name_normalized", "address_normalized"],
        how="left",
    )

    merged["contact_confidence"] = merged["contact_confidence"].fillna("low")
    merged["contact_email"] = merged["contact_email"].fillna("")
    merged["contact_phone"] = merged["contact_phone"].fillna("")

    merged["lead_id"] = merged.apply(
        lambda r: f"{r['source_type']}::{r['source_record_id']}::{r['address_normalized']}",
        axis=1,
    )
    merged["score"] = merged.apply(lambda r: compute_score(r.to_dict(), config), axis=1)
    merged["tier"] = merged["score"].apply(lambda s: assign_tier(s, config))
    merged["score_version"] = score_version
    merged["generated_at"] = generated_at
    merged["suggested_opener"] = merged.apply(lambda r: build_opener(r.to_dict(), config), axis=1)
    merged["export_status"] = "not_exported"

    snapshot = merged[
        [
            "lead_id",
            "source_type",
            "source_record_id",
            "owner_name",
            "address",
            "address_normalized",
            "trigger_type",
            "trigger_date",
            "contact_email",
            "contact_phone",
            "contact_confidence",
            "owner_occupancy_proxy",
            "score",
            "tier",
            "score_version",
            "generated_at",
            "suggested_opener",
            "export_status",
        ]
    ].copy()

    current = snapshot.sort_values(["lead_id", "generated_at"]).drop_duplicates(subset=["lead_id"], keep="last")

    snapshot_path = CURATED_DIR / "lead_score_snapshot.parquet"
    current_path = CURATED_DIR / "lead_current.parquet"
    normalized_path = CURATED_DIR / "normalized_event.parquet"

    snapshot.to_parquet(snapshot_path, index=False)
    current.to_parquet(current_path, index=False)
    merged.to_parquet(normalized_path, index=False)

    with get_connection() as conn:
        conn.execute(f"CREATE OR REPLACE TABLE normalized_event AS SELECT * FROM read_parquet('{normalized_path.as_posix()}')")
        conn.execute(f"CREATE OR REPLACE TABLE lead_score_snapshot AS SELECT * FROM read_parquet('{snapshot_path.as_posix()}')")
        conn.execute(f"CREATE OR REPLACE TABLE lead_current AS SELECT * FROM read_parquet('{current_path.as_posix()}')")

    return {
        "normalized_count": int(len(merged)),
        "snapshot_count": int(len(snapshot)),
        "current_count": int(len(current)),
    }