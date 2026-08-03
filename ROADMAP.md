# Rel-AI — MVP Roadmap

Status: planning. No code written yet. Companion to `CLAUDE.md` (project context/conventions) and
`relocation-copilot/docs/relocation-copilot-design.md` (product spec being reimplemented, not
copied).

**Scope:** native Android (Kotlin + Jetpack Compose) + hand-built FastAPI/LangGraph backend,
fully hand-coded. MVP feature set matches the relocation-copilot web MVP (see that repo's design
doc, Step 2): fitness discovery, workspace discovery, weather-aware timing, basic route
generation, onboarding, chat + recommendation cards + map, accept/reject feedback. Calendar
integration and beyond are explicitly post-MVP.

Each milestone below lists the in-demand skills it exercises, tying back to the job-market
research that informed the tech choices (mobile platform-engineering ownership of CI/CD, secure
storage/OWASP practices, and shipped-to-store experience are what recruiters actually screen for
beyond the framework name).

---

## Milestone 0 — Foundations

**Status: in progress (started 2026-08-02)**

**Goal:** Empty-but-running Android app talking to an empty-but-deployed backend, over real auth.

**Features:** Android project skeleton (Kotlin, Jetpack Compose, single-activity/Compose
Navigation), Firebase Auth (Google sign-in) wired into the app, FastAPI skeleton with a
`/v1/health` endpoint, Cloud Run deploy, GitHub Actions CI for both.

**Tech/skills exercised:** Gradle/Kotlin project structure, Jetpack Compose basics, Firebase Auth
SDK (Android), FastAPI basics, Firebase Admin SDK token verification, CI pipelines (GitHub
Actions) — the CI habit from day one is the "platform engineering" signal recruiters look for.

**Dependencies:** none.

**Testing:** CI runs lint on both sides; manual check that sign-in on-device produces a token the
backend accepts.

**Completion criteria:** an authenticated request from the running Android app to the deployed
backend returns 200, verified on a real device/emulator — not just a curl request.

---

## Milestone 1 — Onboarding & preferences

**Goal:** A signed-in user can complete onboarding and see it persist.

