# Tasks

> **Ordering note**, per [`WORKFLOW.md`'s rough edge](../../../../WORKFLOW.md#openspecs-rough-edges):
> archive moves ahead of anything that claims a scenario id, since the id
> doesn't exist in `openspec/specs/` until the delta is archived.

## 1. The mechanical half

- [x] 1.1 Write `scripts/check_no_session_link.py`: reads the commit message
      file path from argv, reports every line matching `claude.ai/code/session`
      (case-insensitive).
- [x] 1.2 Add `default_install_hook_types: [pre-commit, commit-msg]` to the
      top of `.pre-commit-config.yaml`, and the `no-session-link` local hook
      at the `commit-msg` stage. (First pass used the wrong key name,
      `default_install_types` — pre-commit warns rather than errors on an
      unknown top-level key, so this was caught only by actually running
      `uvx pre-commit run --all-files`, not by the config looking plausible.)
- [x] 1.3 Verify both directions per design.md: a clean message passes
      (exit 0), a planted session-link message is reported and refused
      (exit 1). A guard that cannot fail is not a guard. Measured directly
      (see design.md's own transcript) before wiring into pre-commit.
- [x] 1.4 Run `uvx pre-commit run --all-files` for real, not just the script
      standalone — confirms the hook is actually wired up, and is what caught
      1.2's wrong key name. Also caught `end-of-file-fixer` wanting a trailing
      newline `openspec archive` had left off `openspec/specs/foundation/spec.md`.

## 2. The human half

- [x] 2.1 Add the house rule to `CLAUDE.md`, next to the existing "Disclose AI
      authorship in pull requests" bullet.

## 3. Archive — moved ahead of the claiming test

- [x] 3.1 `openspec archive session-links-not-disclosed -y`.
- [x] 3.2 Confirm `openspec/specs/foundation/spec.md` now carries the
      **Coding Session Links Are Not Disclosed** requirement and its two
      scenarios.

## 4. Claim and declare — only possible once the ids exist

- [x] 4.1 Add `tests/test_check_no_session_link.py` claiming
      `foundation/a-commit-message-containing-a-coding-session-link-is-refused`.
- [x] 4.2 Declare
      `foundation/a-pull-request-or-issue-contains-no-session-link` in
      `[tool.graftwork.traceability]` with a written reason.
- [x] 4.3 Run `mise run trace` (or `uv run python
      scripts/check_spec_traceability.py`) and confirm the summary accounts
      for the new declared gap and reports no unclaimed scenarios. Measured:
      `10/14 scenarios claimed by tests, 4 allowed without one`.

## 5. Release

- [x] 5.1 Write the CHANGELOG entry under `[Unreleased]` — this is
      independent new work discovered after `v0.5.0-rc.3` was cut, not a
      defect that candidate's own UAT found, so it does not amend the
      `[0.5.0]` entry (see `docs/RELEASING.md` step 8's table). Recommend
      grafted projects add the equivalent `CLAUDE.md` house rule directly,
      even before re-syncing, since the platform default applies per
      repository rather than per Stock version.
- [x] 5.2 `mise run check` and `uvx pre-commit run --all-files` both green.

## 6. Verification — before the PR

- [ ] 6.1 Confirm `pre-commit install` (no extra flag) wires up the
      `commit-msg` hook: `ls .git/hooks/commit-msg` after a fresh install in
      a scratch clone, or equivalent.
- [ ] 6.2 Run the UAT cases that apply and report what was seen; do not mark
      any case passed.
