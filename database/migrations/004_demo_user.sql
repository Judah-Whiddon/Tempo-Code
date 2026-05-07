-- Sprint 4 / Phase 11.
-- Renames the original placeholder user to "demo" so the friendlier name
-- shows up in the upcoming profile UI and stays idempotent against re-seed
-- (seed.py's placeholder insert was updated to match in the same commit).
--
-- Idempotent: running it twice is a no-op since the WHERE clause targets the
-- well-known UUID and the SET values are deterministic.

UPDATE users
   SET username = 'demo',
       email    = 'demo@tempocode.local'
 WHERE id = '00000000-0000-0000-0000-000000000001';
