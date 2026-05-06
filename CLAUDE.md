# TempoCode — Project Context for Claude

## What This Project Is

TempoCode is a minimalist coding practice platform inspired by Monkeytype, but focused on **programming fluency, program structure, and software modeling** — not typing speed. Users practice both *modeling* program logic and *implementing* it in code.

**Target audience:** CS students and beginner-to-intermediate programmers.
**Current status:** MVP complete. Sprint 2 in planning — step-level greening for Implementation Mode.

---

## Core Product Concept

The key differentiator is **multi-level abstraction practice**: users work through problems at different levels — modeling the flow of logic first, then implementing it in code. This bridges the gap between understanding a problem and writing working code.

---

## Practice Modes

| Mode | Description |
|---|---|
| **Flow Mode** | Users arrange control-flow shapes or logic steps in the correct sequence before writing code. |
| **Implementation Mode** | Users write code that matches a previously modeled flow. |
| **Structure / Modeling Mode** | Users practice designing program structure using UML-style or diagram-based tasks. |

Flow Mode and Implementation Mode are directly connected — one feeds into the other.

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Frontend | SolidJS + Vite | Minimal, fast UI for practice modes, problem pages, and feedback |
| Backend | Python + FastAPI | Serves problems, handles submissions, connects to DB and AI services |
| Database | PostgreSQL | Core relational data + potential vector extension for AI features later |
| Real-time | WebSockets | Live grading feedback, streaming AI hints, session-based practice |
| REST API | FastAPI routes | Problem loading, user progress, submission saving |

---

## Database Schema (Conceptual)

| Table | Purpose |
|---|---|
| `users` | Account and profile information |
| `problems` | Coding/modeling prompts and metadata |
| `submissions` | User answers, code, diagrams, timestamps |
| `test_cases` | Input/output expectations for code problems |
| `feedback` | Grading results, AI comments, rule-based feedback |
| `progress` | Skill growth, completed problems, streaks, mode-specific progress |

### Problem Schema Fields
`id`, `title`, `prompt`, `difficulty`, `topic`, `mode`, `expected_flow`, `starter_code`, `solution_code`, `test_cases`, `hints`, `tags`

---

## MVP Scope (Version 1)

**Goal:** A small working version before adding heavy AI features.

**Include in MVP:**
- React problem page
- PostgreSQL `problems` table
- FastAPI endpoint to fetch problems
- Basic submission endpoint
- Simple rule-based grading for a few Python problems
- Flow Mode prototype using ordered steps/cards

**Defer until later:**
- Full AI grading
- Vector embeddings / semantic search
- Advanced user analytics
- Large problem library
- Complex diagram comparison

---

## Architecture Principles

- Borrow the **clean, minimal UX feel** of Monkeytype — focused, fast, encouraging.
- Feedback should be **simple and motivating**, like a game reward loop. Correct answers "green" — inspired by NBA2K's shot feedback mechanic.
- The platform should help users move **between abstraction levels** (model → implement).
- PostgreSQL should be treated as more than a relational DB — vector extensions can support AI-adjacent features (semantic search, problem recommendations, submission similarity) when needed.
- Use **REST** for standard page data; **WebSockets** for live grading and real-time interaction.

---

## Problem Types

Three problem types accessible from a **Problem Type Selection window** before any problem loads.

### Type 1 — Flow + Implementation (Core)
- **Gated sequential flow:** Flow phase must be greened before Implementation unlocks.
- Flow phase: user arranges FlowStep cards in correct order → array comparison against `expected_flow` → greens on match → canvas minimizes to corner.
- Implementation phase: code editor appears with minimized flow in corner → user writes code → test runner executes against TestCases → greens on pass.
- Greening is the positive reinforcement signal at both phases.
- Problems: canonical interview questions (two-sum, top-k frequent, anagrams, palindromes).

