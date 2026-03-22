from app.services.ingest_service import validate_columns


def test_validate_columns_success():
    ok, missing = validate_columns(
        "permits",
        ["permit_id", "address", "owner_name", "permit_type", "permit_subtype", "issue_date"],
    )
    assert ok is True
    assert missing == []


def test_validate_columns_missing():
    ok, missing = validate_columns(
        "enrichment",
        ["address", "owner_name", "contact_email"],
    )
    assert ok is False
    assert "contact_phone" in missing
    assert "contact_confidence" in missing