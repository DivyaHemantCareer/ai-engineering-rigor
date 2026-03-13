"""Extractor that parses conventional commit messages and changed file paths."""

import re
from dataclasses import dataclass, field
from typing import List, Optional

from skills.extractors.base import CodeExtractor

# Conventional commit pattern: type(scope): description
CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<description>.+)$"
)


@dataclass
class CommitContext:
    """Parsed commit message and associated file context."""
    raw_message: str
    commit_type: Optional[str] = None
    scope: Optional[str] = None
    description: Optional[str] = None
    is_breaking: bool = False
    is_conventional: bool = False
    changed_files: List[str] = field(default_factory=list)
    body: Optional[str] = None


class CommitContextExtractor(CodeExtractor):
    """
    Parses commit messages using conventional commit format
    and extracts changed file paths from diffs.
    """

    @property
    def language(self) -> str:
        return "any"

    def extract(self, diff: str, commit_message: str = "") -> CommitContext:
        """Extract commit context from message and diff."""
        context = self._parse_message(commit_message)
        context.changed_files = self._extract_changed_files(diff)
        return context

    def to_prompt_payload(self, context) -> str:
        parts = [f"COMMIT MESSAGE: {context.raw_message}"]

        if context.is_conventional:
            parts.append(f"TYPE: {context.commit_type}")
            if context.scope:
                parts.append(f"SCOPE: {context.scope}")
            parts.append(f"DESCRIPTION: {context.description}")
            if context.is_breaking:
                parts.append("BREAKING CHANGE: Yes")
        else:
            parts.append("FORMAT: Non-conventional (does not follow type(scope): description)")

        if context.changed_files:
            files = "\n".join(f"- {f}" for f in context.changed_files)
            parts.append(f"CHANGED FILES:\n{files}")

        if context.body:
            parts.append(f"BODY:\n{context.body}")

        return "\n\n".join(parts)

    def _parse_message(self, message: str) -> CommitContext:
        lines = message.strip().splitlines() if message.strip() else [""]
        subject = lines[0].strip()
        body = "\n".join(lines[2:]).strip() if len(lines) > 2 else None

        match = CONVENTIONAL_COMMIT_RE.match(subject)
        if match:
            return CommitContext(
                raw_message=message,
                commit_type=match.group("type"),
                scope=match.group("scope"),
                description=match.group("description"),
                is_breaking=match.group("breaking") is not None,
                is_conventional=True,
                body=body,
            )

        return CommitContext(
            raw_message=message,
            is_conventional=False,
            body=body,
        )

    def _extract_changed_files(self, diff: str) -> List[str]:
        files = re.findall(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
        return files
