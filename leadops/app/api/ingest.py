from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from app.core.config import RAW_DIR
from app.services.ingest_service import save_uploaded_csv

router = APIRouter()


@router.post("/api/upload/{dataset_type}")
async def upload_dataset(dataset_type: str, file: UploadFile = File(...)):
    if dataset_type not in {"permits", "property_records", "enrichment"}:
        raise HTTPException(status_code=400, detail="Invalid dataset type")

    target_path = RAW_DIR / f"uploaded_{dataset_type}.csv"
    content = await file.read()
    target_path.write_bytes(content)

    try:
        parquet_path = save_uploaded_csv(target_path, dataset_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "status": "ok",
        "dataset_type": dataset_type,
        "parquet_path": str(parquet_path),
    }


@router.post("/upload-form/{dataset_type}")
async def upload_dataset_form(dataset_type: str, file: UploadFile = File(...)):
    await upload_dataset(dataset_type, file)
    return RedirectResponse(url="/upload?status=ok", status_code=303)