from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

from app.services.export_service import export_leads

router = APIRouter()

@router.post("/api/export")
def export_api(lead_ids: list[str]):
try:
path = export_leads(lead_ids)
return {"status": "ok", "export_path": str(path)}
except Exception as e:
raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/export-form")
def export_form(lead_ids: list[str] = Form(default=[])):
path = export_leads(lead_ids)
return FileResponse(path, media_type="text/csv", filename=path.name)
