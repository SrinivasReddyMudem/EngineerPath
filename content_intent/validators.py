"""Structural validators for intent classification — deliberately light."""

from content_agents.core.base_agent import QualityCheckError
from .schemas import IntentClassification

MIN_LEARNING_GOAL_LEN = 10
MIN_STRUCTURE_LEN = 10


def validate(output: IntentClassification) -> None:
    if len(output.learning_goal.strip()) < MIN_LEARNING_GOAL_LEN:
        raise QualityCheckError("learning_goal is too short or missing.")
    if len(output.recommended_content_structure.strip()) < MIN_STRUCTURE_LEN:
        raise QualityCheckError("recommended_content_structure is too short or missing.")
