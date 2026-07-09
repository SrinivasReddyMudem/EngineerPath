"""Output schema for reel_script — 60s Reel/Short script for one technical topic."""

from pydantic import BaseModel, Field
from typing import Literal
from content_agents.core.shared_schema import SelfEvaluationLine

HookType = Literal["curiosity_gap", "fomo", "pain_point", "career_growth", "interview_pressure"]


class Analogy(BaseModel):
    statement: str = Field(description="The real-life analogy in one or two sentences")
    why_it_fits: str = Field(description="Explicit mapping: why the real-world action mirrors the technical concept")


class TechnicalExplanation(BaseModel):
    level_1_beginner: str = Field(description="Simple beginner explanation — no jargon")
    level_2_developer: str = Field(description="Developer-level explanation — assumes basic familiarity")
    level_3_professional: str = Field(description="Professional/production-usage explanation — the real engineering payoff")


class RealProjectExample(BaseModel):
    scenario: str = Field(description="A real situation, grounded in the topic's workflows reference")
    problem: str = Field(description="What goes wrong without this concept/technique")
    solution: str = Field(description="How the concept/technique resolves it")
    why_professionals_use_it: str = Field(description="The concrete engineering payoff, not a vague benefit")


class CommonMistakes(BaseModel):
    beginner_mistake: str
    professional_mistake: str
    interview_trap: str


class StoryboardShot(BaseModel):
    time_range: str = Field(description="e.g. '0-5s'")
    visual: str = Field(description="What's on screen")
    on_screen_text: str = Field(description="Text overlay for this shot")


class ReelScriptOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    hook: str = Field(description="Opening line using exactly one psychological pattern from hook_type")
    hook_type: HookType
    problem: str = Field(description="The problem this topic solves, stated crisply")
    analogy: Analogy
    technical_explanation: TechnicalExplanation
    real_project_example: RealProjectExample
    common_mistakes: CommonMistakes
    interview_question: str = Field(description="One real interview question tied to this topic")
    engagement_cta: str = Field(description="Value-offering CTA — never a bare 'follow for more'")
    visual_storyboard: list[StoryboardShot] = Field(description="At least 4 shots covering the full 60 seconds")
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="One PASS/FAIL line per quality gate: hook_pattern_match, analogy_has_why_it_fits, "
        "three_distinct_levels, example_grounded, all_mistake_tiers_present, cta_offers_value, storyboard_covers_60s"
    )
