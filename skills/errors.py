"""Shared error hierarchy for all skills."""


class SkillError(Exception):
    """Base exception for all skill errors."""


class ExtractionError(SkillError):
    """Raised when code extraction from a diff fails."""


class LLMError(SkillError):
    """Raised when the LLM call fails (network, auth, timeout)."""


class ValidationError(SkillError):
    """Raised when LLM output fails Pydantic validation."""
