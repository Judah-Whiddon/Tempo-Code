import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, Text,
    DateTime, ForeignKey, ARRAY, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class ProblemType(str, enum.Enum):
    FLOW_IMPL       = "FLOW_IMPL"
    DEBUGGING       = "DEBUGGING"
    MOCK_INTERVIEW  = "MOCK_INTERVIEW"

class StepType(str, enum.Enum):
    START        = "START"
    LOOP         = "LOOP"
    NESTED_LOOP  = "NESTED_LOOP"
    CONDITION    = "CONDITION"
    RETURN       = "RETURN"
    END          = "END"

class Phase(str, enum.Enum):
    FLOW            = "FLOW"
    IMPLEMENTATION  = "IMPLEMENTATION"
    DEBUGGING       = "DEBUGGING"
    MOCK_INTERVIEW  = "MOCK_INTERVIEW"

class Difficulty(str, enum.Enum):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username      = Column(String(50),  nullable=False, unique=True)
    email         = Column(String(255), nullable=False, unique=True)
    password_hash = Column(Text,        nullable=False)
    streak_count  = Column(Integer,     nullable=False, default=0)
    created_at    = Column(DateTime(timezone=True), default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")
    progress    = relationship("Progress",   back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title         = Column(String(255), nullable=False)
    prompt        = Column(Text,        nullable=False)
    difficulty    = Column(
        SAEnum(Difficulty, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=Difficulty.BEGINNER,
    )
    topic         = Column(String(100))
    type          = Column(SAEnum(ProblemType), nullable=False)
    expected_flow = Column(JSONB)          # ordered step labels — FLOW_IMPL only
    starter_code  = Column(Text)           # pre-broken code — DEBUGGING only
    solution_code = Column(Text)
    tags          = Column(ARRAY(Text),   default=[])
    created_at    = Column(DateTime(timezone=True), default=datetime.utcnow)

    flow_steps  = relationship("FlowStep",   back_populates="problem", order_by="FlowStep.step_order")
    test_cases  = relationship("TestCase",   back_populates="problem")
    submissions = relationship("Submission", back_populates="problem")
    progress    = relationship("Progress",   back_populates="problem")


class FlowStep(Base):
    __tablename__ = "flow_steps"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    step_type  = Column(SAEnum(StepType), nullable=False)
    step_order = Column(Integer, nullable=False)
    label      = Column(Text,    nullable=False)

    problem = relationship("Problem", back_populates="flow_steps")


class TestCase(Base):
    __tablename__ = "test_cases"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id      = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    input           = Column(JSONB,   nullable=False)
    expected_output = Column(JSONB,   nullable=False)
    is_semantic     = Column(Boolean, nullable=False, default=False)

    problem = relationship("Problem", back_populates="test_cases")


class Submission(Base):
    __tablename__ = "submissions"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    phase      = Column(SAEnum(Phase), nullable=False)
    content    = Column(JSONB,  nullable=False)   # flow array | code string | text response
    is_correct = Column(Boolean, nullable=False, default=False)
    timestamp  = Column(DateTime(timezone=True), default=datetime.utcnow)

    user     = relationship("User",     back_populates="submissions")
    problem  = relationship("Problem",  back_populates="submissions")
    feedback = relationship("Feedback", back_populates="submission", uselist=False)


class Feedback(Base):
    __tablename__ = "feedback"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    verdict       = Column(String(20), nullable=False)   # 'pass' | 'fail' | 'partial'
    greened_steps = Column(JSONB)                        # which flow steps greened
    ai_response   = Column(Text)                         # mock interview verdict
    hint          = Column(Text)                         # optional AI hint
    timestamp     = Column(DateTime(timezone=True), default=datetime.utcnow)

    submission = relationship("Submission", back_populates="feedback")


class Progress(Base):
    __tablename__ = "progress"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    problem_id     = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    flow_completed = Column(Boolean, nullable=False, default=False)
    impl_unlocked  = Column(Boolean, nullable=False, default=False)
    attempts       = Column(Integer, nullable=False, default=0)
    completed_at   = Column(DateTime(timezone=True), nullable=True)

    user    = relationship("User",    back_populates="progress")
    problem = relationship("Problem", back_populates="progress")
