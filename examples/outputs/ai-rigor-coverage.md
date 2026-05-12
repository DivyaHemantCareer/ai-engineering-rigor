# Example Output: ai-rigor-coverage

## Test Coverage Analysis

**Config**: `.ai-rigor/config.yml`

### app/users.py -> tests/test_users.py

| Function | Status | Notes |
|----------|--------|-------|
| `create_user(request: CreateUserRequest)` | Uncovered | No direct test found |
| `get_user(user_id: UUID)` | Covered | `test_get_user_returns_user` |

### Suggested Tests

**`create_user(request: CreateUserRequest)`**

1. `test_create_user_returns_created_user` -- verifies successful creation.
2. `test_create_user_rejects_duplicate_email` -- verifies conflict behavior.
3. `test_create_user_requires_valid_email` -- verifies request validation.

### Summary

| Metric | Value |
|--------|-------|
| Functions Changed | 2 |
| Covered | 1 |
| Uncovered | 1 |
| **Coverage Gap** | **50%** |
