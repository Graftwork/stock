## Why

Every real grafted project so far has hit the same thing: the coding
platform's own per-session default asks the agent to append a link to the
private coding session or conversation — a `Claude-Session:` line in a commit
message, or an equivalent line in a pull request or issue body — alongside
the coding agent and model. Naming the agent and model is the promise
*AI Authorship Is Disclosed* already makes, and it is a good one: a reviewer
reading a diff is owed the same context as the person who prompted it. A link
to the specific private conversation that produced the change is a different
thing entirely — it identifies an account, sometimes a device, and a private
exchange nobody but its participants agreed to publish, and it serves no
reviewer's purpose the agent-and-model disclosure doesn't already serve.

Measured directly on [`Graftwork/talks`](https://github.com/Graftwork/talks)
(a project grafted from Stock, in conversation with its owner): the session
link kept reappearing in pull request bodies across multiple PRs despite being
stripped each time, because the platform re-injects its own default on every
fresh turn unless something in the repository itself overrides it. The
project's owner was explicit that the disclosure itself is welcome — the
agent and model, not the conversation — matching exactly what *AI Authorship
Is Disclosed* already promises and nothing more.

The one property that makes this a foundation-level concern rather than
something each project rediscovers on its own: **a repository's own `CLAUDE.md`
already takes precedence over the platform's per-session default here** — the
Claude Code platform's own attribution guidance says as much explicitly. So
the fix is durable and mechanical for the slice that can be, the same shape
`Context Is Not Content` already established for credentials: a house rule
plus, where the artifact is one the suite can actually observe, a pre-commit
guard.

## What Changes

A new `foundation` requirement, **Coding Session Links Are Not Disclosed**,
alongside the existing *AI Authorship Is Disclosed*: the agent and the model
are named; the private session or conversation that produced a change is not
linked. Two scenarios, split by what can enforce them — same split
`Context Is Not Content` uses for credentials vs. personal detail:

- **One mechanical scenario** — a commit message containing a link to a
  coding session is refused by a new local pre-commit hook
  (`scripts/check_no_session_link.py`), run at the `commit-msg` stage. A
  machine can read a commit message; it cannot read a pull request or issue
  body before it is posted.
- **One review-policy scenario**, declared as a gap in
  `[tool.graftwork.traceability]` — no test can observe a pull request or
  issue body, the same limitation *AI Authorship Is Disclosed* already lives
  with.

Supporting changes: a house rule in `CLAUDE.md` stating the rule plainly
(mirroring the existing "Disclose AI authorship" bullet), a new
`default_install_hook_types` entry in `.pre-commit-config.yaml` so a plain
`pre-commit install` wires up the new `commit-msg` hook without a second,
easy-to-forget install command, and a UAT-adjacent note in the CHANGELOG
recommending grafted projects add the equivalent house rule to their own
`CLAUDE.md` even before re-syncing, since the platform default applies per
repository, not per Stock version.

## Capabilities

### New Capabilities

None. This extends an existing capability.

### Modified Capabilities

- `foundation`: gains the **Coding Session Links Are Not Disclosed**
  requirement. Grafted projects inherit a new promise (additive — a project
  that adopts neither the hook nor the house rule stays green), which makes
  this a minor version bump.

## Impact

`openspec/specs/foundation/spec.md`, `scripts/check_no_session_link.py` (new),
`tests/test_check_no_session_link.py` (new), `.pre-commit-config.yaml`,
`pyproject.toml` (one new declared gap), `CLAUDE.md`, `CHANGELOG.md`.

Under [`docs/RELEASING.md`](../../../../docs/RELEASING.md) this touches
`openspec/specs/`, `scripts/`, and `tests/`, so it takes the full OpenSpec
route.
