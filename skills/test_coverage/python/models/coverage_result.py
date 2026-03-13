"""Pydantic models for test coverage analysis results."""

from pydantic import BaseModel, Field
from typing import List


class SuggestedTest(BaseModel):
    """A test the LLM suggests writing."""
    function_name: str
    test_name: str
    description: str


class CoverageAnalysisResult(BaseModel):
    """Result of test coverage analysis on a diff."""
    source_file: str
    expected_test_file: str
    total_functions: int = Field(..., ge=0)
    uncovered_functions: List[str]
    suggested_tests: List[SuggestedTest]
    coverage_gap_summary: str
