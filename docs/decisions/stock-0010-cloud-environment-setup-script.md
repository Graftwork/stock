# Stock ADR 0010: A committed setup script for Claude Code cloud sessions

- **Status:** accepted
- **Date:** 2026-08-17
- **Corrected:** 2026-08-18 — the original script pinned `MISE_VERSION`.
  Pasted into a real Custom environment by [sorting-office](
  https://github.com/Graftwork/sorting-office), it failed. The pin, the
  domain guidance, and the reasoning below are all updated to match what
  was actually found — see the end of the Decision section. Nothing here
  had shipped in a release yet when this was corrected, so it's fixed in
  place rather than superseded by a new ADR.

## Context

[Stock ADR 0001](stock-0001-why-mise.md) standardizes the toolchain on `mise`.
Claude Code cloud sessions don't have it, and — measured from inside a live
session, not recalled — nothing a session can run gets it there:

- `mise` is absent from the documented pre-installed toolchain
  (Python/Node/Ruby/PHP/Java/Rust; no version manager), confirmed against
  <https://code.claude.com/docs/en/cloud-environments#installed-tools>.
- `curl https://mise.run | sh` fails — `mise.run` is not on a Trusted
  environment's default allowlist. Reproduced independently in two different
  sessions: `curl: (56) CONNECT tunnel failed, response 403`.
- `uv tool install mise` fails — mise isn't published on PyPI. Reproduced
  independently in both sessions with the identical error.
- A direct GitHub release-asset download fails too, for a different reason:
  the cloud session's GitHub proxy restricts release-asset requests to
  repositories attached to the session, and `jdx/mise` isn't one.

This isn't project-specific. It follows mechanically from Stock's own choice
to standardize on mise, so every project grafted from Stock inherits it the
first time someone drives it from Claude Code on the web rather than a
laptop — which is exactly how it was found, driving [sorting-office](
https://github.com/Graftwork/sorting-office).

**The docs name the setup script as the intended mechanism for exactly this
case**, confirmed verbatim: *"Use a setup script to provision the VM itself:
toolchains and CLI tools that aren't pre-installed. Use a SessionStart hook
for project setup that should run everywhere, cloud and local, like `npm
install`."* A SessionStart hook is committed to the repo
(`.claude/settings.json`) and reruns every session assuming the toolchain
already exists. A setup script runs once per environment, as root, before
Claude Code launches — but it lives in the cloud environment's own
configuration in the claude.ai/code UI, which is **not a git object**.
Nothing committed to any repo can complete this unassisted; a human has to
create or edit an environment once and paste a script in.

## Decision

Ship [`.claude/setup.sh`](../../.claude/setup.sh) as the script to paste into
a Custom environment's Setup Script field, and this ADR as where the reasoning
and the manual step live. `README.md`/`CLAUDE.md` point here rather than
restating it.

The script installs mise to `/usr/local/bin`, using variables mise's own
installer documents (`MISE_INSTALL_PATH`, and originally `MISE_VERSION` too
— see the correction below). Both remaining choices were checked, not copied
from the first thing that looked plausible:

- **`/usr/local/bin`, not the installer's default `~/.local/bin`.** Verified
  directly: a value written to `~/.bashrc` in one Bash tool call is invisible
  to the next — "shell state does not persist between commands" isn't
  incidental, it's exactly the property that breaks a PATH edit made that
  way. `/usr/local/bin` is already on `PATH` for every call, confirmed by
  writing an executable there and finding it from a separate call with no
  PATH or rc edit at all.
- **The env vars sit before `sh`, not before `curl`.** In a pipeline,
  `VAR=val cmd1 | cmd2` sets `VAR` only for `cmd1`. The install script runs
  as the `sh` process and reads its own environment, so the variables have to
  be placed there — a fix that would otherwise look correct while silently
  not applying.

**What this does not do.** The script installs `mise` itself only — it does
not also run `mise trust && mise install`. Whether a setup script runs before
or after the repository is cloned isn't confirmed anywhere in the docs this
was checked against, and `mise install` needs `mise.toml` on disk to mean
anything. Rather than assume an ordering, the script does the one thing that
is independent of it, and everything downstream happens the normal way, once
`mise` exists on `PATH`.

**Correction: no `MISE_VERSION` pin, and no GitHub in the domain list.**
The original script pinned to a specific mise release, reasoning that the
binary enforcing `mise.toml`'s pins shouldn't itself be the unpinned thing
in the chain. That reasoning was wrong in a way this session had no way to
catch — `curl https://mise.run` returned 403 in every session available to
check from, so the pinned script was never actually run past that point.
`sorting-office` pasted it into a real Custom environment with `mise.run`
allowlisted, and it failed.

The mechanism, read directly from mise's own installer source
(`jdx/mise`, `packaging/standalone/install.envsubst`) rather than guessed at:

```sh
if [ "$version" != "$current_version" ] ...
  tarball_url="https://github.com/jdx/mise/releases/download/..."
else
  tarball_url="https://mise.jdx.dev/..."
```

`$current_version` is whatever release was current when mise.run's
currently-served script copy was generated, and it moves forward over time.
A pin written today matches that copy today and stops matching the moment
mise ships a new release — silently flipping the branch above to the
**GitHub** path, which is exactly the release-asset download this ADR
already ruled out: scoped to repositories attached to the session, and
`jdx/mise` isn't one. The pinned script wasn't just untested past the first
403 — it carried a second, independent failure mode behind that one, which
only a real environment with `mise.run` actually reachable could surface.

Leaving `MISE_VERSION` unset makes "requested equals current" true by
construction, on every run, so the install always takes the `mise.jdx.dev`
path and never touches GitHub. The domain requirement changes accordingly:
**`mise.run` and `mise.jdx.dev`, not GitHub.**

mise's own docs, quoted verbatim (`jdx/mise`, `docs/installing-mise.md`),
argue against pinning the tool itself on separate grounds: *"Locking users
to one mise version is like preventing `apt update` or `brew update` from
refreshing package metadata: it can hide deprecation messages and cause bit
rot with upstream integrations like aqua-registry... Projects and
organizations should generally set a `min_version` when they need a newer
mise feature instead of locking every user to a specific mise executable."*
`mise.toml` doesn't currently set one; nothing in this repo needs a mise
feature recent enough to warrant it yet.

**What is and isn't verified now.** The installer mechanism above was read
directly from mise's own source and docs, not inferred — that part is
measured. Whether the corrected script completes cleanly end to end is
`sorting-office`'s report, not something reproduced from a session here:
`mise.run` still returns 403 in every session available to check this from,
pinned or not, so no session that has touched this ADR has run the install
past that point itself.

## Consequences

- A grafted project stops rediscovering this from scratch. The fix and the
  reasoning travel with the graft, the same way `mise.toml` itself does.
- The manual step doesn't go away, and no amount of repo automation removes
  it — worth saying plainly rather than implying the script alone fixes
  this. Someone still has to create a Custom environment, set its network
  access, and paste the script in, once per account.
- Unlike `mise.toml`'s pins on Python, uv, and Node, the mise binary itself
  now floats deliberately — the opposite trade-off, and correct for this one
  case, since pinning it is what broke the install. If this repo ever needs
  a mise feature recent enough to matter, that's a `min_version` in
  `mise.toml`, not a version in this script.
- **A theory that looks sound and matches the evidence available at the time
  can still be wrong**, if the evidence available was itself incomplete —
  every session that touched this ADR before `sorting-office` ran it for
  real was blocked at the same 403 and never saw the failure mode past it.
  Worth remembering the next time something here reads as fully verified.

## Related, not addressed here

Investigating this also surfaced that pulling Docker images inside a cloud
session fails against `production.cloudfront.docker.com`, while the docs'
Trusted allowlist names `production.cloudflare.docker.com` — a different
host. That's a discrepancy in Anthropic's own docs or allowlist, not a
consequence of any decision Stock has made, so it doesn't belong in this ADR
or get a workaround here. Worth reporting to Anthropic directly if it's still
reproducing.

## Alternatives considered

- **A `SessionStart` hook instead.** Ruled out by the docs' own stated
  distinction: hooks assume the toolchain exists, they don't install one, and
  they rerun every session rather than provisioning once.
- **Document the manual `curl`/`uv`/GitHub attempts as "just do this
  yourself."** Rejected — all three are dead ends, verified independently
  twice, not workarounds someone is failing to find.
- **Fold the Docker/CloudFront finding into this ADR.** Rejected — different
  root cause, different owner. Bundling it in would make this ADR harder to
  act on for the one thing it actually fixes.
