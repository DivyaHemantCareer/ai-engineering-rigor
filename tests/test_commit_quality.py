"""Tests for the commit quality skill."""

import json
import pytest

from skills.commit_quality.extractors.commit_context import (
    CommitContextExtractor,
)
from skills.commit_quality.models.commit_result import CommitQualityResult
from skills.commit_quality.skill import CommitQualitySkill
from skills.code_review.python.llm_provider import LLMConfig
from tests.conftest import MockLLMProvider


class TestCommitContextExtractor:
    def test_parses_conventional_commit(self):
        ext = CommitContextExtractor()
        ctx = ext.extract(diff="", commit_message="feat(auth): add JWT validation")
        assert ctx.is_conventional is True
        assert ctx.commit_type == "feat"
        assert ctx.scope == "auth"
        assert ctx.description == "add JWT validation"

    def test_parses_breaking_change(self):
        ext = CommitContextExtractor()
        ctx = ext.extract(diff="", commit_message="fix(api)!: remove deprecated endpoint")
        assert ctx.is_conventional is True
        assert ctx.is_breaking is True

    def test_detects_non_conventional(self):
        ext = CommitContextExtractor()
        ctx = ext.extract(diff="", commit_message="Updated the auth system")
        assert ctx.is_conventional is False
        assert ctx.commit_type is None

    def test_extracts_changed_files(self):
        diff = "+++ b/app/auth.py\n+++ b/app/models.py\n"
        ext = CommitContextExtractor()
        ctx = ext.extract(diff=diff, commit_message="fix(auth): fix login")
        assert "app/auth.py" in ctx.changed_files
        assert "app/models.py" in ctx.changed_files

    def test_payload_shows_format(self):
        ext = CommitContextExtractor()
        ctx = ext.extract(diff="", commit_message="feat(auth): add login")
        payload = ext.to_prompt_payload(ctx)
        assert "TYPE: feat" in payload
        assert "SCOPE: auth" in payload

    def test_payload_shows_non_conventional(self):
        ext = CommitContextExtractor()
        ctx = ext.extract(diff="", commit_message="just some changes")
        payload = ext.to_prompt_payload(ctx)
        assert "Non-conventional" in payload


class TestCommitQualitySkill:
    def _make_skill(self, response: str) -> CommitQualitySkill:
        config = LLMConfig(provider="openai", api_key="test", model="test")
        skill = CommitQualitySkill(llm_config=config)
        skill.provider = MockLLMProvider(response)
        return skill

    def test_passing_commit_no_llm_call(self):
        llm_response = json.dumps({
            "raw_message": "", "format_valid": True,
            "scope_matches_files": True, "issues": [],
            "suggested_rewrite": None, "score": 100,
        })
        skill = self._make_skill(llm_response)
        result = skill.analyze(
            commit_message="feat(auth): add JWT validation",
            diff="+++ b/app/auth.py\n",
        )
        assert result.format_valid is True
        assert result.score == 100
        # No LLM call needed for passing commit
        assert skill.provider.call_count == 0

    def test_failing_commit_calls_llm(self):
        llm_response = json.dumps({
            "raw_message": "bad msg", "format_valid": False,
            "scope_matches_files": True, "issues": [],
            "suggested_rewrite": "fix: improve message format",
            "score": 50,
        })
        skill = self._make_skill(llm_response)
        result = skill.analyze(commit_message="bad msg")
        assert result.format_valid is False
        assert result.suggested_rewrite == "fix: improve message format"
        assert skill.provider.call_count == 1

    def test_scope_mismatch_detected(self):
        llm_response = json.dumps({
            "raw_message": "", "format_valid": True,
            "scope_matches_files": False, "issues": [],
            "suggested_rewrite": "feat(models): add user model",
            "score": 75,
        })
        skill = self._make_skill(llm_response)
        result = skill.analyze(
            commit_message="feat(auth): add user model",
            diff="+++ b/app/models/user.py\n",
        )
        assert result.scope_matches_files is False
        assert any("scope" in i.rule for i in result.issues)
