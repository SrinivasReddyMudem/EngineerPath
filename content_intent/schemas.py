"""
Content Intent Classifier output — understands what the user actually
wants before any generation happens. One generic classifier for any
topic/query, not a per-topic or per-intent agent.
"""

from pydantic import BaseModel, Field
from typing import Literal

IntentType = Literal[
    "concept_explanation",
    "comparison",
    "mistake_correction",
    "interview_preparation",
    "real_project_scenario",
    "quick_tip",
]

AudienceLevel = Literal["beginner", "intermediate", "professional", "mixed"]


class IntentClassification(BaseModel):
    model_config = {"extra": "ignore"}

    query: str
    intent_type: IntentType
    audience_level: AudienceLevel
    learning_goal: str = Field(description="What the viewer should be able to do/understand after this content")
    recommended_content_structure: str = Field(
        description="Which sections to emphasize for this query, e.g. 'comparison table + decision rule' or 'hook + analogy + technical depth'"
    )
