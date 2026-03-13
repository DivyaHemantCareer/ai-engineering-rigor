"""Tests for the test coverage analysis skill."""

import json
import pytest

from skills.test_coverage.python.extractors.coverage_context import (
    CoverageContextExtractor,
)
from skills.test_coverage.python.models.coverage_result import CoverageAnalysisResult
from skills.test_coverage.python.skill import PythonTestCoverageSkill
from skills.code_review.python.llm_provider import LLMConfig
from tests.conftest import MockLLMProvider


FUNCTION_DIFF = """\
diff --git a/app/service.py b/app/service.py
--- a/app/service.py
+++ b/app/service.py
@@ -1,3 +1,12 @@
+from typing import Optional
+
+def create_user(username: str, email: str) -> dict:
+    return {"username": username, "email": email}
+
+async def get_user(user_id: int) -> Optional[dict]:
+    return None
+
+def __repr__(self):
+    return "Service"
"""


class TestCoverageContextExtractor:
    def test_extracts_functions(self):
        extractor = CoverageContextExtractor()
        ctx = extractor.extract(FUNCTION_DIFF)
        names = [f.name for f in ctx.changed_functions]
        assert "create_user" in names
        assert "get_user" in names

    def test_skips_dunder_methods(self):
        extractor = CoverageContextExtractor()
        ctx = extractor.extract(FUNCTION_DIFF)
        names = [f.name for f in ctx.changed_functions]
        assert "__repr__" not in names

    def test_maps_to_test_file(self):
        extractor = CoverageContextExtractor()
        ctx = extractor.extract(FUNCTION_DIFF)
        assert ctx.expected_test_file == "tests/test_service.py"

    def test_prompt_payload_contains_functions(self):
        extractor = CoverageContextExtractor()
        ctx = extractor.extract(FUNCTION_DIFF)
        payload = extractor.to_prompt_payload(ctx)
        assert "create_user" in payload
        assert "get_user" in payload
        assert "SOURCE FILE:" in payload


class TestCoverageSkillIntegration:
    def test_full_pipeline(self):
        mock_response = json.dumps({
            "source_file": "app/service.py",
            "expected_test_file": "tests/test_service.py",
            "total_functions": 2,
            "uncovered_functions": ["create_user", "get_user"],
            "suggested_tests": [
                {
                    "function_name": "create_user",
                    "test_name": "test_create_user_returns_dict",
                    "description": "Verify create_user returns a dict with username and email",
                }
            ],
            "coverage_gap_summary": "Both new functions lack test coverage",
        })
        config = LLMConfig(provider="openai", api_key="test", model="test")
        skill = PythonTestCoverageSkill(llm_config=config)
        skill.provider = MockLLMProvider(mock_response)

        result = skill.analyze(diff=FUNCTION_DIFF)
        assert result.total_functions == 2
        assert "create_user" in result.uncovered_functions
        assert len(result.suggested_tests) == 1
