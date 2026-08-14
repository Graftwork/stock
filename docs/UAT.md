# User acceptance tests

The things a test suite cannot judge: whether the output looks right, reads
right, or works the way a person expected. Each case is run by a human, and the
`Last passed` date is the point — it is what stops UAT from going quietly stale
while the suite stays green.

**Run these before opening the PR and before archiving the change.** Not after.
The archive is one-way, and a PR is the wrong place to discover the concept was
wrong. See [Ways of working](../WORKFLOW.md#uat-is-a-gate-and-it-comes-before-the-pr).

An agent may run the commands and report what it saw. It may not mark a case
passed — that is the whole point of the gate. Update `Last passed` yourself when
you have looked at the output.

## Case format

```markdown
### N. <what a person is checking>

- **Command:** the exact thing to run
- **Expect:** what you should see, specifically enough to be wrong
- **Last passed:** YYYY-MM-DD (or `never`)
```

---

## Stock's own cases

### 1. A fresh graft is green before anyone writes code

- **Command:**

  ```bash
  git clone --branch v0.2.0 --depth 1 git@github.com:Graftwork/stock.git /tmp/graft-check
  rm -rf /tmp/graft-check/.git
  cd /tmp/graft-check && mise trust && mise install && uv sync && mise run check
  ```

- **Expect:** lint clean, suite passes, no edits needed to get there. If the
  first command a new project runs is red, the foundation has broken its one
  promise.
- **Last passed:** 2026-08-14 — run against the working tree rather than a
  published tag, since v0.2.0 is not tagged yet. 16 passed.

### 2. The guard's failure output tells a human what to do

- **Command:** add a scenario to `openspec/specs/foundation/spec.md` with no
  claiming test, run `mise run trace`, then remove it again.
- **Expect:** the scenario is named, located by file and line, and followed by a
  `fix:` line you could paste. Judgement call: could someone who has never seen
  this repo act on the output without reading the guard's source?
- **Last passed:** 2026-08-14

### 3. A declared gap reads as a decision, not an oversight

- **Command:** `mise run trace`, then read
  `[tool.graftwork.traceability]` in `pyproject.toml`.
- **Expect:** the summary line accounts for the gap (`… , 1 allowed without
  one`), and every declared reason still holds today. A reason that has quietly
  stopped being true is exactly what this case exists to catch.
- **Last passed:** 2026-08-14

---

## Adding cases

A case belongs here when the check needs human senses or human judgement —
looking at rendered output, reading generated prose, holding a printed part. If
a test could make the call instead, write the test.
