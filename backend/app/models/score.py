from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), nullable=False)
    correctness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    formatting: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    locale_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    regression_pass: Mapped[bool] = mapped_column(Boolean, default=True)
    overall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rubric_version: Mapped[str] = mapped_column(String(20), default="v1")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
