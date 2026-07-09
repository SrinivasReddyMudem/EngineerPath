"""Output schema for cheat_sheet — concise reference material for one technical topic."""

from pydantic import BaseModel, Field
from content_agents.core.shared_schema import SelfEvaluationLine


class CommandEntry(BaseModel):
    command: str = Field(description="The actual command/API call, e.g. 'git rebase -i HEAD~3'")
    description: str = Field(description="What it does, in one line")


class CheatSheetOutput(BaseModel):
    model_config = {"extra": "ignore"}

    topic: str
    definition: str = Field(description="Precise, jargon-light definition of the topic")
    purpose: str = Field(description="Why this exists / what problem it solves")
    commands_or_api: list[CommandEntry] = Field(description="At least 3 real commands, grounded in the topic references")
    when_to_use: list[str] = Field(description="At least 2 concrete situations")
    when_not_to_use: list[str] = Field(description="At least 2 concrete situations")
    common_mistakes: list[str] = Field(description="At least 2 mistakes, grounded in references/mistakes.md")
    interview_points: list[str] = Field(description="At least 2 points an interviewer expects you to know")
    quick_memory_trick: str = Field(description="A short mnemonic or memorable framing")
    self_evaluation: list[SelfEvaluationLine] = Field(
        description="One PASS/FAIL line per gate: commands_are_real, when_to_use_vs_not_distinct, "
        "mistakes_grounded, memory_trick_present"
    )
