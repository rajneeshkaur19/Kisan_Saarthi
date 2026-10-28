import json
import os
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import MandiPriceCache


def _normalize_nearby(items: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    normalized = []
    for idx, item in enumerate(items or []):
        price = float(item.get("price", 0) or 0)
        trend = item.get("trend")
        if not trend:
            trend = "+1.2%" if idx % 2 == 0 else "-0.5%"
        normalized.append(
            {
                "mandi": item.get("mandi", "Nearby Mandi"),
                "distance": item.get("distance", f"{12 + idx * 8} km"),
                "price": price,
                "trend": trend,
            }
        )
    return normalized


def _normalize_history(history: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    points = []
    for point in history or []:
        points.append(
            {
                "date": str(point.get("date", "")),
                "price": float(point.get("price", 0) or 0),
                "volume": point.get("volume"),
            }
        )
    return points


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
                    "disclaimer": "Sample APMC data.",
                },
                "commodities": ["Wheat", "Paddy", "Potato", "Tomato", "Cotton", "Soybean", "Onion"],
                "mandis": [],
                "records": {},
            }

    def get_market_prices(
        self,
        crop: Optional[str] = None,
        mandi_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        commodities = self.cache_data.get("commodities", [])
        mandis = self.cache_data.get("mandis", [])
        records = self.cache_data.get("records", {})
        metadata = self.cache_data.get("metadata", {})

        selected_crop = crop if crop else (commodities[0] if commodities else "Wheat")
        valid_mandi_ids = [m["id"] for m in mandis]
        if mandi_id and mandi_id in valid_mandi_ids:
            selected_mandi = mandi_id
        elif "ludhiana" in valid_mandi_ids:
            selected_mandi = "ludhiana"
        elif mandis:
            selected_mandi = mandis[0]["id"]
        else:
            selected_mandi = mandi_id or "ludhiana"

        record_key = f"{selected_mandi}_{selected_crop}"
        record = records.get(record_key)

        if not record:
            for _, rec in records.items():
                if rec.get("crop", "").lower() == selected_crop.lower():
                    record = dict(rec)
                    break

        if not record:
            mandi_meta = next((m for m in mandis if m["id"] == selected_mandi), None)
            record = {
                "crop": selected_crop,
                "mandi": (mandi_meta["name"] if mandi_meta else f"{selected_mandi.capitalize()} APMC"),
                "district": mandi_meta["district"] if mandi_meta else "Unknown",
                "state": mandi_meta["state"] if mandi_meta else "Unknown",
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
                "recommendation_reason": (
                    f"No recent verified APMC market arrivals or auction records found "
                    f"for {selected_crop} at {selected_mandi}."
                ),
                "trend_percent": 0.0,
                "trend_direction": "neutral",
                "history": [],
                "nearby_comparisons": [],
                "source": metadata.get("source", "Agmarknet"),
                "source_type": metadata.get("source_type", "CACHED_OFFICIAL_RECORDS"),
                "is_cached": True,
            }
        else:
            record = dict(record)
            record["source"] = metadata.get("source", "Agmarknet")
            record["source_type"] = metadata.get("source_type", "CACHED_OFFICIAL_RECORDS")
            record["is_cached"] = True
            record["history"] = _normalize_history(record.get("history"))
            record["nearby_comparisons"] = _normalize_nearby(record.get("nearby_comparisons"))

            history = record.get("history", [])
            if len(history) < 3 and record.get("recommendation") != "INSUFFICIENT DATA":
                record["recommendation"] = "INSUFFICIENT DATA"
                record["recommendation_reason"] = (
                    "Fewer than 3 historical observations available to establish "
                    "a statistically reliable price trajectory."
                )

        if db is not None and record["current_price"] > 0:
            try:
                existing = (
                    db.query(MandiPriceCache)
                    .filter(MandiPriceCache.cache_key == record_key)
                    .first()
                )
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
                        source=record["source"],
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
            "disclaimer": metadata.get(
                "disclaimer",
                "Indicative APMC prices for guidance. Verify at the mandi before selling.",
            ),
        }


_mandi_service = None


def get_mandi_service() -> MandiService:
    global _mandi_service
    if _mandi_service is None:
        _mandi_service = MandiService()
    return _mandi_service


def get_prices(crop: str, mandi: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Return full PricesData-compatible payload for the prices API."""
    return get_mandi_service().get_market_prices(crop=crop, mandi_id=mandi, db=db)
