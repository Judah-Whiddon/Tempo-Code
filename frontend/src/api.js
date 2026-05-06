// TempoCode API client — thin wrappers over fetch().
// Backend runs on :8000, frontend on :3000. CORS is configured for both ports.
// Trailing slashes match FastAPI's APIRouter prefixes — without them, FastAPI
// 307s and the browser drops the request body on POST.

const API_BASE = "http://localhost:8000";

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${method} ${path} → ${res.status} ${text}`);
  }
  return res.json();
}

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
