import re
from dataclasses import dataclass
from typing import List, Optional, Sequence

from skills.extractors.base import CodeExtractor


@dataclass
class CodeContext:
    """Minimal, finite code context extracted from a git diff."""
    filename: str
    changed_hunks: List[str]        # actual changed lines only
    imports: List[str]              # import statements
    function_signatures: List[str]  # def/async def signatures
    class_definitions: List[str]    # class definitions
    decorators: List[str]           # route decorators, etc.
    raw_diff: str                   # original diff for reference


class CodeContextExtractor(CodeExtractor):
    """
    Layer 1 — Extracts minimal, signal-rich context from a git diff.
    No LLM involved — pure Python parsing.
    Goal: pass only what matters to the LLM, not the entire file.
    """

    @property
    def language(self) -> str:
        return "python"

    def extract(self, diff: str) -> CodeContext:
        return CodeContext(
            filename=self._extract_filename(diff),
            changed_hunks=self._extract_changed_hunks(diff),
            imports=self._extract_imports(diff),
            function_signatures=self._extract_function_signatures(diff),
            class_definitions=self._extract_class_definitions(diff),
            decorators=self._extract_decorators(diff),
            raw_diff=diff
        )

    def _extract_filename(self, diff: str) -> str:
        """Extract filename from diff header."""
        match = re.search(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
        return match.group(1) if match else "unknown"

    def _extract_changed_hunks(self, diff: str) -> List[str]:
        """
        Extract only added/modified lines from diff.
        Strips metadata, keeps signal.
        """
        hunks = []
        current_hunk = []

        for line in diff.splitlines():
            if line.startswith("@@"):
                if current_hunk:
                    hunks.append("\n".join(current_hunk))
                current_hunk = [line]
            elif line.startswith("+") and not line.startswith("+++"):
                current_hunk.append(line[1:].rstrip())  # strip leading +
            elif line.startswith("-") and not line.startswith("---"):
                current_hunk.append(f"[REMOVED] {line[1:].rstrip()}")

        if current_hunk:
            hunks.append("\n".join(current_hunk))

        return hunks

    def _extract_imports(self, diff: str) -> List[str]:
        """Extract import statements — reveals dependencies and security risks."""
        imports = []
        for line in diff.splitlines():
            clean = line.lstrip("+-").strip()
            if clean.startswith("import ") or clean.startswith("from "):
                imports.append(clean)
        return list(set(imports))  # deduplicate

    def _extract_function_signatures(self, diff: str) -> List[str]:
        """
        Extract function signatures only — not full bodies.
        Gives LLM interface context without token explosion.
        """
        signatures = []
        lines = diff.splitlines()

        for i, line in enumerate(lines):
            clean = line.lstrip("+-").strip()
            if re.match(r"^(async\s+)?def\s+\w+", clean):
                signatures.append(clean.split(":")[0])  # signature only, no body

        return signatures

    def _extract_class_definitions(self, diff: str) -> List[str]:
        """Extract class definitions — data models, request/response schemas."""
        classes = []
        for line in diff.splitlines():
            clean = line.lstrip("+-").strip()
            if re.match(r"^class\s+\w+", clean):
                classes.append(clean.split(":")[0])
        return classes

    def _extract_decorators(self, diff: str) -> List[str]:
        """
        Extract decorators — FastAPI route decorators reveal
        auth patterns, HTTP methods, endpoint paths.
        """
        decorators = []
        for line in diff.splitlines():
            clean = line.lstrip("+-").strip()
            if clean.startswith("@"):
                decorators.append(clean)
        return list(set(decorators))

    def extract_all(self, diff: str) -> List[CodeContext]:
        """
        Split a multi-file diff on 'diff --git' boundaries
        and extract context for each file segment.
        """
        segments = re.split(r"(?=^diff --git )", diff, flags=re.MULTILINE)
        contexts = []
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            contexts.append(self.extract(segment))
        # If no 'diff --git' headers found, treat as single-file diff
        if not contexts:
            contexts.append(self.extract(diff))
        return contexts

    def to_prompt_payload(self, context: CodeContext) -> str:
        """
        Serialize extracted context into a compact,
        token-efficient string for the LLM prompt.
        """
        parts = []

        parts.append(f"FILE: {context.filename}")

        if context.imports:
            parts.append("IMPORTS:\n" + "\n".join(context.imports))

        if context.class_definitions:
            parts.append("CLASSES:\n" + "\n".join(context.class_definitions))

        if context.decorators:
            parts.append("DECORATORS:\n" + "\n".join(context.decorators))

        if context.function_signatures:
            parts.append("FUNCTION SIGNATURES:\n" + "\n".join(context.function_signatures))

        if context.changed_hunks:
            parts.append("CHANGED CODE:\n" + "\n---\n".join(context.changed_hunks))

        return "\n\n".join(parts)
