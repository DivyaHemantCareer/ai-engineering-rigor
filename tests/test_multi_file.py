"""Tests for multi-file diff support."""

import json
import pytest

from skills.code_review.python.skill import PythonCodeReviewSkill
from skills.code_review.python.llm_provider import LLMConfig
from skills.code_review.python.extractors.code_context import CodeContextExtractor
from tests.conftest import MockLLMProvider, SAMPLE_REVIEW_JSON, SAMPLE_MULTI_FILE_DIFF


class TestExtractAll:
    def test_splits_multi_file_diff(self):
        extractor = CodeContextExtractor()
        contexts = extractor.extract_all(SAMPLE_MULTI_FILE_DIFF)
        assert len(contexts) == 3

    def test_extracts_correct_filenames(self):
        extractor = CodeContextExtractor()
        contexts = extractor.extract_all(SAMPLE_MULTI_FILE_DIFF)
        filenames = [c.filename for c in contexts]
        assert "app/routers/user.py" in filenames
        assert "app/models/user.py" in filenames
        assert "app/config.py" in filenames

    def test_single_file_diff_returns_one_context(self, sample_diff):
        extractor = CodeContextExtractor()
        contexts = extractor.extract_all(sample_diff)
        assert len(contexts) == 1


class TestReviewMulti:
    def _make_skill(self, response: str) -> PythonCodeReviewSkill:
        config = LLMConfig(provider="openai", api_key="test-key", model="test")
        skill = PythonCodeReviewSkill(llm_config=config)
        skill.provider = MockLLMProvider(response)
        return skill

    def test_three_files_produce_three_results(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        result = skill.review_multi(diff=SAMPLE_MULTI_FILE_DIFF)
        assert result.files_reviewed == 3
        assert len(result.results) == 3

    def test_total_issues_aggregated(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        result = skill.review_multi(diff=SAMPLE_MULTI_FILE_DIFF)
        # Each file review has 1 issue, 3 files = 3 total
        assert result.total_issues == 3

    def test_overall_recommendation_is_worst(self):
        skill = self._make_skill(json.dumps(SAMPLE_REVIEW_JSON))
        result = skill.review_multi(diff=SAMPLE_MULTI_FILE_DIFF)
        # SAMPLE_REVIEW_JSON has APPROVE_WITH_COMMENTS, so worst of 3 identical = same
        assert result.overall_recommendation == "APPROVE_WITH_COMMENTS"

    def test_block_merge_propagates(self):
        blocking_review = dict(SAMPLE_REVIEW_JSON)
        blocking_review["recommendation"] = "BLOCK_MERGE"
        blocking_review["issues"] = [{
            "id": "SEC-001",
            "type": "SECURITY",
            "severity": "CRITICAL",
            "line": 1,
            "code": "secret = 'abc'",
            "message": "Hardcoded secret",
            "suggestion": "Use env var"
        }]
        skill = self._make_skill(json.dumps(blocking_review))
        result = skill.review_multi(diff=SAMPLE_MULTI_FILE_DIFF)
        assert result.overall_recommendation == "BLOCK_MERGE"
