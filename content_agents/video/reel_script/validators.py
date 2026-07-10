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
from .schema import ReelScriptOutput, COMPARISON_DIMENSIONS

MIN_MAPPING_PAIRS = 2
MIN_LEVEL_LEN = 25
MIN_LIMITATIONS_LEN = 15
MIN_PROBLEM_FIELD_LEN = 15
MIN_EXAMPLE_FIELD_LEN = 20
MIN_INDUSTRY_CONTEXT_LEN = 8
MIN_MISTAKE_ENTRIES = 2
MAX_MISTAKE_ENTRIES = 3  # content boundary: one reel covers one transformation, not an exhaustive catalog
MIN_MISTAKE_FIELD_LEN = 15
MIN_INTERVIEW_FIELD_LEN = 15
MIN_STRONG_ANSWER_LEN = 60  # loose proxy for "covers definition + mechanism + example" — a terse but accurate answer can be short
MIN_STORYBOARD_SHOTS = 6  # voice_script is now compiled FROM these shots — enough shots to carry hook/problem/analogy/technical/example/anchor+cta as separate one-idea lines
MIN_CAMERA_LEN = 8
MIN_VISUAL_WORDS = 12  # WHO/WHERE/WHAT ACTION needs real sentence structure, not a 2-word label
MIN_ANIMATION_WORDS = 6
MIN_VOICE_LEN = 10
MIN_ON_SCREEN_TEXT_LEN = 5
MIN_LEARNING_OBJECTIVE_LEN = 8
MIN_TECHNICAL_ACCURACY_SCORE = 9
MIN_GATED_SCORE = 8
MIN_MAIN_INSIGHT_LEN = 15
MIN_CONTENT_BOUNDARY_LEN = 15
MIN_VISUAL_STYLE_LEN = 8
MIN_MEMORY_ANCHOR_LEN = 10

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
    "hotfix", "deploy", "release", "collaborat", "merge request", "shared branch", "codebase",
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

# Safety-critical: history-rewriting commands (reset --hard, filter-repo, rebase)
# do NOT permanently erase data — it can persist in reflog / the object database
# until garbage collected, and a pushed secret must be rotated regardless of any
# local history rewrite. Recommending these as a fix for exposed sensitive data
# without that caveat is actively dangerous advice, not just imprecise.
SENSITIVE_DATA_KEYWORDS = ["sensitive data", "secret", "password", "credential", "api key", "private key", "token"]
DESTRUCTIVE_COMMAND_KEYWORDS = ["reset --hard", "reset hard", "filter-branch", "filter-repo", "rebase"]
DESTRUCTIVE_CLAIM_VERBS = [
    "remove", "removes", "removed", "removing",
    "delete", "deletes", "deleted", "deleting",
    "erase", "erases", "erased", "erasing",
    "gets rid of", "get rid of", "eliminate", "eliminates", "wipe", "wipes",
]
SAFETY_CAVEAT_INDICATORS = ["reflog", "object database", "garbage collect", "rotate", "invalidate", "revoke", "already pushed", "already shared"]


def validate(output: ReelScriptOutput) -> None:
    """
    Run every check and collect ALL failures instead of stopping at the
    first one. This matters for two reasons: (1) the retry-feedback loop
    can tell the model about every current problem in one round instead
    of one-at-a-time whack-a-mole, converging faster; (2) if the retry
    budget runs out and the best-effort fallback returns content anyway,
    the logged issue list reflects everything actually wrong, not just
    whichever check happened to run first.
    """
    checks = [
        _check_content_plan, _check_no_preamble, _check_hook_not_fear_or_generic, _check_hook_not_definitional,
        _check_problem, _check_analogy, _check_analogy_completeness, _check_technical_explanation,
        _check_reset_mode_accuracy, _check_no_commit_deletion_claim, _check_technical_safety, _check_hard_reset_warning,
        _check_real_project_example, _check_concept_mistakes, _check_interview, _check_cta, _check_memory_anchor,
        _check_storyboard, _check_voice_script_pacing, _check_voice_visual_sync,
        _check_first_shot_is_the_hook, _check_anchor_and_cta_are_spoken,
        _check_analogy_appears_in_voice, _check_real_example_context_appears_in_voice,
        _check_quality_score, _check_comparison,
    ]
    issues: list[str] = []
    for check in checks:
        try:
            check(output)
        except QualityCheckError as e:
            issues.append(str(e))
    if issues:
        numbered = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(issues))
        raise QualityCheckError(f"{len(issues)} issue(s) found:\n{numbered}")


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


