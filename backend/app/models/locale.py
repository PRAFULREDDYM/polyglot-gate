from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Locale(Base):
    __tablename__ = "locales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_supported: Mapped[bool] = mapped_column(Boolean, default=True)
