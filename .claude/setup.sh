#!/bin/bash
# Installs mise for Claude Code cloud sessions, where it is not pre-installed
# and cannot be fetched by any command run from inside a session — see
# docs/decisions/stock-0010-cloud-environment-setup-script.md for what was
# tried and ruled out, and why this has to be a setup script.
#
# This file is not executed automatically. Copy its contents into a Custom
# cloud environment's Setup Script field (claude.ai/code environment
# settings) — a one-time, per-account step only a human can do; nothing
# committed to a repo can complete it unassisted.
#
# That environment's network access must also reach mise.run and
# mise.jdx.dev — not GitHub, deliberately; see below. Under Custom, ticking
# "Also include default list of common package managers" and adding both
# domains is the simplest way to get there; Trusted alone covers neither.
set -euo pipefail

# MISE_INSTALL_PATH: /usr/local/bin is on PATH for every process by default,
# unlike the installer's usual ~/.local/bin — confirmed by direct test, not
# assumed. A cloud session's shell state does not persist between separate
# tool calls, so anything relying on a PATH edit made in ~/.bashrc or
# ~/.profile is invisible to Claude's next command; installing straight to
# an already-searched directory sidesteps that instead of working around it.
#
# Deliberately no MISE_VERSION pin. mise's own installer, read directly
# (jdx/mise, packaging/standalone/install.envsubst), only downloads from
# GitHub when the requested version doesn't match the version baked into
# whatever copy of the script mise.run is currently serving:
#
#   if [ "$version" != "$current_version" ] ...
#     tarball_url="https://github.com/jdx/mise/releases/download/..."
#   else
#     tarball_url="https://mise.jdx.dev/..."
#
# A pin here goes stale the next time mise ships a release, which silently
# flips that branch to the GitHub path — the exact release-asset download
# already ruled out in the ADR, since it's scoped to repositories attached
# to the session and jdx/mise isn't one. Leaving MISE_VERSION unset makes
# "requested equals current" true by construction, every run, so it always
# takes the mise.jdx.dev path and never touches GitHub at all.
#
# mise's own docs argue against pinning the tool itself, independent of the
# above: "Locking users to one mise version is like preventing `apt update`
# or `brew update` from refreshing package metadata: it can hide deprecation
# messages and cause bit rot with upstream integrations like aqua-registry."
# A project that needs a floor sets `min_version` in mise.toml instead — a
# promise mise checks against itself at run time, not an executable frozen
# in an install script.
curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
