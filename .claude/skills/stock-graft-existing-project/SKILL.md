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
[Stock ADR 0006](../../../docs/decisions/stock-0006-uat-is-a-human-gate.md) on
why an agent reports what it has not yet verified rather than marking it
done.

## When this applies

The README's
["Grafting a project from Stock"](../../../README.md#grafting-a-project-from-stock)
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
Steps 1–3 below are confirmed by doing them; the rest are still the
provisional plan from the applicability review.)*

Before step 1: create a status file in the project being grafted (e.g.
`GRAFT_STATUS.md`), tracking these steps' status for *that* project. See
Lessons below — this is not optional bookkeeping, the first case ran for
several sessions without one and the plan existed only in conversation.

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
3. **Done.** Add an initial test suite for whatever part of the project is
   already plain, importable, testable code — before touching anything that
   is not. On the first case this was a genuinely small scope: one function
   with no I/O beyond the filesystem and sqlite, out of a script whose real
   logic is browser automation around an interactive login. Resist the pull
   to pad coverage by testing CLI argument-parsing glue or anything that
   only exists to call the untestable part — an honest small suite beats a
   padded one that looks more complete than the code actually is. Pair with
   Stock's own pytest/coverage config (`testpaths`, `pythonpath`, `--cov`)
   but leave out `--strict-markers` and the `spec()` marker until step 7
   actually adds the traceability guard those exist for — see Lessons below
   on why this step's own branch naming has the same ordering problem.
4. **In progress.** Decide, file by file, what to do with logic that is not
   structured as testable code at all — extract into testable modules where
   practical, or declare as an untestable gap with a written reason where it
   is genuinely human-only, per
   [Stock ADR 0005](../../../docs/decisions/stock-0005-declared-gaps-in-traceability.md).
   On the first case: every plain, callable function across two Jupyter
   notebooks got wrapped directly with `testbook` (tests run against a real
   kernel, not a mock) rather than extracted first — extraction can follow
   later once the wrapped tests already prove correctness, which lowers the
   stakes of doing it. *(pending: the detailed testbook mechanics —
   serialization quirks, capturing printed output, running a cell with
   `allow_errors` — are still to be written up here.)* One genuine
   extraction case remains open: bare top-level script logic with no
   function boundary at all (dedupe/mkdir/rename against a hardcoded path)
   cannot be wrapped as-is and needs extracting before it is testable —
   tracked as an open item on the project's own status file (see Lessons),
   not treated as a new step of its own.
5. Add `mise.toml` together with `.claude/hooks/session-start.sh` and its
   `.claude/settings.json` wiring, as one change — not `mise.toml` alone. A
   Claude Code cloud session cannot resolve the pinned toolchain any other
   way; see
   [Stock ADR 0012](../../../docs/decisions/stock-0012-uv-not-mise-run-on-claude-code-web.md).
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
cells) most notebooks do not need. Generalized into
[Stock ADR 0013](../../../docs/decisions/stock-0013-defer-to-tool-defaults-over-suppressions.md):
default to a tool's own defaults, treat a suppression as needing a written
justification rather than being a routine option alongside the default —
Graftwork's target user is a product owner who cannot evaluate whether a
suppression is still warranted later, not an engineer who might reasonably
judge one safe to keep.

**Ruff's import-sort can split one multi-name `from module import (A, B,
C)` into several single-name `from module import (X)` statements**, one per
name, rather than keeping them combined. Confirmed stable across repeated
`ruff format` runs (not a transient/unstable formatting choice), just an
unexpected shape when reviewing the diff for the first time.

**Stock's branch-naming convention (`WORKFLOW.md`, "Branch names match the
route") presupposes `openspec/` already exists.** A change to `tests/`
content is documented as the OpenSpec route (`feature/`, `bugfix/`) — but
that route only exists once `openspec/` and the traceability guard are in
the project, which for an existing project being grafted is step 7, not
step 3. Adding the first test suite has nothing to name a `feature/`
branch after yet. Used `chore/` for this step on the first case, as the
least-wrong available prefix, rather than inventing a new one or
force-fitting the OpenSpec-route naming before the OpenSpec route exists.
Revisit once a project reaches step 7: does the *next* test change after
that point correctly switch to `feature/`/`bugfix/`, and is `chore/` still
the right call for the pre-step-7 window, or does this graft skill need its
own documented exception to the branch-naming convention?

**An existing project's `.gitignore` often has real gaps that only surface
once Stock's tooling is actually added**, not before. The first case's
`.gitignore` covered Python build artifacts and the project's own database
files, but had no entries for `.pytest_cache/`, `.ruff_cache/`, `.coverage`,
or `coverage.xml` — not because anyone had reasoned about coverage tooling
and decided against ignoring it, but because nothing in the project had
ever produced those files before. A stray `.coverage` file appearing as
untracked, mid-step, was the actual signal, not a review of the file done
in advance. Check `git status` after running the new tooling for the first
time, not only after writing the config that adds it.

**A per-repo graft's own step-by-step status belongs in a committed file in
that project, not only in conversation.** On the first case, this skill's
numbered steps were tracked purely as a running summary inside an agent
session, across several sessions of real work — nothing recorded which
steps were done, in progress, or deliberately deferred *for that specific
project*, separately from this skill's own generalized text. That would
have been lost entirely had the session ended or reset before being written
down; it was only caught because a person asked how to track what was left.
Fixed by adding a short status file (`GRAFT_STATUS.md` on the first case) to
the grafted project itself — one place a fresh session or person can read
current status without depending on chat history. Keep it separate from
this skill: this file stays the generalized how-to and lessons, the
project's own file tracks only that project's status, including any
deferred sub-items (like the one under step 4 above) that don't warrant
becoming a numbered step of their own. Do this before step 1, not once its
absence is already felt.

## Open questions

*(none currently open)*
