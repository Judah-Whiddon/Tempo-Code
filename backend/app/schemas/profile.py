"""Profile-page response schemas. Shapes are kept stable for empty users —
the dict always carries every ProblemType key, the list is just empty —
so the frontend doesn't need conditional rendering for missing keys."""
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel

from app.models.models import ProblemType


class PerProblemStat(BaseModel):
    problem_id: UUID
    title:      str
    type:       ProblemType
    attempts:   int
    successes:  int
    accuracy:   float
    completed:  bool


class ProfileResponse(BaseModel):
    username: str
    problems_completed_by_type: Dict[str, int]
    per_problem_stats:          List[PerProblemStat]
