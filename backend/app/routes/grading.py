from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import List

from app.db.database import get_db
from app.models.models import Problem
from app.services.grader import grade_steps, StepGraderError

router = APIRouter(prefix="/grade", tags=["grading"])


class StepGradeIn(BaseModel):
    problem_id: UUID
    code:       str


class StepGradeOut(BaseModel):
    completed_steps: List[str]


@router.post("/steps", response_model=StepGradeOut)
def grade_steps_endpoint(payload: StepGradeIn, db: Session = Depends(get_db)):
    """
    Classify which FlowStep labels the user's current code already covers.

    AI is the step *detector*, not the verdict — the test runner still owns
    pass/fail in /submissions. On any LLM failure we return 503 so the
    frontend can degrade silently (steps just don't update on Run).
    """
    problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    flow_labels = [step.label for step in problem.flow_steps]
    if not flow_labels:
        return StepGradeOut(completed_steps=[])

    try:
        completed = grade_steps(code=payload.code, flow_steps=flow_labels)
    except StepGraderError:
        raise HTTPException(status_code=503, detail="ai_unavailable")

    return StepGradeOut(completed_steps=completed)
