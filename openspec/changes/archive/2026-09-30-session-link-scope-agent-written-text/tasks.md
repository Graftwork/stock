# Tasks

> **Ordering note**, per `WORKFLOW.md`'s rough edge on scenario ids: archive
> moves ahead of anything that depends on the new spec text. The scenario id
> is unchanged (see design.md), so no id moves.

## 1. Archive first

- [x] 1.1 `openspec validate session-link-scope-agent-written-text`, then
      `openspec archive session-link-scope-agent-written-text -y`.
- [x] 1.2 Confirm `openspec/specs/foundation/spec.md` carries the narrowed
      requirement and scenario wording, and that no relative link in the
      archived artifacts went dead (archive does not rewrite them).

## 2. Move the claims

- [x] 2.1 In `pyproject.toml`, update the reason on the declared gap for
      `foundation/a-pull-request-or-issue-contains-no-session-link` (the id is
      unchanged): the suite cannot observe agent text; a tool-appended link is
      outside any repository rule.
- [x] 2.2 Add tests for `main()` in `tests/test_check_no_session_link.py`:
      clean message → 0, planted link → 1 and the offending line on stderr,
      no argument → 2. The refusal case also claims
      `foundation/a-commit-message-containing-a-coding-session-link-is-refused`.
- [x] 2.3 `uv run python scripts/check_spec_traceability.py` accounts for the
      gap and reports nothing unclaimed.

## 3. Prose that made the wider promise

- [x] 3.1 `CLAUDE.md`: drop "this is the line that does it"; say what the rule
      does and does not reach.
- [x] 3.2 `CHANGELOG.md` `[Unreleased]`: rewrite the entry to match, and say
      how it relates to the `attribution.sessionUrl` entry.

## 4. Verification

- [x] 4.1 Re-run UAT cases 1, 3, 4 and replace their "Last agent run" lines with
      what was seen. Do not mark any passed.
- [x] 4.2 `uv run pytest`, `ruff check`, `ruff format --check`,
      `uvx pre-commit run --all-files`.
