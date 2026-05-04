r"""
TempoCode Seed Script
─────────────────────
Idempotent — wipes fixture rows and reinserts a known set:

  • Placeholder user (UUID matches PLACEHOLDER_USER_ID in routes/submissions.py)
  • Two Sum problem (FLOW_IMPL) with flow_steps, expected_flow, test_cases
  • Debugging problem (off-by-one IndexError) with test_cases

Run from the backend/ directory with the venv python:
    .\.venv\Scripts\python.exe seed.py
"""
import uuid

from app.db.database import SessionLocal
from app.models.models import (
    User, Problem, FlowStep, TestCase,
    ProblemType, StepType, Difficulty,
)


PLACEHOLDER_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# ── Fixture data ──────────────────────────────────────────────────────────────

TWO_SUM_FLOW = [
    "Initialize an empty hashmap to store seen numbers",
    "Loop through each number with its index",
    "Compute the complement (target - current number)",
    "If complement is in the hashmap, return both indices",
    "Otherwise, store the current number and index in the hashmap",
]

TWO_SUM_FLOW_STEPS = [
    (StepType.START,     "Initialize an empty hashmap to store seen numbers"),
    (StepType.LOOP,      "Loop through each number with its index"),
    (StepType.CONDITION, "Compute the complement (target - current number)"),
    (StepType.RETURN,    "If complement is in the hashmap, return both indices"),
    (StepType.END,       "Otherwise, store the current number and index in the hashmap"),
]

TWO_SUM_SOLUTION = """\
def solve(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
    return []
"""

TWO_SUM_TESTS = [
    ([[2, 7, 11, 15], 9], [0, 1]),
    ([[3, 2, 4],       6], [1, 2]),
    ([[3, 3],          6], [0, 1]),
]

DEBUG_BROKEN = """\
def solve(nums):
    max_val = nums[0]
    for i in range(1, len(nums) + 1):
        if nums[i] > max_val:
            max_val = nums[i]
    return max_val
"""

DEBUG_FIXED = """\
def solve(nums):
    max_val = nums[0]
    for i in range(1, len(nums)):
        if nums[i] > max_val:
            max_val = nums[i]
    return max_val
"""

# Off-by-one: range(1, len(nums) + 1) walks past the last index → IndexError on
# every call. The grader's _run_test returns a fail verdict whenever user code
# raises (returncode != 0), so each test case catches the bug deterministically.
DEBUG_TESTS = [
    ([[1, 2, 3]],     3),
    ([[5, 2, 8, 1]],  8),
    ([[42]],          42),
]


# ── Seed routine ──────────────────────────────────────────────────────────────

def seed():
    db = SessionLocal()
    try:
        # Wipe fixture rows. CASCADE handles flow_steps / test_cases / submissions.
        db.query(Problem).delete()
        db.query(User).filter(User.id == PLACEHOLDER_USER_ID).delete()
        db.commit()

        # Placeholder user — submissions.py FK depends on this row existing.
        user = User(
            id            = PLACEHOLDER_USER_ID,
            username      = "placeholder",
            email         = "placeholder@tempocode.local",
            password_hash = "not-a-real-hash",
        )
        db.add(user)

        # ── Two Sum (FLOW_IMPL) ──
        two_sum = Problem(
            title         = "Two Sum",
            prompt        = (
                "Given an array of integers `nums` and a target integer `target`, "
                "return the indices of the two numbers that add up to `target`. "
                "You may assume each input has exactly one solution. "
                "Implement `solve(nums, target)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "arrays-hashmap",
            type          = ProblemType.FLOW_IMPL,
            expected_flow = TWO_SUM_FLOW,
            solution_code = TWO_SUM_SOLUTION,
            tags          = ["arrays", "hashmap", "interview-classic"],
        )
        db.add(two_sum)
        db.flush()

        for order, (step_type, label) in enumerate(TWO_SUM_FLOW_STEPS):
            db.add(FlowStep(
                problem_id = two_sum.id,
                step_type  = step_type,
                step_order = order,
                label      = label,
            ))

        for inp, expected in TWO_SUM_TESTS:
            db.add(TestCase(
                problem_id      = two_sum.id,
                input           = inp,
                expected_output = expected,
                is_semantic     = False,
            ))

        # ── Debugging (DEBUGGING) ──
        debug = Problem(
            title         = "Find Max — Off By One",
            prompt        = (
                "The function below should return the largest number in `nums`. "
                "Right now it crashes on every input. Find and fix the bug. "
                "Implement `solve(nums)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "loops-indexing",
            type          = ProblemType.DEBUGGING,
            starter_code  = DEBUG_BROKEN,
            solution_code = DEBUG_FIXED,
            tags          = ["python", "off-by-one", "debugging"],
        )
        db.add(debug)
        db.flush()

        for inp, expected in DEBUG_TESTS:
            db.add(TestCase(
                problem_id      = debug.id,
                input           = inp,
                expected_output = expected,
                is_semantic     = False,
            ))

        db.commit()

        print("Seed complete.")
        print(f"  user.id     = {user.id}")
        print(f"  two_sum.id  = {two_sum.id}")
        print(f"  debug.id    = {debug.id}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
