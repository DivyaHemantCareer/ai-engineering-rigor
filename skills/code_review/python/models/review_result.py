from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class IssueType(str, Enum):
    SECURITY = "SECURITY"
    FASTAPI = "FASTAPI"
    TYPE_HINT = "TYPE_HINT"
    PERFORMANCE = "PERFORMANCE"
    QUALITY = "QUALITY"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Recommendation(str, Enum):
    BLOCK_MERGE = "BLOCK_MERGE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    APPROVE_WITH_COMMENTS = "APPROVE_WITH_COMMENTS"
    APPROVE = "APPROVE"


class Issue(BaseModel):
    id: str = Field(..., pattern=r"^(SEC|FASTAPI|TYPE|PERF|QUALITY)-[0-9]{3}$")
    type: IssueType
    severity: Severity
    line: int = Field(..., ge=1)
    code: str
    message: str
    suggestion: str


class SummaryByType(BaseModel):
    CRITICAL: int = 0
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0


class CodeReviewResult(BaseModel):
    file: str
    risk_score: int = Field(..., ge=0, le=100)
    security_score: int = Field(..., ge=0, le=100)
    summary: str
    issues: List[Issue]
    summary_by_type: dict[str, SummaryByType]
    recommendation: Recommendation
