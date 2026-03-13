"""Extractor that parses added/removed dependencies from diffs."""

import re
from dataclasses import dataclass, field
from typing import List

from skills.extractors.base import CodeExtractor


@dataclass
class DepChange:
    """A single dependency change."""
    name: str
    version_spec: str  # e.g. ">=1.0.0" or "" if unpinned
    action: str        # "added" or "removed"


@dataclass
class DepContext:
    """Extracted dependency changes from a diff."""
    source_file: str
    added: List[DepChange]
    removed: List[DepChange]
    raw_diff: str


class DepContextExtractor(CodeExtractor):
    """
    Parses added/removed dependencies from requirements.txt
    or pyproject.toml diffs. Tiny payload — just the dep lines.
    """

    @property
    def language(self) -> str:
        return "python"

    # Matches lines like: requests>=2.28.0 or just: requests
    _DEP_RE = re.compile(r"^([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,]+\])?)\s*(.*)")

    def extract(self, diff: str) -> DepContext:
        filename = self._extract_filename(diff)
        added = []
        removed = []

        for line in diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                dep = self._parse_dep_line(line[1:].strip())
                if dep:
                    dep.action = "added"
                    added.append(dep)
            elif line.startswith("-") and not line.startswith("---"):
                dep = self._parse_dep_line(line[1:].strip())
                if dep:
                    dep.action = "removed"
                    removed.append(dep)

        return DepContext(
            source_file=filename,
            added=added,
            removed=removed,
            raw_diff=diff,
        )

    def to_prompt_payload(self, context: DepContext) -> str:
        parts = [f"DEPENDENCY FILE: {context.source_file}"]

        if context.added:
            lines = "\n".join(
                f"+ {d.name}{d.version_spec}" for d in context.added
            )
            parts.append(f"ADDED DEPENDENCIES:\n{lines}")

        if context.removed:
            lines = "\n".join(
                f"- {d.name}{d.version_spec}" for d in context.removed
            )
            parts.append(f"REMOVED DEPENDENCIES:\n{lines}")

        if not context.added and not context.removed:
            parts.append("NO DEPENDENCY CHANGES DETECTED")

        return "\n\n".join(parts)

    def _extract_filename(self, diff: str) -> str:
        match = re.search(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
        return match.group(1) if match else "unknown"

    def _parse_dep_line(self, line: str) -> DepChange | None:
        """Parse a dependency line. Returns None for non-dep lines."""
        if not line or line.startswith("#") or line.startswith("["):
            return None
        match = self._DEP_RE.match(line)
        if match:
            name = match.group(1)
            version = match.group(2).strip()
            return DepChange(name=name, version_spec=version, action="")
        return None
