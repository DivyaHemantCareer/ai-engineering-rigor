"""Tests for skill registry and plugin architecture."""

import pytest

from skills.registry import SkillRegistry, registry
from skills.base import Skill
from skills.extractors.base import CodeExtractor
from skills.code_review.python.skill import PythonCodeReviewSkill
from skills.code_review.python.extractors.code_context import CodeContextExtractor


class TestSkillRegistry:
    def test_get_code_review_python(self):
        cls = registry.get("code-review-python")
        assert cls is PythonCodeReviewSkill

    def test_list_all_includes_all_skills(self):
        names = registry.list_all()
        assert "code-review-python" in names
        assert "test-coverage-python" in names
        assert "commit-quality" in names
        assert "dependency-audit-python" in names

    def test_get_unknown_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown skill"):
            registry.get("nonexistent-skill")

    def test_register_custom_skill(self):
        reg = SkillRegistry()

        class FakeSkill(Skill):
            __skill_name__ = "fake-skill"

            @property
            def name(self):
                return "fake-skill"

            @property
            def description(self):
                return "A fake skill for testing"

            def run(self, **kwargs):
                pass

        reg.register(FakeSkill)
        assert reg.get("fake-skill") is FakeSkill
        assert "fake-skill" in reg.list_all()


class TestSkillBaseClass:
    def test_python_code_review_is_skill(self):
        assert issubclass(PythonCodeReviewSkill, Skill)

    def test_skill_name_property(self):
        from skills.code_review.python.llm_provider import LLMConfig
        config = LLMConfig(provider="openai", api_key="test", model="test")
        skill = PythonCodeReviewSkill(llm_config=config)
        assert skill.name == "code-review-python"
        assert skill.description != ""


class TestCodeExtractorBase:
    def test_code_context_extractor_is_code_extractor(self):
        assert issubclass(CodeContextExtractor, CodeExtractor)

    def test_language_property(self):
        extractor = CodeContextExtractor()
        assert extractor.language == "python"
