from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.models import Problem, ProblemType
from app.schemas.schemas import ProblemOut

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=List[ProblemOut])
def get_problems(
    type: Optional[ProblemType] = None,
    difficulty: Optional[str]   = None,
    db: Session = Depends(get_db)
):
    """
    Fetch all problems. Optionally filter by type or difficulty.
    This is the primary endpoint the frontend calls on the Problem Type
    Selection screen.
    """
    query = db.query(Problem)
    if type:
        query = query.filter(Problem.type == type)
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    return query.all()


@router.get("/{problem_id}", response_model=ProblemOut)
def get_problem(problem_id: UUID, db: Session = Depends(get_db)):
    """Fetch a single problem by ID, including its flow steps and test cases."""
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem
