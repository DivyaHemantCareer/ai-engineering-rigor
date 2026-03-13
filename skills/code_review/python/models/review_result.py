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


class MultiFileReviewResult(BaseModel):
    """Aggregated review result across multiple files."""
    results: List[CodeReviewResult]
    overall_recommendation: Recommendation
    total_issues: int = Field(..., ge=0)
    files_reviewed: int = Field(..., ge=0)

    @classmethod
    def from_results(cls, results: List[CodeReviewResult]) -> "MultiFileReviewResult":
        """Aggregate individual file results into a multi-file result."""
        if not results:
            return cls(
                results=[],
                overall_recommendation=Recommendation.APPROVE,
                total_issues=0,
                files_reviewed=0,
            )

        total_issues = sum(len(r.issues) for r in results)

        # Overall recommendation = worst recommendation across all files
        priority = [
            Recommendation.BLOCK_MERGE,
            Recommendation.REQUEST_CHANGES,
            Recommendation.APPROVE_WITH_COMMENTS,
            Recommendation.APPROVE,
        ]
        overall = Recommendation.APPROVE
        for rec in priority:
            if any(r.recommendation == rec for r in results):
                overall = rec
                break

        return cls(
            results=results,
            overall_recommendation=overall,
            total_issues=total_issues,
            files_reviewed=len(results),
        )
