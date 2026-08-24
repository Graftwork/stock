#!/bin/bash
# Gets a working Python + dev-dependency venv on a Claude Code cloud session,
# where `mise install` (and every `mise run <task>`) can't fetch the pinned
# python/uv — see docs/decisions/stock-0012-uv-not-mise-run-on-claude-code-web.md
# for what was measured and why this bypasses mise instead of fixing it.
set -euo pipefail

# Only run this setup in Claude Code on the web / remote sessions. Local and
# CI both reach GitHub without restriction and keep using `mise run` as
# documented — this hook still runs there too, but exits immediately.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# mise won't run an untrusted config (see CLAUDE.md). Harmless if mise isn't
# on PATH at all yet — the `|| true` covers that, not just a real trust
# failure.
mise trust "$CLAUDE_PROJECT_DIR" >/dev/null 2>&1 || true

# Read the pinned Python version from mise.toml rather than hardcoding it,
# since a grafted project can move the pin. `uv python install` reaches the
# same build through a release-asset redirect this session's network policy
# allows, where `mise install`'s GitHub API lookup for the same version does
# not — the two are not equivalent for every possible project layout, but
# they are for the one Stock ships.
python_version="$(grep -m1 '^python = ' mise.toml | sed -E 's/^python = "(.*)"$/\1/')"
uv python install "$python_version"

# Python dev dependencies (pytest, ruff, coverage) — pinned in uv.lock.
uv sync
