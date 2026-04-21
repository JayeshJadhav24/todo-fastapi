"""
core/config.py — Application settings loaded from environment variables.

We use pydantic-settings, which reads values from:
  1. Environment variables   (highest priority)
  2. The .env file           (fallback)
  3. Field defaults          (last resort)

Why pydantic-settings?
  • Type validation for free — a bad DATABASE_URL crashes on startup, not at runtime.
  • One place for ALL configuration.
  • Secrets never hard-coded in source code.

Usage anywhere in the project:
    from app.core.config import settings
    print(settings.APP_NAME)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = "Todo API"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    # Default uses SQLite (no server needed).
    # To switch to PostgreSQL set in .env:
    #   DATABASE_URL=postgresql+psycopg2://user:pass@localhost/dbname
    DATABASE_URL: str = "sqlite:///./todo.db"

    # ------------------------------------------------------------------ #
    # Pydantic-settings config
    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=".env",          # load from .env file
        env_file_encoding="utf-8",
        extra="ignore",           # silently ignore unknown env vars
        case_sensitive=False,     # APP_NAME == app_name
    )


# Single shared instance — import this everywhere
settings = Settings()
