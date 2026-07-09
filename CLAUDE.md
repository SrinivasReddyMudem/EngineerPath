# Content Engineering Agents

Converts a technical topic into high-quality educational outputs
(Reel/Shorts scripts; more output types planned) using the same
skill+schema+validator architecture proven in
`automotive-lifecycle-agents`: curated domain knowledge grounds the
model, a strict Pydantic schema forces structural completeness, and
`validators.py` enforces the specific quality rules for that output
type — with automatic retry-with-feedback when a gate fails.

## Architecture — purpose-driven router, not "generate everything"

```
User Request
     v
Intent / Output Router      content_agents/router.py
     v
Knowledge Extraction        content_agents/knowledge/  (shared, deterministic)
     v
Requested Output Generator  e.g. content_agents/video/reel_script/
     v
Quality Validators
     v
Final Output
```

This is a hard rule, not a convenience default: **the system never
generates every content type by default.** `router.generate_content(topic,
subject, purpose)` runs exactly ONE generator pipeline for the given
`purpose`. Adding a new purpose means adding one entry to
`router.PURPOSE_TO_AGENT` plus a new generator package — never changing
the router's control flow or the knowledge layer.

All four current generators — `reel`, `cheatsheet`, `interview`, `quiz`
(see `router.PURPOSE_TO_AGENT`) — are wired through the router and
consume the shared `KnowledgeExtract`. Adding a new output type (blog,
LinkedIn post, PDF notes, ...) means adding one entry to
`PURPOSE_TO_AGENT` plus a new generator package — never touching the
router's control flow or the knowledge layer.

## Global rules

1. Content is never freely generated — every output must match its
   Pydantic schema exactly. No output bypasses `validators.py`.
2. Never fabricate a command, flag, or technical fact. Every factual
   claim in generated content must trace back to a file under
   `skills/<topic>/references/`. If a reference doesn't cover it, the
   agent should generate a general pattern, not a fabricated specific.
3. Analogies must state *why* the mapping holds (and where it breaks
   down — see `Analogy.limitations`), not just assert it. A bare
   comparison, or an analogy missing `limitations`, is a validation
   failure (see `skills/git/references/analogies.md`'s banned list).
4. Hooks and CTAs must match the psychological pattern/value-offer
   rules in each agent's `prompt.py` — generic openers ("In this
   video...") and generic CTAs ("follow for more") are hard validation
   failures for `reel-script`, not style suggestions.
5. Which agents run is controlled by `config/agents_enabled.json` —
   `router.generate_content()` (via `registry.get_agent()`) raises
   `PermissionError` for a disabled agent rather than silently skipping.
6. `interview-prep` and `quiz` currently have minimal validators
   (structural completeness only) by deliberate choice — they're wired
   onto the router but haven't had the fact-checking/completeness gate
   treatment `reel-script` got. Don't add heavy quality gates to them
   without being asked — that was intentionally deferred, not forgotten.
7. Deterministic fact-checking validators (e.g. `reel_script/validators.py`
   `_check_reset_mode_accuracy`) exist because self-reported quality
   scores alone missed a real technical error in manual review. Prefer
   adding a targeted deterministic check over trusting a higher
   self-reported score — that's the higher-leverage place to add rigor.

## Pre-change validation — mandatory before every commit

Look up the file you're touching in `DEPENDENCIES.md` first — it is the
single source of truth for what must be verified per file. Minimum
checks that always run:

```bash
python -m pytest tests/ -q
python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('base_agent OK')"
python -c "from content_agents.router import generate_content, PURPOSE_TO_AGENT; print(PURPOSE_TO_AGENT)"
```

## Architecture notes

- `skills/<topic>/` — domain knowledge only (facts, analogies, mistakes,
  interview questions, commands). No output-format or tone rules here —
  those belong in the agent's `prompt.py`.
- `content_agents/knowledge/extractor.py` loads a topic's full skill
  content ONCE into a `KnowledgeExtract` (deterministic, no LLM call —
  adding semantic extraction/summarization here would cost latency and
  add a drift risk with no proven benefit yet). Each generator's
  `prompt.py` then selects only the `KnowledgeExtract` fields its schema
  needs — this is how prompt tokens stay bounded as more reference files
  are added, not by re-reading `skills/` independently per generator.
  Every agent's system prompt must stay under 25,000 chars — checked in
  `DEPENDENCIES.md`.
- `content_agents/core/` is a near-direct port of
  `automotive-lifecycle-agents/sdk_agents/core/` (Groq + strict
  `json_schema` + retry-on-failure-with-feedback). Don't redesign it
  without a concrete reason — it's already proven at scale in that repo.
- Model: Groq `meta-llama/llama-4-scout-17b-16e-instruct` (see
  `core/base_agent.py` `MODEL` constant) — the only model confirmed on
  this account to support Groq's strict `json_schema` mode;
  `llama-3.3-70b-versatile` rejects that response format outright and
  `llama-4-maverick-17b-128e-instruct` 404s on this account's tier.
