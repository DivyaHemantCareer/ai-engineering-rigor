"""Python test coverage analysis skill."""

import json
from typing import Optional
from pydantic import BaseModel

from skills.base import Skill
from skills.shared.llm_utils import parse_json_response
from skills.code_review.python.llm_provider import LLMConfig, create_provider
from .extractors.coverage_context import CoverageContextExtractor
from .models.coverage_result import CoverageAnalysisResult
from .prompts import SYSTEM_PROMPT, build_user_prompt


class PythonTestCoverageSkill(Skill):
    """Analyzes changed functions and suggests missing test coverage."""

    __skill_name__ = "test-coverage-python"

    @property
    def name(self) -> str:
        return "test-coverage-python"

    @property
    def description(self) -> str:
        return "Analyze changed Python functions and suggest missing tests"

    def run(self, **kwargs) -> BaseModel:
        diff = kwargs.pop("diff")
        return self.analyze(diff=diff)

    def __init__(self, llm_config: LLMConfig):
        self.extractor = CoverageContextExtractor()
        self.provider = create_provider(llm_config)

    def analyze(self, diff: str) -> CoverageAnalysisResult:
        """Analyze a diff for test coverage gaps."""
        context = self.extractor.extract(diff)
        payload = self.extractor.to_prompt_payload(context)
        user_prompt = build_user_prompt(payload)

        raw_response = self.provider.complete(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return parse_json_response(raw_response, CoverageAnalysisResult)
