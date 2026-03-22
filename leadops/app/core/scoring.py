from datetime import datetime
from typing import Any

from app.core.normalize import first_name_from_owner


def freshness_bucket(trigger_date: str) -> str:
    try:
        dt = datetime.strptime(trigger_date, "%Y-%m-%d")
    except ValueError:
        return "181_plus"

    days = (datetime.utcnow() - dt).days
    if days <= 30:
        return "0_30"
    if days <= 90:
        return "31_90"
    if days <= 180:
        return "91_180"
    return "181_plus"


def compute_score(row: dict[str, Any], config: dict[str, Any]) -> int:
    weights = config["weights"]
    score = 0

    score += weights["trigger_type"].get(row["trigger_type"], 0)
    score += weights["freshness_days"].get(freshness_bucket(row["trigger_date"]), 0)
    score += weights["contact_confidence"].get((row["contact_confidence"] or "low").lower(), 0)
    score += weights["owner_occupancy_proxy"].get(row["owner_occupancy_proxy"], 0)

    return int(score)


def assign_tier(score: int, config: dict[str, Any]) -> str:
    tier_1_min = config["tiers"]["tier_1_min"]
    tier_2_min = config["tiers"]["tier_2_min"]

    if score >= tier_1_min:
        return "Tier 1"
    if score >= tier_2_min:
        return "Tier 2"
    return "Tier 3"


def build_opener(row: dict[str, Any], config: dict[str, Any]) -> str:
    template = config["openers"].get(row["trigger_type"], config["openers"]["unknown"])
    return template.format(first_name=first_name_from_owner(row["owner_name"]))