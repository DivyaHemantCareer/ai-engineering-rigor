"""Pydantic models for commit message quality results."""

from pydantic import BaseModel, Field
from typing import List, Optional


class CommitIssue(BaseModel):
    """An issue found with the commit message."""
    rule: str
    message: str
    suggestion: Optional[str] = None


class CommitQualityResult(BaseModel):
    """Result of commit message quality analysis."""
    raw_message: str
    format_valid: bool
    scope_matches_files: bool
    issues: List[CommitIssue]
    suggested_rewrite: Optional[str] = None
    score: int = Field(..., ge=0, le=100)
