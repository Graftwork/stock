## Context

The review check's last step is about 90 lines of `bash` inside
`.github/workflows/claude-review.yml` (measured: extracted and counted). It
reads three things: the action's execution file, the GitHub API for comments,
reviews and changed files, and a byte comparison of the two copies of the
workflow file. It then fails, warns or passes.

Its rules were set against real runs and fixed in `#41` and `#44`, and
exercised on the live PRs `#50`, `#51` and `#52`. During `#44` they were also
exercised by a stubbed-`gh` fixture script of several dozen cases (a count I
recalled, not re-measured for this document); that script lived in a scratch
directory and was never committed.

This change commits that approach as tests. The premise it rests on was
checked before writing this: the gate step is the only step with `id: gate`;
slicing the `run: |` block by indentation gives a script that passes
`bash -n`; and the script contains no `${{ … }}` expressions, because every
input arrives through `env:`. So the step can be run outside Actions by
setting those environment variables.

## Goals / Non-Goals

**Goals:**

- Every rule in the requirement is claimed by a test that runs the real gate
  script, so removing or weakening a rule turns the suite red.
- No new dependency in `pyproject.toml`.
- Tests that fail with a message that names the rule, so a reader who has not
  seen the gate can act on it.

**Non-Goals:**

- Testing the live review: whether the plugin follows the "No reviewable
  changes" instruction or reviews again after a push. That is model and plugin
  behaviour; `#51` and `#52` are the only evidence, and the spec says so.
- Testing the `Record when this review started` step or the
  `denied-calls-comment` job. They are not part of the promise: the first
  feeds the gate a timestamp, the second only lists denials.
- Changing the gate. If writing the tests exposes a bug, that is a finding to
  report and fix in its own change, not to fold in here.

## Decisions

**1. Run the real script, extracted from the YAML.** The test finds the step
with `id: gate`, takes its `run: |` block by indentation, writes it to a file
in `tmp_path` and runs it with `bash`. *Alternative: copy the logic into the
test.* Rejected: a copy passes whatever the workflow does. *Alternative:
move the script to `scripts/review_gate.sh` and call it from the workflow.*
Rejected for now: a grafted project copies the workflow as one file, and a
second file is a second thing to migrate and keep in step. Revisit if the
extraction proves brittle.

**2. Slice by indentation; do not parse the YAML.** PyYAML is not a
dependency, and every dependency added to Stock's dev group is inherited by
every grafted project. The extractor asserts it found exactly one step with
`id: gate` and a non-empty script, so a reformatted workflow fails loudly
instead of testing nothing.

**3. A fake `gh` on `PATH`.** The test writes a small `gh` script into
`tmp_path/bin` that answers by endpoint: issue comments, pull request comments,
reviews and files, from JSON the test supplies, and ignores flags the gate
passes (`--paginate`, `--jq`). It applies `--jq` with the real `jq`. The gate's
other inputs are an execution file (a JSON array holding a `result` object
with `is_error`, `permission_denials`), the environment variables, and two
copies of the workflow file for the `cmp` check.

**4. Build inputs in the test file.** A few helper functions build the
execution file, the comments and the file list from keyword arguments, so each
scenario reads as the one thing that differs from a passing run. No fixture
directory unless the helpers grow past what a reader can take in.

**5. `bash` and `jq` are required, not skipped.** If either is missing the
suite fails with a message saying so, because a skipped test is a promise
nobody is checking (ADR 0013). `ubuntu-latest` has both (recalled, not
checked for the current image; the first CI run on this change is the check).
Both are present in the cloud session used to write this (measured:
`jq-1.7`, `bash`).

**6. Beyond the seven claimed scenarios.** A few extra tests do not claim a
scenario: no execution file; a decline note attempted on a pull request that
also changes code, with the changed file's name containing a `%` or control
character (the gate prints it); and the denied list staying on one line and
within its length cap. They protect behaviour the requirement does not need to
state.

## Risks / Trade-offs

- **A refactor of the gate can break the tests.** The tests read the gate out
  of the workflow, so moving it, renaming `id: gate`, or changing how inputs
  arrive means updating the tests. Accepted: that coupling is what makes them
  test the real thing. The extractor's assertions make the failure explicit.
- **Stubs can drift from the real API.** The fake `gh` returns what the gate
  expects: `user.login` of `claude[bot]`, `created_at` on comments,
  `submitted_at` on reviews. If GitHub's shape changes, the stubs still pass.
  Mitigation: the live runs; the field names were read from `#42`'s real
  responses, and the gate's own comment says so.
- **A grafted project that does not run this workflow.** It receives the
  requirement and the tests on re-sync, and the tests fail because there is no
  gate to extract. See Open Questions.
- **Time.** The gate compares ISO timestamps as strings; tests use fixed
  timestamps, so they do not exercise clock or time-zone behaviour.

## Open Questions

- **What a graft without `claude-review.yml` should do.** Options: delete the
  requirement and the tests in its own copy (a written decision, like a
  declared gap); or have Stock's test skip when the workflow is absent (a skip
  that needs a justification of its own). Recommendation: the first. The
  failing test names the cause, and a project that declined the review
  workflow has not made a promise the requirement should keep for it.
  The semver level follows: **Minor** if that counts as additive (every live
  graft already took the workflow in v0.6.0), **Major** if "needs a manual
  decision" counts as intervention. Decide before the CHANGELOG entry.

## Revised before merge

This change was edited in place after its pull request (`Graftwork/stock#56`)
was open, at the maintainer's decision:

- **The "needed tool denied" rule is removed from the gate, and its scenario
  with it.** The rule matched the text `gh pr comment` anywhere in a denied
  Bash command. This pull request's own test file quotes that phrase, so a
  review that ran a Python script reading it failed the gate (measured: the
  20-minute review run on `7f5d9c8` failed on two such denials; reproduced in
  the test harness with a script that only quotes the phrase). Anchoring the
  match was possible, but guessing intent from command text stays brittle, and
  the rule adds nothing: if a tool the review posts with is denied, nothing is
  posted, and the "posted nothing" rule already fails the run and lists the
  denials.
- **A denied tool call never fails the check by itself.** The scenario is now
  "A denied tool call only warns", and "A run that posted nothing fails the
  check" also lists the denied calls.
- **The review check is advisory, not a required check.** That is a repository
  setting, not something the spec or the workflow can enforce, so it lives in
  the CHANGELOG, the workflow's header comment and the ruleset, not in the spec.
  The requirement still says what it always did: a missing review must never
  look like a review. Seven scenarios, so the guard reads `17/21` claimed with
  4 declared gaps.

The measured basis for the decision is the review workflow's run list, runs 28
to 52 (25 runs: 15 green, 9 red, 1 cancelled); 4 of the reds were pull requests
that edit the workflow, which are red by design.
