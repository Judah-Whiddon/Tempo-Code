"""
Grading Service — TempoCode
────────────────────────────
Rule-based grader for Flow+Implementation and Debugging problems.
AI grader for Mock Interview (single demo problem).

Grading paths:
  FLOW phase         → array comparison against problem.expected_flow
  IMPLEMENTATION     → execute code against test cases
  DEBUGGING          → execute fixed code against test cases (same pipeline)
  MOCK_INTERVIEW     → AI verdict via LLM API
"""

import subprocess
import tempfile
import os
import json
from typing import Tuple, Optional, Any
from sqlalchemy.orm import Session

from app.models.models import Problem, Submission, Phase, ProblemType


def grade_submission(
    problem: Problem,
    submission: Submission,
    db: Session,
) -> Tuple[str, Optional[Any], Optional[str], Optional[str]]:
    """
    Returns: (verdict, greened_steps, ai_response, hint)
      verdict        → 'pass' | 'fail'
      greened_steps  → list of step labels that matched (FLOW only)
      ai_response    → AI explanation text (MOCK_INTERVIEW only)
      hint           → optional hint string
    """
    if submission.phase == Phase.FLOW:
        return _grade_flow(problem, submission)

    if submission.phase in (Phase.IMPLEMENTATION, Phase.DEBUGGING):
        return _grade_code(problem, submission, db)

    if submission.phase == Phase.MOCK_INTERVIEW:
        return _grade_mock_interview(problem, submission)

    return "fail", None, None, None


# ── Flow Grader ───────────────────────────────────────────────────────────────

def _grade_flow(problem: Problem, submission: Submission):
    """
    Compare the user's submitted flow arrangement against problem.expected_flow.
    Both are ordered arrays of step labels. Exact match = green.
    """
    expected = problem.expected_flow  # e.g. ["start", "read input", "compare", "return", "end"]
    submitted = submission.content    # e.g. ["start", "compare", "read input", "return", "end"]

    if not expected or not isinstance(submitted, list):
        return "fail", [], None, "Make sure to arrange all the flow steps."

    # Find which steps are in the correct position
    greened = [
        submitted[i]
        for i in range(min(len(expected), len(submitted)))
        if submitted[i] == expected[i]
    ]

    verdict = "pass" if submitted == expected else "fail"
    hint = None if verdict == "pass" else "Some steps are out of order. Think about what needs to happen first."
    return verdict, greened, None, hint


# ── Code Grader ───────────────────────────────────────────────────────────────

def _grade_code(problem: Problem, submission: Submission, db: Session):
    """
    Execute user's Python code against all test cases.
    Uses a subprocess sandbox — no external libraries needed.
    """
    content = submission.content
    code = content.get("code", "") if isinstance(content, dict) else str(content)

    test_cases = problem.test_cases
    if not test_cases:
        return "fail", None, None, "No test cases found for this problem."

    passed = 0
    for tc in test_cases:
        result = _run_test(code, tc.input, tc.expected_output)
        if result:
            passed += 1

    verdict = "pass" if passed == len(test_cases) else "fail"
    hint = (
        None if verdict == "pass"
        else f"Passed {passed}/{len(test_cases)} test cases. Check your logic and edge cases."
    )
    return verdict, None, None, hint


def _run_test(code: str, input_data: Any, expected_output: Any) -> bool:
    """
    Run a single test case in a subprocess.
    Injects the input as a variable and checks the return value of solve().
    """
    test_script = f"""
import json, sys

{code}

try:
    input_data = json.loads('''{json.dumps(input_data)}''')
    if isinstance(input_data, list):
        result = solve(*input_data)
    else:
        result = solve(input_data)
    print(json.dumps(result))
except Exception as e:
    print("ERROR:", e, file=sys.stderr)
    sys.exit(1)
"""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            tmp_path = f.name

        proc = subprocess.run(
            ["python3", tmp_path],
            capture_output=True, text=True, timeout=5
        )
        os.unlink(tmp_path)

        if proc.returncode != 0:
            return False

        result = json.loads(proc.stdout.strip())
        return result == expected_output

    except Exception:
        return False


# ── Mock Interview Grader ─────────────────────────────────────────────────────

def _grade_mock_interview(problem: Problem, submission: Submission):
    """
    Send the user's text response + the code block to an LLM.
    Returns AI verdict and explanation.
    MVP: one demo problem only.
    """
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "fail", None, "AI grader not configured. Set ANTHROPIC_API_KEY in .env.", None

    content = submission.content
    user_response = content.get("response", "") if isinstance(content, dict) else str(content)
    code_block = problem.starter_code or ""

    try:
        verdict_text, explanation = _call_llm(
            code_block=code_block,
            user_response=user_response,
            api_key=api_key,
        )
        return verdict_text, None, explanation, None
    except Exception as e:
        return "fail", None, f"AI grader error: {str(e)}", None


def _call_llm(code_block: str, user_response: str, api_key: str):
    """Call Anthropic Claude API to evaluate a mock interview response."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""You are evaluating a mock coding interview response.

Code block shown to the candidate:
```python
{code_block}
```

Candidate's response:
{user_response}

Evaluate whether the candidate correctly identified what this code does,
how it is structured, and any notable patterns or issues.

Respond in this exact format:
VERDICT: pass OR fail
EXPLANATION: (2-3 sentences explaining why)"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text
    verdict = "pass" if "VERDICT: pass" in response_text else "fail"
    explanation = response_text.split("EXPLANATION:")[-1].strip() if "EXPLANATION:" in response_text else response_text

    return verdict, explanation
