"""
CLI entry point — goes through the Intent/Output Router. No default
"generate everything"; --purpose is required and runs exactly one
generator pipeline.

Usage:
    python run.py --subject "Git Reset" --purpose reel
    python run.py --subject "Git Rebase" --purpose cheatsheet
    python run.py --subject "Git Merge" --purpose interview --topic git
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from content_agents.router import generate_content, PURPOSE_TO_AGENT
from content_agents.core.renderer import render

OUTPUT_DIR = Path(__file__).parent / "outputs"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True, help="e.g. 'Git Reset' — the specific thing to generate content about")
    parser.add_argument("--purpose", default="reel", choices=sorted(PURPOSE_TO_AGENT.keys()), help="which single output type to generate (default: reel)")
    parser.add_argument("--topic", default="git", help="skill folder to ground generation in, e.g. 'git'")
    args = parser.parse_args()

    agent_name = PURPOSE_TO_AGENT[args.purpose]
    output = generate_content(args.topic, args.subject, args.purpose)

    slug = args.subject.lower().replace(" ", "_")
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    text = render(agent_name, output)
    print(text)
    (out_dir / f"{agent_name}.md").write_text(text, encoding="utf-8")
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
