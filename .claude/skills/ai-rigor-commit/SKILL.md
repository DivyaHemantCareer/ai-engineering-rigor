---
name: ai-rigor-commit
description: Analyze commit message quality — check conventional commit format, scope/file alignment, and suggest rewrites. Reads team config from .ai-rigor/config.yml.
allowed-tools: Bash(git *), Read, Grep, Glob
argument-hint: [commit-ref] — defaults to HEAD
---

# AI Engineering Rigor — Commit Message Quality

Analyze the commit message at `$ARGUMENTS` (default: `HEAD`).

## Phase 0: Load Config

Check for `.ai-rigor/config.yml`. If it exists, read the `commit` section for:
- `conventional` — whether to enforce conventional commits (default: true)
- `types` — allowed commit types (default: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
- `max_subject_length` — max subject line length (default: 72)

Also check `.ai-rigor/standards.md` for any git/PR conventions the team has documented.

## Phase 1: Extract Commit Context

1. `git log --format="%B" -1 $ARGUMENTS` — get commit message
2. `git diff-tree --no-commit-id --name-only -r $ARGUMENTS` — get changed files

## Phase 2: Check Format

Parse the subject line against: `type(scope): description`

| Rule | Check |
|------|-------|
| Conventional format | Matches `type(scope): description` |
| Valid type | One of the allowed types (from config or defaults) |
| Subject length | Under max_subject_length |
| Imperative mood | Verb form ("add" not "added") |
| No period | Subject does not end with `.` |
| Body separation | Blank line between subject and body |
| Scope/files match | Scope relates to changed files |

## Phase 3: Scope/File Alignment

- `feat(auth)` + changes in `app/auth/` — match
- `fix(models)` + changes only in `app/views/` — mismatch
- No scope + 5+ directories changed — suggest adding scope

## Phase 4: Output

```
## Commit Message Analysis

**Message**: `{subject line}`
**Score**: {0-100}/100
**Config**: {.ai-rigor/config.yml | defaults}

### Format Check

| Rule | Status | Details |
|------|--------|---------|
| Conventional format | Pass/Fail | {details} |
| Valid type | Pass/Fail | {type or "none"} |
| Subject length | Pass/Fail | {N} chars |
| Imperative mood | Pass/Fail | {details} |
| Scope matches files | Pass/Fail/N/A | {details} |

### Issues
{List of problems, if any}

### Suggested Rewrite
{Only if issues found}

**Original**: `{original}`
**Suggested**: `{improved}`
```
