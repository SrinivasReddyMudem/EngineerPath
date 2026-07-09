"""Agent registry — maps agent name strings to agent classes. Cross-checked with config/agents_enabled.json."""

from __future__ import annotations
from typing import TYPE_CHECKING
from .config import is_enabled

if TYPE_CHECKING:
    from .base_agent import BaseAgent


def _get_registry() -> dict:
    from content_agents.cheatsheet.cheat_sheet import CheatSheetAgent
    from content_agents.video.reel_script import ReelScriptAgent
    from content_agents.video.reel_critic import ReelCriticAgent
    from content_agents.interview.interview_prep import InterviewPrepAgent
    from content_agents.quiz.quiz_agent import QuizAgent
    from content_intent.classifier import IntentClassifierAgent

    return {
        "cheat-sheet": CheatSheetAgent,
        "reel-script": ReelScriptAgent,
        "reel-critic": ReelCriticAgent,
        "interview-prep": InterviewPrepAgent,
        "quiz": QuizAgent,
        "intent-classifier": IntentClassifierAgent,
    }


AGENT_NAMES = ["cheat-sheet", "reel-script", "reel-critic", "interview-prep", "quiz", "intent-classifier"]


def get_agent(name: str) -> "BaseAgent":
    name = name.lower().strip()
    registry = _get_registry()
    if name not in registry:
        raise KeyError(f"Unknown agent '{name}'. Available: {sorted(registry.keys())}")
    if not is_enabled(name):
        raise PermissionError(f"Agent '{name}' is disabled in config/agents_enabled.json")
    return registry[name]()
