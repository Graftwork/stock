# Changelog

Every entry here is a migration step for projects already grafted from Stock.
Read from the version a project recorded at graft time forward, and apply each
entry as its own small PR.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
where a **major** bump means a grafted project needs manual intervention to
re-sync, and a **minor** bump means the migration is additive.

## [Unreleased]

Nothing here yet — the next real change starts a fresh section.

## [0.7.0] — 2026-10-07

**Minor** — additive; a project that adopts none of the changes below stays green.

### Added

- **`foundation` gains *A Passing Review Check Means A Review Happened*, and
  tests that run the review workflow's final step.** v0.6.0 added that step so
  a green review check means a review was posted; this writes the promise down
  as a requirement with seven scenarios (a posted review passes; nothing
  posted, a run error and an edit to the review workflow each fail; a denied
  tool call only warns; a decline note passes only for a Markdown-only pull
  request; comments by anyone but the review bot do not count).
  `tests/test_review_gate.py` reads the step out of
  `.github/workflows/claude-review.yml`, runs it with `bash` against a fake
  `gh`, and claims all seven, so removing or weakening a rule turns the suite
  red. Each claim was shown able to fail: the matching rule was removed in a
  scratch copy and the matching test went red (7 of 7, plus 5 more for the
  extra tests). The guard reads `17/21 scenarios claimed by tests, 4 allowed
  without one` (was `10/14`).
  **Not covered:** whether the live review follows its prompt (the decline
  note, reviewing again after a push) is model and plugin behaviour, checked on
  real runs, not by the suite. **Needs `bash` and `jq`** on the machine that
  runs the suite; the tests fail, not skip, without them. The tests read the
  gate out of the workflow, so moving the step or renaming its `id: gate` means
  updating them.
  **Migration:** copy the requirement and scenarios into your
  `openspec/specs/foundation/spec.md` (or re-sync the spec) and copy
  `tests/test_review_gate.py`. **If your project does not run Stock's
  `claude-review.yml`,** the tests fail because there is no gate to extract:
  delete the requirement and the test file in your copy and say why in an ADR,
  as you would for a declared gap. A project that took the review workflow in
  v0.6.0 needs nothing else beyond the change below.

### Changed

- **The review check is advisory, not a required check.** The goal changed
  from "green means reviewed, enforced" to "a missing review must never look
  like a review": a visible red check meets it, and blocking merges was the
  expensive part. Measured from the review workflow's run list (runs 28 to 52,
  25 runs): 15 green, 9 red, 1 cancelled. Four of the reds were pull requests
  that edit the workflow, which are red by design; five were the gate or the
  review itself misfiring. Every red that was correct ended with the
  maintainer bypassing or closing the pull request, never with a review.
  **Migration:** if you made `review` a required check (v0.6.0 told you how),
  remove it from the ruleset's required checks. Keep your CI job required. A
  pull request that edits the review workflow still shows `review` red, and
  now no bypass is needed.
- **The gate no longer fails when a tool the review posts with is denied.**
  v0.6.0's gate matched the text `gh pr comment` anywhere in a denied Bash
  command, so a pull request whose own test file quoted that phrase failed it
  (measured on `Graftwork/stock#56`: a 20-minute review failed on two denied
  `python3` commands). The rule added nothing: if `Skill`, the inline-comment
  tool or `gh pr comment` is denied, nothing is posted and the "posted
  nothing" rule already fails the run and lists the denied calls. A denied
  tool call is now only listed. **Migration:** delete the `intended`
  definitions, the `intended_list` and `intended_count` lines and the
  `if [ "$intended_count" != "0" ]` block from the gate step in your
  `claude-review.yml`, or copy the step from this release.

### Fixed

- **CI pins the `mise` binary.** `.github/workflows/ci.yml` let `jdx/mise-action`
  resolve the newest `mise` release older than seven days, which is a call to
  the GitHub API. It failed twice, both before any step of ours ran: on
  `Graftwork/stock#14` a brand-new release returned a 404 for its download, and
  on `#57` `mise self-update` to 2026.9.17 was rate limited (HTTP 403,
  unauthenticated) because the cache held 2026.9.12. The workflow now sets
  `version: 2026.9.12` (the version the repository's cache already held, installed
  by earlier runs) and drops `minimum_release_age`, which the action applies only
  when `version` is not set (read from its `action.yml`). Not run offline: the
  first CI run on a cold cache is the check. **Migration:** in your own
  `ci.yml`, replace `minimum_release_age: 7d` with `version: 2026.9.12` on the
  `jdx/mise-action` step. To upgrade `mise` later, change that number once the
  release is a few days old.

## [0.6.0] — 2026-10-02

**Minor** — additive; a project that adopts none of the changes below stays green.

### Added

- **`"attribution": {"sessionUrl": false}` in `.claude/settings.json`.**
  Claude Code cloud sessions add a `Claude-Session` trailer to commits by
  default. This documented setting stops that at the source: in a fresh
  session on this configuration the agent's attribution instructions no
  longer mention the link, and `Co-Authored-By` stays. It does **not** stop
  the link in a pull request description: the GitHub tool a session uses to
  open a PR appends `_Generated by [Claude Code](…/session_…)_` itself, after
  the body is written, whatever the body says (measured: two PRs, both got
  it). Until that changes upstream, edit the PR body after opening it to
  remove the footer, or add the `session-links` workflow below, which does it
  for you. The setting is per repository (cloud sessions don't
  read `~/.claude/settings.json`), so each grafted project needs its own.
  The links are opaque IDs, not readable by other accounts (checked signed
  out and from a second account), but they are permanent once committed.
  **Migration:** add the key to your own `.claude/settings.json`.

