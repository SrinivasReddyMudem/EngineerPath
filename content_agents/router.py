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
    [purpose-specific critique, e.g. reel-critic]   (optional per purpose)
         v
    Final Output

Deliberately does NOT default to running every generator — `purpose`
is required, and only that one generator's pipeline executes. This is
a hard architectural rule, not a convenience default: adding a new
purpose means adding one entry to PURPOSE_TO_AGENT plus a new generator
package, never touching the router's control flow or the knowledge layer.

All four content generators are ported onto the shared KnowledgeExtract
and reachable through this router. Adding a new purpose (blog, LinkedIn
post, PDF notes, ...) means adding one entry here plus a new generator
package.
"""

from content_agents.core.base_agent import AgentError
from content_agents.core.registry import get_agent
from content_agents.core.renderer import render
from content_agents.knowledge.extractor import extract as extract_knowledge

PURPOSE_TO_AGENT = {
    "reel": "reel-script",
    "cheatsheet": "cheat-sheet",
    "interview": "interview-prep",
    "quiz": "quiz",
}

# Purposes that get an automatic independent critique pass after generation.
# Chosen explicitly (not automatic for every purpose): the user asked for
# this specifically for reel scripts, where audience-psychology/pedagogy
# quality is the whole point. This roughly doubles latency/cost for these
# purposes — an accepted trade-off for "always run the critique."
PURPOSE_TO_CRITIC = {
    "reel": "reel-critic",
}


def generate_content(topic: str, subject: str, purpose: str):
    """
    Run exactly ONE generator pipeline for one subject, plus its critique
    agent if one is registered for this purpose. Returns a tuple
    (result, critique): `critique` is None when no critic is wired up for
    this purpose, or when `result` is itself an AgentError (nothing to
    critique). Never raises for a content-generation failure, only for a
    routing error (bad purpose).
    """
    if purpose not in PURPOSE_TO_AGENT:
        raise ValueError(
            f"Unknown purpose '{purpose}'. Available now: {sorted(PURPOSE_TO_AGENT.keys())}. "
            f"Other output types (blog, LinkedIn post, PDF notes, ...) are added here one at a "
            f"time as their generators are ported onto the shared knowledge layer."
        )
    agent_name = PURPOSE_TO_AGENT[purpose]
    knowledge = extract_knowledge(topic)
    agent = get_agent(agent_name)
    agent.topic = topic
    agent.knowledge = knowledge
    result = agent.run(f"Generate content for: {subject}")

    critic_agent_name = PURPOSE_TO_CRITIC.get(purpose)
    if critic_agent_name is None or isinstance(result, AgentError):
        return result, None

    script_text = render(agent_name, result)
    critic = get_agent(critic_agent_name)
    critique = critic.run(f"Critique this reel script:\n\n{script_text}")
    return result, critique
