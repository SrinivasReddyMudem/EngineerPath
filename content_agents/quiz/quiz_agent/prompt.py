"""
System prompt for quiz. Consumes the shared KnowledgeExtract
(content_agents/knowledge/) — picks only the sections its schema fields
need, rather than independently re-reading skills/.
"""

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


def get_system_prompt(knowledge) -> str:
    """`knowledge` is a content_agents.knowledge.schema.KnowledgeExtract."""
    skill_content = "\n\n".join([
        knowledge.skill_md, knowledge.concepts, knowledge.commands,
        knowledge.internals, knowledge.mistakes, knowledge.interview,
    ])
    return f"{skill_content}\n\n{RULES}"
