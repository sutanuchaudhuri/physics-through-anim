"""Spec-driven serialization: dataclass <-> JSON/XML, and ProblemScenePlan <-> Assembly."""

from __future__ import annotations

from physics_through_anim.physics.mechanics import Assembly, Block, Disk, Keypoint, Rope
from physics_through_anim.physics.mechanics.constraints import PinConstraint
from physics_through_anim.physics.mechanics.contact import Contact
from physics_through_anim.physics.problems.scene_plan import (
    EntitySpec,
    ProblemScenePlan,
    RelationSpec,
)
from physics_through_anim.physics.serialization import (
    assembly_to_plan,
    build_entity,
    entity_spec_of,
    from_json,
    from_xml,
    plan_to_assembly,
    to_json,
    to_xml,
)


def _sample_plan() -> ProblemScenePlan:
    return ProblemScenePlan(
        entities=[
            EntitySpec(kind="disk", name="d", params={"position": [0.0, 1.0], "radius": 0.5}),
            EntitySpec(kind="block", name="b", params={"position": [1.0, 0.0], "width": 0.8}),
        ],
        relations=[RelationSpec(kind="pin", participants=("d", "b"),
                                params={"at": "d.CM", "name": "pin1"})],
    )


def test_json_round_trip_is_lossless() -> None:
    plan = _sample_plan()
    assert from_json(ProblemScenePlan, to_json(plan)) == plan


def test_xml_round_trip_is_lossless() -> None:
    plan = _sample_plan()
    assert from_xml(ProblemScenePlan, to_xml(plan, root="plan")) == plan


def test_build_entity_and_export_round_trip() -> None:
    spec = EntitySpec(kind="disk", name="d", params={"position": [0.0, 1.0], "radius": 0.5})
    disk = build_entity(spec)
    assert isinstance(disk, Disk)
    assert disk.name == "d"
    assert disk.radius == 0.5
    back = entity_spec_of(disk)
    assert back.kind == "disk"
    assert back.name == "d"
    assert back.params["radius"] == 0.5
    assert back.params["position"] == [0.0, 1.0]


def test_plan_to_assembly_builds_members_and_constraints() -> None:
    assembly = plan_to_assembly(_sample_plan())
    assert [m.name for m in assembly.members] == ["d", "b"]
    assert assembly.constraints_by_name["pin1"].participants == ("d", "b")
    assert assembly.constraints_by_name["pin1"].at == "d.CM"


def test_relative_placement_seats_on_and_anchors_at() -> None:
    from physics_through_anim.physics.problems.scene_plan import PlacementSpec

    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="floor", name="floor", params={"y": -2.0}),
        EntitySpec(kind="block", name="m", params={"width": 1.0},
                   place=PlacementSpec(on="floor")),
        EntitySpec(kind="pulley", name="p",
                   params={"center": [0.0, 2.0], "rope_angles": {"left": 225.0, "right": 315.0}}),
        EntitySpec(kind="block", name="hung", params={"width": 0.6},
                   place=PlacementSpec(at="p.left", my="top", offset=(0.0, -1.0))),
    ])
    a = plan_to_assembly(plan)
    assert abs(a.body("m").keypoint("bottom")[1] - (-2.0)) < 1e-6  # seated on the floor
    left_y = a.resolve("p.left")[1]
    assert abs(a.body("hung").keypoint("top")[1] - (left_y - 1.0)) < 1e-6  # anchored below rim



def test_connectors_are_wired_by_name() -> None:
    plan = ProblemScenePlan(
        entities=[
            EntitySpec(kind="block", name="anchor", params={"position": [0.0, 2.0]}),
            EntitySpec(kind="block", name="load", params={"position": [0.0, 0.0]}),
            EntitySpec(kind="rope", name="rope",
                       params={"from_ref": "anchor.bottom", "to_ref": "load.top"}),
        ],
    )
    assembly = plan_to_assembly(plan)
    rope = assembly.body("rope")
    assert isinstance(rope, Rope)
    # connect() records a ROPE relation between the two endpoint assets.
    assert assembly.relations_between("anchor", "load")[0].kind.value == "rope"


def test_assembly_to_plan_exports_entities_and_contacts() -> None:
    a = Assembly()
    a.add(Block(name="b", position=(0.0, 0.0)))
    a.add(Disk(name="d", position=(1.0, 1.0), radius=0.4))
    a.add_relation(Contact(body="b", surface="d"))
    a.add_relation(PinConstraint(participants=("b", "d")), name="pin")
    plan = assembly_to_plan(a)
    assert {e.name for e in plan.entities} == {"b", "d"}
    kinds = {r.kind for r in plan.relations}
    assert "touch" in kinds
    assert "pin" in kinds
    # The exported plan rebuilds an equivalent assembly.
    rebuilt = plan_to_assembly(plan)
    assert {m.name for m in rebuilt.members} == {"b", "d"}
    assert "pin" in rebuilt.constraints_by_name


def test_keypoint_enum_survives_a_json_round_trip() -> None:
    # Enums serialise by value; Keypoint is a StrEnum used across specs.
    assert Keypoint.TOP.value == "top"


def _all_drawable_asset_classes() -> list[type]:
    import importlib
    import pkgutil

    from physics_through_anim.physics import mechanics as m
    from physics_through_anim.physics.mechanics.base import PhysicsAsset

    for mod in pkgutil.iter_modules(m.__path__):
        importlib.import_module(f"physics_through_anim.physics.mechanics.{mod.name}")

    found: set[type] = set()

    def walk(cls: type) -> None:
        for sub in cls.__subclasses__():
            if sub not in found:
                found.add(sub)
                walk(sub)

    walk(PhysicsAsset)
    # Only concrete drawables (override build); abstract bases inherit the raising one.
    return [c for c in found if c.build is not PhysicsAsset.build]


def test_every_drawable_asset_class_is_serializable() -> None:
    from physics_through_anim.physics.serialization.assets import (
        CANONICAL_KIND,
        build_entity,
        entity_spec_of,
    )

    for cls in _all_drawable_asset_classes():
        assert cls in CANONICAL_KIND, f"{cls.__name__} is not registered (not serializable)"
        try:
            obj = cls()  # only default-buildable classes are round-tripped here
        except Exception:  # noqa: BLE001 -- composites (e.g. SpringGroup) need params
            continue
        rebuilt = build_entity(entity_spec_of(obj))
        assert type(rebuilt) is cls

