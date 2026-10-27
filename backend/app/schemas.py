from typing import List, Optional, Any, Dict, Generic, TypeVar
from pydantic import BaseModel, Field

# Generic type variable for APIResponse
T = TypeVar("T")


# ----------------------------------------------------------------------
# Standard API envelope
# ----------------------------------------------------------------------
class APIError(BaseModel):
    """Structured error information returned by the API."""
    code: str
    message: str
    details: Optional[Any] = None


class APIResponse(BaseModel, Generic[T]):
    """Wraps any successful payload or an error."""
    status: str = "ok"
    data: Optional[T] = None
    error: Optional[APIError] = None


# ----------------------------------------------------------------------
# Health endpoint
# ----------------------------------------------------------------------
class HealthData(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    version: str
    environment: str
    model_loaded: bool
    rag_indexed_chunks: int
    database_connected: bool


# ----------------------------------------------------------------------
# Crop‑Doctor (diagnosis) models
# ----------------------------------------------------------------------
class CandidatePrediction(BaseModel):
    class_key: str
    confidence: float


class DiagnoseData(BaseModel):
    model_config = {"protected_namespaces": ()}
    disease_key: str
    disease_name: str
    crop: str
    confidence_score: float
    confidence_percent: float
    severity: str
    is_inconclusive: bool
    is_uncertain: bool
    symptoms: str
    treatment_steps: List[str]
    prevention: Optional[str] = None
    caution: str
    related_schemes: List[str]
    mandi_crop: str
    top_candidates: List[CandidatePrediction]
    model_version: str
    model_loaded: bool
    source_attribution: str = "MobileNetV2 Transfer Learning on PlantVillage Botanical Dataset"


# ----------------------------------------------------------------------
# Mandi price models
# ----------------------------------------------------------------------
class PriceHistoryPoint(BaseModel):
    date: str
    price: float
    volume: Optional[float] = None


class NearbyMandiPrice(BaseModel):
    mandi: str
    distance: str
    price: float
    trend: str


class PriceRecord(BaseModel):
    crop: str
    mandi: str
    district: str
    state: str
    variety: str
    unit: str
    current_price: float
    min_price: float
    max_price: float
    modal_price: float
    msp_benchmark: float
    arrivals_tonnes: float
    last_updated: str
    recommendation: str  # "SELL", "HOLD", "INSUFFICIENT DATA"
    recommendation_reason: str
    trend_percent: float
    trend_direction: str  # "up", "down", "neutral"
    history: List[PriceHistoryPoint]
    nearby_comparisons: List[NearbyMandiPrice]
    source: str
    source_type: str
    is_cached: bool


class MandiMetadata(BaseModel):
    id: str
    name: str
    district: str
    state: str


# ----------------------------------------------------------------------
# Weather & Agromet advisory models
# ----------------------------------------------------------------------
class WeatherForecastDay(BaseModel):
    day: str
    temp_max: float
    temp_min: float
    rain_chance: int
    condition: str


class WeatherData(BaseModel):
    district: str
    state: str
    temperature_c: float
    humidity_percent: int
    wind_speed_kmh: float
    precipitation_chance: int
    condition: str
    spray_advisory_status: str  # "FAVORABLE", "UNFAVORABLE", "CAUTION"
    spray_advisory_text: str
    disease_weather_risk: str
    forecast: List[WeatherForecastDay]
    source: str
    is_live: bool
    last_updated: str


class PricesData(BaseModel):
    selected_record: Optional[PriceRecord] = None
    available_crops: List[str]
    available_mandis: List[MandiMetadata]
    source: str
    source_type: str
    last_synced: str
    disclaimer: str


# ----------------------------------------------------------------------
# Eligibility / Loan‑scheme models
# ----------------------------------------------------------------------
class EligibilityRequest(BaseModel):
    land_holding_acres: float = Field(..., ge=0, description="Land holding in acres")
    annual_income: str = Field(
        ...,
        description="Income bracket: '< 1 lakh', '1 - 3 lakh', '3 - 6 lakh', '> 6 lakh'"
    )
    primary_crop: str = Field(..., description="Crop grown, e.g. Wheat, Paddy, Potato")
    existing_loan_status: str = Field(
        ...,
        description="one of: 'no_active_loan', 'active_kcc_loan_good_standing', "
                    "'active_formal_loan', 'informal_debt'"
    )
    bank_account_status: str = Field(
        ...,
        description="one of: 'aadhaar_linked_dbt', 'bank_account_no_dbt', 'no_formal_account'"
    )
    language: str = "en"


class ReadinessScore(BaseModel):
    score: int
    max_score: int = 100
    label: str
    badge_color: str
    summary: str
    breakdown: Dict[str, int]
    improvement_tips: List[str]


class EligibleScheme(BaseModel):
    id: str
    code: str
    name: str
    short_name: str
    category: str
    financial_benefit: str
    is_eligible: bool
    match_reason: str
    required_documents: List[str]
    portal: str


class EligibilityData(BaseModel):
    readiness_score: ReadinessScore
    recommended_schemes: List[EligibleScheme]
    other_schemes: List[EligibleScheme]
    official_disclaimer: str


# ----------------------------------------------------------------------
# Checklist‑download models
# ----------------------------------------------------------------------
class ChecklistRequest(BaseModel):
    scheme_id: str
    language: str = "en"
    farmer_name: Optional[str] = "Farmer"
    include_pdf_base64: bool = False


class DocumentItem(BaseModel):
    id: str
    name: str
    description: str
    mandatory: bool


class ChecklistData(BaseModel):
    scheme_id: str
    scheme_name: str
    title: str
    portal: str
    official_helpline: str
    required_documents: List[DocumentItem]
    submission_steps: List[str]
    pdf_base64: Optional[str] = None
    printable_text: str


# ----------------------------------------------------------------------
# Chat / “Ask Saarthi” models
# ----------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: str = "en"
    history: Optional[List[Dict[str, str]]] = []


class RetrievedPassage(BaseModel):
    score: float
    title: str
    section: str
    content: str
    source: str


class ChatData(BaseModel):
    response: str
    sources: List[str]
    retrieved_passages: List[RetrievedPassage]
    confidence: str
    language: str
    is_fallback: bool
    suggestions: List[str]