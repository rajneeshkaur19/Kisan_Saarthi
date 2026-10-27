from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.schemas import (
    APIResponse,
    EligibilityRequest,
    EligibilityData,
    ChecklistRequest,
    ChecklistData,
    APIError,
)
from backend.app.db.database import get_db
from backend.app.services.eligibility_service import (
    evaluate_eligibility,
    get_eligibility_service,
)

router = APIRouter(tags=["Eligibility Checker"])


@router.post("/eligibility", response_model=APIResponse[EligibilityData])
def check_eligibility(
    req: EligibilityRequest,
    db: Session = Depends(get_db),
):
    """Evaluate a farmer's eligibility for subsidy schemes."""
    try:
        result = evaluate_eligibility(req, db=db)
        return APIResponse(status="ok", data=result, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="ELIGIBILITY_ERROR",
                message=f"Failed to compute eligibility: {str(e)}",
            ),
        )


def _build_checklist(req: ChecklistRequest) -> ChecklistData:
    return get_eligibility_service().get_document_checklist(req)


@router.post("/checklist", response_model=APIResponse[ChecklistData])
def create_checklist(req: ChecklistRequest):
    """Generate a document checklist (and optional PDF) for a scheme."""
    try:
        checklist = _build_checklist(req)
        return APIResponse(status="ok", data=checklist, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="CHECKLIST_GENERATION_ERROR",
                message=f"Unable to generate checklist: {str(e)}",
            ),
        )


@router.get("/eligibility/checklist", response_model=APIResponse[ChecklistData])
def download_checklist(
    scheme_id: str,
    language: str = "en",
    farmer_name: str = "Farmer",
    include_pdf_base64: bool = True,
):
    """GET alias used by older clients for checklist download."""
    try:
        checklist = _build_checklist(
            ChecklistRequest(
                scheme_id=scheme_id,
                language=language,
                farmer_name=farmer_name,
                include_pdf_base64=include_pdf_base64,
            )
        )
        return APIResponse(status="ok", data=checklist, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="CHECKLIST_GENERATION_ERROR",
                message=f"Unable to generate checklist: {str(e)}",
            ),
        )
