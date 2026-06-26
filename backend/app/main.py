from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging_config import setup_logging
from app.database import init_db
from app.routers.evaluate import router as evaluate_router
from app.routers.metrics import router as metrics_router
from app.routers.moderate import router as moderate_router
from app.routers.triage import router as triage_router


app = FastAPI(title="Polyglot Gate", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluate_router, prefix="/api", tags=["evaluation"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(moderate_router, prefix="/api", tags=["moderation"])
app.include_router(triage_router, prefix="/api", tags=["triage"])


@app.on_event("startup")
def startup_event():
    """Initialize database tables before the API starts serving requests."""
    setup_logging(settings.LOG_LEVEL)
    init_db()


@app.get("/health")
def health():
    """Report service health so callers can confirm the API is reachable."""
    return {"status": "ok", "service": "polyglot-gate"}
