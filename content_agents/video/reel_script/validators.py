"""
Domain validators for reel_script — one quality gate per schema section.
Content philosophy: curiosity/understanding/confidence/motivation, never
fear/shame/insult — see BANNED_HOOK_PHRASES and BANNED_GENERIC_AI_PHRASES.

Fact-checking layer added after manual review caught a real technical
error the structural checks alone couldn't see: the model claimed
`--mixed` resets the working directory (it doesn't — only HEAD + index).
Structural completeness is necessary but not sufficient; the checks
below cross-reference generated text against known-correct Git facts
and against each other (analogy vs technical_explanation coverage).
"""

import re
from content_agents.core.base_agent import QualityCheckError
from .schema import ReelScriptOutput

MIN_MAPPING_PAIRS = 2
MIN_LEVEL_LEN = 25
MIN_LIMITATIONS_LEN = 15
MIN_PROBLEM_FIELD_LEN = 15
MIN_EXAMPLE_FIELD_LEN = 20
MIN_INDUSTRY_CONTEXT_LEN = 8
MIN_MISTAKE_ENTRIES = 2
MIN_MISTAKE_FIELD_LEN = 15
MIN_INTERVIEW_FIELD_LEN = 15
MIN_STRONG_ANSWER_LEN = 60  # loose proxy for "covers definition + mechanism + example" — a terse but accurate answer can be short
MIN_STORYBOARD_SHOTS = 4
MIN_VISUAL_LEN = 15
MIN_ANIMATION_LEN = 10
MIN_VOICE_LEN = 10
MIN_ON_SCREEN_TEXT_LEN = 5
MIN_LEARNING_OBJECTIVE_LEN = 8
MIN_TECHNICAL_ACCURACY_SCORE = 9
MIN_GATED_SCORE = 8

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
    "99% of developers",
    "99% developers",
    "only experts know",
    "this will change your life",
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

# A CTA asking for a comment without offering a concrete reward is
# engagement bait, not value — e.g. "comment if you've struggled with this".
CTA_REWARD_INDICATORS = [
    "i'll send", "i will send", "i'll share", "i will share",
    "cheat sheet", "guide", "pdf", "checklist", "template",
]

TEAMWORK_CONTEXT_KEYWORDS = [
    "team", "review", "pull request", "pr ", "production", "colleague", "teammate", "code review",
]

# Too trivial for this audience (junior devs, interview prep, professionals) —
# real_project_example must feel like real engineering, not a toy scenario.
BANNED_TRIVIAL_SCENARIOS = [
    "forgot to include a file", "forgot a file", "forgot to add a file", "forgot to commit a file",
]

# Concept groups for analogy-completeness checking: an analogy that only
# covers one of several structural components the explanation discusses
# is an incomplete analogy (e.g. "bookmark" only covers HEAD, not index
# or working directory, when reset's three modes are being explained).
CONCEPT_GROUPS = {
    "head_pointer": ["head", "branch pointer", "commit pointer", "current position", "current commit", "current edit position"],
    "index_staging": ["index", "staging area", "staging", "stage", "staged", "preview area"],
    "working_directory": ["working directory", "working dir", "working tree", "files on disk", "local files", "exported"],
}

# Suggested as a concrete fallback when the model's own analogy repeatedly
# fails completeness — covers all 3 structural components explicitly.
FALLBACK_ANALOGY_HINT = (
    "If you can't find an analogy that covers all of "
    "{missing}, use this one verbatim: 'Editing a video timeline' — "
    "current edit position = HEAD, preview area selections = the index/staging "
    "area, the exported final video = the working directory."
)


def validate(output: ReelScriptOutput) -> None:
    _check_no_preamble(output)
    _check_hook_not_fear_or_generic(output)
    _check_problem(output)
    _check_analogy(output)
    _check_analogy_completeness(output)
    _check_technical_explanation(output)
    _check_reset_mode_accuracy(output)
    _check_real_project_example(output)
    _check_concept_mistakes(output)
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
                f"hooks that attack developers or create fear — rewrite using one of the approved "
                f"non-fear hook patterns instead."
            )
    for banned in BANNED_GENERIC_AI_PHRASES:
        if banned in hook_lower:
            raise QualityCheckError(f"hook uses generic AI phrase '{banned}'. Rewrite in a specific, human voice.")
    if len(output.hook.strip()) < 10:
        raise QualityCheckError("hook is too short to be a real opening line.")


