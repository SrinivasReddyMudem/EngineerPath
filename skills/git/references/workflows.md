# Git Workflows (for real_project_example fields)

## Feature branch + rebase before PR
Scenario: multiple developers on one service, each on their own feature
branch off `main`.
Problem: by the time a feature branch is ready to merge, `main` has moved
forward. A plain merge creates a merge commit and interleaves the
feature's commits with unrelated ones in `git log`, making review and
`git bisect` harder.
Solution: `git rebase main` on the feature branch before opening the PR
— replays the feature's commits on top of the latest `main`, producing
a linear history.
Why professionals use it: linear history makes `git log --oneline`,
`git blame`, and `git bisect` far easier to read; the PR diff shows only
the feature's actual changes.

## Interactive rebase to clean up commits before review
Scenario: a feature branch has commits like "wip", "fix typo", "actually
fix it", "address review comment".
Problem: noisy history makes it hard for reviewers to understand intent,
and for future engineers doing `git blame` to find the real reasoning.
Solution: `git rebase -i` before opening/updating the PR, squashing
fixups into the commit they belong to and rewriting messages.
Why professionals use it: each commit becomes a reviewable, revertable
unit of work instead of an arbitrary save point.

## Cherry-pick for backporting a fix
Scenario: a critical bug fix lands on `main`, but a `release/2.3` branch
also needs it and can't take all of `main`'s other changes.
Problem: merging all of `main` into the release branch would pull in
unreleased features.
Solution: `git cherry-pick <sha>` applies just that one commit's diff
onto the release branch as a new commit.
Why professionals use it: isolates exactly one change without merging
unrelated history.

## Stash for interrupting in-progress work
Scenario: mid-way through a change, an urgent production bug needs a
hotfix on a clean `main`.
Problem: the working directory has uncommitted changes that aren't ready
to commit but block switching branches cleanly.
Solution: `git stash` saves the dirty working state and reverts to a
clean tree; `git stash pop` restores it later.
Why professionals use it: lets you switch context without committing
half-finished work or losing it.

## Bisect for finding a regression
Scenario: a test that passed last month now fails, across hundreds of
commits.
Problem: manually checking every commit is too slow.
Solution: `git bisect start`, mark a known-good and known-bad commit,
then `git bisect run <test-command>` — Git binary-searches the commit
range automatically.
Why professionals use it: turns an O(n) manual search into O(log n),
and automates it entirely if the failure is scriptable.

## Rebase vs merge — the actual team decision
Merge preserves true history (what actually happened, including when
branches diverged) and is non-destructive — safe on shared/public
branches. Rebase produces cleaner, linear history but rewrites commit
hashes — unsafe on a branch others have already pulled from. Common team
rule: rebase your own feature branch freely before it's shared; never
rebase a branch other people have already pulled.
