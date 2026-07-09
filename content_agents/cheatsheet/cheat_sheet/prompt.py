"""
System prompt for cheat_sheet. Consumes the shared KnowledgeExtract
(content_agents/knowledge/) — picks only the sections its schema fields
need, rather than independently re-reading skills/.
"""

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


def get_system_prompt(knowledge) -> str:
    """`knowledge` is a content_agents.knowledge.schema.KnowledgeExtract."""
    skill_content = "\n\n".join([
        knowledge.skill_md, knowledge.concepts, knowledge.commands,
        knowledge.workflows, knowledge.mistakes, knowledge.interview,
    ])
    return f"{skill_content}\n\n{RULES}"
