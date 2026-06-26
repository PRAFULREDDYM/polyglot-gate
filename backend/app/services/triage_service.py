import logging
from time import perf_counter
from typing import Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.core.metrics import record
from app.models.issue import Issue
from app.schemas.triage import TriageRequest, TriageResponse


SUPPORTED_LOCALES = {"en", "es", "fr", "de", "ja"}
logger = logging.getLogger(__name__)


def classify(
    prompt_text: str,
    output_text: str,
    locale: str,
    reported_issue: Optional[str],
) -> Tuple[str, float]:
    """Classify globalization issues with heuristics until a model classifier replaces them."""
    # Heuristic, not ML: this is the future slot for a real classifier model.
    if not output_text.strip() or _is_near_duplicate(prompt_text, output_text):
        return "hallucination", 0.6

    if locale not in SUPPORTED_LOCALES:
        return "unsupported_locale", 0.9

    issue_text = (reported_issue or "").lower()
    if any(token in issue_text for token in ("translat", "untranslated", "wrong language")):
        return "translation", 0.8
    if any(token in issue_text for token in ("format", "markdown", "broken layout")):
        return "formatting", 0.8
    if any(token in issue_text for token in ("rude", "tone", "too casual", "too formal")):
        return "tone", 0.7
    if any(token in issue_text for token in ("offensive", "unsafe", "policy")):
        return "policy", 0.85

    return "other", 0.3


def suggest_fix(category: str, locale: str) -> str:
    """Suggest a category-specific remediation so routed teams get an actionable next step."""
    suggestions = {
        "translation": (
            f"Re-run generation with an explicit instruction to respond only in {locale} "
            "and verify no English fallback strings remain."
        ),
        "formatting": (
            "Regenerate or post-process the output with the expected markdown/layout schema, "
            "then validate balanced emphasis, lists, links, and code fences."
        ),
        "policy": (
            "Send the content through moderation review and remove or rewrite the unsafe "
            "claim before exposing it to users."
        ),
        "hallucination": (
            "Compare the answer against the source prompt and reference material, then "
            "regenerate with stricter grounding instructions."
        ),
        "tone": (
            f"Regenerate with a locale-aware tone guide for {locale}, including the desired "
            "formality level and examples of acceptable phrasing."
        ),
        "unsupported_locale": (
            f"Route {locale} through locale onboarding before generation, including glossary, "
            "fallback behavior, and reviewer coverage."
        ),
        "other": (
            "Collect a clearer reporter note and attach the prompt/output pair so triage can "
            "reclassify it with more context."
        ),
    }
    return suggestions[category]


def route(category: str) -> str:
    """Map issue categories to the owning internal queue for follow-up."""
    routes = {
        "translation": "i18n-team",
        "unsupported_locale": "i18n-team",
        "formatting": "platform-team",
        "policy": "trust-and-safety",
        "hallucination": "model-quality",
        "tone": "content-design",
        "other": "general-triage",
    }
    return routes[category]


def triage(db: Session, req: TriageRequest) -> TriageResponse:
    """Persist a routed Issue row from a reported globalization problem."""
    start = perf_counter()
    category, confidence = classify(
        req.prompt_text,
        req.output_text,
        req.locale,
        req.reported_issue,
    )
    suggested_fix = suggest_fix(category, req.locale)
    routed_to = route(category)
    description = req.reported_issue or (
        f"Automatically classified {category} issue for locale {req.locale}."
    )

    issue = Issue(
        run_id=req.run_id,
        category=category,
        description=description,
        suggested_fix=suggested_fix,
        status="routed",
        routed_to=routed_to,
        confidence=confidence,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    latency_ms = int((perf_counter() - start) * 1000)
    record("triage", latency_ms, True, None)
    logger.info(
        "triage completed",
        extra={
            "service": "triage",
            "latency_ms": latency_ms,
            "outcome": "routed",
            "issue_category": category,
            "route_to": routed_to,
        },
    )

    return _issue_to_response(issue)


def issue_summary(issue: Issue) -> TriageResponse:
    """Convert an Issue row into the dashboard triage summary shape."""
    return _issue_to_response(issue)


def _issue_to_response(issue: Issue) -> TriageResponse:
    return TriageResponse(
        issue_id=issue.id,
        issue_category=issue.category,
        confidence=issue.confidence if issue.confidence is not None else 0.0,
        suggested_fix=issue.suggested_fix or "",
        route_to=issue.routed_to or "general-triage",
    )


def _is_near_duplicate(prompt_text: str, output_text: str) -> bool:
    prompt = prompt_text.strip().lower()
    output = output_text.strip().lower()
    if not prompt or not output:
        return False
    if prompt == output:
        return True

    prompt_tokens = _token_set(prompt)
    output_tokens = _token_set(output)
    union = prompt_tokens | output_tokens
    if not union:
        return False
    return len(prompt_tokens & output_tokens) / len(union) >= 0.85


def _token_set(text: str) -> Set[str]:
    return {token for token in text.split() if token}
