
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.config import settings
from backend.app.db.database import get_db
from backend.app.schemas import APIResponse, HealthData

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=APIResponse[HealthData])
def check_health(db: Session = Depends(get_db)):
    db_ok = False

    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        print(f"[Health] Database check failed: {exc}")

    # This indicates that the key is configured, not that an API call
    # to Gemini has been verified successfully.
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))

    return APIResponse(
        status="ok" if db_ok else "error",
        data=HealthData(
            status="healthy" if db_ok else "degraded",
            version=settings.APP_VERSION,
            environment=settings.APP_ENV,
            model_loaded=gemini_configured,
            rag_indexed_chunks=0,
            database_connected=db_ok,
        ),
        error=None,
    )
