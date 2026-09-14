# Going public

A repository stays private by default, which means going public is a deliberate
event, not a setting you flip on a whim. It is also close to irreversible: once
a repository is public, its entire history — including whatever was in it
before anyone thought to check — can be cloned, forked, and indexed by the
time a problem is noticed. Fix what needs fixing first.

This checklist exists because Stock itself went through it. Every item below
traces to something that was actually missing or actually wrong here — a
missing `LICENSE`, a doc that stated its own reasoning incorrectly, a stale
claim that quietly became false, a dead cross-reference a real re-sync caught
— not something anticipated in advance. That is deliberate: see
[Stock ADR 0015](decisions/stock-0015-going-public-checklist.md).

**This runs once**, immediately before a repository's visibility actually
changes — not on every release the way [`docs/UAT.md`](UAT.md)'s cases do, and
not part of [`docs/RELEASING.md`](RELEASING.md)'s per-version sequence. If a
project stays private for years and only later decides to go public, work this
list fresh at that point rather than trusting whatever was true when the
project was grafted.

## 1. License and copyright

- Confirm a `LICENSE` file exists and states a **deliberate** choice. Silence
  is not neutral — no `LICENSE` means default exclusive copyright, which
  blocks anyone else from legally using or forking what you are about to
  share.
- Confirm the copyright holder is an actual legal person or entity — not a
  project or repo name that is not itself a legal entity. See
  [Stock ADR 0014](decisions/stock-0014-license-and-copyright.md) for the
  worked reasoning and the same question asked and answered for real.
- If the license uses a `NOTICE` file (Apache-2.0 and similar), check any
  cross-references inside it actually resolve. Stock's own `NOTICE` shipped
  with a dangling pointer to sections of two other files that didn't mention
  what it claimed — caught only once a real re-sync onto another project
  wrote its own `NOTICE` and declined to copy the mistake forward.
- Record the decision as an ADR. This is exactly the kind of deliberate
  choice a future reader might otherwise mistake for drift.

## 2. Full-history secret scan

A pre-commit secret scanner only guards commits made after it was installed.
Going public exposes everything before that too.

- Scan the **entire** history, not just the working tree:
  `git log --all -p`, checked against common credential patterns (cloud
  provider keys, private key blocks, common API token shapes) — not just the
  scanner's own baseline.
- Also run the project's own scanner across the current tree
  (`detect-secrets scan --all-files` or equivalent) as a second, narrower
  pass, and confirm any hits are in gitignored/untracked paths, not tracked
  content.

## 3. Cross-repo reference check

Grep the whole repository for links to other repositories — sibling
projects, forks, related work referenced in ADRs, changelogs, or skills:

```bash
grep -rln "github.com/<your-org>/" --include='*.md' .
```

For every match, confirm the linked repository is **already public**, or will
go public in the same window. A link into a repository that stays private
becomes a dead link the moment this one goes public — a 404 or a login
prompt for anyone who clicks through, with no way for them to know why.

## 4. Stale conditional wording sweep

Grep for words whose truth depends on the repository's current state:
`private`, `internal`, `confidential`, `not yet released`, `unreleased`.
Every hit needs a judgment call, not a reflexive edit:

- Is it still true?
- Was it ever actually the *real* reason for whatever it's justifying — or
  just a convenient-sounding one that happened to also be true at the time?
  Stock's own `docs/CONTRIBUTING.md` had exactly this problem: it attributed
  a workflow to the repository being private, when the actual cause (Claude
  Code session owner-scoping) had nothing to do with visibility at all.

## 5. A final, whole-repository stranger read

Every individual change already gets a "read as a stranger" pass — see
[`docs/UAT.md`](UAT.md) case 4. That happens per diff, though, not across the
whole repository at once. Before flipping visibility, do one more pass over
the repository **as it will actually appear** to a first-time visitor:
`README.md`, every doc, and anything in git history a stranger might
plausibly go looking at (author names, commit messages, anything that reads
as more personal than it needs to).

This is human-judgment work, the same shape as `docs/UAT.md`'s own cases: an
agent can read the repository and report what it saw, but it cannot be the
one to decide the repository is ready. Only a person can.

## 6. GitHub-side repository settings

None of this is checkable or settable by an agent session as of this
writing — no tool access to GitHub's branch-protection API. It's a manual
pass, in Settings → Branches (or the newer Rulesets UI, depending on what
your account shows).

- **Require a pull request before merging** on the default branch. Turns
  "changes reach `main` by branch and PR, never a direct commit" from a
  written convention into something GitHub actually enforces.
- **Require the project's CI status check to pass** before merging.
- **Disallow force pushes** to the default branch. This is the one that
  matters most: `docs/RELEASING.md`'s whole tag model depends on the
  default branch's history being stable and append-only — a force-push
  (even an accidental one) can silently invalidate every "tag on the exact
  commit" guarantee the release process makes.
- **Disallow deletion** of the default branch.
- Check whether CI secrets (coverage tokens, review-bot tokens, and similar)
  are scoped sensibly now that Actions run logs become publicly visible.
- Repo description and topics, if discoverability matters to you.

## 7. Flip visibility — last, deliberately

Only once everything above is settled. The same principle as *Context Is Not
Content* applies here, just at the scale of a whole repository instead of one
file: the window closes at the moment of the flip, not at the moment someone
notices a problem, and there is no undo that reaches whatever was already
cloned, forked, or indexed in between.
