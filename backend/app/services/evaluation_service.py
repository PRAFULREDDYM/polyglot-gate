import logging
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.core.metrics import record
from app.models.prompt import Prompt
from app.models.run import Run
from app.models.score import Score
from app.schemas.evaluate import (
    EvaluateRequest,
    EvaluateResponse,
    LocaleResult,
    MultiLocaleEvaluateRequest,
    MultiLocaleEvaluateResponse,
    ScoreBreakdown,
)
from app.services import regression_runner
from app.services.llm_provider import LLMProvider


TERMINAL_PUNCTUATION = set(".!?。？！…)]}\"'")
SPANISH_MARKERS = set("ñáéíóúü¿¡")
ENGLISH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "in",
    "is",
    "of",
    "the",
    "to",
}
logger = logging.getLogger(__name__)


def evaluate(
    db: Session,
    llm: LLMProvider,
    req: EvaluateRequest,
    prompt_id: Optional[int] = None,
) -> EvaluateResponse:
    """Score an LLM response for correctness, formatting, locale fit, and regressions."""
    if prompt_id is None:
        prompt = Prompt(text=req.prompt_text, locale=req.locale)
        db.add(prompt)
        db.flush()
        prompt_id = prompt.id

    generation = llm.generate(req.prompt_text, req.locale)
    output_text = str(generation.get("text", ""))
    latency_ms = int(generation.get("latency_ms", 0))
    model_name = req.model_name or str(generation.get("model", ""))

    run = Run(
        prompt_id=prompt_id,
        model_name=model_name,
        output_text=output_text,
        latency_ms=latency_ms,
        status="completed",
    )
    db.add(run)
    db.flush()

    correctness = _score_correctness(output_text, req.reference_answer)
    formatting = _score_formatting(output_text)
    locale_coverage = _score_locale_coverage(output_text, req.locale)
    regression_pass = regression_runner.check_known_case(
        req.prompt_text,
        output_text,
        req,
    )
    overall = round(
        0.4 * correctness
        + 0.2 * formatting
        + 0.2 * locale_coverage
        + 0.2 * (1.0 if regression_pass else 0.0),
        3,
    )
    passed = overall >= 0.7
    failure_reasons = _failure_reasons(
        correctness,
        formatting,
        locale_coverage,
        regression_pass,
    )
    record(
        "evaluate",
        latency_ms,
        passed,
        failure_reasons[0] if failure_reasons else None,
    )
    logger.info(
        "evaluation completed",
        extra={
            "service": "evaluate",
            "latency_ms": latency_ms,
            "outcome": "passed" if passed else "failed",
            "locale": req.locale,
            "failure_reason": failure_reasons[0] if failure_reasons else None,
        },
    )

    score = Score(
        run_id=run.id,
        correctness=correctness,
        formatting=formatting,
        locale_coverage=locale_coverage,
        regression_pass=regression_pass,
        overall=overall,
    )
    db.add(score)
    db.commit()
    db.refresh(run)

    return EvaluateResponse(
        run_id=run.id,
        prompt_id=prompt_id,
        output_text=output_text,
        locale=req.locale,
        latency_ms=latency_ms,
        scores=ScoreBreakdown(
            correctness=correctness,
            formatting=formatting,
            locale_coverage=locale_coverage,
            regression_pass=regression_pass,
            overall=overall,
        ),
        passed=passed,
        failure_reasons=failure_reasons,
    )


def evaluate_multi_locale(
    db: Session,
    llm: LLMProvider,
    req: MultiLocaleEvaluateRequest,
) -> MultiLocaleEvaluateResponse:
    """Score one prompt across locales to find consistency gaps between outputs."""
    prompt = Prompt(text=req.prompt_text, locale=req.locales[0])
    db.add(prompt)
    db.flush()

    results: List[LocaleResult] = []
    for locale in req.locales:
        single_req = EvaluateRequest(
            prompt_text=req.prompt_text,
            locale=locale,
            reference_answer=req.reference_answer,
        )
        response = evaluate(db, llm, single_req, prompt_id=prompt.id)
        results.append(
            LocaleResult(
                locale=locale,
                run_id=response.run_id,
                scores=response.scores,
                passed=response.passed,
            )
        )

    best = max(results, key=lambda result: result.scores.overall)
    worst = min(results, key=lambda result: result.scores.overall)
    spread = best.scores.overall - worst.scores.overall
    consistency_score = max(0.0, min(1.0, round(1.0 - spread, 3)))
    summary = (
        f"{worst.locale} scored {spread:.2f} lower than {best.locale}"
    )

    return MultiLocaleEvaluateResponse(
        prompt_id=prompt.id,
        results=results,
        consistency_score=consistency_score,
        worst_locale=worst.locale,
        summary=summary,
    )


def _score_correctness(output_text: str, reference_answer: Optional[str]) -> float:
    if reference_answer is None:
        return 1.0 if len(output_text.strip()) > 3 else 0.0

    output_tokens = _token_set(output_text)
    reference_tokens = _token_set(reference_answer)
    union = output_tokens | reference_tokens
    if not union:
        return 0.0
    return round(len(output_tokens & reference_tokens) / len(union), 3)


def _score_formatting(output_text: str) -> float:
    stripped = output_text.strip()
    issues = 0

    if output_text.count("**") % 2:
        issues += 1
    if output_text.count("```") % 2:
        issues += 1
    if _looks_truncated(stripped):
        issues += 1

    return max(0.0, round(1.0 - 0.25 * issues, 3))


def _score_locale_coverage(output_text: str, locale: str) -> float:
    normalized_locale = locale.lower()
    if normalized_locale == "en":
        return 1.0

    lowered = output_text.lower()
    if normalized_locale.startswith("es"):
        return 1.0 if any(marker in lowered for marker in SPANISH_MARKERS) else 0.0

    # Placeholder until a real language-detection library is introduced.
    words = _token_set(output_text)
    if words and words <= ENGLISH_STOPWORDS:
        return 0.0
    return 1.0 if output_text.strip() else 0.0


def _failure_reasons(
    correctness: float,
    formatting: float,
    locale_coverage: float,
    regression_pass: bool,
) -> List[str]:
    reasons: List[str] = []
    if correctness < 0.7:
        reasons.append(f"correctness below threshold ({correctness:.2f})")
    if formatting < 0.7:
        reasons.append(f"formatting below threshold ({formatting:.2f})")
    if locale_coverage < 0.7:
        reasons.append(f"locale coverage below threshold ({locale_coverage:.2f})")
    if not regression_pass:
        reasons.append("regression check failed")
    return reasons


def _looks_truncated(text: str) -> bool:
    if not text or len(text) <= 80:
        return False
    return text[-1] not in TERMINAL_PUNCTUATION


def _token_set(text: str) -> Set[str]:
    return {token for token in text.lower().split() if token}
