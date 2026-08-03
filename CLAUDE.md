# Rel-AI (Mobile) — project context

Native Android build of the relocation/routine copilot concept: same product problem as
`relocation-copilot` (helping recently-relocated people rebuild fitness, focused-work, and
outdoor-activity routines via place + route + weather data, deterministic ranking, and explicit
data-confidence labeling), but a **separate, hand-built full-stack project** — not a client
bolted onto the existing web backend.

Product/UX reference only: `relocation-copilot/docs/relocation-copilot-design.md`. Treat it as a
spec to reimplement against, not code to copy — this repo's backend, data model, and API
contracts may diverge from it over time as decisions get made here.

## Why a separate project (read this before suggesting reuse)

- The author is hand-writing every line of this codebase — Android app *and* backend — as a
  deliberate learning project. Do not write implementation code for them; guide, review, explain
  tradeoffs, and point out bugs/risks, but let them type it.
- The stack is deliberately different from `relocation-copilot`'s Next.js frontend: **native
  Android (Kotlin + Jetpack Compose)**, chosen over React Native specifically to build a new
  skill set (see rationale below) and over Flutter/KMP because the near-term scope is
  Android-only, with iOS deferred to a later phase (Flutter vs. KMP decision revisited then).
- Backend is a **fresh FastAPI + LangGraph implementation**, architected the same way as
  `relocation-copilot`'s (LangGraph `StateGraph`, deterministic scoring separated from LLM
  reasoning, human-in-the-loop approval gates for side effects) but written independently.

## Stack decisions (locked)

- **Mobile:** Kotlin, Jetpack Compose, native Android only for MVP. Play Store is the only
  distribution target for now; iOS/App Store is an explicit later phase (framework choice for
  iOS — Flutter rewrite vs. Kotlin Multiplatform — deferred until Android has traction and a Mac
  is available).
  - `applicationId`: `com.shivanibhalsakle.relai` (Play Store identity, effectively permanent —
    decided M0).
  - App/brand naming (decided M0): Play Store listing title and launcher label (`android:label`)
    are **`relai`** (lowercase, no hyphen — easiest to type/search, matches applicationId). The
    in-app wordmark (splash screen, top app bar, about screen — anywhere Claude/she fully control
    the styling) displays **`rel-ai`** as a stylized brand mark. These are two different surfaces
    (store/launcher text vs. custom-rendered UI text) and are allowed to diverge; keep the
    launcher label matched to the Play Store name so installed-app recognition doesn't break.
  - compileSdk/targetSdk/minSdk: use Android Studio's New Project wizard defaults at creation
    time rather than pinning a number here that goes stale (Android ships a new major version
    yearly).
  - Module structure: single `app` module through at least M0–M3. Revisit modularization
    (`core`/`feature` split) right before M4–M5 once real feature surface (chat, recommendations,
    map) exists to draw boundaries around — splitting before then means guessing seams that
    would likely get refactored anyway.
- **Backend:** FastAPI (Python), LangGraph agent orchestration, Firestore for persistence,
  deterministic scoring (no LLM-judged ranking), Claude via Anthropic API for
  intent-classification/explanation generation only.
- **Auth:** Firebase Auth (Google sign-in), Firebase Admin SDK token verification server-side —
  same pattern as `relocation-copilot`.
- **Maps/Places/Routes/Weather:** Google Maps Platform APIs (Places, Routes, Geocoding) + Google
  Weather API, field-masked and cached from day one (this was a hard-learned cost lesson in the
  web project — carry it over, don't relearn it).

## Monorepo layout (planned)

- `android/` — Kotlin + Jetpack Compose app. Chat UI, recommendation cards, map (Google Maps SDK
  for Android), onboarding, settings.
- `backend/` — FastAPI. LangGraph agent orchestration, provider integrations, deterministic
  scoring, Firestore data access. (Mirrors `relocation-copilot/backend/app/` structure
  conceptually — see design doc Step 8 — but written from scratch here.)
- `infrastructure/` — Cloud Run service config, Firestore security rules/indexes.
- `docs/` — roadmap, ADRs, and any decisions that diverge from the relocation-copilot design doc.

See `ROADMAP.md` in this repo for the milestone breakdown and current status.

## MVP scope (finalized)

Matches the `relocation-copilot` web MVP feature-for-feature (see design doc Step 2), rebuilt
natively:

- Firebase Auth sign-in + onboarding preference form
- Fitness discovery (gyms/studios/parks) with deterministic ranking
- Workspace discovery (cafés/libraries/coworking)
- Weather-aware "best time today" recommendation
- Basic running/walking route generation (park/road-classification heuristic)
- Chat interface + recommendation cards + map
- Accept/reject feedback loop, structured preference memory (explicit + implicit)
- Confidence-labeled data (verified/estimated/unavailable) surfaced in the UI

Explicitly **out of scope for this MVP** (same exclusions as the web MVP, see design doc Step 2):
Google Calendar integration, multi-city/travel-mode persistence, review-text NLP for ambiance
attributes, push notifications, social/community features, semantic/vector memory,
booking/payment integration, multi-LLM routing.

## Conventions

- Commit messages are milestone-tagged (`M<major>.<minor>: ...` or `fix: ...`), matching the
  relocation-copilot convention.
- No speculative abstractions ahead of the milestone that needs them.
- Author writes all implementation code by hand. Claude's role in this repo is guidance, code
  review, architecture discussion, and roadmap upkeep — not authorship.

## Working across two Claude sessions

Same handoff discipline as `relocation-copilot`: this repo may be worked on from both a local
Claude Code session and the Claude.ai/Cowork app, which don't share working-tree state.

- Push before switching tools, pull before starting.
- Record any architectural decision or non-obvious constraint here or in `docs/decisions/` —
  don't leave it only in chat history the other session can't see.
- Keep this file and `ROADMAP.md` current as milestones land; don't let them drift from the code.
