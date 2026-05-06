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

The whole stack runs from one command. You only need Docker Desktop and a free Groq API key.

1. **Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).** Make sure it's running.

2. **Get a free Groq API key** at [console.groq.com](https://console.groq.com). Each developer should use their own — don't share keys.

3. **Configure your `.env`:**
   ```powershell
   Copy-Item .env.example .env       # Windows PowerShell
   # cp .env.example .env            # macOS / Linux
   ```
   Then open `.env` in your editor and paste your Groq key into the `GROQ_API_KEY=` line. Save the file — then verify the save actually landed (notepad in particular sometimes appears to save but doesn't):
   ```powershell
   Get-Content .env | Select-String "GROQ_API_KEY"   # PowerShell
   # grep GROQ_API_KEY .env                          # macOS / Linux
   ```
   You should see `GROQ_API_KEY=gsk_...` with your real key — not `your-groq-api-key-here`.

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
   The first should print `{"status":"ok","service":"tempocode-api"}`. The second should print JSON for three problems (Two Sum, Find Max, Lambdas in a Loop).

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
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── routes/       # /problems, /submissions, /grade
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Grading logic (rule-based + AI step detection)
│   │   └── db/           # DB connection + session
│   ├── seed.py           # Idempotent seed script (run automatically by compose)
│   └── Dockerfile
├── database/
│   └── schema.sql        # Auto-applied to the postgres container on first boot
├── docker-compose.yml
└── .env.example
```

## Practice modes

| Mode | Description |
|---|---|
| Flow + Implementation | Arrange flow steps in order → green → write code → green (with step-level AI greening as you type) |
| Debugging | Fix broken Python code; rule-based test runner verdict |
| Mock Interview | Read a code block, explain what it does — AI grades the explanation |

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
cp .env.example .env                 # then fill in your DB password and Groq key
python seed.py
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Frontend will run at [http://localhost:3000](http://localhost:3000).

## Troubleshooting

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
