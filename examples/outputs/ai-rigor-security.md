# Example Output: ai-rigor-security

## Security Best-Practices Report

### Executive Summary

The changed FastAPI authentication path is mostly aligned with the team standards, but one high-risk authorization gap should be fixed before merge.

### High Severity

**SEC-001: Admin route lacks explicit role verification**

- File: `app/admin.py`
- Line: 31
- Impact: Any authenticated user could access an admin-only action.
- Evidence: The route depends on `get_current_user` but does not verify an admin role.

**Remediation**:

```python
@router.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(user_id: UUID) -> DeleteUserResponse:
    ...
```

### Decision

Recommendation: `REQUEST_CHANGES`
