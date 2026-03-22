import urllib.parse

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from app.core.config import RAW_DIR
from app.services.ingest_service import save_uploaded_csv

router = APIRouter()

VALID_DATASET_TYPES = {"permits", "property_records", "enrichment"}


@router.post("/api/upload/{dataset_type}")
async def upload_dataset(dataset_type: str, file: UploadFile = File(...)):
    if dataset_type not in VALID_DATASET_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid dataset type: {dataset_type}")

    target_path = RAW_DIR / f"uploaded_{dataset_type}.csv"
    content = await file.read()
    target_path.write_bytes(content)

    try:
        parquet_path = save_uploaded_csv(target_path, dataset_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"status": "ok", "dataset_type": dataset_type, "parquet_path": str(parquet_path)}


@router.post("/upload-form/{dataset_type}")
async def upload_dataset_form(dataset_type: str, file: UploadFile = File(...)):
    if dataset_type not in VALID_DATASET_TYPES:
        msg = urllib.parse.quote(f"Invalid dataset type: {dataset_type}")
        return RedirectResponse(url=f"/upload?status=error&message={msg}", status_code=303)

    target_path = RAW_DIR / f"uploaded_{dataset_type}.csv"
    content = await file.read()
    target_path.write_bytes(content)

    try:
        save_uploaded_csv(target_path, dataset_type)
        return RedirectResponse(url="/upload?status=ok", status_code=303)
    except ValueError as e:
        msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/upload?status=error&message={msg}", status_code=303)
