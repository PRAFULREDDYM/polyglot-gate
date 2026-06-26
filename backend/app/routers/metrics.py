from fastapi import APIRouter

from app.core.metrics import snapshot


router = APIRouter()


@router.get("/metrics")
def metrics() -> dict:
    """Return the current in-process service metrics snapshot."""
    return snapshot()
