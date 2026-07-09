"""
Minimal validators for quiz — structural correctness only for now.
Deferred: difficulty-mix balance checks, distractor-quality checks —
add these after live-testing output.
"""

from content_agents.core.base_agent import QualityCheckError
from .schema import QuizOutput

MIN_QUESTIONS = 5


def validate(output: QuizOutput) -> None:
    if len(output.questions) < MIN_QUESTIONS:
        raise QualityCheckError(f"questions has {len(output.questions)} items, needs at least {MIN_QUESTIONS}.")
    for i, q in enumerate(output.questions):
        if len(q.options) != 4:
            raise QualityCheckError(f"questions[{i}] has {len(q.options)} options, must have exactly 4.")
        if not (0 <= q.correct_answer_index <= 3):
            raise QualityCheckError(f"questions[{i}].correct_answer_index must be 0-3.")
        if not q.explanation.strip():
            raise QualityCheckError(f"questions[{i}] has no explanation.")
