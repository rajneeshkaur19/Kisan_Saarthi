import os
import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from backend.app.db.models import DiagnosisAudit
from backend.app.services.gemini_service import analyze_leaf_image


def diagnose_leaf_image(
    image_bytes: bytes,
    language: str = "en",
    db: Session = None,
) -> Dict[str, Any]:
    """
    Analyze a crop leaf image using Gemini.
    No local ML model or fabricated demo predictions are used.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is not configured. "
            "Add GEMINI_API_KEY to your backend .env file."
        )

    # Gemini image analysis
    result = analyze_leaf_image(
        image_bytes=image_bytes,
        language=language,
        api_key=api_key,
    )

    if not isinstance(result, dict):
        raise ValueError("Gemini returned an invalid diagnosis response.")

    # Record diagnosis only when a database session is available
    if db is not None:
        try:
            audit = DiagnosisAudit(
                crop=result.get("crop", "Unknown"),
                disease_key=result.get("disease_key", "unknown"),
                confidence=float(result.get("confidence_score", 0.0)),
                is_inconclusive=bool(result.get("is_inconclusive", True)),
                language=language,
            )
            db.add(audit)
            db.commit()
        except Exception as exc:
            db.rollback()
            print(f"[DiagnosisAudit] Could not save diagnosis: {exc}")

    return result