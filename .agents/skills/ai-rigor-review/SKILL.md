---
name: ai-rigor-review
description: LLM-first code review -- accepts a GitHub PR link or number, commit range, or file path. Reviews for security, performance, quality, and correctness with minimal context extraction. Use when the user asks to review code, a diff, a commit, or a PR. Reads team standards from .ai-rigor/standards.md.
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

**If only a PR number**:
- If `.ai-rigor/config.yml` sets `source_control.github.owner`/`repo`, use `gh pr view <number> --repo <owner>/<repo> ...` and `gh pr diff <number> --repo <owner>/<repo>`
- Otherwise run `gh pr diff <number>` against the current repository's remote

**Other hosts** (GitLab, Bitbucket, Azure DevOps, etc.): not fetched directly. Ask the user to check out the branch and review a commit range instead.

**Commit range** (e.g., `HEAD~3`): `git diff $ARGUMENTS`
**File path** (e.g., `app/auth.py`): `git diff HEAD -- $ARGUMENTS`
**Default**: `git diff HEAD~1`

## Phase 2: Extract Code Context (minimal tokens)

For each changed file (skipping files matching `ignore` patterns from config):

Extract ONLY:
- **Filename** -- from `+++ b/` header
- **Changed hunks** -- added/removed lines only
- **Imports** -- deduplicated
- **Function/method signatures** -- e.g. `def foo(x: int) -> str`, `export function foo(x: number): string`, `func (s *Svc) Foo(x int) error`; NOT bodies
- **Type/class declarations** -- class, interface, struct, type alias headers only
- **Decorators, annotations, and route registrations** -- e.g. `@app.post("/users")`, `@UseGuards(...)`, `router.post("/users", ...)`

**Read full file** ONLY for security-sensitive changes (auth, crypto, SQL/queries, subprocess/shell, deserialization, file paths).

## Phase 3: Gather Intent

Use whatever is available:
- PR title/description (from Phase 1)
- Commit messages
- Linked work items or issues

## Phase 4: Apply Standards

**If `.ai-rigor/standards.md` exists**, review against those team standards.

**Otherwise**, use these language-neutral defaults, applied with the idioms of the language and framework in the diff:

### SECURITY
- Hardcoded secrets, API keys, tokens, passwords
- Injection: SQL/NoSQL, shell/command, template, path traversal, unsafe deserialization
- Missing or bypassable authentication/authorization checks on new entry points
- Overly permissive CORS, missing CSRF protection for cookie-authenticated state changes, token/JWT validation gaps
- Sensitive data in logs, error responses, URLs, or analytics

### INPUT AND CONTRACTS
- External input (HTTP bodies, params, env, files, messages) used without validation against a schema or type
- Public API/contract changes that break existing callers or stored data without versioning
- Errors that leak internals, or that are swallowed silently

### TYPE SAFETY AND CORRECTNESS
- Escape hatches that defeat the type system (`Any`/`any`, unchecked casts, ignored errors, `interface{}` misuse)
- Unhandled null/None/undefined/nil and optional values
- Off-by-one and boundary conditions (`>` vs `>=`), time zones and units

### CONCURRENCY AND PERFORMANCE
- Blocking calls on async/event-loop paths; unbounded goroutines, threads, or promises
- N+1 queries, missing pagination or limits, unbounded memory growth
- Races on shared state; missing timeouts and retries on network calls

### CODE QUALITY
- Deep nesting, dead code, duplicated logic, unclear naming
- Missing error handling at system boundaries
- Changed behavior without corresponding tests

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
| Standards Source | {.ai-rigor/standards.md | built-in language-neutral defaults} |
| **Recommendation** | **{worst across all files}** |
```

## Rules

- Only review what is in the diff -- do not hallucinate issues
- Reference exact line numbers
- Show the fix, not just the problem
- If no issues, approve. Don't manufacture issues.
- CRITICAL = BLOCK_MERGE, HIGH = REQUEST_CHANGES, MEDIUM/LOW = APPROVE_WITH_COMMENTS, None = APPROVE
