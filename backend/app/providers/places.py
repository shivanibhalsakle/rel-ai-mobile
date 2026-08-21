import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

import httpx

from app.db.firestore import db

CACHE_TTL = timedelta(hours=24)

FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.location,"
    "places.rating,places.userRatingCount,places.priceLevel,places.types"
)


def _cache_key(latitude: float, longitude: float, radius_meters: int, included_types: list[str]) -> str:
    payload = {
        "lat": round(latitude, 3),
        "lng": round(longitude, 3),
        "radius": radius_meters,
        "types": sorted(included_types),
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()

async def search_nearby_places(
    latitude: float,
    longitude: float,
    radius_meters: int,
    included_types: list[str],
) -> list[dict]:
    cache_key = _cache_key(latitude, longitude, radius_meters, included_types)
    cache_ref = db.collection("apiCache").document(cache_key)
    cached = cache_ref.get()

    if cached.exists:
        cached_data = cached.to_dict()
        if datetime.now(UTC) - cached_data["cachedAt"] < CACHE_TTL:
            print(f"[PlacesProvider] cache hit ({cache_key})")
            return cached_data["places"]

    print(f"[PlacesProvider] cache miss ({cache_key}), calling Places API")
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://places.googleapis.com/v1/places:searchNearby",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            json={
                "includedTypes": included_types,
                "maxResultCount": 20,
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": latitude, "longitude": longitude},
                        "radius": radius_meters,
                    }
                },
            },
        )
        response.raise_for_status()
        places = response.json().get("places", [])

    cache_ref.set({"places": places, "cachedAt": datetime.now(UTC)})
    return places