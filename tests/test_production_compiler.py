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


def test_compile_concept_explanation_has_no_run_on_sentences():
    script = _valid_output()
    package = compile_production_package(script, _intent())
    # Every field must be terminally punctuated before the next one starts —
    # whether or not the source field already had punctuation of its own.
    assert f"{_s(script.problem.real_world_problem)} {_s(script.problem.developer_pain)}" in package.voice_script
    assert f"{_s(script.problem.developer_pain)} {_s(script.problem.why_it_matters)}" in package.voice_script


def test_compile_analogy_mapping_has_no_double_article():
    """Regression: 'The exported final video' + prepended 'the' produced 'the the exported final video'."""
    package = compile_production_package(_valid_output(), _intent())
    assert "the the " not in package.voice_script.lower()


def test_compile_concept_explanation_metadata():
    package = compile_production_package(_valid_output(), _intent())
    assert package.reel_metadata.content_type == "Concept Explanation"
    assert package.reel_metadata.duration == "60 seconds"


def test_compile_comparison_uses_comparison_flow():
    script = _valid_output(comparison=_valid_comparison())
    package = compile_production_package(script, _intent(intent_type="comparison", query="Git Reset vs Git Rebase"))
    assert "Git Reset" in package.voice_script and "Git Rebase" in package.voice_script
    assert "decision rule" in package.voice_script.lower()
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
    assert package.quality_report.overall == "NEEDS_IMPROVEMENT"


def test_compile_notes_parsed_from_unresolved_issues():
    package = compile_production_package(
        _valid_output(), _intent(),
        unresolved_issues=["2 issue(s) found:\n1. First issue text.\n2. Second issue text."],
    )
    assert package.quality_report.notes == ["First issue text.", "Second issue text."]
    assert package.quality_report.overall == "NEEDS_IMPROVEMENT"
