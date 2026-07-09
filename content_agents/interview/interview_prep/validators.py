"""
Minimal validators for interview_prep — schema completeness only for now.
Deferred: per-question quality gates (answer points grounded in references,
no duplicate questions across levels) — add these after live-testing output.
"""

from content_agents.core.base_agent import QualityCheckError
from .schema import InterviewPrepOutput

REQUIRED_LEVELS = {"beginner", "intermediate", "advanced", "expert"}


def validate(output: InterviewPrepOutput) -> None:
    present_levels = {q.level for q in output.questions}
    missing = REQUIRED_LEVELS - present_levels
    if missing:
        raise QualityCheckError(f"Missing questions for level(s): {sorted(missing)}. All four levels are required.")
    for i, q in enumerate(output.questions):
        if not q.ideal_answer_points:
            raise QualityCheckError(f"questions[{i}] has no ideal_answer_points.")
