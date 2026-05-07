from fastapi import APIRouter, Depends
from sqlalchemy import Integer, case, func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Problem, ProblemType, Progress, Submission, User
from app.schemas.profile import PerProblemStat, ProfileResponse
from app.security import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return per-user practice stats. Strict auth — anonymous traffic does
    not get a profile (the frontend renders a logged-out stub instead)."""

    # Section 1 — completed-by-type. Pre-fill every enum so the response shape
    # is stable for new users (empty table → all zeros, never missing keys).
    completed_by_type: dict[str, int] = {pt.value: 0 for pt in ProblemType}
    rows = (
        db.query(Problem.type, func.count(Progress.id))
          .join(Progress, Progress.problem_id == Problem.id)
          .filter(Progress.user_id == current_user.id)
          .filter(Progress.completed_at.isnot(None))
          .group_by(Problem.type)
          .all()
    )
    for ptype, count in rows:
        completed_by_type[ptype.value] = count

    # Section 2 — per-problem stats. One row per problem the user has any
    # submission against. LEFT JOIN Progress so missing-progress rows still
    # report (completed=False). is_correct is a bool — cast to int to sum.
    successes = func.coalesce(
        func.sum(case((Submission.is_correct, 1), else_=0)), 0,
    )
    raw = (
        db.query(
            Problem.id,
            Problem.title,
            Problem.type,
            func.count(Submission.id).label("attempts"),
            successes.label("successes"),
        )
          .join(Submission, Submission.problem_id == Problem.id)
          .filter(Submission.user_id == current_user.id)
          .group_by(Problem.id, Problem.title, Problem.type)
          .all()
    )

    completed_map = {
        p.problem_id: p.completed_at is not None
        for p in db.query(Progress).filter(Progress.user_id == current_user.id).all()
    }

    per_problem: list[PerProblemStat] = []
    for pid, title, ptype, attempts, succ in raw:
        attempts_i = int(attempts or 0)
        succ_i     = int(succ or 0)
        # Compute accuracy in Python — guards the divide-by-zero edge cleanly
        # (attempts can't be 0 here because the row was produced by a JOIN on
        # Submission, but defensive doesn't cost anything).
        accuracy = (succ_i / attempts_i) if attempts_i else 0.0
        per_problem.append(PerProblemStat(
            problem_id = pid,
            title      = title,
            type       = ptype,
            attempts   = attempts_i,
            successes  = succ_i,
            accuracy   = round(accuracy, 4),
            completed  = bool(completed_map.get(pid, False)),
        ))

    return ProfileResponse(
        username                   = current_user.username,
        problems_completed_by_type = completed_by_type,
        per_problem_stats          = per_problem,
    )
