from app.schemas.place_candidate import PlaceCandidate
from app.schemas.preferences import WorkspaceNeeds
from app.scoring.fitness_scoring import score_fitness_candidate
from app.scoring.route_scoring import score_route_candidate
from app.scoring.weather_scoring import score_weather_hour
from app.scoring.workspace_scoring import score_workspace_candidate


def _candidate(**overrides) -> PlaceCandidate:
        defaults = {
        "place_id": "p1",
        "name": "Test Place",
        "rating": 4.0,
        "user_rating_count": 100,
        "price_level": "PRICE_LEVEL_MODERATE",
        "types": ["gym"],
    }
        defaults.update(overrides)
        return PlaceCandidate(**defaults)


class TestFitnessScoring:
    def test_higher_rating_scores_higher(self):
        better = score_fitness_candidate(_candidate(rating=4.8), travel_minutes=15)
        worse = score_fitness_candidate(_candidate(rating=3.0), travel_minutes=15)
        assert better.total_score > worse.total_score

    def test_closer_distance_scores_higher(self):
        closer = score_fitness_candidate(_candidate(), travel_minutes=5)
        farther = score_fitness_candidate(_candidate(), travel_minutes=45)
        assert closer.total_score > farther.total_score

    def test_missing_rating_is_unavailable_not_penalized(self):
        result = score_fitness_candidate(_candidate(rating=None), travel_minutes=15)
        assert "rating" in result.unavailable_factors
        assert all(c.factor != "rating" for c in result.components)

    def test_setting_match_increases_score(self):
        matching = score_fitness_candidate(
            _candidate(types=["gym"]), travel_minutes=15, indoor_outdoor_preference="indoor"
        )
        no_preference = score_fitness_candidate(
            _candidate(types=["gym"]), travel_minutes=15, indoor_outdoor_preference="either"
        )
        assert matching.total_score >= no_preference.total_score

    def test_no_signal_setting_not_penalized(self):
        result = score_fitness_candidate(
            _candidate(types=["restaurant"]), travel_minutes=15, indoor_outdoor_preference="indoor"
        )
        assert all(c.factor != "setting" for c in result.components)


class TestWorkspaceScoring:
    def test_amenity_match_increases_score(self):
        needs = WorkspaceNeeds(wifi=True, quiet=True)
        with_amenities = score_workspace_candidate(
            _candidate(), travel_minutes=15, workspace_needs=needs, amenities={"wifi": True, "quiet": True}
        )
        without_amenity_data = score_workspace_candidate(
            _candidate(), travel_minutes=15, workspace_needs=needs, amenities=None
        )
        assert with_amenities.total_score > without_amenity_data.total_score

    def test_unmatched_amenity_lowers_score(self):
        needs = WorkspaceNeeds(wifi=True)
        has_wifi = score_workspace_candidate(
            _candidate(), travel_minutes=15, workspace_needs=needs, amenities={"wifi": True}
        )
        no_wifi = score_workspace_candidate(
            _candidate(), travel_minutes=15, workspace_needs=needs, amenities={"wifi": False}
        )
        assert has_wifi.total_score > no_wifi.total_score

    def test_unknown_amenity_marked_unavailable(self):
        needs = WorkspaceNeeds(wifi=True)
        result = score_workspace_candidate(
            _candidate(), travel_minutes=15, workspace_needs=needs, amenities=None
        )
        assert "amenity_wifi" in result.unavailable_factors


class TestRouteScoring:
    def test_closer_to_target_distance_scores_higher(self):
        close = score_route_candidate(
            "r1", actual_distance_meters=5000, actual_duration_seconds=1800, target_distance_meters=5000
        )
        far = score_route_candidate(
            "r2", actual_distance_meters=8000, actual_duration_seconds=1800, target_distance_meters=5000
        )
        assert close.total_score > far.total_score

    def test_more_park_coverage_scores_higher(self):
        more_park = score_route_candidate(
            "r1", actual_distance_meters=5000, actual_duration_seconds=1800, park_coverage_ratio=0.8
        )
        less_park = score_route_candidate(
            "r2", actual_distance_meters=5000, actual_duration_seconds=1800, park_coverage_ratio=0.1
        )
        assert more_park.total_score > less_park.total_score

    def test_lower_road_exposure_scores_higher(self):
        lower_exposure = score_route_candidate(
            "r1", actual_distance_meters=5000, actual_duration_seconds=1800, road_exposure_ratio=0.1
        )
        higher_exposure = score_route_candidate(
            "r2", actual_distance_meters=5000, actual_duration_seconds=1800, road_exposure_ratio=0.9
        )
        assert lower_exposure.total_score > higher_exposure.total_score

    def test_road_exposure_detail_never_claims_safety(self):
        result = score_route_candidate(
            "r1", actual_distance_meters=5000, actual_duration_seconds=1800, road_exposure_ratio=0.1
        )
        detail = next(c.detail for c in result.components if c.factor == "road_exposure")
        assert "safe" not in detail.lower()

    def test_missing_park_and_road_marked_unavailable(self):
        result = score_route_candidate("r1", actual_distance_meters=5000, actual_duration_seconds=1800)
        assert "park_coverage" in result.unavailable_factors
        assert "road_exposure" in result.unavailable_factors


class TestWeatherScoring:
    def test_lower_precipitation_scores_higher(self):
        dry = score_weather_hour("h1", precipitation_probability_percent=5, temperature_celsius=18)
        wet = score_weather_hour("h2", precipitation_probability_percent=90, temperature_celsius=18)
        assert dry.total_score > wet.total_score

    def test_temperature_in_comfort_band_scores_full(self):
        result = score_weather_hour("h1", temperature_celsius=18, temperature_preference="balanced")
        temp_component = next(c for c in result.components if c.factor == "temperature")
        assert temp_component.score == 1.0

    def test_temperature_preference_changes_comfort_band(self):
        hot_pref = score_weather_hour("h1", temperature_celsius=30, temperature_preference="hot")
        balanced_pref = score_weather_hour("h2", temperature_celsius=30, temperature_preference="balanced")
        assert hot_pref.total_score > balanced_pref.total_score

    def test_night_scores_lower_than_day_but_not_zero(self):
        day = score_weather_hour("h1", is_daytime=True)
        night = score_weather_hour("h2", is_daytime=False)
        night_component = next(c for c in night.components if c.factor == "daylight")
        assert day.total_score > night.total_score
        assert night_component.score == 0.5

    def test_missing_data_marked_unavailable(self):
        result = score_weather_hour("h1")
        assert "precipitation" in result.unavailable_factors
        assert "temperature" in result.unavailable_factors