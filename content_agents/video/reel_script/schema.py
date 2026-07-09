"""
Output schema for reel_script — 60s Reel/Short script for one technical topic.

Content philosophy: curiosity/understanding/confidence/motivation, never
fear/shame/insult. See prompt.py RULES for the full rationale.
"""

from pydantic import BaseModel, Field
from typing import Literal

HookType = Literal[
    "curiosity_hidden_power",
    "real_developer_situation",
    "transformation",
    "interview_importance",
    "mental_model",
]


class AnalogyMapping(BaseModel):
    real_world: str = Field(description="The real-world element, e.g. 'Bookmark location'")
    technical: str = Field(description="What it maps to technically, e.g. 'Git HEAD pointer'")


class Analogy(BaseModel):
    analogy: str = Field(description="The real-life scenario in one sentence, e.g. 'A bookmark in a book'")
    mapping: list[AnalogyMapping] = Field(description="At least 2 explicit real_world -> technical mappings")


class TechnicalExplanation(BaseModel):
    level_1_beginner: str = Field(description="Simple, technically correct mental model — never an incorrect oversimplification")
    level_2_developer: str = Field(description="Developer-level explanation — assumes basic familiarity")
    level_3_professional: str = Field(description="Professional/interview-level understanding — the real depth")


class RealProjectExample(BaseModel):
    scenario: str = Field(description="A real team/engineering situation, grounded in the topic's workflows reference")
    problem: str = Field(description="The confusion or friction this creates, stated without fear framing")
    solution: str = Field(description="How the concept/technique resolves it")
    why_professionals_use_it: str = Field(description="The concrete engineering payoff, connected to teamwork/code review/production practice")


class ConceptUnderstanding(BaseModel):
    beginner_misunderstanding: str = Field(description="What people commonly think, stated neutrally — not shameful")
    professional_insight: str = Field(description="How experienced engineers actually use/understand it")


class InterviewQA(BaseModel):
    question: str
    strong_answer: str = Field(description="What a strong answer covers")
    common_weak_answer: str = Field(description="What a weak-but-common answer looks like, and why it falls short")
    follow_up_question: str = Field(description="A natural follow-up an interviewer would ask next")


class StoryboardShot(BaseModel):
    time_range: str = Field(description="e.g. '0-5s'")
    visual: str = Field(description="What's on screen")
    animation: str = Field(description="What moves/changes during this shot")
    on_screen_text: str = Field(description="Text overlay for this shot")
    purpose: str = Field(description="What this shot is meant to achieve, e.g. 'Create mental model'")


class QualityScore(BaseModel):
    technical_accuracy: int = Field(ge=0, le=10)
    beginner_clarity: int = Field(ge=0, le=10)
    professional_relevance: int = Field(ge=0, le=10)
    hook_quality: int = Field(ge=0, le=10, description="If below 8, the hook must be regenerated before returning")
    analogy_quality: int = Field(ge=0, le=10, description="If below 8, the analogy must be regenerated before returning")
    share_save_potential: int = Field(ge=0, le=10)


class ReelScriptOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    hook: str = Field(description="Opening line using exactly one non-fear-based pattern from hook_type")
    hook_type: HookType
    problem: str = Field(description="What confusion exists and why understanding it matters — never fear-framed")
    analogy: Analogy
    technical_explanation: TechnicalExplanation
    real_project_example: RealProjectExample
    concept_understanding: ConceptUnderstanding
    interview: InterviewQA
    engagement_cta: str = Field(description="Value-offering CTA that encourages a learning community — never a bare 'follow for more'")
    visual_storyboard: list[StoryboardShot] = Field(description="At least 4 shots covering the full 60 seconds")
    quality_score: QualityScore = Field(description="Honest self-scored quality check — regenerate content if hook_quality or analogy_quality < 8, don't just lower the score")
