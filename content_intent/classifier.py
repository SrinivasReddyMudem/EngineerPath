"""
Content Intent Classifier — understands user intention before any
generation happens. Fast, cheap, generic (works for any topic/query).
"""

from content_agents.core.base_agent import BaseAgent
from .schemas import IntentClassification
from . import validators

RULES = """
# Content Intent Classification

Classify a raw user query into exactly one intent_type:

- concept_explanation: "What is Git rebase?"
- comparison: "Git reset vs Git rebase"
- mistake_correction: "Common Git mistakes beginners make"
- interview_preparation: "Git rebase interview question"
- real_project_scenario: "How Git is used in software teams"
- quick_tip: "One Git command every developer should know"

Also determine audience_level (beginner/intermediate/professional/mixed)
from the query's phrasing and vocabulary, a concrete learning_goal (what
the viewer should be able to do/understand afterward), and a short
recommended_content_structure describing which sections to emphasize
(e.g. a comparison query should emphasize "comparison table + decision
rule"; a concept query should emphasize "analogy + technical depth").
"""


class IntentClassifierAgent(BaseAgent):
    AGENT_NAME = "intent-classifier"

    def get_schema(self):
        return IntentClassification

    def get_prompt(self) -> str:
        return RULES

    def _validate_quality(self, parsed: IntentClassification) -> None:
        validators.validate(parsed)


__all__ = ["IntentClassifierAgent"]
