# Git Mistakes (beginner / professional / interview trap)

Each entry has all three tiers — an agent must not drop any tier.

## Rebase
- Beginner mistake: runs `git rebase` on a branch teammates already
  pulled, then force-pushes, breaking everyone else's local history.
- Professional mistake: rebases a long-lived shared branch instead of
  only personal feature branches, causing duplicate commits when others
  merge instead of rebase.
- Interview trap: says "rebase and merge do the same thing to the final
  code" — true for the resulting file content, false for history shape,
  commit hashes, and safety on shared branches.

## Force push
- Beginner mistake: uses `git push --force` to "fix" a rejected push
  without checking what it will overwrite on the remote.
- Professional mistake: doesn't standardize on `--force-with-lease`
  team-wide, so a plain `--force` from one person occasionally erases
  a teammate's just-pushed commit.
- Interview trap: claims force-push is "never safe" — it's safe and
  routine on your own not-yet-shared feature branch; the risk is specific
  to branches others have already pulled.

## Merge conflicts
- Beginner mistake: resolves a conflict by keeping "my side" or "their
  side" wholesale without reading what actually changed, silently
  dropping a teammate's fix.
- Professional mistake: resolves a large conflict without re-running
  tests afterward, assuming a clean merge marker means correct code.
- Interview trap: says a conflict means "Git is broken" — a conflict
  is Git correctly refusing to guess between two edits to the same lines.

## .gitignore
- Beginner mistake: adds a rule to `.gitignore` for a file that's already
  tracked — Git keeps tracking it because `.gitignore` only affects
  untracked files.
- Professional mistake: commits environment-specific or secret files
  (`.env`, IDE configs) early in a project's life, then `.gitignore`
  can't retroactively remove them from history.
- Interview trap: asked "how do you stop tracking a file already
  committed" and answers only "add to .gitignore" — the real answer
  needs `git rm --cached`.

## Detached HEAD
- Beginner mistake: checks out a specific commit directly (not a branch),
  makes commits, then switches branches and "loses" the work — it isn't
  lost, but it's unreachable from any branch until recovered via reflog.
- Professional mistake: doesn't create a branch immediately upon
  realizing they're in detached HEAD with work worth keeping.
- Interview trap: says detached HEAD commits are deleted immediately —
  they remain in the object database and reflog until garbage collected.

## Reset vs revert
- Beginner mistake: uses `git reset --hard` to "undo" a commit that's
  already been pushed and pulled by others, then force-pushes — erasing
  it from everyone's history instead of properly undoing it.
- Professional mistake: reaches for `git reset` on a shared branch out
  of habit instead of `git revert`, which is the safe choice because it
  adds a new undo commit rather than rewriting history others depend on.
- Interview trap: says "reset and revert do the same thing" — reset
  moves the branch pointer (rewriting history from that point forward);
  revert adds a brand-new commit that inverses a past change, keeping
  the original commit intact.

## Tags
- Beginner mistake: assumes `git push` uploads tags automatically —
  it doesn't; tags need `git push origin <tag>` or `--tags` explicitly.
- Professional mistake: uses lightweight tags for releases instead of
  annotated tags, losing tagger identity, date, and message metadata
  that release tooling and audits often expect.
- Interview trap: says a tag is "just another branch" — a tag doesn't
  move as new commits are added; a branch does.

## Commit hygiene
- Beginner mistake: one giant commit per day covering many unrelated
  changes, making review and revert impossible at fine granularity.
- Professional mistake: squashes an entire feature into one commit that
  mixes an unrelated refactor with the actual feature, making future
  `git revert` or `git blame` less precise.
- Interview trap: asked why atomic commits matter and only mentions
  "cleaner history" without mentioning `git bisect` and `git revert`
  granularity as the concrete engineering payoff.
