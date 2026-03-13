"""Abstract base class for all skills."""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class Skill(ABC):
    """Base class that all skills must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier, e.g. 'code-review-python'."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description of what this skill does."""
        ...

    @abstractmethod
    def run(self, **kwargs) -> BaseModel:
        """Execute the skill and return a validated Pydantic result."""
        ...
