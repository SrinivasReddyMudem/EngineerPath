"""Pure compiler tests — no API calls needed, reuses the reel_script test fixture."""

from content_intent.schemas import IntentClassification
from content_agents.production.compiler import compile_production_package, _s
from tests.test_reel_script_validators import _valid_output, _valid_comparison


def _intent(**overrides) -> IntentClassification:
    base = dict(
        query="Git Reset", intent_type="concept_explanation", audience_level="intermediate",
        learning_goal="Understand Git reset modes", recommended_content_structure="hook + analogy + technical depth",
    )
    base.update(overrides)
    return IntentClassification(**base)


def test_compile_voice_script_is_storyboard_voice_lines_joined():
    """
    voice_script is compiled DIRECTLY from visual_storyboard[i].voice, in
    order — not independently re-composed from problem/analogy/technical.
    This is the fix for the voice/sync-timeline drift bug found in review:
    previously these were two different texts describing the same reel.
    """
    script = _valid_output()
    package = compile_production_package(script, _intent())
    for shot in script.visual_storyboard:
        assert _s(shot.voice) in package.voice_script
    # and nothing from the (now purely internal/validation-only) fields leaks in
    assert script.problem.real_world_problem not in package.voice_script


def test_compile_voice_script_has_no_run_on_sentences():
    script = _valid_output()
    package = compile_production_package(script, _intent())
    shots = script.visual_storyboard
    assert f"{_s(shots[0].voice)} {_s(shots[1].voice)}" in package.voice_script


def test_compile_concept_explanation_metadata():
    package = compile_production_package(_valid_output(), _intent())
    assert package.reel_metadata.content_type == "Concept Explanation"
    assert package.reel_metadata.duration == "60 seconds"


def test_compile_comparison_metadata_reflects_intent():
    """
    The comparison structure itself is validation-only now (ensures the
    model thought through the comparison correctly) — the compiler doesn't
    parse it directly, since the storyboard voice lines are the single
    source of truth for voice_script regardless of intent type.
    """
    script = _valid_output(comparison=_valid_comparison())
    package = compile_production_package(script, _intent(intent_type="comparison", query="Git Reset vs Git Rebase"))
    assert package.reel_metadata.content_type == "Comparison"


def test_compile_sync_timeline_matches_storyboard_length():
    script = _valid_output()
    package = compile_production_package(script, _intent())
    assert len(package.sync_timeline) == len(script.visual_storyboard)
    assert len(package.visual_script) == len(script.visual_storyboard)


def test_compile_quality_report_reflects_low_scores():
    from content_agents.video.reel_script.schema import QualityScore
    script = _valid_output(quality_score=QualityScore(
        technical_accuracy=8, teaching_quality=8, hook_strength=8,
        analogy_quality=8, real_world_relevance=9, interview_value=8, shareability=8,
    ))
    package = compile_production_package(script, _intent())
    assert package.quality_report.technical_correctness == "FAIL"  # 8 < 9 gate
    assert package.quality_report.overall == "NOT_READY"


def test_compile_notes_parsed_from_unresolved_issues():
    package = compile_production_package(
        _valid_output(), _intent(),
        unresolved_issues=["2 issue(s) found:\n1. First issue text.\n2. Second issue text."],
    )
    assert package.quality_report.notes == ["First issue text.", "Second issue text."]
    assert package.quality_report.overall == "NOT_READY"


def test_compile_cta_quality_fails_when_noted():
    package = compile_production_package(
        _valid_output(), _intent(),
        unresolved_issues=["1 issue(s) found:\n1. engagement_cta uses banned generic phrase 'follow for more'."],
    )
    assert package.quality_report.cta_quality == "FAIL"


def test_compile_teaching_flow_fails_when_jargon_front_loaded():
    from content_agents.video.reel_script.schema import StoryboardShot
    script = _valid_output()
    shots = list(script.visual_storyboard)
    shots[0] = StoryboardShot(
        time_range=shots[0].time_range, visual=shots[0].visual, animation=shots[0].animation,
        camera=shots[0].camera, voice="--soft, --mixed, and --hard all work differently, with reflog recovery too.",
        on_screen_text=shots[0].on_screen_text, learning_objective=shots[0].learning_objective,
    )
    package = compile_production_package(_valid_output(visual_storyboard=shots), _intent())
    assert package.quality_report.teaching_flow == "FAIL"


def test_compile_voice_naturalness_fails_when_lines_too_long():
    from content_agents.video.reel_script.schema import StoryboardShot
    script = _valid_output()
    long_voice = " ".join(["word"] * 30)
    shots = [
        StoryboardShot(
            time_range=s.time_range, visual=s.visual, animation=s.animation, camera=s.camera,
            voice=long_voice, on_screen_text=s.on_screen_text, learning_objective=s.learning_objective,
        )
        for s in script.visual_storyboard
    ]
    package = compile_production_package(_valid_output(visual_storyboard=shots), _intent())
    assert package.quality_report.voice_naturalness == "FAIL"
