from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.exports import router as exports_router
from app.api.ingest import router as ingest_router
from app.api.leads import router as leads_router
from app.api.pipeline import router as pipeline_router
from app.core.config import BASE_DIR, ensure_directories
from app.db.duckdb import get_connection

ensure_directories()

app = FastAPI(title="leadops")
app.include_router(ingest_router)
app.include_router(pipeline_router)
app.include_router(leads_router)
app.include_router(exports_router)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.get("/")
def root():
    return RedirectResponse(url="/upload")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/run", response_class=HTMLResponse)
def run_page(request: Request):
    summary = {}
    try:
        with get_connection() as conn:
            if "lead_current" in conn.execute("SHOW TABLES").df()["name"].tolist():
                summary = conn.execute(
                    """
                    SELECT
                        COUNT(*) AS lead_count,
                        SUM(CASE WHEN tier = 'Tier 1' THEN 1 ELSE 0 END) AS tier_1_count,
                        SUM(CASE WHEN tier = 'Tier 2' THEN 1 ELSE 0 END) AS tier_2_count,
                        SUM(CASE WHEN tier = 'Tier 3' THEN 1 ELSE 0 END) AS tier_3_count
                    FROM lead_current
                    """
                ).df().to_dict(orient="records")[0]
    except Exception:
        summary = {}
    return templates.TemplateResponse("run.html", {"request": request, "summary": summary})


@app.get("/leads", response_class=HTMLResponse)
def leads_page(request: Request, tier: str | None = None, trigger_type: str | None = None):
    rows = []
    trigger_types = []

    try:
        with get_connection() as conn:
            query = "SELECT * FROM lead_current WHERE 1=1"
            params: list[str] = []
            if tier:
                query += " AND tier = ?"
                params.append(tier)
            if trigger_type:
                query += " AND trigger_type = ?"
                params.append(trigger_type)
            query += " ORDER BY score DESC, generated_at DESC"
            rows = conn.execute(query, params).df().to_dict(orient="records")

            if "lead_current" in conn.execute("SHOW TABLES").df()["name"].tolist():
                trigger_types = (
                    conn.execute("SELECT DISTINCT trigger_type FROM lead_current ORDER BY trigger_type")
                    .df()["trigger_type"]
                    .tolist()
                )
    except Exception:
        rows = []

    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "rows": rows,
            "trigger_types": trigger_types,
            "selected_tier": tier or "",
            "selected_trigger_type": trigger_type or "",
        },
    )


@app.get("/export", response_class=HTMLResponse)
def export_page(request: Request):
    rows = []
    try:
        with get_connection() as conn:
            if "lead_current" in conn.execute("SHOW TABLES").df()["name"].tolist():
                rows = conn.execute(
                    """
                    SELECT lead_id, owner_name, address_normalized, trigger_type, score, tier, suggested_opener
                    FROM lead_current
                    ORDER BY score DESC
                    LIMIT 200
                    """
                ).df().to_dict(orient="records")
    except Exception:
        rows = []

    return templates.TemplateResponse("export.html", {"request": request, "rows": rows})