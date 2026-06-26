from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prompt import Prompt
from app.models.run import Run
from app.models.score import Score
from app.schemas.evaluate import (
    EvaluationHistoryItem,
    EvaluateRequest,
    EvaluateResponse,
    MultiLocaleEvaluateRequest,
    MultiLocaleEvaluateResponse,
)
from app.services.evaluation_service import (
    evaluate as evaluate_request,
    evaluate_multi_locale as evaluate_multi_locale_request,
)
from app.services.llm_provider import LLMProvider, get_llm_provider
from app.services.regression_runner import run_suite


router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(
    req: EvaluateRequest,
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
) -> EvaluateResponse:
    """Score an LLM response by delegating evaluation to the service layer."""
    return evaluate_request(db, llm, req)


@router.post("/evaluate/multi-locale", response_model=MultiLocaleEvaluateResponse)
def evaluate_multi_locale(
    req: MultiLocaleEvaluateRequest,
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
) -> MultiLocaleEvaluateResponse:
    """Score one prompt across locales by delegating consistency checks to the service."""
    return evaluate_multi_locale_request(db, llm, req)


@router.get("/evaluate/regression-suite")
def regression_suite(
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
) -> dict:
    """Run the batch regression suite against all fixture cases."""
    return run_suite(db, llm)


@router.get("/evaluate/history", response_model=List[EvaluationHistoryItem])
def evaluation_history(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    locale: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[EvaluationHistoryItem]:
    """List recent evaluation runs joined to their latest score for dashboard history."""
    ranked_scores = (
        select(
            Score.id.label("score_id"),
            Score.run_id.label("run_id"),
            Score.overall.label("overall"),
            func.row_number()
            .over(
                partition_by=Score.run_id,
                order_by=(desc(Score.created_at), desc(Score.id)),
            )
            .label("score_rank"),
        )
        .subquery()
    )

    query = (
        db.query(
            Run.id.label("run_id"),
            Run.prompt_id.label("prompt_id"),
            Prompt.text.label("prompt_text"),
            Prompt.locale.label("locale"),
            Run.output_text.label("output_text"),
            ranked_scores.c.overall.label("overall"),
            Run.created_at.label("created_at"),
        )
        .join(Prompt, Prompt.id == Run.prompt_id)
        .join(ranked_scores, ranked_scores.c.run_id == Run.id)
        .filter(ranked_scores.c.score_rank == 1)
    )

    if locale:
        query = query.filter(Prompt.locale == locale)

    rows = (
        query.order_by(desc(Run.created_at), desc(Run.id))
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        EvaluationHistoryItem(
            run_id=row.run_id,
            prompt_id=row.prompt_id,
            prompt_text=row.prompt_text,
            locale=row.locale,
            output_text=row.output_text or "",
            overall=float(row.overall or 0.0),
            passed=float(row.overall or 0.0) >= 0.7,
            created_at=row.created_at,
        )
        for row in rows
    ]