DEFINITIONAL_OPENING_PATTERNS = [" is a ", " is the ", " is used to ", " helps you ", " allows you to ", " lets you ", " means that "]


def _check_hook_not_definitional(output: ReelScriptOutput) -> None:
    """
    A hook that opens by defining the topic ("Git Reset helps you fix
    mistakes") explains instead of attracting — it reads like the first
    line of documentation, not something that makes a viewer stop
    scrolling. Every approved hook_type presents a situation, question,
    or consequence instead.
    """
    hook_lower = output.hook.lower().strip()
    topic_lower = output.topic.lower().strip()
    opening = hook_lower[:60]
    if topic_lower and topic_lower in opening:
        for pattern in DEFINITIONAL_OPENING_PATTERNS:
            if pattern in opening:
                raise QualityCheckError(
                    f"hook opens by defining '{output.topic}' (pattern '{pattern.strip()}') instead of "
                    f"presenting a situation, question, or consequence. A definition-first hook explains; "
                    f"it doesn't attract. Rewrite using the chosen hook_type's actual pattern."
                )


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def _check_first_shot_is_the_hook(output: ReelScriptOutput) -> None:
    """
    voice_script is compiled ONLY from visual_storyboard[i].voice — the
    `hook` field itself never appears in the final output unless shot 0's
    voice actually IS it. Without this check, `hook` can pass every hook
    validator while shot 0 says something completely different, and the
    real hook silently never gets spoken. hook/memory_anchor/engagement_cta
    are the three fields meant to be spoken VERBATIM (not paraphrased
    planning text like problem/analogy/technical_explanation), so exact
    (whitespace/punctuation-normalized) matching is the right bar here.
    """
    if not output.visual_storyboard:
        return
    first_voice = _normalize(output.visual_storyboard[0].voice)
    hook = _normalize(output.hook)
    if first_voice != hook:
        raise QualityCheckError(
            f"visual_storyboard[0].voice does not match `hook` word-for-word. hook='{output.hook}' but "
            f"shot 0's voice='{output.visual_storyboard[0].voice}'. Set shot 0's voice to the hook exactly "
            f"— it's the line that actually gets spoken, and it must be the hook, not a paraphrase or the "
            f"analogy bridge."
        )


def _check_anchor_and_cta_are_spoken(output: ReelScriptOutput) -> None:
    """
    Same gap as the hook, at the other end: memory_anchor and
    engagement_cta must appear verbatim somewhere in the actual spoken
    voice lines, or they're validated-but-never-spoken dead fields.
    """
    combined_voice = _normalize(" ".join(shot.voice for shot in output.visual_storyboard))
    anchor = _normalize(output.memory_anchor)
    cta = _normalize(output.engagement_cta)
    if anchor and anchor not in combined_voice:
        raise QualityCheckError(
            f"memory_anchor ('{output.memory_anchor}') does not appear word-for-word in any shot's voice "
            f"line. Put it verbatim as its own shot, right before the CTA."
        )
    if cta and cta not in combined_voice:
        raise QualityCheckError(
            f"engagement_cta ('{output.engagement_cta}') does not appear word-for-word in any shot's voice "
            f"line. Put it verbatim as the final shot's voice."
        )


STOPWORDS = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or", "is", "are", "your", "you", "like", "think"}


def _significant_words(text: str) -> list[str]:
    return [w.strip(".,!?:;'\"") for w in text.lower().split() if w.strip(".,!?:;'\"") not in STOPWORDS and len(w) > 3]


def _check_analogy_appears_in_voice(output: ReelScriptOutput) -> None:
    """
    A validated, complete analogy that never gets NARRATED is dead weight
    — the model can pass _check_analogy_completeness while the storyboard
    skips straight to bare technical facts. Require at least one of the
    analogy's own significant words to actually appear spoken.
    """
    combined_voice = " ".join(shot.voice for shot in output.visual_storyboard).lower()
    words = _significant_words(output.analogy.analogy)
    if words and not any(w in combined_voice for w in words):
        raise QualityCheckError(
            f"The analogy ('{output.analogy.analogy}') never appears in any shot's voice line — none of "
            f"its key words {words} are spoken anywhere. A validated-but-unspoken analogy doesn't teach "
            f"anyone; narrate it in at least one shot, don't skip straight to technical facts."
        )


