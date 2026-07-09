---
name: git
description: Domain knowledge for generating educational content about Git — concepts, internals, workflows, interview questions, common mistakes, and analogies.
---

# Git Skill

This skill grounds content-generation agents (reel script, cheat sheet,
interview prep, quiz) in accurate, curated Git knowledge instead of the
model's generic training-data recall.

## Scope

Covers Git as a distributed version control tool: local workflow (staging,
commits, branches), history rewriting (rebase, amend, cherry-pick),
collaboration (remotes, push/pull, merge, pull requests), and the object
model that underlies all of it.

## Reference files

- `references/concepts.md` — core vocabulary: repo, working directory,
  staging area, commit, branch, HEAD, remote, tag. Use for beginner-level
  explanations (Level 1).
- `references/internals.md` — object model (blob/tree/commit/tag), refs,
  the index, reflog, how merge and rebase actually work under the hood.
  Use for developer/professional-level explanations (Level 2/3).
- `references/workflows.md` — real workflows: feature branches, rebase
  before PR, interactive rebase, cherry-pick, stash, bisect. Use for
  `real_project_example` fields — never invent a scenario not grounded here.
- `references/interview.md` — question bank by difficulty (beginner /
  intermediate / advanced / expert) with the key points a correct answer
  must hit. Use for `interview_question` fields and the Interview Prep agent.
- `references/mistakes.md` — beginner mistake / professional mistake /
  interview trap, organized per concept. Use for `common_mistakes` fields.
- `references/analogies.md` — vetted strong analogies with an explicit
  "why it fits" mapping, and a list of banned weak analogies. Use for
  `analogy` fields — never generate an analogy not derived from this file
  or built the same way (concrete mapping + justification).

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
