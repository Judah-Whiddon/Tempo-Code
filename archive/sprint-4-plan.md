# Sprint 4 — Final Stretch (Auth + Profile + Problems)

**Goal:** Ship minimal authentication, a profile page, and a small problem-library expansion before final submission.

**Read first:** `CLAUDE.md` in the project root for project context, schema, conventions, and prior sprint history. This plan assumes that context.

**Time budget:** One evening. Phases must be done in order — Phase 11 is load-bearing for Phase 12.

---

## Architectural decisions (locked, no re-litigation)

- **Auth scope:** username + password only. No email verification, no password reset, no OAuth.
- **Password hashing:** bcrypt via `passlib[bcrypt]`.
- **Token strategy:** JWT, signed HS256, returned by `/auth/login`, stored in `localStorage` on the frontend, sent as `Authorization: Bearer <token>`. Tradeoff accepted: XSS-exposed, but fits the existing Vite-3000 ↔ FastAPI-8000 CORS setup with no surgery, and no real users exist on this demo.
- **JWT library:** `pyjwt` (lighter than python-jose).
- **JWT signing key:** `JWT_SECRET` env var. Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Add to `.env`, `.env.example`, and `docker-compose.yml` backend service.
- **Token expiry:** 7 days. Long enough demo users don't get bounced; short enough to not be careless.
- **Existing submissions:** the placeholder UUID `00000000-0000-0000-0000-000000000001` becomes user `demo`. Old submissions stay attached to it (no orphans, no real-account pollution).
- **Streak metric is deferred** from Phase 12 — it requires a daily-activity rollup that's the most likely place for time to evaporate. If Phase 11 finishes early and Phase 12 is humming, pick it up; otherwise, ship without it.

---

## Phase 11 — Minimal Auth

Order matters: backend first (so Postman/curl can prove it), then frontend, then the migration. Migration last so we don't break anything mid-flight.

### Backend

- [ ] Add deps to `backend/requirements.txt`: `passlib[bcrypt]==1.7.4`, `pyjwt==2.10.1`. Re-install in the venv and rebuild the Docker image.
- [ ] New file: `backend/app/security.py`
  - `hash_password(plain: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(user_id: UUID) -> str` — HS256, `sub` claim is the UUID stringified, `exp` = now + 7 days
  - `decode_access_token(token: str) -> UUID` — raises `HTTPException(401)` on invalid/expired/missing
  - FastAPI dependency `get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User` — strips `Bearer `, decodes, fetches the user from DB, 401 if missing
- [ ] New file: `backend/app/schemas/auth.py`
  - `SignupRequest { username: str, password: str }`
  - `LoginRequest { username: str, password: str }`
  - `UserResponse { id: UUID, username: str, streak_count: int, created_at: datetime }`
  - `AuthResponse { user: UserResponse, access_token: str }`
- [ ] New file: `backend/app/routes/auth.py`
  - `POST /auth/signup` — validates username uniqueness, hashes password, inserts `User`, returns `AuthResponse`. **409** on duplicate username, **422** on missing fields.
  - `POST /auth/login` — fetches user by username, `verify_password`, returns `AuthResponse`. **401** on bad creds (don't distinguish "wrong username" vs. "wrong password" in the error — that's a username enumeration leak).
  - `GET /auth/me` — `Depends(get_current_user)`, returns `UserResponse`.
- [ ] Register the router in `backend/app/main.py`.
- [ ] Update `backend/app/routes/submissions.py` — remove the hardcoded `PLACEHOLDER_USER_ID`. Add `current_user: User = Depends(get_current_user)` and use `current_user.id`.
- [ ] Add `JWT_SECRET` to root `.env`, `.env.example`, and `docker-compose.yml` backend env block.

### Frontend

- [ ] New file: `frontend/src/auth.js`
  - `getToken() / setToken(token) / clearToken()` — localStorage wrappers, key: `tempocode_token`
- [ ] Update `frontend/src/api.js`:
  - Helper to build headers with `Authorization: Bearer ${getToken()}` when a token exists
  - On any **401** response: `clearToken()` + redirect to `/login`
  - New methods: `signup(username, password)`, `login(username, password)`, `me()`
- [ ] New file: `frontend/src/AuthContext.jsx` — Solid context with a `currentUser` signal. On provider mount, if a token exists, call `me()` to hydrate. Exposes `login`, `signup`, `logout`.
- [ ] New page: `frontend/src/pages/Login.jsx` — username + password form, calls `login()`, stores token via context, navigates to `/`. Inline error on bad creds. Link to `/signup`.
- [ ] New page: `frontend/src/pages/Signup.jsx` — same shape, calls `signup()`. Inline error on duplicate username. Link to `/login`.
- [ ] Update `frontend/src/App.jsx`:
  - Wrap the router with `<AuthProvider>`
  - Add public routes `/login` and `/signup`
  - Guard `/problem/:id` (and the upcoming `/profile`) — if `currentUser()` is null, redirect to `/login`
