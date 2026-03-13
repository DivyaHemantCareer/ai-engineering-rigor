import unittest

from skills.code_review.python.prompts import build_user_prompt, SYSTEM_PROMPT


class TestPrompts(unittest.TestCase):
    def test_user_prompt_format(self):
        prompt = build_user_prompt(
            code_payload="CODE",
            intent_payload="INTENT",
            standards_payload="STANDARDS"
        )
        self.assertIn("STANDARDS", prompt)
        self.assertIn("INTENT", prompt)
        self.assertIn("CODE", prompt)
        self.assertIn("Return only JSON", prompt)

    def test_system_prompt_mentions_json(self):
        self.assertIn("Return ONLY valid JSON", SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
