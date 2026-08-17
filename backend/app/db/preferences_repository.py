from datetime import UTC, datetime

from app.db.firestore import db
from app.schemas.preferences import OnboardingRequest


def save_preferences(uid: str, preferences: OnboardingRequest) -> None:
    doc_ref = db.collection("users").document(uid).collection("preferences").document("profile")
    data = preferences.model_dump()
    data["updatedAt"] = datetime.now(UTC)
    data["updatedBy"] = "explicit"
    doc_ref.set(data)


def get_preferences(uid: str) -> dict | None:
    doc_ref = db.collection("users").document(uid).collection("preferences").document("profile")
    snapshot = doc_ref.get()
    return snapshot.to_dict() if snapshot.exists else None