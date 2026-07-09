from content_agents.core.base_agent import BaseAgent
from content_agents.knowledge.extractor import extract as extract_knowledge
from .schema import QuizOutput
from . import prompt as prompt_module
from . import validators


class QuizAgent(BaseAgent):
    AGENT_NAME = "quiz"

    def __init__(self, topic: str = "git"):
        super().__init__()
        self.topic = topic
        self.knowledge = None  # set by router.py; falls back to direct extraction if unset (standalone/test use)

    def get_schema(self):
        return QuizOutput

    def get_prompt(self) -> str:
        knowledge = self.knowledge or extract_knowledge(self.topic)
        return prompt_module.get_system_prompt(knowledge)

    def _validate_quality(self, parsed: QuizOutput) -> None:
        validators.validate(parsed)


__all__ = ["QuizAgent"]
