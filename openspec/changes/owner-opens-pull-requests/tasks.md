## 1. Apply

- [x] 1.1 In `pyproject.toml`, reword the reason on the declared gap for
      `foundation/a-pull-request-or-issue-contains-no-session-link` (the id is
      unchanged): keep that the suite cannot observe what an agent writes, and
      drop the sentence presenting the `session-links` workflow's stripping as
      the safeguard.
- [x] 1.2 Add a `CHANGELOG.md` `[Unreleased]` entry: what changed in
      *Coding Session Links Are Not Disclosed*, and for grafted projects, re-copy
      the requirement and the gap reason.
- [x] 1.3 Run `uv run pytest`, `uv run ruff check .`,
      `uv run ruff format --check .`,
      `uv run python scripts/check_spec_traceability.py` (expect 17 of 21
      claimed, 4 allowed without one) and `uvx pre-commit run --all-files`.
- [x] 1.4 `openspec validate owner-opens-pull-requests` passes.

## 2. UAT, before the PR and before the archive

- [ ] 2.1 Case 4, the artifacts read clean to a stranger: read `proposal.md`,
      `design.md`, the delta spec and `git diff --cached` before committing.
      Record the agent run; a person records **Last passed**.
- [ ] 2.2 Case 3, a declared gap reads as a decision: run the guard and read the
      reworded reason. Record the agent run; a person records **Last passed**.

## 3. Hand over and archive

- [ ] 3.1 Push the branch and hand the owner the pull request's title and body.
      The owner opens it.
- [ ] 3.2 After the owner accepts the UAT cases:
      `openspec archive owner-opens-pull-requests -y`, then confirm
      `openspec/specs/foundation/spec.md` carries the new paragraph, both
      scenario titles are unchanged, and no relative link in the archived
      artifacts went dead. Archive moves the change one directory deeper and
      does not rewrite links, so the `docs/decisions/` links in `proposal.md`
      and `design.md` need one more `../` afterwards (four in all).
- [ ] 3.3 Re-run the checks from 1.3 and push. The owner merges.
