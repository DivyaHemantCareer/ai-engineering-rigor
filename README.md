# AI Engineering Rigor

LLM-first code review skill for Python/FastAPI with a strict, structured output schema.

## Structure
- `skills/code_review/python`

## Quickstart
```bash
export LLM_PROVIDER=azure
export LLM_API_KEY=your-key
export LLM_ENDPOINT=your-endpoint
export LLM_MODEL=gpt-4o-mini

git diff HEAD~1 | python cli.py --stdin --pr "Add user auth endpoint"
```

## CLI
```bash
# Review a git diff (string)
python cli.py --diff "$(git diff HEAD~1)" --pr "Add user auth endpoint"

# Review from stdin
git diff HEAD~1 | python cli.py --stdin

# JSON output
git diff HEAD~1 | python cli.py --stdin --format json
```

## Output format
The review returns JSON like:
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
