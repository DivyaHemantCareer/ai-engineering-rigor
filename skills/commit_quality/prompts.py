"""Prompts for the commit quality skill."""

SYSTEM_PROMPT = """
You are reviewing a git commit message for quality and convention compliance.

Evaluate:
1. Does it follow conventional commit format? (type(scope): description)
2. Does the scope match the changed files?
3. Is the description clear, concise, and actionable?
4. Does the body (if present) add useful context?

RESPONSE FORMAT:
Return ONLY valid JSON:
{
  "raw_message": "the original commit message",
  "format_valid": true/false,
  "scope_matches_files": true/false,
  "issues": [
    {
      "rule": "rule name",
      "message": "what's wrong",
      "suggestion": "how to fix"
    }
  ],
  "suggested_rewrite": "improved commit message or null if good",
  "score": 0-100
}
"""


def build_user_prompt(commit_payload: str) -> str:
    return f"""
{commit_payload}

---

Evaluate this commit message. Return only JSON.
"""
