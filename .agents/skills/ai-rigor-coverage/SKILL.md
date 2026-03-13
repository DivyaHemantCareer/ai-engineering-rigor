---
name: ai-rigor-coverage
description: Analyze changed Python functions and identify missing test coverage -- suggest specific test cases. Use when the user asks about test coverage, missing tests, or untested code. Reads ignore patterns from .ai-rigor/config.yml.
argument-hint: [commit-range or file path] -- defaults to HEAD~1
---

# AI Engineering Rigor -- Test Coverage Analysis

Analyze `$ARGUMENTS` (default: `HEAD~1`) for test coverage gaps.

## Phase 0: Load Config

Check for `.ai-rigor/config.yml`. If it exists, read:
- `review.ignore` -- file patterns to skip
- Any test conventions from `.ai-rigor/standards.md`

## Phase 1: Extract Changed Functions

1. Get the diff (same input detection as ai-rigor-review):
   - File path: `git diff HEAD -- <path>`
   - Commit range: `git diff <range>`
   - Default: `git diff HEAD~1`

2. For each changed Python file (skipping ignored patterns), extract:
   - All `def` and `async def` signatures
   - Skip `__dunder__` methods and `test_*` functions

3. Map source files to expected test files:
   - `app/service.py` -> search for `tests/test_service.py` or `tests/test_app_service.py`
   - Use Glob: `**/test_*{stem}*.py`

## Phase 2: Check Existing Coverage

For each changed function:
1. Grep for the function name in the mapped test file(s)
2. Mark as **covered** or **uncovered**
3. For covered functions, check if the test is meaningful

## Phase 3: Suggest Missing Tests

For each uncovered function, suggest:
- **Happy path** -- expected result for normal input
- **Edge cases** -- empty, None, boundary values
- **Error paths** -- invalid input behavior
- **Integration** -- DB, API, or filesystem interactions

## Output

```
## Test Coverage Analysis

**Config**: {.ai-rigor/config.yml | defaults}

### {source_file} -> {test_file}

| Function | Status | Notes |
|----------|--------|-------|
| `create_user(username, email)` | Uncovered | No test found |
| `get_user(user_id)` | Covered | test_get_user in test_service.py |

### Suggested Tests

**`create_user(username, email)`**
1. `test_create_user_returns_dict` -- verify returns dict with expected fields
2. `test_create_user_empty_username` -- verify behavior with empty string
3. `test_create_user_special_characters` -- verify unicode handling

### Summary

| Metric | Value |
|--------|-------|
| Functions Changed | {N} |
| Covered | {N} |
| Uncovered | {N} |
| **Coverage Gap** | **{N}%** |
```

## Rules

- Only analyze functions **changed in the diff**
- Skip test files, `__init__.py`, migrations, and files matching ignore patterns
- Suggest practical, implementable tests
- Trivial one-liners: note them, don't flag as critical
