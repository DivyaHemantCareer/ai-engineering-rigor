# Team Coding Standards
# Drop this file at .ai-rigor/standards.md and the review skill will use it.
# Delete sections you don't need. Add your own.

## Python / FastAPI
- All routes must use Pydantic request/response models — no raw dicts
- Authentication via FastAPI Depends() injection — no manual token parsing
- All database calls must be async — no blocking sync DB calls in async routes
- No raw SQL queries — use ORM or parameterized queries only
- All public functions must have type hints
- Use HTTPException for error responses — no generic Exception raises
- Environment variables via os.getenv() — no hardcoded secrets

## Security
- No hardcoded API keys, passwords, tokens, or secrets
- All user inputs must be validated via Pydantic before use
- No f-strings in database queries — SQL injection risk
- No subprocess calls with unsanitized user input
- Admin routes must have explicit admin role verification
- Passwords must never be logged or returned in responses
- JWT tokens must be validated for expiry and signature
- CORS must be restricted to known origins — no wildcard allow_origins=["*"]
- File uploads must validate type and size

## Code Quality
- Functions should do one thing — max 30 lines
- No nested try/except blocks deeper than 2 levels
- All error messages must be actionable — not just "Something went wrong"
- Test coverage required for all new public functions
- No TODO comments in merged code — create tickets instead

## Git / PR Conventions
- Conventional commit format required: type(scope): description
- PR descriptions must explain WHY, not just WHAT
- One logical change per PR — no unrelated changes bundled together
