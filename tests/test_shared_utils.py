"""Tests for shared utility modules."""

import pytest

from skills.shared.token_utils import estimate_tokens, truncate_to_budget
from skills.shared.diff_utils import split_diff_by_file, is_python_file
from skills.shared.llm_utils import parse_json_response
from skills.code_review.python.models.review_result import CodeReviewResult


class TestTokenUtils:
    def test_estimate_tokens(self):
        text = "hello world foo bar"
        tokens = estimate_tokens(text)
        assert tokens == int(4 * 1.3)

    def test_estimate_tokens_empty(self):
        assert estimate_tokens("") == 0

    def test_truncate_within_budget(self):
        text = "short text"
        assert truncate_to_budget(text, 100) == text

    def test_truncate_over_budget(self):
        text = " ".join(["word"] * 100)
        result = truncate_to_budget(text, 10)
        assert "[...truncated" in result
        assert len(result.split()) < 100


class TestDiffUtils:
    def test_split_diff_by_file(self):
        diff = (
            "diff --git a/foo.py b/foo.py\n+hello\n"
            "diff --git a/bar.py b/bar.py\n+world\n"
        )
        segments = split_diff_by_file(diff)
        assert len(segments) == 2

    def test_split_single_file(self):
        diff = "diff --git a/foo.py b/foo.py\n+hello\n"
        segments = split_diff_by_file(diff)
        assert len(segments) == 1

    def test_is_python_file(self):
        assert is_python_file("foo.py") is True
        assert is_python_file("foo.js") is False
        assert is_python_file("test_foo.py") is True


class TestLLMUtils:
    def test_parse_valid_json(self):
        raw = '{"file":"x.py","risk_score":10,"security_score":90,"summary":"ok","issues":[],"summary_by_type":{},"recommendation":"APPROVE"}'
        result = parse_json_response(raw, CodeReviewResult)
        assert result.file == "x.py"

    def test_parse_markdown_wrapped(self):
        raw = '```json\n{"file":"x.py","risk_score":10,"security_score":90,"summary":"ok","issues":[],"summary_by_type":{},"recommendation":"APPROVE"}\n```'
        result = parse_json_response(raw, CodeReviewResult)
        assert result.file == "x.py"

    def test_parse_invalid_json_raises(self):
        with pytest.raises(ValueError, match="invalid JSON"):
            parse_json_response("not json", CodeReviewResult)

    def test_parse_bad_schema_raises(self):
        with pytest.raises(ValueError, match="validation failed"):
            parse_json_response('{"file":"x.py"}', CodeReviewResult)
