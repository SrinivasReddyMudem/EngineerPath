"""Pure validator tests — no API calls, no GROQ_API_KEY needed."""

import pytest
from content_agents.core.base_agent import QualityCheckError
from content_agents.core.shared_schema import SelfEvaluationLine
from content_agents.cheatsheet.cheat_sheet.schema import CheatSheetOutput, CommandEntry
from content_agents.cheatsheet.cheat_sheet import validators


def _valid_output(**overrides) -> CheatSheetOutput:
    base = dict(
        topic="git rebase",
        definition="Rebase replays commits from one branch onto a new base commit, creating new commit hashes.",
        purpose="Keeps project history linear instead of interleaved with merge commits.",
        commands_or_api=[
            CommandEntry(command="git rebase main", description="Replay current branch's commits onto main"),
            CommandEntry(command="git rebase -i HEAD~3", description="Interactively edit the last 3 commits"),
            CommandEntry(command="git rebase --abort", description="Cancel an in-progress rebase"),
        ],
        when_to_use=["Cleaning up a personal feature branch before a PR", "Keeping history linear on solo projects"],
        when_not_to_use=["On a branch teammates have already pulled", "After the branch is already merged"],
        common_mistakes=["Rebasing a shared branch and force-pushing over teammates' work", "Forgetting --continue after resolving a conflict"],
        interview_points=["Rebase changes commit hashes; merge doesn't", "Never rebase public/shared history"],
        quick_memory_trick="Rebase = REwrite BASE.",
        self_evaluation=[SelfEvaluationLine(item="commands_are_real", result="PASS", evidence="All three commands are real git subcommands")],
    )
    base.update(overrides)
    return CheatSheetOutput(**base)


def test_valid_output_passes():
    validators.validate(_valid_output())


def test_too_few_commands_fails():
    out = _valid_output(commands_or_api=[CommandEntry(command="git rebase main", description="x")])
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_overlapping_when_lists_fails():
    out = _valid_output(
        when_to_use=["Same item here"],
        when_not_to_use=["Same item here"],
    )
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_missing_memory_trick_fails():
    out = _valid_output(quick_memory_trick="")
    with pytest.raises(QualityCheckError):
        validators.validate(out)
