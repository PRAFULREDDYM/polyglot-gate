from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
    )

    ANTHROPIC_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./app.db"
    LLM_PROVIDER: str = "anthropic"
    LOG_LEVEL: str = "INFO"


settings = Settings()
