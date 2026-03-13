# Skill: Python Code Review

## Purpose
Deterministic static scan for critical security issues in Python repositories.

## Inputs
- `repo_path`: Path to the target repository.

## Outputs
- JSON printed to stdout with fields:
  - `issues` (list)
  - `risk_score` (0-100)
  - `security_score` (0-100)

## How to run
```bash
python skills/code-review/python/skill.py /path/to/repo
```

## Exit codes
- `0` on success
- `1` on unexpected failure

## Notes
This v1 skill is non-interactive and uses deterministic heuristics only.
