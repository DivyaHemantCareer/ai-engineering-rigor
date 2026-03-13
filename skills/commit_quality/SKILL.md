# Commit Message Quality Skill

## What This Skill Does
Analyzes git commit messages for quality and conventional commit compliance.
Uses regex for format validation (no LLM for passing commits).
LLM only invoked for rewrite suggestions on failing commits.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `commit_message` | Yes | The commit message to analyze |
| `diff` | Optional | Git diff to check scope/file alignment |

## Outputs

Returns `CommitQualityResult` with:
- `format_valid` — whether commit follows conventional format
- `scope_matches_files` — whether scope aligns with changed files
- `issues` — list of problems found
- `suggested_rewrite` — LLM-suggested improved message (only if issues found)
- `score` — 0-100 quality score

## Example Usage

```python
from skills.commit_quality.skill import CommitQualitySkill
from skills.code_review.python.llm_provider import LLMConfig

skill = CommitQualitySkill(llm_config=LLMConfig.from_env())
result = skill.analyze(
    commit_message="fix(auth): resolve JWT expiry check",
    diff=git_diff
)
print(f"Score: {result.score}, Valid: {result.format_valid}")
```
