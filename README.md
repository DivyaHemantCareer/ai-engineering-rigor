# AI Engineering Rigor

Reusable, deterministic AI skills for developer productivity.

## Structure
- `skills/code-review/python`
- `skills/code-review/typescript`

## Skill discovery
```bash
python cli.py list
```

## Run a skill
```bash
python cli.py run --skill-path skills/code-review/python --repo /path/to/repo
```

## Output format
Each skill returns JSON like:
```json
{
  "issues": [
    {
      "type": "SECURITY",
      "severity": "CRITICAL",
      "line": 23,
      "message": "Hardcoded API key detected",
      "suggestion": "Move to environment variable",
      "file": "path/to/file.py"
    }
  ],
  "risk_score": 85,
  "security_score": 40
}
```
