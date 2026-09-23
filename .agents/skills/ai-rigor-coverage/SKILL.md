---
name: ai-rigor-coverage
description: Analyze changed functions and identify missing test coverage -- suggest specific test cases. Supports Python, JavaScript/TypeScript, and Go. Use when the user asks about test coverage, missing tests, or untested code. Reads ignore patterns from .ai-rigor/config.yml.
argument-hint: [commit-range or file path] -- defaults to HEAD~1
---

# AI Engineering Rigor -- Test Coverage Analysis

Analyze `$ARGUMENTS` (default: `HEAD~1`) for test coverage gaps.

## Phase 0: Load Config

Check for `.ai-rigor/config.yml`. If it exists, read:
- `review.ignore` -- file patterns to skip
- `review.languages` -- limit analysis to these languages (default: auto-detect from extensions)
- Any test conventions from `.ai-rigor/standards.md` (these override the defaults below)

## Phase 1: Extract Changed Functions

1. Get the diff (same input detection as ai-rigor-review):
   - File path: `git diff HEAD -- <path>`
   - Commit range: `git diff <range>`
   - Default: `git diff HEAD~1`

2. For each changed source file (skipping test files, generated files, and ignored patterns), extract the changed symbols for its language:

| Language | Extensions | Extract | Skip |
|----------|-----------|---------|------|
| Python | `.py` | `def` / `async def` | `__dunder__`, `test_*`, `__init__.py`, migrations |
| JavaScript / TypeScript | `.js` `.jsx` `.mjs` `.cjs` `.ts` `.tsx` | exported functions, exported `const` arrow functions, class methods, exported validation schemas | `*.test.*`, `*.spec.*`, `*.d.ts`, `dist/`, `build/` |
| Go | `.go` | `func` and methods | `*_test.go`, generated files (`// Code generated`) |

3. Map source files to likely test files. Detect the repo's convention first (Glob for existing tests), then search:

| Language | Search order |
|----------|--------------|
| Python | `tests/test_{stem}.py`, `tests/**/test_*{stem}*.py`, `{dir}/test_{stem}.py` |
| JavaScript / TypeScript | co-located `{dir}/{stem}.test.{ext}` / `.spec.{ext}`, `{dir}/__tests__/{stem}.*`, `test/**/{stem}*`, then any test in the same folder |
| Go | `{dir}/{stem}_test.go`, then any `_test.go` in the same package |

If no mapped test file exists, Grep for the symbol name across all test files before marking it uncovered.

## Phase 2: Check Existing Coverage

For each changed function:
1. Grep for the function name in the mapped test file(s)
2. Mark as **covered**, **weak** (referenced but the changed branch or condition is not asserted), or **uncovered**
3. For covered functions, check if the test is meaningful

## Phase 3: Suggest Missing Tests

For each uncovered or weak function, suggest tests in the repo's framework (pytest, Vitest/Jest/node:test/Mocha, Go `testing`):
- **Happy path** -- expected result for normal input
- **Edge cases** -- empty, null/None/undefined/nil, boundary values (`>` vs `>=`)
- **Error paths** -- invalid input, rejected validation, returned errors
- **Integration** -- DB, API, or filesystem interactions
- **Invariants** -- any project-specific rules from `.ai-rigor/standards.md`

## Output

```
## Test Coverage Analysis

**Config**: {.ai-rigor/config.yml | defaults}
**Languages**: {detected}

### {source_file} -> {test_file}

| Function | Status | Notes |
|----------|--------|-------|
| `create_user(username, email)` | Uncovered | No test found |
| `get_user(user_id)` | Covered | test_get_user in test_service.py |
| `parseSignal(input)` | Weak | Referenced in signal.test.ts; boundary branch not asserted |

### Suggested Tests

**`create_user(username, email)`**
1. `test_create_user_returns_dict` -- verify returns dict with expected fields
2. `test_create_user_empty_username` -- verify behavior with empty string

**`parseSignal(input)`**
1. `it("rejects values at the exclusive threshold")` -- verify `>` rather than `>=`

### Summary

| Metric | Value |
|--------|-------|
| Functions Changed | {N} |
| Covered | {N} |
| Weak | {N} |
| Uncovered | {N} |
| **Coverage Gap** | **{N}%** |
```

## Rules

- Only analyze functions **changed in the diff**
- Skip test files, generated code, migrations, and files matching ignore patterns
- Follow the repo's existing test framework and file layout; do not introduce a new one
- Suggest practical, implementable tests
- Trivial one-liners: note them, don't flag as critical
- Do not install coverage tooling; recommend it and let the user approve
