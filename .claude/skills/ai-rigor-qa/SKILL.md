---
name: ai-rigor-qa
description: Quality assurance rigor for validating a single task. Use when testing UI/API acceptance criteria, documenting defects with reproducible evidence, retesting fixes, or issuing QA pass/fail sign-off before release. Reads repo standards from .ai-rigor/ when present.
allowed-tools: Bash(git *), Bash(pytest *), Bash(npm *), Bash(python *), Read, Grep, Glob
argument-hint: <task, diff, handoff, or acceptance criteria>
---

# AI Engineering Rigor -- QA

Apply QA rigor to `$ARGUMENTS`. This is a validation workflow skill, not a separate runtime agent.

## Phase 0: Load Context

Before testing:
1. Read `.ai-rigor/config.yml` if it exists.
2. Read `.ai-rigor/standards.md` if it exists.
3. Review the dev handoff, acceptance criteria, and run/test instructions.
4. Check current branch and `git status --short`.

If the dev handoff or acceptance criteria are incomplete, identify the missing details before signing off.

## Phase 1: Build the Test Matrix

Cover each acceptance criterion, changed UI flows or API endpoints, negative/error paths, and adjacent regression areas.

Use `references/templates.md` for `QA_TEST_PLAN`.

## Phase 2: Execute Validation

Run only relevant checks. Prefer repo-defined scripts and explicit user instructions.

Default examples when applicable:
- Backend: `pytest`
- Frontend: `npm test`
- Browser/UI checks: use available browser tooling when the task is UI-facing

Do not run commands that install dependencies as a side effect unless the user has approved.

## Phase 3: Record Defects

For each defect, include severity, area, preconditions, reproducible steps, expected vs actual behavior, and evidence.

Use `references/templates.md` for `QA_BUG_REPORT`.

## Phase 4: Sign Off

Do not sign off if blocker or critical defects remain open unless the user gives an explicit waiver.

Use `references/templates.md` for `QA_SIGNOFF_PACKET` and `QA_COMPLETION_CHECKLIST`.

## Output

When complete, report scenarios tested, defects by severity, retest outcomes, and QA decision: `PASS` or `FAIL`, with rationale.
