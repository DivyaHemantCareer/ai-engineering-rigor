"""Diff splitting and file detection utilities."""

import re
from typing import List


def split_diff_by_file(diff: str) -> List[str]:
    """Split a multi-file diff into per-file segments on 'diff --git' boundaries."""
    segments = re.split(r"(?=^diff --git )", diff, flags=re.MULTILINE)
    return [s.strip() for s in segments if s.strip()]


def is_python_file(filename: str) -> bool:
    """Check if a filename is a Python file."""
    return filename.endswith(".py")
