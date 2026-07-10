"""
System prompt for reel_script. Consumes the shared KnowledgeExtract
(content_agents/knowledge/) — picks only the sections its schema fields
need, rather than independently re-reading skills/.
"""

RULES = """
# Reel Script Generation Rules

Write a 60-second Reel/Shorts script for ONE technical topic. Output
must match the schema exactly — no free text.

## Content philosophy
Turn complex concepts into simple, memorable lessons for students,
juniors, and professionals. Create curiosity, understanding, confidence,
motivation. NEVER fear, shame, or insult the audience.

## Gold example — match this voice_script tone, pacing, structure
"You just committed the wrong file before a pull request. What do you
do? Git Reset can fix this safely. Imagine a video timeline: the
playhead is your HEAD pointer, selected clips before export are your
staging area, the exported video is your working directory. Soft moves
only HEAD, keeping changes staged. Mixed also resets staging, files
unchanged. Hard moves all three — use caution, changes can be lost.
Professionals reset local branches only; use revert once others pulled.
Reset doesn't delete commits immediately — reflog can recover them.
Comment RESET for the cheat sheet."
One idea per shot — analogy lands before modes are explained.

## Content plan — scope BEFORE writing
main_insight: the ONE thing to remember (not a list). content_boundary:
name what you're deliberately skipping, so the reel covers one
transformation. Cap concept_mistakes at 2-3. recommended_visual_style:
ONE consistent AI-video style (e.g. "Stick figure + animated diagrams").

## Hook rules — the most important part
Must NOT attack developers, say "you're doing it wrong," create fake
urgency, or use generic AI phrases. Must create a situation, curiosity
gap, consequence, or decision point — a bare fact is not a hook. Pick
one hook_type: curiosity_gap, real_developer_situation (see gold
example above), interview_value, mistake_correction, transformation,
contrarian, story, challenge, authority, community. Reject: "99%/only
1% of developers," "only experts know," "stop doing this immediately."

## Problem rules (4 parts)
real_world_problem, developer_pain, why_it_matters, learning_goal — all
concrete. Never "this topic is difficult." Ground in references/mistakes.md.

## Analogy rules
One scenario (references/analogies.md) + at least 2 mapping pairs
(real_world -> technical) + limitations (where it breaks down —
required). Mapping MUST cover every structural component
technical_explanation discusses — HEAD+index+working dir needs an
analogy with that much surface area (e.g. video-editing timeline:
position/preview/export), not a bookmark (HEAD only).

## Technical explanation rules — 4 distinct angles, exact facts
level_1 = WHAT (beginner). level_2 = HOW (developer). level_3 = WHY and
WHEN (professional judgment). internal_working = the deep mechanism,
exact not approximated. Reset modes specifically (common error point):
`--soft` = HEAD only. `--mixed` (default) = HEAD + index; working dir
untouched. `--hard` = HEAD + index + working dir. Never say --mixed
touches the working dir, or --soft touches the index.

## Safety rule — non-negotiable
Never say a commit is "deleted"/"disappears"/"gone" after reset or
rebase — the object persists in the object database and is recoverable
via reflog until garbage collected; only the branch pointer stops
referencing it. This applies everywhere, not just when discussing
secrets — but is especially critical there: exposed secrets/credentials
must be rotated regardless of any history rewrite. Any --hard mention
needs a caution word (careful/warning/discard) in the same sentence.

## Real project example rules
industry_context (e.g. "software team") + scenario + problem + solution
+ professional_reasoning. Ground in references/workflows.md, connect to
teamwork/code review/production — not "developer forgot a file." Use
messy commits before a PR or history cleanup before sharing a branch.

## Concept mistakes rules
2-3 entries, distinct levels (beginner/intermediate/professional/
interview), each with wrong_belief, correct_understanding,
professional_tip. Ground in references/mistakes.md, no shaming tone.

## Interview rules
question, why_interviewer_asks, strong_answer (definition + mechanism +
example), weak_answer, 1+ follow_up_question. Ground in references/interview.md.

## Memory anchor + CTA rules
memory_anchor: one short, quotable recap spoken right before the CTA
(e.g. "Reset moves your position. Revert makes a correction."). Then
the CTA — one of: comment-for-a-specific-reward, tag a friend,
save-this-for-later, or follow a NAMED channel (e.g. "Follow
EngineerPath for more"), never a bare "follow for more" with no name.
Banned: any comment-ask with no named reward.

## Storyboard rules — these shots ARE the voice script
There is no separate narration: voice_script is compiled by joining
every shot's `voice` line, one per paragraph. shot[0].voice MUST equal
`hook` word-for-word — not a paraphrase, not the analogy bridge, the
literal hook. The memory_anchor and engagement_cta text must each
appear verbatim as their own shot's voice, at the end. At least 6
shots, ONE self-contained idea per shot's `voice` (never cram HEAD move
+ index change + working-dir change into one line — that's 3 shots),
covering hook -> problem -> analogy -> technical (2+ shots) -> real
example -> memory anchor -> CTA, in that order. No generic visuals
("show logo"). `visual` states WHO's on screen, WHERE, WHAT ACTION —
e.g. "A developer at a laptop; terminal shows commits A-B-C, C
highlighted red." `animation` names the specific motion (e.g. "HEAD
slides backward from C to B"). `camera` says how it's shot (e.g. "Zoom
into the commit history" or "Static wide shot"). EVERY shot also needs
`on_screen_text` (text overlay, e.g. "HEAD moves back") and
`learning_objective` (what this shot teaches) — both required. Full 60s.

## Comparison rule
If the subject is a comparison ("X vs Y") only, populate `comparison`:
why people confuse them, both definitions, one row per required
dimension (Purpose, Main Action, History Impact, When To Use, When Not
To Use, Professional Recommendation — all 6), and a decision_rule.
Otherwise leave `comparison` null.

## Final quality gate
Score yourself 0-10 (whole numbers only, no decimals): technical_accuracy, teaching_quality, hook_strength,
analogy_quality, real_world_relevance, interview_value, shareability. If
technical_accuracy would be below 9, fix the inaccurate section. If
hook_strength or analogy_quality would be below 8, regenerate that
section. Never report a high score to avoid fixing a real problem.
"""


def get_system_prompt(knowledge) -> str:
    """`knowledge` is a content_agents.knowledge.schema.KnowledgeExtract."""
    skill_content = "\n\n".join([
        knowledge.skill_md, knowledge.analogies, knowledge.mistakes,
        knowledge.workflows, knowledge.interview,
    ])
    return f"{skill_content}\n\n{RULES}"
