from content_agents.core.base_agent import BaseAgent
from .schema import ReelScriptOutput
from . import prompt as prompt_module
from . import validators


class ReelScriptAgent(BaseAgent):
    AGENT_NAME = "reel-script"

    def __init__(self, topic: str = "git"):
        super().__init__()
        self.topic = topic

    def get_schema(self):
        return ReelScriptOutput

    def get_prompt(self) -> str:
        return prompt_module.get_system_prompt(self.topic)

    def _validate_quality(self, parsed: ReelScriptOutput) -> None:
        validators.validate(parsed)


__all__ = ["ReelScriptAgent"]
