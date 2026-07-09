"""
Loads skill content from the shared skills/ folder.
Only the ONE requested topic's folder is read per call — never all topics —
to keep per-request prompt tokens bounded as more topics are added.
"""

from pathlib import Path

SKILLS_ROOT = Path(__file__).parents[2] / "skills"


def load_skill(topic: str, references: list[str] | None = None) -> str:
    """
    Load SKILL.md + reference files for a given topic (e.g. 'git').

    `references`, if given, is a list of reference basenames without '.md'
    (e.g. ['analogies', 'mistakes']) — only those files load. Each agent
    passes only the references its schema fields actually need, so prompt
    token cost doesn't grow with the full topic knowledge base as more
    reference files are added over time. Omit to load every reference file.
    """
    skill_dir = SKILLS_ROOT / topic
    if not skill_dir.exists():
        available = [d.name for d in SKILLS_ROOT.iterdir() if d.is_dir()]
        raise FileNotFoundError(f"Topic '{topic}' not found at {skill_dir}. Available: {available}")

    parts = []

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text(encoding="utf-8"))

    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        if references is None:
            ref_files = sorted(refs_dir.glob("*.md"))
        else:
            ref_files = [refs_dir / f"{name}.md" for name in references]
            missing = [f for f in ref_files if not f.exists()]
            if missing:
                raise FileNotFoundError(f"Reference file(s) not found: {missing}")
        for ref_file in ref_files:
            parts.append(ref_file.read_text(encoding="utf-8"))

    return "\n\n".join(parts)
