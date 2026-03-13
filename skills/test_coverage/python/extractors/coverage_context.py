"""Extractor that identifies changed functions and maps them to test files."""

import re
from dataclasses import dataclass, field
from typing import List
from pathlib import PurePosixPath

from skills.extractors.base import CodeExtractor


@dataclass
class FunctionInfo:
    """A function found in a diff."""
    name: str
    signature: str
    source_file: str


@dataclass
class CoverageContext:
    """Extracted coverage context from a diff."""
    source_file: str
    changed_functions: List[FunctionInfo]
    expected_test_file: str
    raw_diff: str


class CoverageContextExtractor(CodeExtractor):
    """
    Extracts changed function signatures from a diff and maps
    source files to their expected test files via naming conventions.
    """

    @property
    def language(self) -> str:
        return "python"

    def extract(self, diff: str) -> CoverageContext:
        filename = self._extract_filename(diff)
        functions = self._extract_functions(diff, filename)
        test_file = self._map_to_test_file(filename)
        return CoverageContext(
            source_file=filename,
            changed_functions=functions,
            expected_test_file=test_file,
            raw_diff=diff,
        )

    def to_prompt_payload(self, context: CoverageContext) -> str:
        parts = [f"SOURCE FILE: {context.source_file}"]
        parts.append(f"EXPECTED TEST FILE: {context.expected_test_file}")

        if context.changed_functions:
            sigs = "\n".join(f"- {f.signature}" for f in context.changed_functions)
            parts.append(f"CHANGED FUNCTIONS:\n{sigs}")
        else:
            parts.append("CHANGED FUNCTIONS: None detected")

        return "\n\n".join(parts)

    def _extract_filename(self, diff: str) -> str:
        match = re.search(r"^\+\+\+ b/(.+)$", diff, re.MULTILINE)
        return match.group(1) if match else "unknown"

    def _extract_functions(self, diff: str, filename: str) -> List[FunctionInfo]:
        functions = []
        for line in diff.splitlines():
            clean = line.lstrip("+-").strip()
            match = re.match(r"^(async\s+)?def\s+(\w+)", clean)
            if match:
                sig = clean.split(":")[0]
                name = match.group(2)
                # Skip test functions and dunder methods
                if not name.startswith("test_") and not (name.startswith("__") and name.endswith("__")):
                    functions.append(FunctionInfo(
                        name=name,
                        signature=sig,
                        source_file=filename,
                    ))
        return functions

    def _map_to_test_file(self, source_file: str) -> str:
        """Map foo.py -> test_foo.py using naming convention."""
        path = PurePosixPath(source_file)
        stem = path.stem
        return f"tests/test_{stem}.py"
