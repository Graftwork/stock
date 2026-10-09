# Stock ADR 0018: The owner opens, accepts and watches; the agent makes and pushes

- **Status:** accepted
- **Date:** 2026-10-08

## Context

Two things went wrong while this repository was being rebuilt and published.

- **The pull request footer outlives its removal.** The GitHub tool a Claude
  Code cloud session uses appends a footer linking the coding session to every
  pull request body it creates, whatever the body says. Stock's answer was to
  edit the footer out once the pull request was open. But GitHub keeps every
  version of an edited description, and anyone who can see the repository can
  open them. All six pull requests the agent opened here carried the footer in
  their first version, and the owner deleted those revisions by hand once the
  repository was public. The owner reports doing the same on four
  `sorting-office` pull requests.
- **The environment's defaults run the other way.** The cloud environment
  tells the agent to offer to watch its pull requests, subscribe to their
  activity, schedule check-ins and drive its own pull requests to green.
  Following that, an agent merged a pull request the owner had not checked.
  Here the owner is the checker, and the owner is also the bottleneck: watching
  only spends effort waiting on them.

## Decision

The owner opens, accepts and watches; the agent makes and pushes.

1. The agent pushes a branch and gives the owner the pull request's title and
   body. The owner opens it from GitHub's compare page. A pull request a person
   opens there gets no footer.
2. Merging, approving, auto-merge, deleting branches, visibility, renames and
   repository settings are the owner's. The agent closes a throwaway pull
   request only when asked.
3. The agent does not watch: no pull request subscriptions, check-ins,
   reminders, routines, triggers or webhooks. The owner reports back when
   something is done.
4. The agent acts on GitHub only when asked, and only for the thing asked.

`CLAUDE.md` carries this as a house rule, which overrides the environment's
defaults. `.claude/settings.json` also denies the tools that would break it, so
the rule does not rest on the agent remembering it:
`mcp__github__create_pull_request`, `mcp__github__merge_pull_request`,
`mcp__github__enable_pr_auto_merge`, `mcp__github__pull_request_review_write`,
`mcp__claude-code-remote__subscribe_pr_activity`,
`mcp__claude-code-remote__send_later`,
`mcp__claude-code-remote__create_trigger`,
`mcp__claude-code-remote__watch_url` and `mcp__github__update_pull_request`;
deleting a branch with `git push --delete` or `-d`; `gh pr create`, `merge`
and `review`; and the local scheduling tools `CronCreate` and
`ScheduleWakeup`. The `main` ruleset already blocks deleting `main`, but not
other branches, such as one an open pull request depends on.

**What was measured about the deny list.** In a Claude Code cloud session on
2026-10-08, a deny rule naming `mcp__github__get_me` was added to a local
settings file, `.claude/settings.local.json`. The call already in flight
completed, and the tool was then removed from the session ("Denied by a
permission rule"). The same happened for
`mcp__claude-code-remote__list_environments`, a tool from the cloud
platform's own server. Removing the rule restored both. `mcp__github__update_pull_request` was
removed the same way. Rules for `git push --delete` and `git push -d` refused
`git push --dry-run origin --delete <branch>` and its `-d` form, while
`git push --dry-run origin <branch>` still ran. This matches Claude
Code's permissions documentation: a deny rule that names a whole tool removes
it from the session, from the next tool call when added mid-session.

**Not measured:** the other names one by one, including the `gh pr` rules,
which rely on the same matching as the `git push` ones; and a deny rule in
the committed `.claude/settings.json`, as opposed to the local file, applying
from the start of a cloud session. The first session after this merges should
check that `mcp__github__create_pull_request` is not available, and report.
`CronCreate` and `ScheduleWakeup` could still be loaded after their deny rules
were added. Whether the rule blocks them when called was not tested, because
testing it means scheduling something if it fails. Treat those two rules as
unverified.

**Not covered by the deny list:** deleting a branch by pushing an empty
refspec (`git push origin :branch`; a rule ending in `:*` would match every
push), commands run with `git -C <path>`, the GitHub API reached by other
means, and issue or comment writes. These rest on the house rule alone.

## Consequences

- The owner opens each pull request: one extra click, from a page the agent
  links to.
- The agent cannot correct a pull request body after it is open. It hands over
  the final text instead.
- CI results and review comments do not wake the agent. The owner says when
  to look.
- `foundation`'s *Coding Session Links Are Not Disclosed* still says a
  tool-appended link "is removed by editing the body once it is posted". That
  is no longer the remedy. The spec is written only by archiving an OpenSpec
  change, so correcting it is a separate change.

## Alternatives considered

- **Keep opening pull requests through the tool and delete the footer revision
  each time.** Rejected: the link is public from the moment the pull request
  opens until a person deletes the revision, and every pull request needs that
  manual step.
- **Rely on the `session-links` workflow to strip the footer.** Rejected for
  the same reason: stripping it is an edit, and the original stays in the
  history.