### Type 2 — Debugging
- Broken code presented in editor as `starter_code`.
- **Scope:** bugs that explicitly raise an exception when executed (`IndexError`, `TypeError`, `KeyError`, `AttributeError`, `NameError`, `ZeroDivisionError`, off-by-ones that crash, etc.).
- User fixes code in editor → test runner grades → pass/fail verdict.
- **Out of scope:** semantic gotchas (mutable defaults, late-binding closures, `is` vs `==`, integer/float division surprises). The grader runs each test case in a fresh subprocess, so state-dependent bugs never manifest under it. Those problems belong in Mock Interview (Type 3, AI-graded) instead.
- Same grading pipeline as Implementation Mode. No new infrastructure.

### Type 3 — Mock Interview
- Code block presented with a "what does this do / how is it arranged" prompt.
- AI is the grader (only problem type where AI gives the verdict, not just hints).
- MVP scope: **one demo problem only.**
- Implementation: one FastAPI endpoint → sends user text response + code block to LLM API → structured prompt → returns pass/fail + brief explanation.
- Isolated module — does not touch the rule-based grading pipeline.

---

## Grading Layer

| Problem Type | Verdict | AI Role |
|---|---|---|
| Flow + Implementation | Rule-based (array compare + test runner) | Hints only |
| Debugging | Rule-based (test runner) | Hints only |
| Mock Interview | AI verdict | Grader + explanation |

Rule-based grading is the default. AI is isolated to Mock Interview verdicts and optional hints across all types.

---

## Core User Flow

1. User hits the app → **Problem Type Selection window**
2. Selects problem type → problem loads
3. **Flow + Implementation:** Flow canvas → arrange FlowSteps → green → canvas minimizes → code editor → write code → green → complete
4. **Debugging:** Broken code in editor → fix it → test runner → pass/fail
5. **Mock Interview:** Code block + question → text response → AI evaluates → feedback

---

## Key Class Structure

| Class | Key Fields |
|---|---|
| `User` | id, username, email, password_hash, streak_count, created_at |
| `Problem` | id, title, prompt, difficulty, topic, type (enum), expected_flow (JSON), starter_code, solution_code, tags |
| `FlowStep` | id, problem_id, step_type (enum), order, label |
| `Submission` | id, user_id, problem_id, phase (enum), content (JSON), is_correct, timestamp |
| `TestCase` | id, problem_id, input, expected_output, is_semantic (bool) |
| `Feedback` | id, submission_id, verdict, greened_steps (JSON), ai_response, hint, timestamp |
| `Progress` | id, user_id, problem_id, flow_completed (bool), impl_unlocked (bool), attempts, completed_at |

---

## Resolved Decisions

1. **Flow Mode interaction:** Two-phase hybrid.
   - Phase 1 — **Ordered Cards:** User arranges cards in the sequence components should be *implemented*. Tests implementation-order thinking.
   - Phase 2 — **Drag to Architecture:** Same cards are placed onto a UML-style canvas at their correct architectural positions (e.g., controller layer, DB layer). Tests structural understanding.
   - Both phases use the same problem — sequencing feeds directly into architecture.

2. **Grading approach:** Hybrid (Option C).
   - Rule-based grader handles **pass/fail verdict** — deterministic, fast, testable, no external dependencies.
   - AI activates only for **hints and explanations** — not for the verdict itself.
   - This keeps the MVP grading layer independent from the AI layer. Each can be built, tested, and upgraded separately.

---

3. **Language scope:** Python only for MVP. Each additional language requires a separate execution environment, sandbox, and test runner. Start with one clean path; add languages as a later feature.

4. **Authentication:** Required — user stories in the sprint backlog depend on identity (progress, streaks, saved submissions). Deferred from the initial build but must be designed with it in mind so the architecture doesn't need to be reworked later.

5. **WebSocket scope:** REST-first for MVP. Load problem, submit, receive result — all REST. WebSockets added only when the experience actively calls for streaming (e.g., live test case results, token-by-token AI hints).

---

## Engineering Practices

- Treat this as a **real software engineering project** — not a coding experiment.
- Use **code discovery** to study how existing apps (Monkeytype, coding challenge platforms, diagramming tools) are structured before building.
- Document **architectural decisions** early.
- Break work into **manageable tasks** (Trello board in use).
- Use **diagrams** to communicate system design.

