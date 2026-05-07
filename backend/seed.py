r"""
TempoCode Seed Script
─────────────────────
Idempotent — wipes fixture rows and reinserts a known set:

  • Demo user (UUID matches ANONYMOUS_USER_ID in routes/submissions.py;
    anonymous submissions attach here)
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


DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


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


# ── Sprint 4 / Phase 13 — Library expansion ────────────────────────────────────
# Flow+Impl labels follow the deferred Phase 8 convention: concrete and
# code-descriptive (real variable names, named iteration, named conditionals)
# so the Llama 3.3 70B step grader can reliably classify partial code.

# ── Valid Anagram (FLOW_IMPL) ──
ANAGRAM_FLOW = [
    "Initialize `char_count = {}` hash map",
    "Loop through each char in `s` and increment `char_count[char]`",
    "Loop through each char in `t` and decrement `char_count[char]`",
    "If any value in `char_count` is non-zero, return `False`",
    "Return `True`",
]

ANAGRAM_FLOW_STEPS = [
    (StepType.START,     "Initialize `char_count = {}` hash map"),
    (StepType.LOOP,      "Loop through each char in `s` and increment `char_count[char]`"),
    (StepType.LOOP,      "Loop through each char in `t` and decrement `char_count[char]`"),
    (StepType.CONDITION, "If any value in `char_count` is non-zero, return `False`"),
    (StepType.RETURN,    "Return `True`"),
]

ANAGRAM_SOLUTION = """\
def solve(s, t):
    char_count = {}
    for char in s:
        char_count[char] = char_count.get(char, 0) + 1
    for char in t:
        char_count[char] = char_count.get(char, 0) - 1
    for value in char_count.values():
        if value != 0:
            return False
    return True
"""

ANAGRAM_TESTS = [
    (["anagram", "nagaram"], True),
    (["rat", "car"],         False),
    (["", ""],               True),
    (["a", "ab"],            False),
]


# ── Reverse a String (FLOW_IMPL — LeetCode 344) ──
REVERSE_FLOW = [
    "Initialize `left = 0` and `right = len(s) - 1`",
    "While `left < right`, swap `s[left]` and `s[right]`",
    "Increment `left` and decrement `right`",
    "Return `s` (modified in place)",
]

REVERSE_FLOW_STEPS = [
    (StepType.START,  "Initialize `left = 0` and `right = len(s) - 1`"),
    (StepType.LOOP,   "While `left < right`, swap `s[left]` and `s[right]`"),
    (StepType.LOOP,   "Increment `left` and decrement `right`"),
    (StepType.RETURN, "Return `s` (modified in place)"),
]

REVERSE_SOLUTION = """\
def solve(s):
    left = 0
    right = len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
    return s
"""

REVERSE_TESTS = [
    ([["h", "e", "l", "l", "o"]], ["o", "l", "l", "e", "h"]),
    ([["a"]],                     ["a"]),
    ([[]],                        []),
]


# ── Sum List Elements (DEBUGGING — IndexError) ──
SUM_LIST_BROKEN = """\
def solve(nums):
    total = 0
    for i in range(len(nums) + 1):
        total += nums[i]
    return total
"""

SUM_LIST_FIXED = """\
def solve(nums):
    total = 0
    for i in range(len(nums)):
        total += nums[i]
    return total
"""

# range(len(nums) + 1) walks one past the last index → IndexError on every
# non-empty input AND on [] (range(1) → nums[0] crashes too).
SUM_LIST_TESTS = [
    ([[1, 2, 3]],         6),
    ([[10, 20, 30, 40]],  100),
    ([[5]],               5),
    ([[]],                0),
]


# ── Get User Email (DEBUGGING — KeyError) ──
GET_EMAIL_BROKEN = """\
def solve(user):
    return user["email"]
"""

GET_EMAIL_FIXED = """\
def solve(user):
    return user.get("email")
"""

# Inputs include both shapes: dict with "email" (works either way) and dict
# without (starter raises KeyError, fix returns None).
GET_EMAIL_TESTS = [
    ([{"email": "a@b.com"}],            "a@b.com"),
    ([{"name": "X"}],                   None),
    ([{"name": "Y", "age": 10}],        None),
    ([{"email": "ok@example.com",
       "name": "Z"}],                   "ok@example.com"),
]


# ── Calculate Average (DEBUGGING — ZeroDivisionError) ──
AVERAGE_BROKEN = """\
def solve(nums):
    return sum(nums) / len(nums)
"""

AVERAGE_FIXED = """\
def solve(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)
"""

# Empty list trips ZeroDivisionError on starter; fix short-circuits to 0.
AVERAGE_TESTS = [
    ([[1, 2, 3]],   2.0),
    ([[10]],        10.0),
    ([[]],          0),
    ([[2, 4, 6, 8]], 5.0),
]


# ── Mock Interview: late-binding closure gotcha ────────────────────────────────
# Classic Python interview question. Per-test subprocess isolation in the rule
# grader hides this bug, so it lives here as an explanation-style prompt the AI
# can grade on understanding rather than execution.
MOCK_CODE = """\
def make_multipliers():
    funcs = []
    for i in range(3):
        funcs.append(lambda x: x * i)
    return funcs

