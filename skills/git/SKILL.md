---
name: git
description: Domain knowledge for generating educational content about Git — concepts, internals, workflows, interview questions, common mistakes, and analogies.
---

# Git Skill

This skill grounds content-generation agents (reel script, cheat sheet,
interview prep, quiz) in accurate, curated Git knowledge instead of the
model's generic training-data recall.

## Scope

Git as a distributed version control tool: local workflow (staging,
commits, branches), history rewriting (rebase, amend, cherry-pick),
collaboration (remotes, push/pull, merge, PRs), and the object model
underlying all of it.

## Reference files

- `references/concepts.md` — core vocabulary (repo, working directory,
  staging, commit, branch, HEAD, remote, tag). Beginner-level (L1).
- `references/internals.md` — object model, refs, index, reflog, how
  merge/rebase actually work. Developer/professional-level (L2/L3).
- `references/workflows.md` — real workflows (feature branches, rebase
  before PR, cherry-pick, stash, bisect). Ground `real_project_example`
  here — never invent an ungrounded scenario.
- `references/interview.md` — question bank by difficulty with the key
  points a correct answer must hit.
- `references/mistakes.md` — beginner/professional/interview-trap per
  concept.
- `references/analogies.md` — vetted analogies with explicit mapping +
  a banned weak-analogy list. Never generate an analogy not derived from
  this file or built the same way (concrete mapping + justification).
- `references/commands.md` — real command reference; never invent a
  flag or subcommand not listed here.

## Non-negotiable rules for any agent using this skill

1. Never invent a Git command, flag, or behavior not in these references.
   If a claim isn't in the references, mark it as a general pattern, not
   a stated fact — do not fabricate command syntax.
2. Every analogy must include why it fits — a bare comparison
   ("a branch is like a tree branch") is a validation failure.
3. Every mistake set must have all three tiers: beginner, professional,
   interview trap. Two out of three is a validation failure.
4. Interview material must be labeled with the correct difficulty tier —
   don't mislabel an intermediate question as "beginner."
