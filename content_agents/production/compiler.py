"""
Deterministic compiler: ReelScriptOutput (+ intent, + unresolved issues)
-> ProductionPackage. Pure Python, no LLM call — zero added latency.

Why deterministic and not another generation call: the internal fields
(hook, analogy, technical_explanation, ...) are already validated field
by field (hook bans, analogy completeness, reset-mode fact-check, CTA
reward pattern, etc.). Having a SEPARATE call freely rewrite them into
"a voice script" would risk silently reintroducing an error that
validation just caught, or drifting from the visual_storyboard's `voice`
lines that sync_timeline depends on being accurate. Composing them with
plain string templates keeps one single source of truth.
"""

import re
from content_agents.video.reel_script.schema import ReelScriptOutput
from content_intent.schemas import IntentClassification
from .schema import ProductionPackage, ReelMetadata, VisualScene, SyncEntry, QualityReport

INTENT_LABELS = {
    "concept_explanation": "Concept Explanation",
    "comparison": "Comparison",
    "mistake_correction": "Mistake Correction",
    "interview_preparation": "Interview Preparation",
    "real_project_scenario": "Real Project Scenario",
    "quick_tip": "Quick Tip",
}


_LEADING_ARTICLE_RE = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)


def _strip_article(text: str) -> str:
    """Avoid 'the the exported final video' when the field itself already starts with an article."""
    return _LEADING_ARTICLE_RE.sub("", text.strip())


def _s(text: str) -> str:
    """Ensure a fragment ends with terminal punctuation before it's joined with the next one."""
    text = text.strip()
    if not text:
        return text
    return text if text[-1] in ".!?" else text + "."


def _compose_voice_script(script: ReelScriptOutput) -> str:
    parts = [_s(script.hook)]

    p = script.problem
    parts.append(" ".join(_s(x) for x in [p.real_world_problem, p.developer_pain, p.why_it_matters]))

    if script.comparison is not None:
        c = script.comparison
        parts.append(_s(c.why_confused))
        parts.append(f"{_s(c.concept_a + ' is ' + c.concept_a_definition)} {_s(c.concept_b + ' is ' + c.concept_b_definition)}")
        row_by_dim = {row.dimension: row for row in c.comparison_rows}
        for dim in ["When To Use", "When Not To Use", "Professional Recommendation"]:
            row = row_by_dim.get(dim)
            if row:
                parts.append(f"For {dim.lower()}: {c.concept_a} — {_s(row.concept_a_value)} {c.concept_b} — {_s(row.concept_b_value)}")
        parts.append(f"Here's the decision rule: {_s(c.decision_rule)}")
    else:
        a = script.analogy
        mapping_sentence = " and ".join(
            f"the {_strip_article(m.real_world).lower()} is your {_strip_article(m.technical).lower()}"
            for m in a.mapping
        )
        parts.append(f"Think of it like this: {_s(a.analogy)} {_s(mapping_sentence)}")

        te = script.technical_explanation
        parts.append(f"{_s(te.level_1_beginner)} {_s(te.level_3_professional)}")

        ex = script.real_project_example
        parts.append(" ".join(_s(x) for x in [ex.scenario, ex.solution, ex.professional_reasoning]))

        if script.concept_mistakes:
            parts.append(_s(script.concept_mistakes[0].professional_tip))

    parts.append(_s(script.engagement_cta))
    return " ".join(p.strip() for p in parts if p and p.strip())


def _parse_unresolved_issues(raw_issues: list[str]) -> list[str]:
    """Unpack validate()'s collected 'N issue(s) found:\\n1. ...\\n2. ...' blob into a flat list."""
    notes: list[str] = []
    for blob in raw_issues:
        lines = blob.split("\n")
        for line in lines:
            line = line.strip()
            if re.match(r"^\d+\.\s", line):
                notes.append(re.sub(r"^\d+\.\s", "", line))
            elif line and "issue(s) found" not in line:
                notes.append(line)
    return notes


def compile_production_package(
    script: ReelScriptOutput,
    intent: IntentClassification,
    unresolved_issues: list[str] | None = None,
) -> ProductionPackage:
    unresolved_issues = unresolved_issues or []
    notes = _parse_unresolved_issues(unresolved_issues)

    metadata = ReelMetadata(
        topic=script.topic,
        content_type=INTENT_LABELS.get(intent.intent_type, intent.intent_type),
        audience=intent.audience_level,
        duration="60 seconds",
        learning_objective=intent.learning_goal,
        core_message=script.problem.learning_goal,
    )

    voice_script = _compose_voice_script(script)

    visual_script = [
        VisualScene(
            scene_number=i + 1, time_range=shot.time_range, visual=shot.visual,
            animation=shot.animation, on_screen_text=shot.on_screen_text,
            purpose=shot.learning_objective,
        )
        for i, shot in enumerate(script.visual_storyboard)
    ]

    sync_timeline = [
        SyncEntry(time_range=shot.time_range, voice=shot.voice, visual=shot.visual)
        for shot in script.visual_storyboard
    ]

    qs = script.quality_score
    technical_accuracy: str = "PASS" if qs.technical_accuracy >= 9 else "FAIL"
    teaching_quality: str = "PASS" if qs.teaching_quality >= 7 else "FAIL"
    hook_quality: str = "PASS" if qs.hook_strength >= 8 else "FAIL"
    analogy_quality: str = "PASS" if qs.analogy_quality >= 8 else "FAIL"
    voice_ready: str = "PASS" if len(voice_script) > 100 else "FAIL"
    video_generation_ready: str = "PASS" if all(
        s.visual.strip() and s.animation.strip() and s.on_screen_text.strip() for s in visual_script
    ) else "FAIL"

    all_pass = all(v == "PASS" for v in [
        technical_accuracy, teaching_quality, hook_quality,
        analogy_quality, voice_ready, video_generation_ready,
    ])
    overall: str = "READY" if (all_pass and not notes) else "NEEDS_IMPROVEMENT"

    quality_report = QualityReport(
        technical_accuracy=technical_accuracy, teaching_quality=teaching_quality,
        hook_quality=hook_quality, analogy_quality=analogy_quality,
        voice_ready=voice_ready, video_generation_ready=video_generation_ready,
        overall=overall, notes=notes,
    )

    return ProductionPackage(
        reel_metadata=metadata, voice_script=voice_script,
        visual_script=visual_script, sync_timeline=sync_timeline,
        quality_report=quality_report,
    )
