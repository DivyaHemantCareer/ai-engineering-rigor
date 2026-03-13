# Dependency Audit Skill

## What This Skill Does
Parses added/removed dependencies from diffs (requirements.txt, pyproject.toml)
and uses an LLM to reason about risk: CVEs, unpinned versions, unnecessary deps.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `diff` | Yes | Git diff containing dependency file changes |

## Outputs

Returns `DependencyAuditResult` with:
- `new_deps` — newly added dependency names
- `removed_deps` — removed dependency names
- `risk_flags` — risk assessments per dependency
- `summary` — one-line risk overview
- `overall_risk` — HIGH, MEDIUM, or LOW

## Example Usage

```python
from skills.dependency_audit.python.skill import PythonDependencyAuditSkill
from skills.code_review.python.llm_provider import LLMConfig

skill = PythonDependencyAuditSkill(llm_config=LLMConfig.from_env())
result = skill.audit(diff=git_diff)

for flag in result.risk_flags:
    print(f"[{flag.risk_level}] {flag.dependency}: {flag.reason}")
```
