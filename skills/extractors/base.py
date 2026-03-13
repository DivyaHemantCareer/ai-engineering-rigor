"""Abstract base class for code extractors."""

from abc import ABC, abstractmethod
from typing import Any


class CodeExtractor(ABC):
    """Base class for all code extractors.

    Extractors distill raw diffs into minimal, signal-rich context
    for LLM consumption. No LLM involved — pure Python parsing.
    """

    @property
    @abstractmethod
    def language(self) -> str:
        """Language this extractor handles, e.g. 'python'."""
        ...

    @abstractmethod
    def extract(self, diff: str) -> Any:
        """Parse a diff and return a structured context dataclass."""
        ...

    @abstractmethod
    def to_prompt_payload(self, context: Any) -> str:
        """Serialize extracted context into a compact prompt string."""
        ...
