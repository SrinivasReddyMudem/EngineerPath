"""Turns each agent's Pydantic output into copy-paste-ready markdown."""

from .base_agent import AgentError


def render(agent_name: str, output) -> str:
    if isinstance(output, AgentError):
        return f"# {agent_name} FAILED\n\n**{output.error_type}**: {output.message}\n"
    renderer = _RENDERERS.get(agent_name)
    if renderer is None:
        return output.model_dump_json(indent=2)
    return renderer(output)


def render_reel_script(o) -> str:
    lines = [
        f"# Reel Script — {o.topic}\n",
        f"**Hook ({o.hook_type}):** {o.hook}\n",
        f"**Problem:** {o.problem}\n",
        f"**Analogy:** {o.analogy.analogy}",
    ]
    for pair in o.analogy.mapping:
        lines.append(f"- {pair.real_world} = {pair.technical}")
    lines += [
        "",
        "**Technical explanation:**",
        f"- L1 (beginner): {o.technical_explanation.level_1_beginner}",
        f"- L2 (developer): {o.technical_explanation.level_2_developer}",
        f"- L3 (professional): {o.technical_explanation.level_3_professional}\n",
        "**Real project example:**",
        f"- Scenario: {o.real_project_example.scenario}",
        f"- Problem: {o.real_project_example.problem}",
        f"- Solution: {o.real_project_example.solution}",
        f"- Why professionals use it: {o.real_project_example.why_professionals_use_it}\n",
        "**Concept understanding:**",
        f"- Beginner misunderstanding: {o.concept_understanding.beginner_misunderstanding}",
        f"- Professional insight: {o.concept_understanding.professional_insight}\n",
        "**Interview:**",
        f"- Q: {o.interview.question}",
        f"- Strong answer: {o.interview.strong_answer}",
        f"- Common weak answer: {o.interview.common_weak_answer}",
        f"- Follow-up: {o.interview.follow_up_question}\n",
        f"**CTA:** {o.engagement_cta}\n",
        "**Storyboard:**",
    ]
    for shot in o.visual_storyboard:
        lines.append(
            f"- [{shot.time_range}] {shot.visual} | animation: {shot.animation} | "
            f"text: \"{shot.on_screen_text}\" | purpose: {shot.purpose}"
        )
    qs = o.quality_score
    lines += [
        "",
        "**Self-scored quality:** "
        f"accuracy={qs.technical_accuracy}/10, clarity={qs.beginner_clarity}/10, "
        f"relevance={qs.professional_relevance}/10, hook={qs.hook_quality}/10, "
        f"analogy={qs.analogy_quality}/10, shareability={qs.share_save_potential}/10",
    ]
    return "\n".join(lines)


def render_cheat_sheet(o) -> str:
    lines = [
        f"# Cheat Sheet — {o.topic}\n",
        f"**Definition:** {o.definition}\n",
        f"**Purpose:** {o.purpose}\n",
        "**Commands / API:**",
    ]
    for c in o.commands_or_api:
        lines.append(f"- `{c.command}` — {c.description}")
    lines.append("\n**When to use:**")
    lines += [f"- {x}" for x in o.when_to_use]
    lines.append("\n**When NOT to use:**")
    lines += [f"- {x}" for x in o.when_not_to_use]
    lines.append("\n**Common mistakes:**")
    lines += [f"- {x}" for x in o.common_mistakes]
    lines.append("\n**Interview points:**")
    lines += [f"- {x}" for x in o.interview_points]
    lines.append(f"\n**Quick memory trick:** {o.quick_memory_trick}")
    return "\n".join(lines)


def render_interview_prep(o) -> str:
    lines = [f"# Interview Prep — {o.topic}\n"]
    for q in o.questions:
        lines.append(f"**[{q.level}]** {q.question}")
        for p in q.ideal_answer_points:
            lines.append(f"  - {p}")
        lines.append("")
    return "\n".join(lines)


def render_quiz(o) -> str:
    lines = [f"# Quiz — {o.topic}\n"]
    for i, q in enumerate(o.questions, start=1):
        lines.append(f"**Q{i} ({q.difficulty}):** {q.question}")
        for j, opt in enumerate(q.options):
            marker = "CORRECT" if j == q.correct_answer_index else "       "
            lines.append(f"  [{marker}] {opt}")
        lines.append(f"  _Explanation: {q.explanation}_\n")
    return "\n".join(lines)


_RENDERERS = {
    "reel-script": render_reel_script,
    "cheat-sheet": render_cheat_sheet,
    "interview-prep": render_interview_prep,
    "quiz": render_quiz,
}
