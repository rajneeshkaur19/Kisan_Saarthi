from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.schemas import APIResponse, EligibilityRequest, EligibilityResult, APIError
from backend.app.db.database import get_db
from backend.app.services.eligibility_service import evaluate_eligibility

router = APIRouter(tags=["Eligibility Checker"])


@router.post("/eligibility", response_model=APIResponse[EligibilityResult])
def check_eligibility(
    req: EligibilityRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate a farmer's eligibility for subsidy schemes.
    Returns a readiness score and a list of recommended schemes.
    """
    try:
        result = evaluate_eligibility(req, db=db)
        return APIResponse(status="ok", data=result, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="ELIGIBILITY_ERROR",
                message=f"Failed to compute eligibility: {str(e)}"
            )
        )


@router.get("/eligibility/checklist", response_model=APIResponse)
def download_checklist(
    scheme_id: str,
    language: str = "en",
    farmer_name: str = "Farmer",
    include_pdf_base64: bool = True,
):
    """
    Generate a PDF checklist for a specific scheme and return it (optionally base‑64 encoded).
    The heavy lifting is done in `backend/app/services/mandi_service.py` – here we just format the response.
    """
    from backend.app.services.mandi_service import generate_checklist_pdf

    try:
        checklist = generate_checklist_pdf(
            scheme_id=scheme_id,
            language=language,
            farmer_name=farmer_name,
            include_pdf_base64=include_pdf_base64,
        )
        return APIResponse(status="ok", data=checklist, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="CHECKLIST_GENERATION_ERROR",
                message=f"Unable to generate checklist: {str(e)}"
            )
        )