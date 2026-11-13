# Stock ADR 0019: A UAT verdict is the owner's act, not a line in a file

- **Status:** accepted
- **Date:** 2026-10-23
- **Supersedes:** the `Last passed` mechanism in
  [Stock ADR 0006](stock-0006-uat-is-a-human-gate.md). ADR 0006's other
  decisions stand: UAT is a human gate, and its cases run before the PR and
  before the archive.

## Context

[Stock ADR 0006](stock-0006-uat-is-a-human-gate.md) gave each case in
[`docs/UAT.md`](../UAT.md) a `Last passed` date that only a person may write,
beside a `Last agent run` the agent may write. The split was right. The agent
must not be the party that closes the gate.

The rule worked here. Asked on 2026-11-13, the maintainer reports writing
these lines themselves. One entry, case 3's of 2026-10-15, records that it was
*"Entered by the agent at the maintainer's instruction."* Two things about the
mechanism do not travel, though.

**Writing the line is a technical act.** "A person edits a Markdown file in the
right place, in the right format" is something Stock's maintainer can do.
Stock's audience is a product owner directing an agent, who is not assumed to
edit repository files. In a project grafted from Stock, a gate that only works
if the owner does that is a gate the owner will route through the agent, and
then the line is the agent's.

**Nothing but trust separates the two fields.** Both are lines in one file,
and the agent can edit that file. The history cannot tell them apart either.
Every commit that has changed a `Last passed` line carries an agent co-author
trailer: 8 of 8, measured with `git log -G'Last passed' -- docs/UAT.md`. A
trailer shows an agent worked on the commit, not which lines it wrote. So a
reader cannot check from the repository who wrote a verdict.

The rule protects **who decides**, not **who types**. Each gate already has an
act that only the owner can perform.

## Decision

`Last passed` is removed. Each case keeps `Command`, `Expect` and
`Last agent run`, which is the evidence. It gains a `Verdict` line naming the
owner's act at the gate where the case sits:

| The case runs | The verdict is |
| --- | --- |
| before the PR | the owner merging the PR that carries the evidence |
| before the commit | the owner's answer in conversation, recorded word for word |
| against a release candidate | the owner cutting the stable tag |

- **Merging** is denied to the agent in `.claude/settings.json`, along with
  approving and enabling auto-merge
  ([Stock ADR 0018](stock-0018-owner-opens-agent-pushes.md)).
- **Cutting the stable tag** joins the never-list in `CLAUDE.md`'s
  *The owner opens, accepts and watches* rule. The tag is what a graft clones,
  so it is the release verdict. This half is a house rule, not a deny entry.
  A tag push looks the same to the permission system whether it is a
  candidate or stable, and candidates are not verdicts.
- **A verdict given in conversation** covers the stranger-read case, which must
  be judged before anything is committed, so a PR is too late for it. The agent:
  - asks a plain yes/no question naming what to look at;
  - uses the app's own question prompt where it has one, and falls back to
    plain chat;
  - records the owner's words, the date, and which of the two was used.

  It records a verdict and never infers one.

## Consequences

- **The agent has no line to fill in for cases judged at merge or at the
  tag.** The failure ADR 0006 was written against, an agent recording a pass
  nobody gave, cannot happen there by construction.
- **The conversation verdict still relies on the agent's honesty.** But it now
  carries the owner's own words, which can be checked against the conversation,
  rather than a paraphrase.
- **This is the same pattern planned for projects whose owner never touches a
  repository file:** the person decides, the agent records, and the record
  says how the decision was given. Stock uses it first.
- **Staleness is read from history, not from a field.** `git log docs/UAT.md`,
  together with the PR that merged each `Last agent run` update, shows when a
  person last accepted a case. That is less glanceable than a date in the
  file. It also cannot be written by the agent, which a line in the file can.
- **An archive can now come before the verdict on the same branch.** Stock
  sometimes archives in the same PR as the change. The archive is one-way
  inside OpenSpec, but on an unmerged branch it is one commit, which git can
  revert if the owner does not merge. What stays one-way is the archive
  reaching `main`, and that happens only at the owner's merge.
- **Stock's maintainer gives up a line they wrote themselves.** The merge and
  the tag, which they already perform, carry the same meaning.
- **Existing entries.** `Last passed` lines are removed. They remain in git
  history. Case 4's entry is replaced by the first verdict recorded in the new
  format, which was given for this change.
- **Grafted projects** migrate by replacing `Last passed` with `Verdict` in their
  own cases. See `CHANGELOG.md`.

## Alternatives considered

- **Keep `Last passed`, and have the owner write it.** That is the rule as
  written, and Stock's maintainer followed it. But it asks the owner of every
  grafted project to edit a repository file by hand, which the audience should
  not need, and it leaves the verdict where the agent can write it too.
- **Keep `Last passed`, written by the agent at the owner's instruction.** The
  file records this once (case 3, 2026-10-15). It makes the line a transcript
  of a chat message with nothing to check it against, which is weaker than the
  merge it duplicates.
- **Only the app's question prompt, no chat fallback.** The prompt is stronger
  evidence, because the question and the answer are separate events. But it
  exists in some agent apps and not others. A rule that needs it would tie Stock
  to one agent, so the record says which was used instead.
