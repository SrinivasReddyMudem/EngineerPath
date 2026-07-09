"""
The single structured representation of a topic's domain knowledge.
Every output generator consumes this SAME object for a given topic —
no generator re-reads or re-interprets skills/ independently anymore.
"""

from pydantic import BaseModel


class KnowledgeExtract(BaseModel):
    topic: str
    skill_md: str
    concepts: str
    internals: str
    workflows: str
    mistakes: str
    analogies: str
    interview: str
    commands: str
