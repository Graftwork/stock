# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repo is

Graftwork Stock is a foundation ("rootstock") repo. Projects are grafted from it
and re-synced as it improves. Changes here propagate outward to real projects, so
the bar for adding something is higher than in a normal repo — see Conventions.

## Commands

```bash
mise trust            # once per clone — mise won't run an untrusted config
mise install          # install the pinned toolchain
uv sync               # install Python dev dependencies
mise run check        # everything CI runs (lint + test)
mise run test         # pytest with coverage
mise run lint         # ruff check + format check
mise run format       # auto-fix and format
mise run trace        # spec traceability guard on its own
mise run openspec -- list   # the pinned OpenSpec CLI
uvx pre-commit run --all-files
```

## Architecture

There is deliberately no `src/`. Stock carries the verification layer and nothing
speculative; a grafted project adds its own package alongside.

- `openspec/specs/<capability>/spec.md` — plain-English scenarios, the review layer
- `scripts/check_spec_traceability.py` — the guard linking scenarios to tests
- `tests/` — the suite, including tests of the guard itself
- `docs/decisions/` — ADRs recording deliberate choices
- `mise.toml` — pinned toolchain and task entry points

## Conventions

**The spec traceability contract.** Every scenario in `openspec/specs/` must be
claimed by at least one test:

```python
@pytest.mark.spec("<capability>/<slugified-scenario-title>")
def test_something(): ...
```

When you add a scenario, add the claiming test in the same change. When you
rename a scenario, its id changes and the guard will flag the broken link —
update the marker deliberately rather than routing around the guard.

**Never weaken the guard to make it pass.** If the guard fails, either the test
is missing or the spec is wrong. Both are real findings.

**Keep it unspeculative.** No `src/` ceremony, no publishing pipeline, no
monorepo layout until a real project needs one. The template grows by promotion
from things that proved themselves in real projects, never by anticipation. If
you are tempted to add something "for later", don't.

**Record deliberate choices.** Anything a future reader might mistake for drift
gets an ADR in `docs/decisions/`.

**Every change here is a migration for grafted projects.** Log it in
`CHANGELOG.md` so "migrate project Y to Stock vX" is a reviewable batch of small
PRs rather than an archaeology exercise.

## Notes

- OpenSpec is `@fission-ai/openspec`, pinned via `OPENSPEC_VERSION` in `mise.toml`.
  The bare `openspec` npm package is an unrelated placeholder — do not use it.
- `.claude/settings.local.json` is machine-local and gitignored; the shared
  allowlist is `.claude/settings.json`.
