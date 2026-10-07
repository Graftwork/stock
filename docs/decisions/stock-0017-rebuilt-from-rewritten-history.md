# Stock ADR 0017: Rebuilt from rewritten history

- **Status:** accepted
- **Date:** 2026-10-07

## Context

Between August and October 2026, cloud coding sessions added a
`Claude-Session:` trailer to commit messages, each a link to the private
session that produced the commit. [`foundation`'s "Coding Session Links Are
Not Disclosed"](../../openspec/specs/foundation/spec.md) stops new ones, but
it cannot remove the ones already in history: 26 of the 54 commits on `main`
carried one, plus one more on the rc-fix commit tagged `v0.4.0` that never
merged to `main` — under every tag from `v0.2.0` to `v0.7.0`. Only a history
rewrite removes them, and rewriting a repository in place breaks every
existing clone without telling it why.

## Decision

Publish a new repository built from rewritten history; keep the old one.

- The old repository was renamed `Graftwork/stock-archive` and stays private.
  This repository took the original name.
- History is **rewritten, not squashed**: every commit is kept and only commit
  messages changed. A `Claude-Session:` line, or a line that is only a session
  link, was dropped; the blank lines that left behind were collapsed.
  `Co-Authored-By` lines were kept. Annotated tag messages carried no links
  and are unchanged.
- Only `main` and the 20 tags were carried over. Branches and pull-request
  refs were not.
- **Pull request and issue numbers, and commit hashes, cited anywhere in this
  repository before 2026-10-07 refer to the archive, not to this
  repository.** They were left as written rather than edited one by one. This
  repository's own pull request numbering starts again at 1, so a `#NN` from
  before the rebuild — in a document or a commit subject — may link to an
  unrelated pull request here.

Measured before the first push, against a fresh mirror of the old repository
(`git rev-list`, `git rev-parse <ref>^{tree}`, `git grep`):

| | Before | After |
|---|---|---|
| Commits on `main` | 54 | 54 |
| Commits on `main` and tags | 55 | 55 |
| Commit messages with a session link | 27 | 0 |
| Refs whose tree differs (`main` and 20 tags) | — | 0 of 21 |
| `Co-Authored-By` lines on `main` | 110 | 110 |
| Commits whose author, committer, dates or parents changed | — | 0 |

The file contents of every commit are identical, so the guard's own test
fixtures still contain placeholder links (`session_01ABC` and similar); no
real session id appears in any file.

Old to new commit at each ref:

| Ref | Old | New |
|---|---|---|
| `main` | `6a7c944` | `e902da6` |
| `v0.1.0`, `v0.1.1`, `v0.1.2` | unchanged | unchanged |
| `v0.2.0` | `99cec36` | `c1a075c` |
| `v0.3.0-rc.1` | `eae03eb` | `9818958` |
| `v0.3.0-rc.2` | `7667602` | `129cc55` |
| `v0.3.0` | `4ec60d1` | `1db5cc3` |
| `v0.4.0-rc.1` | `d7c449a` | `350db12` |
| `v0.4.0-rc.2`, `v0.4.0` | `51ec560` | `73d3ad0` |
| `v0.5.0-rc.1` | `3fc7b50` | `83c888f` |
| `v0.5.0-rc.2` | `2ba4d44` | `f6cd387` |
| `v0.5.0-rc.3`, `v0.5.0` | `57905e9` | `822d376` |
| `v0.5.1-rc.1`, `v0.5.1` | `b42c526` | `e076b49` |
| `v0.6.0-rc.1`, `v0.6.0` | `3ed5e22` | `51595d0` |
| `v0.7.0-rc.1`, `v0.7.0` | `7fccde9` | `4a053c9` |

Every number above came from real command output.

## Consequences

- Tag names are unchanged, so a grafted project that records its Stock
  version by tag (`stock-version` in `pyproject.toml`) needs no change. A
  project that cites a Stock commit hash should read it through the table
  above.
- Links into the archive are dead for anyone without access to it. The
  reasoning they pointed at is kept in the documents that cite them.
- Clones of the old repository do not share history with this one. Re-clone
  rather than pull.

## Alternatives considered

- **Rewrite the existing repository in place.** Rejected: it silently breaks
  every clone and keeps pull requests whose descriptions and branches still
  carry links.
- **Squash to one commit.** Rejected: it throws away the history the
  CHANGELOG and ADRs are written against.
- **Edit every old hash and `#NN` to point at the new repository.** Rejected:
  about forty edits across documents, workflows and archived OpenSpec changes,
  and it cannot reach commit subjects without a further rewrite. One dated
  note explains all of them.
