"""System prompt for interview_prep."""

from content_agents.core.skill_loader import load_skill

REFERENCES = ["concepts", "internals", "interview", "mistakes"]

RULES = """
# Interview Prep Generation Rules

Generate interview questions for ONE topic across all four difficulty
levels: beginner, intermediate, advanced, expert. Pull questions and
their ideal_answer_points from references/interview.md — do not invent
questions or answer criteria not grounded there. Each level needs at
least one question.
"""


def get_system_prompt(topic: str) -> str:
    skill_content = load_skill(topic, references=REFERENCES)
    return f"{skill_content}\n\n{RULES}"
