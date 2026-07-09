"""
System prompt for interview_prep. Consumes the shared KnowledgeExtract
(content_agents/knowledge/) — picks only the sections its schema fields
need, rather than independently re-reading skills/.
"""

RULES = """
# Interview Prep Generation Rules

Generate interview questions for ONE topic across all four difficulty
levels: beginner, intermediate, advanced, expert. Pull questions and
their ideal_answer_points from references/interview.md — do not invent
questions or answer criteria not grounded there. Each level needs at
least one question.
"""


def get_system_prompt(knowledge) -> str:
    """`knowledge` is a content_agents.knowledge.schema.KnowledgeExtract."""
    skill_content = "\n\n".join([
        knowledge.skill_md, knowledge.concepts, knowledge.internals,
        knowledge.interview, knowledge.mistakes,
    ])
    return f"{skill_content}\n\n{RULES}"
