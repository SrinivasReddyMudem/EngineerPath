"""
Structural validators for reel_critic. Deliberately light — this agent's
whole point is a subjective, holistic critique; the only things worth
enforcing mechanically are "did it actually critique" (non-generic,
non-empty) and "is the verdict consistent with the scores it gave."
"""

from content_agents.core.base_agent import QualityCheckError
from .schema import ReelCritique

MIN_CRITIQUE_LEN = 20
MIN_SUGGESTION_LEN = 10
MIN_TOP_FIX_LEN = 15
LOW_SCORE_THRESHOLD = 7
MIN_LOW_SCORES_FOR_REVISION = 3

DIMENSION_NAMES = [
    "curiosity", "mental_model", "story_flow", "natural_language", "retention",
    "shareability", "emotional_connection", "conversation_style",
    "visual_explainability", "beginner_friendliness", "professional_relevance",
]


def validate(output: ReelCritique) -> None:
    issues: list[str] = []
    low_score_count = 0

    for name in DIMENSION_NAMES:
        dim = getattr(output, name)
        if len(dim.critique.strip()) < MIN_CRITIQUE_LEN:
            issues.append(f"{name}.critique is too short or missing ({len(dim.critique)} chars).")
        if len(dim.improvement_suggestion.strip()) < MIN_SUGGESTION_LEN:
            issues.append(f"{name}.improvement_suggestion is too short or missing.")
        if dim.score < LOW_SCORE_THRESHOLD:
            low_score_count += 1

    if len(output.top_priority_fix.strip()) < MIN_TOP_FIX_LEN:
        issues.append("top_priority_fix is too short or missing.")

    if low_score_count >= MIN_LOW_SCORES_FOR_REVISION and output.overall_verdict == "ready_to_publish":
        issues.append(
            f"overall_verdict is 'ready_to_publish' but {low_score_count} dimensions scored below "
            f"{LOW_SCORE_THRESHOLD} — that combination isn't consistent. Set verdict to 'needs_revision'."
        )

    if issues:
        numbered = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(issues))
        raise QualityCheckError(f"{len(issues)} issue(s) found:\n{numbered}")