---

## Assistant Role

Claude is acting as a **development assistant and software architecture mentor** on this project. Prefer explanations that teach reasoning, not just answers. Point out tradeoffs. Flag decisions that will be hard to undo.

---

---

## Session Handoff Notes

- All architecture decisions, problem types, grading layer, and class structure are finalized — see sections above.
- Backend is **fully scaffolded, seeded, and verified end-to-end**: FastAPI app, SQLAlchemy models, grader service (flow comparison, subprocess code runner, AI mock interview), Pydantic schemas, DB connection, routes for `/problems` and `/submissions`.
- Database schema is live on PostgreSQL 18 (localhost:5432, db `tempocode`). The integer-keyed `users` table has been dropped and re-created with UUID. `database/teardown.sql` is the canonical reset script — run it then re-apply `database/schema.sql` if you need a clean slate.
- `backend/seed.py` inserts a placeholder user + Two Sum (FLOW_IMPL) + Find Max — Off By One (DEBUGGING). Idempotent — safe to re-run.
- Backend Python venv lives at `backend/.venv` (deps installed from `requirements.txt`). Run the API via `& .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000` from `backend/`.
- Frontend is built with SolidJS + Vite. Run via `npm run dev` from `frontend/` (Vite serves on :3000; CORS is configured for that origin). Routes: `/` (problem-type select) and `/problem/:id`. API client is `frontend/src/api.js`.
- Frontend file layout: `src/pages/` (`ProblemTypeSelect.jsx`, `ProblemPage.jsx`, `FlowImplWorkspace.jsx`); `src/components/` (`FlowCanvas.jsx`, `ImplementationPanel.jsx`); empty scaffold dirs `CodeEditor/`, `Feedback/`, `FlowCanvas/`, `ProblemTypeSelector/` are leftovers — safe to delete.
- `backend/.env` carries the bare-metal `DATABASE_URL` and `GROQ_API_KEY`. The root `.env` is for `docker compose` (real `GROQ_API_KEY` lives there too). Both are gitignored. Anthropic SDK is no longer a runtime dependency — `anthropic==0.25.0` in `requirements.txt` is dead weight and can be removed.
- **Resolved:** the Windows `python3` PATH bug in `grader.py` is fixed — `[sys.executable, tmp_path]` is used for the subprocess invocation, so IMPLEMENTATION and DEBUGGING grading work on Windows.
- GitHub repo at https://github.com/Judah-Whiddon/Tempo-Code — `master` is pushed through Sprint 3 Phase 9 (Mock Interview UI + Dockerize). Local commits beyond that get pushed manually with `git push`.
- Assignment 3 PDF (`TempoCode_Project_Management.pdf`) is complete and in the project root.
- **Sprint 2 provider decision:** Step-level greening uses **Groq + Llama 3.3 70B Versatile** (`llama-3.3-70b-versatile`). Initially started on `llama-3.1-8b-instant` but the 8B model reliably missed conditional-branch return steps and ignored explicit "no empty bodies" instructions; bumped to 70B during Phase 7 testing and it greens correctly across partial / mid / full code states. Groq's API is OpenAI-compatible, free tier, and fast enough for interactive use. `GROQ_API_KEY` is live and rotated in `.env`. Env vars: `STEP_GRADER_BASE_URL=https://api.groq.com/openai/v1`, `STEP_GRADER_MODEL=llama-3.3-70b-versatile`. Provider/model are intentionally env-configurable so switching to Ollama (local) or Anthropic later is a one-line change.

*Last updated: 2026-05-05 (Mock Interview UI shipped; Sprint 3 Phase 9 — Dockerize the stack — shipped end-to-end. `docker compose up` from a clean clone produces a working app on Windows. Phase 10 — public hosted demo — is the next queued effort.)*

---

## MVP Sprint Plan

All five phases of the MVP sprint are complete. The platform supports the two core problem types (Flow+Implementation and Debugging) end-to-end against real data. Mock Interview UI remains deferred per the original scope.

