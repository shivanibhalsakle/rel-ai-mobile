from app.scoring.base import ScoreComponent, ScoredResult, normalize, to_scored_result

DISTANCE_TARGET_WEIGHT = 4.0
DURATION_TARGET_WEIGHT = 3.0
PARK_COVERAGE_WEIGHT = 2.0
ROAD_EXPOSURE_WEIGHT = 3.0
WEATHER_COMFORT_WEIGHT = 2.0

# A route this far off-target (as a fraction of the target) scores 0 on that factor.
TARGET_TOLERANCE = 0.5


def score_route_candidate(
    route_id: str,
    actual_distance_meters: float,
    actual_duration_seconds: float,
    target_distance_meters: float | None = None,
    target_duration_seconds: float | None = None,
    park_coverage_ratio: float | None = None,
    road_exposure_ratio: float | None = None,
    weather_comfort_score: float | None = None,
) -> ScoredResult[str]:
    components: list[ScoreComponent] = []
    unavailable: list[str] = []

    if target_distance_meters is not None:
        deviation = abs(actual_distance_meters - target_distance_meters) / target_distance_meters
        components.append(
            ScoreComponent(
                factor="distance_target",
                score=normalize(deviation, low=0, high=TARGET_TOLERANCE, invert=True),
                weight=DISTANCE_TARGET_WEIGHT,
                detail=f"{actual_distance_meters / 1000:.1f} km (target: {target_distance_meters / 1000:.1f} km)",
                confidence="verified",
            )
        )

    if target_duration_seconds is not None:
        deviation = abs(actual_duration_seconds - target_duration_seconds) / target_duration_seconds
        components.append(
            ScoreComponent(
                factor="duration_target",
                score=normalize(deviation, low=0, high=TARGET_TOLERANCE, invert=True),
                weight=DURATION_TARGET_WEIGHT,
                detail=f"{actual_duration_seconds / 60:.0f} min (target: {target_duration_seconds / 60:.0f} min)",
                confidence="verified",
            )
        )

    if park_coverage_ratio is not None:
        components.append(
            ScoreComponent(
                factor="park_coverage",
                score=normalize(park_coverage_ratio, low=0, high=1),
                weight=PARK_COVERAGE_WEIGHT,
                detail=f"{park_coverage_ratio:.0%} through parks/green space",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("park_coverage")

    if road_exposure_ratio is not None:
        components.append(
            ScoreComponent(
                factor="road_exposure",
                score=normalize(road_exposure_ratio, low=0, high=1, invert=True),
                weight=ROAD_EXPOSURE_WEIGHT,
                detail="Lower-traffic based on available data -- not a safety guarantee",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("road_exposure")

    if weather_comfort_score is not None:
        components.append(
            ScoreComponent(
                factor="weather_comfort",
                score=weather_comfort_score,
                weight=WEATHER_COMFORT_WEIGHT,
                detail="Weather comfort for this time window",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("weather_comfort")

    return to_scored_result(item=route_id, components=components, unavailable_factors=unavailable)