def _check_problem(output: ReelScriptOutput) -> None:
    p = output.problem
    fields = {
        "real_world_problem": p.real_world_problem, "developer_pain": p.developer_pain,
        "why_it_matters": p.why_it_matters, "learning_goal": p.learning_goal,
    }
    for name, value in fields.items():
        if len(value.strip()) < MIN_PROBLEM_FIELD_LEN:
            raise QualityCheckError(f"problem.{name} is too short ({len(value)} chars) or missing.")


def _check_analogy(output: ReelScriptOutput) -> None:
    if len(output.analogy.mapping) < MIN_MAPPING_PAIRS:
        raise QualityCheckError(
            f"analogy.mapping has {len(output.analogy.mapping)} pairs, needs at least {MIN_MAPPING_PAIRS} "
            f"explicit real_world -> technical mappings."
        )
    for i, pair in enumerate(output.analogy.mapping):
        if not pair.real_world.strip() or not pair.technical.strip():
            raise QualityCheckError(f"analogy.mapping[{i}] has an empty real_world or technical field.")
    if len(output.analogy.limitations.strip()) < MIN_LIMITATIONS_LEN:
        raise QualityCheckError(
            "analogy.limitations is too short or missing — every analogy must state where it breaks "
            "down, so it can't quietly create a misconception."
        )


def _detect_concepts(text_lower: str) -> set[str]:
    found = set()
    for group, keywords in CONCEPT_GROUPS.items():
        if any(kw in text_lower for kw in keywords):
            found.add(group)
    return found


def _check_analogy_completeness(output: ReelScriptOutput) -> None:
    te = output.technical_explanation
    te_text = f"{te.level_1_beginner} {te.level_2_developer} {te.level_3_professional} {te.internal_working}".lower()
    te_concepts = _detect_concepts(te_text)
    if len(te_concepts) < 2:
        return  # single-component concept (e.g. a simple pointer move) — nothing to cross-check
    mapping_text = " ".join(f"{p.real_world} {p.technical}" for p in output.analogy.mapping).lower()
    mapping_concepts = _detect_concepts(mapping_text)
    missing = te_concepts - mapping_concepts
    if missing:
        raise QualityCheckError(
            f"analogy only maps {sorted(mapping_concepts)} but technical_explanation discusses "
            f"{sorted(te_concepts)} — missing a mapping for {sorted(missing)}. An analogy that only "
            f"covers some structural components is incomplete when the explanation covers several. "
            + FALLBACK_ANALOGY_HINT.format(missing=sorted(missing))
        )


def _check_technical_explanation(output: ReelScriptOutput) -> None:
    te = output.technical_explanation
    levels = [te.level_1_beginner, te.level_2_developer, te.level_3_professional, te.internal_working]
    names = ["level_1_beginner", "level_2_developer", "level_3_professional", "internal_working"]
    for name, level in zip(names, levels):
        if len(level.strip()) < MIN_LEVEL_LEN:
            raise QualityCheckError(f"technical_explanation.{name} is too short ({len(level)} chars).")
    if len({lvl.strip() for lvl in levels}) < len(levels):
        raise QualityCheckError(
            "technical_explanation fields must be genuinely distinct (WHAT/HOW/WHY-WHEN/internal "
            "mechanism), not near-duplicates."
        )


def _split_sentences(text: str) -> list[str]:
    return re.split(r"[.!?;\n]", text)


# If a sentence explicitly negates the effect ("leaves X untouched"), it's
# stating the CORRECT fact, not making the wrong claim — don't flag it.
NEGATION_INDICATORS = [
    "untouched", "unchanged", "unaffected", "not touch", "doesn't touch",
    "does not touch", "left alone", " alone", "intact", "not affected",
    "remains the same", "stays the same", "no changes", "stay in the working",
    "stays in the working", "remain in the working", "remains in the working",
    "not reset", "isn't reset", "is not reset",
]


