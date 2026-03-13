"""AI Engineering Rigor — Skills package."""

from .registry import registry

# Register built-in skills
from .code_review.python.skill import PythonCodeReviewSkill
from .test_coverage.python.skill import PythonTestCoverageSkill
from .commit_quality.skill import CommitQualitySkill
from .dependency_audit.python.skill import PythonDependencyAuditSkill

registry.register(PythonCodeReviewSkill)
registry.register(PythonTestCoverageSkill)
registry.register(CommitQualitySkill)
registry.register(PythonDependencyAuditSkill)
