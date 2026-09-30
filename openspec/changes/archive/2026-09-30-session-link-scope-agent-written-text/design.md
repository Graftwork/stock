# Design

Every number or claim here was measured, derived, or is labelled recalled.

## The premise, checked

The original change rested on: "a repository's own `CLAUDE.md` takes
precedence over the platform's per-session default". Split it in two.

| Claim | Status |
| --- | --- |
| A repo instruction outranks the platform's default instruction to the agent about *what to write* | **Recalled, not tested.** The session's own attribution instructions say a `CLAUDE.md` rule takes precedence over them. No session was run with the rule present and the default asking for a link. |
| A repo instruction can stop a session link in a pull request body | **Measured false** for the GitHub tool path. Two draft PRs (`Graftwork/stock#36`, `#37`), opened in a session whose attribution instructions did not mention a session link, each read back with exactly one line containing `claude.ai/code/session` (the body as returned by the pull request API, read and counted by eye — not a scripted count). In `#37` the agent's own plain footer was replaced by the session-link version. |

The tool appends after the body is written; the two claims differ because one
is about what the agent writes and the other is about what the tool adds.

## What the requirement can and cannot govern

| Artifact | Who writes the link | Can a repository stop it? |
| --- | --- | --- |
| A commit message | the agent, from its instructions | Partly at source (instructions), fully at commit time (the `commit-msg` hook) |
| A PR or issue body, agent-written text | the agent | By instruction; the suite cannot observe it — declared gap |
| A PR or issue body, tool-appended footer | the platform's tool, after the fact | **No.** Not from an instruction, not from a local hook |

The requirement now covers the first two rows and says the third is outside
it. A CI check on pull request bodies would reach the third row; that is a
separate decision, deliberately not made here.

## Why the scenario keeps its title

The first plan renamed the scenario to say "the text an agent writes …", which
changes its id. `openspec archive` refused: with a `MODIFIED` block, a scenario
present in the current spec but absent from the block is an error ("contains
scenario(s) not present in the modified block … to avoid dropping scenarios"),
and a renamed scenario reads as one dropped and one added. Measured against
`@fission-ai/openspec@1.6.0`; the archive aborted with no files changed. The
title stays, and the narrowing lives in the requirement paragraph and the
WHEN/THEN, where the scope is stated in words. The declared gap keeps its id
and only its reason changes. (An in-flight artifact corrected in place, per
the house rule.)

## Alternatives considered

- **Leave the wording, fix only `CLAUDE.md` and the CHANGELOG.** Rejected: the
  spec is the promise that travels into every grafted project. Correcting the
  prose around it and leaving the promise wrong is the inconsistency this
  change exists to remove.
- **Keep the wide scenario and declare it a gap with a longer reason.** A gap
  is a claim that *no test could have kept this promise*; it is not a way to
  keep a promise nothing can keep. Rejected (see ADR 0005).
- **Reach the tool-appended footer with a workflow.** Would need a GitHub
  Action, and it is a separate decision with its own trade-offs. Not here.

## Verified

- The `main()` tests exercise the script's three exits (clean 0, link 1,
  missing argument 2) through its real entry point, not only `check()`.
- Coverage of `scripts/check_no_session_link.py` was 32% before (lines 30–47
  of `main()` and the `__main__` guard uncovered), read from the coverage
  report of `uv run pytest`.
