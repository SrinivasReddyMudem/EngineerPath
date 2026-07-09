# Git Concepts (Level 1 — beginner)

## Repository
A folder tracked by Git. Contains a hidden `.git` directory holding the
entire history. Created with `git init` or obtained with `git clone`.

## Working directory
The actual files on disk that you edit. Git compares this against the
staging area and the last commit to compute what changed.

## Staging area (the index)
A holding area between the working directory and a commit. `git add`
moves changes here. Lets you build a commit from part of your changes,
not everything you touched.

## Commit
A saved snapshot of the staged changes, with a message, author, timestamp,
and a pointer to the previous commit (its parent). Identified by a SHA
hash. Commits are immutable — "editing" a commit actually creates a new one.

## Branch
A movable pointer to a commit. `main`/`master` is just a branch name by
convention, not special to Git. Creating a branch is cheap (a 41-byte
file) — it does not copy the project.

## HEAD
A pointer to whichever commit/branch you currently have checked out.
Normally HEAD points to a branch, which points to a commit. In "detached
HEAD" state, HEAD points directly to a commit instead of a branch.

## Remote
A named reference to another copy of the repository, usually on a server
(e.g. `origin`). `git push`/`git pull` sync commits between local and
remote. A remote is not automatically kept in sync — you fetch/pull
explicitly.

## Tag
A pointer to a specific commit that, unlike a branch, does not move.
Used to mark releases (e.g. `v1.2.0`).

## Merge conflict
Happens when Git cannot automatically reconcile changes to the same lines
of a file from two different histories. Requires a human to pick the
correct result before the merge/rebase can complete.
