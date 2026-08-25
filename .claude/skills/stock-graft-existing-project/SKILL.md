---
name: stock-graft-existing-project
description: Graft Graftwork Stock onto a project that already exists — its own history, its own code, no prior Stock relationship — rather than the README's clone-fresh path, which assumes starting empty. Use when a project needs Stock's foundation (lint, tests, CI, spec traceability, the working conventions) layered onto code and history that already exist, not stamped fresh.
license: MIT
compatibility: Not yet established — pending the first complete case.
metadata:
  author: graftwork
  version: "0.1"
  status: "draft — in progress, being written against a real first case, not yet proposed upstream"
  provenance: "Started while grafting Stock onto comic-book-guy (stiffneckjim/comic-book-guy) — an existing project with its own history and no prior Stock relationship. Sections are filled in as each step is actually taken and measured, not written ahead of the real work."
---

Graft Stock onto a project that already has its own history, code, and
conventions — without discarding any of it.

## Status

This skill is incomplete by design. It is being written one real step at a
time against comic-book-guy, the first project Stock has been grafted onto
after the fact rather than at creation. Sections marked *(pending)* have not
been done yet; treat the gap as honest, not an oversight — see
[Stock ADR 0006](../../docs/decisions/stock-0006-uat-is-a-human-gate.md) on
why an agent reports what it has not yet verified rather than marking it
done.

## When this applies

The README's
["Grafting a project from Stock"](../../README.md#grafting-a-project-from-stock)
procedure — clone at a tag, drop history, point at a new remote — assumes the
project does not exist yet. This skill is for the opposite case: a project
with its own commits, its own files, and its own conventions already in
place, that wants Stock's foundation layered on top of them.

## Why the documented graft does not apply as-is

*(pending — draft note, to confirm or correct once the graft is done: the
clone-fresh procedure discards exactly the thing an existing project cannot
discard, its own history. Every step below is about reconciling Stock's
scaffold against files and conventions that already exist, rather than
writing them onto an empty repo.)*

## Steps

*(still being reordered and refined as later steps are done and measured.
Steps 1–2 below are confirmed by doing them; the rest are still the
provisional plan from the applicability review.)*

1. **Done.** Reconcile the Python version pin (and any other toolchain pins)
   between what Stock requires and what the project already declares. On the
   first case this was a one-line bump each in `pyproject.toml` and
   `.python-version`, followed by re-resolving the lockfile against the new
   interpreter — no dependency versions changed, only the wheel selection for
   the new Python tag. Small enough that there is not much more to say about
   it in general; watch for it costing more on a project with tighter
   third-party version constraints.
2. **Done.** Bring the project's existing code to lint-clean under Stock's
   `ruff` config before wiring in CI, so a freshly added check does not go
   red on day one for code Stock had no part in writing. This includes any
   Jupyter notebooks in the project — see Lessons below, ruff's notebook
   support changes what this step actually covers. Auto-fix what `ruff check
   --fix` and `ruff format` can; the findings with no safe autofix need a
   real per-case decision, not a blind accept — e.g. a mutable-default-argument
   finding (`B008`) needs the function's actual default-value semantics
   understood before rewriting it, not a mechanical transform.
3. Add an initial test suite for whatever part of the project is already
   plain, importable, testable code — before touching anything that is not.
4. Decide, file by file, what to do with logic that is not structured as
   testable code at all — extract into testable modules where practical, or
   declare as an untestable gap with a written reason where it is genuinely
   human-only, per
   [Stock ADR 0005](../../docs/decisions/stock-0005-declared-gaps-in-traceability.md).
5. Add `mise.toml` together with `.claude/hooks/session-start.sh` and its
   `.claude/settings.json` wiring, as one change — not `mise.toml` alone. A
   Claude Code cloud session cannot resolve the pinned toolchain any other
   way; see
   [Stock ADR 0012](../../docs/decisions/stock-0012-uv-not-mise-run-on-claude-code-web.md).
6. Add CI (`.github/workflows/ci.yml`), `.pre-commit-config.yaml`, and the
   rest of Stock's scaffolding once the steps above make it honestly
   reachable.
7. Bring in `openspec/`, the traceability guard, `WORKFLOW.md`,
   `docs/UAT.md`, `docs/decisions/` (starting the project's own ADRs at
   `0001`), and `CLAUDE.md`, adapted for the project's own identity per the
   README's existing "Grafting a project from Stock" steps 1–5.

## Lessons so far

**Ruff lints and formats `.ipynb` natively, not just `.py`.** This changes
what "bring the code to lint-clean" means for a notebook-heavy project —
notebooks are not automatically out of scope for that step, or automatically
deferred to the harder testable-code question. Confirmed by diff on a real
notebook: `ruff format` only rewrote cell `source`; `outputs` and
`execution_count` were untouched in every cell, in both a `ruff check --fix`
pass and a `ruff format` pass. Safe to run as part of the same lint-clean
step as the project's plain `.py` files, not a separate concern.

**Ruff also reformats fenced ` ```python ` code blocks inside Markdown
files**, including `README.md`. Not specific to grafting, but easy to miss
the first time `ruff format .` touches a file with no `.py` extension.

**Ruff's unused-import check (`F401`) treats a whole notebook as one shared
namespace**, not per-cell scopes. A name imported in an earlier cell reads as
already available in every later cell, so `ruff check --fix` will remove a
"redundant" import from a later cell even when that cell calls the name
directly — the import is not actually unused within the cell, only unused
*given* the earlier cell's import. Consequence: the later cell can no longer
be run standalone (kernel restart, run only that cell) without a
`NameError`.

**Decided: accept this, do not suppress it.** A notebook meant to be run
top-to-bottom in one kernel session — the normal way to use one — genuinely
does not need each cell independently runnable, so ruff's default behavior
is not wrong here, only unfamiliar on first read. Reaching for `# noqa` or
splitting the `--fix` pass to work around it would mean carrying a
project-specific exception to a tool default, for a benefit (standalone
cells) most notebooks do not need. Graftwork's target user is a product
owner, not an engineer — someone who cannot evaluate whether a suppression
comment is still justified two years later, or safely remove one that is
not. An exception that requires that judgement call is a liability for this
audience specifically, even where an experienced engineer might reasonably
keep it. Default to the tool's own defaults; treat a suppression as
something to justify explicitly, not a routine option alongside it.

**Ruff's import-sort can split one multi-name `from module import (A, B,
C)` into several single-name `from module import (X)` statements**, one per
name, rather than keeping them combined. Confirmed stable across repeated
`ruff format` runs (not a transient/unstable formatting choice), just an
unexpected shape when reviewing the diff for the first time.

## Open questions

*(none currently open)*