- **`foundation` gains Coding Session Links Are Not Disclosed**, alongside
  the existing *AI Authorship Is Disclosed*: name the coding agent and model,
  never write a link to the private session or conversation that produced a
  change. **Scope, stated plainly:** it governs what the agent writes and what
  a commit message contains. It does not reach a link that the GitHub tool
  appends to a pull request body after the agent has written it (measured, see
  the `attribution` entry above); the rule tells you to edit that out
  afterwards, or to let the `session-links` workflow below do it. Reported from
  [`Graftwork/talks`](https://github.com/Graftwork/talks): the link kept
  reappearing in PR bodies across several PRs despite being stripped each
  time, which is consistent with a tool-appended footer (not checked in that
  repository from here).
  - The commit-message half is caught mechanically: a new `no-session-link`
    pre-commit hook, at the `commit-msg` stage. Run `pre-commit install` (no
    extra flag — `default_install_hook_types` now covers both stages) to pick
    it up on an existing clone. With `sessionUrl: false` above, the agent no
    longer starts from an instruction to add the link, so the hook is a
    backstop rather than the only defence.
  - What the agent writes for a pull request or issue is a declared
    review-policy gap, the same limitation *AI Authorship Is Disclosed* lives
    with: the suite cannot observe it.
  - **Migration for an already-grafted project:** add the equivalent house
    rule to your own `CLAUDE.md`, even before re-syncing this entry — the
    platform default applies per repository, not per Stock version. To get the
    hook, add the `no-session-link` entry and `default_install_hook_types` from
    `.pre-commit-config.yaml`, plus `scripts/check_no_session_link.py`. If you
    declare the `a-pull-request-or-issue-contains-no-session-link` gap in your
    own `pyproject.toml`, copy its `reason` as it stands in Stock's: it says what
    the `session-links` workflow does and does not cover.

- **`.github/workflows/session-links.yml` keeps coding-session links out of
  pull request descriptions and commits, in CI.** Enforced in CI because the
  GitHub tool appends the link after the body is written, so no setting or
  instruction can stop it, and a local hook can be skipped with `--no-verify`.
  Two jobs, on `pull_request`:
  - **Description:** reads the current body and removes the link. A line that
    is only the link (the tool's `_Generated by …_` footer, or a
    `Claude-Session:` line) is dropped; in any other line only the URL is
    removed, so a sentence that mentions it keeps its words. Same-repository
    pull requests only: a fork's token is read-only.
  - **Commits:** fails a pull request whose own commits carry a link, naming
    them. It matches the same pattern as the `no-session-link` hook
    (`claude.ai/code/session`, case-insensitive) against the base branch as it
    is when the job runs, so a branch that has merged the base in is not
    blamed for commits that were already on it.
  - **Limits, measured or stated as not checked:** the original text stays in
    the pull request's edit history, so this tidies what is displayed and
    does not erase it. Comments and reviews are not covered. Also not
    covered, found after this was written: the pull request **title** is not
    scanned, and a squash merge can carry it into the commit message on
    `main`; a link written **without `https://`** (`claude.ai/code/session_…`)
    survives the description cleaning (measured), though the commits job and
    the hook still catch it in a commit message; on a **fork** pull request
    the description job is skipped, and a skipped job may count as passing for
    a required check (recalled, not checked), while the commits job still
    runs; **pushes to `main`** are not scanned
    ([Stock ADR 0016](docs/decisions/stock-0016-no-ci-check-on-pushes-to-main.md)).
    The pattern is written in three places (the hook, the commits job, the
    description script) and nothing checks that they agree; the missing-scheme
    case is that drift. A later release is planned to close these.
    Commits already on `main` are not touched: 26 of them carry a `Claude-Session:` trailer
    in this repository (`git log --grep`), all from before the setting and
    the hook. The cleaning logic lives in the workflow and is not covered by
    the suite; it was exercised by extracting it and running it against
    23 bodies, including nested lists, hard line breaks and autolinks.
  - **Migration:** copy the file into your own `.github/workflows/`. It needs
    no secrets, only the workflow's own `GITHUB_TOKEN`.

### Changed

- **The `SessionStart` hook now runs `uvx pre-commit install --install-hooks`.**
  A fresh `git clone` has no git hooks (measured), so unless something
  installs them, the pre-commit checks don't run in a cloud session. Commits
  there now run them. **Migration:** add the same line to your own
  session-start hook.

- **`docs/RELEASING.md` steps 7 and 9 now also describe the GitHub Releases
  page**, for a maintainer without `git` installed: where to set the tag and the
  target commit (steps 7 and 9), the previous tag (step 9 only), and how to
  check the result. Releases made there create *lightweight* tags, as every
  Stock tag since `v0.2.0` is (`v0.1.0` to `v0.1.2` are annotated). The doc
  showed only `git tag -a`, which makes annotated ones, so it was not what made
  them.
  **Migration:** if your project keeps its own `docs/RELEASING.md`, copy the
  paragraphs you want; nothing depends on them.

### Fixed

These ship with the additions above, in `0.6.0`. They are not part of `0.5.1`,
which carries only the `Skill` grant and the background-tasks switch (the entry
below). See [Graftwork/stock#39](https://github.com/Graftwork/stock/issues/39)
for the evidence behind each one.

- **The automated review workflow (`.github/workflows/claude-review.yml`)
  reported a green check whether or not a review happened.** Every earlier
  failure (the missing `Skill` grant, the background subagents) ended the
  same way: job `success`, nothing posted. The workflow now ends with a step
  that fails the job when any of these is true:
  - the review bot (`claude[bot]`) posted no comment or review on the pull
    request since the run started;
  - the action reports `is_error: true` (seen in `Graftwork/talks`: job
    green with `is_error: true` and 8 denials);
  - the pull request edits `claude-review.yml` itself. The action skips
    itself for those (it requires the workflow file to match the default
    branch's) and exits `success` in seconds; measured in `Graftwork/talks`.
    The check now fails for them so a skip is never green. **Merging such a
    pull request needs a repository admin to bypass the check**, after a
    human has read the change;
  - a tool the review is meant to use was denied: `Skill`, the inline-comment
    tool, or `gh pr comment`.

  **Other permission denials only warn.** The first version failed on any
  denial. Measured on a pull request with planted bugs: the review named both
  and posted, and four exploratory `Bash` calls (`gh pr diff`, `git ls-tree`,
  a `python3` trace) were denied, which turned a good review red. They differ
  from run to run and one of them executes code, so granting them one at a
  time would not converge and would widen the allowlist for nothing. The
  denied commands are listed in the run summary and in one comment on the
  pull request, which is updated in place on each push. That comment comes
  from a separate job (`denied-calls-comment`) with `pull-requests: write`,
  so the job that runs the model keeps a read-only token; it is skipped for
  fork pull requests and never fails the check.

  **"Nothing to review" is an explicit outcome, not silence.** The review
  declines pull requests it judges to have nothing to review and, left alone,
  posts nothing (measured on an empty commit). The prompt now asks it to post
  a comment beginning `No reviewable changes`, and the gate accepts that. It
  accepts it only when the pull request has no changed files other than
  Markdown, checked from the GitHub API and not from anything the model said;
  otherwise text in a pull request could talk the review out of reviewing
  code. Only `claude[bot]`'s comments count, so the denied-calls comment and
  the `session-links` job (both `github-actions[bot]`) can never make a broken
  run look reviewed. Whether the review follows the new instruction is checked
  on a live run, not assumed; if it does not, the gate still fails loudly.
- **The workflow now also runs on `synchronize` (a push to an open pull
  request), not only `opened` and `ready_for_review`.** Needed so the check
  can be made *required*: a required check is matched to the head commit, so
  without it any pull request with a follow-up push would wait for a check
  that never runs. The review plugin reviews a pull request once (it stops if
  Claude has already commented; measured on `Graftwork/stock#47`, finding 11
  on #39), so a push after the first review posted nothing and the gate went
  red. The `prompt` now tells the review to ignore that condition and review
  the current head. Measured on a throwaway pull request (`Graftwork/stock#51`) with a planted
  bug in each of two commits: the first push was reviewed and named bug one;
  the second push's run posted new reviews naming bug two (and bug one again),
  and `review` was green. One pass, not a guarantee: the wording depends on a
  plugin Stock does not pin, and each push costs a full review (about 6
  minutes here). If the review ignores the instruction the gate still fails,
  loudly, so a green tick still means a review happened.

  **Known limit: a small code pull request can get no review, and the check
  goes red.** On a first attempt (`Graftwork/stock#50`, a 3-line file) the review posted
  nothing, not even the "No reviewable changes" note, and the gate failed it;
  an 18-line one (`#51`) was reviewed. Cause not established. Candidates: the
  plugin skips changes it judges trivial (size), or the description's
  "throwaway, not to be merged" wording (#51 used the same wording and was
  reviewed, so wording alone does not explain it). The "No reviewable changes"
  note only covers Markdown-only pull requests, so expect an occasional admin
  bypass on a tiny code change. The failure is loud, not silent.

  **Migration:** copy the new final step, the `Record when this review
  started` step, the `id: review` on the action step, and the `synchronize`
  trigger into your own `claude-review.yml`. Expect the check to go red where
  it was green: that is the point, and each failure message names the cause.
  Copy the `denied-calls-comment` job too if you want the comment, and the
  second and third paragraphs of the `prompt` (review again after a push;
  the "nothing to review" outcome).
  Making the check required is a repository setting (Settings, Rules), not
  something the workflow file can do; use the job name `review`.

## [0.5.1] — 2026-09-29

**Patch** — fixes existing tooling, adds no new promise or interface.

### Fixed

- **The automated review workflow (`.github/workflows/claude-review.yml`)
  never posted anything, for two separate reasons.** Every run reported
  `success` regardless. Both fixes are needed; the first alone is not enough.
  1. `Skill(code-review:code-review)` was missing from `--allowedTools`.
     The prompt runs `/code-review:code-review`, which goes through the
     `Skill` tool, so the first step was denied
     (`permission_denials_count: 1`). Seen in this repository and in
     [`Graftwork/talks`](https://github.com/Graftwork/talks). Scoped to that
     one skill, not a bare `Skill` grant, since the plugin marketplace is
     un-pinned.
  2. The plugin starts subagents in the background, and the action's single
     non-interactive turn can end while they are still running, still
     reported as `success`. The workflow now sets
     `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` through the action's `settings`
     input (a workflow `env:` does not reach Claude Code). Measured in
     [`sorting-office`](https://github.com/Graftwork/sorting-office), same
     code change on two PRs: switch off, nothing posted; switch on, two
     inline comments posted. One run per arm.

  **Migration:** apply both changes to your own `claude-review.yml`. Until
  you do, its automated review has likely never posted anything. Test with a
  code change described neutrally: the plugin can decline a PR that calls
  itself a throwaway, and a run that ends quickly with nothing posted may
  be that.

## [0.5.0] — 2026-09-28

**Minor** — both entries below are additive; a project already grafted from
`v0.4.0` stays green without adopting either of them.

### Fixed

- **`NOTICE` pointed to `WORKFLOW.md`'s "Growing this file" section and
  `CLAUDE.md`'s Notes section for where the vendored `openspec-*/` skills'
  MIT license is explained — neither actually says it.** Found by
  [sorting-office](https://github.com/Graftwork/sorting-office) writing its
  own `NOTICE` for its independent Apache-2.0 decision while re-syncing to
  `v0.4.0` — it declined to carry the broken reference forward. The
  underlying claim still holds (each `openspec-*` skill's own frontmatter
  declares `license: MIT`); the fix drops the dangling pointer rather than
  inventing content elsewhere to make it resolve, since nothing else in the
  repo documents this fact either.

### Added

- **[`docs/GOING_PUBLIC.md`](docs/GOING_PUBLIC.md)** and
  [Stock ADR 0015](docs/decisions/stock-0015-going-public-checklist.md) — a
  once-only checklist for when a repository's visibility actually changes:
  license and copyright, a full-history secret scan, a cross-repo dead-link
  check, a sweep for stale conditional wording, a final whole-repository
  stranger read, and the GitHub-side settings (branch protection in
  particular) no agent session can currently check on its own.

  Assembled from Stock's own real pre-publication review, not written ahead
  of need — every item traces to something that actually went wrong or was
  actually missing here this week, matching every other promoted-from-a-real-
  case addition to this repo.

- **`.claude/skills/stock-graft-existing-project/` is present in this tag,
  and is not ready to use.** Its own frontmatter says so —
  `status: "draft — in progress... not yet proposed upstream"`, several
  sections marked `(pending)` — and that stays true here; nothing about it
  changed for this release. Disclosed only so its presence doesn't go
  undiscovered: it was added in one PR (#17), whole, with no CHANGELOG
  entry of its own — missed once, at that PR's own review, and only
  surfaced now because a real `v0.5.0-rc.1` graft (`talks`) read through
  everything the tag added rather than trusting this file to say so. Not a
  capability to adopt yet — treat it as absent until a real entry replaces
  this one.

## [0.4.0] — 2026-09-11

**Released as `v0.4.0`.** `v0.4.0-rc.1`'s tag-dependent UAT (case 5) included
a real hand-walkthrough of the graft steps against the published candidate,
not just the mechanical rehearsal — and that walkthrough found the gaps
below. Per
[`RELEASING.md` step 8](docs/RELEASING.md#8-run-the-tag-dependent-uat-cases-against-the-candidate)
the fixes are folded into this same entry rather than filed separately.
`v0.4.0-rc.2` carried the fixes; `v0.4.0` and `rc.2` point at the exact same
commit, per step 9.

**Minor** — every entry below is additive; a project already grafted from
`v0.3.0` stays green without adopting any of it.

### Fixed

- **Step 5's "keep or replace" framing missed that `NOTICE`'s first line is
  an identity line, not just a copyright statement.** Walking the graft steps
  by hand against `v0.4.0-rc.1` (rather than only running the mechanical
  rehearsal) showed that a grafter who genuinely wants to keep Apache-2.0 and
  Stock's copyright holder would still end up with `NOTICE` reading
  `Graftwork Stock` — misnaming their own project — since step 5 treated
  `LICENSE`/`NOTICE` as one binary keep-or-replace decision. Step 5 now says
  explicitly: update `NOTICE`'s first line to the new project's name either
  way, the same identity-rewrite step 4 already gives `README.md` and
  `CHANGELOG.md`.
- **Step 8 didn't say how to keep an `-rc.N` fix clean when unrelated work
  had already landed on `main`.** It classified "independent work" as
  belonging to the next version, but building this very fix's `rc.2` exposed
  that nothing said *how* to keep that true mechanically — branching from
  current `main` as usual would have silently carried the unrelated work
  (PR #17) into the fix, and from there into the tag, unaccounted for in this
  CHANGELOG entry. Step 8 now says explicitly: branch the fix from the
  candidate's own commit, not from `main`; merging into `main` afterward is
  still normal, but the tag is cut from a cherry-pick onto the candidate, not
  from `main`'s tip.

### Added

- **`LICENSE` and `NOTICE`** — Apache License 2.0, copyright held by James
  Rennison individually rather than by "Graftwork" (a repo name, not a legal
  entity). See [Stock ADR 0014](docs/decisions/stock-0014-license-and-copyright.md).
  Found missing during the pre-publication review ahead of making the
  repository public: with no `LICENSE`, default exclusive copyright applied,
  which is incompatible with a repository whose whole purpose is being
  grafted from. The graft steps in `README.md` now call out `LICENSE`/`NOTICE`
  explicitly — a fresh graft carries them across like any other file, so doing
  nothing means Apache-2.0 under Stock's copyright holder by default.
- **[Branch names match the route](WORKFLOW.md#branch-names-match-the-route).**
  A branch prefix for each route and change type — `feature/`, `bugfix/` on
  the OpenSpec route; `chore/`, `docs/`, `ci/`, `refactor/`, `test/` on the
  direct route — so the branch states which route it's on before the PR is
  opened. `release/` and `hotfix/` were considered and left out: Stock ships
  from a tag cut directly off `main`, not a stabilization branch, and has no
  expedited or unreviewed path to `main`, so neither prefix names a step
  Stock actually has. A Claude Code cloud session's auto-derived
  `claude/<slug>-<hash>` branch should be renamed onto the matching prefix
  before opening a PR.

  Brought over from sorting-office, which established the two-prefix
  version of this first.

- **`.claude/setup.sh` and [Stock ADR 0010](docs/decisions/stock-0010-cloud-environment-setup-script.md).**
  Claude Code cloud sessions don't have `mise`, and — measured, not assumed —
  nothing a session can run installs it: `mise.run` returns 403 through the
  Trusted allowlist, `uv tool install mise` fails (not on PyPI), and a direct
  GitHub release-asset fetch is blocked because `jdx/mise` isn't attached to
  the session. This is a mechanical consequence of Stock's own choice to
  standardize on mise ([Stock ADR 0001](docs/decisions/stock-0001-why-mise.md)),
  so every grafted project inherits it, and no amount of committed code
  removes the fix's one manual step — creating a Custom cloud environment and
  pasting the script in is a human, per-account action. `README.md` and
  `CLAUDE.md` both point here so a session hitting `mise: command not found`
  doesn't spend a turn rediscovering it.

  Found and independently verified from a live cloud session while grafting
  and rebuilding [sorting-office](https://github.com/Graftwork/sorting-office)
  — the same project that found the v0.1.1 and `openspec/changes/` fixes.

- **`.claude/skills/stock-resync-in-flight-graft/`** and
  [Stock ADR 0011](docs/decisions/stock-0011-resync-in-flight-graft-skill.md).
  Catches up a grafted project's `main` (kept as a rolling mirror of a Stock
  tag) and its in-progress work branch to a newer Stock tag, without a raw
  `git merge` mangling files the project has already rewritten for its own
  identity — untouched files get a straight patch, verified with tree hashes
  rather than assumed; already-rewritten files are read and decided on by
  hand, one at a time.

  Written and proven on [sorting-office](https://github.com/Graftwork/sorting-office)
  — the same project this CHANGELOG already credits for the v0.1.1,
  `openspec/changes/`, and cloud-environment `mise` fixes — after Stock moved
  from `v0.3.0-rc.1` to `v0.3.0-rc.2` while its first PR was still unmerged.
  Renamed with the `stock-` prefix on the way in, matching the ADR-numbering
  convention rather than introducing a second one; content otherwise
  unchanged.

  This does not attempt the general case — an already-settled, already-released
  project reading Stock's CHANGELOG forward and applying entries by hand,
  per `RELEASING.md` step 10, still has no tooling behind it. That stays a
  backlog item on purpose: one proven narrow case is real evidence for
  *this* situation, not for the general one.

- **`.claude/hooks/session-start.sh` and [Stock ADR 0012](docs/decisions/stock-0012-uv-not-mise-run-on-claude-code-web.md).**
  Getting `mise` itself onto a Claude Code cloud session ([Stock ADR 0010](docs/decisions/stock-0010-cloud-environment-setup-script.md))
  doesn't make `mise install` work there: resolving the pinned python/uv
  versions needs GitHub release metadata, and a cloud session's GitHub
  access is scoped to the repositories attached to it — never `astral-sh/uv`
  or the Python build repo for a grafted project. Measured directly,
  `mise install` and every `mise run <task>` fail on this before the task
  itself ever runs. A `SessionStart` hook now runs `uv python install
  <version from mise.toml>` and `uv sync` instead — `uv` reaches the same
  builds through a direct release-asset URL, which redirects to a CDN host
  outside the restriction, where `mise`'s API lookup for the same version
  does not. `CLAUDE.md` and `README.md` both say to use `uv run`/`npx`
  directly instead of `mise run lint`/`test`/`trace` in this environment,
  for the same reason.

  Found and re-verified from a live cloud session while grafting and
  rebuilding [sorting-office](https://github.com/Graftwork/sorting-office) —
  the same project this CHANGELOG already credits for the v0.1.1,
  `openspec/changes/`, cloud-environment `mise`, and resync-skill fixes.

- **[Stock ADR 0009](docs/decisions/stock-0009-not-a-template-repo.md)** — Stock
  is deliberately *not* a GitHub template repository. Templates copy a branch,
  never a tag, and start the new repository with a single commit carrying no
  tags or releases; Stock's whole re-sync contract is tag-based, so a template
  graft would have no honest `stock-version` to record. Recorded because
  switching the setting on looks like an obvious improvement and is a one-click
  action. The ADR names the condition under which it should be revisited.

- **[Stock ADR 0013](docs/decisions/stock-0013-defer-to-tool-defaults-over-suppressions.md)**
  — grafted projects default to a tool's own defaults over a suppression,
  exception, or workaround, even where an experienced engineer might
  reasonably judge one safe to add. Treat a suppression as needing a written
  justification, the same bar `[tool.graftwork.traceability]`'s declared gaps
  already hold ([Stock ADR 0005](docs/decisions/stock-0005-declared-gaps-in-traceability.md)),
  not a routine option alongside the default. Grounded in who Stock is
  for: a product owner directing an LLM, not an engineer who can judge
  whether a `# noqa` is still warranted two years on, or safely remove one
  that no longer is.

  Found while grafting Stock onto an existing project (`comic-book-guy`) —
  ruff's `F401` strips an "already imported earlier" name from a later
  notebook cell even when that cell uses it directly, since ruff treats a
  whole notebook as one shared import namespace. The instinctive fix was a
  suppression to keep the cell independently runnable; decided against it,
  since the notebook was already written for sequential execution and
  didn't need that property. The specific case is one example of the
  general rule, not the reason for it.

- **`.github/workflows/claude-review.yml`** — an automated Claude Code
  review on every pull request opened against a grafted project, using the
  `code-review` plugin from `anthropics/claude-code`, authenticated via a
  Claude subscription OAuth token (`CLAUDE_CODE_OAUTH_TOKEN` repo secret,
  not committed anywhere — set it per project after grafting).

  Drafted here, then actually shaken out on `comic-book-guy` before coming
  back — two real bugs found and fixed that way: a clean review (no issues
  found) posts its summary through a different mechanism (`gh pr comment`)
  than one that finds issues (an inline-comment MCP tool), so granting only
  one made the other look like it silently did nothing; and `--comment` is
  required on the review prompt at all, or nothing reaches the PR, only the
  workflow's own run log.

  Hardened across two review rounds after the first version merged: fork
  PRs (the shape every contribution into `Graftwork/stock` itself takes)
  withhold secrets from a plain `pull_request` trigger by default, and
  enabling the private-repo setting that restores them turns an unpinned
  checkout of the PR's own content into real exposure — fixed by splitting
  into two checkouts, base branch at the workspace root, the PR's content
  isolated in a subdirectory. Separately, `claude-code-action` carried a
  disclosed, since-patched prompt-injection vulnerability (malicious PR
  content tricking the action into leaking its own credentials through
  tools it's legitimately granted); fixed by pinning the action to a
  specific commit past the fix, rather than a floating major-version tag.

### Fixed

- **CI's `jdx/mise-action@v4` step now sets `minimum_release_age: 7d`.** Not
  a pin — `mise.toml`'s own tool versions are untouched, and this still
  always moves forward to whatever mise release is newest once it clears
  the threshold. It only guards against the mise binary itself (resolved by
  `mise-action`, separate from anything in `mise.toml`) shipping with
  release assets that don't resolve for the first few days after publish.
  Measured directly: CI failed with `curl: (22) ... 404` fetching
  `mise-v2026.9.2-linux-x64.tar.zst` immediately after that release went
  out, while every prior run on the same workflow was green. `7d` matches
  `mise-action`'s own documented example for this input.

## [0.3.0] — 2026-08-16

**Amended, not yet released.** `v0.3.0-rc.1` failed UAT case 5 — the first real
graft attempted under it found the bug below — so per
[`RELEASING.md` step 8](docs/RELEASING.md#8-run-the-tag-dependent-uat-cases-against-the-candidate)
the fix is folded into this same entry rather than filed separately, and the
next tag is `v0.3.0-rc.2`, not a release. Nothing here is final until a
candidate passes.

### Fixed

- **The graft instructions said nothing about `openspec/changes/`.** Stock's
  own backlog stubs and archived changes came across into the grafted project
  by default, because step 1 covers `openspec/specs/` and is silent on
  `openspec/changes/`. Left in place, an agent reading `openspec list` in the
  grafted project sees Stock's TODOs as if they were its own, and
  `CLAUDE.md`'s "don't open a second change over the same ground" rule then
  treats a stale Stock stub as ground already covered — actively steering the
  agent away from real work, not just leaving noise behind. The graft steps
  now have a step 2: remove `openspec/changes/`; `openspec new change`
  recreates it (and `archive/`) the first time it's needed, verified against
  the pinned CLI rather than assumed.

**Context is not content.** Learned the expensive way: the first project grafted
from Stock was torn down and rebuilt because personal detail supplied while
scoping the work had been written into a spec, then into code, then pushed. By
the time it was noticed it was in git history, and history is not edited but
rewritten — so rebuilding was the cheapest honest remedy.

This is structural, not careless. Spec-driven development with an agent is a
transcription pipeline by design — conversation to proposal to spec to code to
commit — and the pipeline has no notion of *why* a detail was supplied. Every
project grafted from Stock inherits the same exposure, which is what makes it a
foundation concern.

The migration is additive: a new promise and one new pre-commit hook. A grafted
project that adopts neither stays green.

### Added

- **`foundation` requirement: Context Is Not Content.** Detail supplied so the
  agent understands a problem is not thereby material for artifacts. Requirements
  are written as categories and rules — a named correspondent, not their name; a
  retention period, not whose records. A specific that genuinely is the
  requirement gets confirmed before it is written down.
- **A `detect-secrets` pre-commit hook** (`Yelp/detect-secrets`, pinned
  `v1.5.0`), covering the half of that promise a machine can keep. Verified both
  ways: clean across the repository, and failing on a planted credential. No
  baseline file — Stock has no false positives to suppress, and a project adds
  one the day it gets its first.
- **Two declared gaps** in `[tool.graftwork.traceability]` for the half a machine
  cannot keep. No test can read a requirement and judge whether "the consultant"
  is a category or a person. The split is stated rather than blurred, because a
  green hook reading as "checked" is exactly the false assurance to avoid here.
- **UAT case 4** — read the artifacts as a stranger would. The only case that
  must run **before the commit** rather than before the PR, for the reason above.
- **House rule in `CLAUDE.md`** and the long-form convention in `WORKFLOW.md`,
  including the pipeline diagram showing where the window closes.
- **Three more of OpenSpec's rough edges**, all hit while making this change:
  nothing may reference a scenario id until the change is archived (there is no
  `sync` command to write main specs early, so the archive has to be ordered
  *ahead* of any claiming test or declared gap); `archive` moves a change one
  directory deeper without rewriting its relative links, silently breaking every
  `../../../` reference in its artifacts; and `validate --change <name>` prints
  `error: unknown option` while exiting 0.

### Changed

- **UAT `Last passed` dates are batched** into the next real change rather than
  each earning its own PR. A one-line date change costing a full pull request is
  friction that gets a rule quietly ignored; an exemption is a hole that widens.
  This release is the first use of it.
- **`docs/UAT.md` cases now carry two dates, not one.** `Last agent run` records
  that the commands were executed and what came back; `Last passed` records that
  a person looked and accepted. Only a person writes the second.

  This corrects a real defect in v0.2.0: every `Last passed` date in that release
  was written by the agent that had just run the commands itself. Everything was
  green and nothing had been reviewed — the exact failure UAT exists to prevent,
  shipped inside the file that forbids it. All `Last passed` dates are reset to
  `never` pending a human read.

- **Release candidates.** `docs/RELEASING.md` gains a step: after merge, cut
  `vX.Y.Z-rc.N` and run the tag-dependent UAT cases against *that*, before the
  stable tag exists. This closes a circle the v0.2.0 process could not: those
  cases need a real, cloneable tag, so they could only run after the release was
  already made — and a stable tag that turns out to be wrong cannot be moved,
  because someone may already have grafted from it. A candidate is real enough to
  clone and carries no promise, so a failure costs an `-rc.2` rather than a bad
  release. Cases previously marked *post-release* are now marked *needs a
  published tag*, since they no longer happen after the release.
- **A backlog stub** at `openspec/changes/fresh-graft-check-belongs-in-ci/`. UAT
  case 1 is fully machine-judgeable — its `Expect` is three exit codes — and by
  `docs/UAT.md`'s own admission rule it should be a CI job. A UAT list padded
  with mechanical checks trains the reader to skim, and the cases either side of
  it are the ones that must not be skimmed.

### Notes

- **This is the first change to take the full OpenSpec route** that
  [Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md)
  established — propose, design, delta specs, tasks, apply, archive. v0.2.0
  introduced the rule and could not follow it. The main spec here was written by
  `openspec archive`, not by hand.
- `gitleaks` was tested and rejected: its pre-commit hook declares
  `language: golang`, and Stock's toolchain pins Python, uv and Node but no Go.
  Adding a language runtime for one hook is disproportionate; the Docker variant
  trades it for a Docker dependency. `detect-secrets` declares `language: python`,
  which pre-commit provisions itself.
- The task list was edited mid-flight. Its first draft put the claiming test and
  the declared gaps before the archive step, which cannot work — see the rough
  edge above. The correction is recorded in the archived change rather than
  quietly applied.

## [0.2.0] — 2026-08-16

The ways of working, promoted from a real project. Everything here changed an
outcome on a real project — a parametric model generator run this way for its
whole life — rather than being added because it sounded sensible.

The migration is additive: nothing existing changes behaviour, and a grafted
project that adopts none of it stays green.

### Added

- **`WORKFLOW.md`** — how changes are actually run. The loop, the recipe table
  (situation → action), and the conventions OpenSpec cannot enforce for you:
  backlog stubs as proposal-only changes, transcribing learnings forward when a
  change is abandoned, small scope justified by abandonment cost rather than
  velocity, `MODIFIED` meaning the *entire* requirement, deprecation as a
  first-class `REMOVED` delta, and proving the untouched path is untouched. Ends
  with OpenSpec's rough edges written down, so nobody assumes they have
  misunderstood the tool.
- **Declared gaps in the traceability guard.** A scenario that genuinely cannot
  be tested is declared in `pyproject.toml` with a mandatory written reason:

  ```toml
  [tool.graftwork.traceability]
  unclaimed = [
      { scenario = "foundation/...", reason = "review policy; the suite cannot observe a pull request" },
  ]
  ```

  The declarations are checked like everything else — an entry with no reason, one
  naming a scenario that no spec declares, and one for a gap a test has since
  closed all fail the guard. The distinction that matters is not "tested or not"
  but "decided or not".
  ([Stock ADR 0005](docs/decisions/stock-0005-declared-gaps-in-traceability.md))
- **`docs/UAT.md`** — numbered cases with `Command` / `Expect` / `Last passed`,
  run before the PR and before the archive. An agent may run the commands and
  report what it saw; it may not mark a case passed. Ships with four real cases
  for Stock itself rather than an empty template, one of them marked
  *post-release* because it verifies the published tag and so genuinely cannot
  run before the release exists.
  ([Stock ADR 0006](docs/decisions/stock-0006-uat-is-a-human-gate.md))
- **House rules in `CLAUDE.md`** — the agent-facing half. Measure rather than
  derive and mark which you did; test an empirical premise before specifying on
  top of it; in-flight artifacts are editable and edits get reported; don't open
  a second change over ground an existing one covers; ask on genuine forks and
  decide on everything else; treat the user's field experience as evidence and
  say when it moves your recommendation; don't close a gate that needs human
  senses.
- **Two new `foundation` requirements** — *Declared Gaps* (four scenarios, all
  claimed by tests) and *AI Authorship Is Disclosed* (one scenario, declared as a
  review policy, which is what gives Stock a worked example of the new mechanism
  in its own repo).
- **`docs/RELEASING.md`** — how a change gets *out*, which Stock had never
  written down. The route table (spec/guard changes run as full OpenSpec changes;
  docs and CI go direct), the version decision, tag-after-merge, and the re-sync
  PRs each release owes every grafted project. A grafted project should keep the
  file and replace the specifics.
  ([Stock ADR 0007](docs/decisions/stock-0007-how-stock-changes-itself.md))
- **Project context and artifact rules in `openspec/config.yaml`**, which was
  previously entirely commented out. The `proposal` rules ask for a
  `## Background` section carrying reasoning forward from a superseded change,
  and for the provenance of load-bearing numbers; the `tasks` rule asks for a UAT
  step ordered before archive. Rules are the supported customisation hook — the
  artifact templates themselves are regenerated and would lose an edit.
- **A worked backlog stub** at
  `openspec/changes/version-string-consistency/` — proposal-only, no deltas,
  demonstrating the convention and tracking a real problem: the version string
  appears in 13 places across 6 files, only 5 of which may be bumped at a
  release. It will report as invalid under `openspec validate` until designed,
  which is the documented cost of the pattern.

### Changed

- `check()` in `scripts/check_spec_traceability.py` takes an `allowed` argument.
  It defaults to reading `pyproject.toml`, so existing callers keep working;
  pass `allowed=[]` to check specs on their own. `Report` gains `unexplained`,
  `orphaned`, and `redundant` alongside `unclaimed` and `unknown`, and the
  summary line accounts for declared gaps: `8/9 scenarios claimed by tests, 1
  allowed without one`.
- **Stock's ADRs are renamed `stock-NNNN-<slug>.md`**, titled `# Stock ADR NNNN:`
  and cited in prose as "Stock ADR 0004". A grafted project now numbers its own
  ADRs from `0001` and never renumbers them — the two sequences share a directory
  and cannot collide.

  This replaces the old advice that a project's ADRs "start at the next free
  number", which could not work: a project stamped when Stock had four ADRs
  started at 0005, and this release adds Stock's own 0005, 0006 and 0007. The
  collision was measured on a real graft — three colliding filenames and 45
  cross-references across 11 files that a renumber would have to rewrite by hand,
  recurring at every future release that adds an ADR. Since nothing outside Stock
  cites Stock's ADR filenames, moving Stock's files instead costs almost nothing.
  ([Stock ADR 0008](docs/decisions/stock-0008-adr-numbering.md))

  **Re-syncers:** if you grafted before v0.2.0 and numbered your own ADRs from
  0005, you do *not* need to renumber. Take the renamed `stock-*` files, keep
  yours exactly as they are, and update any of your own prose that cited Stock's
  ADRs by their old bare numbers.
- Graft steps in `README.md` now say to keep `WORKFLOW.md` and to replace Stock's
  UAT cases rather than the file.
- The ADR template carries a comment explaining the two numbering sequences, so
  the convention is visible at the moment someone copies it.
- **Stock no longer commits to `main` directly.** Up to v0.1.2 every release was
  a direct commit — `main` is a linear run with no merge commits and the repo had
  never had a pull request. From v0.2.0 changes reach `main` by branch and PR,
  which is also what makes the new *AI Authorship Is Disclosed* requirement
  something Stock itself can keep. This is a process change, not a code change;
  grafted projects are free to ignore it.

### Notes

- The vendored `.claude/skills/openspec-*` files are deliberately untouched. The
  "don't open a duplicate change" guardrail belongs in one of them by rights, but
  those files are generated by `@fission-ai/openspec` and would lose the edit on
  the next regeneration. `CLAUDE.md` is loaded every session and carries it
  instead.
- **v0.2.0 sits on the wrong side of its own rule.** It edits
  `openspec/specs/foundation/spec.md` directly, which Stock ADR 0007 forbids from
  v0.2.0 onward — it is the change that introduced the rule and could not have
  followed it. Retrofitting an archived change would fabricate a record of
  deliberation that never happened. The gap is deliberate and stays on the
  record; everything after this follows the route table.
- The auto-marked fast/slow test split is documented in `WORKFLOW.md` as a
  pattern, not shipped as code. Stock has no slow tests, and a `slow` marker with
  nothing to mark is exactly the "added for later" the conventions forbid. It
  should be promoted the first time a grafted project earns it.

## [0.1.2] — 2026-08-13

Permission allowlist tightened. Grafted projects should apply this to their own
`.claude/settings.json`.

### Fixed

- **The allowlist granted arbitrary code execution.** `Bash(uv run:*)` permitted
  `uv run python -c '<anything>'`, and `Bash(mise run:*)` permitted any task
  `mise.toml` happens to define. Both are removed and replaced by the specific
  commands actually used — `uv run pytest`, `uv run ruff check .`,
  `mise run check`, and so on. Because this file is copied into every grafted
  project, the over-broad version propagated outward, which is what makes it
  worth a release of its own.

### Added

- Narrow read-only allowlist entries derived from real usage across sessions:
  the `mise run` tasks, `uv run pytest`, ruff's check-only forms, the
  traceability guard, `uvx pre-commit run --all-files`, `uv sync --locked`, and
  the read-only OpenSpec subcommands.

### Notes

- `Bash(uvx pre-commit:*)` and `Bash(npx --yes @fission-ai/openspec@1.6.0:*)`
  are deliberately kept. Both are scoped to a single named tool rather than to
  an interpreter, and narrowing OpenSpec further would mean a prompt on every
  `new change` and `archive` — a real cost for no real gain.
- Entries such as `Bash(git status:*)` are redundant, since Claude Code already
  treats read-only git and gh subcommands as safe. They are harmless and left
  alone.

## [0.1.1] — 2026-08-12

Fixes found by the first real graft.
No code changed, so re-syncing is documentation-only.

### Fixed

- **The graft instructions produced a red stamp.** They said to drop
  `openspec/specs/`, but the suite asserts at least one scenario exists, so a
  project following them would fail on its first run — the exact opposite of the
  promise. The `foundation` spec now explicitly travels with the graft, which is
  what its own Purpose section always said.
- `mise trust` was missing from the getting-started steps. mise refuses to run an
  untrusted config, so a fresh clone stopped at the first command.
- CI pinned stale action majors (`checkout@v5`, `mise-action@v2`,
  `codecov-action@v5`); now `v7`, `v4`, and `v7`.

### Added

- **`[tool.graftwork]` in `pyproject.toml`** — records `stock-version` and the
  graft date. Previously "record the version you grafted from" named no location,
  so a re-sync had nowhere to look. This is now the starting point for reading
  the CHANGELOG forward.
- Concrete clone-and-detach commands for grafting, rather than "copy the
  foundation across".

## [0.1.0] — 2026-07-25

The initial foundation.

### Added

- **Pinned toolchain** via `mise.toml` — Python 3.13, uv 0.11.16, Node 26.
  Drives the local shell, CI, and the devcontainer from one source of truth.
  ([Stock ADR 0001](docs/decisions/stock-0001-why-mise.md))
- **Python project config** in `pyproject.toml` — uv dependency groups, ruff
  (lint + format), pytest with coverage and `--strict-markers`.
- **OpenSpec** initialised via the pinned `@fission-ai/openspec@1.6.0`, with
  Claude Code skills and `/opsx:*` commands.
  ([Stock ADR 0002](docs/decisions/stock-0002-why-openspec-via-npx.md))
- **Spec traceability guard** (`scripts/check_spec_traceability.py`) — checks
  that every scenario is claimed by a test and that every claim names a real
  scenario. Runs standalone, as a pre-commit hook, and inside the test suite.
  ([Stock ADR 0004](docs/decisions/stock-0004-spec-traceability-guard.md))
- **`foundation` spec** — Stock's own promises, written as scenarios and claimed
  by tests, so the foundation is verified by the same mechanism it provides.
- **CI** (`.github/workflows/ci.yml`) — lint, test, and a non-blocking Codecov
  upload so a fresh stamp is green before any secret exists.
  ([Stock ADR 0003](docs/decisions/stock-0003-coverage-reporting.md))
- **pre-commit config** — whitespace/YAML/TOML hygiene, ruff, and the
  traceability guard.
- **Devcontainer** layered on mise, for when a project graduates from experiment.
- **`CLAUDE.md`** — commands, conventions, architecture.
- **`.claude/settings.json`** — shared permission allowlist.
- **ADRs** in `docs/decisions/`, with a template.

[0.6.0]: https://github.com/Graftwork/stock/releases/tag/v0.6.0
[0.5.1]: https://github.com/Graftwork/stock/releases/tag/v0.5.1
[0.5.0]: https://github.com/Graftwork/stock/releases/tag/v0.5.0
[0.4.0]: https://github.com/Graftwork/stock/releases/tag/v0.4.0
[0.3.0]: https://github.com/Graftwork/stock/releases/tag/v0.3.0
[0.2.0]: https://github.com/Graftwork/stock/releases/tag/v0.2.0
[0.1.2]: https://github.com/Graftwork/stock/releases/tag/v0.1.2
[0.1.1]: https://github.com/Graftwork/stock/releases/tag/v0.1.1
[0.1.0]: https://github.com/Graftwork/stock/releases/tag/v0.1.0
