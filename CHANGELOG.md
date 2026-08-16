# Changelog

Every entry here is a migration step for projects already grafted from Stock.
Read from the version a project recorded at graft time forward, and apply each
entry as its own small PR.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
where a **major** bump means a grafted project needs manual intervention to
re-sync, and a **minor** bump means the migration is additive.

## [0.2.0] — 2026-08-16

The ways of working, promoted from a real project. Everything here changed an
outcome on [count-spatula](https://github.com/Bear-Prince/count-spatula) — a
parametric model generator run this way for its whole life — rather than being
added because it sounded sensible.

The migration is additive: nothing existing changes behaviour, and a grafted
project that adopts none of it stays green.

### Added

- **`WORKFLOW.md`** — how changes are actually run. The loop, the recipe table
  (situation → action), and the conventions OpenSpec cannot enforce for you:
  backlog stubs as proposal-only changes, transcribing learnings forward when a
  change is abandoned, small scope justified by abandonment cost rather than
  velocity, `MODIFIED` meaning the *entire* requirement, deprecation as a
  first-class `REMOVED` delta, and proving the untouched path is untouched. Ends
  with OpenSpec's rough edges written down, so nobody assumes they have
  misunderstood the tool.
- **Declared gaps in the traceability guard.** A scenario that genuinely cannot
  be tested is declared in `pyproject.toml` with a mandatory written reason:

  ```toml
  [tool.graftwork.traceability]
  unclaimed = [
      { scenario = "foundation/...", reason = "review policy; the suite cannot observe a pull request" },
  ]
  ```

  The declarations are checked like everything else — an entry with no reason, one
  naming a scenario that no spec declares, and one for a gap a test has since
  closed all fail the guard. The distinction that matters is not "tested or not"
  but "decided or not".
  ([ADR 0005](docs/decisions/0005-declared-gaps-in-traceability.md))
- **`docs/UAT.md`** — numbered cases with `Command` / `Expect` / `Last passed`,
  run before the PR and before the archive. An agent may run the commands and
  report what it saw; it may not mark a case passed. Ships with four real cases
  for Stock itself rather than an empty template, one of them marked
  *post-release* because it verifies the published tag and so genuinely cannot
  run before the release exists.
  ([ADR 0006](docs/decisions/0006-uat-is-a-human-gate.md))
- **House rules in `CLAUDE.md`** — the agent-facing half. Measure rather than
  derive and mark which you did; test an empirical premise before specifying on
  top of it; in-flight artifacts are editable and edits get reported; don't open
  a second change over ground an existing one covers; ask on genuine forks and
  decide on everything else; treat the user's field experience as evidence and
  say when it moves your recommendation; don't close a gate that needs human
  senses.
- **Two new `foundation` requirements** — *Declared Gaps* (four scenarios, all
  claimed by tests) and *AI Authorship Is Disclosed* (one scenario, declared as a
  review policy, which is what gives Stock a worked example of the new mechanism
  in its own repo).
- **`docs/RELEASING.md`** — how a change gets *out*, which Stock had never
  written down. The route table (spec/guard changes run as full OpenSpec changes;
  docs and CI go direct), the version decision, tag-after-merge, and the re-sync
  PRs each release owes every grafted project. A grafted project should keep the
  file and replace the specifics.
  ([ADR 0007](docs/decisions/0007-how-stock-changes-itself.md))
- **Project context and artifact rules in `openspec/config.yaml`**, which was
  previously entirely commented out. The `proposal` rules ask for a
  `## Background` section carrying reasoning forward from a superseded change,
  and for the provenance of load-bearing numbers; the `tasks` rule asks for a UAT
  step ordered before archive. Rules are the supported customisation hook — the
  artifact templates themselves are regenerated and would lose an edit.
- **A worked backlog stub** at
  `openspec/changes/version-string-consistency/` — proposal-only, no deltas,
  demonstrating the convention and tracking a real problem: the version string
  appears in 13 places across 6 files, only 5 of which may be bumped at a
  release. It will report as invalid under `openspec validate` until designed,
  which is the documented cost of the pattern.

### Changed

- `check()` in `scripts/check_spec_traceability.py` takes an `allowed` argument.
  It defaults to reading `pyproject.toml`, so existing callers keep working;
  pass `allowed=[]` to check specs on their own. `Report` gains `unexplained`,
  `orphaned`, and `redundant` alongside `unclaimed` and `unknown`, and the
  summary line accounts for declared gaps: `8/9 scenarios claimed by tests, 1
  allowed without one`.
- Graft steps in `README.md` now say to keep `WORKFLOW.md` and to replace Stock's
  UAT cases rather than the file. A grafted project's own ADRs now start at 0008.
- **Stock no longer commits to `main` directly.** Up to v0.1.2 every release was
  a direct commit — `main` is a linear run with no merge commits and the repo had
  never had a pull request. From v0.2.0 changes reach `main` by branch and PR,
  which is also what makes the new *AI Authorship Is Disclosed* requirement
  something Stock itself can keep. This is a process change, not a code change;
  grafted projects are free to ignore it.

### Notes

- The vendored `.claude/skills/openspec-*` files are deliberately untouched. The
  "don't open a duplicate change" guardrail belongs in one of them by rights, but
  those files are generated by `@fission-ai/openspec` and would lose the edit on
  the next regeneration. `CLAUDE.md` is loaded every session and carries it
  instead.
- **v0.2.0 sits on the wrong side of its own rule.** It edits
  `openspec/specs/foundation/spec.md` directly, which ADR 0007 forbids from
  v0.2.0 onward — it is the change that introduced the rule and could not have
  followed it. Retrofitting an archived change would fabricate a record of
  deliberation that never happened. The gap is deliberate and stays on the
  record; everything after this follows the route table.
- The auto-marked fast/slow test split is documented in `WORKFLOW.md` as a
  pattern, not shipped as code. Stock has no slow tests, and a `slow` marker with
  nothing to mark is exactly the "added for later" the conventions forbid. It
  should be promoted the first time a grafted project earns it.

## [0.1.2] — 2026-08-13

Permission allowlist tightened. Grafted projects should apply this to their own
`.claude/settings.json`.

### Fixed

- **The allowlist granted arbitrary code execution.** `Bash(uv run:*)` permitted
  `uv run python -c '<anything>'`, and `Bash(mise run:*)` permitted any task
  `mise.toml` happens to define. Both are removed and replaced by the specific
  commands actually used — `uv run pytest`, `uv run ruff check .`,
  `mise run check`, and so on. Because this file is copied into every grafted
  project, the over-broad version propagated outward, which is what makes it
  worth a release of its own.

### Added

- Narrow read-only allowlist entries derived from real usage across sessions:
  the `mise run` tasks, `uv run pytest`, ruff's check-only forms, the
  traceability guard, `uvx pre-commit run --all-files`, `uv sync --locked`, and
  the read-only OpenSpec subcommands.

### Notes

- `Bash(uvx pre-commit:*)` and `Bash(npx --yes @fission-ai/openspec@1.6.0:*)`
  are deliberately kept. Both are scoped to a single named tool rather than to
  an interpreter, and narrowing OpenSpec further would mean a prompt on every
  `new change` and `archive` — a real cost for no real gain.
- Entries such as `Bash(git status:*)` are redundant, since Claude Code already
  treats read-only git and gh subcommands as safe. They are harmless and left
  alone.

## [0.1.1] — 2026-08-12

Fixes found by the first real graft ([sorting-office](https://github.com/Graftwork/sorting-office)).
No code changed, so re-syncing is documentation-only.

### Fixed

- **The graft instructions produced a red stamp.** They said to drop
  `openspec/specs/`, but the suite asserts at least one scenario exists, so a
  project following them would fail on its first run — the exact opposite of the
  promise. The `foundation` spec now explicitly travels with the graft, which is
  what its own Purpose section always said.
- `mise trust` was missing from the getting-started steps. mise refuses to run an
  untrusted config, so a fresh clone stopped at the first command.
- CI pinned stale action majors (`checkout@v5`, `mise-action@v2`,
  `codecov-action@v5`); now `v7`, `v4`, and `v7`.

### Added

- **`[tool.graftwork]` in `pyproject.toml`** — records `stock-version` and the
  graft date. Previously "record the version you grafted from" named no location,
  so a re-sync had nowhere to look. This is now the starting point for reading
  the CHANGELOG forward.
- Concrete clone-and-detach commands for grafting, rather than "copy the
  foundation across".

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

[0.2.0]: https://github.com/Graftwork/stock/releases/tag/v0.2.0
[0.1.2]: https://github.com/Graftwork/stock/releases/tag/v0.1.2
[0.1.1]: https://github.com/Graftwork/stock/releases/tag/v0.1.1
[0.1.0]: https://github.com/Graftwork/stock/releases/tag/v0.1.0
