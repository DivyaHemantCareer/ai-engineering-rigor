import unittest

from skills.code_review.python.extractors.code_context import CodeContextExtractor


class TestCodeContextExtractor(unittest.TestCase):
    def test_extracts_filename_and_hunks(self):
        diff = """
+++ b/app/routers/user.py
@@ -1,3 +1,4 @@
-import os
+import os
+from fastapi import APIRouter

-def foo():
+def foo(x: int) -> int:
+    return x
"""
        extractor = CodeContextExtractor()
        ctx = extractor.extract(diff)

        self.assertEqual(ctx.filename, "app/routers/user.py")
        self.assertTrue(any("from fastapi import APIRouter" in h for h in ctx.changed_hunks))
        self.assertTrue(any("def foo" in s for s in ctx.function_signatures))

    def test_prompt_payload_contains_sections(self):
        diff = """
+++ b/app/main.py
@@ -1,2 +1,3 @@
+from fastapi import FastAPI
+app = FastAPI()
"""
        extractor = CodeContextExtractor()
        payload = extractor.to_prompt_payload(extractor.extract(diff))
        self.assertIn("FILE: app/main.py", payload)
        self.assertIn("IMPORTS:", payload)
        self.assertIn("CHANGED CODE:", payload)


if __name__ == "__main__":
    unittest.main()
