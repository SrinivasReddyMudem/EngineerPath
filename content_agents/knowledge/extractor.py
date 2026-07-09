"""
Knowledge Extraction — the single source of truth every output generator
consumes for a topic. Deterministic (no LLM call): it loads the topic's
skill content once per request, so every generator sees identical facts
instead of independently re-reading and re-interpreting skills/.

Deliberately not LLM-based extraction (no summarization/interpretation
step) — that would add cost, latency, and a new place for drift for no
proven benefit yet. If a generator needs a narrower slice, it selects
which KnowledgeExtract fields it needs (see reel_script/prompt.py);
the retrieval itself stays centralized here.
"""

from content_agents.core.skill_loader import load_skill_md, load_reference
from .schema import KnowledgeExtract

REFERENCE_NAMES = ["concepts", "internals", "workflows", "mistakes", "analogies", "interview", "commands"]


def extract(topic: str) -> KnowledgeExtract:
    return KnowledgeExtract(
        topic=topic,
        skill_md=load_skill_md(topic),
        **{name: load_reference(topic, name) for name in REFERENCE_NAMES},
    )
