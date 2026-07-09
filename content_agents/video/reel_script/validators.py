"""
Domain validators for reel_script — one quality gate per schema section.
Content philosophy: curiosity/understanding/confidence/motivation, never
fear/shame/insult — see BANNED_HOOK_PHRASES and BANNED_GENERIC_AI_PHRASES.
"""

from content_agents.core.base_agent import QualityCheckError
from .schema import ReelScriptOutput

MIN_MAPPING_PAIRS = 2
MIN_LEVEL_LEN = 25
MIN_EXAMPLE_FIELD_LEN = 20
MIN_UNDERSTANDING_LEN = 20
MIN_INTERVIEW_FIELD_LEN = 15
MIN_STORYBOARD_SHOTS = 4
MIN_SCORE_TO_PASS = 8

BANNED_PREAMBLE_PHRASES = [
    "in this video",
    "in this reel",
    "today we will",
    "today we'll",
    "let's talk about",
    "let's discuss",
    "in this post",
]

# Fear/shame/insult-based hooks are banned outright, regardless of hook_type —
# see EngineerPath Content Philosophy: never create content based on fear,
# shame, or insulting the audience.
BANNED_HOOK_PHRASES = [
    "most developers don't know",
    "most devs don't know",
    "you are using git wrong",
    "you're using git wrong",
    "using it wrong",
    "doing it wrong",
    "stop doing this immediately",
    "this mistake will destroy your career",
    "only 1% of developers",
    "only 1% developers",
]

BANNED_GENERIC_AI_PHRASES = [
    "in today's fast-paced world",
    "let's dive in",
    "unlock the power of",
    "in this digital age",
]

BANNED_CTA_PHRASES = [
    "follow for more",
    "like and subscribe",
    "hit the follow button",
    "don't forget to subscribe",
]

TEAMWORK_CONTEXT_KEYWORDS = [
    "team", "review", "pull request", "pr ", "production", "colleague", "teammate", "code review",
]


def validate(output: ReelScriptOutput) -> None:
    _check_no_preamble(output)
    _check_hook_not_fear_or_generic(output)
    _check_analogy(output)
    _check_technical_explanation(output)
    _check_real_project_example(output)
    _check_concept_understanding(output)
    _check_interview(output)
    _check_cta(output)
    _check_storyboard(output)
    _check_quality_score(output)


def _check_no_preamble(output: ReelScriptOutput) -> None:
    hook_lower = output.hook.lower()
    for banned in BANNED_PREAMBLE_PHRASES:
        if banned in hook_lower:
            raise QualityCheckError(
                f"hook contains preamble phrase '{banned}'. The hook must start at the payoff, "
                f"not introduce the video — this kills retention in the first 3 seconds."
            )


def _check_hook_not_fear_or_generic(output: ReelScriptOutput) -> None:
    hook_lower = output.hook.lower()
    for banned in BANNED_HOOK_PHRASES:
        if banned in hook_lower:
            raise QualityCheckError(
                f"hook uses banned fear/insult phrase '{banned}'. The content philosophy bans "
                f"hooks that attack developers or create fear — rewrite using curiosity, a real "
                f"developer situation, transformation, non-threatening interview importance, or a "
                f"mental model instead."
            )
    for banned in BANNED_GENERIC_AI_PHRASES:
        if banned in hook_lower:
            raise QualityCheckError(f"hook uses generic AI phrase '{banned}'. Rewrite in a specific, human voice.")
    if len(output.hook.strip()) < 10:
        raise QualityCheckError("hook is too short to be a real opening line.")


def _check_analogy(output: ReelScriptOutput) -> None:
    if len(output.analogy.mapping) < MIN_MAPPING_PAIRS:
        raise QualityCheckError(
            f"analogy.mapping has {len(output.analogy.mapping)} pairs, needs at least {MIN_MAPPING_PAIRS} "
            f"explicit real_world -> technical mappings."
        )
    for i, pair in enumerate(output.analogy.mapping):
        if not pair.real_world.strip() or not pair.technical.strip():
            raise QualityCheckError(f"analogy.mapping[{i}] has an empty real_world or technical field.")


