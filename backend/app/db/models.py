from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.db.database import Base


class DiagnosisAudit(Base):
    __tablename__ = "diagnosis_audits"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(100), nullable=False, default="Unknown")
    disease_key = Column(String(150), nullable=False, default="unknown")
    confidence = Column(Float, nullable=False, default=0.0)
    is_inconclusive = Column(Boolean, nullable=False, default=True)
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MandiPriceCache(Base):
    __tablename__ = "mandi_price_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    crop = Column(String(100), nullable=False)
    mandi_id = Column(String(100), nullable=False)
    mandi_name = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False, default="")
    state = Column(String(100), nullable=False, default="")
    current_price = Column(Float, nullable=False, default=0.0)
    min_price = Column(Float, nullable=False, default=0.0)
    max_price = Column(Float, nullable=False, default=0.0)
    modal_price = Column(Float, nullable=False, default=0.0)
    recommendation = Column(String(100), nullable=False, default="INSUFFICIENT DATA")
    recommendation_reason = Column(Text, nullable=False, default="")
    trend_percent = Column(Float, nullable=False, default=0.0)
    data_json = Column(Text, nullable=False, default="{}")
    source = Column(String(255), nullable=False, default="Agmarknet")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EligibilityAssessment(Base):
    __tablename__ = "eligibility_assessments"

    id = Column(Integer, primary_key=True, index=True)
    land_acres = Column(Float, nullable=False, default=0.0)
    income_bracket = Column(String(100), nullable=False, default="")
    primary_crop = Column(String(100), nullable=False, default="")
    score = Column(Integer, nullable=False, default=0)
    readiness_label = Column(String(100), nullable=False, default="")
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
