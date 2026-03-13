---
name: ai-rigor-deps
description: Audit dependency changes for security risk -- unpinned versions, known vulnerabilities, unnecessary packages. Use when the user asks about dependency changes, supply chain risk, or package security. Reads allowed packages from .ai-rigor/config.yml.
argument-hint: [commit-range] -- defaults to HEAD~1
---

# AI Engineering Rigor -- Dependency Audit

Audit dependency changes in `$ARGUMENTS` (default: `HEAD~1`).

## Phase 0: Load Config

Check for `.ai-rigor/config.yml`. If it exists, read the `deps` section for:
- `files` -- which dependency files to check (default: auto-detect)
- `allowed` -- known-good packages that should not be flagged

## Phase 1: Get Dependency Diff

```
git diff $ARGUMENTS -- requirements*.txt pyproject.toml setup.py setup.cfg Pipfile poetry.lock package.json
```

If config specifies `deps.files`, check those files instead.

If no dependency files changed, report "No dependency changes detected" and stop.

## Phase 2: Parse Changes

- Lines with `+` (not `+++`) = added
- Lines with `-` (not `---`) = removed
- Extract: package name, version specifier

## Phase 3: Risk Assessment

For each **added** dependency:

| Pattern | Risk |
|---------|------|
| `package==1.2.3` | LOW -- exact pin |
| `package>=1.2,<2.0` | LOW -- bounded |
| `package>=1.2` | MEDIUM -- unbounded upper |
| `package` (no version) | HIGH -- unpinned |

Skip packages listed in `deps.allowed` from config -- these are pre-approved.

Also check:
- Known CVEs for recent versions
- Typosquat risk (similar names to popular packages)
- Is it necessary, or does stdlib/existing deps cover this?

For **removed** dependencies:
- Grep the codebase for `import {package}` -- still imported = broken removal

## Phase 4: Codebase Cross-Reference

For each new dep, search for `import {package}` or `from {package}`. Flag:
- Added but never imported = potentially unnecessary
- Removed but still imported = broken removal

## Phase 5: Output

```
## Dependency Audit

**Config**: {.ai-rigor/config.yml | defaults}
**Allowed (pre-approved)**: {list from config, or "none configured"}

### Changes

| Action | Package | Version | Risk |
|--------|---------|---------|------|
| Added | boto3 | (unpinned) | HIGH |
| Added | pyjwt | >=2.0.0 | LOW |
| Removed | requests | >=2.28.0 | -- |

### Risk Flags

**[HIGH] boto3 -- Unpinned dependency**
No version specifier. Future install could pull breaking version.
**Fix**: Pin to `boto3>=1.28.0,<2.0.0`

### Codebase Check

| Package | Imported? | Files |
|---------|-----------|-------|
| boto3 | Yes | app/storage.py |
| pyjwt | No | (may be unused) |

### Summary
| Metric | Value |
|--------|-------|
| Added | {N} |
| Removed | {N} |
| High / Medium / Low Risk | {N} / {N} / {N} |
| **Overall Risk** | **{HIGH/MEDIUM/LOW}** |
```
