from app.schemas.place_candidate import PlaceCandidate
from app.schemas.preferences import WorkspaceNeeds
from app.scoring.base import ScoreComponent, ScoredResult, normalize, to_scored_result

RATING_WEIGHT = 3.0
REVIEW_COUNT_WEIGHT = 1.5
DISTANCE_WEIGHT = 2.0
AFFORDABILITY_WEIGHT = 1.0
AMENITY_WEIGHT_PER_MATCH = 1.5

REVIEW_COUNT_CAP = 500

PRICE_LEVEL_RANK = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}


def score_workspace_candidate(
    candidate: PlaceCandidate,
    travel_minutes: float | None,
    workspace_needs: WorkspaceNeeds | None = None,
    amenities: dict[str, bool] | None = None,
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

    amenity_components, amenity_unavailable = _amenity_score_components(workspace_needs, amenities)
    components.extend(amenity_components)
    unavailable.extend(amenity_unavailable)

    return to_scored_result(item=candidate, components=components, unavailable_factors=unavailable)


def _amenity_score_components(
    workspace_needs: WorkspaceNeeds | None, amenities: dict[str, bool] | None
) -> tuple[list[ScoreComponent], list[str]]:
    components: list[ScoreComponent] = []
    unavailable: list[str] = []

    if workspace_needs is None:
        return components, unavailable

    for need, wanted in workspace_needs.model_dump().items():
        if not wanted:
            continue
        factor = f"amenity_{need}"
        if amenities is not None and need in amenities:
            has_it = amenities[need]
            components.append(
                ScoreComponent(
                    factor=factor,
                    score=1.0 if has_it else 0.0,
                    weight=AMENITY_WEIGHT_PER_MATCH,
                    detail=f"{'Has' if has_it else 'No'} {need}",
                    confidence="verified",
                )
            )
        else:
            unavailable.append(factor)

    return components, unavailable