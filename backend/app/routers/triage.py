from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.issue import Issue
from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_service import issue_summary, triage as triage_request


router = APIRouter()


@router.post("/triage", response_model=TriageResponse)
def triage(
    req: TriageRequest,
    db: Session = Depends(get_db),
) -> TriageResponse:
    """Classify and route a globalization issue into the Issue table."""
    return triage_request(db, req)


@router.get("/triage/issues", response_model=List[TriageResponse])
def list_issues(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> List[TriageResponse]:
    """List routed issue summaries for dashboard history."""
    issues = (
        db.query(Issue)
        .order_by(desc(Issue.created_at), desc(Issue.id))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [issue_summary(issue) for issue in issues]
