# Dependency Map

Single source of truth for what to verify when touching a file. Look up
the file here before editing; run everything under **must verify**.

Minimum checks that always run regardless of what changed:
```bash
python -m pytest tests/ -q
python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('base_agent OK')"
python -c "from content_agents.router import generate_content, PURPOSE_TO_AGENT; print(PURPOSE_TO_AGENT)"
```

---

## Core files — highest impact

### `content_agents/router.py`
**Depended on by:** `run.py`, `app.py`. The single entry point for content generation — never add a "generate all purposes" default here.
**Must verify:**
- `python -c "from content_agents.router import generate_content, PURPOSE_TO_AGENT; print(PURPOSE_TO_AGENT)"`
- Every key in `PURPOSE_TO_AGENT` must map to a name registered in `core/registry.py`.
- Every key in `PURPOSE_TO_COMPILER` must also have an entry in `PURPOSE_TO_RESULT_RENDER_KEY`, and that render key must exist in `core/renderer.py`'s `_RENDERERS`.

### `content_intent/classifier.py` / `content_intent/schemas.py`
**Depended on by:** `router.py` (`_classify_intent`, only for purposes in `PURPOSE_TO_COMPILER`).
**Must verify:**
- `python -c "from content_intent.classifier import IntentClassifierAgent; print('OK')"`
- If classification itself fails (`AgentError`), the router falls back to a safe default rather than blocking generation — don't remove that fallback.

### `content_agents/production/compiler.py` / `content_agents/production/schema.py`
**Depended on by:** `router.py` for any purpose in `PURPOSE_TO_COMPILER` (currently only `reel`).
**Must verify:**
- `python -m pytest tests/test_production_compiler.py -v`
- Pure Python, no LLM call — if you find yourself wanting to add an LLM call here, reconsider: the whole point is one source of truth (the validated `ReelScriptOutput`) with zero added latency.

### `content_agents/knowledge/extractor.py` / `content_agents/knowledge/schema.py`
**Depended on by:** `router.py`, and all four generators' `prompt.py` (`reel_script`, `cheat_sheet`, `interview_prep`, `quiz_agent`).
**Must verify:**
- `python -c "from content_agents.knowledge.extractor import extract; k = extract('git'); print(list(k.model_dump().keys()))"`
- `KnowledgeExtract.REFERENCE_NAMES` in `extractor.py` must match the actual `.md` basenames under `skills/<topic>/references/` for every topic — a mismatch raises `FileNotFoundError` at extraction time, not import time.

### `content_agents/core/base_agent.py`
**Depended on by:** every agent `__init__.py`, every `validators.py` (`QualityCheckError`), `renderer.py` (`AgentError`), `run.py`.
**Must verify:**
- `python -m pytest tests/ -q`
- `python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('OK')"`

### `content_agents/core/skill_loader.py`
**Depended on by:** `knowledge/extractor.py` (via `load_skill_md`/`load_reference`) — all four agents get their skill content through the knowledge layer now, not directly from this module.
**Must verify:**
- `python -c "from content_agents.core.skill_loader import load_skill_md, load_reference; print(len(load_skill_md('git')))"`
- Re-run the per-agent prompt char budget check below for every agent whose reference selection changed.

### `content_agents/core/registry.py` / `content_agents/core/config.py`
**Depended on by:** `router.py` (via `get_agent`), `app.py`'s standalone-agent path.
**Must verify:**
- `python -c "from content_agents.core.registry import get_agent; [get_agent(n) for n in ['cheat-sheet','reel-script','interview-prep','quiz']]; print('all agents construct OK')"`
- Confirm `config/agents_enabled.json` has an entry for every name in `AGENT_NAMES`.

### `content_agents/core/renderer.py`
**Depended on by:** `run.py`, `app.py`, affects every agent's saved output.
**Must verify:**
- Every `render_<agent>` function's field access must exist in that agent's `schema.py` — cross-check the table below.

| Agent | Schema | Render function |
|---|---|---|
| reel-script | `video/reel_script/schema.py` — `ReelScriptOutput` | `render_reel_script` |
| cheat-sheet | `cheatsheet/cheat_sheet/schema.py` — `CheatSheetOutput` | `render_cheat_sheet` |
| interview-prep | `interview/interview_prep/schema.py` — `InterviewPrepOutput` | `render_interview_prep` |
| quiz | `quiz/quiz_agent/schema.py` — `QuizOutput` | `render_quiz` |

---

## Per-agent files — isolated impact

Chain: `schema.py` → `validators.py` (imports schema types) → `renderer.py` (field names must match). `prompt.py` → knowledge source + must satisfy `validators.py` minimums.

### When touching any agent's `schema.py`
1. Check `validators.py` in the same folder still imports correctly.
2. Check `core/renderer.py`'s render function for that agent — every accessed field still exists.
3. Run `python -m pytest tests/ -q`.

### When touching any agent's `validators.py`
1. `grep -n "MIN_\|BANNED_" content_agents/<group>/<agent>/validators.py` — confirm test fixtures in `tests/test_<agent>_validators.py` still satisfy/violate the right thresholds.
2. Run `python -m pytest tests/test_<agent>_validators.py -v`.

