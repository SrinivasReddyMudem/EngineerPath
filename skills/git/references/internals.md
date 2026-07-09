# Git Internals (Level 2/3 — developer / professional)

## The object model
Git stores everything as one of four object types in `.git/objects`,
each addressed by the SHA hash of its content:

- **blob** — raw file content (no filename, no metadata).
- **tree** — a directory listing: maps names to blob/tree hashes and
  file modes. A commit's tree is a full snapshot of the repo at that point.
- **commit** — pointer to one tree, pointer(s) to parent commit(s),
  author, committer, timestamp, message.
- **tag** (annotated) — pointer to a commit plus tagger info and message.

Because objects are content-addressed, identical file content anywhere
in history is stored once. This is why commits are cheap and why the
same blob hash can appear under many commits.

## Refs
A ref is just a file (or packed-refs entry) containing a commit SHA.
`refs/heads/<branch>` = local branches, `refs/remotes/<remote>/<branch>`
= remote-tracking branches, `refs/tags/<tag>` = tags. `HEAD` is a ref
that usually contains `ref: refs/heads/<branch>` (symbolic ref).

## The reflog
A local, per-repo log of where HEAD and branch refs have pointed,
kept independently of the object graph. Survives even after a commit
becomes unreachable from any branch (e.g. after a bad reset or rebase).
`git reflog` + `git reset --hard <sha>` is the standard recovery path
when history rewriting goes wrong. Reflog entries expire (default 90
days for reachable, 30 for unreachable) — it is not permanent.

## How merge actually works
A merge commit has two parents. Git finds the common ancestor (merge
base) of the two branch tips, then does a three-way diff: base vs branch
A, base vs branch B. Non-overlapping changes combine automatically;
overlapping line ranges become a conflict requiring manual resolution.
History is preserved exactly as it happened — both branches' commits stay.

## How rebase actually works
Rebase does NOT move commits — it creates new commits with the same
diff/message but a new parent, then moves the branch pointer to the new
chain. This is why commit hashes change after rebase: the hash is a
function of the content, parent, author, and timestamp — changing the
parent changes the hash even if the diff is identical. The original
commits still exist (reachable via reflog) until garbage collected.
Interactive rebase (`git rebase -i`) replays commits one at a time,
letting you reorder, squash, edit, or drop them individually.

## The index in more detail
The staging area is a binary file (`.git/index`) listing every tracked
path with its blob hash, mode, and stat cache. `git add` updates entries
here; `git commit` turns the index into a tree object. This is why
`git add -p` can stage part of a file's changes — the index operates
at content granularity, not file granularity.

## Why force-push is dangerous
`git push --force` overwrites the remote branch ref to match your local
history unconditionally, discarding any commits on the remote that
aren't in your local history — including work colleagues pushed after
you last fetched. `git push --force-with-lease` refuses if the remote
moved since your last fetch, which is why teams prefer it as the default.
