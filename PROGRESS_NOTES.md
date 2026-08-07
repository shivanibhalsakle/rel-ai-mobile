# Rel-AI — Progress Notes (interview-ready)

Last synced against actual repo state: commit `a382244`. Covers everything built so far —
Milestone 0 is in progress (Android skeleton + auth wiring done, backend skeleton + auth
verification done; Cloud Run deploy + CI still pending).

---

## 1. One-line pitch

A native Android app that helps people who've just relocated rebuild routines — fitness,
focused-work, outdoor activity — using place, route, and weather data, with deterministic
(non-LLM) ranking and explicit "verified vs. estimated vs. unavailable" data-confidence labels.
Same product idea as an earlier web project (`relocation-copilot`), rebuilt from scratch as a
separate, hand-coded full-stack project: native Android (Kotlin/Compose) + a fresh FastAPI/
LangGraph backend.

## 2. Why these tech choices (talking points)

- **Native Kotlin over React Native/Flutter/KMP:** already knew React, wanted a genuinely new
  skill rather than a lateral move. Chose plain native Kotlin + Jetpack Compose over Flutter or
  Kotlin Multiplatform because the app is Android-only for now (Play Store only); KMP's extra
  cost (two UI frameworks eventually, Mac-dependent CI for iOS) isn't worth paying until an iOS
  phase is actually real. Business logic written in clean Kotlin now migrates into a KMP module
  later with modest rework if iOS happens — decision kept reversible, not locked in.
- **Fresh backend, not reusing relocation-copilot's:** deliberate — the whole project is a
  hands-on learning exercise, so even the backend is hand-typed, using the old project's design
  doc as a spec to reimplement, not code to copy.
- **uv over pip+venv / Poetry:** faster, single tool replaces pip+venv+pyenv, and is the more
  current default for new Python projects going into 2026.
- **Docker + Cloud Run for backend hosting:** Cloud Run only runs containers, so Docker is
  required, not optional, once deploying past localhost. Also gives byte-for-byte reproducible
  environments (same idea as a lock file, one level up).

## 3. What's actually built right now

**Android app** (`android/`):
- Kotlin + Jetpack Compose project, package/applicationId `com.shivanibhalsakle.relai`.
- `MainActivity.kt` — single entry point Activity, hosts the Compose UI tree, currently shows
  `SignInScreen`.
- `AuthViewModel.kt` — a `ViewModel` holding sign-in state as a sealed interface (`Idle`,
  `Loading`, `Success(uid)`, `Error(message)`) exposed via `StateFlow`. Talks to Firebase Auth
  (`FirebaseAuth.getInstance().signInWithCredential(...)`) to exchange a Google ID token for a
  Firebase session.
- `SignInScreen.kt` — Compose UI that collects `AuthViewModel`'s state and renders the right view
  (button / spinner / success / error). Uses the newer **Credential Manager API**
  (`androidx.credentials`) + Google Identity Services (`googleid`) to get a Google ID token,
  rather than the older deprecated Google Sign-In SDK.
- Firebase wired in via `google-services.json` + Firebase BOM (`firebase-bom:34.17.0`) +
  `firebase-auth` dependency.
- `WEB_CLIENT_ID` (needed for Google Sign-In) is injected via `local.properties` →
  `buildConfigField` → `BuildConfig.WEB_CLIENT_ID`, so the secret isn't hardcoded into source or
  committed to git.
- Version catalog (`libs.versions.toml`) centralizes dependency versions; Compose BOM pins
  compatible Compose library versions together.
- Test scaffolding present (`ExampleUnitTest.kt`, `ExampleInstrumentedTest.kt`) — default
  templates, not real tests yet.

**Backend** (`backend/`):
- FastAPI app, managed with `uv` (`pyproject.toml` + `uv.lock`), Python 3.14.
- `app/main.py` — creates the `FastAPI()` app, includes two routers under an `/v1` prefix.
- `app/api/health.py` — `GET /v1/health`, unauthenticated liveness check, returns
  `{"status": "ok"}`. Used by Cloud Run / uptime checks to confirm the service is alive.
- `app/api/me.py` — `GET /v1/me`, **protected** route. Uses `Depends(get_current_user)` so it
  only runs if the caller presents a valid Firebase ID token; returns `{"uid": ...}`.
