# Stock ADR 0012: `uv` installs Python directly; `mise run` doesn't work on Claude Code web

- **Status:** accepted
- **Date:** 2026-08-24

## Context

[Stock ADR 0010](stock-0010-cloud-environment-setup-script.md) gets the `mise`
binary itself onto a Claude Code cloud session, via a one-time Setup Script
paste. That doesn't make `mise install` work: `mise.toml` also pins
`python = "3.13"` and `uv = "0.11.16"`, and resolving either needs GitHub
release metadata — `api.github.com/repos/astral-sh/uv/releases` for uv, and a
`python-build-standalone` GitHub release for Python. A Claude Code cloud
session's GitHub access is scoped to the repositories attached to that
session, so both lookups are denied for a project pinning tools that live in
someone else's repository — which is every project grafted from Stock, since
neither `astral-sh/uv` nor the Python build repo is ever the project's own.

This surfaced grafting and rebuilding [sorting-office](
https://github.com/Graftwork/sorting-office) — the same repository, worked
from a different session, that surfaced [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)'s
original mistake. That session measured it directly:

```
$ mise install
mise WARN  Remote versions cannot be fetched for astral-sh/uv: HTTP status client error (403 Forbidden) for url (https://api.github.com/repos/astral-sh/uv/releases?per_page=100)
github response: {"message":"GitHub access to this repository is not enabled for this session. ..."}
...
mise ERROR Failed to install tools: aqua:astral-sh/uv@0.11.16, core:python@3.13
core:python@3.13: error sending request: client error (Connect): tunnel error: unsuccessful
```

This isn't only `mise install`'s problem. Every `mise run <task>`
auto-installs all of a project's declared tools before running the task it
was actually asked for, regardless of whether that task needs them — the
`sorting-office` session confirmed this by running a task that only shells
out to `npx` and watching it fail on the same python/uv error before `npx`
ever ran. So `mise run check`/`test`/`lint`/`trace`/`openspec` are all broken
in this environment, not only the tools each happens to touch.

**This session re-verified the finding directly, and went one step further
than the `sorting-office` session had — establishing the actual mechanism,
not just the symptom.** `CLAUDE_CODE_REMOTE` reads `true` here too, so the
same commands were run again from scratch rather than trusted secondhand:

- `curl https://api.github.com/repos/astral-sh/uv/releases?per_page=5` → the
  same 403, identical error text.
- `uv python install 3.13.7` (forcing a real download rather than a cache
  hit) → succeeded, 30.8MiB in 5.28s.
- `RUST_LOG=uv=debug uv python install 3.12.11` traced the exact URL `uv`
  fetched from: `https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.12.11%2B20250902-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`
  — a GitHub URL, the same host the blocked API calls hit.
- `curl -sSI` on that exact URL showed why it isn't blocked: a **302 redirect
  to `release-assets.githubusercontent.com`**, a separate, reachable host.
  `github.com/<owner>/<repo>/releases/download/<tag>/<file>` — a direct
  asset link — resolves through that redirect; `api.github.com` and the
  general release-listing pages do not.

That's the actual boundary: not "uv uses a different provider" (checked and
ruled out — uv's Python builds are GitHub releases too, same as mise's), but
*which shape of GitHub request* the session's proxy allows. A direct,
already-known download URL redirects to a CDN host outside the restriction.
A request that has to ask GitHub's API what's available first — which is
what `mise install` always does, and what `uv self update` and `uv add`
would also do — does not. `uv python install <version>` never asks; it
already knows the URL for a given version and platform, so it never touches
the blocked path.

**What this does not explain.** `mise`'s own `core:python` backend fails
with a connection/tunnel error rather than a clean 403, a different failure
mode from the API's 403 — and mise itself isn't installed in this session
(`mise: command not found`, consistent with every session that hasn't run
[Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)'s Setup
Script step), so the exact host mise's python backend tries to reach, and
why it fails at the connection level rather than getting the same 403 as the
REST API, remains unmeasured from here. Worth tracing directly the next time
a session has `mise` on `PATH` and hits it again.

