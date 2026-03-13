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
  "file": "repository",
  "risk_score": 85,
  "security_score": 40,
  "summary": "Found 1 issue(s).",
  "issues": [
    {
      "id": "SEC-001",
      "type": "SECURITY",
      "severity": "CRITICAL",
      "line": 23,
      "code": "API_KEY = \"...\"",
      "message": "Hardcoded API key detected",
      "suggestion": "Move to environment variable",
      "file": "path/to/file.py"
    }
  ],
  "summary_by_type": {
    "SECURITY": { "CRITICAL": 1, "HIGH": 0, "MEDIUM": 0, "LOW": 0 }
  },
  "recommendation": "BLOCK_MERGE"
}
```
