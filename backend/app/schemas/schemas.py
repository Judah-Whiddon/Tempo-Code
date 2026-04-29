from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from app.models.models import ProblemType, StepType, Phase, Difficulty


# ── Problem ───────────────────────────────────────────────────────────────────

class FlowStepOut(BaseModel):
    id:         UUID
    step_type:  StepType
    step_order: int
    label:      str

    class Config:
        from_attributes = True

class TestCaseOut(BaseModel):
    id:              UUID
    input:           Any
    expected_output: Any
    is_semantic:     bool

    class Config:
        from_attributes = True

class ProblemOut(BaseModel):
    id:            UUID
    title:         str
    prompt:        str
    difficulty:    Difficulty
    topic:         Optional[str]
    type:          ProblemType
    expected_flow: Optional[Any]
    starter_code:  Optional[str]
    tags:          List[str]
    flow_steps:    List[FlowStepOut] = []
    test_cases:    List[TestCaseOut] = []

    class Config:
        from_attributes = True


# ── Submission ────────────────────────────────────────────────────────────────

class SubmissionIn(BaseModel):
    problem_id: UUID
    phase:      Phase
    content:    Any       # flow array | {"code": "..."} | {"response": "..."}

class FeedbackOut(BaseModel):
    id:            UUID
    verdict:       str
    greened_steps: Optional[Any]
    ai_response:   Optional[str]
    hint:          Optional[str]
    timestamp:     datetime

    class Config:
        from_attributes = True

class SubmissionOut(BaseModel):
    id:         UUID
    phase:      Phase
    is_correct: bool
    timestamp:  datetime
    feedback:   Optional[FeedbackOut]

    class Config:
        from_attributes = True


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressOut(BaseModel):
    problem_id:     UUID
    flow_completed: bool
    impl_unlocked:  bool
    attempts:       int
    completed_at:   Optional[datetime]

    class Config:
        from_attributes = True


# ── Auth (stub — wired up later) ──────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email:    EmailStr
    password: str

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"
