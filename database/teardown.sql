-- TempoCode Database Teardown
-- Drops all TempoCode tables and types so schema.sql can be re-run cleanly.
-- Use only on dev databases — this destroys data.

DROP TABLE IF EXISTS feedback     CASCADE;
DROP TABLE IF EXISTS progress     CASCADE;
DROP TABLE IF EXISTS submissions  CASCADE;
DROP TABLE IF EXISTS test_cases   CASCADE;
DROP TABLE IF EXISTS flow_steps   CASCADE;
DROP TABLE IF EXISTS problems     CASCADE;
DROP TABLE IF EXISTS users        CASCADE;

DROP TYPE  IF EXISTS problem_type CASCADE;
DROP TYPE  IF EXISTS step_type    CASCADE;
DROP TYPE  IF EXISTS phase        CASCADE;
DROP TYPE  IF EXISTS difficulty   CASCADE;
