# Content Engineering Agents

Converts a technical topic into multiple high-quality educational
outputs (Reel/Shorts scripts, cheat sheets, interview prep, quizzes)
using the same skill+schema+validator architecture proven in
`automotive-lifecycle-agents`: curated domain knowledge grounds the
model, a strict Pydantic schema forces structural completeness, and
`validators.py` enforces the specific quality rules for that output
type — with automatic retry-with-feedback when a gate fails.

## Global rules

1. Content is never freely generated — every output must match its
   Pydantic schema exactly. No output bypasses `validators.py`.
2. Never fabricate a command, flag, or technical fact. Every factual
   claim in generated content must trace back to a file under
   `skills/<topic>/references/`. If a reference doesn't cover it, the
   agent should generate a general pattern, not a fabricated specific.
3. Analogies must state *why* the mapping holds, not just assert it —
   a bare comparison is a validation failure (see
   `skills/git/references/analogies.md`'s banned list for examples).
4. Hooks and CTAs must match the psychological pattern/value-offer
   rules in each agent's `prompt.py` — generic openers ("In this
   video...") and generic CTAs ("follow for more") are hard validation
   failures for `reel-script`, not style suggestions.
5. Which agents run is controlled by `config/agents_enabled.json` —
   check it before assuming an agent is active; `orchestrator.py`
   skips disabled agents silently rather than erroring.
6. `interview-prep` and `quiz` currently have minimal validators
   (structural completeness only) by deliberate choice, pending live
   testing of `reel-script` and `cheat-sheet` first. Don't add heavy
   quality gates to them without being asked — that was intentionally
   deferred, not forgotten.

## Pre-change validation — mandatory before every commit

Look up the file you're touching in `DEPENDENCIES.md` first — it is the
single source of truth for what must be verified per file. Minimum
checks that always run:

```bash
python -m pytest tests/ -q
python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('base_agent OK')"
python -c "from content_agents.core.registry import get_agent, AGENT_NAMES; print(AGENT_NAMES)"
```

## Architecture notes

- `skills/<topic>/` — domain knowledge only (facts, analogies, mistakes,
  interview questions). No output-format or tone rules here — those
  belong in the agent's `prompt.py`.
- Each agent's `prompt.py` declares a `REFERENCES` list — only those
  reference files load into its system prompt, not the whole topic.
  This keeps prompt tokens bounded as more reference files are added.
  Every agent's system prompt must stay under 25,000 chars — checked
  in `DEPENDENCIES.md`.
- `content_agents/core/` is a near-direct port of
  `automotive-lifecycle-agents/sdk_agents/core/` (Groq + strict
  `json_schema` + retry-on-failure-with-feedback). Don't redesign it
  without a concrete reason — it's already proven at scale in that repo.
- Model: Groq `llama-3.3-70b-versatile` (see `core/base_agent.py`
  `MODEL` constant) — chosen over `llama-4-scout` for better creative/
  analogy quality, still free tier. Gemini was considered as a
  provider-swap for even higher creative quality; not adopted yet —
  revisit if Groq output quality disappoints after live testing.
