"""Integration tests — full skill pipeline with mocked LLM."""

import json
import pytest

from skills.code_review.python.skill import PythonCodeReviewSkill
from tests.conftest import MockLLMProvider, SAMPLE_REVIEW_JSON, SAMPLE_DIFF


class TestSkillIntegration:
    def _make_skill(self, response: str) -> PythonCodeReviewSkill:
        """Create a skill with a mock LLM provider."""
        from skills.code_review.python.llm_provider import LLMConfig
        config = LLMConfig(provider="openai", api_key="test-key", model="test")
        skill = PythonCodeReviewSkill(llm_config=config)
        # Replace the real provider with our mock
        skill.provider = MockLLMProvider(response)
        return skill

    def test_full_pipeline_returns_valid_result(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        result = skill.review(
            diff=SAMPLE_DIFF,
            pr_description="Add user creation endpoint",
        )
        assert result.file == "app/routers/user.py"
        assert result.recommendation == "APPROVE_WITH_COMMENTS"
        assert len(result.issues) == 1
        assert result.issues[0].id == "TYPE-001"
        assert 0 <= result.risk_score <= 100
        assert 0 <= result.security_score <= 100

    def test_pipeline_with_all_intent_fields(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        result = skill.review(
            diff=SAMPLE_DIFF,
            pr_description="Add user creation endpoint",
            ticket_id="PROJ-123",
            spec_summary="Users can create accounts",
        )
        # Verify intent was passed through to the LLM
        provider = skill.provider
        assert "PROJ-123" in provider.last_user_prompt
        assert "Users can create accounts" in provider.last_user_prompt
        assert result.file == "app/routers/user.py"

    def test_pipeline_with_no_issues(self):
        clean_review = {
            "file": "app/main.py",
            "risk_score": 0,
            "security_score": 100,
            "summary": "No issues found.",
            "issues": [],
            "summary_by_type": {},
            "recommendation": "APPROVE"
        }
        skill = self._make_skill(json.dumps(clean_review))
        result = skill.review(diff=SAMPLE_DIFF)
        assert result.recommendation == "APPROVE"
        assert len(result.issues) == 0

    def test_invalid_json_raises_value_error(self):
        skill = self._make_skill("This is not JSON at all")
        with pytest.raises(ValueError, match="LLM returned invalid JSON"):
            skill.review(diff=SAMPLE_DIFF)

    def test_invalid_schema_raises_value_error(self):
        bad_schema = json.dumps({"file": "test.py"})  # missing required fields
        skill = self._make_skill(bad_schema)
        with pytest.raises(ValueError, match="Response validation failed"):
            skill.review(diff=SAMPLE_DIFF)

    def test_markdown_wrapped_json_is_handled(self):
        wrapped = "```json\n" + json.dumps(SAMPLE_REVIEW_JSON) + "\n```"
        skill = self._make_skill(wrapped)
        result = skill.review(diff=SAMPLE_DIFF)
        assert result.file == "app/routers/user.py"

    def test_extractor_output_reaches_prompt(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        skill.review(diff=SAMPLE_DIFF)
        provider = skill.provider
        # Extractor should have put file info into the prompt
        assert "app/routers/user.py" in provider.last_user_prompt
        assert "FUNCTION SIGNATURES:" in provider.last_user_prompt
        assert "IMPORTS:" in provider.last_user_prompt
