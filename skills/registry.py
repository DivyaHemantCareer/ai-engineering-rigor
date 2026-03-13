"""Skill registry — discover and dispatch skills by name."""

from typing import Dict, List, Type
from .base import Skill


class SkillRegistry:
    """Registry for discovering and dispatching skills by name."""

    def __init__(self):
        self._skills: Dict[str, Type[Skill]] = {}

    def register(self, skill_cls: Type[Skill]) -> Type[Skill]:
        """Register a skill class. Can be used as a decorator."""
        # Instantiate temporarily to get the name
        # We store the class, not the instance
        name = skill_cls.__skill_name__
        self._skills[name] = skill_cls
        return skill_cls

    def get(self, name: str) -> Type[Skill]:
        """Get a skill class by name. Raises KeyError if not found."""
        if name not in self._skills:
            available = ", ".join(sorted(self._skills.keys()))
            raise KeyError(
                f"Unknown skill: '{name}'. Available: {available}"
            )
        return self._skills[name]

    def list_all(self) -> List[str]:
        """Return sorted list of registered skill names."""
        return sorted(self._skills.keys())


# Global registry instance
registry = SkillRegistry()
