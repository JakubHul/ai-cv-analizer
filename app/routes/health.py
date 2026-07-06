import json
from urllib import error, request

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import get_connection
from app.models.api import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    database_status = "ok"
    ollama_status = "ok"

    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
    except Exception:
        database_status = "error"

    payload = {
        "model": settings.ollama_model,
        "prompt": "healthcheck",
        "stream": False,
    }
    req = request.Request(
        settings.ollama_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10):
            pass
    except (error.URLError, TimeoutError):
        ollama_status = "unavailable"

    return HealthResponse(
        status="ok" if database_status == "ok" else "degraded",
        database=database_status,
        ollama=ollama_status,
    )
