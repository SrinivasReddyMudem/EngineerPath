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
1. Check prompt length stays under 25,000 chars:
   ```bash
   python -c "
   from content_agents.knowledge.extractor import extract
   from content_agents.video.reel_script.prompt import get_system_prompt
   p = get_system_prompt(extract('git')); print(len(p)); assert len(p) < 25000"
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
| reel-script | `content_agents/video/reel_script/` | Yes (`purpose="reel"`) | Full quality gates + deterministic fact-checking (hook/analogy/problem/technical/example/mistakes/interview/CTA/storyboard/quality-score gates) |
| cheat-sheet | `content_agents/cheatsheet/cheat_sheet/` | No — standalone | Full quality gates |
| interview-prep | `content_agents/interview/interview_prep/` | No — standalone | Minimal (schema completeness only) — harden + port to router later |
| quiz | `content_agents/quiz/quiz_agent/` | No — standalone | Minimal (structural only) — harden + port to router later |

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
