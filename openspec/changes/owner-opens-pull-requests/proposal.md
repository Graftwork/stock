## Why

`foundation`'s *Coding Session Links Are Not Disclosed* says that a link the
platform appends to a pull request body "is removed by editing the body once it
is posted". That remedy does not work: GitHub keeps every version of an edited
description, and anyone who can see the repository can open them. On six
pull requests in this repository the link was edited out, stayed readable in
each first version, and had to be deleted from the history by hand once the
repository was public. [Stock ADR 0018](../../../docs/decisions/stock-0018-owner-opens-agent-pushes.md)
replaced the remedy with a working rule, *the agent does not open pull
requests; a person does*, but the spec still states the old one. A grafted
project that re-syncs the spec inherits a remedy known not to work.

## What Changes

- The second paragraph of *Coding Session Links Are Not Disclosed* no longer
  says the appended link is removed by editing. It says the agent does not open
  pull requests, so the platform never appends the link, and that editing it
  out afterwards leaves it in the description's history.
- Both existing scenarios keep their exact titles and text, so their ids and the
  tests and declared gap that name them are unaffected. No scenario is added:
  who opened a pull request is not something the suite can observe.
- The declared gap for `foundation/a-pull-request-or-issue-contains-no-session-link`
  in `pyproject.toml` keeps its claim (the suite cannot observe what an agent
  writes for a pull request) but no longer presents the `session-links`
  workflow's stripping as the remedy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `foundation`: *Coding Session Links Are Not Disclosed* changes how a
  platform-appended pull request link is kept out: by the agent not opening
  pull requests, not by editing the body afterwards.

## Impact

- `openspec/specs/foundation/spec.md`, through the archived delta.
- `pyproject.toml`: one declared-gap reason.
- `CHANGELOG.md`: an `[Unreleased]` entry; grafted projects re-copy the
  requirement and the reason.
- No code, workflow or test changes. The traceability guard's count stays at
  17 of 21 scenarios claimed, with 4 declared gaps (measured on `main` at
  `498a01b` with `uv run python scripts/check_spec_traceability.py`).
