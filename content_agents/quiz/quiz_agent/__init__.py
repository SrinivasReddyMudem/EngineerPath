from content_agents.core.base_agent import BaseAgent
from .schema import QuizOutput
from . import prompt as prompt_module
from . import validators


class QuizAgent(BaseAgent):
    AGENT_NAME = "quiz"

    def __init__(self, topic: str = "git"):
        super().__init__()
        self.topic = topic

    def get_schema(self):
        return QuizOutput

    def get_prompt(self) -> str:
        return prompt_module.get_system_prompt(self.topic)

    def _validate_quality(self, parsed: QuizOutput) -> None:
        validators.validate(parsed)


__all__ = ["QuizAgent"]
