---
name: ai-rigor-release
description: Release execution rigor for the current repository. Use when planning release builds, validating QA/Infra readiness, deploying to test stage, coordinating production approval, smoke testing, or documenting rollback. Reads repo standards from .ai-rigor/ when present.
argument-hint: <release scope, environment, or sign-off packet>
---

# AI Engineering Rigor -- Release

Apply release rigor to `$ARGUMENTS`. This is a release workflow skill, not a separate runtime agent.

## Phase 0: Load Context

Before release work:
1. Read `.ai-rigor/config.yml` if it exists.
2. Read `.ai-rigor/standards.md` if it exists.
3. Confirm QA sign-off and any Infra readiness notes.
4. Check current branch and `git status --short`.

If QA sign-off is required but missing, stop and request approval before deployment steps.

## Phase 1: Plan the Release

Capture:
- release scope
- source branch/tag/commit
- artifacts and versions
- target environments
- approvals required
- rollback strategy

Use `references/templates.md` for `RELEASE_PLAN`.

## Phase 2: Build and Stage

Rules:
- Follow the repo branch policy.
- Use repeatable scripted steps.
- Capture artifact metadata and commit/tag traceability.
- Deploy to test/stage before production.
- Do not run commands that install dependencies as a side effect unless the user has approved.

## Phase 3: Validate

Run smoke checks after each deployment stage and capture evidence.

Coordinate defects with Dev/QA before production promotion.

## Phase 4: Promote or Roll Back

Require explicit human approval before production promotion.

Before production deployment, ensure rollback is defined and feasible.

Use `references/templates.md` for:
- `STAGE_DEPLOY_REPORT`
- `PROD_PROMOTION_SIGNOFF`
- `ROLLBACK_REPORT`
- `RELEASE_COMPLETION_CHECKLIST`

## Output

When complete, report:
1. Release plan and artifact metadata.
2. Stage deploy result and smoke-check evidence.
3. Production promotion approval and result, if performed.
4. Rollback status, if invoked.
