"""TDD spec for M17 -- problem / corpus orchestration."""

from __future__ import annotations

from physics_through_anim.physics.problems.adapters import plan_to_recipe
from physics_through_anim.physics.problems.refs import ProblemRef
from physics_through_anim.physics.problems.scene_plan import (
    EntitySpec,
    ProblemScenePlan,
    RelationSpec,
)


def test_problem_ref_and_plan_are_typed() -> None:
    ref = ProblemRef(problem_id="KRO-045", source_id="krotov", problem_number="45")
    assert ref.problem_id == "KRO-045"
    plan = ProblemScenePlan(
        problem=ref,
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        relations=[RelationSpec(kind="rolling", participants=("d", "incline"))],
    )
    assert plan.problem.source_id == "krotov"
    assert plan.entities[0].params["radius"] == 0.5


def test_plan_to_recipe_builds_an_assembly() -> None:
    plan = ProblemScenePlan(
        entities=[
            EntitySpec(kind="disk", name="d", params={"radius": 0.5}),
            EntitySpec(kind="incline", name="incline", params={"angle_deg": 30.0}),
        ],
        relations=[RelationSpec(kind="rolling", participants=("d", "incline"),
                                params={"radius": 0.5, "name": "roll"})],
    )
    recipe = plan_to_recipe(plan)
    names = [m.name for m in recipe.assembly.members]
    assert names == ["d", "incline"]
    assert recipe.assembly.constraints_by_name["roll"].participants == ("d", "incline")
