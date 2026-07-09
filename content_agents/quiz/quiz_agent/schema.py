"""Output schema for quiz. Minimal validators for now — harden after live testing."""

from pydantic import BaseModel, Field
from typing import Literal


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(description="Exactly 4 options")
    correct_answer_index: int = Field(description="0-based index into options")
    explanation: str = Field(description="Why the correct answer is right")
    difficulty: Literal["easy", "medium", "hard"]


class QuizOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    questions: list[QuizQuestion] = Field(description="At least 5 questions")