def _sentence_asserts_negation(sentence_lower: str) -> bool:
    return any(neg in sentence_lower for neg in NEGATION_INDICATORS)


def _check_reset_mode_accuracy(output: ReelScriptOutput) -> None:
    """
    Fact-check specifically for git reset mode claims — the exact class of
    error found in manual review: `--mixed` does NOT touch the working
    directory (only HEAD + index); `--soft` touches neither index nor
    working directory. Only fires on sentences that explicitly discuss
    reset, to avoid false positives on unrelated content.
    """
    te = output.technical_explanation
    fields = {
        "technical_explanation.level_1_beginner": te.level_1_beginner,
        "technical_explanation.level_2_developer": te.level_2_developer,
        "technical_explanation.level_3_professional": te.level_3_professional,
        "technical_explanation.internal_working": te.internal_working,
        "interview.strong_answer": output.interview.strong_answer,
        "real_project_example.solution": output.real_project_example.solution,
    }
    for i, entry in enumerate(output.concept_mistakes):
        fields[f"concept_mistakes[{i}].correct_understanding"] = entry.correct_understanding

    for field_name, text in fields.items():
        for sentence in _split_sentences(text):
            s = sentence.lower()
            if "reset" not in s or _sentence_asserts_negation(s):
                continue
            if "mixed" in s and ("working directory" in s or "working dir" in s):
                raise QualityCheckError(
                    f"{field_name} incorrectly claims --mixed reset touches the working directory. "
                    f"--mixed only moves HEAD and resets the index; the working directory is left "
                    f"unchanged (changes become unstaged, not discarded). Fix this specific claim."
                )
            if "soft" in s and ("index" in s or "staging" in s or "working directory" in s or "working dir" in s):
                raise QualityCheckError(
                    f"{field_name} incorrectly claims --soft reset touches the index/staging area or "
                    f"working directory. --soft only moves the branch pointer/HEAD — index and working "
                    f"directory are both left untouched. Fix this specific claim."
                )


