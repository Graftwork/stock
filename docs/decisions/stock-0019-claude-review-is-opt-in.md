# Stock ADR 0019: The Claude review runs only when the owner adds a label

- **Status:** accepted
- **Date:** 2026-10-21

## Context

`.github/workflows/claude-review.yml` reviewed every pull request when it was
opened, marked ready for review, or pushed to. It runs on the owner's personal
Claude subscription, and the owner is the only person who can spend that
allowance. Four things were seen around `Graftwork/stock` PR #10 (measured
from its check runs, reviews and job log):

- The review took about 11 minutes and posted one valid comment.
- A Markdown-only fix-up push made the review decline ("No reviewable
  changes"), and the gate then failed the check, because the pull request as a
  whole changed a file that is not Markdown. That is the requirement working as
  written, but it means a small docs fix on a pull request with code turns the
  check red.
- Earlier, a run failed in seconds because the owner's allowance was spent.
- CodeRabbit, installed on the organisation, reviewed the same push the Claude
  review declined.

A pull request from a fork gets no secrets, so this review cannot run on one
whatever the trigger is. The check was already advisory, not required.

## Decision

The review runs only when someone adds the `claude-review` label to a pull
request. To review again after a push, remove the label and add it back.

- The trigger is `pull_request: types: [labeled]`. The job runs only for that
  label name, and not for a draft.
- The label name is part of the concurrency key. Adding any other label also
  starts a run, which skips its job, and without the name in the key that run
  would cancel a review already in progress.
- Nothing about the gate step changes, so *A Passing Review Check Means A
  Review Happened* and its tests are untouched. A push after a labelled run
  gets no `review` check on the new commit, which cannot be mistaken for a
  review.

Who can add the label: anyone with triage access. That is the owner, and also
the agent, because the agent's token can write to the GitHub API and the deny
list in `.claude/settings.json` does not cover label writes. The house rule in
`CLAUDE.md` that the agent acts on GitHub only when asked is what stops it. The
label is a gate by rule, not by permission.

## Not measured

- That the action runs when started by a `labeled` event. The gate step reads
  `github.event.pull_request`, which a `labeled` event carries, but this was
  not run. The first code pull request after this merges should be labelled
  and checked: the review should post and `review` should go green. If the run
  skips within seconds, the trigger does not work and this ADR needs
  correcting.
- Whether re-adding the label after a Markdown-only fix-up avoids the red
  check. It may not: the gate still reads the whole pull request's file list.
- The pull request that adds this ADR edits `claude-review.yml`, so the action
  would skip itself on it. It is not labelled, so no `review` check appears.

## Consequences

- A grafted project that copies this workflow gets no review until it adds the
  label to a pull request. Its changelog entry says so.
- The review no longer runs on its own for pull requests that change code.
  CodeRabbit is the automatic reviewer, and the owner asks for the Claude
  review when it is wanted. If CodeRabbit stops reviewing, nothing turns red to
  say so.
- Removing the review altogether (the workflow, its requirement and its tests)
  is a separate, larger change. This one keeps them, so that the gate still
  describes a real review when someone does ask for one.

## Alternatives considered

- **Require the `review` check.** Rejected: it runs on a personal token, cannot
  pass on a fork's pull request, and went red on a legitimate push.
- **`workflow_dispatch` with a pull request number, or an `@claude` comment
  trigger.** Rejected: the first needs the checkout and gate rewritten around a
  number input, and the second changes how the secret is exposed.
- **Remove the review.** Deferred, not rejected: decide after roughly ten pull
  requests have gone by without the label being used.
