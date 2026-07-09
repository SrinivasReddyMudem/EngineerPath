"""
Thin orchestrator: given a topic and a list of requested agent names,
dispatches to each enabled agent and collects results. No routing
intelligence — that's deliberately out of scope for the MVP.
"""

from content_agents.core.registry import get_agent, AGENT_NAMES
from content_agents.core.config import is_enabled


def generate(topic: str, subject: str, agent_names: list[str] | None = None) -> dict:
    """
    Run the requested agents (default: all registered agents) for one subject.

    `topic` is the skill folder to ground generation in (e.g. 'git') —
    controls which references/*.md get loaded into the prompt.
    `subject` is the specific thing to generate content about (e.g.
    'Git Rebase') — passed as the user message, can be narrower than topic.

    Returns {agent_name: BaseModel | AgentError}. Skips agents disabled in
    config/agents_enabled.json rather than failing the whole batch.
    """
    names = agent_names or AGENT_NAMES
    results = {}
    for name in names:
        if not is_enabled(name):
            continue
        agent = get_agent(name)
        agent.topic = topic
        results[name] = agent.run(f"Generate content for: {subject}")
    return results