- [ ] Update `frontend/src/pages/ProblemTypeSelect.jsx`:
  - When authenticated: show "Logged in as {username}" + Logout button
  - When unauthenticated: show "Log in" / "Sign up" links
  - Browsing problem types stays unauthenticated; the auth wall lives at the problem page so the landing page stays open and inviting

### Migration (run last, after backend + frontend are working against new accounts)

- [ ] Create `backend/migrations/004_demo_user.sql` (or a Python one-shot — match the existing convention; if there is none, SQL is fine):
  ```sql
  UPDATE users
     SET username = 'demo',
         email    = 'demo@tempocode.local'
   WHERE id = '00000000-0000-0000-0000-000000000001';
  ```
- [ ] Confirm `seed.py` still works — the placeholder insert there should now upsert to `username = 'demo'` to stay idempotent.

### Acceptance criteria

- [ ] Brand-new user signs up at `/signup` → lands on `/` logged in, token in localStorage
- [ ] Logout → redirects to `/`, token removed
- [ ] Login with wrong password → inline error, no navigation, no token written
- [ ] Visiting `/problem/<id>` with no token → redirect to `/login`
- [ ] After login, submitting Two Sum → DB shows `submissions.user_id = <new user's UUID>`, not the placeholder
- [ ] Old placeholder user is renamed `demo`, old submissions still attached to it
- [ ] `docker compose up` from a clean clone still works (deps installed, env vars present)

---

## Phase 12 — Profile Page (trimmed: streak deferred)

If Phase 11 runs long, this whole phase can be cut to a stub `/profile` route that just shows "Welcome, {username}." Don't ship a fake-looking profile.

### Backend

- [ ] New file: `backend/app/routes/profile.py`
- [ ] `GET /profile/me` — protected via `get_current_user`. Response shape:
  ```json
  {
    "username": "judah",
    "problems_completed_by_type": {
      "FLOW_IMPL": 2,
      "DEBUGGING": 1,
      "MOCK_INTERVIEW": 0
    },
    "per_problem_stats": [
      {
        "problem_id": "1b2134ad-...",
        "title": "Two Sum",
        "type": "FLOW_IMPL",
        "attempts": 5,
        "successes": 1,
        "accuracy": 0.20,
        "completed": true
      }
    ]
  }
  ```
- [ ] Queries:
  - **completed-by-type:** join `Progress` → `Problem`, filter `completed_at IS NOT NULL` and `user_id = current_user.id`, group by `problem.type`. Pre-fill the three enum values with 0 so the response is always shape-stable.
  - **per-problem:** join `Submission` → `Problem`, filter `user_id = current_user.id`, group by `problem_id`, `COUNT(*)` and `SUM(CAST(is_correct AS INT))`. LEFT JOIN `Progress` for the `completed` flag. Compute `accuracy` Python-side after the query (avoid SQL division-by-zero edge case).
- [ ] Register the router in `main.py`.

### Frontend

- [ ] Update `api.js` — add `getProfile()`.
- [ ] New page: `frontend/src/pages/Profile.jsx`
  - Section 1 — "Problems completed": three lines or three small cards, one per problem type, each with a count
  - Section 2 — "Per problem": table with columns Title, Type, Attempts, Accuracy %, Completed (badge)
  - Loading state, error state, empty state ("No submissions yet — try a problem")
- [ ] Add `/profile` route in `App.jsx`, guarded.
- [ ] Add a "Profile" link to `ProblemTypeSelect.jsx` when authenticated.

### Acceptance criteria

- [ ] Brand new user lands on `/profile` → all zeros + empty table + empty-state copy
- [ ] After completing Two Sum: type counter for FLOW_IMPL increments to 1, table row shows correct attempts/accuracy/completed
- [ ] Two-account isolation: signing up two accounts and submitting on each → each `/profile/me` only shows its own data

---

## Phase 13 — Problem Library Expansion

Lowest priority. Cut entirely if 11 + 12 run long. Pure data work — no schema changes, no new code outside `backend/seed.py`.

### Flow+Impl label convention (the deferred Phase 8 convention — document this in CLAUDE.md when shipping)

Each `flow_steps` label must be **concrete and code-descriptive** so the Llama 3.3 70B step grader can reliably classify partial code. Rules:

1. Use real-looking variable names: `seen = {}` not "the storage".
2. For loops: name the iteration variable AND what's being processed. "Loop through each `(i, num)` in `enumerate(nums)`" not "Loop through".
3. For conditionals/returns: name what's checked AND what's returned. "If complement is in `seen`, return `[seen[complement], i]`" not "Return the indices".
4. For initialization: name the structure. "Initialize `seen = {}` hash map" not "Set up storage".

