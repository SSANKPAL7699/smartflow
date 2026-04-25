# backend/config.py
# Central settings for the entire SmartFlow application.
# All environment variables are loaded here — no raw os.environ anywhere else!

from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """
    SmartFlow application settings.
    Values are loaded from .env file automatically.
    If not found in .env, defaults below are used.
    """

    # ── App Info ─────────────────────────────────────────────
    APP_NAME: str        = "SmartFlow ERP Analytics"
    APP_VERSION: str     = "1.0.0"
    DEBUG: bool          = True

    # ── API Settings ─────────────────────────────────────────
    API_PREFIX: str      = "/api"
    HOST: str            = "0.0.0.0"
    PORT: int            = 8000

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str    = "sqlite+aiosqlite:///./smartflow.db"
    # Switch to PostgreSQL on AWS by changing this in .env:
    # DATABASE_URL=postgresql+psycopg2://user:pass@rds-host:5432/smartflow

    # ── SAP Data Paths ───────────────────────────────────────
    DATA_DIR: str = Field(
        default_factory=lambda: os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "simulated"
        )
    )

    # ── AWS Settings (used later for deployment) ──────────────
    AWS_REGION: str           = "us-east-1"
    AWS_S3_BUCKET: str        = "smartflow-data-bucket"
    AWS_ACCESS_KEY_ID: str    = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # ── Dashboard Settings ───────────────────────────────────
    DASHBOARD_PORT: int       = 8501
    API_BASE_URL: str         = "http://localhost:8000"

    class Config:
        env_file = ".env"           # Load from .env file
        env_file_encoding = "utf-8"
        case_sensitive = True       # ENV_VAR must match exactly


# ── Single instance used across entire app ───────────────────
settings = Settings()


# ── Quick test when run directly ─────────────────────────────
if __name__ == "__main__":
    print(f"App:      {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Debug:    {settings.DEBUG}")
    print(f"API:      {settings.HOST}:{settings.PORT}{settings.API_PREFIX}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Data Dir: {settings.DATA_DIR}")
    print(f"AWS:      {settings.AWS_REGION} → {settings.AWS_S3_BUCKET}")