"""Tests for the dependency audit skill."""

import json
import pytest

from skills.dependency_audit.python.extractors.dep_context import (
    DepContextExtractor,
)
from skills.dependency_audit.python.models.audit_result import DependencyAuditResult
from skills.dependency_audit.python.skill import PythonDependencyAuditSkill
from skills.code_review.python.llm_provider import LLMConfig
from tests.conftest import MockLLMProvider


REQ_DIFF = """\
diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,3 +1,5 @@
 flask>=2.0
-requests>=2.28.0
+requests>=2.31.0
+boto3
+pyjwt>=2.0.0
"""


class TestDepContextExtractor:
    def test_extracts_added_deps(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        added_names = [d.name for d in ctx.added]
        assert "boto3" in added_names
        assert "pyjwt" in added_names

    def test_extracts_removed_deps(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        removed_names = [d.name for d in ctx.removed]
        assert "requests" in removed_names

    def test_version_spec_captured(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        pyjwt = next(d for d in ctx.added if d.name == "pyjwt")
        assert "2.0.0" in pyjwt.version_spec

    def test_unpinned_detected(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        boto3 = next(d for d in ctx.added if d.name == "boto3")
        assert boto3.version_spec == ""

    def test_filename_extracted(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        assert ctx.source_file == "requirements.txt"

    def test_payload_format(self):
        ext = DepContextExtractor()
        ctx = ext.extract(REQ_DIFF)
        payload = ext.to_prompt_payload(ctx)
        assert "ADDED DEPENDENCIES:" in payload
        assert "REMOVED DEPENDENCIES:" in payload
        assert "boto3" in payload


class TestDepAuditSkillIntegration:
    def test_full_pipeline(self):
        mock_response = json.dumps({
            "source_file": "requirements.txt",
            "new_deps": ["boto3", "pyjwt"],
            "removed_deps": ["requests"],
            "risk_flags": [
                {
                    "dependency": "boto3",
                    "risk_level": "MEDIUM",
                    "reason": "No version pin — may introduce breaking changes",
                    "recommendation": "Pin to a specific version: boto3>=1.28.0",
                }
            ],
            "summary": "1 medium risk: unpinned boto3 dependency",
            "overall_risk": "MEDIUM",
        })
        config = LLMConfig(provider="openai", api_key="test", model="test")
        skill = PythonDependencyAuditSkill(llm_config=config)
        skill.provider = MockLLMProvider(mock_response)

        result = skill.audit(diff=REQ_DIFF)
        assert "boto3" in result.new_deps
        assert len(result.risk_flags) == 1
        assert result.overall_risk == "MEDIUM"
