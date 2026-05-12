# Example Output: ai-rigor-review

## app/auth.py

**Risk Score**: 72 | **Security Score**: 45  
**Recommendation**: REQUEST_CHANGES

### Summary
JWT validation accepts tokens without enforcing issuer or audience, which weakens auth boundary checks.

### Issues

**[HIGH] AUTH-001** -- Line 42

> `payload = jwt.decode(token, key, algorithms=["HS256"])`

The token decode verifies the signature, but it does not restrict issuer or audience. A valid token minted for another service could be accepted here.

**Fix**:

```python
payload = jwt.decode(
    token,
    key,
    algorithms=["HS256"],
    audience=settings.jwt_audience,
    issuer=settings.jwt_issuer,
)
```

## Overall

| Metric | Value |
|--------|-------|
| Files Reviewed | 1 |
| Total Issues | 1 |
| Critical / High / Medium / Low | 0 / 1 / 0 / 0 |
| Standards Source | `.ai-rigor/standards.md` |
| **Recommendation** | **REQUEST_CHANGES** |
