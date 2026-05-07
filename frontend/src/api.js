// TempoCode API client — thin wrappers over fetch().
// Backend runs on :8000, frontend on :3000. CORS is configured for both ports.
// Trailing slashes match FastAPI's APIRouter prefixes — without them, FastAPI
// 307s and the browser drops the request body on POST.

import { clearToken, getToken } from "./auth";

const API_BASE = "http://localhost:8000";

async function request(path, { method = "GET", body, auth = "auto" } = {}) {
  const headers = { "Content-Type": "application/json" };
  // auth: "auto" attaches the token if one exists; "skip" never attaches
  // (used by signup/login so we don't send a stale token to the auth endpoints).
  if (auth === "auto") {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    // Stale/expired token. Clear it so we don't keep re-sending it; let the
    // caller decide what to do (auth is opt-in — nothing forces a redirect).
    clearToken();
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    let detail = text;
    try {
      detail = JSON.parse(text).detail ?? text;
    } catch { /* not JSON, keep raw */ }
    const err = new Error(`${method} ${path} → ${res.status} ${detail}`);
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  return res.json();
}

// ── Auth ────────────────────────────────────────────────────────────────────
export function signup(username, password) {
  return request(`/auth/signup`, {
    method: "POST",
    body: { username, password },
    auth: "skip",
  });
}

export function login(username, password) {
  return request(`/auth/login`, {
    method: "POST",
    body: { username, password },
    auth: "skip",
  });
}

export function me() {
  return request(`/auth/me`);
}

// ── Profile ──────────────────────────────────────────────────────────────────
export function getProfile() {
  return request(`/profile/me`);
}

// ── Problems ─────────────────────────────────────────────────────────────────
// GET /problems/?type=FLOW_IMPL  (type optional)
export function getProblems(type) {
  const qs = type ? `?type=${encodeURIComponent(type)}` : "";
  return request(`/problems/${qs}`);
}

// GET /problems/{id}
export function getProblem(id) {
  return request(`/problems/${id}`);
}

// POST /submissions/   body: { problem_id, phase, content }
export function submitAnswer(payload) {
  return request(`/submissions/`, { method: "POST", body: payload });
}

// POST /grade/steps   body: { problem_id, code }  → { completed_steps: [labels] }
// Backend returns 503 with { detail: "ai_unavailable" } when the LLM is down;
// callers should catch and degrade silently.
export function gradeSteps(problemId, code) {
  return request(`/grade/steps`, {
    method: "POST",
    body: { problem_id: problemId, code },
  });
}
