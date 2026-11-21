## Context

[Stock ADR 0018](../../../../docs/decisions/stock-0018-owner-opens-agent-pushes.md)
went the direct route: a `CLAUDE.md` house rule, a deny list in
`.claude/settings.json`, and docs. It could not touch `openspec/specs/`, which is
written only by archiving a change. So `foundation` still describes the remedy
that ADR 0018 records as not working. This change brings the spec into line.
The ADR is the evidence; this change only states the requirement.

## Goals / Non-Goals

**Goals:**

- The requirement states the remedy that works: the agent does not open pull
  requests.
- Nothing that names a scenario breaks: test markers, the declared gap, the
  guard's count.

**Non-Goals:**

- Issues. Whether the platform appends the link to an issue the agent opens
  has not been measured, and ADR 0018's rule covers pull requests. The
  requirement's first paragraph still governs what the agent writes in an issue.
- Enforcement. The deny list from ADR 0018 already blocks the tools; this
  change adds no test or workflow.

## Decisions

- **Rewrite the paragraph; add no scenario.** A scenario such as "a pull request
  is opened by a person" could only become another declared gap: no test can
  observe who opened a pull request, and `pyproject.toml` already declares the
  neighbouring scenario untestable for the same reason. A gap that only restates
  that adds nothing. *Alternative:* add the scenario and declare it; rejected
  because it adds a declaration with no new information.
- **Keep both scenario titles byte-for-byte.** A title is a scenario's id
  (`foundation/<slugified-title>`), and the declared gap and the test markers
  name those ids. *Alternative:* retitle the first scenario to mention who opens
  the pull request; rejected because it renames an id and breaks the gap for a
  wording gain.
- **Reword the gap reason, not its claim.** The reason says the suite cannot
  observe what an agent writes for a pull request or issue; that stays. What
  goes is the sentence presenting the `session-links` workflow's stripping as
  the safeguard. The workflow still runs, but stripping is an edit and the
  original stays in the history.

## Risks / Trade-offs

- [The `SHALL NOT open pull requests` sentence has no scenario of its own] →
  ADR 0018's deny list enforces it mechanically for the GitHub tool and `gh pr`
  commands, and the ADR lists what the deny list does not cover.
