# TypeScript / React Team Standards

## TypeScript
- Avoid `any`; use explicit types, generics, or discriminated unions.
- Public component props must be typed.
- Handle nullable and loading states explicitly.
- Keep data transformation logic outside presentation components when it grows.

## React
- Prefer accessible semantic HTML before custom widgets.
- Buttons and controls must have clear labels or accessible names.
- Avoid unnecessary global state; keep state local unless it is shared across flows.
- Do not expose secrets or privileged configuration to client-side code.

## API and Data
- Validate server responses before trusting shape-sensitive data.
- Handle failed requests with user-appropriate error states.
- Avoid logging tokens, personal data, or sensitive payloads.

## Tests
- Cover changed components with user-visible behavior tests.
- Include loading, empty, error, and success states.
- Add regression tests for bug fixes.
