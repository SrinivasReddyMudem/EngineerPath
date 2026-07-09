"""Pure validator tests — no API calls, no GROQ_API_KEY needed."""

import pytest
from content_agents.core.base_agent import QualityCheckError
from content_agents.core.shared_schema import SelfEvaluationLine
from content_agents.video.reel_script.schema import (
    ReelScriptOutput, Analogy, TechnicalExplanation, RealProjectExample, CommonMistakes, StoryboardShot,
)
from content_agents.video.reel_script import validators


def _valid_output(**overrides) -> ReelScriptOutput:
    base = dict(
        topic="git",
        hook="Most developers don't know why rebase changes commit hashes.",
        hook_type="curiosity_gap",
        problem="Rebased history confuses teams that don't know why hashes changed.",
        analogy=Analogy(
            statement="Rebase is like re-recording your podcast lines after a new intro.",
            why_it_fits="The content is the same but the new context changes the recording, just like a new parent changes the commit hash.",
        ),
        technical_explanation=TechnicalExplanation(
            level_1_beginner="Rebase moves your changes onto the latest code.",
            level_2_developer="Rebase replays your commits on top of a new base, creating new commit objects.",
            level_3_professional="Teams rebase feature branches before PRs to keep production history linear and bisectable.",
        ),
        real_project_example=RealProjectExample(
            scenario="Multiple developers share a service repo with frequent main updates.",
            problem="Merge commits interleave unrelated history, making review hard.",
            solution="Each developer rebases onto main before opening a PR.",
            why_professionals_use_it="Linear history makes git log, blame, and bisect far easier to use.",
        ),
        common_mistakes=CommonMistakes(
            beginner_mistake="Rebases a branch teammates already pulled, then force-pushes over their work.",
            professional_mistake="Rebases a long-lived shared branch instead of only personal feature branches.",
            interview_trap="Claims rebase and merge produce identical results, ignoring history shape and hash differences.",
        ),
        interview_question="Why does the commit hash change after a rebase even with an identical diff?",
        engagement_cta="Comment REBASE and I'll send you the full Git interview question bank.",
        visual_storyboard=[
            StoryboardShot(time_range="0-5s", visual="Split screen of two terminals", on_screen_text="Most devs don't know this"),
            StoryboardShot(time_range="5-20s", visual="Terminal running git log --graph", on_screen_text="Rebase = new commits"),
            StoryboardShot(time_range="20-40s", visual="Animated commit graph replaying", on_screen_text="Same diff, new hash"),
            StoryboardShot(time_range="40-60s", visual="Text overlay of CTA", on_screen_text="Comment REBASE"),
        ],
        self_evaluation=[
            SelfEvaluationLine(item="hook_pattern_match", result="PASS", evidence="Uses 'Most developers don't know'"),
        ],
    )
    base.update(overrides)
    return ReelScriptOutput(**base)


def test_valid_output_passes():
    validators.validate(_valid_output())


def test_hook_type_mismatch_fails():
    out = _valid_output(hook_type="interview_pressure")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_banned_cta_phrase_fails():
    out = _valid_output(engagement_cta="Follow for more Git tips!")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_preamble_hook_fails():
    out = _valid_output(hook="In this video we'll talk about Git rebase and why it matters.")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_weak_analogy_fails():
    out = _valid_output(analogy=Analogy(statement="A branch is like a tree branch.", why_it_fits="Trees have branches."))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_duplicate_explanation_levels_fails():
    out = _valid_output(technical_explanation=TechnicalExplanation(
        level_1_beginner="Rebase moves your changes onto the latest code base here.",
        level_2_developer="Rebase moves your changes onto the latest code base here.",
        level_3_professional="Rebase moves your changes onto the latest code base here.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_few_storyboard_shots_fails():
    out = _valid_output(visual_storyboard=[
        StoryboardShot(time_range="0-60s", visual="One long shot", on_screen_text="Everything"),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)
