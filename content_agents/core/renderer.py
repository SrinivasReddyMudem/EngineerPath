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
    p = o.problem
    lines = [
        f"# Reel Script — {o.topic}\n",
        f"**Hook ({o.hook_type}):** {o.hook}\n",
        "**Problem:**",
        f"- Real-world problem: {p.real_world_problem}",
        f"- Developer pain: {p.developer_pain}",
        f"- Why it matters: {p.why_it_matters}",
        f"- Learning goal: {p.learning_goal}\n",
        f"**Analogy:** {o.analogy.analogy}",
    ]
    for pair in o.analogy.mapping:
        lines.append(f"- {pair.real_world} = {pair.technical}")
    lines.append(f"_Limitations: {o.analogy.limitations}_\n")
    te = o.technical_explanation
    lines += [
        "**Technical explanation:**",
        f"- L1 (what): {te.level_1_beginner}",
        f"- L2 (how): {te.level_2_developer}",
        f"- L3 (why/when): {te.level_3_professional}",
        f"- Internal mechanism: {te.internal_working}\n",
        "**Real project example:**",
        f"- Industry context: {o.real_project_example.industry_context}",
        f"- Scenario: {o.real_project_example.scenario}",
        f"- Problem: {o.real_project_example.problem}",
        f"- Solution: {o.real_project_example.solution}",
        f"- Professional reasoning: {o.real_project_example.professional_reasoning}\n",
        "**Concept mistakes:**",
    ]
    for m in o.concept_mistakes:
        lines.append(f"- [{m.level}] Wrong: {m.wrong_belief} | Correct: {m.correct_understanding} | Tip: {m.professional_tip}")
    qa = o.interview
    lines += [
        "",
        "**Interview:**",
        f"- Q: {qa.question}",
        f"- Why asked: {qa.why_interviewer_asks}",
        f"- Strong answer: {qa.strong_answer}",
        f"- Weak answer: {qa.weak_answer}",
        "- Follow-ups: " + "; ".join(qa.follow_up_questions) + "\n",
        f"**Memory anchor:** {o.memory_anchor}",
        f"**CTA:** {o.engagement_cta}\n",
        "**Storyboard:**",
    ]
    for shot in o.visual_storyboard:
        lines.append(
            f"- [{shot.time_range}] {shot.visual} | animation: {shot.animation} | voice: \"{shot.voice}\" | "
            f"text: \"{shot.on_screen_text}\" | goal: {shot.learning_objective}"
        )
    qs = o.quality_score
    lines += [
        "",
        "**Self-scored quality:** "
        f"accuracy={qs.technical_accuracy}/10, teaching={qs.teaching_quality}/10, "
        f"hook={qs.hook_strength}/10, analogy={qs.analogy_quality}/10, "
        f"relevance={qs.real_world_relevance}/10, interview={qs.interview_value}/10, "
        f"shareability={qs.shareability}/10",
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


def render_production_package(o) -> str:
    m = o.reel_metadata
    lines = [
        "# SECTION 1: REEL METADATA\n",
        f"**Topic:** {m.topic}",
        f"**Content Type:** {m.content_type}",
        f"**Audience:** {m.audience}",
        f"**Duration:** {m.duration}",
        f"**Learning Objective:** {m.learning_objective}",
        f"**Core Message:** {m.core_message}",
        f"**Recommended Visual Style:** {m.recommended_visual_style}\n",
        "# SECTION 2: VOICE SCRIPT\n",
        o.voice_script,
        "\n# SECTION 3: VISUAL GENERATION SCRIPT\n",
    ]
    for scene in o.visual_script:
        lines += [
            f"**Scene {scene.scene_number}** ({scene.time_range})",
            f"- Visual: {scene.visual}",
            f"- Animation: {scene.animation}",
            f"- Text: {scene.on_screen_text}",
            f"- Purpose: {scene.purpose}\n",
        ]
    lines.append("# SECTION 4: SYNCHRONIZATION TIMELINE\n")
    for entry in o.sync_timeline:
        lines += [f"**{entry.time_range}**", f"- Voice: {entry.voice}", f"- Visual: {entry.visual}\n"]
    q = o.quality_report
    lines += [
        "# SECTION 5: QUALITY REPORT\n",
        f"- Technical Correctness: {q.technical_correctness}",
        f"- Command Safety: {q.command_safety}",
        f"- Example Correctness: {q.example_correctness}",
        f"- Beginner Clarity: {q.beginner_clarity}",
        f"- Retention: {q.retention}",
        f"- Visual Generation Readiness: {q.visual_generation_readiness}",
        f"- Hook Quality: {q.hook_quality}",
        f"- Analogy Quality: {q.analogy_quality}",
        f"- **Overall: {q.overall}**",
    ]
    if q.notes:
        lines.append("\n**Notes:**")
        lines += [f"- {n}" for n in q.notes]
    return "\n".join(lines)


def render_reel_critic(o) -> str:
    dims = [
        "curiosity", "mental_model", "story_flow", "natural_language", "retention",
        "shareability", "emotional_connection", "conversation_style",
        "visual_explainability", "beginner_friendliness", "professional_relevance",
    ]
    lines = [f"# Audience Psychology Critique — {o.topic}\n", f"**Verdict: {o.overall_verdict.upper()}**\n"]
    for name in dims:
        d = getattr(o, name)
        label = name.replace("_", " ").title()
        lines.append(f"**{label}: {d.score}/10** — {d.critique}")
        lines.append(f"  _Fix: {d.improvement_suggestion}_\n")
    lines.append(f"**Top priority fix:** {o.top_priority_fix}")
    return "\n".join(lines)


_RENDERERS = {
    "reel-script": render_reel_script,
    "reel-critic": render_reel_critic,
    "reel-production": render_production_package,
    "cheat-sheet": render_cheat_sheet,
    "interview-prep": render_interview_prep,
    "quiz": render_quiz,
}
