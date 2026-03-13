"""Tests for LLM error recovery (retry on parse failure)."""

import json
import pytest

from skills.code_review.python.skill import PythonCodeReviewSkill
from skills.code_review.python.llm_provider import LLMConfig
from tests.conftest import SequentialMockLLMProvider, SAMPLE_REVIEW_JSON, SAMPLE_DIFF


class TestRetry:
    def _make_skill(self, responses: list[str]) -> PythonCodeReviewSkill:
        config = LLMConfig(provider="openai", api_key="test-key", model="test")
        skill = PythonCodeReviewSkill(llm_config=config)
        skill.provider = SequentialMockLLMProvider(responses)
        return skill

    def test_garbage_then_valid_json_succeeds(self):
        skill = self._make_skill([
            "Sorry, here is my analysis of the code...",
            json.dumps(SAMPLE_REVIEW_JSON),
        ])
        result = skill.review(diff=SAMPLE_DIFF)
        assert result.file == "app/routers/user.py"
        assert skill.provider.call_count == 2

    def test_valid_json_on_first_try_no_retry(self):
        skill = self._make_skill([json.dumps(SAMPLE_REVIEW_JSON)])
        result = skill.review(diff=SAMPLE_DIFF)
        assert result.file == "app/routers/user.py"
        assert skill.provider.call_count == 1

    def test_both_attempts_fail_raises(self):
        skill = self._make_skill([
            "not json",
            "still not json",
        ])
        with pytest.raises(ValueError, match="LLM returned invalid JSON"):
            skill.review(diff=SAMPLE_DIFF)
        assert skill.provider.call_count == 2
