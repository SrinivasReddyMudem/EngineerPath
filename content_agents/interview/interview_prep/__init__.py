from content_agents.core.base_agent import BaseAgent
from .schema import InterviewPrepOutput
from . import prompt as prompt_module
from . import validators


class InterviewPrepAgent(BaseAgent):
    AGENT_NAME = "interview-prep"

    def __init__(self, topic: str = "git"):
        super().__init__()
        self.topic = topic

    def get_schema(self):
        return InterviewPrepOutput

    def get_prompt(self) -> str:
        return prompt_module.get_system_prompt(self.topic)

    def _validate_quality(self, parsed: InterviewPrepOutput) -> None:
        validators.validate(parsed)


__all__ = ["InterviewPrepAgent"]