- `app/core/auth.py` — the reusable auth dependency. Reads the `Authorization: Bearer <token>`
  header, verifies it against Firebase (`firebase_auth.verify_id_token`), raises `401` on
  missing/malformed header or invalid/expired token, otherwise returns the decoded token. This
  is the one piece every future protected endpoint will reuse via `Depends(...)`.
- `Dockerfile` — multi-stage-ish build: starts from `python:3.14-slim`, copies the `uv` binary in
  from its official image, runs `uv sync --frozen` (installs exact locked dependency versions),
  copies app code, runs Uvicorn on `$PORT` (Cloud Run injects this env var at runtime).
- Local dev: `firebase_admin` picks up Application Default Credentials (ADC) via
  `gcloud auth application-default login` — no service-account key file committed to the repo.

## 4. End-to-end auth flow (the core mechanism built so far)

1. User taps "Sign in with Google" in `SignInScreen`.
2. Credential Manager + Google Identity Services prompts the system Google account picker,
   returns a Google ID token.
3. `AuthViewModel.signInWithGoogle(idToken)` wraps that token in a `GoogleAuthProvider` credential
   and calls `FirebaseAuth.signInWithCredential(...)` — this is what actually creates/logs into a
   Firebase user and gives the app a **Firebase ID token** (different from the Google ID token —
   Firebase re-issues its own signed token after accepting the Google one).
4. (Next piece, not yet wired) the Android app would attach that Firebase ID token as
   `Authorization: Bearer <token>` on requests to the backend.
5. Backend's `get_current_user` dependency verifies that token against Firebase's servers via
   `firebase_admin`, extracting a trustworthy `uid` — this `uid`, not anything the client claims
   in a request body, is what any future endpoint uses to scope data access per user.
6. `/v1/me` is the first (and so far only) endpoint proving this whole chain works — hitting it
   with a valid token returns that verified `uid`.

Why it matters: without step 5's server-side verification, a client could claim to be any user
by just editing a request payload — the signed token is what makes identity trustworthy end to
end, and it's also the mechanism Firestore security rules will lean on later
(`request.auth.uid == resource.data.user_id`).

## 5. Known issue to fix (caught while reviewing)

`backend/app/core/auth.py` line 6: `firebase_admin.initialize_app` is missing its call
parentheses — `firebase_admin.initialize_app` (a reference to the function) does nothing;
it needs to be `firebase_admin.initialize_app()` to actually run. As written, the SDK's default
app never gets initialized, which would make `verify_id_token` fail with a
"default Firebase app does not exist" error the first time it's actually exercised against a
real token. Worth fixing before relying on `/v1/me` working end to end.

## 6. Repo mechanics/conventions established

- Two-repo split: `android/` (Gradle project) and `backend/` (uv-managed Python project) live
  in one monorepo (`rel-ai`), each with its own dependency/build tooling.
- Git commit history is milestone-tagged in spirit (`bbd8452` Android skeleton →
  `85e13b3` FastAPI skeleton → `a382244` `/v1/me` + token verification) — matches the
  `relocation-copilot` convention documented in `CLAUDE.md`.
- `CLAUDE.md` + `ROADMAP.md` at repo root are the persistent shared-context files across Claude
  Code and Cowork sessions (decisions, stack choices, milestone status) so nothing lives only in
  chat history.
- Naming: Play Store listing/launcher label = `relai` (lowercase); in-app stylized wordmark =
  `rel-ai`. `applicationId` (`com.shivanibhalsakle.relai`) is separate from both and permanent.

## 7. What's next (per ROADMAP.md, Milestone 0 remainder)

- Fix the `initialize_app()` bug above.
- Wire the Android app to actually call the backend's `/v1/me` with the Firebase ID token
  attached, closing the loop end to end (currently the two sides work independently but aren't
  yet calling each other).
- Cloud Run deploy of the backend container.
- GitHub Actions CI for both Android and backend (lint + trivial test on push).
- Once that's done: Milestone 0 completion criterion is an authenticated request from the
  *running app on a real device/emulator* reaching the *deployed* backend and getting a 200 —
  not just localhost-to-localhost.
