from content_agents.core.base_agent import BaseAgent
from .schema import ReelCritique
from . import prompt as prompt_module
from . import validators


class ReelCriticAgent(BaseAgent):
    """
    Independent audience-psychology/educational-experience critic. Takes
    an already-generated reel script's rendered text as its user_message
    — not topic-grounded, doesn't need KnowledgeExtract, since it's
    critiquing craft/pedagogy, not Git facts.
    """

    AGENT_NAME = "reel-critic"

    def __init__(self, topic: str = "git"):
        super().__init__()
        self.topic = topic  # unused for prompt content; kept for logging/consistency with other agents

    def get_schema(self):
        return ReelCritique

    def get_prompt(self) -> str:
        return prompt_module.get_system_prompt()

    def _validate_quality(self, parsed: ReelCritique) -> None:
        validators.validate(parsed)


__all__ = ["ReelCriticAgent"]