def _check_real_example_context_appears_in_voice(output: ReelScriptOutput) -> None:
    """Same gap for real_project_example: teamwork/production context must actually be narrated, not just validated as a hidden field."""
    combined_voice = " ".join(shot.voice for shot in output.visual_storyboard).lower()
    if not any(kw in combined_voice for kw in TEAMWORK_CONTEXT_KEYWORDS):
        raise QualityCheckError(
            "real_project_example's teamwork/code-review/production context never appears in any shot's "
            "voice line — the reel must narrate the real-world scenario, not just validate it silently."
        )


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
    """
    Split on true sentence boundaries only (.!?), not semicolons.
    Regression: "But --hard changes all; use with caution, discarding
    changes." is one coherent sentence a writer joined with a semicolon —
    splitting on ';' separated the --hard mention from its own caution
    word, producing a false-positive rejection of a perfectly safe claim.
    """
    return re.split(r"[.!?\n]", text)


# If a sentence explicitly negates the effect ("leaves X untouched"), it's
# stating the CORRECT fact, not making the wrong claim — don't flag it.
NEGATION_INDICATORS = [
    "untouched", "unchanged", "unaffected", "not touch", "doesn't touch",
    "does not touch", "left alone", " alone", "intact", "not affected",
    "remains the same", "stays the same", "no changes", "stay in the working",
    "stays in the working", "remain in the working", "remains in the working",
    "not reset", "isn't reset", "is not reset",
    "not delete", "doesn't delete", "does not delete",
    "not remove", "doesn't remove", "does not remove",
    "not erase", "doesn't erase", "does not erase",
]


def _sentence_asserts_negation(sentence_lower: str) -> bool:
    return any(neg in sentence_lower for neg in NEGATION_INDICATORS)


