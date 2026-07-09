"""Domain validators for cheat_sheet — one quality gate per schema section."""

from content_agents.core.base_agent import QualityCheckError
from .schema import CheatSheetOutput

MIN_COMMANDS = 3
MIN_LIST_ITEMS = 2
MIN_MEMORY_TRICK_LEN = 10


def validate(output: CheatSheetOutput) -> None:
    _check_definition_and_purpose(output)
    _check_commands(output)
    _check_when_lists(output)
    _check_mistakes_and_interview_points(output)
    _check_memory_trick(output)
    _check_self_evaluation_has_evidence(output)


def _check_definition_and_purpose(output: CheatSheetOutput) -> None:
    if len(output.definition.strip()) < 15:
        raise QualityCheckError("definition is too short to be useful.")
    if len(output.purpose.strip()) < 15:
        raise QualityCheckError("purpose is too short to be useful.")


def _check_commands(output: CheatSheetOutput) -> None:
    if len(output.commands_or_api) < MIN_COMMANDS:
        raise QualityCheckError(f"commands_or_api has {len(output.commands_or_api)} entries, needs at least {MIN_COMMANDS}.")
    for i, c in enumerate(output.commands_or_api):
        if not c.command.strip() or not c.description.strip():
            raise QualityCheckError(f"commands_or_api[{i}] has an empty command or description.")


def _check_when_lists(output: CheatSheetOutput) -> None:
    if len(output.when_to_use) < MIN_LIST_ITEMS:
        raise QualityCheckError(f"when_to_use needs at least {MIN_LIST_ITEMS} items.")
    if len(output.when_not_to_use) < MIN_LIST_ITEMS:
        raise QualityCheckError(f"when_not_to_use needs at least {MIN_LIST_ITEMS} items.")
    overlap = set(s.strip().lower() for s in output.when_to_use) & set(s.strip().lower() for s in output.when_not_to_use)
    if overlap:
        raise QualityCheckError(f"when_to_use and when_not_to_use must not contain the same item verbatim: {overlap}")


def _check_mistakes_and_interview_points(output: CheatSheetOutput) -> None:
    if len(output.common_mistakes) < MIN_LIST_ITEMS:
        raise QualityCheckError(f"common_mistakes needs at least {MIN_LIST_ITEMS} items.")
    if len(output.interview_points) < MIN_LIST_ITEMS:
        raise QualityCheckError(f"interview_points needs at least {MIN_LIST_ITEMS} items.")


def _check_memory_trick(output: CheatSheetOutput) -> None:
    if len(output.quick_memory_trick.strip()) < MIN_MEMORY_TRICK_LEN:
        raise QualityCheckError("quick_memory_trick is missing or too short.")


def _check_self_evaluation_has_evidence(output: CheatSheetOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise QualityCheckError(f"self_evaluation item '{line.item}' claims PASS but evidence is empty or too short.")
