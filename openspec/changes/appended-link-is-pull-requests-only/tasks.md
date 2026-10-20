## 1. Apply

- [x] 1.1 In `docs/decisions/stock-0018-owner-opens-agent-pushes.md`, record the
      issue measurements (dates, routes, sample sizes, what was not tested) and
      the sorting-office confirmation for pull requests, and replace the
      Consequences bullet that says the spec is still wrong.
- [x] 1.2 Fix the link in `docs/decisions/stock-0011-resync-in-flight-graft-skill.md`
      to `stock-resync-in-flight-graft`.
- [x] 1.3 Correct `docs/GOING_PUBLIC.md` step 7: an agent cannot change the
      settings, but can read a public repository's rules back.
- [x] 1.4 Add the `CHANGELOG.md` `[Unreleased]` entries, with migration steps
      for grafted projects.
- [x] 1.5 Run `uv run pytest`, `uv run ruff check .`,
      `uv run ruff format --check .`,
      `uv run python scripts/check_spec_traceability.py` (expect 17 of 21
      claimed, 4 allowed without one) and `uvx pre-commit run --all-files`.
- [x] 1.6 `openspec validate appended-link-is-pull-requests-only` passes.

## 2. UAT, before the archive and before the PR

- [ ] 2.1 Case 4, the artifacts read clean to a stranger. Record the agent run;
      a person records **Last passed**. Case 3 is not affected: the declared gap
      is unchanged.

## 3. Archive, then hand over

- [ ] 3.1 After the owner accepts case 4, archive the change on this branch,
      before the pull request is opened, so one push carries everything and the
      review runs once. Confirm the new wording is in
      `openspec/specs/foundation/spec.md`, both scenario titles are unchanged,
      and the `docs/decisions/` links in the archived `proposal.md` and
      `design.md` gain a fourth `../`.
- [ ] 3.2 Re-run the checks from 1.5, push, and hand the owner the title and
      body. The owner opens the pull request and merges it.