def _check_real_project_example(output: ReelScriptOutput) -> None:
    ex = output.real_project_example
    if len(ex.industry_context.strip()) < MIN_INDUSTRY_CONTEXT_LEN:
        raise QualityCheckError(f"real_project_example.industry_context is too short ({len(ex.industry_context)} chars) or missing.")
    fields = {
        "scenario": ex.scenario, "problem": ex.problem,
        "solution": ex.solution, "professional_reasoning": ex.professional_reasoning,
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
    for banned in BANNED_TRIVIAL_SCENARIOS:
        if banned in ex.scenario.lower():
            raise QualityCheckError(
                f"real_project_example.scenario uses a too-trivial scenario ('{banned}'). This audience "
                f"is junior devs and professionals — ground it in something like messy commits before a "
                f"PR, a review comment, or a shared-branch conflict, per references/workflows.md."
            )


def _check_concept_mistakes(output: ReelScriptOutput) -> None:
    entries = output.concept_mistakes
    if len(entries) < MIN_MISTAKE_ENTRIES:
        raise QualityCheckError(f"concept_mistakes has {len(entries)} entries, needs at least {MIN_MISTAKE_ENTRIES}.")
    if len({e.level for e in entries}) < 2:
        raise QualityCheckError("concept_mistakes entries must cover at least 2 distinct levels, not the same level repeated.")
    for i, entry in enumerate(entries):
        fields = {
            "wrong_belief": entry.wrong_belief, "correct_understanding": entry.correct_understanding,
            "professional_tip": entry.professional_tip,
        }
        for name, value in fields.items():
            if len(value.strip()) < MIN_MISTAKE_FIELD_LEN:
                raise QualityCheckError(f"concept_mistakes[{i}].{name} is too short ({len(value)} chars) or missing.")


def _check_interview(output: ReelScriptOutput) -> None:
    qa = output.interview
    fields = {
        "question": qa.question, "why_interviewer_asks": qa.why_interviewer_asks,
        "weak_answer": qa.weak_answer,
    }
    for name, value in fields.items():
        if len(value.strip()) < MIN_INTERVIEW_FIELD_LEN:
            raise QualityCheckError(f"interview.{name} is too short ({len(value)} chars) or missing.")
    if len(qa.strong_answer.strip()) < MIN_STRONG_ANSWER_LEN:
        raise QualityCheckError(
            f"interview.strong_answer is only {len(qa.strong_answer)} chars — too short to plausibly "
            f"cover all 3 required parts: (1) a definition, (2) the internal mechanism, and (3) a "
            f"practical example. It's most likely missing the example — add one specific scenario "
            f"where this comes up, don't just restate the definition more briefly."
        )
    if qa.strong_answer.strip().lower() == qa.weak_answer.strip().lower():
        raise QualityCheckError("interview.strong_answer and weak_answer must not be identical.")
    if len(qa.follow_up_questions) < 1:
        raise QualityCheckError("interview.follow_up_questions must have at least 1 entry.")
    for i, q in enumerate(qa.follow_up_questions):
        if len(q.strip()) < MIN_INTERVIEW_FIELD_LEN:
            raise QualityCheckError(f"interview.follow_up_questions[{i}] is too short or missing.")


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

    has_comment_pattern = "comment" in cta_lower
    has_tag_pattern = "tag a friend" in cta_lower or "tag someone" in cta_lower
    has_save_pattern = "save this" in cta_lower
    has_series_pattern = "follow" in cta_lower and "series" in cta_lower
    has_reward = any(r in cta_lower for r in CTA_REWARD_INDICATORS)

    if not (has_comment_pattern or has_tag_pattern or has_save_pattern or has_series_pattern):
        raise QualityCheckError(
            "engagement_cta must use one of: comment-for-reward, tag a friend, save-this-for-later, "
            "or follow-a-named-series — found none of these patterns."
        )
    if has_comment_pattern and not (has_tag_pattern or has_save_pattern) and not has_reward:
        raise QualityCheckError(
            "engagement_cta asks for a comment but offers no concrete reward (e.g. 'Comment X and I'll "
            "send the cheat sheet'). A bare 'comment if you've struggled with this' is engagement bait, "
            "not real value — this is weaker than your own CTA rules require."
        )


def _check_storyboard(output: ReelScriptOutput) -> None:
    if len(output.visual_storyboard) < MIN_STORYBOARD_SHOTS:
        raise QualityCheckError(
            f"visual_storyboard has {len(output.visual_storyboard)} shots, needs at least "
            f"{MIN_STORYBOARD_SHOTS} to plausibly cover 60 seconds."
        )
    for i, shot in enumerate(output.visual_storyboard):
        if len(shot.visual.strip()) < MIN_VISUAL_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].visual is too vague/short — describe the concrete shot, not a generic label like 'show logo'.")
        if len(shot.animation.strip()) < MIN_ANIMATION_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].animation is too vague/short — describe what actually moves or changes.")
        if len(shot.voice.strip()) < MIN_VOICE_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].voice is empty or too short.")
        if len(shot.on_screen_text.strip()) < MIN_ON_SCREEN_TEXT_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].on_screen_text is empty or too short.")
        if len(shot.learning_objective.strip()) < MIN_LEARNING_OBJECTIVE_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].learning_objective is empty or too short.")


def _check_quality_score(output: ReelScriptOutput) -> None:
    qs = output.quality_score
    if qs.technical_accuracy < MIN_TECHNICAL_ACCURACY_SCORE:
        raise QualityCheckError(
            f"quality_score.technical_accuracy is {qs.technical_accuracy}, below the required "
            f"{MIN_TECHNICAL_ACCURACY_SCORE}. Fix the inaccurate section, don't just report a low score."
        )
    if qs.hook_strength < MIN_GATED_SCORE:
        raise QualityCheckError(
            f"quality_score.hook_strength is {qs.hook_strength}, below the required {MIN_GATED_SCORE}. "
            f"Create another hook using a stronger pattern."
        )
    if qs.analogy_quality < MIN_GATED_SCORE:
        raise QualityCheckError(
            f"quality_score.analogy_quality is {qs.analogy_quality}, below the required {MIN_GATED_SCORE}. "
            f"Regenerate the analogy with a more accurate, better-mapped comparison."
        )
