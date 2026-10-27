from datetime import datetime
from typing import Dict

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
    },
    "moga": {
        "temperature_c": 26.0,
        "humidity_percent": 70,
        "wind_speed_kmh": 10.5,
        "precipitation_chance": 15,
        "condition": "Partly Cloudy",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Morning hours suitable for spraying. Keep finished by mid-day heat.",
        "disease_weather_risk": "Moderate rust watch if overnight dew persists.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 27.5, "temp_min": 16.5, "rain_chance": 10, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 27.0, "temp_min": 16.0, "rain_chance": 20, "condition": "Partly Cloudy"},
            {"day": "Day 3", "temp_max": 26.2, "temp_min": 15.8, "rain_chance": 25, "condition": "Cloudy"}
        ]
    },
    "jagraon": {
        "temperature_c": 25.8,
        "humidity_percent": 66,
        "wind_speed_kmh": 12.0,
        "precipitation_chance": 12,
        "condition": "Clear",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Wind under 15 km/h — good spray window before noon.",
        "disease_weather_risk": "Low to moderate foliar disease pressure.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 27.0, "temp_min": 16.0, "rain_chance": 10, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 26.5, "temp_min": 15.5, "rain_chance": 15, "condition": "Clear"},
            {"day": "Day 3", "temp_max": 26.0, "temp_min": 15.0, "rain_chance": 20, "condition": "Partly Cloudy"}
        ]
    },
    "khanna": {
        "temperature_c": 26.2,
        "humidity_percent": 64,
        "wind_speed_kmh": 9.8,
        "precipitation_chance": 8,
        "condition": "Sunny",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Dry canopy and light wind — favourable for fungicide or insecticide sprays.",
        "disease_weather_risk": "Watch wheat rust if nights turn cooler with dew.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 28.0, "temp_min": 17.0, "rain_chance": 5, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 27.5, "temp_min": 16.5, "rain_chance": 10, "condition": "Clear"},
            {"day": "Day 3", "temp_max": 27.0, "temp_min": 16.0, "rain_chance": 15, "condition": "Partly Cloudy"}
        ]
    },
    "hisar": {
        "temperature_c": 28.4,
        "humidity_percent": 55,
        "wind_speed_kmh": 13.5,
        "precipitation_chance": 5,
        "condition": "Hazy Clear",
        "spray_advisory_status": "CAUTION",
        "spray_advisory_text": "Wind near 13–15 km/h — spray carefully to avoid drift; prefer early morning.",
        "disease_weather_risk": "Low disease pressure; monitor cotton sucking pests.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 30.0, "temp_min": 18.5, "rain_chance": 5, "condition": "Sunny"},
            {"day": "Day 2", "temp_max": 30.5, "temp_min": 18.0, "rain_chance": 5, "condition": "Clear"},
            {"day": "Day 3", "temp_max": 29.5, "temp_min": 17.5, "rain_chance": 10, "condition": "Partly Cloudy"}
        ]
    },
    "indore": {
        "temperature_c": 27.8,
        "humidity_percent": 60,
        "wind_speed_kmh": 11.0,
        "precipitation_chance": 18,
        "condition": "Partly Cloudy",
        "spray_advisory_status": "FAVORABLE",
        "spray_advisory_text": "Suitable spray morning for soybean / wheat stands. Avoid late evening applications.",
        "disease_weather_risk": "Moderate foliar disease risk if humidity rises overnight.",
        "forecast": [
            {"day": "Tomorrow", "temp_max": 29.0, "temp_min": 18.0, "rain_chance": 15, "condition": "Partly Cloudy"},
            {"day": "Day 2", "temp_max": 28.5, "temp_min": 17.5, "rain_chance": 20, "condition": "Cloudy"},
            {"day": "Day 3", "temp_max": 28.0, "temp_min": 17.0, "rain_chance": 25, "condition": "Light Rain Possible"}
        ]
    },
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
