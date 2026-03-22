from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.services.pipeline_service import run_pipeline

router = APIRouter()


@router.post("/api/run-pipeline")
def run_pipeline_api():
    try:
        result = run_pipeline()
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/run-pipeline-form")
def run_pipeline_form():
    run_pipeline_api()
    return RedirectResponse(url="/run?status=ok", status_code=303)