multipliers = make_multipliers()
print(multipliers[0](5))
print(multipliers[1](5))
print(multipliers[2](5))
"""

MOCK_PROMPT = (
    "Read the code carefully. What does this script print when you run it, "
    "and why does each lambda behave that way? Walk through what `i` "
    "actually refers to inside the lambda when each function is called."
)


# ── Seed routine ──────────────────────────────────────────────────────────────

def seed():
    db = SessionLocal()
    try:
        # Wipe fixture rows. CASCADE handles flow_steps / test_cases / submissions.
        db.query(Problem).delete()
        db.query(User).filter(User.id == DEMO_USER_ID).delete()
        db.commit()

        # Demo user — submissions.py FK depends on this row existing for
        # anonymous (logged-out) submissions.
        user = User(
            id            = DEMO_USER_ID,
            username      = "demo",
            email         = "demo@tempocode.local",
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

        # ── Valid Anagram (FLOW_IMPL) ──
        anagram = Problem(
            title         = "Valid Anagram",
            prompt        = (
                "Given two strings `s` and `t`, return `True` if `t` is an "
                "anagram of `s`, otherwise `False`. An anagram uses exactly "
                "the same characters in any order. Implement `solve(s, t)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "strings-hashmap",
            type          = ProblemType.FLOW_IMPL,
            expected_flow = ANAGRAM_FLOW,
            solution_code = ANAGRAM_SOLUTION,
            tags          = ["strings", "hashmap", "interview-classic"],
        )
        db.add(anagram)
        db.flush()
        for order, (step_type, label) in enumerate(ANAGRAM_FLOW_STEPS):
            db.add(FlowStep(problem_id=anagram.id, step_type=step_type,
                            step_order=order, label=label))
        for inp, expected in ANAGRAM_TESTS:
            db.add(TestCase(problem_id=anagram.id, input=inp,
                            expected_output=expected, is_semantic=False))

        # ── Reverse a String (FLOW_IMPL) ──
        reverse = Problem(
            title         = "Reverse a String",
            prompt        = (
                "Reverse the list of characters `s` in place. "
                "Return the same list after reversing. "
                "Implement `solve(s)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "two-pointers",
            type          = ProblemType.FLOW_IMPL,
            expected_flow = REVERSE_FLOW,
            solution_code = REVERSE_SOLUTION,
            tags          = ["strings", "two-pointers", "in-place"],
        )
        db.add(reverse)
        db.flush()
        for order, (step_type, label) in enumerate(REVERSE_FLOW_STEPS):
            db.add(FlowStep(problem_id=reverse.id, step_type=step_type,
                            step_order=order, label=label))
        for inp, expected in REVERSE_TESTS:
            db.add(TestCase(problem_id=reverse.id, input=inp,
                            expected_output=expected, is_semantic=False))

        # ── Sum List Elements (DEBUGGING — IndexError) ──
        sum_list = Problem(
            title         = "Sum List Elements",
            prompt        = (
                "The function below should return the sum of all numbers in "
                "`nums`. It crashes on every input. Find and fix the bug. "
                "Implement `solve(nums)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "loops-indexing",
            type          = ProblemType.DEBUGGING,
            starter_code  = SUM_LIST_BROKEN,
            solution_code = SUM_LIST_FIXED,
            tags          = ["python", "off-by-one", "debugging", "IndexError"],
        )
        db.add(sum_list)
        db.flush()
        for inp, expected in SUM_LIST_TESTS:
            db.add(TestCase(problem_id=sum_list.id, input=inp,
                            expected_output=expected, is_semantic=False))

        # ── Get User Email (DEBUGGING — KeyError) ──
        get_email = Problem(
            title         = "Get User Email",
            prompt        = (
                "The function should return the user's email if it exists, "
                "and `None` otherwise. Right now it crashes when the key is "
                "missing. Fix the bug. Implement `solve(user)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "dicts-defensive-access",
            type          = ProblemType.DEBUGGING,
            starter_code  = GET_EMAIL_BROKEN,
            solution_code = GET_EMAIL_FIXED,
            tags          = ["python", "dicts", "debugging", "KeyError"],
        )
        db.add(get_email)
        db.flush()
        for inp, expected in GET_EMAIL_TESTS:
            db.add(TestCase(problem_id=get_email.id, input=inp,
                            expected_output=expected, is_semantic=False))

        # ── Calculate Average (DEBUGGING — ZeroDivisionError) ──
        average = Problem(
            title         = "Calculate Average",
            prompt        = (
                "Return the arithmetic mean of `nums`. Empty input should "
                "return `0`. Right now it crashes on the empty case. Fix it. "
                "Implement `solve(nums)`."
            ),
            difficulty    = Difficulty.BEGINNER,
            topic         = "edge-cases-empty",
            type          = ProblemType.DEBUGGING,
            starter_code  = AVERAGE_BROKEN,
            solution_code = AVERAGE_FIXED,
            tags          = ["python", "edge-cases", "debugging", "ZeroDivisionError"],
        )
        db.add(average)
        db.flush()
        for inp, expected in AVERAGE_TESTS:
            db.add(TestCase(problem_id=average.id, input=inp,
                            expected_output=expected, is_semantic=False))

        # ── Mock Interview ──
        mock = Problem(
            title         = "Lambdas in a Loop",
            prompt        = MOCK_PROMPT,
            difficulty    = Difficulty.INTERMEDIATE,
            topic         = "closures-scoping",
            type          = ProblemType.MOCK_INTERVIEW,
            starter_code  = MOCK_CODE,
            tags          = ["python", "closures", "late-binding", "gotcha"],
        )
        db.add(mock)
        db.flush()

        db.commit()

        print("Seed complete.")
        print(f"  user.id      = {user.id}")
        print(f"  two_sum.id   = {two_sum.id}")
        print(f"  anagram.id   = {anagram.id}")
        print(f"  reverse.id   = {reverse.id}")
        print(f"  debug.id     = {debug.id}")
        print(f"  sum_list.id  = {sum_list.id}")
        print(f"  get_email.id = {get_email.id}")
        print(f"  average.id   = {average.id}")
        print(f"  mock.id      = {mock.id}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
