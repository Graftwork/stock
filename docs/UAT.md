# User acceptance tests

The things a test suite cannot judge: whether the output looks right, reads
right, or works the way a person expected. Each case is run by a human, and the
`Last passed` date is the point — it is what stops UAT from going quietly stale
while the suite stays green.

**Run these before opening the PR and before archiving the change.** Not after.
The archive is one-way, and a PR is the wrong place to discover the concept was
wrong. See [Ways of working](../WORKFLOW.md#uat-is-a-gate-and-it-comes-before-the-pr).

The one exception is a case marked **post-release**, which verifies the release
itself and therefore cannot run until the tag exists. Those run at step 8 of
[the release sequence](RELEASING.md#8-run-the-post-release-uat-cases). A case is
post-release only if it genuinely cannot be checked earlier — it is not a way to
defer an awkward case past the gate.

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

Run before the PR, against the working tree, because the tag does not exist yet.
Case 4 is the same check against the real tag once it does.

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
- **Last passed:** 2026-08-16 — 16 passed, ruff clean.

### 2. The guard's failure output tells a human what to do

- **Command:** add a scenario to `openspec/specs/foundation/spec.md` with no
  claiming test, run `mise run trace`, then remove it again.
- **Expect:** the scenario is named, located by file and line, and followed by a
  `fix:` line you could paste. Judgement call: could someone who has never seen
  this repo act on the output without reading the guard's source?
- **Last passed:** 2026-08-16

### 3. A declared gap reads as a decision, not an oversight

- **Command:** `mise run trace`, then read
  `[tool.graftwork.traceability]` in `pyproject.toml`.
- **Expect:** the summary line accounts for the gap (`… , 1 allowed without
  one`), and every declared reason still holds today. A reason that has quietly
  stopped being true is exactly what this case exists to catch.
- **Last passed:** 2026-08-16

### 4. The published tag is actually graftable — *post-release*

Case 1 rehearses this against the working tree. This is the real thing, and it is
the only check that catches a tag pushed to the wrong commit, a tag never pushed,
or a file that is gitignored in a way nobody noticed.

- **Command:**

  ```bash
  git clone --branch v<X.Y.Z> --depth 1 git@github.com:Graftwork/stock.git /tmp/graft-real
  rm -rf /tmp/graft-real/.git
  cd /tmp/graft-real && mise trust && mise install && uv sync && mise run check
  ```

- **Expect:** green, and `pyproject.toml` reads `version = "<X.Y.Z>"` — the tag
  and the file agree. Check the README's own graft snippet names this tag too.
- **Last passed:** never — v0.2.0 is not released yet.

---

## Adding cases

A case belongs here when the check needs human senses or human judgement —
looking at rendered output, reading generated prose, holding a printed part. If
a test could make the call instead, write the test.
