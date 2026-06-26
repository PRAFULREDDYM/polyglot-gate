from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class EvaluateRequest(BaseModel):
    prompt_text: str = Field(min_length=1)
    locale: str = "en"
    reference_answer: Optional[str] = None
    model_name: Optional[str] = None

    @field_validator("prompt_text")
    @classmethod
    def prompt_text_must_not_be_blank(cls, value: str) -> str:
        """Validate prompt input so empty prompts are not scored as real evaluations."""
        if not value.strip():
            raise ValueError("prompt_text must not be empty or whitespace-only")
        return value


class ScoreBreakdown(BaseModel):
    correctness: float
    formatting: float
    locale_coverage: float
    regression_pass: bool
    overall: float


class EvaluateResponse(BaseModel):
    run_id: int
    prompt_id: int
    output_text: str
    locale: str
    latency_ms: int
    scores: ScoreBreakdown
    passed: bool
    failure_reasons: List[str]


class MultiLocaleEvaluateRequest(BaseModel):
    prompt_text: str = Field(min_length=1)
    locales: List[str] = Field(default_factory=lambda: ["en", "es", "fr"], min_length=1)
    reference_answer: Optional[str] = None

    @field_validator("prompt_text")
    @classmethod
    def prompt_text_must_not_be_blank(cls, value: str) -> str:
        """Validate prompt input so empty prompts are not scored across locales."""
        if not value.strip():
            raise ValueError("prompt_text must not be empty or whitespace-only")
        return value

    @field_validator("locales")
    @classmethod
    def locales_must_not_be_blank(cls, value: List[str]) -> List[str]:
        """Validate requested locales so every cross-locale score has a target."""
        if any(not locale.strip() for locale in value):
            raise ValueError("locales must not contain empty values")
        return value


class LocaleResult(BaseModel):
    locale: str
    run_id: int
    scores: ScoreBreakdown
    passed: bool


class MultiLocaleEvaluateResponse(BaseModel):
    prompt_id: int
    results: List[LocaleResult]
    consistency_score: float
    worst_locale: str
    summary: str


class EvaluationHistoryItem(BaseModel):
    run_id: int
    prompt_id: int
    prompt_text: str
    locale: str
    output_text: str
    overall: float
    passed: bool
    created_at: datetime
