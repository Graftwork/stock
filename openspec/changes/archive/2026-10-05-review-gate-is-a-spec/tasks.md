## 1. Archive first

> Archive moves ahead of the tests: the guard flags a claim that names a
> scenario that does not exist yet (see `WORKFLOW.md`, scenario ids).

- [x] 1.1 `openspec validate review-gate-is-a-spec`, then
      `openspec archive review-gate-is-a-spec -y`.
- [x] 1.2 Confirm `openspec/specs/foundation/spec.md` carries the new
      requirement and its seven scenarios, with the ids given below, and that
      no relative link in the archived artifacts went dead.
- [x] 1.3 `uv run python scripts/check_spec_traceability.py` now reports the
      seven scenarios as unclaimed (expected; they are claimed in group 2).

## 2. The tests

- [x] 2.1 `tests/test_review_gate.py`: a helper that extracts the step with
      `id: gate` from `.github/workflows/claude-review.yml` by indentation and
      asserts exactly one step and a non-empty script; a helper that builds
      the fake `gh`, the execution file and the environment; a check that
      `bash` and `jq` exist, failing (not skipping) if not.
- [x] 2.2 One test per scenario, each marked
      `@pytest.mark.spec("foundation/<id>")`:
      `a-review-that-was-posted-passes-the-check`,
      `a-run-that-posted-nothing-fails-the-check`,
      `a-run-that-reports-an-error-fails-the-check`,
      `a-pull-request-that-edits-the-review-workflow-fails-the-check`,
      `a-denied-tool-call-only-warns`,
      `a-declined-review-passes-only-for-a-markdown-only-pull-request`,
      `comments-by-anyone-but-the-review-bot-do-not-count`.
      The "only warns" scenario is parametrised over an exploratory call, each
      tool the review posts with (`Skill`, the inline-comment tool, a
      `gh pr comment` call), and a command that merely quotes that phrase.
- [x] 2.3 The extra tests from design.md decision 6 (no execution file;
      awkward file name in the decline path; denied list on one line and
      capped). They claim no scenario.
- [x] 2.4 Show that each claimed test can fail: for every scenario, change the
      gate in a scratch copy to drop that rule and confirm the matching test
      goes red. Record the result in the PR (measured, not assumed).
- [x] 2.5 `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`,
      and `uv run python scripts/check_spec_traceability.py`: all claimed
      (`17/21` claimed, 4 declared gaps, matching the existing `10/14` plus 7), nothing unclaimed.

## 3. Prose and record

- [x] 3.1 `CHANGELOG.md` `[Unreleased]`: what the change adds, what it does
      not cover (live behaviour), the `bash`/`jq` requirement, and the
      migration for a graft that does not run the review workflow (the open
      question in design.md, resolved first). Choose the version level.
- [x] 3.2 `docs/UAT.md`: decide whether a case needs adding or changing (the
      new tests are suite-observable, so probably none). Record the decision;
      do not write a "Last passed" date.
- [x] 3.3 Read the artifacts as a stranger would (UAT case 4) before the
      commit: no names of real people, accounts or employers.

## 4. Before the PR

- [x] 4.1 Branch is `feature/review-gate-is-a-spec`; the PR names the coding
      agent and the model; no session link in any commit or the PR body.
- [x] 4.2 The PR does not edit `claude-review.yml`, so `review` runs normally.
      If a test reveals a gate bug, stop and report it instead of fixing it
      here.

## 5. Revised before merge

> Added after `#56` was open, at the maintainer's decision; see design.md,
> "Revised before merge".

- [x] 5.1 Remove the "needed tool denied" rule from the gate in
      `.github/workflows/claude-review.yml`; update the gate's comments and
      the failure message for a workflow edit (the check is advisory, so no
      bypass is needed).
- [x] 5.2 Spec: remove the scenario "A denied tool the review needs fails the
      check"; reword "A denied exploratory call only warns" to "A denied tool
      call only warns" (the id changes to `a-denied-tool-call-only-warns`);
      "A run that posted nothing fails the check" also lists denied calls.
- [x] 5.3 Tests: update the claiming tests; show each of the seven can fail.
- [x] 5.4 CHANGELOG and docs: the check is advisory; the gate no longer fails
      on a denied tool.
- [ ] 5.5 Maintainer: remove `review` from the ruleset's required checks
      (GitHub web UI). `check` stays required.
