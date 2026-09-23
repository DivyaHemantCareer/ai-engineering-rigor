---
name: ai-rigor-deps
description: Audit dependency changes for security risk -- unpinned versions, lockfile drift, known vulnerabilities, unnecessary packages. Supports Python, npm/pnpm/Yarn, and Go. Use when the user asks about dependency changes, supply chain risk, or package security. Reads allowed packages from .ai-rigor/config.yml.
argument-hint: [commit-range] -- defaults to HEAD~1
---

# AI Engineering Rigor -- Dependency Audit

Audit dependency changes in `$ARGUMENTS` (default: `HEAD~1`).

This skill is read-only. Never run a command that installs, updates, or removes packages (`pip install`, `uv sync`, `npm install`, `npm ci`, `pnpm install`, `yarn`, `go get`) unless the user explicitly approves it.

## Phase 0: Load Config

Check for `.ai-rigor/config.yml`. If it exists, read the `deps` section for:
- `files` -- which dependency files to check (default: auto-detect)
- `allowed` -- known-good packages that should not be flagged

## Phase 1: Get Dependency Diff

Auto-detect changed manifest and lock files, including workspace/monorepo subfolders:

```
git diff --name-only $ARGUMENTS
```

| Ecosystem | Manifests | Lockfiles |
|-----------|-----------|-----------|
| Python | `requirements*.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile` | `poetry.lock`, `uv.lock`, `Pipfile.lock` |
| JavaScript / TypeScript | `package.json` (root and workspaces) | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` |
| Go | `go.mod` | `go.sum` |

Then `git diff $ARGUMENTS -- <files>`. If config specifies `deps.files`, check those files instead.

If no dependency files changed, report "No dependency changes detected" and stop.

## Phase 2: Parse Changes

- Lines with `+` (not `+++`) = added; lines with `-` (not `---`) = removed
- For JSON manifests, compare `dependencies`, `devDependencies`, `peerDependencies`, and `optionalDependencies` by key
- Extract: package name, version specifier, and (for workspaces) which workspace changed

## Phase 3: Risk Assessment

For each **added or version-changed** dependency:

| Ecosystem | Pattern | Risk |
|-----------|---------|------|
| Python | `package==1.2.3` | LOW -- exact pin |
| Python | `package>=1.2,<2.0` | LOW -- bounded |
| Python | `package>=1.2` | MEDIUM -- unbounded upper |
| Python | `package` (no version) | HIGH -- unpinned |
| npm | `1.2.3` | LOW -- exact pin |
| npm | `~1.2.3` / `^1.2.3` | LOW if lockfile committed, else MEDIUM; MEDIUM if standards require exact pins |
| npm | `*`, `latest`, `>=`, git/URL/`file:` spec | HIGH -- unbounded or unverifiable |
| Go | tagged `vX.Y.Z` | LOW |
| Go | pseudo-version / `replace` to a fork or local path | MEDIUM -- review |

Cross-ecosystem checks:
- **Lockfile drift** -- manifest changed without its lockfile (or the reverse) = HIGH
- **Install scripts** -- new npm package with `hasInstallScript` in the lockfile, or a new `postinstall`/`preinstall` = MEDIUM, review
- Known CVEs for the added versions
- Typosquat risk (similar names to popular packages)
- License compatibility when the project states a license policy
- Is it necessary, or does the standard library / an existing dependency cover this?

Skip packages listed in `deps.allowed` from config -- these are pre-approved.

## Phase 4: Codebase Cross-Reference

Search imports for each added or removed dependency:

| Ecosystem | Import patterns |
|-----------|-----------------|
| Python | `import {package}`, `from {package}` |
| JavaScript / TypeScript | `from "{package}"`, `require("{package}")`, `import("{package}")` |
| Go | `"{module path}"` in import blocks |

Flag:
- Added but never imported = potentially unnecessary (check config files and CLI usage before concluding)
- Removed but still imported = broken removal

## Phase 5: Vulnerability Scan (read-only, optional)

Only when dependencies are already installed locally, run the ecosystem's read-only audit (`pip-audit` if present, `npm audit --audit-level=high`, `pnpm audit`, `yarn audit`, `govulncheck` if present). Otherwise state that no local audit was run.

## Phase 6: Output

```
## Dependency Audit

**Config**: {.ai-rigor/config.yml | defaults}
**Ecosystems**: {detected}
**Allowed (pre-approved)**: {list from config, or "none configured"}

### Changes

| Action | Ecosystem | Package | Version | Risk |
|--------|-----------|---------|---------|------|
| Added | Python | boto3 | (unpinned) | HIGH |
| Added | npm | zod | 4.1.0 | LOW |
| Removed | Python | requests | >=2.28.0 | -- |

### Risk Flags

**[HIGH] boto3 -- Unpinned dependency**
No version specifier. Future install could pull breaking version.
**Fix**: Pin to `boto3>=1.28.0,<2.0.0`

### Codebase Check

| Package | Imported? | Files |
|---------|-----------|-------|
| boto3 | Yes | app/storage.py |
| zod | Yes | src/schemas.ts |
| requests | Still imported | app/client.py -- broken removal |

### Vulnerability Scan
{command run and result, or "not run -- dependencies not installed locally"}

### Summary
| Metric | Value |
|--------|-------|
| Added | {N} |
| Removed | {N} |
| High / Medium / Low Risk | {N} / {N} / {N} |
| **Overall Risk** | **{HIGH/MEDIUM/LOW}** |
```

## Rules

- Only flag **real** risks -- don't flag well-known, pinned packages
- Pre-approved packages from config are listed but not flagged
- Consider transitive/peer dependency implications for removals
- Keep suggestions actionable with specific version pins
