import urllib.parse

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
    try:
        result = run_pipeline()
        params = (
            f"status=ok"
            f"&normalized={result['normalized_count']}"
            f"&snapshot={result['snapshot_count']}"
            f"&current={result['current_count']}"
        )
        return RedirectResponse(url=f"/run?{params}", status_code=303)
    except Exception as e:
        msg = urllib.parse.quote(str(e))
        return RedirectResponse(url=f"/run?status=error&message={msg}", status_code=303)
