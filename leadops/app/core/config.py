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
        return yaml.safe_load(f)