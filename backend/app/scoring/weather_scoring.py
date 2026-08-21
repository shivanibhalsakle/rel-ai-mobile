from typing import Literal

from app.scoring.base import ScoreComponent, ScoredResult, normalize, to_scored_result

PRECIPITATION_WEIGHT = 4.0
TEMPERATURE_WEIGHT = 3.0
WIND_WEIGHT = 1.5
HUMIDITY_WEIGHT = 1.0
UV_WEIGHT = 1.0
DAYLIGHT_WEIGHT = 1.0

# (taper floor, comfort low, comfort high, taper ceiling), all Celsius.
TEMPERATURE_PREFERENCE_BANDS: dict[str, tuple[float, float, float, float]] = {
    "cold": (-15.0, 2.0, 14.0, 22.0),
    "balanced": (-5.0, 12.0, 24.0, 35.0),
    "hot": (5.0, 22.0, 34.0, 45.0),
}


def score_weather_hour(
    hour_id: str,
    precipitation_probability_percent: float | None = None,
    temperature_celsius: float | None = None,
    temperature_preference: Literal["hot", "balanced", "cold"] = "balanced",
    wind_speed: float | None = None,
    humidity_percent: float | None = None,
    uv_index: float | None = None,
    is_daytime: bool | None = None,
) -> ScoredResult[str]:
    components: list[ScoreComponent] = []
    unavailable: list[str] = []

    if precipitation_probability_percent is not None:
        components.append(
            ScoreComponent(
                factor="precipitation",
                score=normalize(precipitation_probability_percent, low=0, high=100, invert=True),
                weight=PRECIPITATION_WEIGHT,
                detail=f"{precipitation_probability_percent:.0f}% chance of rain",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("precipitation")

    if temperature_celsius is not None:
        components.append(
            ScoreComponent(
                factor="temperature",
                score=_temperature_comfort_score(temperature_celsius, temperature_preference),
                weight=TEMPERATURE_WEIGHT,
                detail=f"{temperature_celsius:.0f}°C ({temperature_preference} preference)",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("temperature")

    if wind_speed is not None:
        components.append(
            ScoreComponent(
                factor="wind",
                score=normalize(wind_speed, low=0, high=40, invert=True),
                weight=WIND_WEIGHT,
                detail=f"Wind speed {wind_speed:.0f} (units as reported by the API, not converted)",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("wind")

    if humidity_percent is not None:
        components.append(
            ScoreComponent(
                factor="humidity",
                score=normalize(humidity_percent, low=0, high=100, invert=True),
                weight=HUMIDITY_WEIGHT,
                detail=f"{humidity_percent:.0f}% humidity",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("humidity")

    if uv_index is not None:
        components.append(
            ScoreComponent(
                factor="uv_index",
                score=normalize(uv_index, low=0, high=11, invert=True),
                weight=UV_WEIGHT,
                detail=f"UV index {uv_index:.0f}",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("uv_index")

    if is_daytime is not None:
        components.append(
            ScoreComponent(
                factor="daylight",
                score=1.0 if is_daytime else 0.5,
                weight=DAYLIGHT_WEIGHT,
                detail="Daytime" if is_daytime else "After dark",
                confidence="verified",
            )
        )
    else:
        unavailable.append("daylight")

    return to_scored_result(item=hour_id, components=components, unavailable_factors=unavailable)


def _temperature_comfort_score(
    temperature_celsius: float, temperature_preference: Literal["hot", "balanced", "cold"]
) -> float:
    cold_floor, comfort_low, comfort_high, hot_ceiling = TEMPERATURE_PREFERENCE_BANDS[
        temperature_preference
    ]
    if comfort_low <= temperature_celsius <= comfort_high:
        return 1.0
    if temperature_celsius < comfort_low:
        return normalize(temperature_celsius, low=cold_floor, high=comfort_low)
    return normalize(temperature_celsius, low=comfort_high, high=hot_ceiling, invert=True)