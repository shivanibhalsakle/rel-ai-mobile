from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.rate_limit import RateLimitExceeded
from app.providers.places import search_nearby_places


async def test_cache_hit_skips_http_call():
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {
        "places": [{"id": "abc123"}],
        "cachedAt": datetime.now(UTC),
    }

    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = mock_snapshot

    with (
        patch("app.providers.places.db", mock_db),
        patch("httpx.AsyncClient") as mock_client_class,
    ):
        result = await search_nearby_places(
            latitude=40.7580, longitude=-73.9855, radius_meters=1500, included_types=["gym"]
        )

    assert result == [{"id": "abc123"}]
    mock_client_class.assert_not_called()


async def test_cache_miss_calls_api_and_writes_cache(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")

    mock_snapshot = MagicMock()
    mock_snapshot.exists = False

    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_snapshot

    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json.return_value = {"places": [{"id": "xyz789"}]}

    mock_client = AsyncMock()
    mock_client.post.return_value = fake_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with (
        patch("app.providers.places.db", mock_db),
        patch("app.providers.places.check_and_increment"),
        patch("httpx.AsyncClient", return_value=mock_client),
    ):
        result = await search_nearby_places(
            latitude=40.7580, longitude=-73.9855, radius_meters=1500, included_types=["gym"]
        )

    assert result == [{"id": "xyz789"}]
    mock_doc_ref.set.assert_called_once()


async def test_rate_limit_exceeded_propagates(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-key")

    mock_snapshot = MagicMock()
    mock_snapshot.exists = False
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = mock_snapshot

    with ( patch("app.providers.places.db", mock_db), patch(  # noqa: SIM117
        "app.providers.places.check_and_increment", side_effect=RateLimitExceeded("too many calls"),
        ),
    ):
        with pytest.raises(RateLimitExceeded):
            await search_nearby_places(
                latitude=40.7580, longitude=-73.9855, radius_meters=1500, included_types=["gym"]
            )