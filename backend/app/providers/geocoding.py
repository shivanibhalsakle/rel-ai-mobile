import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

import httpx

from app.core.rate_limit import check_and_increment
from app.db.firestore import db

CACHE_TTL = timedelta(days=30)


def _cache_key(address: str) -> str:
    payload = {"address": address.strip().lower()}
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


async def geocode_address(address: str) -> dict:
    cache_key = _cache_key(address)
    cache_ref = db.collection("apiCache").document(cache_key)
    cached = cache_ref.get()

    if cached.exists:
        cached_data = cached.to_dict()
        if datetime.now(UTC) - cached_data["cachedAt"] < CACHE_TTL:
            print(f"[GeocodingProvider] cache hit ({cache_key})")
            return cached_data["result"]

    print(f"[GeocodingProvider] cache miss ({cache_key}), calling Geocoding API")
    check_and_increment("geocoding", max_calls=10, window=timedelta(minutes=1))
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": api_key},
        )
        response.raise_for_status()
        result = response.json()

    cache_ref.set({"result": result, "cachedAt": datetime.now(UTC)})
    return result