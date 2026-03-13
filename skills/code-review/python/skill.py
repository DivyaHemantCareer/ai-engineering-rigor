import json
from typing import Optional
from .extractors.code_context import CodeContextExtractor
from .layers.intent_layer import IntentContext
from .layers.standards_layer import StandardsContext
from .llm_provider import LLMConfig, create_provider
from .models.review_result import CodeReviewResult
from .prompts import SYSTEM_PROMPT, build_user_prompt


class PythonCodeReviewSkill:
    """
    AI Engineering Rigor — Python Code Review Skill

    A 3-layer LLM-first code review skill:
      Layer 1: Code context extractor (what changed)
      Layer 2: Intent layer (why it changed)
      Layer 3: Standards layer (how it should be written)

    Model-agnostic — user brings their own LLM via LLMConfig.
    Designed to be used standalone (CLI) or composed into agents.

    Usage:
        skill = PythonCodeReviewSkill(llm_config=LLMConfig.from_env())
        result = skill.review(
            diff=git_diff,
            pr_description="Add user auth endpoint",
            standards_file="standards.md"   # optional
        )
    """

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
        Perform a code review on a git diff.

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

        # Call LLM
        raw_response = self.provider.complete(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        # Parse and validate response
        return self._parse_response(raw_response)

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
