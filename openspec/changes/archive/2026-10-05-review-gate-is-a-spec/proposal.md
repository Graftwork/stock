## Why

The automated review check promises something specific: a green tick means a
review was actually posted. v0.6.0 ships a final step in the review workflow
that keeps that promise. The promise exists only as shell inside a workflow
file and the comments around it. `foundation` does not mention it, the
traceability guard cannot see it, and no test runs the step, so a refactor can
delete a rule without any check noticing.

That matters because the original failure was exactly a rule going missing
unnoticed. Before the step existed, every earlier review failure ended the
same way: the job reported success and nothing was posted
([`Graftwork/stock#39`](https://github.com/Graftwork/stock/issues/39)). The
rules in the step were then set one at a time against measured runs
(`#41`, `#44`); none of that measurement survives in a form the suite can
re-check.

This change writes the promise down as a requirement, and makes tests claim it.

## What Changes

**ADDED** `foundation` → *A Passing Review Check Means A Review Happened*,
with seven scenarios: a posted review passes; nothing posted fails; a run that
reports an error fails; a pull request that edits the review workflow fails;
a denied tool call only warns; a
declined review passes only when the pull request changes nothing but
Markdown; comments by anyone but the review bot do not count.

The scenarios are claimed by tests, not declared as gaps (maintainer's choice,
over a declared gap with a written reason). A new `tests/test_review_gate.py`
reads the gate step out of `.github/workflows/claude-review.yml`, runs it with
`bash` against a fake `gh` and a fake execution file, and checks the exit code
and the output.

Not changed: the workflow itself, the gate's behaviour, the four existing
declared gaps.

Not covered, and said so in the spec: whether the review follows its
instructions (the "No reviewable changes" note, reviewing again after a push)
is behaviour of a model and a plugin Stock does not pin. It is checked on live
runs (`#51`, `#52`), not by this suite.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `foundation`: gains one requirement, *A Passing Review Check Means A Review
  Happened*, with seven scenarios. No existing requirement changes.

## Impact

- `openspec/specs/foundation/spec.md`: one requirement, seven scenarios, added
  by archiving. The guard's total goes from 14 scenarios to 21 (derived:
  14 measured on `main` with `check_spec_traceability.py` today, plus 7), all
  claimed, so the declared gaps stay at 4.
- `tests/test_review_gate.py`: new. Needs `bash` and `jq` on the machine that
  runs the suite; see `design.md`.
- `CHANGELOG.md`: an `[Unreleased]` entry. Grafted projects that run the
  review workflow get the requirement and the tests on their next re-sync; a
  project that does not run it must decide what to do with them (an open
  question in `design.md`).
- No change to `.github/workflows/`, `scripts/` or `pyproject.toml`
  dependencies.
