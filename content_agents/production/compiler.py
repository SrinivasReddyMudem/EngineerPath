"""
Deterministic compiler: ReelScriptOutput (+ intent, + unresolved issues,
+ optional critique) -> ProductionPackage. Pure Python, no LLM call —
zero added latency.

Why deterministic and not another generation call: the internal fields
(hook, analogy, technical_explanation, ...) are already validated field
by field (hook bans, analogy completeness, reset-mode fact-check, CTA
reward pattern, safety caveats, etc.). Having a SEPARATE call freely
rewrite them into "a voice script" would risk silently reintroducing an
error that validation just caught.

voice_script is a straight concatenation of visual_storyboard[i].voice,
in order — NOT independently re-composed from problem/analogy/technical
fields. That used to be two different texts describing the same reel
(the voice script and the sync timeline's per-shot voice lines could
drift apart); making them the same text is the fix, not a stricter
"do these match" check after the fact. The internal reasoning fields
still exist and are still validated (fact-checking, analogy completeness,
safety), they just aren't the source of the spoken narrative anymore —
the storyboard shots are.
"""

import re
from content_agents.core.base_agent import AgentError
from content_agents.video.reel_script.schema import ReelScriptOutput
from content_agents.video.reel_script.validators import MIN_VISUAL_WORDS, MIN_ANIMATION_WORDS
from content_agents.video.reel_critic.schema import ReelCritique
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


def _s(text: str) -> str:
    """Ensure a fragment ends with terminal punctuation before it's joined with the next one."""
    text = text.strip()
    if not text:
        return text
    return text if text[-1] in ".!?" else text + "."


def _compose_voice_script(script: ReelScriptOutput) -> str:
    return " ".join(_s(shot.voice) for shot in script.visual_storyboard if shot.voice.strip())


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


def _notes_mention(notes: list[str], *keywords: str) -> bool:
    combined = " ".join(notes).lower()
    return any(kw in combined for kw in keywords)


def compile_production_package(
    script: ReelScriptOutput,
    intent: IntentClassification,
    unresolved_issues: list[str] | None = None,
    critique: ReelCritique | AgentError | None = None,
) -> ProductionPackage:
    unresolved_issues = unresolved_issues or []
    notes = _parse_unresolved_issues(unresolved_issues)

    metadata = ReelMetadata(
        topic=script.topic,
        content_type=INTENT_LABELS.get(intent.intent_type, intent.intent_type),
        audience=intent.audience_level,
        duration="60 seconds",
        learning_objective=intent.learning_goal,
        core_message=script.content_plan.main_insight,
        recommended_visual_style=script.recommended_visual_style,
    )

    voice_script = _compose_voice_script(script)

    visual_script = [
        VisualScene(
            scene_number=i + 1, time_range=shot.time_range, visual=shot.visual,
            animation=shot.animation, camera=shot.camera, on_screen_text=shot.on_screen_text,
            purpose=shot.learning_objective,
        )
        for i, shot in enumerate(script.visual_storyboard)
    ]

    sync_timeline = [
        SyncEntry(time_range=shot.time_range, voice=shot.voice, visual=shot.visual)
        for shot in script.visual_storyboard
    ]

    qs = script.quality_score
    technical_correctness = "PASS" if qs.technical_accuracy >= 9 else "FAIL"
    command_safety = "FAIL" if _notes_mention(notes, "sensitive data", "rotate", "reflog") else "PASS"
    example_correctness = "FAIL" if _notes_mention(notes, "real_project_example") else "PASS"
    beginner_clarity = "PASS" if qs.teaching_quality >= 7 else "FAIL"
    hook_quality = "PASS" if qs.hook_strength >= 8 else "FAIL"
    analogy_quality = "PASS" if qs.analogy_quality >= 8 else "FAIL"
    visual_generation_readiness = "PASS" if all(
        len(s.visual.split()) >= MIN_VISUAL_WORDS and len(s.animation.split()) >= MIN_ANIMATION_WORDS
        and s.on_screen_text.strip() for s in visual_script
    ) else "FAIL"

    if isinstance(critique, ReelCritique):
        retention = "PASS" if critique.retention.score >= 7 else "FAIL"
    else:
        retention = "NEEDS_IMPROVEMENT"  # no independent critique available — genuinely unknown, not assumed fine

    checked_fields = [
        technical_correctness, command_safety, example_correctness, beginner_clarity,
        visual_generation_readiness, hook_quality, analogy_quality,
    ]
    all_pass = all(v == "PASS" for v in checked_fields) and retention == "PASS"
    overall = "READY" if (all_pass and not notes) else "NOT_READY"

    quality_report = QualityReport(
        technical_correctness=technical_correctness, command_safety=command_safety,
        example_correctness=example_correctness, beginner_clarity=beginner_clarity,
        retention=retention, visual_generation_readiness=visual_generation_readiness,
        hook_quality=hook_quality, analogy_quality=analogy_quality,
        overall=overall, notes=notes,
    )

    return ProductionPackage(
        reel_metadata=metadata, voice_script=voice_script,
        visual_script=visual_script, sync_timeline=sync_timeline,
        quality_report=quality_report,
    )
