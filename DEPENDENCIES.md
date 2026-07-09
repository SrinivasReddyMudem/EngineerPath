# Dependency Map

Single source of truth for what to verify when touching a file. Look up
the file here before editing; run everything under **must verify**.

Minimum checks that always run regardless of what changed:
```bash
python -m pytest tests/ -q
python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('base_agent OK')"
python -c "from content_agents.core.registry import get_agent, AGENT_NAMES; print(AGENT_NAMES)"
```

---

## Core files — highest impact

### `content_agents/core/base_agent.py`
**Depended on by:** every agent `__init__.py`, every `validators.py` (`QualityCheckError`), `renderer.py` (`AgentError`), `run.py`.
**Must verify:**
- `python -m pytest tests/ -q`
- `python -c "from content_agents.core.base_agent import BaseAgent, AgentError; print('OK')"`

### `content_agents/core/skill_loader.py`
**Depended on by:** every agent's `prompt.py`.
**Must verify:**
- `python -c "from content_agents.core.skill_loader import load_skill; print(len(load_skill('git')))"`
- Re-run the per-agent prompt char budget check below for every agent whose `REFERENCES` list changed.

### `content_agents/core/registry.py` / `content_agents/core/config.py`
**Depended on by:** `orchestrator.py`, `run.py`.
**Must verify:**
- `python -c "from content_agents.core.registry import get_agent; [get_agent(n) for n in ['cheat-sheet','reel-script','interview-prep','quiz']]; print('all agents construct OK')"`
- Confirm `config/agents_enabled.json` has an entry for every name in `AGENT_NAMES`.

### `content_agents/core/renderer.py`
**Depended on by:** `run.py`, affects every agent's saved output.
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

Chain: `schema.py` → `validators.py` (imports schema types) → `renderer.py` (field names must match). `prompt.py` → `skill_loader.py` + must satisfy `validators.py` minimums.

### When touching any agent's `schema.py`
1. Check `validators.py` in the same folder still imports correctly.
2. Check `core/renderer.py`'s render function for that agent — every accessed field still exists.
3. Run `python -m pytest tests/ -q`.

### When touching any agent's `validators.py`
1. `grep -n "MIN_\|BANNED_" content_agents/<group>/<agent>/validators.py` — confirm test fixtures in `tests/test_<agent>_validators.py` still satisfy/violate the right thresholds.
2. Run `python -m pytest tests/test_<agent>_validators.py -v`.

### When touching any agent's `prompt.py` (including its `REFERENCES` list)
1. Check prompt length stays under 25,000 chars:
   ```bash
   python -c "from content_agents.<group>.<agent>.prompt import get_system_prompt as f; p=f('git'); print(len(p)); assert len(p)<25000"
   ```
2. Run `python -m pytest tests/ -q`.

### When touching any file under `skills/git/references/`
1. Re-run the prompt char budget check above for every agent whose `REFERENCES` list includes that file (see each agent's `prompt.py`).
2. Never add a claim that isn't real Git behavior — this content grounds every agent's factual accuracy.

---

## Agent registry

| Agent | Folder | Validators status |
|---|---|---|
| reel-script | `content_agents/video/reel_script/` | Full quality gates (hook/analogy/levels/example/mistakes/CTA/storyboard/preamble) |
| cheat-sheet | `content_agents/cheatsheet/cheat_sheet/` | Full quality gates |
| interview-prep | `content_agents/interview/interview_prep/` | Minimal (schema completeness only) — harden after live testing |
| quiz | `content_agents/quiz/quiz_agent/` | Minimal (structural only) — harden after live testing |

## Adding a new topic (e.g. `c`, `cpp`, `linux`)
1. Create `skills/<topic>/SKILL.md` + `skills/<topic>/references/*.md` mirroring `skills/git/`.
2. No code changes needed — every agent already takes `topic` as a constructor arg.
3. Run `python run.py --topic <topic> --agents cheat-sheet` first to sanity-check the new skill content before enabling all four agents.

## Adding a new agent (new output type)
1. Create `schema.py`, `prompt.py`, `validators.py`, `__init__.py` in a new group folder.
2. Add its render function to `core/renderer.py`.
3. Register it in `core/registry.py` (`_get_registry()` + `AGENT_NAMES`) and add its entry to `config/agents_enabled.json`.
4. Add `tests/test_<agent>_validators.py`.
5. Add a row to the Agent registry table above.
6. Run `python -m pytest tests/ -q`.
