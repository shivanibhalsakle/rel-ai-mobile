from pydantic import BaseModel


class PlaceCandidate(BaseModel):
    place_id: str
    name: str
    rating: float | None = None
    user_rating_count: int | None = None
    price_level: str | None = None
    types: list[str] = []