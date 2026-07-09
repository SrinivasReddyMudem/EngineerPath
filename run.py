"""
CLI entry point.

Usage:
    python run.py --subject "Git Rebase" --agents cheat-sheet,reel-script
    python run.py --subject "Git Rebase"                # runs all enabled agents
    python run.py --subject "Git Rebase" --topic git    # --topic defaults to "git"
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from content_agents.orchestrator import generate
from content_agents.core.renderer import render
from content_agents.core.registry import AGENT_NAMES

OUTPUT_DIR = Path(__file__).parent / "outputs"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True, help="e.g. 'Git Rebase' — the specific thing to generate content about")
    parser.add_argument("--topic", default="git", help="skill folder to ground generation in, e.g. 'git'")
    parser.add_argument("--agents", default=None, help=f"comma-separated subset of {AGENT_NAMES}")
    args = parser.parse_args()

    agent_names = args.agents.split(",") if args.agents else None
    results = generate(args.topic, args.subject, agent_names)

    slug = args.subject.lower().replace(" ", "_")
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, output in results.items():
        text = render(name, output)
        print(text)
        print("\n" + "=" * 60 + "\n")
        (out_dir / f"{name}.md").write_text(text, encoding="utf-8")

    print(f"Saved to {out_dir}")


if __name__ == "__main__":
    main()
