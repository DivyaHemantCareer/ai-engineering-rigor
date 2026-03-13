"""Commit message quality analysis skill."""

from typing import Optional
from pydantic import BaseModel

from skills.base import Skill
from skills.shared.llm_utils import parse_json_response
from skills.code_review.python.llm_provider import LLMConfig, create_provider
from .extractors.commit_context import CommitContextExtractor
from .models.commit_result import CommitQualityResult, CommitIssue
from .prompts import SYSTEM_PROMPT, build_user_prompt


class CommitQualitySkill(Skill):
    """
    Analyzes commit messages for quality and convention compliance.
    Uses regex for format validation (no LLM for passing commits).
    LLM only used for rewrite suggestions on failing commits.
    """

    __skill_name__ = "commit-quality"

    @property
    def name(self) -> str:
        return "commit-quality"

    @property
    def description(self) -> str:
        return "Analyze commit message quality and conventional commit compliance"

    def run(self, **kwargs) -> BaseModel:
        diff = kwargs.pop("diff", "")
        commit_message = kwargs.pop("commit_message", "")
        return self.analyze(commit_message=commit_message, diff=diff)

    def __init__(self, llm_config: LLMConfig):
        self.extractor = CommitContextExtractor()
        self.provider = create_provider(llm_config)

    def analyze(
        self,
        commit_message: str,
        diff: str = "",
    ) -> CommitQualityResult:
        """Analyze a commit message for quality."""
        context = self.extractor.extract(diff=diff, commit_message=commit_message)

        # Fast path: regex-based checks (no LLM needed for passing commits)
        issues = []
        format_valid = context.is_conventional
        scope_matches = True

        if not format_valid:
            issues.append(CommitIssue(
                rule="conventional-format",
                message="Commit message does not follow conventional commit format",
                suggestion="Use: type(scope): description",
            ))

        if context.scope and context.changed_files:
            scope_matches = self._scope_matches_files(
                context.scope, context.changed_files
            )
            if not scope_matches:
                issues.append(CommitIssue(
                    rule="scope-file-mismatch",
                    message=f"Scope '{context.scope}' does not match changed files",
                    suggestion=f"Changed files suggest scope related to: {', '.join(context.changed_files[:3])}",
                ))

        if context.description and len(context.description) > 72:
            issues.append(CommitIssue(
                rule="subject-length",
                message="Subject line exceeds 72 characters",
                suggestion="Keep the subject line under 72 characters",
            ))

        # If issues found, ask LLM for a rewrite suggestion
        suggested_rewrite = None
        if issues:
            payload = self.extractor.to_prompt_payload(context)
            user_prompt = build_user_prompt(payload)
            raw_response = self.provider.complete(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )
            llm_result = parse_json_response(raw_response, CommitQualityResult)
            suggested_rewrite = llm_result.suggested_rewrite

        score = 100 - (len(issues) * 25)
        score = max(0, min(100, score))

        return CommitQualityResult(
            raw_message=commit_message,
            format_valid=format_valid,
            scope_matches_files=scope_matches,
            issues=issues,
            suggested_rewrite=suggested_rewrite,
            score=score,
        )

    def _scope_matches_files(self, scope: str, files: list[str]) -> bool:
        """Check if the commit scope loosely matches the changed file paths."""
        scope_lower = scope.lower()
        return any(scope_lower in f.lower() for f in files)
