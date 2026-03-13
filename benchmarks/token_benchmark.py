#!/usr/bin/env python3
"""
Benchmark: Measures token reduction from context extraction.

Compares two approaches:
  1. NAIVE  -- Send the raw git diff straight to the LLM
  2. EXTRACTED -- Run extractors first, send only the minimal payload

Runs against real git diffs AND synthetic production-like diffs.
"""

import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.code_review.python.extractors.code_context import CodeContextExtractor
from skills.code_review.python.layers.intent_layer import IntentContext
from skills.code_review.python.layers.standards_layer import StandardsContext
from skills.code_review.python.prompts import SYSTEM_PROMPT, build_user_prompt
from skills.shared.token_utils import estimate_tokens


# ---------------------------------------------------------------------------
# Synthetic diffs that simulate real production scenarios
# ---------------------------------------------------------------------------

# Scenario A: Small change in a large file (most common PR pattern)
# 500 lines of existing code, only 3 lines changed
SYNTHETIC_LARGE_FILE_SMALL_CHANGE = """diff --git a/app/services/user_service.py b/app/services/user_service.py
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -1,6 +1,6 @@
 import logging
 from typing import Optional, List
-from datetime import datetime
+from datetime import datetime, timedelta
 from sqlalchemy.orm import Session
 from fastapi import Depends, HTTPException

@@ -15,6 +15,7 @@
 from app.models.user import User, UserCreate, UserUpdate, UserResponse
 from app.models.auth import TokenPayload
 from app.core.security import get_password_hash, verify_password, create_access_token
+from app.core.security import create_refresh_token
 from app.core.config import settings
 from app.db.session import get_db

@@ -45,200 +46,200 @@
 class UserService:
     \"\"\"Service layer for user management operations.\"\"\"

     def __init__(self, db: Session = Depends(get_db)):
         self.db = db
         self.logger = logging.getLogger(__name__)

     async def get_user(self, user_id: int) -> Optional[UserResponse]:
         \"\"\"Get a user by ID.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")
         return UserResponse.from_orm(user)

     async def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
         \"\"\"Get paginated list of users.\"\"\"
         users = self.db.query(User).offset(skip).limit(limit).all()
         return [UserResponse.from_orm(u) for u in users]

     async def create_user(self, user_data: UserCreate) -> UserResponse:
         \"\"\"Create a new user with hashed password.\"\"\"
         existing = self.db.query(User).filter(User.email == user_data.email).first()
         if existing:
             raise HTTPException(status_code=400, detail="Email already registered")

         db_user = User(
             email=user_data.email,
             username=user_data.username,
             hashed_password=get_password_hash(user_data.password),
             created_at=datetime.utcnow(),
         )
         self.db.add(db_user)
         self.db.commit()
         self.db.refresh(db_user)
         self.logger.info("Created user: %s", db_user.email)
         return UserResponse.from_orm(db_user)

     async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
         \"\"\"Update an existing user.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")

         for field, value in user_data.dict(exclude_unset=True).items():
             if field == "password":
                 setattr(user, "hashed_password", get_password_hash(value))
             else:
                 setattr(user, field, value)

         user.updated_at = datetime.utcnow()
         self.db.commit()
         self.db.refresh(user)
         return UserResponse.from_orm(user)

     async def delete_user(self, user_id: int) -> None:
         \"\"\"Soft delete a user.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")
         user.is_active = False
         user.deleted_at = datetime.utcnow()
         self.db.commit()

     async def authenticate(self, email: str, password: str) -> Optional[dict]:
         \"\"\"Authenticate user and return tokens.\"\"\"
         user = self.db.query(User).filter(User.email == email).first()
         if not user or not verify_password(password, user.hashed_password):
             return None
-        access_token = create_access_token(subject=str(user.id))
-        return {"access_token": access_token, "token_type": "bearer"}
+        access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=30))
+        refresh_token = create_refresh_token(subject=str(user.id), expires_delta=timedelta(days=7))
+        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

     async def search_users(self, query: str) -> List[UserResponse]:
         \"\"\"Search users by username or email.\"\"\"
         users = self.db.query(User).filter(
             (User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
         ).limit(50).all()
         return [UserResponse.from_orm(u) for u in users]

     async def get_user_stats(self, user_id: int) -> dict:
         \"\"\"Get user activity statistics.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")
         return {
             "total_posts": len(user.posts),
             "total_comments": len(user.comments),
             "member_since": user.created_at.isoformat(),
             "last_login": user.last_login.isoformat() if user.last_login else None,
         }

     async def update_last_login(self, user_id: int) -> None:
         \"\"\"Update user's last login timestamp.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if user:
             user.last_login = datetime.utcnow()
             self.db.commit()

     async def change_password(self, user_id: int, old_pass: str, new_pass: str) -> bool:
         \"\"\"Change user password after verifying old password.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user or not verify_password(old_pass, user.hashed_password):
             return False
         user.hashed_password = get_password_hash(new_pass)
         user.updated_at = datetime.utcnow()
         self.db.commit()
         return True

     async def verify_email(self, user_id: int, token: str) -> bool:
         \"\"\"Verify user email with token.\"\"\"
         user = self.db.query(User).filter(User.id == user_id).first()
         if not user:
             return False
         if user.email_verification_token != token:
             return False
         user.is_email_verified = True
         user.email_verification_token = None
         self.db.commit()
         return True

     async def request_password_reset(self, email: str) -> Optional[str]:
         \"\"\"Generate password reset token.\"\"\"
         user = self.db.query(User).filter(User.email == email).first()
         if not user:
             return None
         import secrets
         token = secrets.token_urlsafe(32)
         user.reset_token = token
         user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
         self.db.commit()
         return token

     async def reset_password(self, token: str, new_password: str) -> bool:
         \"\"\"Reset password using token.\"\"\"
         user = self.db.query(User).filter(User.reset_token == token).first()
         if not user or user.reset_token_expires < datetime.utcnow():
             return False
         user.hashed_password = get_password_hash(new_password)
         user.reset_token = None
         user.reset_token_expires = None
         user.updated_at = datetime.utcnow()
         self.db.commit()
         return True

     async def get_active_sessions(self, user_id: int) -> List[dict]:
         \"\"\"Get all active sessions for a user.\"\"\"
         sessions = self.db.query(Session).filter(
             Session.user_id == user_id,
             Session.is_active == True,
         ).all()
         return [{"id": s.id, "created_at": s.created_at, "ip": s.ip_address} for s in sessions]

     async def revoke_session(self, user_id: int, session_id: int) -> bool:
         \"\"\"Revoke a specific session.\"\"\"
         session = self.db.query(Session).filter(
             Session.id == session_id,
             Session.user_id == user_id,
         ).first()
         if not session:
             return False
         session.is_active = False
         self.db.commit()
         return True
"""

