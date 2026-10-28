from fastapi import APIRouter, Query
from backend.app.schemas import APIResponse, WeatherData, APIError
from backend.app.services.weather_service import get_weather

router = APIRouter(tags=["Weather"])


@router.get("/weather", response_model=APIResponse[WeatherData])
def get_weather_endpoint(
    district: str = Query(..., description="Indian district name (e.g., ludhiana)")
):
    """
    Return current weather conditions for the requested district.
    If the OPENWEATHER_API_KEY is missing, a deterministic demo payload is returned.
    """
    try:
        data = get_weather(district=district)
        return APIResponse(status="ok", data=data, error=None)
    except Exception as e:
        return APIResponse(
            status="error",
            data=None,
            error=APIError(
                code="WEATHER_FETCH_ERROR",
                message=f"Failed to retrieve weather for {district}: {str(e)}"
            )
        )