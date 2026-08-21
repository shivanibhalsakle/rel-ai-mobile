from app.schemas.place_candidate import PlaceCandidate
from app.scoring.base import ScoreComponent, ScoredResult, normalize, to_scored_result

RATING_WEIGHT = 3.0
REVIEW_COUNT_WEIGHT = 1.5
DISTANCE_WEIGHT = 2.0
AFFORDABILITY_WEIGHT = 1.0
SETTING_WEIGHT = 1.0

REVIEW_COUNT_CAP = 500

PRICE_LEVEL_RANK = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}

OUTDOOR_TYPES = {"park", "hiking_area", "trail"}
INDOOR_TYPES = {"gym", "fitness_center", "yoga_studio"}


def score_fitness_candidate(
    candidate: PlaceCandidate,
    travel_minutes: float | None,
    indoor_outdoor_preference: str = "either",
) -> ScoredResult[PlaceCandidate]:
    components: list[ScoreComponent] = []
    unavailable: list[str] = []

    if candidate.rating is not None:
        components.append(
            ScoreComponent(
                factor="rating",
                score=normalize(candidate.rating, low=1.0, high=5.0),
                weight=RATING_WEIGHT,
                detail=f"Rated {candidate.rating} out of 5",
                confidence="verified",
            )
        )
    else:
        unavailable.append("rating")

    if candidate.user_rating_count is not None:
        capped = min(candidate.user_rating_count, REVIEW_COUNT_CAP)
        components.append(
            ScoreComponent(
                factor="review_count",
                score=normalize(capped, low=0, high=REVIEW_COUNT_CAP),
                weight=REVIEW_COUNT_WEIGHT,
                detail=f"{candidate.user_rating_count} reviews",
                confidence="verified",
            )
        )
    else:
        unavailable.append("review_count")

    if travel_minutes is not None:
        components.append(
            ScoreComponent(
                factor="distance",
                score=normalize(travel_minutes, low=0, high=60, invert=True),
                weight=DISTANCE_WEIGHT,
                detail=f"About {round(travel_minutes)} min away",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("distance")

    if candidate.price_level in PRICE_LEVEL_RANK:
        rank = PRICE_LEVEL_RANK[candidate.price_level]
        label = candidate.price_level.replace("PRICE_LEVEL_", "").title()
        components.append(
            ScoreComponent(
                factor="affordability",
                score=normalize(rank, low=0, high=4, invert=True),
                weight=AFFORDABILITY_WEIGHT,
                detail=f"Price level: {label}",
                confidence="estimated",
            )
        )
    else:
        unavailable.append("affordability")

    setting_score = _setting_match_score(candidate.types, indoor_outdoor_preference)
    if setting_score is not None:
        components.append(
            ScoreComponent(
                factor="setting",
                score=setting_score,
                weight=SETTING_WEIGHT,
                detail=f"Matches your {indoor_outdoor_preference} preference",
                confidence="estimated",
            )
        )

    return to_scored_result(item=candidate, components=components, unavailable_factors=unavailable)


def _setting_match_score(types: list[str], indoor_outdoor_preference: str) -> float | None:
    if indoor_outdoor_preference == "either":
        return None
    type_set = set(types)
    matches_outdoor = bool(type_set & OUTDOOR_TYPES)
    matches_indoor = bool(type_set & INDOOR_TYPES)
    if not matches_outdoor and not matches_indoor:
        return None
    if indoor_outdoor_preference == "outdoor":
        return 1.0 if matches_outdoor else 0.0
    return 1.0 if matches_indoor else 0.0