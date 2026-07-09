"""
Domain validators for reel_script — one quality gate per schema section.
Every field the user's content spec calls out gets an explicit check here,
not just the hook.
"""

from content_agents.core.base_agent import QualityCheckError
from .schema import ReelScriptOutput

MIN_ANALOGY_WHY_LEN = 40
MIN_LEVEL_LEN = 25
MIN_EXAMPLE_FIELD_LEN = 20
MIN_MISTAKE_LEN = 20
MIN_INTERVIEW_Q_LEN = 15
MIN_STORYBOARD_SHOTS = 4

BANNED_PREAMBLE_PHRASES = [
    "in this video",
    "in this reel",
    "today we will",
    "today we'll",
    "let's talk about",
    "let's discuss",
    "in this post",
]

BANNED_CTA_PHRASES = [
    "follow for more",
    "like and subscribe",
    "hit the follow button",
    "don't forget to subscribe",
]

BANNED_WEAK_ANALOGY_PHRASES = [
    "is like a tree branch",
    "is like a save button",
    "mixing two colors of paint",
]

HOOK_TYPE_KEYWORDS: dict[str, list[str]] = {
    "curiosity_gap": ["most", "don't know", "secret", "hidden", "few people", "nobody tells you", "what nobody"],
    "fomo": ["if you don't", "you're probably", "you might be", "without this", "you are missing"],
    "pain_point": ["mistake", "problem", "issue", "wrong", "breaks", "fails", "unnecessary"],
    "career_growth": ["beginner", "professional", "junior", "senior", "career", "promotion", "difference between"],
    "interview_pressure": ["interview", "candidates", "fail this", "asked in", "get rejected"],
}


def validate(output: ReelScriptOutput) -> None:
    _check_no_preamble(output)
    _check_hook_matches_type(output)
    _check_analogy(output)
    _check_technical_explanation(output)
    _check_real_project_example(output)
    _check_common_mistakes(output)
    _check_interview_question(output)
    _check_cta(output)
    _check_storyboard(output)
    _check_self_evaluation_has_evidence(output)


def _check_no_preamble(output: ReelScriptOutput) -> None:
    hook_lower = output.hook.lower()
    for banned in BANNED_PREAMBLE_PHRASES:
        if banned in hook_lower:
            raise QualityCheckError(
                f"hook contains preamble phrase '{banned}'. The hook must start at the payoff, "
                f"not introduce the video — this kills retention in the first 3 seconds."
            )


def _check_hook_matches_type(output: ReelScriptOutput) -> None:
    hook_lower = output.hook.lower()
    keywords = HOOK_TYPE_KEYWORDS[output.hook_type]
    if not any(kw in hook_lower for kw in keywords):
        raise QualityCheckError(
            f"hook '{output.hook}' does not match declared hook_type '{output.hook_type}'. "
            f"Expected one of these signal phrases: {keywords}. Either rewrite the hook to genuinely "
            f"use this pattern, or change hook_type to match what the hook actually does."
        )
    if len(output.hook.strip()) < 10:
        raise QualityCheckError("hook is too short to be a real opening line.")


def _check_analogy(output: ReelScriptOutput) -> None:
    statement_lower = output.analogy.statement.lower()
    for banned in BANNED_WEAK_ANALOGY_PHRASES:
        if banned in statement_lower:
            raise QualityCheckError(
                f"analogy.statement uses a banned weak analogy pattern: '{banned}'. "
                f"Use a concrete real-world action with a clear mapping instead."
            )
    if len(output.analogy.why_it_fits.strip()) < MIN_ANALOGY_WHY_LEN:
        raise QualityCheckError(
            f"analogy.why_it_fits is too short ({len(output.analogy.why_it_fits)} chars). "
            f"Must explicitly explain why the real-world mapping holds, not just restate the analogy."
        )


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


def _check_common_mistakes(output: ReelScriptOutput) -> None:
    m = output.common_mistakes
    fields = {
        "beginner_mistake": m.beginner_mistake,
        "professional_mistake": m.professional_mistake,
        "interview_trap": m.interview_trap,
    }
    for name, value in fields.items():
        if len(value.strip()) < MIN_MISTAKE_LEN:
            raise QualityCheckError(f"common_mistakes.{name} is too short ({len(value)} chars) or missing.")


def _check_interview_question(output: ReelScriptOutput) -> None:
    if len(output.interview_question.strip()) < MIN_INTERVIEW_Q_LEN:
        raise QualityCheckError("interview_question is too short to be a real interview question.")
    if output.interview_question.strip().rstrip(".!") == output.hook.strip().rstrip(".!"):
        raise QualityCheckError("interview_question must not just repeat the hook verbatim.")


def _check_cta(output: ReelScriptOutput) -> None:
    cta_lower = output.engagement_cta.lower().strip()
    for banned in BANNED_CTA_PHRASES:
        if banned in cta_lower:
            raise QualityCheckError(
                f"engagement_cta uses banned generic phrase '{banned}'. "
                f"CTA must offer specific value (e.g. 'Comment X and I will send Y') or ask viewers to tag a friend."
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
        if not shot.visual.strip() or not shot.on_screen_text.strip():
            raise QualityCheckError(f"visual_storyboard[{i}] has an empty visual or on_screen_text field.")


def _check_self_evaluation_has_evidence(output: ReelScriptOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise QualityCheckError(
                f"self_evaluation item '{line.item}' claims PASS but evidence is empty or too short."
            )