# Scenario B: Multi-file PR with mix of changes
SYNTHETIC_MULTI_FILE = """diff --git a/app/routers/auth.py b/app/routers/auth.py
--- a/app/routers/auth.py
+++ b/app/routers/auth.py
@@ -1,8 +1,10 @@
 from fastapi import APIRouter, Depends, HTTPException
 from pydantic import BaseModel
+from typing import Optional

 from app.services.user_service import UserService
 from app.core.security import get_current_user
+from app.core.rate_limit import rate_limit

 router = APIRouter(prefix="/auth", tags=["auth"])

@@ -15,8 +17,12 @@
     password: str

+class RefreshRequest(BaseModel):
+    refresh_token: str
+
 @router.post("/login")
+@rate_limit(max_calls=5, period=60)
 async def login(data: LoginRequest, service: UserService = Depends()):
     result = await service.authenticate(data.email, data.password)
     if not result:
         raise HTTPException(status_code=401, detail="Invalid credentials")
     return result

+@router.post("/refresh")
+async def refresh_token(data: RefreshRequest, service: UserService = Depends()):
+    result = await service.refresh_access_token(data.refresh_token)
+    if not result:
+        raise HTTPException(status_code=401, detail="Invalid refresh token")
+    return result
+
 @router.post("/register")
 async def register(data: RegisterRequest, service: UserService = Depends()):
     return await service.create_user(data)

@@ -30,6 +36,7 @@
 async def logout(current_user = Depends(get_current_user)):
     return {"message": "Logged out"}

 @router.get("/me")
+@rate_limit(max_calls=30, period=60)
 async def get_current_user_info(current_user = Depends(get_current_user)):
     return current_user

@@ -40,4 +47,4 @@
     return await service.get_users()

-# TODO: Add password reset endpoints
+# Password reset endpoints moved to /auth/password router
diff --git a/app/models/auth.py b/app/models/auth.py
--- a/app/models/auth.py
+++ b/app/models/auth.py
@@ -1,15 +1,25 @@
 from pydantic import BaseModel, Field
-from typing import Optional
+from typing import Optional, List
 from datetime import datetime

 class TokenPayload(BaseModel):
     sub: str
     exp: datetime
+    type: str = "access"

 class TokenResponse(BaseModel):
     access_token: str
+    refresh_token: Optional[str] = None
     token_type: str = "bearer"
+    expires_in: int = 1800

+class RefreshTokenPayload(BaseModel):
+    sub: str
+    exp: datetime
+    type: str = "refresh"
+    jti: str = Field(..., description="JWT ID for revocation")
+
 class UserClaims(BaseModel):
     user_id: int
     email: str
     roles: List[str] = []
+    permissions: List[str] = []
diff --git a/tests/test_auth.py b/tests/test_auth.py
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -1,5 +1,6 @@
 import pytest
 from unittest.mock import MagicMock, AsyncMock
+from datetime import timedelta
 from app.routers.auth import router

 class TestLogin:
@@ -10,3 +11,15 @@
     async def test_login_success(self, mock_service):
         mock_service.authenticate.return_value = {"access_token": "abc", "token_type": "bearer"}
         # ... test body

+class TestRefreshToken:
+    async def test_refresh_success(self, mock_service):
+        mock_service.refresh_access_token.return_value = {"access_token": "new", "token_type": "bearer"}
+        # ... test body
+
+    async def test_refresh_invalid_token(self, mock_service):
+        mock_service.refresh_access_token.return_value = None
+        # ... test body
+
+class TestRateLimit:
+    async def test_login_rate_limited(self):
+        # ... test body
"""

