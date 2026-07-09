"""Pure validator tests — no API calls, no GROQ_API_KEY needed."""

import pytest
from content_agents.core.base_agent import QualityCheckError
from content_agents.video.reel_script.schema import (
    ReelScriptOutput, ProblemSetup, Analogy, AnalogyMapping, TechnicalExplanation,
    RealProjectExample, MistakeEntry, InterviewQA, StoryboardShot, QualityScore,
    ComparisonStructure, ComparisonRow, ContentPlan,
)
from content_agents.video.reel_script import validators


def _valid_output(**overrides) -> ReelScriptOutput:
    base = dict(
        topic="git",
        content_plan=ContentPlan(
            main_insight="Reset moves your position in history; the mode decides what else gets touched.",
            content_boundary="Skip reflog recovery and object database internals — save those for another reel.",
        ),
        recommended_visual_style="Stick figure + animated terminal diagrams",
        hook="Git reset looks simple, but it changes your entire history in three different ways.",
        hook_type="curiosity_gap",
        problem=ProblemSetup(
            real_world_problem="A developer commits changes but the commit is messy or incomplete.",
            developer_pain="They don't know whether to create another commit or use a cleaner Git approach.",
            why_it_matters="Understanding reset's modes prevents accidentally losing or mishandling work.",
            learning_goal="Confidently choose the right reset mode for the situation.",
        ),
        analogy=Analogy(
            analogy="Editing a video timeline.",
            mapping=[
                AnalogyMapping(real_world="Current edit position", technical="Git HEAD pointer"),
                AnalogyMapping(real_world="Preview area selections", technical="the index / staging area"),
                AnalogyMapping(real_world="The exported final video", technical="the working directory"),
            ],
            limitations="Unlike video editing, Git reset can't be undone with a simple 'undo' button once objects are garbage collected.",
        ),
        technical_explanation=TechnicalExplanation(
            level_1_beginner="Reset moves where your branch is pointing to in history.",
            level_2_developer="Reset moves the branch pointer and, depending on mode, may also reset the index; --mixed leaves the working directory untouched.",
            level_3_professional="Teams choose --soft to reorganize commits, --mixed to unstage, and --hard only when discarding local work entirely.",
            internal_working="Soft moves only HEAD; mixed also resets the index while leaving the working directory alone; hard resets HEAD, index, and working directory together.",
        ),
        real_project_example=RealProjectExample(
            industry_context="software team",
            scenario="A developer on a team creates a feature commit but notices during code review that the commit structure is unclear.",
            problem="Reviewers can't follow the change because unrelated edits are mixed into one commit.",
            solution="They use git reset --soft to uncommit and reorganize into cleaner commits before updating the pull request.",
            professional_reasoning="Clean, atomic commits make code review and future git blame far more useful for the whole team.",
        ),
        concept_mistakes=[
            MistakeEntry(
                level="beginner",
                wrong_belief="Many assume reset deletes commits outright rather than just moving a pointer.",
                correct_understanding="Reset moves the branch pointer; the effect on index/working dir depends on mode.",
                professional_tip="Check `git status` after any reset to confirm what actually changed.",
            ),
            MistakeEntry(
                level="professional",
                wrong_belief="Some engineers reset a shared branch without warning teammates.",
                correct_understanding="Resetting a shared branch diverges everyone else's history from yours.",
                professional_tip="Prefer git revert on branches others have already pulled from.",
            ),
        ],
        interview=InterviewQA(
            question="What's the difference between git reset --soft, --mixed, and --hard?",
            why_interviewer_asks="It reveals whether the candidate understands Git's three-tree model (HEAD, index, working dir).",
            strong_answer="Soft moves only the branch pointer, keeping the index and working directory unchanged. Mixed additionally resets the index, so changes become unstaged but stay in the working directory. Hard resets HEAD, index, and working directory together, discarding local changes. For example, a developer might use --soft to reorganize commits before a PR.",
            weak_answer="Reset just undoes commits, without distinguishing what happens to staged or working directory changes.",
            follow_up_questions=["How would you recover if you ran reset --hard by mistake?"],
        ),
        memory_anchor="Reset moves your position. Revert makes a correction instead.",
        engagement_cta="Comment RESET and I'll send you the full Git reset cheat sheet.",
        visual_storyboard=[
            StoryboardShot(time_range="0-5s", visual="A developer at a laptop; terminal shows a commit timeline A-B-C-D on screen", animation="The HEAD pointer slides backward from D to C", voice="Reset doesn't delete your code", on_screen_text="Reset doesn't delete your code", learning_objective="Create mental model"),
            StoryboardShot(time_range="5-20s", visual="A split-screen terminal window showing three separate reset modes running side by side", animation="Index and working directory panels highlight differently per mode", voice="Soft, mixed, and hard each change something different", on_screen_text="Soft, mixed, hard", learning_objective="Show the distinction"),
            StoryboardShot(time_range="20-40s", visual="A code review screen with a messy commit list next to a cleaned-up version", animation="Commits visually reorganize and merge into clean single entries", voice="Professionals clean commits before review", on_screen_text="Clean commits, easier review", learning_objective="Ground in real workflow"),
            StoryboardShot(time_range="40-60s", visual="A large text overlay of the CTA centered on a dark terminal-style background", animation="The CTA text pulses once and then holds steady", voice="Comment RESET for the cheat sheet", on_screen_text="Comment RESET", learning_objective="Drive engagement"),
        ],
        quality_score=QualityScore(
            technical_accuracy=9, teaching_quality=8, hook_strength=8,
            analogy_quality=8, real_world_relevance=9, interview_value=8, shareability=8,
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
    out = _valid_output(analogy=Analogy(
        analogy="A bookmark in a book.",
        mapping=[AnalogyMapping(real_world="Bookmark location", technical="Git HEAD pointer")],
        limitations="It doesn't cover much else.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_missing_analogy_limitations_fails():
    out = _valid_output(analogy=Analogy(
        analogy="Editing a video timeline.",
        mapping=[
            AnalogyMapping(real_world="Current edit position", technical="Git HEAD pointer"),
            AnalogyMapping(real_world="Preview area selections", technical="the index / staging area"),
        ],
        limitations="",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_low_hook_strength_score_fails():
    out = _valid_output(quality_score=QualityScore(
        technical_accuracy=9, teaching_quality=8, hook_strength=6,
        analogy_quality=8, real_world_relevance=9, interview_value=8, shareability=8,
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_low_technical_accuracy_score_fails():
    out = _valid_output(quality_score=QualityScore(
        technical_accuracy=8, teaching_quality=8, hook_strength=8,
        analogy_quality=8, real_world_relevance=9, interview_value=8, shareability=8,
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_duplicate_explanation_levels_fails():
    out = _valid_output(technical_explanation=TechnicalExplanation(
        level_1_beginner="Reset moves your branch pointer around in history here.",
        level_2_developer="Reset moves your branch pointer around in history here.",
        level_3_professional="Reset moves your branch pointer around in history here.",
        internal_working="Reset moves your branch pointer around in history here.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_mixed_reset_touching_working_dir_fails():
    """Regression: manual review found the model claiming --mixed resets the working directory. It doesn't."""
    out = _valid_output(technical_explanation=TechnicalExplanation(
        level_1_beginner="Reset moves where your branch is pointing to in history overall.",
        level_2_developer="When you run a mixed reset, Git resets the index and working directory.",
        level_3_professional="Soft moves only HEAD; hard resets HEAD, index, and working directory together.",
        internal_working="Mixed reset updates the index to match the new HEAD commit's tree.",
    ))
    with pytest.raises(QualityCheckError, match="working directory"):
        validators.validate(out)


def test_soft_reset_touching_index_fails():
    out = _valid_output(interview=InterviewQA(
        question="What's the difference between reset modes?",
        why_interviewer_asks="Tests understanding of Git's internal state model.",
        strong_answer="A soft reset moves HEAD and also resets the index to match the new commit position exactly.",
        weak_answer="They all just undo commits the same way.",
        follow_up_questions=["How would you recover from a bad reset --hard?"],
    ))
    with pytest.raises(QualityCheckError, match="index"):
        validators.validate(out)


def test_weak_cta_without_reward_fails():
    """Regression: manual review flagged 'comment if you've struggled' as engagement bait, not value."""
    out = _valid_output(engagement_cta="Comment below if you've ever struggled with Git reset!")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_follow_named_series_cta_passes():
    out = _valid_output(engagement_cta="Follow the Daily Git Series for a new concept every day.")
    validators.validate(out)


def test_too_few_storyboard_shots_fails():
    out = _valid_output(visual_storyboard=[
        StoryboardShot(time_range="0-60s", visual="One long shot of everything", animation="Nothing much changes here", voice="This is the whole video", on_screen_text="Everything", learning_objective="Cover it all"),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_real_project_example_without_teamwork_context_fails():
    out = _valid_output(real_project_example=RealProjectExample(
        industry_context="solo project",
        scenario="A developer forgot to commit a file before going home for the day.",
        problem="They realized it the next morning and had to redo some work.",
        solution="They committed the missing file the next day.",
        professional_reasoning="It saves time later on.",
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_few_concept_mistake_entries_fails():
    out = _valid_output(concept_mistakes=[
        MistakeEntry(
            level="beginner",
            wrong_belief="Many assume reset deletes commits outright rather than just moving a pointer.",
            correct_understanding="Reset moves the branch pointer; effect on index/working dir depends on mode.",
            professional_tip="Check git status after any reset.",
        ),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_concept_mistakes_same_level_repeated_fails():
    out = _valid_output(concept_mistakes=[
        MistakeEntry(level="beginner", wrong_belief="Wrong belief number one about reset behavior.", correct_understanding="Correct understanding number one about reset.", professional_tip="Tip number one for this situation."),
        MistakeEntry(level="beginner", wrong_belief="Wrong belief number two about reset behavior.", correct_understanding="Correct understanding number two about reset.", professional_tip="Tip number two for this situation."),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_short_strong_answer_fails():
    out = _valid_output(interview=InterviewQA(
        question="What's the difference between reset modes?",
        why_interviewer_asks="Tests understanding of Git's internal state model.",
        strong_answer="Soft, mixed, hard differ in scope.",
        weak_answer="They all just undo commits the same way.",
        follow_up_questions=["How would you recover from a bad reset --hard?"],
    ))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def _valid_comparison() -> ComparisonStructure:
    return ComparisonStructure(
        concept_a="Git Reset", concept_b="Git Rebase",
        why_confused="Both rewrite local history and are used to 'fix' commits, so beginners lump them together.",
        concept_a_definition="Reset moves the branch pointer, optionally touching index/working dir.",
        concept_b_definition="Rebase replays commits onto a new base, creating new commit hashes.",
        comparison_rows=[
            ComparisonRow(dimension="Purpose", concept_a_value="Move branch pointer back", concept_b_value="Replay commits on a new base"),
            ComparisonRow(dimension="Main Action", concept_a_value="Moves HEAD/index/working dir", concept_b_value="Creates new commits with new hashes"),
            ComparisonRow(dimension="History Impact", concept_a_value="Discards or unstages local commits", concept_b_value="Rewrites commit history linearly"),
            ComparisonRow(dimension="When To Use", concept_a_value="Undo local, unshared commits", concept_b_value="Clean up a feature branch before a PR"),
            ComparisonRow(dimension="When Not To Use", concept_a_value="On commits already pushed and pulled", concept_b_value="On a branch others have already pulled"),
            ComparisonRow(dimension="Professional Recommendation", concept_a_value="Use revert instead on shared branches", concept_b_value="Rebase only personal branches, never shared ones"),
        ],
        decision_rule="If the commit is only local, reset; if you need clean linear history before sharing, rebase.",
    )


def test_valid_comparison_passes():
    out = _valid_output(comparison=_valid_comparison())
    validators.validate(out)


def test_comparison_missing_dimension_fails():
    comp = _valid_comparison()
    comp.comparison_rows = comp.comparison_rows[:-1]  # drop "Professional Recommendation"
    out = _valid_output(comparison=comp)
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_comparison_empty_value_fails():
    comp = _valid_comparison()
    comp.comparison_rows[0].concept_b_value = ""
    out = _valid_output(comparison=comp)
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_reset_hard_removes_secret_without_caveat_fails():
    """The exact dangerous pattern flagged in manual review: reset --hard does NOT permanently erase data."""
    out = _valid_output(real_project_example=RealProjectExample(
        industry_context="software team",
        scenario="A developer accidentally committed an API key to the repository and needs to clean it up before the team pulls.",
        problem="The credential is now sitting in the commit history where anyone with repo access could see it.",
        solution="Run git reset --hard to remove the commit that contains the sensitive data, then continue working.",
        professional_reasoning="This keeps the team's history clean without the exposed credential visible in normal git log output.",
    ))
    with pytest.raises(QualityCheckError, match="removes/deletes sensitive data"):
        validators.validate(out)


def test_reset_hard_removes_secret_with_caveat_passes():
    out = _valid_output(real_project_example=RealProjectExample(
        industry_context="software team",
        scenario="A developer accidentally committed an API key to the repository and needs to clean it up before the team pulls.",
        problem="The credential is now sitting in the commit history where anyone with repo access could see it.",
        solution="Reset only removes it from the visible branch tip — it can persist in reflog or the object database until garbage collected, so the key must be rotated regardless.",
        professional_reasoning="Rotating the credential is the actual fix; history cleanup is secondary and doesn't guarantee removal.",
    ))
    validators.validate(out)


def test_missing_content_plan_field_fails():
    out = _valid_output(content_plan=ContentPlan(main_insight="Too short", content_boundary="Also short"))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_short_memory_anchor_fails():
    out = _valid_output(memory_anchor="Short.")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_too_many_concept_mistakes_fails():
    entry = MistakeEntry(
        level="beginner", wrong_belief="Wrong belief about reset behavior here.",
        correct_understanding="Correct understanding about reset behavior here.",
        professional_tip="A professional tip about handling this situation.",
    )
    out = _valid_output(concept_mistakes=[
        entry,
        MistakeEntry(level="intermediate", wrong_belief="Another wrong belief entirely here.", correct_understanding="Another correct understanding entirely here.", professional_tip="Another professional tip entirely here."),
        MistakeEntry(level="professional", wrong_belief="Yet another wrong belief here too.", correct_understanding="Yet another correct understanding here too.", professional_tip="Yet another professional tip here too."),
        MistakeEntry(level="interview", wrong_belief="One more wrong belief for good measure.", correct_understanding="One more correct understanding for good measure.", professional_tip="One more professional tip for good measure."),
    ])
    with pytest.raises(QualityCheckError):
        validators.validate(out)
