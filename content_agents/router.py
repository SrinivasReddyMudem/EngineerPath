"""
Intent / Output Router — the single entry point for content generation.

    User Request
         v
    Content Intent Classifier   (content_intent/, purpose="reel" only)
         v
    Intent / Output Router       (this file)
         v
    Knowledge Extraction         (content_agents/knowledge/, shared)
         v
    Requested Output Generator   (e.g. reel_script)
         v
    Quality Validators
         v
    [purpose-specific critique, e.g. reel-critic]   (router.PURPOSE_TO_CRITIC)
         v
    [purpose-specific production compiler, e.g. reel]   (router.PURPOSE_TO_COMPILER)
         v
    Final Output

Deliberately does NOT default to running every generator — `purpose`
is required, and only that one generator's pipeline executes. This is
a hard architectural rule, not a convenience default: adding a new
purpose means adding one entry to PURPOSE_TO_AGENT plus a new generator
package, never touching the router's control flow or the knowledge layer.

All four content generators are ported onto the shared KnowledgeExtract
and reachable through this router. Adding a new purpose (blog, LinkedIn
post, PDF notes, ...) means adding one entry here plus a new generator
package.
"""

from content_agents.core.base_agent import AgentError
from content_agents.core.registry import get_agent
from content_agents.core.renderer import render
from content_agents.knowledge.extractor import extract as extract_knowledge
from content_intent.schemas import IntentClassification
from content_agents.production.compiler import compile_production_package

PURPOSE_TO_AGENT = {
    "reel": "reel-script",
    "cheatsheet": "cheat-sheet",
    "interview": "interview-prep",
    "quiz": "quiz",
}

# Purposes that get an automatic independent critique pass after generation.
# Chosen explicitly (not automatic for every purpose): the user asked for
# this specifically for reel scripts, where audience-psychology/pedagogy
# quality is the whole point. This roughly doubles latency/cost for these
# purposes — an accepted trade-off for "always run the critique."
PURPOSE_TO_CRITIC = {
    "reel": "reel-critic",
}

# Purposes that get intent-classified first and compiled into a
# production-ready package instead of returning the raw generator output.
# The raw internal fields (hook, analogy, technical_explanation, ...) are
# never shown to the caller for these purposes — only the compiled
# package (metadata, voice script, visual script, sync timeline, quality
# report), per explicit design: internal validators are internal.
PURPOSE_TO_COMPILER = {
    "reel": compile_production_package,
}

# Render key for the (possibly compiled) primary result — "reel-production"
# for compiled purposes, otherwise the same as PURPOSE_TO_AGENT.
PURPOSE_TO_RESULT_RENDER_KEY = {
    "reel": "reel-production",
}


def result_render_key(purpose: str) -> str:
    return PURPOSE_TO_RESULT_RENDER_KEY.get(purpose, PURPOSE_TO_AGENT[purpose])


def _classify_intent(subject: str) -> IntentClassification:
    classifier = get_agent("intent-classifier")
    result = classifier.run(f"Classify this query: {subject}")
    if isinstance(result, AgentError):
        # Classification failing shouldn't block generation — fall back to
        # a safe default rather than erroring the whole request.
        return IntentClassification(
            query=subject, intent_type="concept_explanation", audience_level="mixed",
            learning_goal=f"Understand {subject}",
            recommended_content_structure="hook + analogy + technical depth",
        )
    return result


def generate_content(topic: str, subject: str, purpose: str):
    """
    Run exactly ONE generator pipeline for one subject, plus its critique
    agent if one is registered, plus its production compiler if one is
    registered. Returns a tuple (result, critique): `critique` is None
    when no critic is wired up for this purpose, or when `result` is
    itself an AgentError (nothing to critique). Never raises for a
    content-generation failure, only for a routing error (bad purpose).
    """
    if purpose not in PURPOSE_TO_AGENT:
        raise ValueError(
            f"Unknown purpose '{purpose}'. Available now: {sorted(PURPOSE_TO_AGENT.keys())}. "
            f"Other output types (blog, LinkedIn post, PDF notes, ...) are added here one at a "
            f"time as their generators are ported onto the shared knowledge layer."
        )
    agent_name = PURPOSE_TO_AGENT[purpose]

    intent = _classify_intent(subject) if purpose in PURPOSE_TO_COMPILER else None
    user_message = f"Generate content for: {subject}"
    if intent is not None:
        user_message += (
            f"\n\nClassified intent: {intent.intent_type}. Audience: {intent.audience_level}. "
            f"Learning goal: {intent.learning_goal}. Recommended structure: {intent.recommended_content_structure}."
        )

    knowledge = extract_knowledge(topic)
    agent = get_agent(agent_name)
    agent.topic = topic
    agent.knowledge = knowledge
    result = agent.run(user_message)
    unresolved_issues = list(getattr(agent, "last_unresolved_issues", []))

    critic_agent_name = PURPOSE_TO_CRITIC.get(purpose)
    critique = None
    if critic_agent_name is not None and not isinstance(result, AgentError):
        script_text = render(agent_name, result)
        critic = get_agent(critic_agent_name)
        critique = critic.run(f"Critique this reel script:\n\n{script_text}")

    compiler = PURPOSE_TO_COMPILER.get(purpose)
    if compiler is not None and not isinstance(result, AgentError):
        result = compiler(result, intent, unresolved_issues)

    return result, critique
