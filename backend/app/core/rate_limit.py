from datetime import UTC, datetime, timedelta

from app.db.firestore import db


class RateLimitExceeded(Exception):
    pass


def check_and_increment(provider_name: str, max_calls: int, window: timedelta) -> None:
    window_start = datetime.now(UTC) - window
    doc_ref = db.collection("rateLimits").document(provider_name)
    doc = doc_ref.get()

    if doc.exists:
        call_times = [t for t in doc.to_dict().get("callTimes", []) if t > window_start]
    else:
        call_times = []

    if len(call_times) >= max_calls:
        raise RateLimitExceeded(f"{provider_name} exceeded {max_calls} calls per {window}")

    call_times.append(datetime.now(UTC))
    doc_ref.set({"callTimes": call_times})