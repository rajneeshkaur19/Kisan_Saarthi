import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application‑wide configuration loaded from environment variables or .env."""

    APP_NAME: str = "KisanSaarthi API"
    APP_VERSION: str = "1.0.0"

    # Runtime environment (development / production)
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Host / port on which UVicorn will listen
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # CORS – origins that the frontend may call
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # SQLite DB (relative to the project root)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kisansaarthi.db")

    # Absolute path to the static data folder (price lists, schemes, etc.)
    DATA_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data")
    )

    # Minimum confidence score for Gemini‑generated answers (used by RAG)
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", 0.55))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AGMARKNET_API_KEY: str = os.getenv("AGMARKNET_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()