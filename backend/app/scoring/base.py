from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def clamp01(value: float) -> float:
    """Clamp a value into [0, 1]."""
    return max(0.0, min(1.0, value))


def normalize(value: float, low: float, high: float, invert: bool = False) -> float:
    """Linearly map value from [low, high] to a [0, 1] score, clamped at both ends.
    invert=True - for factors where *lower* raw values are better (e.g. distance). """
    if high == low:
        return 1.0
    score = clamp01((value - low) / (high - low))
    return 1 - score if invert else score


class ScoreComponent(BaseModel):
    """factor that fed into a total score normalized to [0, 1]"""

    factor: str
    score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0)
    detail: str
    confidence: Literal["verified", "estimated"]


class ScoredResult(BaseModel, Generic[T]):

    item: T
    total_score: float = Field(ge=0, le=100)
    components: list[ScoreComponent]
    unavailable_factors: list[str] = Field(default_factory=list)

    @property
    def explanation(self) -> list[str]:
        """Human-readable reasons, ordered by how much each factor
        contributed (weight * score) -- "why we recommend this" UI."""
        ordered = sorted(self.components, key=lambda c: c.weight * c.score, reverse=True)
        return [c.detail for c in ordered]


def weighted_average(components: list[ScoreComponent]) -> float:
    total_weight = sum(c.weight for c in components)
    if total_weight <= 0:
        return 0.0
    return sum(c.score * c.weight for c in components) / total_weight


def to_scored_result(
    item: T,
    components: list[ScoreComponent],
    unavailable_factors: list[str] | None = None,
) -> ScoredResult[T]:
    """converting the [0, 1] weighted average into the [0, 100] scale used in total_score."""
    return ScoredResult[T](
        item=item,
        total_score=round(weighted_average(components) * 100, 1),
        components=components,
        unavailable_factors=unavailable_factors or [],
    )


def rank(results: list[ScoredResult[T]]) -> list[ScoredResult[T]]:
    """Sort scored results highest-first."""
    return sorted(results, key=lambda r: r.total_score, reverse=True)