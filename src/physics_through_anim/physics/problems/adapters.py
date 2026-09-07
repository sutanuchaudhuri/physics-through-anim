"""plan -> generic Recipe adapter (Milestone M17)."""

from __future__ import annotations

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.recipes.base import Recipe
from physics_through_anim.physics.serialization.assembly_io import plan_to_assembly


def plan_to_recipe(plan: ProblemScenePlan) -> Recipe:
    """Build a generic ``Recipe`` (a semantic ``Assembly`` bundle) from a typed plan."""
    return Recipe(assembly=plan_to_assembly(plan))
