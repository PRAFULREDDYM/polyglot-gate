from typing import List, Optional

from pydantic import BaseModel


class ModerateRequest(BaseModel):
    text: str
    locale: str = "en"
    context: Optional[str] = None


class PolicyViolation(BaseModel):
    rule_id: str
    rule_name: str
    severity: str


class ModerateResponse(BaseModel):
    audit_id: int
    is_safe: bool
    labels: List[str]
    policy_violations: List[PolicyViolation]
    action: str
