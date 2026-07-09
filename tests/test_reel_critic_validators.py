"""Pure validator tests — no API calls, no GROQ_API_KEY needed."""

import pytest
from content_agents.core.base_agent import QualityCheckError
from content_agents.video.reel_critic.schema import ReelCritique, DimensionScore
from content_agents.video.reel_critic import validators


def _dim(score=8, critique="This works because the hook creates a genuine open question about reset modes.", suggestion="Tighten the first sentence to under 10 words.") -> DimensionScore:
    return DimensionScore(score=score, critique=critique, improvement_suggestion=suggestion)


def _valid_output(**overrides) -> ReelCritique:
    base = dict(
        topic="git",
        curiosity=_dim(), mental_model=_dim(), story_flow=_dim(), natural_language=_dim(),
        retention=_dim(), shareability=_dim(), emotional_connection=_dim(),
        conversation_style=_dim(), visual_explainability=_dim(), beginner_friendliness=_dim(),
        professional_relevance=_dim(),
        overall_verdict="ready_to_publish",
        top_priority_fix="Shorten the hook to create tension faster in the first 2 seconds.",
    )
    base.update(overrides)
    return ReelCritique(**base)


def test_valid_output_passes():
    validators.validate(_valid_output())


def test_short_critique_fails():
    out = _valid_output(curiosity=_dim(critique="Good."))
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_short_top_priority_fix_fails():
    out = _valid_output(top_priority_fix="Fix it.")
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_ready_to_publish_with_many_low_scores_fails():
    out = _valid_output(
        curiosity=_dim(score=5), mental_model=_dim(score=4), story_flow=_dim(score=6),
        overall_verdict="ready_to_publish",
    )
    with pytest.raises(QualityCheckError):
        validators.validate(out)


def test_needs_revision_with_many_low_scores_passes():
    out = _valid_output(
        curiosity=_dim(score=5), mental_model=_dim(score=4), story_flow=_dim(score=6),
        overall_verdict="needs_revision",
    )
    validators.validate(out)