def _check_technical_explanation(output: ReelScriptOutput) -> None:
    te = output.technical_explanation
    levels = [te.level_1_beginner, te.level_2_developer, te.level_3_professional]
    for i, level in enumerate(levels, start=1):
        if len(level.strip()) < MIN_LEVEL_LEN:
            raise QualityCheckError(f"technical_explanation level_{i} is too short ({len(level)} chars).")
    if len({levels[0].strip(), levels[1].strip(), levels[2].strip()}) < 3:
        raise QualityCheckError(
            "technical_explanation levels must be three genuinely distinct explanations, not near-duplicates."
        )


def _check_real_project_example(output: ReelScriptOutput) -> None:
    ex = output.real_project_example
    fields = {
        "scenario": ex.scenario,
        "problem": ex.problem,
        "solution": ex.solution,
        "why_professionals_use_it": ex.why_professionals_use_it,
    }
    for name, value in fields.items():
        if len(value.strip()) < MIN_EXAMPLE_FIELD_LEN:
            raise QualityCheckError(f"real_project_example.{name} is too short ({len(value)} chars).")
    combined = " ".join(fields.values()).lower()
    if not any(kw in combined for kw in TEAMWORK_CONTEXT_KEYWORDS):
        raise QualityCheckError(
            "real_project_example must connect to teamwork, code review, or production practice — "
            "none of those contexts were found in the example."
        )


def _check_concept_understanding(output: ReelScriptOutput) -> None:
    cu = output.concept_understanding
    if len(cu.beginner_misunderstanding.strip()) < MIN_UNDERSTANDING_LEN:
        raise QualityCheckError("concept_understanding.beginner_misunderstanding is too short or missing.")
    if len(cu.professional_insight.strip()) < MIN_UNDERSTANDING_LEN:
        raise QualityCheckError("concept_understanding.professional_insight is too short or missing.")


def _check_interview(output: ReelScriptOutput) -> None:
    qa = output.interview
    fields = {
        "question": qa.question,
        "strong_answer": qa.strong_answer,
        "common_weak_answer": qa.common_weak_answer,
        "follow_up_question": qa.follow_up_question,
    }
    for name, value in fields.items():
        if len(value.strip()) < MIN_INTERVIEW_FIELD_LEN:
            raise QualityCheckError(f"interview.{name} is too short ({len(value)} chars) or missing.")
    if qa.strong_answer.strip().lower() == qa.common_weak_answer.strip().lower():
        raise QualityCheckError("interview.strong_answer and common_weak_answer must not be identical.")


def _check_cta(output: ReelScriptOutput) -> None:
    cta_lower = output.engagement_cta.lower().strip()
    for banned in BANNED_CTA_PHRASES:
        if banned in cta_lower:
            raise QualityCheckError(
                f"engagement_cta uses banned generic phrase '{banned}'. "
                f"CTA must offer specific value or invite the viewer into a learning community."
            )
    if len(cta_lower) < 10:
        raise QualityCheckError("engagement_cta is too short.")


def _check_storyboard(output: ReelScriptOutput) -> None:
    if len(output.visual_storyboard) < MIN_STORYBOARD_SHOTS:
        raise QualityCheckError(
            f"visual_storyboard has {len(output.visual_storyboard)} shots, needs at least "
            f"{MIN_STORYBOARD_SHOTS} to plausibly cover 60 seconds."
        )
    for i, shot in enumerate(output.visual_storyboard):
        fields = {
            "visual": shot.visual, "animation": shot.animation,
            "on_screen_text": shot.on_screen_text, "purpose": shot.purpose,
        }
        for name, value in fields.items():
            if not value.strip():
                raise QualityCheckError(f"visual_storyboard[{i}].{name} is empty — every scene needs all fields specified, not a generic visual.")


def _check_quality_score(output: ReelScriptOutput) -> None:
    qs = output.quality_score
    if qs.hook_quality < MIN_SCORE_TO_PASS:
        raise QualityCheckError(
            f"quality_score.hook_quality is {qs.hook_quality}, below the required {MIN_SCORE_TO_PASS}. "
            f"Regenerate the hook using a stronger pattern, don't just report a low score."
        )
    if qs.analogy_quality < MIN_SCORE_TO_PASS:
        raise QualityCheckError(
            f"quality_score.analogy_quality is {qs.analogy_quality}, below the required {MIN_SCORE_TO_PASS}. "
            f"Regenerate the analogy with a more accurate, better-mapped comparison."
        )