### Phase 1 — Backend verification + seed data ✅ DONE (2026-05-02)
**Goal:** Confirm the backend runs end-to-end against real data before touching the frontend.

- [x] DB teardown + `schema.sql` re-applied (`database/teardown.sql` is the reset script)
- [x] `backend/seed.py` inserts placeholder user + Two Sum (FLOW_IMPL) + Find Max — Off By One (DEBUGGING)
- [x] FastAPI boots; verified `GET /health`, `GET /problems`, `POST /submissions` (correct flow → `pass`, shuffled flow → `fail` with `greened_steps` and hint)

**Source patches needed during verification (small, deliberate fixes):**
- `models.py` — added `values_callable` to `Difficulty` enum column (Postgres enum stores lowercase values; SAEnum was sending uppercase member names)
- `submissions.py` — explicit `attempts=0` (and the other booleans) in the new-`Progress` constructor (Python-side defaults don't fire before the first `+= 1`)
- `grader.py:129` — replaced `["python3", tmp_path]` with `[sys.executable, tmp_path]` so subprocess grading works on Windows where `python3` is not on PATH

### Phase 2 — Frontend skeleton + API layer ✅ DONE (2026-05-03)
**Goal:** Routing and API plumbing before any UI components.

- [x] `frontend/src/api.js` — thin wrappers: `getProblems(type?)`, `getProblem(id)`, `submitAnswer(payload)`. Trailing slashes on collection routes match FastAPI's APIRouter prefixes (without them FastAPI 307s and the browser drops POST bodies).
- [x] SolidJS routing (`@solidjs/router`) wired in `App.jsx` with `/` and `/problem/:id`.
- [x] **Problem Type Selection screen** (`pages/ProblemTypeSelect.jsx`) — three cards (Flow+Impl, Debugging, Mock Interview). Clicking fetches `getProblems(type)` and navigates to the first match.

### Phase 3 — Flow Mode UI ✅ DONE (2026-05-03)
**Goal:** Reorderable FlowStep cards, submit flow arrangement, green on pass.

- [x] Shuffled `flow_steps` rendered as cards in `components/FlowCanvas.jsx` with ↑/↓ reorder controls (MVP swap; drag-and-drop deferred).
- [x] Submit → `POST /submissions` with `{ phase: "FLOW", content: [ordered labels] }`.
- [x] On `verdict: pass`: cards green, ~900 ms celebration delay, then handoff to Implementation panel.
- [x] On `verdict: fail`: surface `greened_steps` (correctly placed cards stay green) + grader hint.

### Phase 4 — Implementation Mode UI ✅ DONE (2026-05-03)
**Goal:** Code editor, submit code, pass/fail with hint.

- [x] Plain `<textarea>` editor in `components/ImplementationPanel.jsx` (CodeMirror deferred per the "or a plain `<textarea>` for pure MVP" allowance).
- [x] Phase orchestrator `pages/FlowImplWorkspace.jsx` swaps from `FlowCanvas` to `ImplementationPanel` on flow pass. (Note: spec called for "minimize to corner" — current behavior shows the greened flow as a sidebar list inside the impl panel. Functional, not the spec'd corner-dock animation. Acceptable for MVP; revisit if polish budget allows.)
- [x] Submit → `POST /submissions` with `{ phase: "IMPLEMENTATION", content: { code } }`.
- [x] Verdict display: pass → green editor + success line; fail → hint string from grader.

### Phase 5 — Debugging Mode UI ✅ DONE (2026-05-03)
**Goal:** Reuse the Implementation editor, pre-fill broken code.

- [x] `ImplementationPanel` accepts a `phase` prop (`"IMPLEMENTATION"` | `"DEBUGGING"`) and swaps headers/copy accordingly. `props.problem.starter_code ?? DEFAULT_STARTER` preloads the broken code.
- [x] `pages/ProblemPage.jsx` renders `<ImplementationPanel problem={problem()} phase="DEBUGGING" />` for `DEBUGGING`-type problems — no new backend or component needed.
- [x] Backend already routes `Phase.DEBUGGING` through the same code grader as `IMPLEMENTATION` (`grader.py:40`, `submissions.py:79`).
- [x] Pass/fail verdict display reuses the Implementation panel's verdict UI.

### Deferred (not in MVP)
- Authentication (placeholder user `00000000-0000-0000-0000-000000000001` is hardcoded in submissions.py — fine for now)
- Mock Interview UI (backend is ready; add this last)
- WebSockets
- Styling beyond functional
- Additional problems / problem library
- "Minimize flow canvas to corner" polish on the FLOW → IMPLEMENTATION handoff
- CodeMirror in place of `<textarea>`
- Re-author the late-binding-closure / mutable-default gotcha as a Mock Interview prompt once the MI UI lands. It was removed from Debugging on 2026-05-03 because the per-test subprocess isolation hid the bug; it's a strong candidate for AI-graded explanation-style evaluation.

---

## Sprint 2 — Step-Level Greening for Implementation Mode ✅ DONE (2026-05-04)

Sprint 2 is closed as demoable. Phases 6 and 7 shipped — step-level greening is live end-to-end on Llama 3.3 70B via Groq. Phase 8 (label tuning) was scoped out as a polish pass and intentionally not done; the only known artefact is the empty-`for`-loop body being credited as "Loop through each number with its index", which is a label-sharpness issue, not a functional one.

**Goal:** Replace the current all-or-nothing Implementation verdict with incremental step-by-step greening. Each FlowStep greens as the user implements it, giving continuous positive reinforcement rather than a single pass/fail at the end.

**Design decision:** Use AI (Groq + Llama 3.1 8B) as the step detector, not the final verdict. The final correctness verdict (did all tests pass?) stays rule-based. AI's only job is to classify which FlowSteps the current code covers. This keeps the separation of concerns intact and limits AI to a role it's well-suited for — semantic classification, not execution.

**Greening rules:**
- Greening is additive and one-directional. Once a step greens, it stays green for the session.
- AI step detection runs on "Run" button press, not on every keystroke (avoid latency/cost per keystroke).
- Final pass/fail verdict is still determined by the test runner (rule-based), same as today.
- If the AI call fails (network error, rate limit), fail silently — show a neutral state and let the test runner verdict still work normally.

---

### Phase 6 — AI Step Detection Endpoint (Backend) ✅ DONE (2026-05-04)

**Goal:** Add a `/grade/steps` endpoint that accepts the user's current code + problem ID and returns which FlowSteps are complete.

- [x] `GROQ_API_KEY` live and rotated in `.env`. `STEP_GRADER_BASE_URL` and `STEP_GRADER_MODEL` added. Provider is env-configurable.
- [x] Added `grade_steps(code, flow_steps) -> list[str]` to `grader.py`. Uses `openai.OpenAI` pointed at `STEP_GRADER_BASE_URL` with `GROQ_API_KEY`, `temperature=0`, `response_format={"type": "json_object"}`. Filters returned labels against the input list (defends against hallucinated labels). New `StepGraderError` exception covers missing config, transport failure, and malformed JSON.
- [x] New `backend/app/routes/grading.py` with `POST /grade/steps`. 503 with `{detail: "ai_unavailable"}` on `StepGraderError`. Registered in `main.py`.
- [x] `openai==1.59.9` added to `requirements.txt` and installed. (Pinned to 1.59.9 specifically: 1.54.0 passes a deprecated `proxies=` kwarg to httpx 0.28, which crashes at `OpenAI()` construction. 1.55.3+ removed it. If you ever bump httpx, keep openai ≥1.55.3.)
- [x] Manual test against Two Sum (`1b2134ad-29dd-489b-ad12-fad23def9498`):
  - Empty code → 0 steps greened (correct).
  - Partial (hashmap init + empty loop body) → 1 step greened: hashmap init only. Llama 3.1 8B is correctly strict — empty loop body doesn't credit the loop step.
  - Full solution → 4/5 greened. The "If complement is in the hashmap, return both indices" label was missed despite the code containing that exact return. Symptom of label/code-language mismatch — Phase 8 territory.

---

### Phase 7 — Step Greening UI (Frontend) ✅ DONE (2026-05-04)

**Goal:** Update `ImplementationPanel` to call `/grade/steps` on Run and green completed steps in the sidebar flow list.

- [x] Added `gradeSteps(problemId, code)` to `frontend/src/api.js`.
- [x] Extended `ImplementationPanel.jsx`:
  - `greenedSteps` is a `createSignal(new Set())`. **Deviation from the original spec line "Initialized from the flow steps that were greened during Flow Mode":** since flow is all-or-nothing, pre-populating from `flowOrder` would start the impl sidebar fully green and make AI greening invisible. Initializing empty preserves the intended progressive-feedback UX. The `flowOrder` prop is still used to enumerate which labels to render in the sidebar.
  - On Submit: `gradeSteps()` and `submitAnswer()` fire via `Promise.all`. AI failures are swallowed (`.catch(() => null)`); the test runner verdict path is unaffected.
  - Newly completed steps are merged into `greenedSteps` additively (never removed).
  - Sidebar header changed from "Your greened flow" → "Flow steps". Each `<li>` gets a `.greened` class when its label is in `greenedSteps`.
- [x] Final verdict still driven by the test runner; AI is detector-only.
- [x] CSS: added `.flow-summary li` muted default + `.flow-summary li.greened` accent color (incl. `::marker`).
- [x] Browser-tested end-to-end on Two Sum.

**Two findings from real testing — addressed before sign-off:**

1. **Llama 3.1 8B was reliably missing step 4** ("If complement is in the hashmap, return both indices") even on a perfect solution. Tried softening the system prompt with an explicit example crediting conditional-branch returns; **didn't fix the miss** and made the partial case slightly worse (started crediting an empty `for` loop). Diagnosis: capability ceiling, not prompt.
2. **Swapped to `llama-3.3-70b-versatile`** (still on Groq, still free tier — one-line `.env` change). Result: full Two Sum greens **5/5**, mid-state (hashmap + loop + complement, no return) greens **3/5** — proper progressive signal. The empty-loop case still credits "Loop through each number with its index" — judgment call (the loop *is* there); fixable in Phase 8 by sharpening the label if undesired.

The softened system prompt was kept (it doesn't hurt 70B and adds an example for future tuning).

---

### Phase 8 — Seed Data: Intermediate Test Alignment ⏸ DEFERRED

**Goal:** Ensure Two Sum's `flow_steps` labels match the language the AI will naturally use when reading code. If labels are vague, the AI may misclassify.

- [ ] Review Two Sum `flow_steps` labels in `seed.py` against how Claude describes partial implementations.
- [ ] Adjust labels to be concrete and code-descriptive (e.g., "Initialize seen = {} hash map" instead of "Set up storage").
- [ ] Re-seed and re-test step detection with updated labels.
- [ ] Document the label convention in this file so future problems follow the same pattern.

**Status:** intentionally deferred. With Llama 3.3 70B the only undesirable behavior we observed is "empty `for` loop body credited as the Loop step." Tightening that label (e.g. "Loop body iterates each number and processes it") would fix it but isn't blocking demo. Pick this up if/when adding the third+ problem.

---

### Deferred from Sprint 2
- WebSocket streaming for token-by-token step greening (REST + polling is sufficient for now).
- Rate limiting on `/grade/steps` (add when multiple users are active).
- Per-step hint generation (AI currently classifies steps; generating targeted hints per incomplete step is a separate prompt and a separate feature).
- CodeMirror editor (still deferred — `<textarea>` is fine through demo).

---

## Sprint 3 — Dockerize & Distribute

**Goal:** Make TempoCode runnable by anyone with one command and pavable for a public hosted demo. Current "clone and run" requires installing Postgres 18, creating a Python venv, running two SQL scripts, npm-installing the frontend, setting env vars, running seed, and booting two servers — a non-trivial barrier for graders, classmates, or future contributors.

**Why now:** The MVP + Sprint 2 are demoable but only on the author's machine. A presentation link beats a "git clone it" instruction every time, and Docker is the foundation that unlocks both reproducible local dev and most free-tier hosting platforms (Render, Railway, Fly).

### Phase 9 — Dockerize the stack ✅ DONE (2026-05-05)

- [x] `backend/Dockerfile` — `python:3.12-slim`, installs `requirements.txt`, runs uvicorn on `:8000`. Secrets read from env at runtime, never baked into the image.
- [x] `frontend/Dockerfile` — `node:20-alpine`, `npm install`, runs `vite --host 0.0.0.0` on `:3000`. Dev mode (not multi-stage build → nginx) so source bind-mount + hot reload works in dev. Build-for-prod is a Phase 10 concern.
- [x] `docker-compose.yml` — four services: `postgres` (Postgres 18, healthchecked), `seed` (one-shot, gates `backend` via `service_completed_successfully`), `backend`, `frontend`. Env vars sourced from root `.env`; nothing hardcoded.
- [x] `database/schema.sql` mounted at `/docker-entrypoint-initdb.d/01-schema.sql:ro` for first-boot init. `seed.py` runs as the dedicated `seed` service.
- [x] `.dockerignore` for both backend and frontend (`.venv`, `node_modules`, `__pycache__`, `.git`, etc.).
- [x] Manual test: clean `docker compose up` on Windows produces a working app at `http://localhost:3000`. Verified `/health`, `/problems/`, `/grade/steps` all 200, full Two Sum flow + step greening end-to-end.
- [x] `README.md` — comprehensive Docker quickstart added (prerequisites, one command, env setup, verification, troubleshooting).

**Two gotchas hit during bring-up — both documented in the README troubleshooting section:**

1. **PG18 volume path.** The image now stores data under `/var/lib/postgresql/<version>/docker` so the container expects the volume mount at `/var/lib/postgresql` (parent dir), not `/var/lib/postgresql/data`. Mounting at the old path makes Postgres bail with a "format compatibility" error pointing at [docker-library/postgres#1259](https://github.com/docker-library/postgres/pull/1259). Compose is correct; just `docker compose down -v` if you ever migrate from a pre-PG18 volume.
2. **`docker compose restart` does NOT re-read `.env`.** It restarts the existing container with its baked-in env. To pick up a new `GROQ_API_KEY` (or any env change), use `docker compose up -d --force-recreate <service>` or `down && up`. This bit twice during bring-up — flagged prominently in README troubleshooting.

### Phase 10 — Public hosted demo (optional, blocked on Phase 9)

Pick one of:
- **Render** — Postgres + two services (backend Docker, frontend static or Docker), free tier with cold starts. Easiest if Dockerfiles work.
- **Railway** — similar to Render, slightly more generous free tier; Dockerfile-driven.
- **Fly.io + Neon** — Fly for the apps, Neon for managed Postgres free tier. More setup, more durable.
- **Vercel (frontend) + Render/Railway (backend) + Neon (DB)** — split-stack, each on the platform that does it best.

Whatever the host: secrets (`GROQ_API_KEY`) go in the platform's secret manager, never in committed config. CORS in `main.py` will need the public frontend origin added.

### Why not Codespaces / devcontainers
Considered. Tradeoff is hours-limited and configuring three services in one container is fiddlier than docker-compose. Compose buys most of the same reproducibility with broader portability and is the on-ramp to hosting. If a contributor wants Codespaces later, the existing Dockerfiles + a thin `.devcontainer/` config make it trivial.

### Out of scope for Sprint 3
- Production-grade Postgres setup (backups, connection pooling, migrations) — not needed for a demo.
- CI/CD pipeline — manual `git push` + platform auto-deploy is fine until the project has more contributors.
- Auth (still deferred from MVP). Hosting a single-user demo with the placeholder UUID is acceptable; flagging it for the user in the README is enough.
