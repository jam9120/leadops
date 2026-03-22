from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.exports import router as exports_router
from app.api.ingest import router as ingest_router
from app.api.leads import router as leads_router
from app.api.pipeline import router as pipeline_router
from app.core.config import BASE_DIR, CURATED_DIR, ensure_directories
from app.db.duckdb import get_connection

ensure_directories()

app = FastAPI(title="leadops")
app.include_router(ingest_router)
app.include_router(pipeline_router)
app.include_router(leads_router)
app.include_router(exports_router)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

_PIPELINE_INPUTS = ("permits", "property_records", "enrichment")
_ALLOWED_SORT_COLUMNS = {"score", "tier", "owner_name", "trigger_type"}
_DEFAULT_SORT_BY = "score"
_DEFAULT_SORT_ORDER = "desc"


def _lead_summary() -> dict:
    try:
        with get_connection() as conn:
            tables = conn.execute("SHOW TABLES").df()["name"].tolist()
            if "lead_current" not in tables:
                return {}
            return (
                conn.execute(
                    """
                    SELECT
                        COUNT(*) AS lead_count,
                        CAST(SUM(CASE WHEN tier = 'Tier 1' THEN 1 ELSE 0 END) AS INTEGER) AS tier_1_count,
                        CAST(SUM(CASE WHEN tier = 'Tier 2' THEN 1 ELSE 0 END) AS INTEGER) AS tier_2_count,
                        CAST(SUM(CASE WHEN tier = 'Tier 3' THEN 1 ELSE 0 END) AS INTEGER) AS tier_3_count
                    FROM lead_current
                    """
                )
                .df()
                .to_dict(orient="records")[0]
            )
    except Exception:
        return {}


def _dataset_info() -> dict:
    info = {name: {"loaded": False, "row_count": 0} for name in _PIPELINE_INPUTS}
    try:
        with get_connection() as conn:
            tables = conn.execute("SHOW TABLES").df()["name"].tolist()
            for name in _PIPELINE_INPUTS:
                if name in tables:
                    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                    info[name] = {"loaded": True, "row_count": int(count)}
    except Exception:
        pass
    return info


@app.get("/")
def root():
    return RedirectResponse(url="/upload")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, status: str | None = None, message: str | None = None):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "status": status,
            "message": message,
            "datasets": _dataset_info(),
        },
    )


@app.get("/run", response_class=HTMLResponse)
def run_page(
    request: Request,
    status: str | None = None,
    message: str | None = None,
    normalized: int | None = None,
    snapshot: int | None = None,
    current: int | None = None,
):
    has_curated = all((CURATED_DIR / f"{name}.parquet").exists() for name in _PIPELINE_INPUTS)
    pipeline_result = (
        {"normalized": normalized, "snapshot": snapshot, "current": current}
        if normalized is not None
        else None
    )
    return templates.TemplateResponse(
        "run.html",
        {
            "request": request,
            "status": status,
            "message": message,
            "has_curated": has_curated,
            "summary": _lead_summary(),
            "pipeline_result": pipeline_result,
        },
    )


@app.get("/leads", response_class=HTMLResponse)
def leads_page(
    request: Request,
    tier: str | None = None,
    trigger_type: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
):
    sort_col = sort_by if sort_by in _ALLOWED_SORT_COLUMNS else _DEFAULT_SORT_BY
    sort_dir = "ASC" if sort_order == "asc" else "DESC"

    rows = []
    trigger_types = []
    try:
        with get_connection() as conn:
            tables = conn.execute("SHOW TABLES").df()["name"].tolist()
            if "lead_current" in tables:
                query = "SELECT * FROM lead_current WHERE 1=1"
                params: list[str] = []
                if tier:
                    query += " AND tier = ?"
                    params.append(tier)
                if trigger_type:
                    query += " AND trigger_type = ?"
                    params.append(trigger_type)
                query += f" ORDER BY {sort_col} {sort_dir}"
                rows = conn.execute(query, params).df().to_dict(orient="records")
                trigger_types = (
                    conn.execute(
                        "SELECT DISTINCT trigger_type FROM lead_current ORDER BY trigger_type"
                    )
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
            "sort_by": sort_col,
            "sort_order": sort_dir.lower(),
        },
    )


@app.get("/export", response_class=HTMLResponse)
def export_page(request: Request, status: str | None = None, message: str | None = None):
    rows = []
    try:
        with get_connection() as conn:
            tables = conn.execute("SHOW TABLES").df()["name"].tolist()
            if "lead_current" in tables:
                rows = (
                    conn.execute(
                        """
                        SELECT lead_id, owner_name, address_normalized, trigger_type, score, tier, suggested_opener
                        FROM lead_current
                        ORDER BY score DESC
                        LIMIT 200
                        """
                    )
                    .df()
                    .to_dict(orient="records")
                )
    except Exception:
        rows = []

    return templates.TemplateResponse(
        "export.html",
        {"request": request, "rows": rows, "status": status, "message": message},
    )
