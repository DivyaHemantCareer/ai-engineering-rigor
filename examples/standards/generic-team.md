# Generic Team Standards

## Engineering Principles
- Prefer simple, readable implementations over clever abstractions.
- Keep changes scoped to the task and avoid unrelated refactors.
- Public functions should have clear names, type hints or equivalent typing, and focused tests.
- Do not commit generated files, secrets, local environment files, or tool cache directories.

## Security
- No hardcoded secrets, tokens, passwords, or private keys.
- Validate external input at system boundaries.
- Avoid shell execution with unsanitized input.
- Do not log sensitive data.
- Use least privilege for service credentials and deployment identities.

## Testing
- Add or update tests for new behavior and bug fixes.
- Include happy path, error path, and important boundary cases.
- Document any test gaps in the handoff if they are intentionally deferred.

## Git / PR
- Use conventional commits: `type(scope): description`.
- PR descriptions should explain why the change exists and what risk remains.
- Keep one logical change per PR.
