"""System prompt for quiz."""

from content_agents.core.skill_loader import load_skill

REFERENCES = ["concepts", "commands", "internals", "mistakes", "interview"]

RULES = """
# Quiz Generation Rules

Generate at least 5 multiple-choice questions for ONE topic, each with
exactly 4 options, one correct_answer_index, and an explanation. Ground
questions in references/concepts.md, references/internals.md, and
references/mistakes.md (mistakes make excellent wrong-answer distractors
and question material) — do not invent facts not covered there. Mix
difficulty across easy/medium/hard rather than making every question
the same difficulty.
"""


def get_system_prompt(topic: str) -> str:
    skill_content = load_skill(topic, references=REFERENCES)
    return f"{skill_content}\n\n{RULES}"
