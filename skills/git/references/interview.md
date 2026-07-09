# Git Interview Question Bank

Each question lists the key points a correct answer must hit — agents
must use these points, not invent unrelated criteria.

## Beginner
- "What is Git?" → distributed version control; tracks history locally
  (not just on a server); every clone is a full copy of history.
- "What is the difference between `git add` and `git commit`?" → add
  stages changes into the index; commit snapshots the index into
  permanent history with a message.
- "What is a branch?" → a movable pointer to a commit, not a copy of
  the project; cheap to create.
- "What does `git clone` do?" → copies the entire repository including
  full history, not just the current file snapshot.

## Intermediate
- "Merge vs rebase — what's the actual difference?" → merge creates a
  merge commit with two parents and preserves both histories as-is;
  rebase replays commits onto a new base, creating new commits with new
  hashes, producing linear history but rewriting it.
- "What happens on a merge conflict?" → Git's three-way diff can't
  auto-resolve overlapping line changes between the two branches and
  the common ancestor; requires manual resolution before the merge/
  rebase can complete.
- "What is `HEAD`?" → pointer to the currently checked-out commit,
  normally via a branch (symbolic ref); can be "detached" if pointing
  directly at a commit.
- "What's the difference between `git fetch` and `git pull`?" → fetch
  downloads remote refs/objects without touching your working branch;
  pull is fetch + merge (or rebase, with `--rebase`) into your current
  branch.

- "What's the difference between `git reset` and `git revert`?" → reset
  moves the branch pointer (and optionally index/working dir), rewriting
  history from that point forward — unsafe on shared branches; revert
  creates a new commit that inverses a past change without touching
  existing history — safe on shared branches.
- "Why doesn't `git push` upload tags by default?" → tags are a separate
  ref namespace from branches; Git treats them as opt-in to push,
  requiring `git push origin <tag>` or `--tags`, to avoid accidentally
  publishing local-only markers.

## Advanced
- "Why does the commit hash change after a rebase, even if the diff is
  identical?" → the hash is computed from content + parent commit +
  author + timestamp; rebase changes the parent, so the hash changes
  even though the tree/diff content is the same.
- "How would you recover a commit lost after a bad `git reset --hard`?"
  → `git reflog` to find the SHA the branch pointed to before the reset,
  then `git reset --hard <sha>` (or `git cherry-pick`/`git branch` from
  that SHA) to recover it; works because the commit object still exists
  until garbage collected.
- "What's the difference between `git reset --soft`, `--mixed`, and
  `--hard`?" → soft moves HEAD/branch only (keeps index + working dir);
  mixed also resets the index (keeps working dir changes unstaged);
  hard resets index and working directory too (discards uncommitted
  changes).
- "How does `git bisect` work internally?" → binary search over the
  commit range between a known-good and known-bad commit, checking out
  the midpoint and asking you (or a script) to mark it good/bad, halving
  the search space each iteration.

## Expert
- "How do you handle a rebase conflict across a team-shared branch
  safely?" → correct answer notes you generally shouldn't rebase a
  branch others have pulled from at all; if it must happen (e.g. cleanup
  before a release), it requires explicit team coordination, force-push
  with lease, and everyone re-basing their local copies rather than
  merging the old remote state back in.
- "Explain what a force-push with `--force-with-lease` protects against
  that plain `--force` doesn't." → `--force-with-lease` refuses the push
  if the remote branch has moved since your last fetch, preventing you
  from silently overwriting a teammate's commit you haven't even seen
  yet; plain `--force` overwrites unconditionally.
- "How would you design a Git workflow for a large team to keep history
  both clean and safe?" → correct answer covers: rebase-only on personal
  feature branches, merge (not rebase) for integrating into shared/
  release branches, protected branch rules disallowing force-push to
  `main`, and squash-merge at PR time as an alternative that avoids
  rebase risk entirely while still keeping `main` linear.
- "Why can `git filter-branch` / history rewriting break collaborators'
  repositories, and what's the safer modern alternative?" → rewriting
  published history changes commit hashes for every affected commit,
  breaking every clone's shared ancestry, forcing everyone to re-clone
  or carefully re-base; `git filter-repo` is the maintained, faster,
  safer replacement recommended by the Git project itself.
