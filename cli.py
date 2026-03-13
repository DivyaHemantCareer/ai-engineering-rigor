#!/usr/bin/env python3
"""
AI Engineering Rigor — Python Code Review Skill CLI

Usage:
    # Review a git diff
    python cli.py --diff "$(git diff HEAD~1)" --pr "Add user auth endpoint"

    # Review a specific file diff
    git diff HEAD~1 -- app/routers/user.py | python cli.py --stdin

    # With custom standards
    python cli.py --diff "$(git diff)" --standards ./standards.md

Environment Variables:
    LLM_PROVIDER    azure | openai  (default: azure)
    LLM_API_KEY     Your API key
    LLM_MODEL       Model name     (default: gpt-4o-mini)
    LLM_ENDPOINT    Azure endpoint (required for Azure)
"""

import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from skills.code_review.python.skill import PythonCodeReviewSkill
from skills.code_review.python.llm_provider import LLMConfig


def print_review(result, output_format: str):
    """Print review result in requested format."""

    if output_format == "json":
        print(json.dumps(result.model_dump(), indent=2))
        return

    # Markdown output
    severity_emoji = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🔵"
    }

    recommendation_emoji = {
        "BLOCK_MERGE": "🚫",
        "REQUEST_CHANGES": "⚠️",
        "APPROVE_WITH_COMMENTS": "💬",
        "APPROVE": "✅"
    }

    print(f"\n{'='*60}")
    print(f"AI Engineering Rigor — Code Review")
    print(f"{'='*60}")
    print(f"File:            {result.file}")
    print(f"Risk Score:      {result.risk_score}/100")
    print(f"Security Score:  {result.security_score}/100")
    print(f"Recommendation:  {recommendation_emoji.get(result.recommendation, '')} {result.recommendation}")
    print(f"\nSummary: {result.summary}")

    if result.issues:
        print(f"\n{'─'*60}")
        print(f"Issues Found ({len(result.issues)}):")
        print(f"{'─'*60}")
        for issue in result.issues:
            emoji = severity_emoji.get(issue.severity, "")
            print(f"\n{emoji} [{issue.severity}] {issue.id} — Line {issue.line}")
            print(f"   Code:       {issue.code}")
            print(f"   Issue:      {issue.message}")
            print(f"   Fix:        {issue.suggestion}")
    else:
        print("\n✅ No issues found!")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI Engineering Rigor — Python Code Review Skill"
    )
    parser.add_argument("--diff", type=str, help="Git diff string")
    parser.add_argument("--stdin", action="store_true", help="Read diff from stdin")
    parser.add_argument("--pr", type=str, help="PR description", default=None)
    parser.add_argument("--ticket", type=str, help="Ticket ID", default=None)
    parser.add_argument("--spec", type=str, help="Spec summary", default=None)
    parser.add_argument("--standards", type=str, help="Path to standards file", default=None)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()

    # Get diff
    if args.stdin:
        diff = sys.stdin.read()
    elif args.diff:
        diff = args.diff
    else:
        print("Error: provide --diff or --stdin")
        sys.exit(1)

    if not diff.strip():
        print("Error: empty diff provided")
        sys.exit(1)

    # Load LLM config from environment
    config = LLMConfig.from_env()

    if not config.api_key:
        print("Error: LLM_API_KEY environment variable not set")
        sys.exit(1)

    # Run review
    skill = PythonCodeReviewSkill(llm_config=config)

    try:
        result = skill.review(
            diff=diff,
            pr_description=args.pr,
            ticket_id=args.ticket,
            spec_summary=args.spec,
            standards_file=args.standards
        )
        print_review(result, args.format)

        # Exit with non-zero if BLOCK_MERGE — useful for CI
        if result.recommendation == "BLOCK_MERGE":
            sys.exit(1)

    except Exception as e:
        print(f"Review failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
