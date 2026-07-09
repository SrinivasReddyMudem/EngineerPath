"""
Output schema for reel_script — 60s Reel/Short script for one technical topic.

Content philosophy: curiosity/understanding/confidence/motivation, never
fear/shame/insult. See prompt.py RULES for the full rationale.
"""

from pydantic import BaseModel, Field
from typing import Literal

HookType = Literal[
    "curiosity_gap",
    "real_developer_situation",
    "interview_value",
    "mistake_correction",
    "transformation",
    "contrarian",
    "story",
    "challenge",
    "authority",
    "community",
]

MistakeLevel = Literal["beginner", "intermediate", "professional", "interview"]


class ProblemSetup(BaseModel):
    real_world_problem: str = Field(description="The concrete situation where this confusion shows up")
    developer_pain: str = Field(description="What specifically frustrates or blocks the developer")
    why_it_matters: str = Field(description="Why understanding this actually matters, not just 'it's important'")
    learning_goal: str = Field(description="What the viewer will be able to do after watching")


class AnalogyMapping(BaseModel):
    real_world: str = Field(description="The real-world element, e.g. 'Playhead position'")
    technical: str = Field(description="What it maps to technically, e.g. 'Git HEAD pointer'")


class Analogy(BaseModel):
    analogy: str = Field(description="The real-life scenario in one sentence, e.g. 'Editing a video timeline'")
    mapping: list[AnalogyMapping] = Field(description="At least 2 explicit real_world -> technical mappings")
    limitations: str = Field(description="Where this analogy breaks down or stops applying — required so it can't create a misconception")


class TechnicalExplanation(BaseModel):
    level_1_beginner: str = Field(description="WHAT it is — simple, technically correct, no jargon")
    level_2_developer: str = Field(description="HOW it works — assumes basic familiarity")
    level_3_professional: str = Field(description="WHY and WHEN to use it — the real engineering judgment")
    internal_working: str = Field(description="The deep internal mechanism — exact, not approximated")


class RealProjectExample(BaseModel):
    industry_context: str = Field(description="e.g. 'software team', 'embedded project', 'cloud system'")
    scenario: str = Field(description="A real team/engineering situation, grounded in the topic's workflows reference")
    problem: str = Field(description="The confusion or friction this creates, stated without fear framing")
    solution: str = Field(description="How the concept/technique resolves it")
    professional_reasoning: str = Field(description="Why an engineer would actually choose this — connected to teamwork/code review/production")


class MistakeEntry(BaseModel):
    level: MistakeLevel
    wrong_belief: str
    correct_understanding: str
    professional_tip: str


class InterviewQA(BaseModel):
    question: str
    why_interviewer_asks: str = Field(description="What this question reveals about the candidate's understanding")
    strong_answer: str = Field(description="Must cover: definition, internal mechanism, practical example")
    weak_answer: str = Field(description="A common but incomplete answer, and implicitly why it falls short")
    follow_up_questions: list[str] = Field(description="At least 1 natural follow-up an interviewer would ask next")


class StoryboardShot(BaseModel):
    """
    These shots ARE the reel, in order — voice_script is compiled by
    concatenating every shot's `voice` line (see production/compiler.py).
    There is no separate free-standing narration: one idea per shot,
    written in the order it should be heard, is the whole script.
    """
    time_range: str = Field(description="e.g. '0-5s'")
    visual: str = Field(description="WHO is on screen, WHERE, WHAT ACTION — e.g. 'A developer at a laptop; terminal shows commits A-B-C; C is highlighted red', never 'show logo'")
    animation: str = Field(description="The specific motion, e.g. 'HEAD pointer slides backward from C to B'")
    camera: str = Field(description="How the viewer sees it, e.g. 'Zoom into the commit history' or 'Static wide shot'")
    voice: str = Field(description="ONE self-contained spoken idea for this shot — never combine multiple facts (e.g. HEAD move + index change + working dir change) in one line")
    on_screen_text: str = Field(description="Text overlay for this shot")
    learning_objective: str = Field(description="What this shot is meant to teach")


class ContentPlan(BaseModel):
    main_insight: str = Field(description="The ONE thing the viewer should remember — not a list")
    content_boundary: str = Field(description="What this reel deliberately does NOT cover, to stay focused on one transformation")


COMPARISON_DIMENSIONS = ["Purpose", "Main Action", "History Impact", "When To Use", "When Not To Use", "Professional Recommendation"]


class ComparisonRow(BaseModel):
    dimension: Literal["Purpose", "Main Action", "History Impact", "When To Use", "When Not To Use", "Professional Recommendation"]
    concept_a_value: str
    concept_b_value: str


class ComparisonStructure(BaseModel):
    """Populated ONLY when the query is a comparison (e.g. 'Git reset vs Git rebase'); null otherwise."""
    concept_a: str
    concept_b: str
    why_confused: str = Field(description="Why people mix these two up")
    concept_a_definition: str
    concept_b_definition: str
    comparison_rows: list[ComparisonRow] = Field(description="One row per required dimension — all 6 required")
    decision_rule: str = Field(description="One clear rule for which to use when")


class QualityScore(BaseModel):
    technical_accuracy: int = Field(ge=0, le=10, description="If below 9, regenerate the inaccurate section")
    teaching_quality: int = Field(ge=0, le=10)
    hook_strength: int = Field(ge=0, le=10, description="If below 8, create another hook")
    analogy_quality: int = Field(ge=0, le=10, description="If below 8, regenerate the analogy")
    real_world_relevance: int = Field(ge=0, le=10)
    interview_value: int = Field(ge=0, le=10)
    shareability: int = Field(ge=0, le=10)


class ReelScriptOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    content_plan: ContentPlan
    recommended_visual_style: str = Field(description="e.g. 'Stick figure + animated diagrams' — one consistent style for the AI video tool")
    hook: str = Field(description="Opening line using exactly one non-fear-based pattern from hook_type")
    hook_type: HookType
    problem: ProblemSetup
    analogy: Analogy
    technical_explanation: TechnicalExplanation
    real_project_example: RealProjectExample
    concept_mistakes: list[MistakeEntry] = Field(description="At least 2 entries with distinct levels (beginner/intermediate/professional/interview)")
    interview: InterviewQA
    comparison: ComparisonStructure | None = Field(default=None, description="Populate ONLY for a comparison query (e.g. 'X vs Y'); otherwise null")
    memory_anchor: str = Field(description="One short, quotable recap sentence — spoken right before the CTA")
    engagement_cta: str = Field(description="Value-offering CTA — comment-for-reward, tag a friend, save-this, or follow-a-named-series — never a bare 'follow for more'")
    visual_storyboard: list[StoryboardShot] = Field(description="At least 4 shots covering the full 60 seconds")
    quality_score: QualityScore = Field(description="Honest self-scored quality check — regenerate the specific section if a gated score is too low, don't just lower the number")
