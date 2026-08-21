import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

import httpx

from app.core.rate_limit import check_and_increment
from app.db.firestore import db

CACHE_TTL = timedelta(hours=1)


def _cache_key(latitude: float, longitude: float, hours: int) -> str:
    payload = {"lat": round(latitude, 3), "lng": round(longitude, 3), "hours": hours}
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_hourly_forecast(latitude: float, longitude: float, hours: int = 24) -> dict:
    cache_key = _cache_key(latitude, longitude, hours)
    cache_ref = db.collection("apiCache").document(cache_key)
    cached = cache_ref.get()

    if cached.exists:
        cached_data = cached.to_dict()
        if datetime.now(UTC) - cached_data["cachedAt"] < CACHE_TTL:
            print(f"[WeatherProvider] cache hit ({cache_key})")
            return cached_data["forecast"]

    print(f"[WeatherProvider] cache miss ({cache_key}), calling Weather API")
    check_and_increment("weather", max_calls=10, window=timedelta(minutes=1))
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://weather.googleapis.com/v1/forecast/hours:lookup",
            params={
                "key": api_key,
                "location.latitude": latitude,
                "location.longitude": longitude,
                "hours": hours,
            },
        )
        response.raise_for_status()
        forecast = response.json()

    cache_ref.set({"forecast": forecast, "cachedAt": datetime.now(UTC)})
    return forecast