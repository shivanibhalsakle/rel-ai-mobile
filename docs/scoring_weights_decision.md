# Deterministic scoring weights

## Shared mechanics (`app/scoring/base.py`)

Every module produces a `ScoredResult`: a 0–100 `total_score` plus a list of
`ScoreComponent`s (factor, 0–1 normalized score, weight, human-readable detail,
verified/estimated confidence). Components combine via a weighted average, so weights are
plain, readable numbers (not fractions that must sum to 1) — a component with weight 4
matters roughly twice as much as one with weight 2, regardless of what else is present.

A component is only added when the underlying data is actually known. Missing data means
the factor is skipped and recorded in `unavailable_factors`, not scored as neutral/0.5 and
not penalized as if-missing-means-bad — this directly implements the app's
verified/estimated/unavailable data-confidence requirement (`CLAUDE.md`'s MVP scope).

## fitness_scoring

| Factor | Weight | Source | Rationale |
|---|---|---|---|
| Rating | 3.0 | `PlaceCandidate.rating` | Highest weight — the single strongest available signal of place quality, and the only factor sourced directly from Google with no approximation involved. |
| Review count | 1.5 | `PlaceCandidate.user_rating_count` | Capped normalization at 500 reviews so one mega-gym with thousands of reviews doesn't dominate every comparison. |
| Distance | 2.0 | caller-supplied `travel_minutes` | Not computed by this module (no network calls in scoring) — the caller supplies travel time it already fetched elsewhere. Normalized against a 60-minute ceiling. |
| Affordability | 1.0 | `PlaceCandidate.price_level` | Lowest of the numeric weights — this approximates budget fit from Google's categorical price level (0–4), **not** a dollar comparison against `budgetBand`. Google doesn't return exact prices for fitness venues; documented limitation, not silently assumed precise. |
| Setting (indoor/outdoor) | 1.0 | `PlaceCandidate.types` vs. `indoorOutdoorPreference` | Small fixed bonus, only applied when the user expressed a preference *and* the candidate's `types` give a recognizable indoor/outdoor signal. Absence of signal doesn't penalize — returns `None`, not `0.0`. |

## workspace_scoring

Same rating/review-count/distance/affordability treatment and weights as fitness_scoring.
The one addition:

| Factor | Weight | Source | Rationale |
|---|---|---|---|
| Amenity match (per amenity: wifi/outlets/quiet/food) | 1.5 each | caller-supplied `amenities` dict vs. `WorkspaceNeeds` | One independent component per amenity the user explicitly wants — not one blended score — because "the place doesn't have wifi" (known, verified data) and "we don't know if it has wifi" (unavailable) are genuinely different and deserve different treatment, not an averaged number that blurs them together. **Known MVP gap:** `PlacesProvider`'s field mask doesn't request amenity data — Google only exposes it via a paid per-place Details fetch. This module is ready to score real amenity data the moment that's wired up; until then, every amenity factor is simply unavailable. |

## route_scoring

| Factor | Weight | Rationale |
|---|---|---|
| Distance-to-target | 4.0 | Usually the most literal thing a user asked for ("a 5K route") — weighted highest. Scored independently of duration; a request typically supplies one target, not both. |
| Duration-to-target | 3.0 | Same idea for "a 30 minute run." |
| Park coverage | 2.0 | Routes should be biased toward parks/green space where possible. |
| Road exposure | 3.0 | Weighted close to the target-accuracy factors deliberately — lower-traffic routing is a core differentiator, not an afterthought. **Explicitly never described as "safe"** — detail text always reads "lower-traffic based on available data ... not a safety guarantee." |
| Weather comfort | 2.0 | Optional, supplied by `weather_scoring` for the route's time window — kept as a separate module rather than duplicated logic. |

Park coverage and road exposure aren't things any current provider returns — they're
heuristic ratios Milestone 6's route-generation step will estimate once it exists. Until
then, both are simply `None` and marked unavailable, never defaulted to a value and
displayed as if real — showing "80% low-traffic" with zero actual signal behind it would be
fabricating a favorable estimate, not just omitting an unknown one.

## weather_scoring

| Factor | Weight | Rationale |
|---|---|---|
| Precipitation chance | 4.0 | Weighted highest — rain is the single biggest factor in whether an outdoor plan actually happens. |
| Temperature comfort | 3.0 | Scored against a **categorical preference** (hot/balanced/cold), each with its own comfort band and taper range — chosen over a single fixed band or a continuous numeric preference because it's simpler for both the user to express and the code to score. |
| Wind | 1.5 | Minor discomfort factor relative to rain/temperature. Not unit-converted — a documented simplification, not a precision claim. |
| Humidity | 1.0 | Minor factor. |
| UV index | 1.0 | Minor factor. |
| Daylight | 1.0 | After-dark hours score 0.5, not 0 — night activity is a legitimate preference, not automatically bad, so this is a mild nudge rather than an exclusion. |

This module doesn't import `OnboardingRequest` at all — `temperature_preference` is a plain
parameter, same decoupling pattern `fitness_scoring` uses for `indoor_outdoor_preference`.
Whoever calls this maps a real stored preference into the parameter once that's wired up in
a later milestone.

## Explicit non-goals for this pass

- No weight here has been tuned against real usage data — reasoned defaults, revisited once
  real accept/reject behavior exists (Milestone 7, if adopted here).
- Weights aren't normalized to sum to any particular total within a module —
  `weighted_average()` normalizes by whatever weights are actually present per candidate, so
  this is intentional, not an oversight.
- Fixed weights throughout, not user-tunable importance sliders — no schema support for that
  exists in `OnboardingRequest` yet; a legitimate future feature, not a gap being hidden.