# TempoCode

A minimalist coding practice platform focused on programming fluency, program structure, and software modeling. Inspired by Monkeytype, but for code — not typing speed.

## Stack

| Layer    | Tech                |
|----------|---------------------|
| Frontend | SolidJS + Vite      |
| Backend  | Python + FastAPI    |
| Database | PostgreSQL 18       |
| AI       | Groq (Llama 3.3 70B) for step-level greening + mock interview grading |

## Quick start (Docker — recommended)

The whole stack runs from one command. You need Docker Desktop, a free Groq API key, and a generated JWT secret — step 3 walks through both secrets.

1. **Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).** Make sure it's running.

2. **Get a free Groq API key** at [console.groq.com](https://console.groq.com). Each developer should use their own — don't share keys.

3. **Configure your `.env`:**
   ```powershell
   Copy-Item .env.example .env       # Windows PowerShell
   # cp .env.example .env            # macOS / Linux
   ```
   You need to fill in **two** values before the stack will boot:

   - **`GROQ_API_KEY`** — paste the key you got at [console.groq.com](https://console.groq.com).
   - **`JWT_SECRET`** — a random 32-byte URL-safe string used to sign auth tokens. **Compose refuses to boot without it.** Generate one:
     ```powershell
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
     Copy the output and paste it as the `JWT_SECRET=` value.

   Save the file — then verify both values actually landed (notepad in particular sometimes appears to save but doesn't):
   ```powershell
   Get-Content .env | Select-String "GROQ_API_KEY|JWT_SECRET"   # PowerShell
   # grep -E 'GROQ_API_KEY|JWT_SECRET' .env                     # macOS / Linux
   ```
   Neither value should still read `your-groq-api-key-here` or `replace-me-with-…`.

   > **Heads up:** anytime you change `.env` later, `docker compose restart` will *not* pick up the change. You have to recreate the container — see the troubleshooting section.

4. **Boot the stack:**
   ```bash
   docker compose up
   ```
   First run pulls images and builds — give it 1–3 minutes. Subsequent runs start in seconds. Leave this terminal running; it's your live log stream. You'll know it's healthy when you see all four services log success in this rough order:
   - `postgres-1` → `database system is ready to accept connections`
   - `seed-1` → `Seed complete.` then `seed-1 exited with code 0`
   - `frontend-1` → `VITE v5.x.x ready in N ms`
   - `backend-1` → `Uvicorn running on http://0.0.0.0:8000`

5. **Verify the stack is up.** From a *second* terminal:
   ```powershell
   curl.exe http://localhost:8000/health
   curl.exe "http://localhost:8000/problems/"
   ```
   The first should print `{"status":"ok","service":"tempocode-api"}`. The second should print JSON for **eight** problems across all three modes:
   - **Flow + Impl:** Two Sum, Valid Anagram, Reverse a String
   - **Debugging:** Find Max — Off By One, Sum List Elements, Get User Email, Calculate Average
   - **Mock Interview:** Lambdas in a Loop

6. **Open the app:** [http://localhost:3000](http://localhost:3000). Try Two Sum end-to-end — arrange the flow cards, write the solution. As you type a real implementation, the flow steps in the sidebar should green progressively. *That's* the proof your Groq key reached the container.

API docs are at [http://localhost:8000/docs](http://localhost:8000/docs).

### Useful commands

| Action | Command |
|---|---|
| Stop the stack | `docker compose down` |
| Stop AND wipe the database | `docker compose down -v` |
| Re-seed problems (without wiping) | `docker compose run --rm seed` |
| Tail logs from one service | `docker compose logs -f backend` |
| Rebuild after a Dockerfile change | `docker compose up --build` |

The frontend is in dev mode with hot reload — edits to `frontend/src/` show up instantly. The backend source is baked into its image, so backend code changes need a rebuild:
```powershell
docker compose up -d --build backend
```

## Project structure

```
TempoCode/
├── frontend/             # SolidJS + Vite app (port 3000)
│   └── Dockerfile
├── backend/              # FastAPI app (port 8000)
│   ├── app/
│   │   ├── main.py
│   │   ├── security.py   # Password hashing + JWT helpers + auth deps
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── routes/       # /auth, /problems, /submissions, /grade, /profile
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Grading logic (rule-based + AI step detection)
│   │   └── db/           # DB connection + session
│   ├── seed.py           # Idempotent seed script (run automatically by compose)
│   └── Dockerfile
├── database/
│   ├── schema.sql        # Auto-applied to the postgres container on first boot
│   └── migrations/       # One-shot SQL migrations for schema deltas after deploy
├── archive/              # Historical sprint plans (sprint-4-plan.md, etc.)
├── docker-compose.yml
└── .env.example
```

## Practice modes

| Mode | Description |
|---|---|
| Flow + Implementation | Arrange flow steps in order → green → write code → green (with step-level AI greening as you type) |
| Debugging | Fix broken Python code; rule-based test runner verdict |
| Mock Interview | Read a code block, explain what it does — AI grades the explanation |

## Accounts (optional)

The platform is fully usable without an account — anonymous submissions are accepted and attached to a built-in `demo` user. **Signing up is opt-in**, not a gate. You'd want one if you care about per-user progress tracking on the profile page.

| Page | What it does |
|---|---|
| `/signup` | Create an account (username + password only — no email needed). |
| `/login` | Log in to an existing account. |
| `/profile` | Per-user stats: completed-problem counts by type and a per-problem table (attempts, accuracy, completed badge). When logged out, shows a "sign in to see your profile" stub instead of redirecting. |

Tokens are JWTs stored in `localStorage`, valid for 7 days.

## Bare-metal dev (advanced)

If you'd rather run the stack without Docker (e.g. you already have Postgres 18 locally), use `backend/.env.example` as a reference and run each service yourself:

```bash
# Database (one-time setup)
psql -U postgres -c "CREATE DATABASE tempocode;"
psql -U postgres -d tempocode -f database/schema.sql

# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate              # Windows; use source .venv/bin/activate elsewhere
pip install -r requirements.txt
cp .env.example .env                 # then fill in DB password, GROQ_API_KEY, JWT_SECRET
# Generate JWT_SECRET if you don't have one:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
python seed.py
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Frontend will run at [http://localhost:3000](http://localhost:3000).

## Troubleshooting

**`docker compose up` errors with `JWT_SECRET must be set in .env`.** The backend service requires a `JWT_SECRET` value and compose refuses to start without one. Generate one and paste it into `.env`:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Then `docker compose up` again.

**`docker compose up` says "port 5432 already in use".** You have a local Postgres running. Either stop it, or remove the `5432:5432` line under the `postgres` service in `docker-compose.yml` (the rest of the stack doesn't need port 5432 exposed to the host).

**Step-level greening doesn't trigger / Mock Interview returns 401.** Your `GROQ_API_KEY` isn't reaching the container. Check what the backend is actually seeing:
```powershell
docker compose exec backend env | findstr GROQ
```
If that prints `your-groq-api-key-here`, fix the value in your root `.env` and recreate the container (see the next entry — `restart` is not enough). The backend silently degrades when the AI is unavailable, so the test-runner verdict still works either way; only AI features go dark.

**I edited `.env` but the container still sees the old value.** `docker compose restart` does *not* re-read `.env`. It only stops and starts the same container with the env vars captured at creation time. To pick up env changes you have to recreate the container:
```powershell
docker compose up -d --force-recreate backend
```
Or `docker compose down && docker compose up` to recreate everything.

**Database changes aren't taking effect.** Postgres only runs `schema.sql` on a fresh data volume. If you've edited the schema, run `docker compose down -v` to drop the volume, then `docker compose up`.
