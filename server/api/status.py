from fastapi import APIRouter
from sqlalchemy import text

from api.dependencies import DbSession
from models.chat import MODEL_OPTIONS, ModelOption

router = APIRouter(prefix="/api")


@router.get("/health")
def health(session: DbSession) -> dict[str, bool]:
    """Liveness check; returns {"ok": true} once a trivial DB query succeeds."""
    session.execute(text("SELECT 1"))
    return {"ok": True}


@router.get("/models")
def models() -> list[ModelOption]:
    """List the selectable chat models; exactly one is flagged is_default."""
    return list(MODEL_OPTIONS)
