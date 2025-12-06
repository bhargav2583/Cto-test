"""Application configuration and settings management."""

from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load dotenv file early so local development picks up defaults without extra tooling.
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    """Centralised application settings."""

    app_name: str = "FastAPI Backend"
    environment: str = Field(default="development")
    backend_cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )
    log_level: str = Field(default="INFO")

    gmail_client_id: str | None = None
    gmail_client_secret: str | None = None
    gmail_redirect_uri: str | None = None
    openai_api_key: str | None = None

    static_dir: Path = BACKEND_DIR / "static"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings object."""

    return Settings()
