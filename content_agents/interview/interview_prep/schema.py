"""Output schema for interview_prep. Minimal validators for now — harden after live testing."""

from pydantic import BaseModel, Field
from typing import Literal

DifficultyLevel = Literal["beginner", "intermediate", "advanced", "expert"]


class InterviewQuestion(BaseModel):
    level: DifficultyLevel
    question: str
    ideal_answer_points: list[str] = Field(description="Key points a correct answer must hit")


class InterviewPrepOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    questions: list[InterviewQuestion] = Field(description="At least one question per difficulty level")
