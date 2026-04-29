# TempoCode — Project Context for Claude

## What This Project Is

TempoCode is a minimalist coding practice platform inspired by Monkeytype, but focused on **programming fluency, program structure, and software modeling** — not typing speed. Users practice both *modeling* program logic and *implementing* it in code.

**Target audience:** CS students and beginner-to-intermediate programmers.
**Current status:** Early design and planning phase.

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
| Frontend | React + Vite | Minimal, fast UI for practice modes, problem pages, and feedback |
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
- Combination of syntax errors and semantic errors (Python gotchas: mutable default arguments, `is` vs `==`, late binding closures, integer vs float division).
- User fixes code in editor → test runner grades → pass/fail verdict.
- Semantic bugs are exposed via specifically authored failing test cases — no AI needed.
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
- Backend scaffold is complete: FastAPI app, SQLAlchemy models, grader service, Pydantic schemas, DB connection.
- Database schema has been run against PostgreSQL 18 on localhost:5432. The `tempocode` database exists. The old `users` table (integer id) needs to be dropped and recreated with UUID — run the DROP commands below before re-running schema.sql:
  ```sql
  DROP TABLE IF EXISTS users CASCADE;
  DROP TYPE IF EXISTS problem_type CASCADE;
  DROP TYPE IF EXISTS step_type CASCADE;
  DROP TYPE IF EXISTS phase CASCADE;
  DROP TYPE IF EXISTS difficulty CASCADE;
  ```
- Frontend folder structure is scaffolded. React app still needs to be moved from `Desktop\my-react-app` into `frontend/`.
- `.env` file needs to be created from `.env.example` with the correct DB password.
- GitHub repo exists at https://github.com/Judah-Whiddon/Tempo-Code — nothing pushed yet.
- Assignment 3 is due tonight (April 30, 11:59pm). Diagrams are done. Project Management PDF still needs to be written.
- Switching from Cowork mode to **Claude Code** for active development. Pick up from here.

*Last updated: 2026-04-29*
