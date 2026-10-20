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
  open them. The owner found the footer in the edit history of all six Stock
  pull requests the agent opened, when deleting those revisions by hand once
  the repository was public. The agent can vouch for only two of the six: it
  read the body of #1 and #3 before editing them and saw the footer on both;
  it edited the other four before reading them. An earlier version of this
  record said the agent saw it on five; that was wrong. The owner reports
  doing the same on four `sorting-office` pull requests.
- **Re-checked on 2026-10-14**, by opening a draft pull request in a private
  repository: the footer was still appended after the last line of the body as
  written. Re-checked the same day through the REST API with `gh`
  (`gh api -X POST repos/<owner>/<repo>/pulls`): the footer was appended there
  too, so it comes from the session's network layer, not from one tool.
- **Pull requests, counted again on 2026-10-20: 8 of 8 read carried the
  footer.** Two on Stock, two on `stock-archive` (one made through the REST
  API) and four on `sorting-office`, where a separate session read them.
- **Issues are different, measured on 2026-10-20 and only for creating one.**
  Two issues created with the GitHub tool, one in `stock-archive` and one in
  `sorting-office`, came back with the body unchanged (2 of 2). The
  `sorting-office` one had `created_at` equal to `updated_at`, so nothing
  edited it after creation. One issue created through the REST API (`gh api`)
  got a generic `claude.ai/code` footer with no session id (1 of 1). Not
  tested: issue comments, edits to issues, and other repositories. These
  samples are small. They support narrowing this rule to pull requests; they
  do not show that an issue can never carry a session link.
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
deleting a branch with `git push --delete` or `-d`; `gh pr create`, `edit`,
`merge` and `review`; and the local scheduling tools `CronCreate` and
`ScheduleWakeup`, and `RemoteTrigger`, which creates routines and webhook
triggers. The `main` ruleset already blocks deleting `main`, but not
other branches, such as one an open pull request depends on.

**What was measured about the deny list.** In a Claude Code cloud session on
2026-10-08, a deny rule naming `mcp__github__get_me` was added to a local
settings file, `.claude/settings.local.json`. The call already in flight
completed, and the tool was then removed from the session ("Denied by a
permission rule"). The same happened for
`mcp__claude-code-remote__list_environments`, a tool from the cloud
platform's own server. Removing the rule restored both.
`mcp__github__update_pull_request` was removed the same way. Rules for `git push --delete` and `git push -d` refused
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
unverified. `RemoteTrigger` was not offered in that session, so its rule is
untested too; in a session without the tool, a deny rule naming it may raise
a one-line unknown-tool warning at startup.

**Not covered by the deny list:** deleting a branch by pushing an empty
refspec (`git push origin :branch`; a rule ending in `:*` would match every
push), commands run with `git -C <path>`, write requests made with `gh api`
(for example `gh api -X PATCH repos/<owner>/<repo>/pulls/<n>`, which edits or
closes a pull request), the GitHub API reached by other means, and issue or
comment writes. `gh api` is left available because it is also how an agent
reads CI runs and review comments, and its write requests can be spelled too
many ways for a pattern to catch reliably. `Monitor`, which follows a command's
output for the length of a session, is left available on purpose: it could
poll for pull request activity, but it is also how an agent follows a long
local build or test run. These rest on the house rule alone.

## Consequences

- The owner opens each pull request: one extra click, from a page the agent
  links to.
- The agent does not correct a pull request body after it is open; it hands
  over the final text instead. The deny list blocks the GitHub tool and
  `gh pr edit`; an edit through `gh api` is ruled out by the house rule alone.
- CI results and review comments do not wake the agent. The owner says when
  to look.
- `foundation`'s *Coding Session Links Are Not Disclosed* said a tool-appended
  link "is removed by editing the body once it is posted". That was corrected
  in two steps: the pull request that archived `owner-opens-pull-requests`
  replaced the remedy with the agent not opening pull requests, and the change
  `appended-link-is-pull-requests-only` narrowed the premise from "pull
  request or issue" to pull requests, after the issue measurements above.

## Alternatives considered

- **Keep opening pull requests through the tool and delete the footer revision
  each time.** Rejected: the link is public from the moment the pull request
  opens until a person deletes the revision, and every pull request needs that
  manual step.
- **Rely on the `session-links` workflow to strip the footer.** Rejected for
  the same reason: stripping it is an edit, and the original stays in the
  history.
- **Open pull requests from the session with `gh` instead of the GitHub
  tool.** Rejected: measured on 2026-10-14. `gh pr create` is refused, because
  the session blocks GitHub's GraphQL API, and a pull request created through
  the REST API got the same footer.
