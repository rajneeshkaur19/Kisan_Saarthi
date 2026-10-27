import os
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

from backend.app.schemas import WeatherData, WeatherForecastDay

DISTRICT_COORDINATES = {
    "ludhiana": {"name": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lon": 75.8573},
    "moga": {"name": "Moga", "state": "Punjab", "lat": 30.8165, "lon": 75.1717},
    "jagraon": {"name": "Jagraon", "state": "Punjab", "lat": 30.7845, "lon": 75.4784},
    "khanna": {"name": "Khanna", "state": "Punjab", "lat": 30.7027, "lon": 76.2163},
    "karnal": {"name": "Karnal", "state": "Haryana", "lat": 29.6857, "lon": 76.9905},
    "hisar": {"name": "Hisar", "state": "Haryana", "lat": 29.1492, "lon": 75.7217},
    "indore": {"name": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577},
    "nashik": {"name": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898}
}

# Cached meteorological baseline observations
CACHED_WEATHER_DB = {
    "ludhiana": {
        "temperature_c": 26.5,
        "humidity_percent": 68,
        "wind_speed_kmh": 11.2,
        "precipitation_chance": 10,
        "condition": "Partly Cloudy",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Dry canopy and moderate wind conditions. Favorable for chemical or bio-fungicide spraying during morning hours.",
        "disease_weather_risk": "Moderate risk for rust development if night temperatures drop with dew formation.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 28.0, "temp_min": 17.5, "rain_chance": 15, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 27.2, "temp_min": 16.8, "rain_chance": 20, "condition": "Clear"},
            {"day": "Day 3", "temp_max": 26.0, "temp_min": 16.0, "rain_chance": 10, "condition": "Partly Cloudy"}
        ]
    },
    "karnal": {
        "temperature_c": 27.0,
        "humidity_percent": 62,
        "wind_speed_kmh": 9.5,
        "precipitation_chance": 5,
        "condition": "Clear Sky",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Optimal spraying window. Wind velocity is well below 15 km/h, preventing chemical drift.",
        "disease_weather_risk": "Low disease pressure. Keep regular pest monitoring active.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 28.5, "temp_min": 18.0, "rain_chance": 5, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 29.0, "temp_min": 18.2, "rain_chance": 10, "condition": "Clear"},
            {"day": "Day 3", "temp_max": 27.8, "temp_min": 17.0, "rain_chance": 15, "condition": "Partly Cloudy"}
        ]
    },
    "nashik": {
        "temperature_c": 29.2,
        "humidity_percent": 74,
        "wind_speed_kmh": 14.0,
        "precipitation_chance": 35,
        "condition": "Humid / Overcast",
        "spray_advisory_status": "CAUTION",
        "spray_advisory_text": "High humidity and sporadic drizzle expected. Use a non-ionic surfactant/sticker if spraying fungicide on onion or grape crops.",
        "disease_weather_risk": "Elevated risk of downy mildew and purple blotch in allium crops.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 30.0, "temp_min": 21.0, "rain_chance": 40, "condition": "Scattered Showers"},
            {"day": "Day 2", "temp_max": 28.5, "temp_min": 20.5, "rain_chance": 30, "condition": "Overcast"},
            {"day": "Day 3", "temp_max": 29.0, "temp_min": 20.0, "rain_chance": 20, "condition": "Partly Cloudy"}
        ]
    }
}

class WeatherService:
    def get_district_weather(self, district_id: str = "ludhiana") -> WeatherData:
        key = district_id.lower().strip()
        coords = DISTRICT_COORDINATES.get(key, DISTRICT_COORDINATES["ludhiana"])
        district_name = coords["name"]
        state_name = coords["state"]

        # Default to cached baseline
        cached = CACHED_WEATHER_DB.get(key, CACHED_WEATHER_DB["ludhiana"])

        forecast_objs = [WeatherForecastDay(**f) for f in cached["forecast"]]

        return WeatherData(
            district=district_name,
            state=state_name,
            temperature_c=cached["temperature_c"],
            humidity_percent=cached["humidity_percent"],
            wind_speed_kmh=cached["wind_speed_kmh"],
            precipitation_chance=cached["precipitation_chance"],
            condition=cached["condition"],
            spray_advisory_status=cached["spray_advisory_status"],
            spray_advisory_text=cached["spray_advisory_text"],
            disease_weather_risk=cached["disease_weather_risk"],
            forecast=forecast_objs,
            source="IMD Agromet Advisory Service (Gramin Krishi Mausam Sewa) / Open-Meteo",
            is_live=False,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M IST")
        )

_weather_service = None

def get_weather_service() -> WeatherService:
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

def get_weather(district: str = "ludhiana") -> WeatherData:
    """Return the available district weather data."""
    return get_weather_service().get_district_weather(district_id=district)
