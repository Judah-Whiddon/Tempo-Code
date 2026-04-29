from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import get_db
from app.models.models import Submission, Feedback, Progress, Problem, Phase
from app.schemas.schemas import SubmissionIn, SubmissionOut
from app.services.grader import grade_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionOut)
def submit(payload: SubmissionIn, db: Session = Depends(get_db)):
    """
    Accept a submission from the frontend.
    Routes to the correct grader based on problem type and phase.
    Returns a Feedback record with verdict and optional hint.

    NOTE: user_id is hardcoded as a placeholder until auth is wired up.
    """
    problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # TODO: replace with real user_id from JWT token once auth is implemented
    PLACEHOLDER_USER_ID = "00000000-0000-0000-0000-000000000001"

    submission = Submission(
        user_id    = PLACEHOLDER_USER_ID,
        problem_id = payload.problem_id,
        phase      = payload.phase,
        content    = payload.content,
        is_correct = False,
    )
    db.add(submission)
    db.flush()  # get submission.id before creating feedback

    # Grade and create feedback
    verdict, greened_steps, ai_response, hint = grade_submission(
        problem=problem,
        submission=submission,
        db=db,
    )

    submission.is_correct = verdict == "pass"

    feedback = Feedback(
        submission_id = submission.id,
        verdict       = verdict,
        greened_steps = greened_steps,
        ai_response   = ai_response,
        hint          = hint,
    )
    db.add(feedback)

    # Update progress — unlock implementation phase if flow is greened
    progress = db.query(Progress).filter_by(
        user_id=PLACEHOLDER_USER_ID,
        problem_id=payload.problem_id
    ).first()

    if not progress:
        progress = Progress(
            user_id    = PLACEHOLDER_USER_ID,
            problem_id = payload.problem_id,
        )
        db.add(progress)

    progress.attempts += 1

    if payload.phase == Phase.FLOW and verdict == "pass":
        progress.flow_completed = True
        progress.impl_unlocked  = True

    if payload.phase in (Phase.IMPLEMENTATION, Phase.DEBUGGING, Phase.MOCK_INTERVIEW) and verdict == "pass":
        from datetime import datetime
        progress.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)
    return submission
