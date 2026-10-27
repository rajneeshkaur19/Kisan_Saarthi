from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.schemas import APIResponse, DiagnoseData, APIError
from backend.app.db.database import get_db
from backend.app.services.disease_service import diagnose_leaf_image

router = APIRouter(tags=["Crop Doctor"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/diagnose", response_model=APIResponse[DiagnoseData])
async def diagnose(
    file: UploadFile = File(...),
    language: str = Form("en"),
    db: Session = Depends(get_db)
):
    # ---- Validate file type -------------------------------------------------
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="INVALID_FILE_TYPE",
                message=f"Unsupported file type '{file.content_type}'. Please upload a JPG, PNG, or WebP image."
            )
        )

    # ---- Read file bytes ----------------------------------------------------
    image_bytes = await file.read()

    # ---- Size checks ---------------------------------------------------------
    if len(image_bytes) > MAX_FILE_SIZE:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="FILE_TOO_LARGE",
                message="File size exceeds maximum allowed limit of 10MB."
            )
        )
    if len(image_bytes) < 100:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="EMPTY_FILE",
                message="Uploaded file is empty or corrupted."
            )
        )

    # ---- Run the diagnosis ---------------------------------------------------
    try:
        result = diagnose_leaf_image(image_bytes=image_bytes, language=language, db=db)
        return APIResponse(status="ok", data=DiagnoseData(**result), error=None)
    except ValueError as ve:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(code="IMAGE_PROCESSING_ERROR", message=str(ve))
        )
    except Exception as exc:
        print(f"[Diagnose] Unexpected error: {type(exc).__name__}: {exc}")
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="INTERNAL_INFERENCE_ERROR",
                message="Crop Doctor inference pipeline encountered an unexpected issue. Please try another clear photograph."
            )
        )