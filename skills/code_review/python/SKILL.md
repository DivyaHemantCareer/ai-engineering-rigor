# Python Code Review Skill
## AI Engineering Rigor

### What This Skill Does
Reviews Python/FastAPI code diffs using LLM reasoning.
Acts as a **second-opinion reviewer** — independent from the coding assistant that wrote the code.

Covers:
- Security vulnerabilities (injection, hardcoded secrets, auth gaps)
- FastAPI anti-patterns (missing Pydantic models, sync routes, CORS issues)
- Type hint coverage
- Performance concerns
- Code quality

---

### When to Use This Skill
Use this skill when:
- A Python or FastAPI file has been changed in a PR
- You need a risk score before merging
- You want security and quality checks on AI-generated code
- You want to enforce team standards automatically

---

### Inputs

| Input | Required | Description |
|---|---|---|
| `diff` | ✅ Yes | Git diff output |
| `pr_description` | Recommended | Intent of the change |
| `ticket_id` | Optional | Ticket/issue reference |
| `spec_summary` | Optional | Acceptance criteria |
| `standards_file` | Optional | Path to team standards .md file |
| `custom_standards` | Optional | Inline standards string |

---

### Outputs

Returns `CodeReviewResult` with:
- `risk_score` — 0 (clean) to 100 (critical)
- `security_score` — 100 (clean) to 0 (critical)
- `issues[]` — list of issues with severity, line, code, suggestion
- `recommendation` — BLOCK_MERGE | REQUEST_CHANGES | APPROVE_WITH_COMMENTS | APPROVE

---

### Example Usage

```python
from skills.code_review.python.skill import PythonCodeReviewSkill
from skills.code_review.python.llm_provider import LLMConfig

skill = PythonCodeReviewSkill(
    llm_config=LLMConfig(
        provider="azure",
        api_key="your-key",
        model="gpt-4o-mini",
        endpoint="your-azure-endpoint"
    )
)

result = skill.review(
    diff=git_diff,
    pr_description="Add user authentication endpoint",
    standards_file="./standards.md"  # optional
)

print(result.recommendation)  # BLOCK_MERGE | APPROVE | ...
print(result.risk_score)       # 0-100
```

---

### Agent Skill Usage

```
# Claude Code
/ai-rigor-review HEAD~1

# Codex
$ai-rigor-review
```

---

### LLM Configuration (Python Library)

Model-agnostic — bring your own LLM:

```python
# Azure AI Foundry
LLMConfig(provider="azure", api_key="...", endpoint="...", model="gpt-4o-mini")

# OpenAI
LLMConfig(provider="openai", api_key="...", model="gpt-4o")
```

---

### Custom Standards

Configure once per repo — reused across every review:

```markdown
# my-standards.md
CODING STANDARDS:
- All routes must use Pydantic models
- Auth via JWT Depends() injection
- No raw SQL queries
```

```python
result = skill.review(diff=diff, standards_file="./my-standards.md")
```

---

### Recommendation Logic

| Condition | Recommendation |
|---|---|
| Any CRITICAL issue | BLOCK_MERGE |
| HIGH issues only | REQUEST_CHANGES |
| MEDIUM/LOW only | APPROVE_WITH_COMMENTS |
| No issues | APPROVE |
