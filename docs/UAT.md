# User acceptance tests

The things a test suite cannot judge: whether the output looks right, reads
right, or works the way a person expected. Each case is judged by a human, and
the verdict is an act only the owner can perform — that is what stops UAT from
going quietly stale while the suite stays green.

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

An agent may run the commands and report what it saw. It may not pass a case —
that is the whole point of the gate.

So the two halves are kept apart:

- **Last agent run** — the commands were executed and this is what came back. An
  agent writes this. It is evidence, not a verdict.
- **The verdict** — a person looked at that evidence and accepted it. It is not a
  line in this file. It is something the owner does, at the gate the case sits
  at, that the agent has no way to do for them:

  | The case runs | The verdict is |
  | --- | --- |
  | before the PR | the owner **merging** the PR that carries the evidence |
  | before the commit | the owner's **answer in conversation**, recorded word for word (below) |
  | against a release candidate | the owner **cutting the stable tag** |

  The agent cannot merge or approve (both are denied in `.claude/settings.json`)
  and does not cut a stable tag (`CLAUDE.md`).

Why the verdict is an act rather than a line: the first version of this file had
`Last passed` dates that an agent had written after running the commands itself.
Everything was green and nothing had been reviewed, which is precisely the
failure UAT exists to prevent. A second field, written only by a person, fixed
that for as long as the person wrote it by hand. But writing it means editing
this file, which an owner directing an agent should not have to do, and the
agent can edit the same line. An act the agent has no way to perform needs
neither. See
[Stock ADR 0020](decisions/stock-0020-uat-verdict-is-the-owners-act.md).

**A verdict given in conversation** — the one case that has to be judged before
anything is committed — is recorded by the agent, never inferred by it. The
agent asks a plain yes/no question naming exactly what to look at, using the
app's own question prompt where it has one and plain chat where it does not.
It then writes the owner's own words, the date, and which of the two was used:

```markdown
- **Last verdict:** YYYY-MM-DD, for `<change>`: "<the owner's words>" (prompt | chat)
```

An agent that writes a verdict nobody gave has broken the gate, exactly as
before; the difference is that the quotation and the conversation can be checked
against each other.

`Last agent run` dates are **batched**. They are updated as part of the next
real change rather than each earning its own pull request.

## Case format

```markdown
### N. <what a person is checking>

- **Command:** the exact thing to run
- **Expect:** what you should see, specifically enough to be wrong
- **Verdict:** merging the PR | in conversation, before the commit | cutting the stable tag
- **Last agent run:** YYYY-MM-DD — what came back
```

When the verdict is given in conversation, a `Last verdict` line follows.

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
- **Verdict:** merging the PR.
- **Last agent run:** 2026-11-13, for the change that made the verdict the
  owner's act (Stock ADR 0020) — from tracked files only, with the change
  staged: 50 passed, `ruff check` and `ruff format --check` clean, the
  traceability guard `17/21` claimed with 4 declared gaps, and
  `pyproject.toml` in the rehearsal copy reads `version = "0.7.0"`, agreeing
  with the working tree.

### 2. The guard's failure output tells a human what to do

- **Command:** add a scenario to `openspec/specs/foundation/spec.md` with no
  claiming test, run `mise run trace`, then remove it again.
- **Expect:** the scenario is named, located by file and line, and followed by a
  `fix:` line you could paste. Judgement call: could someone who has never seen
  this repo act on the output without reading the guard's source?
- **Verdict:** merging the PR.
- **Last agent run:** 2026-10-07 — in a scratch copy of the prep branch, an
  added scenario with no claiming test was named
  (`foundation/probe-scenario-nobody-claims`), located at `spec.md:213`, and
  given a pasteable `fix:` line; exit 1. The tracked tree was not touched.

### 3. A declared gap reads as a decision, not an oversight

- **Command:** `mise run trace`, then read
  `[tool.graftwork.traceability]` in `pyproject.toml`.
- **Expect:** the summary line accounts for the gap (`… , 1 allowed without
  one`), and every declared reason still holds today. A reason that has quietly
  stopped being true is exactly what this case exists to catch.
- **Verdict:** merging the PR.
- **Last agent run:** 2026-11-13, for the Stock ADR 0020 change —
  `17/21 scenarios claimed by tests, 4 allowed without one`. The change does
  not touch `pyproject.toml` (`git diff --cached --quiet -- pyproject.toml`),
  so the four reasons are the ones accepted with `owner-opens-pull-requests`.
  I re-read them against this change: none mentions `Last passed` or
  `docs/UAT.md`, and all four still read as true to me.

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

- **Verdict:** in conversation, before the commit. A PR is too late for this
  case.
- **Last agent run:** 2026-11-13, for the Stock ADR 0020 change — a
  docs-only change with no proposal, design or delta spec. Scanned the added
  lines of `git diff --cached -- . ':!docs/UAT.md'` (8 files, 187 added lines,
  counted with `git diff --numstat`; this file's own edits are not in that
  count, and I read them instead). Found no names, usernames, places, email
  addresses, web addresses, repository names, token-like strings or session
  identifiers, and no zero-width characters. People appear only as "the
  owner" and "the maintainer". The only specifics are Stock ADR numbers, three
  dates, one sentence quoted from this file's earlier case 3 entry, and the
  maintainer's own report, in Stock ADR 0020, that they wrote the `Last passed`
  lines themselves.
- **Last verdict:** 2026-11-13, for the Stock ADR 0020 change: "Yes, it reads
  clean" (prompt)

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
- **Verdict:** cutting the stable tag. The owner does it, on the commit the
  candidate points at, only once they have accepted what this case found.
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

---

## Adding cases

A case belongs here when the check needs human senses or human judgement —
looking at rendered output, reading generated prose, holding a printed part. If
a test could make the call instead, write the test.
