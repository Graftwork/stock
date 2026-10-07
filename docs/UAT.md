# User acceptance tests

The things a test suite cannot judge: whether the output looks right, reads
right, or works the way a person expected. Each case is judged by a human, and
the `Last passed` date is the point — it is what stops UAT from going quietly
stale while the suite stays green.

**Run these before opening the PR and before archiving the change.** Not after.
The archive is one-way, and a PR is the wrong place to discover the concept was
wrong. See [Ways of working](../WORKFLOW.md#uat-is-a-gate-and-it-comes-before-the-pr).

The one exception is a case marked **needs a published tag**, which verifies the
release itself and so cannot run until a tag exists. Those run against a release
**candidate** — `vX.Y.Z-rc.N` — at
[step 8 of the release sequence](RELEASING.md#8-run-the-tag-dependent-uat-cases-against-the-candidate),
which is what lets them happen before the release rather than after it. A case
earns this marking only if it genuinely cannot be checked earlier; it is not a
way to defer an awkward case past the gate.

An agent may run the commands and report what it saw. It may not mark a case
passed — that is the whole point of the gate.

Because that line is easy to blur, each case carries **two** dates:

- **Last agent run** — the commands were executed and this is what came back. An
  agent may write this. It is evidence, not a verdict.
- **Last passed** — a person looked at that output and accepted it. Only a
  person writes this line.

The distinction earns its keep: the first version of this file had `Last passed`
dates that an agent had written after running the commands itself. Everything was
green and nothing had been reviewed, which is precisely the failure UAT exists to
prevent. Two fields make that mistake impossible to make quietly.

Dates are **batched** — they are updated as part of the next real change rather
than each earning its own pull request.

## Case format

```markdown
### N. <what a person is checking>

- **Command:** the exact thing to run
- **Expect:** what you should see, specifically enough to be wrong
- **Last agent run:** YYYY-MM-DD — what came back
- **Last passed:** YYYY-MM-DD (or `never`) — a person's judgement only
```

---

## Stock's own cases

### 1. A fresh graft is green before anyone writes code

Run before the PR, against the working tree, because the tag does not exist yet.
Case 5 is the same check against the real published tag once it does.

- **Command:**

  ```bash
  rm -rf /tmp/graft-check && mkdir -p /tmp/graft-check
  git ls-files -z | xargs -0 tar cf - | tar xf - -C /tmp/graft-check
  cd /tmp/graft-check && uv sync && uv run pytest && uv run ruff check .
  ```

  `git ls-files` is what makes this a real rehearsal: it copies only tracked
  files, so anything you forgot to `git add` is missing here exactly as it would
  be missing from a clone.

- **Expect:** lint clean, suite passes, no edits needed to get there. If the
  first command a new project runs is red, the foundation has broken its one
  promise.
- **Last agent run:** 2026-10-07 — on the `0.7.0` prep branch, from tracked
  files only: 50 passed, `ruff check` and `ruff format --check` clean, the
  traceability guard `17/21` claimed with 4 declared gaps, and
  `pyproject.toml` in the rehearsal copy reads `version = "0.7.0"`, agreeing
  with the working tree.
- **Last passed:** 2026-10-07, against `v0.7.0-rc.1` — accepted by the maintainer
  after reading the output above.

### 2. The guard's failure output tells a human what to do

- **Command:** add a scenario to `openspec/specs/foundation/spec.md` with no
  claiming test, run `mise run trace`, then remove it again.
- **Expect:** the scenario is named, located by file and line, and followed by a
  `fix:` line you could paste. Judgement call: could someone who has never seen
  this repo act on the output without reading the guard's source?
- **Last agent run:** 2026-10-07 — in a scratch copy of the prep branch, an
  added scenario with no claiming test was named
  (`foundation/probe-scenario-nobody-claims`), located at `spec.md:213`, and
  given a pasteable `fix:` line; exit 1. The tracked tree was not touched.
- **Last passed:** 2026-10-07, against `v0.7.0-rc.1` — accepted by the maintainer
  after reading the output above.

### 3. A declared gap reads as a decision, not an oversight

- **Command:** `mise run trace`, then read
  `[tool.graftwork.traceability]` in `pyproject.toml`.
- **Expect:** the summary line accounts for the gap (`… , 1 allowed without
  one`), and every declared reason still holds today. A reason that has quietly
  stopped being true is exactly what this case exists to catch.
- **Last agent run:** 2026-10-07 — `17/21 scenarios claimed by tests, 4 allowed
  without one`; all four reasons printed for reading, none changed since
  `v0.6.0`. All four still read as true to me; the fourth
  (`a-pull-request-or-issue-contains-no-session-link`) is accurate but not
  exhaustive, as recorded on 2026-10-04.
- **Last passed:** 2026-10-07, against `v0.7.0-rc.1` — the maintainer accepted
  that each declared reason still holds.

### 4. The artifacts read clean to a stranger

The one check that has to happen **before the commit**, not before the PR. Git
history is rewritten rather than edited, so this case is worth nothing if it runs
late. See [Context is not content](../WORKFLOW.md#context-is-not-content).

- **Command:** read the change's `proposal.md`, `design.md`, delta specs and any
  new code as someone with no knowledge of the project would. Then:

  ```bash
  git diff --cached
  ```

- **Expect:** nothing that identifies a real person, place, account, employer,
  or medical or financial circumstance. Requirements read as categories and
  rules. Where a specific *is* present, you recognise it as one you were asked
  about and agreed to.

  Judgement call, and the one to be honest about: if you needed project context
  to understand why a detail is harmless, a stranger reading the public
  repository does not have it.

- **Last agent run:** 2026-10-07 — scanned the added lines of
  `git diff v0.6.0` against the prep working tree (14 files, 954 added lines):
  no token-like strings, no zero-width characters, no usernames or personal
  names. One line mentions the pattern `claude.ai/code/session` as text; none
  contains a real session identifier. The only email-shaped text is the
  `git@github.com` clone address and the `noreply@anthropic.com` co-author
  address. This covers the whole release.
- **Last passed:** 2026-10-07, against `v0.7.0-rc.1` — accepted by the maintainer
  after reading the output above and the scan's findings.

### 5. The published tag is actually graftable — *needs a published tag*

Case 1 rehearses this against the working tree. This is the real thing, and it is
the only check that catches a tag pushed to the wrong commit, a tag never pushed,
or a file that is gitignored in a way nobody noticed.

- **Command:**

  ```bash
  # against the release candidate, before the stable tag exists
  git clone --branch v<X.Y.Z>-rc.<N> --depth 1 git@github.com:Graftwork/stock.git /tmp/graft-real
  rm -rf /tmp/graft-real/.git
  cd /tmp/graft-real && mise trust && mise install && uv sync && mise run check
  ```

- **Expect:** green, and `pyproject.toml` reads `version = "<X.Y.Z>"` — the
  candidate and the file agree on the version being released. Check the README's
  graft snippet names the **stable** tag, not the candidate.

  If this passes, the stable tag goes on the exact commit the candidate points
  at. If it fails, fix it and cut `-rc.<N+1>`; nothing has been released.
- **Last agent run:** 2026-10-07 — against `v0.7.0-rc.1` (commit `7fccde9`,
  published as a pre-release): a shallow clone of the tag with `.git` removed
  gave `pytest` 50 passed, `ruff check` and `ruff format --check` clean, the
  traceability guard `17/21` with 4 declared gaps, `pyproject.toml` reading
  `version = "0.7.0"`, and the README graft snippet naming the stable
  `v0.7.0`. `ci.yml` carries the pinned `mise` version, and CI on `main` at
  that commit ran green with the pin (the `jdx/mise-action` step succeeded).
  `sorting-office` was then re-synced from the candidate (its PRs #27 to #30,
  one per CHANGELOG entry), and I checked the result from this side: its
  `main` (`d9193b7`) has `claude-review.yml`, `session-links.yml`,
  `check_no_session_link.py`, `test_review_gate.py` and
  `test_check_no_session_link.py` byte-identical to the tag (blob hashes),
  `stock-version = "0.7.0-rc.1"`, the pinned `mise` version in its `ci.yml`,
  and CI green. The session that did the re-sync reports 77 tests passing, the
  guard at `42/46` claimed with 4 declared gaps, and that the `mise` pin
  passed on a cold cache (the first run downloaded the release directly, with
  no API resolution). `mise` is unavailable in the agent environment, so the
  `uv`/`ruff` equivalents ran instead (see `CLAUDE.md`).
- **Last passed:** 2026-10-07, against `v0.7.0-rc.1` — confirmed by the person
  who re-synced `sorting-office` from the candidate (its PRs #27 to #30): it
  worked. After the re-sync its review workflow, session-links workflow, hook
  script and both test files for them were byte-identical to the tag's (blob
  hashes compared), its `stock-version` read `0.7.0-rc.1`, and CI was green on
  `main`. That real graft, not the rehearsal alone, is what this case is
  actually meant to test. (The `v0.6.0` record this replaces is preserved in
  git history, not duplicated here — see the "Case format" section above.)

---

## Adding cases

A case belongs here when the check needs human senses or human judgement —
looking at rendered output, reading generated prose, holding a printed part. If
a test could make the call instead, write the test.
