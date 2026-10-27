import os
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db.models import MandiPriceCache

class MandiService:
    def __init__(self):
        self.cached_file = os.path.join(settings.DATA_DIR, "cached_prices.json")
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cached_file):
            with open(self.cached_file, "r", encoding="utf-8") as f:
                self.cache_data = json.load(f)
        else:
            self.cache_data = {
                "metadata": {
                    "source": "Agmarknet (Ministry of Agriculture & Farmers Welfare)",
                    "source_type": "CACHED_OFFICIAL_RECORDS",
                    "last_synced": "2026-10-26T18:00:00+05:30",
                    "disclaimer": "Sample APMC data."
                },
                "commodities": ["Wheat", "Paddy", "Potato", "Tomato", "Cotton", "Soybean", "Onion"],
                "mandis": [],
                "records": {}
            }

    def get_market_prices(
        self,
        crop: Optional[str] = None,
        mandi_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        commodities = self.cache_data.get("commodities", [])
        mandis = self.cache_data.get("mandis", [])
        records = self.cache_data.get("records", {})
        metadata = self.cache_data.get("metadata", {})

        # Crop & mandi selection: preserve explicit user query, default only if omitted
        selected_crop = crop if crop else (commodities[0] if commodities else "Wheat")
        valid_mandi_ids = [m["id"] for m in mandis]
        selected_mandi = mandi_id if mandi_id else ("ludhiana" if "ludhiana" in valid_mandi_ids else (mandis[0]["id"] if mandis else "ludhiana"))

        record_key = f"{selected_mandi}_{selected_crop}"
        record = records.get(record_key)

        # Fallback search if exact pair not found
        if not record:
            # Look for any record with matching crop
            for k, rec in records.items():
                if rec.get("crop", "").lower() == selected_crop.lower():
                    record = rec
                    break

        # If still no record, construct an INSUFFICIENT DATA notice
        if not record:
            record = {
                "crop": selected_crop,
                "mandi": selected_mandi.capitalize() + " APMC",
                "district": "Unknown",
                "state": "Unknown",
                "variety": "Common Variety",
                "unit": "₹ / quintal",
                "current_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "modal_price": 0.0,
                "msp_benchmark": 0.0,
                "arrivals_tonnes": 0.0,
                "last_updated": metadata.get("last_synced", "N/A"),
                "recommendation": "INSUFFICIENT DATA",
                "recommendation_reason": f"No recent verified APMC market arrivals or auction records found for {selected_crop} at {selected_mandi}.",
                "trend_percent": 0.0,
                "trend_direction": "neutral",
                "history": [],
                "nearby_comparisons": [],
                "source": metadata.get("source", "Agmarknet"),
                "source_type": metadata.get("source_type", "CACHED_OFFICIAL_RECORDS"),
                "is_cached": True
            }
        else:
            # Ensure metadata flags are populated
            record["source"] = metadata.get("source", "Agmarknet")
            record["source_type"] = metadata.get("source_type", "CACHED_OFFICIAL_RECORDS")
            record["is_cached"] = True

            # Evaluate decision logic
            history = record.get("history", [])
            if len(history) < 3:
                record["recommendation"] = "INSUFFICIENT DATA"
                record["recommendation_reason"] = "Fewer than 3 historical observations available to establish a statistically reliable price trajectory."

        # Optionally save to SQLite cache
        if db is not None and record["current_price"] > 0:
            try:
                existing = db.query(MandiPriceCache).filter(MandiPriceCache.cache_key == record_key).first()
                if not existing:
                    new_cache = MandiPriceCache(
                        cache_key=record_key,
                        crop=record["crop"],
                        mandi_id=selected_mandi,
                        mandi_name=record["mandi"],
                        district=record.get("district", ""),
                        state=record.get("state", ""),
                        current_price=record["current_price"],
                        min_price=record["min_price"],
                        max_price=record["max_price"],
                        modal_price=record["modal_price"],
                        recommendation=record["recommendation"],
                        recommendation_reason=record["recommendation_reason"],
                        trend_percent=record["trend_percent"],
                        data_json=json.dumps(record),
                        source=record["source"]
                    )
                    db.add(new_cache)
                    db.commit()
            except Exception as e:
                db.rollback()
                print(f"[MandiCache] DB sync error: {e}")

        return {
            "selected_record": record,
            "available_crops": commodities,
            "available_mandis": mandis,
            "source": metadata.get("source", "Agmarknet"),
            "source_type": metadata.get("source_type", "CACHED_OFFICIAL_RECORDS"),
            "last_synced": metadata.get("last_synced", "N/A"),
            "disclaimer": metadata.get("disclaimer", "Indicative APMC prices.")
        }

_mandi_service = None

def get_mandi_service() -> MandiService:
    global _mandi_service
    if _mandi_service is None:
        _mandi_service = MandiService()
    return _mandi_service
def get_prices(crop: str, mandi: str, db: Optional[Session] = None) -> Dict[str, Any]:
    service = get_mandi_service()
    result = service.get_market_prices(
        crop=crop,
        mandi_id=mandi,
        db=db,
    )
    return result["selected_record"]
