"""Python code-review skill (deterministic, non-interactive)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Issue:
    type: str
    severity: str
    line: int
    message: str
    suggestion: str
    file: str


def _iter_source_files(repo_path: str) -> Iterable[str]:
    for root, _, files in os.walk(repo_path):
        for name in files:
            if name.endswith((".py", ".env", ".ini", ".yaml", ".yml", ".toml")):
                yield os.path.join(root, name)


def _scan_for_hardcoded_keys(path: str) -> List[Issue]:
    issues: List[Issue] = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, start=1):
                if "API_KEY" in line and ("=" in line or ":" in line):
                    issues.append(
                        Issue(
                            type="SECURITY",
                            severity="CRITICAL",
                            line=idx,
                            message="Hardcoded API key detected",
                            suggestion="Move to environment variable",
                            file=path,
                        )
                    )
    except OSError:
        return issues
    return issues


def run(repo_path: str) -> dict:
    issues: List[Issue] = []
    for path in _iter_source_files(repo_path):
        issues.extend(_scan_for_hardcoded_keys(path))

    risk_score = 0
    security_score = 100
    if issues:
        risk_score = 85
        security_score = 40

    return {
        "issues": [issue.__dict__ for issue in issues],
        "risk_score": risk_score,
        "security_score": security_score,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Python code-review skill")
    parser.add_argument("repo", help="Path to repository")
    args = parser.parse_args()

    result = run(args.repo)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
