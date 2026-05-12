---
name: ai-rigor-dev
description: Development execution rigor for a single task. Use when implementing features, fixes, refactors, architecture/design updates, or unit tests and when the user wants a production-ready dev handoff. Reads repo standards from .ai-rigor/ when present.
argument-hint: <task or acceptance criteria>
---

# AI Engineering Rigor -- Development

Apply development rigor to `$ARGUMENTS`. This is a delivery workflow skill, not a separate runtime agent.

## Phase 0: Load Context

Before coding:
1. Read `.ai-rigor/config.yml` if it exists for repo preferences.
2. Read `.ai-rigor/standards.md` if it exists for team standards.
3. Check current branch and `git status --short`.
4. Read relevant architecture/docs if present.

If acceptance criteria are missing and cannot be inferred safely, ask a concise clarification before editing.

## Phase 1: Scope the Change

Identify:
- impacted modules and public contracts
- tests likely affected
- security, config, data, or deployment impact
- whether QA or Infra handoff is needed

For non-trivial changes, prepare a short design impact note using `references/templates.md`.

## Phase 2: Implement

Follow the repo's existing patterns.

Rules:
- Keep changes minimal and reviewable.
- Follow SOLID, DRY, KISS, and YAGNI.
- Do not add dependencies without explicit user approval.
- Do not commit secrets or generated noise.
- Keep production-ready structure; do not add unnecessary files or folders.
- Add or update tests for changed behavior.

## Phase 3: Validate

Run only relevant local checks. Prefer repo-defined scripts.

Default examples when applicable:
- Backend: `pytest`
- Frontend: `npm test`
- Static checks: repo-configured lint/typecheck commands

Do not run commands that install dependencies as a side effect unless the user has approved.

## Phase 4: Handoff

Use `references/templates.md` for:
- `DESIGN_IMPACT_NOTE`
- `DEV_TO_QA_HANDOFF`
- `DEV_TO_INFRA_HANDOFF`
- `TASK_COMPLETION_CHECKLIST`

## Output

When complete, report:
1. Design impact summary.
2. Change list with files and behavior.
3. Test evidence.
4. QA handoff packet if applicable.
5. Infra handoff packet if applicable.
6. Any docs/tracking updates.
