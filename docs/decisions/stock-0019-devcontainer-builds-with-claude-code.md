# Stock ADR 0019: the devcontainer builds, and carries Claude Code

- **Status:** accepted
- **Date:** 2026-10-14

## Context

Codespaces is the lead candidate for where a non-technical owner runs Claude
Code against a grafted project. That rests on Stock's `.devcontainer/`, which
had never been built: the research sessions that proposed it could not reach
the container registries. It was built on 2026-10-14 with the Dev Containers
CLI 0.89.0 against Docker 29.1.3, and it did not work.

**The mise feature reference does not resolve.** `devcontainer up` failed in
2.5 s, before pulling an image:

```
[httpOci] 403: Failed to fetch bearer token for 'ghcr.io': {"errors":[{"code":"DENIED","message":"requested access to the resource is denied"}]}
Error: ERR: Feature 'ghcr.io/jdx/mise/devcontainer-feature/mise:1' could not be processed.
```

Asking GHCR for an anonymous pull token for `jdx/mise/devcontainer-feature/mise`
returns the same 403. The reference `mise generate devcontainer` now emits,
`ghcr.io/devcontainers-extra/features/mise`, returns a token and the tags
`1, 1.0, 1.0.0, latest`.

**The replacement feature installs mise but does not activate it.** Its only
option is `version`; it downloads the binary to `/usr/local/bin` and nothing
else. With it swapped in, the image built and `mise install` installed all
three tools in 21.0 s, then the unchanged `postCreateCommand` failed with
`/bin/sh: 1: uv: not found` (exit 127). In the built container, `node`,
`uv` and `python` were not on `PATH` in any shell. `mise run check` and
`mise run trace` passed anyway, because `mise run` sets up its own
environment; a bare `node --version` did not.

**Anthropic's Claude Code feature installs an old Claude Code that cannot
update.** `ghcr.io/anthropics/devcontainer-features/claude-code:1.0`
(feature version 1.0.5) installs Node 18 from nodesource when `node` is
missing, which it is at feature time, since mise's Node arrives later, in
`postCreateCommand`. npm on Node 18 then installed Claude Code 2.1.197, not
`latest` (2.1.299 on the day). `npm view` shows why: 2.1.197 declares
`engines.node >=18.0.0`, while 2.1.198, 2.1.287 and 2.1.299 declare
`>=22.0.0`, and npm installed the newest version whose engines Node 18
satisfied. 2.1.197 was released on 2026-06-30. `claude update` in the container failed
with `Error: Insufficient permissions to install update`, because npm's global
folder is root-owned. The container ends up with two Nodes: `/usr/bin/node`
18.20.8 first on `PATH`, and mise's 26.11.1 only inside `mise exec` and
`mise run`.

`claude` itself is a native binary in every route measured, an ELF file that
npm only delivers. It ran with an empty environment and `PATH=/nonexistent`.
Which Node is on `PATH` decides what version npm installs, not what Claude
Code runs under.

## Decision

`.devcontainer/devcontainer.json`:

- references `ghcr.io/devcontainers-extra/features/mise:1`;
- puts `~/.local/bin` and mise's shims directory on `PATH` through
  `remoteEnv`, so `python`, `uv` and `node` resolve to the `mise.toml` pins in
  every shell and in `postCreateCommand`;
- installs Claude Code in `postCreateCommand` with the native installer
  (`curl -fsSL https://claude.ai/install.sh | bash`), after `mise install`
  and `uv sync`;
- recommends the `anthropic.claude-code` VS Code extension.

## Consequences

- With this config, a first `devcontainer up` on a fresh container ran in
  55.6 s with the image already cached, `postCreateCommand` taking 49.8 s.
  Inside, `mise run check` passed (50 tests), `mise run trace` passed,
  `node --version` gave v26.11.1 and `claude --version` 2.1.299, in
  non-login, login and interactive bash alike.
- A second `up` against the existing container took 0.4 s and did not rerun
  `postCreateCommand`. Rebuilding the container with the image cached took
  55.7 s.
- Building the feature image with no cache, base image pull included, took
  48.3 s on an empty BuildKit builder. A fully cold `up` is therefore about
  55.6 − 1.0 + 48.3 ≈ 103 s (derived: the cached run, less its 1.0 s image
  build, plus the cold image build). It was not measured end to end, because
  the empty builder could not complete the CLI's UID-update step.
- The native installer took 28.4 s of `postCreateCommand`; npm into mise's
  Node took 9.0 s. That is the price of the decision below, paid once per
  container.
- The `PATH` entries name `/home/vscode`, the `remoteUser` of
  `mcr.microsoft.com/devcontainers/base`. A project that changes the base
  image or the user changes them too.
- Claude Code tracks the installer's default channel, `latest`, and updates
  itself in `~/.local`, where the container user can write.
- The owner still has to sign Claude Code in. That step was not measured.
- **Not measured:** Codespaces itself (only Docker Desktop on a Linux host
  was available); the VS Code extension, which the Dev Containers CLI does not
  install; an Apple Silicon host.

Numbers in this ADR were measured on 2026-10-14 with the commands named, except
the one marked derived.

## Alternatives considered

- **Anthropic's Claude Code feature.** Measured above: Claude Code 2.1.197
  where 2.1.299 was current, a second Node first on `PATH`, and updates
  refused without sudo. Adding `ghcr.io/devcontainers/features/node` ahead
  of it would give npm a Node it accepts, but that is a second Node pin
  outside `mise.toml`, which Stock ADR 0001 exists to prevent.
- **`npm install -g @anthropic-ai/claude-code` with mise's Node.** It
  installed 2.1.299 in 9.0 s, and mise created a `claude` shim. Rejected
  because the package lives inside mise's install of the pinned Node, so
  Claude Code would be tied to the project's Node pin. Reasoned, not measured:
  a change to `node` in `mise.toml` would leave `claude` behind in the old
  Node's directory.
- **`eval "$(mise activate bash)"` in `~/.bashrc`.** It only reaches
  interactive shells, and `postCreateCommand` is not one. `remoteEnv` covered
  every shell measured.
- **`mise exec -- uv sync` in `postCreateCommand` alone.** Fixes the build
  but leaves `node` and `uv` missing from the owner's terminal.
