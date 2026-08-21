import asyncio

from dotenv import load_dotenv

from app.providers.places import FIELD_MASK, search_nearby_places
from app.providers.weather import get_hourly_forecast

load_dotenv()

# Times Square, NYC
TEST_LATITUDE = 40.7580
TEST_LONGITUDE = -73.9855


async def main():
    print(f"Places field mask in use: {FIELD_MASK}\n")

    print("=== Places: first call (expect cache miss) ===")
    places = await search_nearby_places(
        latitude=TEST_LATITUDE,
        longitude=TEST_LONGITUDE,
        radius_meters=1500,
        included_types=["gym"],
    )
    print(f"Got {len(places)} places")

    print("\n=== Places: second call, same params (expect cache hit) ===")
    places_again = await search_nearby_places(
        latitude=TEST_LATITUDE,
        longitude=TEST_LONGITUDE,
        radius_meters=1500,
        included_types=["gym"],
    )
    print(f"Got {len(places_again)} places")

    print("\n=== Weather: first call (expect cache miss) ===")
    forecast = await get_hourly_forecast(latitude=TEST_LATITUDE, longitude=TEST_LONGITUDE, hours=6)
    print(f"Forecast response keys: {list(forecast.keys())}")

    print("\n=== Weather: second call, same params (expect cache hit) ===")
    forecast_again = await get_hourly_forecast(latitude=TEST_LATITUDE, longitude=TEST_LONGITUDE, hours=6)
    print(f"Forecast response keys: {list(forecast_again.keys())}")


if __name__ == "__main__":
    asyncio.run(main())