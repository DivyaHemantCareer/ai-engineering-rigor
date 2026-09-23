---
name: ai-rigor-infra
description: Infrastructure rigor for a single task. Use when creating or updating IaC, validating existing resources, preparing deployment or maintenance scripts, checking security baselines, or producing infra readiness sign-off. Reads repo standards from .ai-rigor/ when present.
allowed-tools: Bash(git *), Bash(terraform *), Bash(az *), Bash(aws *), Bash(gcloud *), Bash(python *), Read, Grep, Glob, Edit, MultiEdit, Write
argument-hint: <infra task, handoff, or target environment>
---

# AI Engineering Rigor -- Infrastructure

Apply infrastructure rigor to `$ARGUMENTS`. This is an infra workflow skill, not a separate runtime agent.

## Phase 0: Load Context

Before editing:
1. Read `.ai-rigor/config.yml` if it exists.
2. Read `.ai-rigor/standards.md` if it exists.
3. Review the Dev-to-Infra handoff and target environment.
4. Check current branch and `git status --short`.

If required infra inputs are missing, request the missing details before changing IaC or scripts.

## Phase 1: Classify the Change

Classify as new infrastructure, existing infrastructure update, or validation/maintenance only.

Prefer IaC for new or changed resources. For existing resources, use validation, drift checks, and safe update scripts when appropriate.

## Phase 2: Implement

Rules:
- Keep blast radius minimal.
- Use managed identity or equivalent platform identity; do not embed secrets.
- Enforce least privilege.
- Enforce encryption in transit and at rest where applicable.
- Do not add dependencies without explicit user approval.
- Require human approval before significant apply/deployment actions.

## Phase 3: Validate

Use dry-run, plan, what-if, lint, or validation commands when available.

Do not run commands that install dependencies as a side effect unless the user has approved.

## Phase 4: Sign Off

Use `references/templates.md` for `INFRA_CHANGE_PLAN`, `INFRA_VALIDATION_REPORT`, `INFRA_SIGNOFF_PACKET`, and `INFRA_COMPLETION_CHECKLIST`.

## Output

When complete, report change classification and plan, IaC/script changes, validation evidence, security checks, and infra decision: `READY` or `NOT READY`, with rationale.