### New problems to seed (idempotent — guard each insert with an existence check)

- [ ] **Flow+Impl: Valid Anagram**
  - Prompt: given two strings `s` and `t`, return whether `t` is an anagram of `s`
  - Flow steps (in order):
    1. "Initialize `char_count = {}` hash map"
    2. "Loop through each char in `s` and increment `char_count[char]`"
    3. "Loop through each char in `t` and decrement `char_count[char]`"
    4. "If any value in `char_count` is non-zero, return `False`"
    5. "Return `True`"
  - Test cases: `("anagram","nagaram") → True`, `("rat","car") → False`, `("","") → True`, `("a","ab") → False`
- [ ] **Flow+Impl: Reverse a String** (LeetCode 344)
  - Prompt: reverse a list of characters `s` in place
  - Flow steps:
    1. "Initialize `left = 0` and `right = len(s) - 1`"
    2. "While `left < right`, swap `s[left]` and `s[right]`"
    3. "Increment `left` and decrement `right`"
    4. "Return `s` (modified in place)"
  - Test cases: `["h","e","l","l","o"] → ["o","l","l","e","h"]`, `["a"] → ["a"]`, `[] → []`
- [ ] **Debugging: Sum List Elements (IndexError)**
  - Starter: uses `range(len(nums) + 1)` → IndexError on the last iteration
  - Solution: `range(len(nums))`
  - Test cases must include non-empty input that triggers the crash
- [ ] **Debugging: Get User Email (KeyError)**
  - Starter: accesses `user["email"]` directly; some test inputs are dicts with no `email` key
  - Solution: `user.get("email")` or guard `if "email" in user`
  - Test cases include both shapes
- [ ] **Debugging: Calculate Average (ZeroDivisionError)**
  - Starter: `return sum(nums) / len(nums)` — crashes on empty list
  - Solution: `if not nums: return 0`
  - Test cases include `[]`

### Acceptance criteria

- [ ] `python seed.py` is still idempotent (re-running doesn't double-insert)
- [ ] All five new problems load via `GET /problems/`
- [ ] Each Flow+Impl problem greens **5/5** when given the canonical solution; **0** on empty code; **partial** on partial code (manually verify on at least one)
- [ ] Each Debugging starter crashes the test runner with the expected exception class; the solution code passes all tests

---

## Things that will burn time if you're not careful

1. **CORS preflight on authed requests.** FastAPI's `CORSMiddleware` must include `Authorization` in `allow_headers` (or use `allow_headers=["*"]`). Browsers preflight any request carrying an auth header; if OPTIONS 405s, every authed call fails silently from the user's perspective.
2. **Solid is not React.** Use `createContext` + `useContext`, but the lifecycle is `createEffect` / `onMount`, not `useEffect`. Don't pattern-match from React tutorials.
3. **The frontend never trusts JWT claims.** Decoding the token client-side is fine for reading `exp` to short-circuit a logout, but the source of truth for "who is the user" is `me()` against the server.
4. **bcrypt is slow on purpose.** Signup will take ~200ms. That's correct. Don't tune the rounds.
5. **`docker compose restart` does NOT re-read `.env`.** Already in CLAUDE.md troubleshooting, repeated here because it'll bite again when adding `JWT_SECRET`. Use `docker compose up -d --force-recreate backend` after editing `.env`.
6. **Don't run the migration twice carelessly.** `004_demo_user.sql` is safe to re-run (UPDATE is idempotent), but be aware that once real users exist, you do not want a script that touches the `users` table broadly.
7. **Test order at the end.** Sign up → log out → log in → submit Two Sum → check `/profile/me`. Run that path once before declaring done.

---

## Out of scope (intentionally cut)

- Streak metric (deferred — can be picked up if Phase 12 finishes early)
- Recent activity feed
- Step-greening detail per problem on profile (would require persisting per-attempt `greened_steps` history; `feedback` only holds the latest)
- Email verification, password reset, OAuth (any flavor)
- Mock Interview problem additions (the existing demo problem covers the type)
- Admin dashboard, "remember me" longer expiry, refresh tokens
- Token rotation / revocation (no logout-everywhere)

If anything from Phase 11 or 12 is dropped under time pressure, **document the cut in CLAUDE.md** so future-you knows it was intentional, not forgotten.

---

## When the sprint is done

1. Fold the completed phases into `CLAUDE.md` under a new `## Sprint 4 — ...` section (matching the Sprint 2 / Sprint 3 style: phase list with `[x]` checkboxes, real findings inline).
2. Update the "Session Handoff Notes" `Last updated` line.
3. Commit: `git commit -m "Sprint 4: minimal auth, profile page, problem library expansion"` and push.
4. Delete this file (`sprint-4-plan.md`) — its contents now live in `CLAUDE.md`.
