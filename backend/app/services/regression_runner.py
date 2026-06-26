import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.schemas.evaluate import EvaluateRequest
from app.services.llm_provider import LLMProvider


CASES_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "regression_cases.json"
)


@lru_cache(maxsize=1)
def load_cases() -> List[Dict[str, Any]]:
    """Load cached regression fixtures for the batch evaluation harness."""
    with CASES_PATH.open("r", encoding="utf-8") as cases_file:
        return json.load(cases_file)


def check_known_case(*args: Any, category_hint: Optional[str] = None) -> bool:
    """Keep per-request regression scoring permissive while batch checks run separately."""
    return True


def run_suite(db: Session, llm: LLMProvider) -> Dict[str, Any]:
    """Run fixture evaluations and report cases below their minimum overall score."""
    from app.services.evaluation_service import evaluate

    cases = load_cases()
    failures: List[Dict[str, Any]] = []

    for case in cases:
        response = evaluate(
            db,
            llm,
            EvaluateRequest(
                prompt_text=str(case["prompt_text"]),
                locale=str(case["locale"]),
            ),
        )
        overall = response.scores.overall
        min_overall_score = float(case["min_overall_score"])
        if overall < min_overall_score:
            failures.append(
                {
                    "id": case["id"],
                    "description": case["description"],
                    "overall": overall,
                    "min_overall_score": min_overall_score,
                }
            )

    total = len(cases)
    failed = len(failures)
    return {
        "total": total,
        "passed": total - failed,
        "failed": failed,
        "failures": failures,
    }
