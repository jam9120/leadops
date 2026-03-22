from fastapi import APIRouter, Query

from app.db.duckdb import get_connection

router = APIRouter()


@router.get("/api/leads")
def list_leads(
    tier: str | None = Query(default=None),
    trigger_type: str | None = Query(default=None),
):
    query = "SELECT * FROM lead_current WHERE 1=1"
    params: list[str] = []

    if tier:
        query += " AND tier = ?"
        params.append(tier)
    if trigger_type:
        query += " AND trigger_type = ?"
        params.append(trigger_type)

    query += " ORDER BY score DESC, generated_at DESC"

    with get_connection() as conn:
        df = conn.execute(query, params).df()

    return {"rows": df.to_dict(orient="records")}