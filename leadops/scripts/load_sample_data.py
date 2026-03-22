from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import BASE_DIR, RAW_DIR, ensure_directories
from app.services.ingest_service import save_uploaded_csv

ensure_directories()

samples_dir = BASE_DIR / "data" / "samples"

for dataset_type, filename in [
    ("permits", "permits.csv"),
    ("property_records", "property_records.csv"),
    ("enrichment", "enrichment.csv"),
]:
    src = samples_dir / filename
    temp = RAW_DIR / f"seed_{filename}"
    shutil.copyfile(src, temp)
    save_uploaded_csv(temp, dataset_type)

print("Sample datasets loaded.")