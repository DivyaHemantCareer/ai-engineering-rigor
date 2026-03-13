"""AI Engineering Rigor CLI for skill discovery and execution."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from typing import List


def _discover_skills(root: str) -> List[dict]:
    skills = []
    for dirpath, _, filenames in os.walk(root):
        if "SKILL.md" in filenames:
            rel_path = os.path.relpath(dirpath, root)
            parts = rel_path.split(os.sep)
            skill_name = parts[0] if parts else rel_path
            language = parts[1] if len(parts) > 1 else "unknown"
            skills.append(
                {
                    "skill": skill_name,
                    "language": language,
                    "path": dirpath,
                }
            )
    return skills


def _load_skill_module(skill_dir: str):
    skill_path = os.path.join(skill_dir, "skill.py")
    spec = importlib.util.spec_from_file_location("skill", skill_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load skill from {skill_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cmd_list(args: argparse.Namespace) -> None:
    skills = _discover_skills(args.skills_root)
    print(json.dumps(skills, indent=2))


def cmd_run(args: argparse.Namespace) -> None:
    module = _load_skill_module(args.skill_path)
    if not hasattr(module, "run"):
        raise RuntimeError("Skill module missing run()")
    result = module.run(args.repo)
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Engineering Rigor CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available skills")
    p_list.add_argument("--skills-root", default="skills", help="Skills root directory")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Run a skill")
    p_run.add_argument("--skill-path", required=True, help="Path to a skill directory")
    p_run.add_argument("--repo", required=True, help="Path to repository")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
