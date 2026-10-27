import os
import sys
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.config import settings
from backend.app.db.database import get_db
from backend.app.schemas import APIResponse, HealthData
from backend.app.services.dummy_predictor import get_disease_predictor
from backend.app.services.rag_engine import get_rag_engine  # assuming a simple wrapper

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=APIResponse[HealthData])
def check_health(db: Session = Depends(get_db)):
    # ---- Database connectivity check ----
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # ---- Model / RAG status ----
    predictor = get_disease_predictor()
    rag = get_rag_engine()

    return APIResponse(
        status="ok",
        data=HealthData(
            status="healthy",
            version=settings.APP_VERSION,
            environment=settings.APP_ENV,
            model_loaded=predictor.model_loaded,
            rag_indexed_chunks=len(rag.chunks),
            database_connected=db_ok,
        ),
        error=None,
    )