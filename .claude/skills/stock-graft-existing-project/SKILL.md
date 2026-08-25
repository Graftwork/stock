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

*(pending — filled in and reordered as each is actually done and measured on
comic-book-guy. The list below is the provisional plan from the applicability
review, not yet confirmed by doing it.)*

1. Reconcile the Python version pin (and any other toolchain pins) between
   what Stock requires and what the project already declares.
2. Bring the project's existing code to lint-clean under Stock's `ruff`
   config before wiring in CI, so a freshly added check does not go red on
   day one for code Stock had no part in writing.
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

*(pending — this section is the point of the skill. It stays empty honestly
until there is a real lesson to record, rather than being filled with
anticipated ones.)*

## Open questions

*(pending)*
