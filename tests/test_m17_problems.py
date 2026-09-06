"""TDD spec for M17 -- problem / corpus orchestration."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.problems.adapters import plan_to_recipe
from physics_through_anim.physics.problems.refs import ProblemRef
from physics_through_anim.physics.problems.scene_plan import (
    EntitySpec,
    ProblemScenePlan,
    RelationSpec,
)

TDD = pytest.mark.xfail(reason="M17 not implemented (TDD spec)", strict=False)


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


@TDD
def test_plan_to_recipe() -> None:
    plan_to_recipe(ProblemScenePlan())
