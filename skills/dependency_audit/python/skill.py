"""Python dependency audit skill."""

from pydantic import BaseModel

from skills.base import Skill
from skills.shared.llm_utils import parse_json_response
from skills.code_review.python.llm_provider import LLMConfig, create_provider
from .extractors.dep_context import DepContextExtractor
from .models.audit_result import DependencyAuditResult
from .prompts import SYSTEM_PROMPT, build_user_prompt


class PythonDependencyAuditSkill(Skill):
    """Audits dependency changes in Python projects for risk."""

    __skill_name__ = "dependency-audit-python"

    @property
    def name(self) -> str:
        return "dependency-audit-python"

    @property
    def description(self) -> str:
        return "Audit Python dependency changes for security and supply chain risk"

    def run(self, **kwargs) -> BaseModel:
        diff = kwargs.pop("diff")
        return self.audit(diff=diff)

    def __init__(self, llm_config: LLMConfig):
        self.extractor = DepContextExtractor()
        self.provider = create_provider(llm_config)

    def audit(self, diff: str) -> DependencyAuditResult:
        """Audit a diff for dependency risk."""
        context = self.extractor.extract(diff)
        payload = self.extractor.to_prompt_payload(context)
        user_prompt = build_user_prompt(payload)

        raw_response = self.provider.complete(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return parse_json_response(raw_response, DependencyAuditResult)
