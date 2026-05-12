# Python / FastAPI Team Standards

## FastAPI
- Routes must use Pydantic request and response models.
- Authentication and authorization must use dependency injection.
- Async routes must not call blocking database or network clients.
- Use `HTTPException` for API errors instead of generic exceptions.
- Route responses must not expose passwords, tokens, secrets, or internal stack traces.

## Data Access
- Use ORM APIs or parameterized queries.
- Do not build SQL with f-strings or string concatenation.
- Add pagination to list endpoints that can grow unbounded.

## Python Quality
- Public functions must have type hints.
- Keep functions focused and easy to test.
- Avoid broad `except Exception` unless the error is re-raised or translated with context.

## Tests
- Add tests for route validation, auth failures, happy paths, and expected error responses.
- Use fixtures for repeated setup.
- Mock external services at the boundary.
