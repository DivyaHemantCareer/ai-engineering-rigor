"""Pydantic models for dependency audit results."""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskFlag(BaseModel):
    """A risk flag for a dependency."""
    dependency: str
    risk_level: RiskLevel
    reason: str
    recommendation: str


class DependencyAuditResult(BaseModel):
    """Result of dependency audit analysis."""
    source_file: str
    new_deps: List[str]
    removed_deps: List[str]
    risk_flags: List[RiskFlag]
    summary: str
    overall_risk: RiskLevel
