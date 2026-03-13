"""Shared test fixtures for ai-engineering-rigor."""

import json
import pytest

from skills.code_review.python.llm_provider import LLMProvider


SAMPLE_DIFF = """\
diff --git a/app/routers/user.py b/app/routers/user.py
--- a/app/routers/user.py
+++ b/app/routers/user.py
@@ -1,5 +1,12 @@
+from fastapi import APIRouter, Depends
+from pydantic import BaseModel
+from app.auth import get_current_user
+
+router = APIRouter()
+
+class UserCreate(BaseModel):
+    username: str
+    email: str
+
+@router.post("/users")
+async def create_user(user: UserCreate, current_user=Depends(get_current_user)):
+    return {"username": user.username}
"""

SAMPLE_MULTI_FILE_DIFF = """\
diff --git a/app/routers/user.py b/app/routers/user.py
--- a/app/routers/user.py
+++ b/app/routers/user.py
@@ -1,3 +1,8 @@
+from fastapi import APIRouter
+
+@router.post("/users")
+async def create_user(user: UserCreate):
+    return {"username": user.username}
diff --git a/app/models/user.py b/app/models/user.py
--- /dev/null
+++ b/app/models/user.py
@@ -0,0 +1,6 @@
+from pydantic import BaseModel
+
+class UserCreate(BaseModel):
+    username: str
+    email: str
diff --git a/app/config.py b/app/config.py
--- a/app/config.py
+++ b/app/config.py
@@ -1,2 +1,3 @@
+import os
+DATABASE_URL = os.getenv("DATABASE_URL")
"""

SAMPLE_REVIEW_JSON = {
    "file": "app/routers/user.py",
    "risk_score": 25,
    "security_score": 85,
    "summary": "Clean endpoint with minor type hint improvements needed.",
    "issues": [
        {
            "id": "TYPE-001",
            "type": "TYPE_HINT",
            "severity": "LOW",
            "line": 12,
            "code": "current_user=Depends(get_current_user)",
            "message": "Missing type annotation for current_user parameter",
            "suggestion": "Add type hint: current_user: User = Depends(get_current_user)"
        }
    ],
    "summary_by_type": {
        "SECURITY": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "FASTAPI": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "TYPE_HINT": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 1},
        "PERFORMANCE": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "QUALITY": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
    },
    "recommendation": "APPROVE_WITH_COMMENTS"
}


class MockLLMProvider(LLMProvider):
    """LLM provider that returns a fixed response. For testing only."""

    def __init__(self, response: str):
        self.response = response
        self.last_system_prompt = None
        self.last_user_prompt = None
        self.call_count = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        self.call_count += 1
        return self.response


class SequentialMockLLMProvider(LLMProvider):
    """LLM provider that returns different responses on successive calls."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        idx = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[idx]


@pytest.fixture
def sample_diff():
    return SAMPLE_DIFF


@pytest.fixture
def sample_multi_file_diff():
    return SAMPLE_MULTI_FILE_DIFF


@pytest.fixture
def sample_review_json():
    return SAMPLE_REVIEW_JSON


@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider(json.dumps(SAMPLE_REVIEW_JSON))
