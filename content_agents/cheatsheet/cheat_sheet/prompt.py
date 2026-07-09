"""System prompt for cheat_sheet. Loads only the reference files this agent's schema needs."""

from content_agents.core.skill_loader import load_skill

REFERENCES = ["concepts", "commands", "workflows", "mistakes", "interview"]

RULES = """
# Cheat Sheet Generation Rules

Produce concise reference material for ONE technical topic. Structure:
definition, purpose, commands/API, when to use, when not to use, common
mistakes, interview points, quick memory trick.

Rules:
- commands_or_api: at least 3 real commands grounded in references/workflows.md
  and references/concepts.md — never invent a flag or command not covered there.
- when_to_use / when_not_to_use: concrete situations, not generic advice;
  the two lists must not overlap.
- common_mistakes: pull from references/mistakes.md, don't invent new ones.
- interview_points: pull from references/interview.md.
- quick_memory_trick: a genuinely memorable framing (mnemonic, short phrase),
  not a restatement of the definition.

Self-evaluation: check commands_are_real, when_to_use_vs_not_distinct,
mistakes_grounded, memory_trick_present — PASS only with real evidence.
"""


def get_system_prompt(topic: str) -> str:
    skill_content = load_skill(topic, references=REFERENCES)
    return f"{skill_content}\n\n{RULES}"
