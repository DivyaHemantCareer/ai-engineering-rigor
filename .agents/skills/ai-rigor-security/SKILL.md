---
name: ai-rigor-security
description: Security rigor for secure-by-default implementation and security best-practice reviews. Use when the user explicitly asks for security guidance, a security review/report, hardening, or secure coding help for Python, JavaScript/TypeScript, or Go. Reads language/framework references and repo standards from .ai-rigor/ when present.
argument-hint: <code path, diff, repo, or security question>
---

# AI Engineering Rigor -- Security

Apply security rigor to `$ARGUMENTS`. This skill adapts the security-best-practices guidance into the `ai-rigor-*` skill family.

Use this skill only for explicit security work:
- security best-practice review
- secure-by-default implementation
- hardening
- vulnerability report
- security-focused code review

Do not trigger it for ordinary debugging or general code review unless the user asks for security.

## Phase 0: Load Context

1. Read `.ai-rigor/config.yml` if it exists.
2. Read `.ai-rigor/standards.md` if it exists.
3. Identify all languages and primary frameworks in scope.
4. Load only matching reference files from `references/`.

Reference filenames follow:

`<language>-<framework>-<stack>-security.md`

Also check for general references, such as:
- `python-fastapi-web-server-security.md`
- `python-django-web-server-security.md`
- `python-flask-web-server-security.md`
- `javascript-general-web-frontend-security.md`
- `javascript-typescript-react-web-frontend-security.md`
- `javascript-typescript-nextjs-web-server-security.md`
- `javascript-express-web-server-security.md`
- `golang-general-backend-security.md`

For full-stack web work, check both frontend and backend guidance.

## Phase 1: Choose Mode

Use the mode that matches the user request:

- **Secure implementation**: apply secure defaults while writing code.
- **Passive detection**: flag only critical or high-impact security issues found while working.
- **Security report**: produce a prioritized report with evidence and line numbers.
- **Fixes**: implement one security finding at a time after the user approves the fix scope.

## Phase 2: Review or Implement

Prioritize:
- authn/authz failures
- injection risks
- secret exposure
- unsafe subprocess/file handling
- weak session/cookie/JWT handling
- unsafe CORS or CSRF posture
- sensitive data in logs or responses
- dependency and supply-chain risk when dependency files changed

Follow project-specific rules when they intentionally override generic best practices. Note important overrides instead of fighting them.

## Phase 3: Security Report Format

When the user asks for a report, write it to `security_best_practices_report.md` unless they specify another path.

Include:
1. Executive summary.
2. Prioritized findings by severity.
3. Numeric finding IDs.
4. File and line references.
5. Impact statement for critical findings.
6. Concrete remediation.

After writing the report, summarize the findings and report path to the user.

## Phase 4: Fixes

Before implementing fixes from a report, let the user confirm the fix scope.

When fixing:
- address one finding or tightly related group at a time
- preserve existing behavior where possible
- add concise comments only where the security reason is not obvious
- run relevant tests/checks
- avoid bundling unrelated security changes

## Attribution

Bundled security reference files are adapted from Apache-licensed security best-practices material. Keep `LICENSE.txt` with this skill when redistributing it.