### When touching `reel_script/prompt.py` (knowledge-layer agent)
1. Check prompt length stays under 26,000 chars — raised from the default 25,000 because this schema now covers safety validation, content planning, and richer visual requirements; don't raise it further without a real reason:
   ```bash
   python -c "
   from content_agents.knowledge.extractor import extract
   from content_agents.video.reel_script.prompt import get_system_prompt
   p = get_system_prompt(extract('git')); print(len(p)); assert len(p) < 26000"
   ```
2. Run `python -m pytest tests/ -q`.

### When touching `cheat_sheet`/`interview_prep`/`quiz_agent`'s `prompt.py` (still `load_skill`-direct, not on knowledge layer)
1. Check prompt length stays under 25,000 chars:
   ```bash
   python -c "from content_agents.<group>.<agent>.prompt import get_system_prompt as f; p=f('git'); print(len(p)); assert len(p)<25000"
   ```
2. Run `python -m pytest tests/ -q`.

### When touching any file under `skills/git/references/`
1. Re-run the prompt char budget check above for every agent that references that file (reel-script's set is in `knowledge/extractor.py` + `reel_script/prompt.py`; other agents declare their own `REFERENCES` list).
2. Never add a claim that isn't real Git behavior — this content grounds every agent's factual accuracy.

---

## Agent registry

| Agent | Folder | On router? | Validators status |
|---|---|---|---|
| reel-script | `content_agents/video/reel_script/` | Yes (`purpose="reel"`, internal — output is compiled, not shown directly) | Full quality gates + deterministic fact-checking; `validate()` collects ALL failing checks per attempt, not just the first; includes optional `comparison` structure |
| reel-critic | `content_agents/video/reel_critic/` | Auto-runs after `purpose="reel"` (see `router.PURPOSE_TO_CRITIC`) | Independent audience-psychology/educational-experience critic — takes the rendered reel script as input, not topic-grounded (no KnowledgeExtract) |
| intent-classifier | `content_intent/classifier.py` | Runs before generation for any purpose in `PURPOSE_TO_COMPILER` | Minimal (structural) — classifies intent_type/audience_level/learning_goal from the raw query |
| cheat-sheet | `content_agents/cheatsheet/cheat_sheet/` | Yes (`purpose="cheatsheet"`) | Full quality gates |
| interview-prep | `content_agents/interview/interview_prep/` | Yes (`purpose="interview"`) | Minimal (schema completeness only) — harden after live testing |
| quiz | `content_agents/quiz/quiz_agent/` | Yes (`purpose="quiz"`) | Minimal (structural only) — harden after live testing |

**Not an agent, but on the critical path for `purpose="reel"`:** `content_agents/production/compiler.py` (`compile_production_package`) — deterministic, no LLM call, turns the validated `reel-script` output into the user-facing `ProductionPackage` (metadata, voice script, visual script, sync timeline, quality report).

### Best-effort fallback (all agents, `core/base_agent.py`)
If the final retry attempt still fails a `QualityCheckError`, `run()` returns the parsed content anyway (it already passed strict schema validation) instead of `AgentError`, logging the unresolved issue. This trades "guaranteed quality" for "never a wasted wait with nothing to show" — check the agent's log file if you want to know whether a returned result had an unresolved gate.

### Critique pipeline (`router.PURPOSE_TO_CRITIC`)
Adding a critic for another purpose: register the critic agent in `core/registry.py` + `config/agents_enabled.json` like any other agent, then add one entry to `PURPOSE_TO_CRITIC` in `router.py`. The critic receives `render(agent_name, result)` (the rendered markdown) as its `user_message` — no other wiring needed. This **roughly doubles** latency/cost for that purpose; only add it where the user has explicitly asked for an always-on critique.

## Adding a new topic (e.g. `c`, `cpp`, `linux`)
1. Create `skills/<topic>/SKILL.md` + `skills/<topic>/references/*.md` mirroring `skills/git/` — same 7 reference basenames (`concepts, internals, workflows, mistakes, analogies, interview, commands`), since `knowledge/extractor.py` expects those exact names.
2. No code changes needed — `router.generate_content(topic, subject, purpose)` already takes `topic` as a parameter.
3. Run `python run.py --subject "<something>" --purpose reel --topic <topic>` first to sanity-check the new skill content.

## Adding a new purpose / output generator
1. Create `schema.py`, `prompt.py`, `validators.py`, `__init__.py` in a new group folder (same pattern as `video/reel_script/`).
2. If porting onto the shared knowledge layer: `prompt.py`'s `get_system_prompt(knowledge)` takes a `KnowledgeExtract` and selects the fields it needs (see `reel_script/prompt.py`); the agent's `__init__.py` stores `self.knowledge` (see `reel_script/__init__.py`).
3. Add its render function to `core/renderer.py`.
4. Register it in `core/registry.py` (`_get_registry()` + `AGENT_NAMES`) and add its entry to `config/agents_enabled.json`.
5. Add one entry to `router.PURPOSE_TO_AGENT` (e.g. `"interview": "interview-prep"`).
6. Add `tests/test_<agent>_validators.py`.
7. Add a row to the Agent registry table above.
8. Run `python -m pytest tests/ -q`.
