"""
Intent / Output Router — the single entry point for content generation.

    User Request
         v
    Intent / Output Router   (this file)
         v
    Knowledge Extraction     (content_agents/knowledge/, shared)
         v
    Requested Output Generator   (e.g. reel_script)
         v
    Quality Validators
         v
    Final Output

Deliberately does NOT default to running every generator — `purpose`
is required, and only that one generator's pipeline executes. This is
a hard architectural rule, not a convenience default: adding a new
purpose means adding one entry to PURPOSE_TO_AGENT plus a new generator
package, never touching the router's control flow or the knowledge layer.

All four generators are now ported onto the shared KnowledgeExtract and
reachable through this router. Adding a new purpose (blog, LinkedIn
post, PDF notes, ...) means adding one entry here plus a new generator
package — the router's control flow and the knowledge layer don't change.
"""

from content_agents.core.registry import get_agent
from content_agents.knowledge.extractor import extract as extract_knowledge

PURPOSE_TO_AGENT = {
    "reel": "reel-script",
    "cheatsheet": "cheat-sheet",
    "interview": "interview-prep",
    "quiz": "quiz",
}


def generate_content(topic: str, subject: str, purpose: str):
    """
    Run exactly ONE generator pipeline for one subject. Returns a
    BaseModel (success) or AgentError (failure) — never raises for a
    content-generation failure, only for a routing error (bad purpose).
    """
    if purpose not in PURPOSE_TO_AGENT:
        raise ValueError(
            f"Unknown purpose '{purpose}'. Available now: {sorted(PURPOSE_TO_AGENT.keys())}. "
            f"Other output types (interview, cheatsheet, quiz, blog, ...) are added here one at "
            f"a time as their generators are ported onto the shared knowledge layer."
        )
    agent_name = PURPOSE_TO_AGENT[purpose]
    knowledge = extract_knowledge(topic)
    agent = get_agent(agent_name)
    agent.topic = topic
    agent.knowledge = knowledge
    return agent.run(f"Generate content for: {subject}")
