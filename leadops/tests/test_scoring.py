from app.core.config import load_scoring_config
from app.core.scoring import assign_tier, build_opener, compute_score


def test_compute_score():
    config = load_scoring_config()
    row = {
        "trigger_type": "adu_permit",
        "trigger_date": "2026-03-01",
        "contact_confidence": "high",
        "owner_occupancy_proxy": "owner_occupied",
        "owner_name": "Mark Johnson",
    }
    score = compute_score(row, config)
    assert score >= 70


def test_assign_tier():
    config = load_scoring_config()
    assert assign_tier(85, config) == "Tier 1"
    assert assign_tier(65, config) == "Tier 2"
    assert assign_tier(20, config) == "Tier 3"


def test_build_opener():
    config = load_scoring_config()
    row = {"trigger_type": "adu_permit", "owner_name": "Mark Johnson"}
    opener = build_opener(row, config)
    assert "Mark" in opener
    assert "insurance" in opener.lower()
