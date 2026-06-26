import logging
import re
from time import perf_counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import yaml
from sqlalchemy.orm import Session

from app.core.metrics import record
from app.models.audit_log import AuditLog
from app.models.issue import Issue
from app.schemas.moderate import ModerateRequest, ModerateResponse, PolicyViolation


RULES_PATH = Path(__file__).resolve().parents[1] / "policies" / "moderation_rules.yaml"
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_rules() -> List[Dict[str, Any]]:
    """Load moderation rules so policy checks use the repo-managed YAML source."""
    with RULES_PATH.open("r", encoding="utf-8") as rules_file:
        rules = yaml.safe_load(rules_file) or []
    return rules


def moderate(db: Session, req: ModerateRequest) -> ModerateResponse:
    """Score text against moderation rules and persist audit/issue records."""
    start = perf_counter()
    matched_rules: List[Dict[str, Any]] = []

    for rule in load_rules():
        pattern = rule.get("pattern")
        if not pattern:
            # TODO: Implement locale-specific formality checks for LOCALE_MISMATCH.
            continue
        if re.search(pattern, req.text, flags=re.IGNORECASE):
            matched_rules.append(rule)

    labels = [str(rule["id"]) for rule in matched_rules]
    policy_violations = [
        PolicyViolation(
            rule_id=str(rule["id"]),
            rule_name=str(rule["name"]),
            severity=str(rule["severity"]),
        )
        for rule in matched_rules
    ]
    severities = {str(rule["severity"]).lower() for rule in matched_rules}
    if "high" in severities:
        action = "block"
    elif matched_rules:
        action = "flag"
    else:
        action = "allow"
    is_safe = action == "allow"

    audit_log = AuditLog(
        text_snippet=req.text[:200],
        locale=req.locale,
        action=action,
    )
    db.add(audit_log)
    db.flush()

    if action != "allow":
        summary = "Matched moderation rules: " + ", ".join(labels)
        issue = Issue(
            category="policy",
            description=summary,
            status="open",
        )
        db.add(issue)

    db.commit()
    db.refresh(audit_log)
    latency_ms = int((perf_counter() - start) * 1000)
    record("moderate", latency_ms, is_safe, labels[0] if labels else None)
    logger.info(
        "moderation completed",
        extra={
            "service": "moderate",
            "latency_ms": latency_ms,
            "outcome": action,
            "locale": req.locale,
            "failure_reason": labels[0] if labels else None,
        },
    )

    return ModerateResponse(
        audit_id=audit_log.id,
        is_safe=is_safe,
        labels=labels,
        policy_violations=policy_violations,
        action=action,
    )
