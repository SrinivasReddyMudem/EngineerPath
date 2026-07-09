# Git Analogies

Rule: every analogy needs a concrete real-world action, a clear mapping
to the technical concept, and an explicit statement of *why* the mapping
holds. A comparison with no "why it fits" is a weak analogy and must be
rejected.

## Branch
Weak (banned): "A branch is like a tree branch."
Strong: "Creating a branch is like duplicating a shared Google Doc into
your own copy before editing — you can experiment freely, and the
original document (main) stays untouched until you decide to bring your
changes back."
Why it fits: a branch and a doc copy both let you diverge from a shared
baseline without risk, and both require a deliberate action (merge / copy
changes back) to rejoin.

## Commit
Strong: "A commit is like taking a labeled photograph of your entire
project at one moment — you can always jump back to look at exactly
that photo later, and the label (commit message) tells you why it was
taken."
Why it fits: a photograph is a full snapshot, not a diff, just like a
commit's tree points to the complete state of every file, not just what
changed — the "diff view" you usually see is a derived comparison, not
what's actually stored.

## Rebase
Strong: "Rebase is like re-recording your part of a podcast after the
host re-recorded their intro — you replay your same lines, but now they
follow a different, updated beginning, so the final episode sounds
seamless instead of stitched together."
Why it fits: the content (words/diff) is the same, but re-recording after
a new intro changes the recording itself (the commit hash), exactly like
rebase changing a commit's parent changes its hash even though the diff
is identical.

## Merge
Strong: "Merging is like two co-authors combining their separately edited
chapters into one book, keeping a note of exactly which chapters each
person wrote and when."
Why it fits: a merge commit has two parents and preserves both
histories exactly as they happened — nothing is replayed or hidden,
unlike rebase.

## Staging area (index)
Strong: "The staging area is like a shopping cart — adding an item
(`git add`) doesn't buy it yet; checkout (`git commit`) is the moment it
becomes final."
Why it fits: both are an intermediate holding state you can freely
adjust (add/remove items or files) before committing to the final
action.

## Stash
Strong: "Stash is like putting your current desk papers into a drawer
before a surprise meeting, so your desk (working directory) is clear —
you take them back out exactly as they were when the meeting ends."
Why it fits: both preserve incomplete work exactly as-is, out of the way,
without discarding or finalizing it.

## Reflog
Strong: "The reflog is like your browser history for HEAD — even if a
bookmark (branch) gets deleted or moved, you can still find where you
were by scrolling back through history."
Why it fits: both are a chronological local log of positions visited,
independent of whether the thing you were pointing at is still
"officially" reachable.

## Remote / origin
Strong: "A remote is like a shared drive folder that mirrors your local
project — nothing syncs automatically; you explicitly upload (push) or
download (pull) changes."
Why it fits: both require an explicit sync action, and both can drift
out of sync with your local copy until you do.

## Cherry-pick
Strong: "Cherry-picking a commit is like copying one specific paragraph
from a friend's document into yours, instead of merging their entire
document in."
Why it fits: both take exactly one discrete unit of content across,
leaving everything else in the source untouched — unlike a merge, which
brings the whole history across.

## Reset vs revert
Strong: "`git reset --hard` is like tearing pages out of a notebook —
they're gone from that copy; `git revert` is like writing a new page
that says 'ignore what page 12 said', leaving page 12 intact for the
record."
Why it fits: reset actually removes/rewrites history from that point on
(destructive to that branch's record), while revert adds new history
that cancels an old change without deleting the original entry — exactly
matching why revert is the safe choice on shared branches.

## Tag
Strong: "A tag is like a bookmark stuck at a specific page of a book —
it stays there even as you keep writing new pages (commits); a branch is
like your current reading position, which moves forward as you read."
Why it fits: a tag is fixed to one commit forever, while a branch
pointer moves automatically with each new commit — the exact technical
distinction being taught.

## Banned weak analogies (do not use)
- "A branch is like a tree branch" (circular — restates the name, no
  new mapping).
- "Git is like a save button" (too vague — doesn't distinguish commit
  from staging from working directory).
- "Merge is like mixing two colors of paint" (implies information loss/
  blending, which is the opposite of how merge preserves both histories
  discretely).
