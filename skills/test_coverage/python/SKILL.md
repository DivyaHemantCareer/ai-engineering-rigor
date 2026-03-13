# Test Coverage Analysis Skill

## What This Skill Does
Analyzes changed Python functions in a diff and identifies missing test coverage.
Uses naming conventions (`foo.py` -> `test_foo.py`) to map source to test files.
The LLM suggests specific test cases for uncovered functions.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `diff` | Yes | Git diff output |

## Outputs

Returns `CoverageAnalysisResult` with:
- `source_file` — file being analyzed
- `expected_test_file` — where tests should live
- `total_functions` — count of changed functions
- `uncovered_functions` — list of function names lacking tests
- `suggested_tests` — specific test suggestions with descriptions
- `coverage_gap_summary` — one-line summary

## Example Usage

```python
from skills.test_coverage.python.skill import PythonTestCoverageSkill
from skills.code_review.python.llm_provider import LLMConfig

skill = PythonTestCoverageSkill(llm_config=LLMConfig.from_env())
result = skill.analyze(diff=git_diff)

for test in result.suggested_tests:
    print(f"{test.test_name}: {test.description}")
```
