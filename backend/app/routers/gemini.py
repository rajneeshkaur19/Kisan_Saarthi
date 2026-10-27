# ------------------------------------------------------------
# Gemini endpoint – forwards a GeminiRequest to the Gemini service
# ------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.gemini_service import (
    GeminiRequest,
    GeminiResponse,
    get_gemini_service,
)

router = APIRouter()

@router.post("/gemini", response_model=GeminiResponse)
def call_gemini(
    req: GeminiRequest,
    service = Depends(get_gemini_service),
):
    """Generate a response from Google Gemini."""
    try:
        return service.generate(req)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))