## Decision

Ship [`.claude/hooks/session-start.sh`](../../.claude/hooks/session-start.sh)
as a `SessionStart` hook — not a Setup Script; it needs the repository
already checked out, which happens after any Setup Script runs. Gated on
`CLAUDE_CODE_REMOTE=true` so it's a no-op locally and in CI, it does:

```bash
python_version="$(grep -m1 '^python = ' mise.toml | sed -E 's/^python = "(.*)"$/\1/')"
uv python install "$python_version"
uv sync
```

reading the pinned Python version out of `mise.toml` rather than hardcoding
it, since a grafted project can move that pin and this hook ships to every
one of them unchanged. `uv sync` then installs the pinned dev dependencies
exactly as `uv.lock` specifies. Registered in `.claude/settings.json`'s
`hooks.SessionStart`, so it runs automatically once committed — no manual
per-account step, unlike [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)'s
Setup Script.

`CLAUDE.md` and `README.md` both point here, and tell a session in this
environment to reach for `uv run ruff check .`, `uv run pytest`,
`uv run python scripts/check_spec_traceability.py` directly instead of
`mise run lint`/`test`/`trace` — those tasks are exactly the ones broken by
this, for the reason measured above.

## Consequences

- **The pinned `uv` version (0.11.16) isn't what actually runs** in a Claude
  Code cloud session — it runs whatever `uv` the image ships. `uv self
  update` hits the same blocked API path as `mise install` does, so nothing
  inside a session can move it. Confirmed compatible for `uv sync`/`uv run`
  here; worth re-checking if a future `uv sync` ever behaves differently
  only in this environment.
- **`mise run <task>` is not "how you verify it" in this environment.**
  Anyone driving a Stock-grafted project from Claude Code on the web needs
  `uv run …` / `npx …` directly — which is why this is an ADR and a
  committed hook, not a comment someone has to already know to look for.
- Scoped to Claude Code cloud sessions only, via the `CLAUDE_CODE_REMOTE`
  gate. Nothing here changes `mise.toml`, so the pins stay exact everywhere
  else, and a local or CI run never executes this hook's body.
- A grafted project stops rediscovering this from scratch, the same way
  [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)'s fix
  travels with the graft — except this one needs no manual step at all,
  since a `SessionStart` hook (unlike a Setup Script) is a git object.

## Alternatives considered

- **Ask for the session's GitHub access to include `astral-sh/uv` and the
  Python build repo.** That scoping is a per-session security boundary, not
  an environment domain allowlist like the one [Stock ADR 0010](stock-0010-cloud-environment-setup-script.md)
  used for `mise.run`/`mise.jdx.dev` — there's no setup-script equivalent for
  widening it, and doing so would mean trusting arbitrary third-party
  repositories' release assets inside every session for every grafted
  project, a much bigger door to open than the problem needs.
- **Loosen `mise.toml`'s pins** (e.g. `python = "system"`) so mise doesn't
  need to fetch a specific build at all. Rejected without trying it: the
  pins are shared by every environment a grafted project runs in, and
  loosening them to fix one sandbox's network policy would weaken
  reproducibility everywhere else for a problem that's local to this one
  environment.
- **Wait for mise to skip the auto-install-on-run behaviour.** `mise`
  documents `task.run_auto_install`/`MISE_TASK_RUN_AUTO_INSTALL` for
  disabling it, which would make `mise run <task>` usable again without
  fixing `mise install` itself. Not adopted here: it would still leave
  `mise install` broken, still needs the network exception this ADR avoids
  opening, and the hook already gets a fully working venv without it. Worth
  revisiting only if a future task needs `mise run`'s own dependency graph
  rather than a direct `uv run`/`npx` call.
