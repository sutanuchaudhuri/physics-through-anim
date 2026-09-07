"""Deterministic plan validation: clear, ordered key/value errors."""

from __future__ import annotations

from physics_through_anim.physics.problems.scene_plan import (
    EntitySpec,
    ProblemScenePlan,
    RelationSpec,
    StepKind,
    StepSpec,
)
from physics_through_anim.physics.serialization import validate_plan
from physics_through_anim.physics.serialization.validation import PlanError


def _paths(errors: list[PlanError]) -> list[str]:
    return [e.path for e in errors]


def test_valid_plan_has_no_errors() -> None:
    plan = ProblemScenePlan(
        entities=[
            EntitySpec(kind="block", name="b", params={"position": [0.0, 0.0], "width": 0.8}),
            EntitySpec(kind="disk", name="d", params={"radius": 0.5}),
            EntitySpec(kind="rope", name="r",
                       params={"from_ref": "b.top", "to_ref": "d.CM"}),
        ],
        relations=[RelationSpec(kind="pin", participants=("b", "d"))],
        steps=[StepSpec(kind=StepKind.TIMESTEP, at=0.0, dt=0.5)],
    )
    assert validate_plan(plan) == []


def test_unknown_kind_and_param_and_duplicate_name() -> None:
    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="blork", name="x"),
        EntitySpec(kind="block", name="x", params={"width": "big", "bogus": 1}),
    ])
    paths = _paths(validate_plan(plan))
    assert "entities[0].kind" in paths
    assert "entities[1].name" in paths  # duplicate
    assert "entities[1].params.width" in paths  # wrong type
    assert "entities[1].params.bogus" in paths  # unknown param


def test_relation_kind_participants_and_refs() -> None:
    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        relations=[
            RelationSpec(kind="levitate", participants=("d", "d")),
            RelationSpec(kind="rope", participants=("d",)),
            RelationSpec(kind="pin", participants=("d", "ghost")),
        ],
    )
    paths = _paths(validate_plan(plan))
    assert "relations[0].kind" in paths  # unknown relation kind
    assert "relations[1].participants" in paths  # needs >= 2
    assert "relations[2].participants[1]" in paths  # dangling ref


def test_connector_keypoint_refs_are_checked() -> None:
    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="disk", name="d", params={"radius": 0.5}),
        EntitySpec(kind="rope", name="r", params={"from_ref": "d.middle", "to_ref": "ghost.top"}),
    ])
    paths = _paths(validate_plan(plan))
    assert "entities[1].params.from_ref" in paths  # bad keypoint
    assert "entities[1].params.to_ref" in paths  # unknown asset


def test_step_values_are_checked() -> None:
    plan = ProblemScenePlan(steps=[StepSpec(kind=StepKind.TIMESTEP, at=-1.0, dt=-2.0)])
    paths = _paths(validate_plan(plan))
    assert "steps[0].at" in paths
    assert "steps[0].dt" in paths


def test_marker_refs_are_checked() -> None:
    from physics_through_anim.physics.problems.scene_plan import MarkerSpec

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        markers=[
            MarkerSpec(point=(3.0, 0.0), label="ok"),  # valid
            MarkerSpec(at="d.middle"),  # bad keypoint
            MarkerSpec(),  # neither at nor point
        ],
    )
    paths = _paths(validate_plan(plan))
    assert "markers[1].at" in paths
    assert "markers[2]" in paths
    assert "markers[0]" not in [p.split(".")[0] for p in paths]  # the valid one is silent


def test_style_schema_is_checked() -> None:
    from physics_through_anim.physics.problems.scene_plan import StyleSpec

    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="disk", name="d", params={"radius": 0.5},
                   style=StyleSpec(display="glow", fill="marble", opacity=2.0)),
    ])
    paths = _paths(validate_plan(plan))
    assert "entities[0].style.display" in paths
    assert "entities[0].style.fill" in paths
    assert "entities[0].style.opacity" in paths


def test_mask_schema_is_checked() -> None:
    from physics_through_anim.physics.problems.scene_plan import MaskSpec

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        masks=[
            MaskSpec(kind="unicorn", at="d.CM"),  # unknown kind
            MaskSpec(kind="plume", at="d.middle"),  # bad keypoint
            MaskSpec(kind="rocket", point=(0.0, 0.0), opacity=1.5),  # opacity out of range
        ],
    )
    paths = _paths(validate_plan(plan))
    assert "masks[0].kind" in paths
    assert "masks[1].at" in paths
    assert "masks[2].opacity" in paths


def test_transform_schema_is_checked() -> None:
    from physics_through_anim.physics.problems.scene_plan import StepKind, StepSpec, TransformSpec

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        steps=[StepSpec(kind=StepKind.TIMESTEP, transforms=[
            TransformSpec(target="ghost", translate=(1.0, 0.0)),  # unknown target
            TransformSpec(target="d"),  # no translate/rotate
            TransformSpec(target="d", rotate_deg=45.0, about="d.middle"),  # bad pivot keypoint
        ])],
    )
    paths = _paths(validate_plan(plan))
    assert "steps[0].transforms[0].target" in paths
    assert "steps[0].transforms[1]" in paths
    assert "steps[0].transforms[2].about" in paths





def test_errors_are_deterministic_and_stringify() -> None:
    plan = ProblemScenePlan(entities=[EntitySpec(kind="blork", name="x")])
    first = validate_plan(plan)
    second = validate_plan(plan)
    assert first == second  # stable order + content
    assert str(first[0]).startswith("entities[0].kind:")
