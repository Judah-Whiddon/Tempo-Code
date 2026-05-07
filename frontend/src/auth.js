// localStorage wrappers for the JWT. Tradeoff documented in archive/sprint-4-plan.md:
// XSS-exposed, but fits the existing CORS shape with no surgery and the demo
// has no real users yet. Switch to httpOnly cookies if real users land.

const TOKEN_KEY = "tempocode_token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* private mode / quota — fail silently, the user just won't stay logged in */
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* see setToken */
  }
}