# Scenario C: Huge diff (refactoring, many files with context)
SYNTHETIC_HUGE_CONTEXT = (
    "diff --git a/app/huge_file.py b/app/huge_file.py\n"
    "--- a/app/huge_file.py\n"
    "+++ b/app/huge_file.py\n"
    "@@ -1,3 +1,4 @@\n"
    "+import os\n"
    " # " + "x" * 200 + "\n" +
    "\n".join(f" # unchanged line {i} with padding {'.' * 80}" for i in range(300)) +
    "\n@@ -500,3 +501,5 @@\n"
    "-    old_value = 42\n"
    "+    new_value = 99\n"
    "+    logger.info('Updated value')\n"
)


def get_diff(commit_range: str) -> str:
    """Get a real git diff."""
    result = subprocess.run(
        ["git", "diff", commit_range],
        capture_output=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return result.stdout.decode("utf-8", errors="replace")


def build_naive_prompt(diff: str, pr_description: str = "") -> str:
    """What most people do: dump the raw diff into the prompt with the same system prompt and standards."""
    # Fair comparison: both approaches use the same system prompt and standards overhead.
    # The only difference is HOW the code context is represented.
    intent = IntentContext(pr_description=pr_description)
    standards = StandardsContext()

    return build_user_prompt(
        code_payload=f"RAW DIFF:\n```\n{diff}\n```",
        intent_payload=intent.to_prompt_payload(),
        standards_payload=standards.to_prompt_payload(),
    )


def build_extracted_prompt(diff: str, pr_description: str = "") -> str:
    """Our approach: extract minimal context first, then build prompt."""
    extractor = CodeContextExtractor()
    contexts = extractor.extract_all(diff)

    code_payloads = []
    for ctx in contexts:
        code_payloads.append(extractor.to_prompt_payload(ctx))
    combined_code = "\n\n===\n\n".join(code_payloads)

    intent = IntentContext(pr_description=pr_description)
    intent_payload = intent.to_prompt_payload()

    standards = StandardsContext()
    standards_payload = standards.to_prompt_payload()

    user_prompt = build_user_prompt(
        code_payload=combined_code,
        intent_payload=intent_payload,
        standards_payload=standards_payload,
    )
    return user_prompt


def benchmark_diff(name: str, diff: str, pr_desc: str = ""):
    """Run both approaches on a diff and compare."""
    if not diff.strip():
        return None

    naive_prompt = build_naive_prompt(diff, pr_desc)
    extracted_prompt = build_extracted_prompt(diff, pr_desc)

    system_tokens = estimate_tokens(SYSTEM_PROMPT)
    naive_tokens = estimate_tokens(naive_prompt) + system_tokens
    extracted_tokens = estimate_tokens(extracted_prompt) + system_tokens

    diff_lines = len(diff.splitlines())
    reduction_pct = ((naive_tokens - extracted_tokens) / naive_tokens) * 100 if naive_tokens > 0 else 0

    extractor = CodeContextExtractor()
    contexts = extractor.extract_all(diff)
    files = len(contexts)

    return {
        "name": name,
        "diff_lines": diff_lines,
        "files": files,
        "naive_tokens": naive_tokens,
        "extracted_tokens": extracted_tokens,
        "reduction_pct": reduction_pct,
    }


def main():
    print("=" * 90)
    print("TOKEN REDUCTION BENCHMARK")
    print("Comparing: naive (raw diff in prompt) vs extracted (minimal context)")
    print("=" * 90)

    # -----------------------------------------------------------------------
    # Part 1: Real diffs from this repo
    # -----------------------------------------------------------------------
    print("\n--- REAL DIFFS (this repo's git history) ---\n")

    real_cases = [
        ("Single commit (tests)", "972f8af~1..972f8af", "Add unit tests"),
        ("Single commit (core skill)", "e808c60~1..e808c60", "LLM-first code review"),
        ("Full project (all commits)", "8741acc..972f8af", "Full project"),
        ("Working tree (uncommitted)", "HEAD", "Current changes"),
    ]

    real_results = []
    for name, commit_range, pr_desc in real_cases:
        diff = get_diff(commit_range)
        result = benchmark_diff(name, diff, pr_desc)
        if result:
            real_results.append(result)

    print_table(real_results)

    # -----------------------------------------------------------------------
    # Part 2: Synthetic production-like diffs
    # -----------------------------------------------------------------------
    print("\n--- SYNTHETIC DIFFS (production-like scenarios) ---\n")

    synth_cases = [
        ("Large file, 3-line change", SYNTHETIC_LARGE_FILE_SMALL_CHANGE, "Add refresh tokens"),
        ("Multi-file PR (3 files)", SYNTHETIC_MULTI_FILE, "Auth refresh + rate limiting"),
        ("Huge file (300 unchanged lines)", SYNTHETIC_HUGE_CONTEXT, "Config update"),
    ]

    synth_results = []
    for name, diff, pr_desc in synth_cases:
        result = benchmark_diff(name, diff, pr_desc)
        if result:
            synth_results.append(result)

    print_table(synth_results)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    all_results = real_results + synth_results
    total_naive = sum(r["naive_tokens"] for r in all_results)
    total_extracted = sum(r["extracted_tokens"] for r in all_results)
    total_saved = total_naive - total_extracted
    total_pct = (total_saved / total_naive * 100) if total_naive else 0

    print("=" * 90)
    print(f"OVERALL: {total_naive} naive tokens -> {total_extracted} extracted tokens")
    print(f"         {total_saved} tokens saved ({total_pct:.1f}% reduction)")
    print()
    print("WHY IT MATTERS:")
    print("  - Real repo diffs are mostly NEW code (additions) -- little to drop")
    print("  - Production diffs touch EXISTING files with lots of unchanged context")
    print("  - The extractor shines on large-file, small-change scenarios")
    print("  - At scale (10+ files, 1000+ lines), savings compound")
    print("=" * 90)


def print_table(results):
    if not results:
        print("  (no diffs found)")
        return

    header = f"{'Test Case':<40} {'Diff':>6} {'Files':>5} {'Naive':>7} {'Extracted':>10} {'Saved':>7} {'Reduction':>10}"
    print(header)
    print("-" * len(header))

    for r in results:
        saved = r["naive_tokens"] - r["extracted_tokens"]
        sign = "+" if saved < 0 else ""
        print(
            f"{r['name']:<40} {r['diff_lines']:>6} {r['files']:>5} "
            f"{r['naive_tokens']:>7} {r['extracted_tokens']:>10} {sign}{saved:>6} "
            f"{r['reduction_pct']:>9.1f}%"
        )


if __name__ == "__main__":
    main()
