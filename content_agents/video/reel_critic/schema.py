"""
Output schema for reel_critic — an independent audience-psychology and
educational-experience review of an ALREADY-GENERATED reel script.

Deliberately a separate agent, not more self-scored fields on the
generator: the generator grading its own output is a weak signal (it
tends to rate itself uniformly high). A different call, with a critic's
persona and no stake in the script being good, is a real second opinion.
"""

from pydantic import BaseModel, Field
from typing import Literal


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=10)
    critique: str = Field(description="Specific reasoning quoting the actual script — not generic praise or complaint")
    improvement_suggestion: str = Field(description="One concrete, actionable fix — not a vague 'make it better'")


class ReelCritique(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    curiosity: DimensionScore = Field(description="Does the first line create a genuine open question in under 3 seconds?")
    mental_model: DimensionScore = Field(description="Does the analogy produce an actual 'aha', or is it decorative?")
    story_flow: DimensionScore = Field(description="Setup -> tension -> insight -> payoff, or a list of facts?")
    natural_language: DimensionScore = Field(description="Would a real person actually say this out loud?")
    retention: DimensionScore = Field(description="Is there a reason to keep watching past each cut point?")
    shareability: DimensionScore = Field(description="Would someone send this to a friend, and why?")
    emotional_connection: DimensionScore = Field(description="Does the viewer feel understood, not judged?")
    conversation_style: DimensionScore = Field(description="Second person, contractions, rhythm — or stiff and formal?")
    visual_explainability: DimensionScore = Field(description="Could the storyboard be filmed and make sense without narration?")
    beginner_friendliness: DimensionScore = Field(description="Would a junior developer follow this on first watch?")
    professional_relevance: DimensionScore = Field(description="Does a senior engineer learn something or tune out?")
    overall_verdict: Literal["ready_to_publish", "needs_revision"]
    top_priority_fix: str = Field(description="The SINGLE most impactful change — not a list")
