from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.moderate import ModerateRequest, ModerateResponse
from app.services.moderation_service import moderate as moderate_request


router = APIRouter()


@router.post("/moderate", response_model=ModerateResponse)
def moderate(
    req: ModerateRequest,
    db: Session = Depends(get_db),
) -> ModerateResponse:
    """Score text for policy violations and return the moderation action."""
    return moderate_request(db, req)
