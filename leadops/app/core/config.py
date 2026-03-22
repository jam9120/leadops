from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"
EXPORT_DIR = DATA_DIR / "exports"
DB_PATH = BASE_DIR / "leadops.duckdb"


def ensure_directories() -> None:
    for path in [RAW_DIR, CURATED_DIR, EXPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_scoring_config() -> dict[str, Any]:
    config_path = CONFIG_DIR / "scoring.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError("scoring.yaml must load as a dictionary")

    required_top_level = ["score_version", "tiers", "weights", "openers"]
    for key in required_top_level:
        if key not in config:
            raise ValueError(f"scoring.yaml missing required top-level key: {key}")
        if config[key] is None:
            raise ValueError(f"scoring.yaml key '{key}' is present but empty/null")

    required_weight_sections = [
        "trigger_type",
        "freshness_days",
        "contact_confidence",
        "owner_occupancy_proxy",
    ]
    if not isinstance(config["weights"], dict):
        raise ValueError("scoring.yaml 'weights' must be a dictionary")

    for key in required_weight_sections:
        if key not in config["weights"]:
            raise ValueError(f"scoring.yaml missing weights section: {key}")
        if config["weights"][key] is None:
            raise ValueError(f"scoring.yaml weights section '{key}' is empty/null")
        if not isinstance(config["weights"][key], dict):
            raise ValueError(f"scoring.yaml weights section '{key}' must be a mapping")

    freshness_keys = list(config["weights"]["freshness_days"].keys())
    non_string_keys = [k for k in freshness_keys if not isinstance(k, str)]
    if non_string_keys:
        raise ValueError(
            f"scoring.yaml freshness_days keys must be quoted strings. "
            f"Unquoted keys {non_string_keys!r} were parsed as {[type(k).__name__ for k in non_string_keys]}. "
            f"Wrap them in double quotes: \"0_30\", \"31_90\", etc."
        )

    return config