from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas import APIResponse, PricesData, APIError
from app.db.database import get_db
from app.services.mandi_service import get_prices

router = APIRouter(tags=["Mandi Prices"])


@router.get("/prices", response_model=APIResponse[PricesData])
def get_prices_endpoint(
    crop: str = Query("Wheat", description="Crop name (e.g., Wheat, Paddy)"),
    mandi: str = Query("ludhiana", description="Mandi id (e.g., ludhiana)"),
    db: Session = Depends(get_db),
):
    """Return selected mandi price plus available crop/mandi options."""
    try:
        result = get_prices(crop=crop, mandi=mandi, db=db)
        return APIResponse(status="ok", data=PricesData(**result), error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="PRICE_FETCH_ERROR",
                message=f"Unable to fetch price data: {str(e)}",
            ),
        )
