# Git Command Reference (for cheat sheet / quiz grounding)

Real commands only — every agent must draw from this list, never invent
flags or subcommands not listed here.

## Setup & inspection
- `git init` — create a new repo in the current directory.
- `git clone <url>` — copy a remote repo including full history.
- `git status` — show staged/unstaged/untracked changes.
- `git log --oneline --graph` — compact commit history with branch shape.
- `git diff` — unstaged changes vs the index. `git diff --staged` — staged
  changes vs last commit.
- `git show <sha>` — full diff and metadata for one commit.
- `git blame <file>` — which commit last touched each line.

## Staging & committing
- `git add <file>` / `git add -p` — stage a file / stage interactively
  by hunk.
- `git commit -m "msg"` — commit staged changes.
- `git commit --amend` — replace the last commit (new hash) with staged
  changes added/message changed. Never amend a commit already pushed
  and pulled by others.
- `git rm --cached <file>` — stop tracking a file without deleting it
  from disk (the actual fix for "already-committed file in .gitignore").

## Branching & switching
- `git branch <name>` — create a branch (doesn't switch to it).
- `git switch <name>` / `git checkout <name>` — switch to a branch.
- `git switch -c <name>` / `git checkout -b <name>` — create and switch
  in one step.
- `git branch -d <name>` — delete a merged branch (safe). `-D` forces
  deletion even if unmerged.

## Merging & rebasing
- `git merge <branch>` — merge another branch into the current one,
  creating a merge commit if histories diverged.
- `git rebase <branch>` — replay current branch's commits onto the tip
  of `<branch>`, producing new commit hashes.
- `git rebase -i <base>` — interactive rebase: reorder, squash, edit,
  or drop commits since `<base>`.
- `git cherry-pick <sha>` — apply one specific commit's diff onto the
  current branch as a new commit.

## Undoing changes
- `git restore <file>` — discard unstaged changes to a file.
- `git restore --staged <file>` — unstage a file (keeps working dir
  changes).
- `git reset --soft <sha>` — move branch pointer only; index and working
  dir unchanged.
- `git reset --mixed <sha>` (default) — move branch pointer + reset
  index; working dir unchanged (changes become unstaged).
- `git reset --hard <sha>` — move branch pointer + reset index + working
  dir. Discards uncommitted changes — irreversible for those changes.
- `git revert <sha>` — create a NEW commit that undoes `<sha>`'s changes,
  without rewriting history. Safe on shared/public branches, unlike reset.

## Stashing
- `git stash` — save uncommitted changes and clean the working directory.
- `git stash pop` — reapply the most recent stash and remove it from the
  stash list. `git stash apply` reapplies without removing it.

## Remotes & syncing
- `git remote add origin <url>` — register a remote named `origin`.
- `git fetch` — download remote refs/objects without touching your
  working branch.
- `git pull` — fetch + merge (or `--rebase` for fetch + rebase) into
  the current branch.
- `git push` — upload local commits to the remote branch.
- `git push --force-with-lease` — force-push that aborts if the remote
  moved since your last fetch (safer than plain `--force`).

## Tags
- `git tag v1.0.0` — lightweight tag: just a name pointing at a commit.
- `git tag -a v1.0.0 -m "msg"` — annotated tag: includes tagger, date,
  message — the recommended kind for releases.
- `git push origin v1.0.0` — tags are not pushed by `git push` alone;
  they must be pushed explicitly (or with `--tags` for all of them).

## History search
- `git bisect start` / `git bisect good <sha>` / `git bisect bad <sha>`
  — binary-search commit history for a regression.
- `git bisect run <script>` — automate bisect against a script that
  exits nonzero on failure.

## Config & ignore
- `git config --global user.name "..."` / `user.email "..."` — required
  identity for commits.
- `.gitignore` — patterns for untracked files Git should not track.
  Only affects untracked files — see `git rm --cached` above for files
  already tracked.

## Hooks & submodules (brief — advanced/expert level)
- Git hooks (`.git/hooks/pre-commit`, `pre-push`, etc.) — local scripts
  Git runs automatically at specific points; used for linting/tests
  before a commit or push. Not copied by clone — each clone must set
  its own hooks (or use a shared hooks path via `core.hooksPath`).
- `git submodule add <url> <path>` — embeds another repo at a fixed
  commit inside this one. Submodules pin an exact commit, not a branch
  — updating requires an explicit `git submodule update --remote`.
