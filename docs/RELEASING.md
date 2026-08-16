# Releasing

[`WORKFLOW.md`](../WORKFLOW.md) is how a change is *run*. This is how a change
gets *out* — the sequence from branch to tag to the projects that need it.

Stock's own process is below. A grafted project needs its own; keep this file,
replace the specifics. Most projects can drop the re-sync step and keep the rest.

## Which route a change takes

Not every change earns the full ceremony. The test is what it touches.

| The change touches | Route |
| --- | --- |
| `openspec/specs/`, `scripts/`, or `tests/` | **Full OpenSpec change** — propose, apply, UAT, archive. Main specs are written by archiving, never by hand. |
| Docs, CI, `mise.toml`, `.pre-commit-config.yaml`, permissions | **Direct** — branch, commit, PR. The CHANGELOG entry is the record. |

The split is deliberate: the verification layer is the thing Stock exists to
provide, so changes to it go through the flow Stock ships. A CI action bump does
not need a design document.

If you are unsure, ask whether the change alters a promise. Promises go through
OpenSpec.

**Cutover:** this rule starts at v0.2.0 and is not applied backwards. v0.2.0
itself edited `openspec/specs/foundation/spec.md` directly, because it is the
change that introduced the rule — it could not have followed it. Retrofitting an
archived change for it would be a fabricated record, which is worse than an
honest gap. Everything after v0.2.0 follows the table.

## The sequence

### 1. Branch

```bash
git fetch origin main && git checkout -b <topic> origin/main
```

Never commit to `main` directly. Up to and including v0.1.2 that is exactly what
happened — `main` is a linear run of direct commits with no merges — and the
practice stops here.

### 2. Run the change

Per the route table above. If it is a full OpenSpec change, the specs are updated
by `/opsx:archive`, not by editing `openspec/specs/` yourself.

### 3. Get it green

```bash
mise run check          # lint + test, everything CI runs
uvx pre-commit run --all-files
```

### 4. Run UAT — before the PR, not after

Work [`docs/UAT.md`](UAT.md), run the cases you can, and record what you saw.
Cases marked *post-release* cannot run yet; leave them. Reporting a case as open
is the correct outcome — an agent may run the commands and report, but may not
mark a case passed.

### 5. Decide the version and write the CHANGELOG entry

The rule is stated in [`CHANGELOG.md`](../CHANGELOG.md) and repeated here because
it is the decision most often got wrong:

- **major** — a grafted project needs manual intervention to re-sync
- **minor** — the migration is additive; a project that adopts none of it stays green
- **patch** — a fix that changes no interface

The entry is not release notes. **It is the migration instruction** for every
already-grafted project, and it is the only thing standing between "re-sync to
Stock vX" and an archaeology exercise. Write it for someone holding a project
three versions behind.

Bump the version everywhere it appears. There are currently 8 occurrences across
4 files and nothing checks they agree — see the backlog stub at
`openspec/changes/version-string-consistency/`. Until that is built, this step is
manual and easy to half-do:

```bash
grep -rn "$OLD_VERSION" --include="*.md" --include="*.toml" .
```

### 6. Open the PR

Disclose the coding agent and the model. This is not etiquette — it is a
published requirement of the `foundation` spec (*AI Authorship Is Disclosed*),
and it is declared as a review-policy gap in `[tool.graftwork.traceability]`
precisely because no test can enforce it. The only thing keeping it true is
someone doing it.

### 7. Merge, then tag

```bash
git checkout main && git pull origin main
git tag -a v<X.Y.Z> -m "v<X.Y.Z>"
git push origin v<X.Y.Z>
```

Tag after the merge, on `main`, never on the branch. The tag is what
[the graft instructions](../README.md#grafting-a-project-from-stock) clone, so a
missing or misplaced tag breaks new projects rather than existing ones — which
makes it a failure nobody in the repo will notice.

### 8. Run the post-release UAT cases

Now that the tag exists, run the cases that need it and record `Last passed`.
This is the one step that is legitimately *after* the PR, because it verifies the
release rather than the change.

### 9. Push the migration outward

Every entry in the CHANGELOG is work waiting to happen in every grafted project.
Read each project's recorded `stock-version` in its `pyproject.toml`, read this
CHANGELOG forward from there, and open one small PR per entry.

**There are currently no live grafts.** The first one was retired before v0.2.0
shipped, so this step has nothing to do yet — which is also why
[Stock ADR 0008](decisions/stock-0008-adr-numbering.md) could renumber Stock's
own ADRs at no cost to anyone.

Keep the list of grafts here as they appear, and record which Stock version each
one has reached. Nothing tracks whether a migration has landed; if that becomes a
problem before someone builds something better, the honest fix is a checklist in
the CHANGELOG entry itself.

## Why it is worth this much

A change to Stock is not a change to one repo. It is a change to every project
grafted from it, arriving later, applied by someone who was not in the room. The
CHANGELOG entry and the tag are the entire interface for that person.
