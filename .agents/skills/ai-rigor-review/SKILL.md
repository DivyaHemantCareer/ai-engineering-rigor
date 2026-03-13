---
name: ai-rigor-review
description: LLM-first code review -- accepts a PR link (GitHub/ADO), commit range, or file path. Reviews for security, performance, quality, and correctness with minimal context extraction. Use when the user asks to review code, a diff, a commit, or a PR. Reads team standards from .ai-rigor/standards.md.
argument-hint: <PR-URL, PR-number, commit-range, or file-path>
---

# AI Engineering Rigor -- Code Review

Review `$ARGUMENTS`. You are a **second-opinion reviewer** -- reason independently. Think like a senior engineer AND a security auditor.

## Phase 0: Load Config

**Before doing anything else**, check for repo configuration:

1. **Read `.ai-rigor/config.yml`** (if it exists) -- get source control settings, ignore patterns, and review preferences
2. **Read `.ai-rigor/standards.md`** (if it exists) -- team coding standards and conventions. If this file exists, use it AS your review standards instead of the defaults below.

If neither file exists, use the built-in defaults. That's fine -- config is optional.

## Phase 1: Detect Input & Get Diff

Parse `$ARGUMENTS` to determine what you're reviewing:

**PR Link (GitHub)** -- matches `github.com/.../pull/\d+`:
1. `gh pr view <URL> --json title,body,author,baseRefName,headRefName,files`
2. `gh pr diff <URL>`

**PR Link (Azure DevOps)** -- matches `dev.azure.com` or `visualstudio.com`:
1. Parse URL for org, project, repo, PR ID
2. Use MCP tools: `repo_get_repo_by_name_or_id` then `repo_get_pull_request_by_id`
3. `az repos pr diff --id <ID> --org <org-url> --project "<project>"`

**If only a PR number** and `.ai-rigor/config.yml` has `source_control` settings:
- Use the configured `org_url` and `project` to build the full reference
- For ADO: `az repos pr show --id <number> --org <org_url> --project "<project>"`
- For GitHub: `gh pr diff <number>`

**Commit range** (e.g., `HEAD~3`): `git diff $ARGUMENTS`
**File path** (e.g., `app/auth.py`): `git diff HEAD -- $ARGUMENTS`
**Default**: `git diff HEAD~1`

## Phase 2: Extract Code Context (minimal tokens)

For each changed file (skipping files matching `ignore` patterns from config):

Extract ONLY:
- **Filename** -- from `+++ b/` header
- **Changed hunks** -- added/removed lines only
- **Imports** -- deduplicated
- **Function signatures** -- `def foo(x: int) -> str` only, NOT bodies
- **Class definitions** -- `class Foo(Base)` only
- **Decorators** -- `@app.post("/users")`, `@require_admin` etc.

**Read full file** ONLY for security-sensitive changes (auth, crypto, SQL, subprocess).

## Phase 3: Gather Intent

Use whatever is available:
- PR title/description (from Phase 1)
- Commit messages
- Linked work items or issues

## Phase 4: Apply Standards

**If `.ai-rigor/standards.md` exists**, review against those team standards.

**Otherwise**, use these defaults:

### SECURITY
- Hardcoded secrets, API keys, tokens, passwords
- SQL injection, command injection
- Auth gaps, CORS wildcards, JWT validation gaps
- Sensitive data in logs or error responses

### FRAMEWORK PATTERNS
- Missing Pydantic models, manual token parsing
- Sync DB calls in async routes, missing response_model
- Generic Exception instead of HTTPException

### TYPE SAFETY
- Missing type hints, Any types, unhandled Optional

### PERFORMANCE
- N+1 queries, blocking calls in async, missing pagination

### CODE QUALITY
- Deep nesting, dead code, unclear naming
- Missing error handling at system boundaries

## Phase 5: Output Structured Review

For EACH changed file:

```
## {filename}

**Risk Score**: {0-100} | **Security Score**: {100-0}
**Recommendation**: {APPROVE | APPROVE_WITH_COMMENTS | REQUEST_CHANGES | BLOCK_MERGE}

### Summary
{One sentence -- most critical finding first}

### Issues
**[{SEVERITY}] {ID}** -- Line {N}
> `{exact code snippet}`
{Description}
**Fix**: {Concrete fix -- show corrected code}
```

Then:

```
## Overall

| Metric | Value |
|--------|-------|
| Files Reviewed | {N} |
| Total Issues | {N} |
| Critical / High / Medium / Low | {N} / {N} / {N} / {N} |
| Standards Source | {.ai-rigor/standards.md | built-in defaults} |
| **Recommendation** | **{worst across all files}** |
```

## Rules

- Only review what is in the diff -- do not hallucinate issues
- Reference exact line numbers
- Show the fix, not just the problem
- If no issues, approve. Don't manufacture issues.
- CRITICAL = BLOCK_MERGE, HIGH = REQUEST_CHANGES, MEDIUM/LOW = APPROVE_WITH_COMMENTS, None = APPROVE
