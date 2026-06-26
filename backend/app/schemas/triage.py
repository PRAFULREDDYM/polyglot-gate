from typing import List, Optional

from pydantic import BaseModel


class TriageRequest(BaseModel):
    run_id: Optional[int] = None
    prompt_text: str
    output_text: str
    locale: str = "en"
    reported_issue: Optional[str] = None


class TriageResponse(BaseModel):
    issue_id: int
    issue_category: str
    confidence: float
    suggested_fix: str
    route_to: str


TriageResponseList = List[TriageResponse]
