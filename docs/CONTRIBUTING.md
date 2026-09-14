# Contributing to Stock

Most work against `Graftwork/stock` happens from inside a grafted project's
own Claude Code session — which usually cannot reach `Graftwork/stock`
directly, since a session's GitHub access is scoped to one repository owner
at a time (see "Why this shape" below). This file is about that specific
path: routing a change back to Stock from a same-owner fork, and why each
step is there.

## Branch names

Every branch names its route before the PR is opened — see
[`WORKFLOW.md`'s "Branch names match the route"](../WORKFLOW.md#branch-names-match-the-route).
That applies here unchanged, whether the branch lives in `Graftwork/stock`
directly or in a fork.

## Contributing from a same-owner fork

A Claude Code cloud session's GitHub access is scoped to one owner tier at a
time — a session already sourced from your own repositories cannot also add
`Graftwork/stock`, since it belongs to a different owner. Forking Stock into
your own account or org gives such a session somewhere it *can* reach, so it
can still push a branch and open a PR — just not directly against
`Graftwork/stock`.

1. **The session works on a branch inside the fork**, named per the
   convention above.
2. **Don't merge that branch into the fork's own `main`.** Keep `main` an
   untouched mirror of `Graftwork/stock:main`. GitHub's "Sync fork" only
   fast-forwards cleanly when `main` carries no commits of its own —
   merging into it directly breaks that for every sync afterward, not just
   this one.
3. **Open the pull request against `Graftwork/stock` directly from that
   branch** — not via the fork's own "Contribute" banner, which always
   compares default branches and would use `main` as the head, losing both
   the branch name and the untouched-mirror property in one step. On
   `github.com/Graftwork/stock`: "New pull request" → "compare across
   forks" → pick the fork and the feature branch as head.
4. **This step needs a person, in their own browser.** The session that did
   the work cannot open this PR itself — its GitHub access doesn't extend
   to `Graftwork/stock`, regardless of the fork relationship.
5. **Once merged** (Stock squash-merges every PR into a single commit),
   click "Sync fork" on the fork to fast-forward `main`. Clean, since `main`
   was never touched directly in step 2.

## Why this shape

Two failures forced this, not preference:

- A session scoped to a fork genuinely cannot open a PR against
  `Graftwork/stock` — confirmed directly, not assumed: attempting to add a
  different-owner repo to an already-scoped session returns a hard "cross-tier
  adds are not supported" error, not a permissions prompt to click through.
- Merging a branch into the fork's `main` before contributing upstream is
  the standard-looking move, but it silently costs the fork its clean
  "Sync fork" going forward — the divergence doesn't undo itself once
  `Graftwork/stock` merges the PR.

Skipping the intermediate merge avoids both: the branch alone is enough to
open the cross-fork PR, and `main` never has anything to recover from.
