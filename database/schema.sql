-- TempoCode Database Schema
-- PostgreSQL
-- Run this file to initialize or reset the database schema.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────
-- ENUMS
-- ─────────────────────────────────────────────

CREATE TYPE problem_type AS ENUM ('FLOW_IMPL', 'DEBUGGING', 'MOCK_INTERVIEW');
CREATE TYPE step_type    AS ENUM ('START', 'LOOP', 'NESTED_LOOP', 'CONDITION', 'RETURN', 'END');
CREATE TYPE phase        AS ENUM ('FLOW', 'IMPLEMENTATION', 'DEBUGGING', 'MOCK_INTERVIEW');
CREATE TYPE difficulty   AS ENUM ('beginner', 'intermediate', 'advanced');

-- ─────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username       VARCHAR(50)  NOT NULL UNIQUE,
    email          VARCHAR(255) NOT NULL UNIQUE,
    password_hash  TEXT         NOT NULL,
    streak_count   INT          NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- PROBLEMS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS problems (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title          VARCHAR(255)   NOT NULL,
    prompt         TEXT           NOT NULL,
    difficulty     difficulty     NOT NULL DEFAULT 'beginner',
    topic          VARCHAR(100),
    type           problem_type   NOT NULL,
    expected_flow  JSONB,                        -- ordered array of step labels (FLOW_IMPL only)
    starter_code   TEXT,                         -- pre-broken code for DEBUGGING
    solution_code  TEXT,
    tags           TEXT[]         DEFAULT '{}',
    created_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- FLOW STEPS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS flow_steps (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id  UUID        NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    step_type   step_type   NOT NULL,
    step_order  INT         NOT NULL,
    label       TEXT        NOT NULL
);

-- ─────────────────────────────────────────────
-- TEST CASES
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS test_cases (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    problem_id       UUID    NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    input            JSONB   NOT NULL,
    expected_output  JSONB   NOT NULL,
    is_semantic      BOOLEAN NOT NULL DEFAULT FALSE   -- TRUE = semantic/gotcha test
);

-- ─────────────────────────────────────────────
-- SUBMISSIONS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS submissions (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id  UUID        NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    phase       phase       NOT NULL,
    content     JSONB       NOT NULL,  -- flow array | code string | text response
    is_correct  BOOLEAN     NOT NULL DEFAULT FALSE,
    timestamp   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- FEEDBACK
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS feedback (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id  UUID        NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    verdict        VARCHAR(20) NOT NULL,           -- 'pass' | 'fail' | 'partial'
    greened_steps  JSONB,                          -- which flow steps greened
    ai_response    TEXT,                           -- mock interview verdict text
    hint           TEXT,                           -- optional AI hint
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────
-- PROGRESS
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS progress (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id      UUID    NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    flow_completed  BOOLEAN NOT NULL DEFAULT FALSE,
    impl_unlocked   BOOLEAN NOT NULL DEFAULT FALSE,  -- gates implementation phase
    attempts        INT     NOT NULL DEFAULT 0,
    completed_at    TIMESTAMPTZ,
    UNIQUE (user_id, problem_id)
);

-- ─────────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_submissions_user     ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_problem  ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_progress_user        ON progress(user_id);
CREATE INDEX IF NOT EXISTS idx_flow_steps_problem   ON flow_steps(problem_id, step_order);
CREATE INDEX IF NOT EXISTS idx_test_cases_problem   ON test_cases(problem_id);