**Features:** onboarding form screens in Compose (activities, budget band, travel time/mode, min
rating, workspace needs, free-time windows — same fields as the web design doc's Step 3.1),
`/v1/onboarding` endpoint, Firestore preferences document, settings screen to edit.

**Tech/skills exercised:** Compose form state handling, navigation between screens, Firestore
repository pattern on the backend, Firestore security rules (scoped to `request.auth.uid`).

**Dependencies:** Milestone 0.

**Testing:** unit tests on preference validation (backend); manual test that a cross-user read is
actually blocked by security rules, not just assumed.

**Completion criteria:** preferences persist across app restarts; security rule cross-user block
verified, not assumed.

---

## Milestone 2 — Provider abstractions & caching

**Goal:** Backend can return real place/weather data, cost-controlled, before any agent exists.

**Features:** `PlacesProvider`, `WeatherProvider`, `RouteProvider`, `GeocodingProvider` classes
with field masks; shared Firestore `apiCache` collection; basic rate limiting.

**Tech/skills exercised:** external API integration discipline (field masking, caching,
retry/backoff), cost-awareness as an engineering practice — this is the part of the original web
project that most directly maps to "production mobile backend" hiring signal, since API cost
control is a recurring theme in real job specs.

**Dependencies:** Milestone 0.

**Testing:** unit tests with mocked HTTP responses; cache hit/miss test (second identical call
doesn't re-hit the external API).

**Completion criteria:** a manual script fetches places + weather for a test location with
visible cache reuse and no unmasked Places requests.

---

## Milestone 3 — Deterministic scoring

**Goal:** Ranking logic exists and is testable independent of any LLM.

**Features:** `fitness_scoring`, `workspace_scoring`, `route_scoring`, `weather_scoring` modules
with explicit, documented weights (same principle as the web project: ranking is math, not an
LLM guess).

**Tech/skills exercised:** pure Python, pydantic models, test-driven development on the most
testable part of the system.

**Dependencies:** Milestone 2.

**Testing:** unit tests with fixed inputs and expected score ordering.

**Completion criteria:** scoring functions have test coverage and documented weight rationale
(mirror the `docs/decisions/0001-scoring-weights.md` pattern from relocation-copilot, written
fresh for this repo's own weights).

---

## Milestone 4 — LangGraph agent (fitness + workspace flows)

**Goal:** End-to-end chat-driven agent flow for the first two domains.

**Features:** `understand_request`, `check_missing_info`, `ask_user` (interrupt), search/score/
explain nodes, tool-call budget enforcement, `/v1/chat` and `/v1/chat/{sessionId}/resume`
endpoints.

**Tech/skills exercised:** LangGraph `StateGraph` design, Claude structured outputs, interrupt/
resume (human-in-the-loop) patterns, checkpointing.

**Dependencies:** Milestones 1–3.

**Testing:** integration tests simulating multi-turn conversations (missing info → clarification
→ completion).

**Completion criteria:** a scripted set of representative conversations (10–15) completes
correctly end to end.

---

## Milestone 5 — Android chat UI + recommendation cards + map

**Goal:** Usable UI for the agent flow built in Milestone 4.

**Features:** chat screen, recommendation cards (with confidence badges), Google Maps SDK for
Android map view of results, accept/reject actions.

**Tech/skills exercised:** Compose UI composition at scale, state management (ViewModel +
StateFlow or similar), Google Maps SDK for Android, networking layer (Retrofit/Ktor client) with
the Firebase ID token attached per request.

**Dependencies:** Milestone 4.

**Testing:** Compose UI tests for cards; manual end-to-end pass of the full flow on-device.

**Completion criteria:** a first-time user (yourself, cold) can go from sign-in to an accepted
recommendation without guidance.

---

## Milestone 6 — Route planning + weather-aware scheduling

**Goal:** Add the remaining two MVP domains to the same agent and app.

**Features:** route generation flow (with the explicit "lower-traffic, not a safety guarantee"
caveat language from the design doc), weather "best time" flow, route map overlay, weather
timeline UI component.

**Tech/skills exercised:** Routes API integration, weather-comfort scoring, map polyline
rendering on Android, careful UX copy for liability-sensitive claims.

**Dependencies:** Milestones 4–5.

**Testing:** integration tests for route/weather conversation flows; manual check of caveat
language on all route outputs.

**Completion criteria:** route and weather flows pass the same scripted-conversation bar as
Milestone 4.

---

## Milestone 7 — Feedback loop & preference learning (structured, non-ML)

**Goal:** Accept/reject history visibly influences future results.

**Features:** implicit preference weight adjustment from the feedback collection, a "why we
think this" screen showing inferred vs. explicit preferences.

**Tech/skills exercised:** deterministic rule-based adjustment logic, before/after testing on
recommendation sets.

**Dependencies:** Milestones 3–5 in real use for feedback data to exist.

**Testing:** unit tests on adjustment rules; before/after comparison on a test account.

**Completion criteria:** a test account that repeatedly rejects expensive options sees
budget-sensitive ranking shift measurably, and this is visible in the UI, not just internal state.

---

## Milestone 8 — Hardening, cost controls, and Play Store launch readiness

**Goal:** Production-readiness pass before a closed pilot on Play Store.

**Features:** rate limiting per user, API budget alerts, Firestore security rule audit, analytics
event tracking (Firebase Analytics), data export/delete tooling, crash/error monitoring
(Crashlytics), release build signing, Play Console listing (privacy policy, data-safety form),
closed testing track.

**Tech/skills exercised:** this is the milestone that most directly maps to what job specs call
"platform engineering" — owning CI/CD, release automation (Fastlane or Gradle Play Publisher
plugin for automated Play Store uploads), crash reporting, and store compliance end to end. This
is also the block of skills that's hardest to fake in an interview, since it only comes from
having actually shipped something.

**Dependencies:** Milestones 0–7.

**Testing:** load test at expected pilot usage; security review of auth/data-access paths;
release build tested on a physical device, not just emulator.

**Completion criteria:** app is installable via a Play Store closed-testing link, cost dashboards
and data-deletion controls verified working, go/no-go checklist signed off before wider release.

---

## Post-MVP (not started, sequencing TBD)

- Google Calendar integration (mirrors relocation-copilot's Milestone 8: OAuth connect/disconnect,
  free/busy read, approval-gated event creation).
- iOS build — framework choice (Flutter rewrite vs. Kotlin Multiplatform) revisited once Android
  has real usage and a Mac is available; see `CLAUDE.md` for the reasoning already discussed.
- Push notifications, multi-city persistence, review-text NLP for ambiance attributes — same
  "not yet" list as the web MVP.

---

## Notes for future updates

- Keep this file in sync with actual progress — mark milestones with status as they land (e.g.
  a `**Status: done (2026-XX-XX)**` line under the goal), the same discipline relocation-copilot
  uses in its own doc set.
- If backend architecture or data model choices diverge from the relocation-copilot design doc
  reference, record the decision and reasoning here or in a new `docs/decisions/` ADR — don't
  leave it only in chat history.
