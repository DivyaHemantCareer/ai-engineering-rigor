import json
import logging
from typing import Optional
from pydantic import BaseModel

from skills.base import Skill
from .extractors.code_context import CodeContextExtractor
from .layers.intent_layer import IntentContext
from .layers.standards_layer import StandardsContext
from .llm_provider import LLMConfig, create_provider
from .models.review_result import CodeReviewResult, MultiFileReviewResult
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class PythonCodeReviewSkill(Skill):
    """
    AI Engineering Rigor — Python Code Review Skill

    A 3-layer LLM-first code review skill:
      Layer 1: Code context extractor (what changed)
      Layer 2: Intent layer (why it changed)
      Layer 3: Standards layer (how it should be written)

    Model-agnostic — user brings their own LLM via LLMConfig.
    Designed to be used standalone or composed into agents.

    Usage:
        skill = PythonCodeReviewSkill(llm_config=LLMConfig.from_env())
        result = skill.review(
            diff=git_diff,
            pr_description="Add user auth endpoint",
            standards_file="standards.md"   # optional
        )
    """

    __skill_name__ = "code-review-python"

    @property
    def name(self) -> str:
        return "code-review-python"

    @property
    def description(self) -> str:
        return "LLM-powered Python/FastAPI code review with structured output"

    def run(self, **kwargs) -> BaseModel:
        """Execute the skill via the generic Skill interface."""
        diff = kwargs.pop("diff")
        return self.review(diff=diff, **kwargs)

    def __init__(self, llm_config: LLMConfig):
        self.extractor = CodeContextExtractor()
        self.provider = create_provider(llm_config)

    def review(
        self,
        diff: str,
        pr_description: Optional[str] = None,
        spec_summary: Optional[str] = None,
        ticket_id: Optional[str] = None,
        standards_file: Optional[str] = None,
        custom_standards: Optional[str] = None,
    ) -> CodeReviewResult:
        """
        Perform a code review on a single-file git diff.

        Args:
            diff:             Git diff output (required)
            pr_description:   PR description — intent of the change
            spec_summary:     Brief spec or acceptance criteria
            ticket_id:        Ticket/issue reference
            standards_file:   Path to team standards markdown file
            custom_standards: Inline standards string (alternative to file)

        Returns:
            CodeReviewResult — validated Pydantic model
        """

        # Layer 1 — Extract minimal code context
        code_context = self.extractor.extract(diff)
        code_payload = self.extractor.to_prompt_payload(code_context)

        # Layer 2 — Build intent context
        intent = IntentContext(
            pr_description=pr_description,
            spec_summary=spec_summary,
            ticket_id=ticket_id
        )
        intent_payload = intent.to_prompt_payload()

        # Layer 3 — Load standards (custom or default)
        standards = StandardsContext(custom_standards=custom_standards)
        if standards_file:
            standards.load_from_file(standards_file)
        standards_payload = standards.to_prompt_payload()

        # Assemble prompt
        user_prompt = build_user_prompt(
            code_payload=code_payload,
            intent_payload=intent_payload,
            standards_payload=standards_payload
        )

        # Call LLM with retry on parse failure
        return self._parse_response_with_retry(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    def review_multi(
        self,
        diff: str,
        pr_description: Optional[str] = None,
        spec_summary: Optional[str] = None,
        ticket_id: Optional[str] = None,
        standards_file: Optional[str] = None,
        custom_standards: Optional[str] = None,
    ) -> MultiFileReviewResult:
        """
        Review a multi-file diff. Splits on 'diff --git' boundaries
        and reviews each file individually.

        Returns:
            MultiFileReviewResult — aggregated across all files
        """
        contexts = self.extractor.extract_all(diff)
        results = []

        # Build shared intent and standards once
        intent = IntentContext(
            pr_description=pr_description,
            spec_summary=spec_summary,
            ticket_id=ticket_id
        )
        intent_payload = intent.to_prompt_payload()

        standards = StandardsContext(custom_standards=custom_standards)
        if standards_file:
            standards.load_from_file(standards_file)
        standards_payload = standards.to_prompt_payload()

        for ctx in contexts:
            code_payload = self.extractor.to_prompt_payload(ctx)
            user_prompt = build_user_prompt(
                code_payload=code_payload,
                intent_payload=intent_payload,
                standards_payload=standards_payload
            )
            result = self._parse_response_with_retry(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            results.append(result)

        return MultiFileReviewResult.from_results(results)

    def _parse_response_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> CodeReviewResult:
        """
        Call LLM and parse response. On parse failure, retry once
        with the error message asking the LLM to fix its JSON.
        """
        raw_response = self.provider.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        try:
            return self._parse_response(raw_response)
        except ValueError as first_error:
            logger.warning("First parse attempt failed: %s. Retrying.", first_error)
            retry_prompt = (
                f"Your previous response was not valid JSON. "
                f"Error: {first_error}\n\n"
                f"Please return ONLY valid JSON matching the required schema. "
                f"No markdown fences, no preamble."
            )
            raw_retry = self.provider.complete(
                system_prompt=system_prompt,
                user_prompt=retry_prompt,
            )
            return self._parse_response(raw_retry)

    def _parse_response(self, raw: str) -> CodeReviewResult:
        """
        Parse LLM response into validated Pydantic model.
        Strips markdown fences if LLM wraps response in ```json blocks.
        """
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return CodeReviewResult(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}\nRaw response:\n{raw}")
        except Exception as e:
            raise ValueError(f"Response validation failed: {e}\nRaw response:\n{raw}")