def _fact_bearing_fields(output: ReelScriptOutput) -> dict[str, str]:
    """
    Every field that makes a factual claim a viewer will actually hear or
    read — including storyboard voice lines, since those ARE the voice
    script now (see StoryboardShot docstring). Excludes weak_answer
    (deliberately wrong, by design) and questions (no factual claim).
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
    for i, shot in enumerate(output.visual_storyboard):
        fields[f"visual_storyboard[{i}].voice"] = shot.voice
    return fields


def _check_reset_mode_accuracy(output: ReelScriptOutput) -> None:
    """
    Fact-check specifically for git reset mode claims — the exact class of
    error found in manual review: `--mixed` does NOT touch the working
    directory (only HEAD + index); `--soft` touches neither index nor
    working directory. Only fires on sentences that explicitly discuss
    reset, to avoid false positives on unrelated content.
    """
    for field_name, text in _fact_bearing_fields(output).items():
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


def _check_no_commit_deletion_claim(output: ReelScriptOutput) -> None:
    """
    Generalizes the safety check beyond the secrets-specific case: ANY
    claim that a commit "disappears"/is "deleted"/"gone" after reset is
    imprecise — the commit object persists in the object database and is
    reachable via reflog until garbage collected. Only the branch pointer
    stops referencing it. Reviewers flagged this as dangerous teaching for
    beginners even outside the sensitive-data context.
    """
    for field_name, text in _fact_bearing_fields(output).items():
        for sentence in _split_sentences(text):
            s = sentence.lower()
            if "commit" not in s or _sentence_asserts_negation(s):
                continue
            claims_deletion = any(verb in s for verb in DESTRUCTIVE_CLAIM_VERBS) or "disappear" in s or "gone" in s
            if claims_deletion and ("reset" in s or "rebase" in s):
                raise QualityCheckError(
                    f"{field_name} claims a commit is deleted/disappears/gone after reset or rebase. "
                    f"Say the branch pointer stops referencing it instead — the commit object persists "
                    f"in the object database and is recoverable via reflog until garbage collected."
                )


CAUTION_WORDS = ["careful", "caution", "warning", "discard", "irreversible", "risky", "danger"]


def _check_hard_reset_warning(output: ReelScriptOutput) -> None:
    """
    Beginners copy commands verbatim from a 60-second reel — any mention
    of --hard (the one mode that actually discards working directory
    changes) needs a caution word in the same sentence, not a bare
    demonstration with no risk signal.
    """
    for field_name, text in _fact_bearing_fields(output).items():
        for sentence in _split_sentences(text):
            s = sentence.lower()
            if "--hard" not in s and "hard reset" not in s:
                continue
            if not any(word in s for word in CAUTION_WORDS):
                raise QualityCheckError(
                    f"{field_name} mentions --hard with no caution word (careful/warning/discard/"
                    f"irreversible) in the same sentence — beginners may copy it verbatim without "
                    f"realizing it discards uncommitted working directory changes."
                )


def _check_technical_safety(output: ReelScriptOutput) -> None:
    """
    Reject a specific dangerous pattern: claiming a history-rewriting
    command (reset --hard, filter-branch/-repo, rebase) "removes" or
    "deletes" sensitive data (secrets, passwords, credentials, tokens)
    without the safety caveat — it doesn't permanently erase anything
    (reflog/object database can retain it until garbage collected), and
    an already-pushed secret must be rotated regardless of any local
    history rewrite. Recommending otherwise is dangerous advice, not
    just an imprecise simplification.
    """
    for field_name, text in _fact_bearing_fields(output).items():
        text_lower = text.lower()
        mentions_sensitive_data = any(kw in text_lower for kw in SENSITIVE_DATA_KEYWORDS)
        mentions_destructive_command = any(kw in text_lower for kw in DESTRUCTIVE_COMMAND_KEYWORDS)
        if not (mentions_sensitive_data and mentions_destructive_command):
            continue
        makes_destructive_claim = any(verb in text_lower for verb in DESTRUCTIVE_CLAIM_VERBS)
        has_caveat = any(ind in text_lower for ind in SAFETY_CAVEAT_INDICATORS)
        if makes_destructive_claim and not has_caveat:
            raise QualityCheckError(
                f"{field_name} claims a history-rewriting command removes/deletes sensitive data without "
                f"the safety caveat. This command does not permanently erase anything — it can persist in "
                f"reflog or the object database until garbage collected, and any exposed secret must be "
                f"rotated/invalidated regardless. Add that caveat or don't frame it as data removal."
            )


def _check_content_plan(output: ReelScriptOutput) -> None:
    cp = output.content_plan
    if len(cp.main_insight.strip()) < MIN_MAIN_INSIGHT_LEN:
        raise QualityCheckError("content_plan.main_insight is too short or missing.")
    if len(cp.content_boundary.strip()) < MIN_CONTENT_BOUNDARY_LEN:
        raise QualityCheckError("content_plan.content_boundary is too short or missing.")
    if len(output.recommended_visual_style.strip()) < MIN_VISUAL_STYLE_LEN:
        raise QualityCheckError("recommended_visual_style is too short or missing.")


def _check_memory_anchor(output: ReelScriptOutput) -> None:
    if len(output.memory_anchor.strip()) < MIN_MEMORY_ANCHOR_LEN:
        raise QualityCheckError("memory_anchor is too short or missing.")


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
    if len(entries) > MAX_MISTAKE_ENTRIES:
        raise QualityCheckError(
            f"concept_mistakes has {len(entries)} entries, more than {MAX_MISTAKE_ENTRIES}. One reel covers "
            f"one transformation — trim to the most important mistakes, not an exhaustive catalog."
        )
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
    # "follow" alone is fine as long as it isn't one of BANNED_CTA_PHRASES
    # above (e.g. bare "follow for more") — "Follow EngineerPath" names a
    # specific channel, which is exactly what makes it not generic.
    has_follow_pattern = "follow" in cta_lower
    has_reward = any(r in cta_lower for r in CTA_REWARD_INDICATORS)

    if not (has_comment_pattern or has_tag_pattern or has_save_pattern or has_follow_pattern):
        raise QualityCheckError(
            "engagement_cta must use one of: comment-for-reward, tag a friend, save-this-for-later, "
            "or follow (naming a specific channel/series) — found none of these patterns."
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
        visual_words = len(shot.visual.strip().split())
        if visual_words < MIN_VISUAL_WORDS:
            raise QualityCheckError(
                f"visual_storyboard[{i}].visual is only {visual_words} words — needs WHO is on screen, "
                f"WHERE, and WHAT ACTION is happening (at least {MIN_VISUAL_WORDS} words), not a short label "
                f"like 'Git Reset logo'."
            )
        animation_words = len(shot.animation.strip().split())
        if animation_words < MIN_ANIMATION_WORDS:
            raise QualityCheckError(
                f"visual_storyboard[{i}].animation is only {animation_words} words — describe the specific "
                f"motion (at least {MIN_ANIMATION_WORDS} words), not just naming what changes."
            )
        if len(shot.voice.strip()) < MIN_VOICE_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].voice is empty or too short.")
        if len(shot.camera.strip()) < MIN_CAMERA_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].camera is empty or too short.")
        if len(shot.on_screen_text.strip()) < MIN_ON_SCREEN_TEXT_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].on_screen_text is empty or too short.")
        if len(shot.learning_objective.strip()) < MIN_LEARNING_OBJECTIVE_LEN:
            raise QualityCheckError(f"visual_storyboard[{i}].learning_objective is empty or too short.")


MIN_VOICE_SCRIPT_WORDS = 110  # a 60s reel spoken at natural pace needs enough words to actually fill the time
MAX_VOICE_SCRIPT_WORDS = 190  # too many words for 60s reads rushed, not natural


def _check_voice_script_pacing(output: ReelScriptOutput) -> None:
    """voice_script is the join of every shot's voice line (see StoryboardShot docstring) — check it as a whole, not per shot."""
    total_words = sum(len(shot.voice.split()) for shot in output.visual_storyboard)
    if total_words < MIN_VOICE_SCRIPT_WORDS:
        raise QualityCheckError(
            f"voice_script (all shots' voice lines combined) is only {total_words} words — too short to "
            f"naturally fill 60 seconds spoken aloud (need {MIN_VOICE_SCRIPT_WORDS}-{MAX_VOICE_SCRIPT_WORDS})."
        )
    if total_words > MAX_VOICE_SCRIPT_WORDS:
        raise QualityCheckError(
            f"voice_script (all shots' voice lines combined) is {total_words} words — too dense to speak "
            f"naturally in 60 seconds (need {MIN_VOICE_SCRIPT_WORDS}-{MAX_VOICE_SCRIPT_WORDS}). Trim, don't rush."
        )


