import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

import httpx

from app.core.rate_limit import check_and_increment
from app.db.firestore import db

CACHE_TTL = timedelta(hours=24)

FIELD_MASK = "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"

TRAVEL_MODE_MAP = {
    "walk": "WALK",
    "bike": "BICYCLE",
    "transit": "TRANSIT",
    "drive": "DRIVE",
}


def _cache_key(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, travel_mode: str) -> str:
    payload = {
        "origin": [round(origin_lat, 5), round(origin_lng, 5)],
        "destination": [round(dest_lat, 5), round(dest_lng, 5)],
        "mode": travel_mode,
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


async def compute_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    travel_mode: str = "walk",
) -> dict:
    cache_key = _cache_key(origin_lat, origin_lng, dest_lat, dest_lng, travel_mode)
    cache_ref = db.collection("apiCache").document(cache_key)
    cached = cache_ref.get()

    if cached.exists:
        cached_data = cached.to_dict()
        if datetime.now(UTC) - cached_data["cachedAt"] < CACHE_TTL:
            print(f"[RouteProvider] cache hit ({cache_key})")
            return cached_data["route"]

    print(f"[RouteProvider] cache miss ({cache_key}), calling Routes API")
    check_and_increment("routes", max_calls=10, window=timedelta(minutes=1))
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]
    google_travel_mode = TRAVEL_MODE_MAP.get(travel_mode, "WALK")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            json={
                "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
                "destination": {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}},
                "travelMode": google_travel_mode,
                "units": "METRIC",
            },
        )
        response.raise_for_status()
        route = response.json()

    cache_ref.set({"route": route, "cachedAt": datetime.now(UTC)})
    return route