import unittest

from skills.code_review.python.models.review_result import CodeReviewResult


class TestReviewResultModel(unittest.TestCase):
    def test_valid_model(self):
        data = {
            "file": "app/main.py",
            "risk_score": 30,
            "security_score": 90,
            "summary": "Found 1 issue(s).",
            "issues": [
                {
                    "id": "SEC-001",
                    "type": "SECURITY",
                    "severity": "LOW",
                    "line": 10,
                    "code": "API_KEY = 'x'",
                    "message": "Example",
                    "suggestion": "Use env var"
                }
            ],
            "summary_by_type": {
                "SECURITY": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 1}
            },
            "recommendation": "APPROVE_WITH_COMMENTS"
        }

        result = CodeReviewResult(**data)
        self.assertEqual(result.file, "app/main.py")
        self.assertEqual(result.issues[0].id, "SEC-001")


if __name__ == "__main__":
    unittest.main()
