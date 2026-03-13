from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


# Built-in default standards for Python/FastAPI
# Used when no custom standards file is provided
DEFAULT_FASTAPI_STANDARDS = """
CODING STANDARDS (Python/FastAPI):
- All routes must use Pydantic request/response models — no raw dicts
- Authentication via FastAPI Depends() injection — no manual token parsing
- All database calls must be async — no blocking sync DB calls
- No raw SQL queries — use ORM or parameterized queries only
- All public functions must have type hints
- Sensitive data must never appear in logs or error responses
- CORS must be restricted to known origins — no wildcard allow_origins=['*']
- All endpoints must have explicit response_model defined
- Use HTTPException for error responses — no generic Exception raises
- Environment variables via os.getenv() — no hardcoded secrets
"""

DEFAULT_SECURITY_RULES = """
SECURITY RULES:
- No hardcoded API keys, passwords, tokens, or secrets
- All user inputs must be validated via Pydantic before use
- No f-strings in database queries — SQL injection risk
- No subprocess calls with unsanitized user input
- Admin routes must have explicit admin role verification
- Passwords must never be logged or returned in responses
- JWT tokens must be validated for expiry and signature
- File uploads must validate type and size
"""


@dataclass
class StandardsContext:
    """
    Layer 3 — Team conventions and security rules.
    Configured ONCE per repo, reused across every review.
    Falls back to built-in FastAPI/Python standards if not provided.
    """
    custom_standards: Optional[str] = None
    custom_security_rules: Optional[str] = None
    standards_file_path: Optional[str] = None

    def load_from_file(self, path: str) -> None:
        """Load custom standards from a markdown or text file."""
        file = Path(path)
        if file.exists():
            self.custom_standards = file.read_text()
            self.standards_file_path = path
        else:
            raise FileNotFoundError(f"Standards file not found: {path}")

    def to_prompt_payload(self) -> str:
        """
        Serialize standards into compact prompt string.
        Uses custom standards if provided, falls back to defaults.
        """
        parts = []

        standards = self.custom_standards or DEFAULT_FASTAPI_STANDARDS
        parts.append(standards.strip())

        security = self.custom_security_rules or DEFAULT_SECURITY_RULES
        parts.append(security.strip())

        source = f"(source: {self.standards_file_path})" if self.standards_file_path else "(source: built-in defaults)"
        parts.append(f"STANDARDS {source}")

        return "\n\n".join(parts)

    def is_custom(self) -> bool:
        return self.custom_standards is not None
