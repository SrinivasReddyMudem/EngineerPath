"""
Enable/disable control for which agents actually run.
Edit config/agents_enabled.json to turn an agent on or off without touching code.
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parents[2] / "config" / "agents_enabled.json"


def get_enabled_agents() -> list[str]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return [name for name, enabled in data.items() if enabled]


def is_enabled(agent_name: str) -> bool:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if agent_name not in data:
        raise KeyError(f"'{agent_name}' not in {CONFIG_PATH}. Known agents: {list(data.keys())}")
    return data[agent_name]
