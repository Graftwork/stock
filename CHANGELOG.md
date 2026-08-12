# Changelog

Every entry here is a migration step for projects already grafted from Stock.
Read from the version a project recorded at graft time forward, and apply each
entry as its own small PR.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
where a **major** bump means a grafted project needs manual intervention to
re-sync, and a **minor** bump means the migration is additive.

## [0.1.0] — 2026-07-25

The initial foundation.

### Added

- **Pinned toolchain** via `mise.toml` — Python 3.13, uv 0.11.16, Node 26.
  Drives the local shell, CI, and the devcontainer from one source of truth.
  ([ADR 0001](docs/decisions/0001-why-mise.md))
- **Python project config** in `pyproject.toml` — uv dependency groups, ruff
  (lint + format), pytest with coverage and `--strict-markers`.
- **OpenSpec** initialised via the pinned `@fission-ai/openspec@1.6.0`, with
  Claude Code skills and `/opsx:*` commands.
  ([ADR 0002](docs/decisions/0002-why-openspec-via-npx.md))
- **Spec traceability guard** (`scripts/check_spec_traceability.py`) — checks
  that every scenario is claimed by a test and that every claim names a real
  scenario. Runs standalone, as a pre-commit hook, and inside the test suite.
  ([ADR 0004](docs/decisions/0004-spec-traceability-guard.md))
- **`foundation` spec** — Stock's own promises, written as scenarios and claimed
  by tests, so the foundation is verified by the same mechanism it provides.
- **CI** (`.github/workflows/ci.yml`) — lint, test, and a non-blocking Codecov
  upload so a fresh stamp is green before any secret exists.
  ([ADR 0003](docs/decisions/0003-coverage-reporting.md))
- **pre-commit config** — whitespace/YAML/TOML hygiene, ruff, and the
  traceability guard.
- **Devcontainer** layered on mise, for when a project graduates from experiment.
- **`CLAUDE.md`** — commands, conventions, architecture.
- **`.claude/settings.json`** — shared permission allowlist.
- **ADRs** in `docs/decisions/`, with a template.

[0.1.0]: https://github.com/Graftwork/stock/releases/tag/v0.1.0
