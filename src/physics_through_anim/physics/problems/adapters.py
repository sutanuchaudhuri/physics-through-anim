"""plan -> generic Recipe adapter (Milestone M17). Scaffold."""

from __future__ import annotations

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.recipes.base import Recipe


def plan_to_recipe(plan: ProblemScenePlan) -> Recipe:
    """Build a generic Recipe from a typed ProblemScenePlan."""
    raise NotImplementedError("M17 plan_to_recipe")
