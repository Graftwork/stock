# Stock ADR 0019: The Claude review runs only when the owner adds a label

- **Status:** accepted
- **Date:** 2026-10-21

## Context

`.github/workflows/claude-review.yml` reviewed every pull request when it was
opened, marked ready for review, or pushed to. It runs on the owner's personal
Claude subscription, and the owner is the only person who can spend that
allowance. Four things were seen (measured, from check runs, reviews and job
logs; the first, second and fourth on `Graftwork/stock` PR #10):

- The review took about 11 minutes and posted one valid comment.
- A Markdown-only fix-up push made the review decline ("No reviewable
  changes"), and the gate then failed the check, because the pull request as a
  whole changed a file that is not Markdown (an `.openspec.yaml`; the pull
  request had no code). The decline comment described the whole pull request,
  not just the push. That is the requirement working as written. It means a
  small docs fix on any pull request that includes a non-Markdown file turns
  the check red. Whether that also happens on a pull request with code is
  derived, not measured.
- On PR #8's branch on 2026-10-14, a run failed within seconds (the action step
  took 23 seconds). The owner said it was the allowance; the log could not be
  read (HTTP 503), so the cause is the owner's report, not confirmed.
- CodeRabbit, installed on the organisation, reviewed the earlier push of PR #10
  (one comment). On the fix-up push it processed the commit but reviewed
  nothing: its summary says three files were "skipped from review as they are
  similar to previous changes" and "No actionable comments were generated".

By default a pull request from a fork of a public repository gets no secrets,
so this review cannot run on one whatever the trigger is. A private graft that
turns on GitHub's setting to send secrets to fork workflows would change that.
The check was already advisory, not required.

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
  starts no run, so the new commit has no `review` check.
- Adding any other label still starts a run, whose job is skipped. That leaves
  a skipped `review` entry on the head commit. GitHub's checks API lists a
  skipped run beside an earlier run of the same name (seen on PR #10 for the
  session-link checks), but how the pull request page orders them was not
  tested, so an unrelated label might hide an earlier red `review`.
- A draft pull request is skipped and keeps the label, and nothing starts when
  it is marked ready, so remove the label and add it again. "Re-run jobs"
  replays the original event, so it reviews the commit the label was added
  at; removing and re-adding the label does not have that problem.

Who can add the label: anyone with triage access. Who can get a review from it:
only someone with write or admin access, because the pinned action (`v1.0.207`,
`src/github/validation/permissions.ts`, read in the source) accepts only those
levels for the person whose action started the run and otherwise refuses to
run, so a triage-only user's label would make the gate fail (derived from the
gate's code, not run). In practice that is the owner, and possibly the agent. The deny list in `.claude/settings.json` blocks
`gh pr edit`, the usual way to add a label, but not `gh api`, `gh issue edit`
or possibly `mcp__github__issue_write` (recalled, not tested). The house rule
in `CLAUDE.md` that the agent acts on GitHub only when asked is what stops it.
The label is a gate by rule, not by permission.

## Not measured

- That the action runs when started by a `labeled` event. The gate step reads
  `github.event.pull_request`, which a `labeled` event carries, but this was
  not run. All 16 earlier runs came from the old triggers. The first code pull
  request after this merges should be labelled and checked: the review should
  post and `review` should go green. A job that skips within seconds only
  means the wrong label or a draft. If the action ignores a `labeled` event,
  the job does not skip: the gate fails within seconds with "no execution
  file" or "posted nothing", and this ADR needs correcting.
- Whether re-adding the label after a Markdown-only fix-up avoids the red
  check. It may not: the gate still reads the whole pull request's file list.
- The pull request that adds this ADR edits `claude-review.yml`, so the action
  would skip itself on it. It is not labelled, so no `review` check appears.

## Consequences

- A grafted project that copies this workflow gets no review until it adds the
  label to a pull request. Its changelog entry says so.
- The review no longer runs on its own for pull requests that change code.
  CodeRabbit reviews automatically, though on a push it judges similar to
  earlier changes it skips files, and the owner asks for the Claude review when
  it is wanted. If CodeRabbit stops reviewing, nothing turns red to say so.
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
