from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import problems, submissions, grading

app = FastAPI(
    title="TempoCode API",
    description="Backend for the TempoCode coding practice platform.",
    version="0.1.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Vite dev server (configured to :3000 in vite.config.js). 5173 is kept as a
# fallback for anyone running Vite with default settings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(problems.router)
app.include_router(submissions.router)
app.include_router(grading.router)

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "tempocode-api"}
