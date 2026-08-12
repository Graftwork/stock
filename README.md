# Graftwork Stock

[![CI](https://github.com/Graftwork/stock/actions/workflows/ci.yml/badge.svg)](https://github.com/Graftwork/stock/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Graftwork/stock/branch/main/graph/badge.svg)](https://codecov.io/gh/Graftwork/stock)

The rootstock for new projects — a versioned foundation you graft new work onto,
so every project starts from a proven, consistent base and can be re-synced as
the foundation improves.

**Version 0.1.2.** See [CHANGELOG.md](CHANGELOG.md) for what changes between
versions, which doubles as the migration list for already-grafted projects.

## What you get

A project that is green from commit one — lint, tests, coverage, and CI all pass
on a fresh stamp with zero edits — so the first real commit is the idea, not the
plumbing.

| Piece | What it's for |
| --- | --- |
| [`mise.toml`](mise.toml) | Pinned toolchain (Python, uv, Node) — same versions on a laptop and in CI |
| [`pyproject.toml`](pyproject.toml) | uv-managed deps, ruff, pytest, coverage |
| [`openspec/`](openspec/) | Plain-English scenarios — the review layer |
| [`scripts/check_spec_traceability.py`](scripts/check_spec_traceability.py) | The guard: every scenario is claimed by a test |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Lint + test + coverage upload |
| [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | The same checks, before the commit lands |
| [`.devcontainer/`](.devcontainer/) | Reproducibility layer, for when a project graduates |
| [`docs/decisions/`](docs/decisions/) | ADRs — which choices were deliberate |
| [`CLAUDE.md`](CLAUDE.md) | Commands, conventions, architecture for Claude Code |

## Getting started

```bash
mise trust          # once per clone — mise won't run an untrusted config
mise install && uv sync
mise run check
```

## The verification layer

This is the part that matters. A spec scenario is written in plain English:

```markdown
#### Scenario: A refund returns the full amount
- **WHEN** a customer requests a refund
- **THEN** the full amount is returned
```

and a test claims it by id:

```python
@pytest.mark.spec("billing/a-refund-returns-the-full-amount")
def test_refund_returns_full_amount(): ...
```

`mise run trace` then checks **both directions** — a scenario with no test, or a
test claiming a scenario that doesn't exist — and prints what's missing in plain
English:

```
Scenarios with no test claiming them:
  billing/a-refund-returns-the-full-amount
    "A refund returns the full amount" under "Refunds"
    openspec/specs/billing/spec.md:12
    fix: add @pytest.mark.spec("billing/a-refund-returns-the-full-amount") to a test

0/1 scenarios claimed by tests
```

It runs three ways — standalone, as a pre-commit hook, and as a test in the suite
— so the link between what was promised and what is checked can't quietly rot.
The guard is itself tested against known-bad input, because a guard that can't
fail isn't a guard. See [ADR 0004](docs/decisions/0004-spec-traceability-guard.md).

## Turning on the coverage badge

Coverage runs from day one, but the hosted badge needs one step: add a
`CODECOV_TOKEN` secret to the repo and it goes live on the next push. Until then
CI stays green and the real number is in the CI log — the upload is deliberately
non-blocking so a fresh stamp is never red. See
[ADR 0003](docs/decisions/0003-coverage-reporting.md).

## Grafting a project from Stock

Clone Stock at a tag, drop its history, and point the remote at the new repo:

```bash
git clone --branch v0.1.0 --depth 1 git@github.com:Graftwork/stock.git <project>
rm -rf <project>/.git
git -C <project> init -b main
git -C <project> remote add origin <new-repo-url>
```

Then:

1. **Keep `openspec/specs/foundation/`.** It is Stock's own spec, and its
   promises stay true of the grafted project — the suite asserts at least one
   scenario exists, so removing it turns a fresh stamp red. Your capabilities go
   alongside it.
2. Rewrite `README.md`, `CHANGELOG.md`, and the "what this repo is" section of
   `CLAUDE.md` for the new project. Keep `docs/decisions/` — the foundation's
   rationale travels with it, and the project's own ADRs start at 0005.
3. Set `name` and `description` in `pyproject.toml`, and record the graft:

   ```toml
   [tool.graftwork]
   stock-version = "0.1.0"
   grafted = "YYYY-MM-DD"
   ```

4. Run `mise trust && mise install && uv sync && mise run check` — it should be
   green before you write a line of your own code.

To re-sync later, read this CHANGELOG forward from the recorded `stock-version`,
apply each entry as its own small PR, then bump the recorded version.