def _check_voice_visual_sync(output: ReelScriptOutput) -> None:
    """
    The sync gap reviewers flagged: a shot's voice can discuss one
    concept (e.g. HEAD moving) while its visual shows something
    unrelated. Reuses the same concept-detection used for analogy
    completeness — if the voice names a structural concept, the visual
    side of the SAME shot must reference it too.
    """
    for i, shot in enumerate(output.visual_storyboard):
        voice_concepts = _detect_concepts(shot.voice.lower())
        if not voice_concepts:
            continue
        visual_side = f"{shot.visual} {shot.animation} {shot.on_screen_text}".lower()
        visual_concepts = _detect_concepts(visual_side)
        missing = voice_concepts - visual_concepts
        if missing:
            raise QualityCheckError(
                f"visual_storyboard[{i}]: voice mentions {sorted(voice_concepts)} but the visual/animation/"
                f"on_screen_text don't reflect {sorted(missing)} — the screen must show what's being said, "
                f"not something unrelated."
            )


def _check_comparison(output: ReelScriptOutput) -> None:
    c = output.comparison
    if c is None:
        return
    if not c.concept_a.strip() or not c.concept_b.strip():
        raise QualityCheckError("comparison.concept_a / concept_b must both be named.")
    if len(c.why_confused.strip()) < 15:
        raise QualityCheckError("comparison.why_confused is too short or missing.")
    if len(c.concept_a_definition.strip()) < 15 or len(c.concept_b_definition.strip()) < 15:
        raise QualityCheckError("comparison.concept_a_definition / concept_b_definition are too short or missing.")
    covered = {row.dimension for row in c.comparison_rows}
    missing = set(COMPARISON_DIMENSIONS) - covered
    if missing:
        raise QualityCheckError(f"comparison.comparison_rows is missing required dimension(s): {sorted(missing)}.")
    for row in c.comparison_rows:
        if not row.concept_a_value.strip() or not row.concept_b_value.strip():
            raise QualityCheckError(f"comparison.comparison_rows['{row.dimension}'] has an empty value for one side.")
    if len(c.decision_rule.strip()) < 15:
        raise QualityCheckError("comparison.decision_rule is too short or missing.")


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
