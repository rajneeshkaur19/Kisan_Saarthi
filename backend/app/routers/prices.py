from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.schemas import APIResponse, PriceRecord, APIError
from backend.app.db.database import get_db
from backend.app.services.mandi_service import get_prices

router = APIRouter(tags=["Mandi Prices"])


@router.get("/prices", response_model=APIResponse[PriceRecord])
def get_prices_endpoint(
    crop: str = Query(..., description="Crop name (e.g., Wheat, Rice)"),
    mandi: str = Query(..., description="Mandi / market name (e.g., ludhiana)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve the latest price record for a given crop at a specific mandi.
    The service falls back to a deterministic “insufficient data” payload when no record is found.
    """
    try:
        result = get_prices(crop=crop, mandi=mandi, db=db)
        # The service already returns a dict matching the PriceRecord schema
        return APIResponse(status="ok", data=result["data"]["selected_record"], error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="PRICE_FETCH_ERROR",
                message=f"Unable to fetch price data: {str(e)}"
            )
        )