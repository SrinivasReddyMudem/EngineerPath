"""Pure validator tests — no API calls, no GROQ_API_KEY needed."""

import pytest
from content_agents.core.base_agent import QualityCheckError
from content_agents.video.reel_script.schema import (
    ReelScriptOutput, Analogy, AnalogyMapping, TechnicalExplanation, RealProjectExample,
    ConceptUnderstanding, InterviewQA, StoryboardShot, QualityScore,
)
from content_agents.video.reel_script import validators


def _valid_output(**overrides) -> ReelScriptOutput:
    base = dict(
        topic="git",
        hook="Git reset looks simple, but it has three different behaviors every developer should understand.",
        hook_type="curiosity_hidden_power",
        problem="Developers often confuse reset's three modes because they don't know what moves the branch pointer vs the index vs the working directory.",
        analogy=Analogy(
            analogy="A bookmark in a book.",
            mapping=[
                AnalogyMapping(real_world="Bookmark location", technical="Git HEAD pointer"),
                AnalogyMapping(real_world="Moving the bookmark", technical="git reset"),
            ],
        ),
        technical_explanation=TechnicalExplanation(
            level_1_beginner="Reset moves where your branch is pointing to in history.",
            level_2_developer="Reset moves the branch pointer and, depending on mode, updates the index and working directory too.",
            level_3_professional="Soft/mixed/hard reset differ in how far the reset propagates through index and working tree, which matters for safely undoing local work.",
        ),
        real_project_example=RealProjectExample(
            scenario="A developer on a team creates a feature commit but notices during code review that the commit structure is unclear.",
            problem="Reviewers can't follow the change because unrelated edits are mixed into one commit.",
            solution="They use git reset --soft to uncommit and reorganize into cleaner commits before updating the pull request.",
            why_professionals_use_it="Clean, atomic commits make code review and future git blame far more useful for the whole team.",
        ),
        concept_understanding=ConceptUnderstanding(
            beginner_misunderstanding="Many assume reset deletes commits outright rather than just moving a pointer.",
            professional_insight="Experienced engineers pick the reset mode deliberately based on whether they want to keep changes staged, unstaged, or discarded.",
        ),
        interview=InterviewQA(
            question="What's the difference between git reset --soft, --mixed, and --hard?",
            strong_answer="Soft moves only the branch pointer; mixed also resets the index; hard resets index and working directory too.",
            common_weak_answer="Reset just undoes commits, without distinguishing what happens to staged or working directory changes.",
            follow_up_question="How would you recover if you ran reset --hard by mistake?",
        ),
        engagement_cta="Comment RESET and I'll send you the full Git reset cheat sheet.",
        visual_storyboard=[
            StoryboardShot(time_range="0-5s", visual="Git timeline A-B-C-D", animation="HEAD pointer moves backward", on_screen_text="Reset doesn't delete your code", purpose="Create mental model"),
            StoryboardShot(time_range="5-20s", visual="Split view of three reset modes", animation="Index and working dir highlight differently per mode", on_screen_text="Soft, mixed, hard", purpose="Show the distinction"),
            StoryboardShot(time_range="20-40s", visual="Code review screen", animation="Commits reorganizing", on_screen_text="Clean commits, easier review", purpose="Ground in real workflow"),
            StoryboardShot(time_range="40-60s", visual="Text overlay of CTA", animation="Text pulses once", on_screen_text="Comment RESET", purpose="Drive engagement"),
        ],
        quality_score=QualityScore(
            technical_accuracy=9, beginner_clarity=8, professional_relevance=9,
            hook_quality=8, analogy_quality=8, share_save_potential=8,
        ),
    )
    base.update(overrides)
    return ReelScriptOutput(**base)


def test_valid_output_passes():
    validators.validate(_valid_output())


def test_fear_based_hook_fails():
    out = _valid_output(hook="You are using Git wrong if you don't understand reset.")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_banned_cta_phrase_fails():
    out = _valid_output(engagement_cta="Follow for more Git tips!")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_preamble_hook_fails():
    out = _valid_output(hook="In this video we'll talk about Git reset and why it matters.")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_few_analogy_mappings_fails():
    out = _valid_output(analogy=Analogy(analogy="A bookmark in a book.", mapping=[
        AnalogyMapping(real_world="Bookmark location", technical="Git HEAD pointer"),
    ]))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_low_hook_quality_score_fails():
    out = _valid_output(quality_score=QualityScore(
        technical_accuracy=9, beginner_clarity=8, professional_relevance=9,
        hook_quality=6, analogy_quality=8, share_save_potential=8,
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_low_analogy_quality_score_fails():
    out = _valid_output(quality_score=QualityScore(
        technical_accuracy=9, beginner_clarity=8, professional_relevance=9,
        hook_quality=8, analogy_quality=5, share_save_potential=8,
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_duplicate_explanation_levels_fails():
    out = _valid_output(technical_explanation=TechnicalExplanation(
        level_1_beginner="Reset moves your branch pointer around in history here.",
        level_2_developer="Reset moves your branch pointer around in history here.",
        level_3_professional="Reset moves your branch pointer around in history here.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_few_storyboard_shots_fails():
    out = _valid_output(visual_storyboard=[
        StoryboardShot(time_range="0-60s", visual="One long shot", animation="Nothing changes", on_screen_text="Everything", purpose="Cover it all"),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_real_project_example_without_teamwork_context_fails():
    out = _valid_output(real_project_example=RealProjectExample(
        scenario="A developer forgot to commit a file before going home for the day.",
        problem="They realized it the next morning and had to redo some work.",
        solution="They committed the missing file the next day.",
        why_professionals_use_it="It saves time later on.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)
