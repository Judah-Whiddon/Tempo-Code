from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Submission, Feedback, Progress, Problem, Phase, User
from app.schemas.schemas import SubmissionIn, SubmissionOut
from app.security import get_current_user_optional
from app.services.grader import grade_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])

# Anonymous (logged-out) submissions attach to this row. Created by seed.py;
# kept around so the FK constraint is satisfied without forcing login.
ANONYMOUS_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@router.post("/", response_model=SubmissionOut)
def submit(
    payload: SubmissionIn,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Accept a submission. Authentication is optional — anonymous submissions
    attach to the placeholder/demo user so the practice loop works without
    login. Logged-in submissions attach to the real user for profile tracking.
    """
    problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    user_id = current_user.id if current_user else ANONYMOUS_USER_ID

    submission = Submission(
        user_id    = user_id,
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
        user_id=user_id,
        problem_id=payload.problem_id,
    ).first()

    if not progress:
        progress = Progress(
            user_id        = user_id,
            problem_id     = payload.problem_id,
            flow_completed = False,
            impl_unlocked  = False,
            attempts       = 0,
        )
        db.add(progress)

    progress.attempts += 1

    if payload.phase == Phase.FLOW and verdict == "pass":
        progress.flow_completed = True
        progress.impl_unlocked  = True

    if payload.phase in (Phase.IMPLEMENTATION, Phase.DEBUGGING, Phase.MOCK_INTERVIEW) and verdict == "pass":
        progress.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)
    return submission
