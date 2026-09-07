"""Assembly <-> ProblemScenePlan: build a scene graph from config, and back (M17).

``plan_to_assembly`` is the spec-driven constructor: entities become mechanics
assets, connectors are wired by name, and explicit constraints/contacts are
re-declared. ``assembly_to_plan`` exports a built ``Assembly`` to the same typed,
serialisable plan (see ``serialization.codec`` for JSON/XML).

Caveat: assets are rebuilt from constructor params, so author absolute positions
in the spec -- placement sugar such as ``Assembly.hang`` is not reverse-engineered.
"""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics import (
    Assembly,
    PhysicsAsset,
    RelationKind,
)
from physics_through_anim.physics.mechanics.constraints import (
    ContactLockConstraint,
    DistanceConstraint,
    FixedAxleConstraint,
    FixedPointConstraint,
    PathConstraint,
    PinConstraint,
    RollingConstraint,
    RopeLengthConstraint,
    SlotConstraint,
)
from physics_through_anim.physics.mechanics.contact import Contact
from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan, RelationSpec
from physics_through_anim.physics.serialization.assets import (
    CANONICAL_KIND,
    build_entity,
    entity_spec_of,
)
from physics_through_anim.physics.serialization.codec import to_jsonable

__all__ = ["plan_to_assembly", "assembly_to_plan"]

# RelationKind -> typed constraint class (inverse of assembly._CONSTRAINT_KINDS).
_CONSTRAINT_CLASSES: dict[RelationKind, type] = {
    RelationKind.PIN: PinConstraint,
    RelationKind.FIXED_POINT: FixedPointConstraint,
    RelationKind.DISTANCE: DistanceConstraint,
    RelationKind.ROPE_LENGTH: RopeLengthConstraint,
    RelationKind.ROLLING: RollingConstraint,
    RelationKind.PATH: PathConstraint,
    RelationKind.SLOT: SlotConstraint,
    RelationKind.AXLE: FixedAxleConstraint,
    RelationKind.CONTACT_LOCK: ContactLockConstraint,
}
# Structural relations are re-derived from placement/connectors, not rebuilt directly.
_STRUCTURAL = {RelationKind.HANG, RelationKind.ROPE}


def _is_connector(asset: PhysicsAsset) -> bool:
    # A connector to *wire* only if both endpoint refs are set (a Rope); a Hinge
    # positioned by ``at`` has empty refs and is added like any other asset.
    return bool(getattr(asset, "from_ref", "")) and bool(getattr(asset, "to_ref", ""))


def plan_to_assembly(plan: ProblemScenePlan) -> Assembly:
    """Build a fully wired ``Assembly`` from a declarative ``ProblemScenePlan``.

    Placement is resolved relatively (``EntitySpec.place``): a body is seated
    ``on`` a support, or its ``my`` keypoint moved onto ``at`` + offset. Entities
    are added in dependency order so anchors exist first. Penetration checking is
    off: authored teaching snapshots may place bodies touching surfaces.
    """
    assembly = Assembly(check_penetration=False)
    built = {e.name: build_entity(e) for e in plan.entities}
    specs = {e.name: e for e in plan.entities}
    connectors = {n for n, a in built.items() if _is_connector(a)}

    def deps(entity) -> set[str]:
        d: set[str] = set()
        if entity.place:
            if entity.place.on:
                d.add(entity.place.on)
            if entity.place.at:
                d.add(entity.place.at.split(".", 1)[0])
        return d - connectors

    placed: set[str] = set()
    pending = [n for n in built if n not in connectors]
    progress = True
    while pending and progress:
        progress = False
        for name in list(pending):
            if deps(specs[name]) <= placed:
                _place_entity(assembly, specs[name], built[name], built)
                placed.add(name)
                pending.remove(name)
                progress = True
    for name in pending:  # cyclic/unresolved placement -> add as-is
        assembly.add(built[name])
    for name in connectors:
        assembly.connect(built[name])
    for rel in plan.relations:
        _apply_relation(assembly, rel)
    return assembly


def _place_entity(assembly: Assembly, spec, asset: PhysicsAsset, built: dict) -> None:
    place = spec.place
    if place and place.on and place.on in built:
        assembly.add(asset, place_on=built[place.on])
        return
    if place and place.at:
        try:
            target = assembly.resolve(place.at)
        except KeyError:
            assembly.add(asset)
            return
        goal = np.array([float(target[0]) + place.offset[0],
                         float(target[1]) + place.offset[1], 0.0])
        my = place.my if place.my in asset.keypoints else "CM"
        if my in asset.keypoints:
            asset.shift(goal - asset.keypoint(my))
    assembly.add(asset)


def _apply_relation(assembly: Assembly, rel: RelationSpec) -> None:
    kind = RelationKind(rel.kind)
    if kind in _STRUCTURAL:
        return  # re-derived when connectors are connected
    if kind is RelationKind.TOUCH:
        body, surface = (rel.participants + ("", ""))[:2]
        assembly.add_relation(Contact(body=body, surface=surface))
        return
    cls = _CONSTRAINT_CLASSES.get(kind)
    if cls is None:
        return
    params = dict(rel.params)
    name = params.pop("name", None)
    assembly.add_relation(cls(participants=tuple(rel.participants), **params), name=name)


def assembly_to_plan(assembly: Assembly) -> ProblemScenePlan:
    """Export a built ``Assembly`` to a typed, serialisable ``ProblemScenePlan``."""
    entities = [entity_spec_of(m) for m in assembly.members if type(m) in CANONICAL_KIND]
    relations: list[RelationSpec] = []
    for name, constraint in assembly.constraints_by_name.items():
        kind = _kind_of_constraint(constraint)
        params = {
            f: to_jsonable(getattr(constraint, f))
            for f in ("at", "to", "point", "distance", "length", "radius", "gap", "slot", "path")
            if hasattr(constraint, f)
        }
        params["name"] = name
        relations.append(RelationSpec(kind=kind.value,
                                      participants=tuple(getattr(constraint, "participants", ())),
                                      params=params))
    for contact in assembly.contacts:
        relations.append(RelationSpec(kind=RelationKind.TOUCH.value,
                                      participants=(contact.body, contact.surface)))
    for rel in assembly.relations:
        if rel.kind in _STRUCTURAL:
            params = {"name": rel.name} if rel.name else {}
            relations.append(RelationSpec(kind=rel.kind.value,
                                          participants=rel.participants, params=params))
    return ProblemScenePlan(entities=entities, relations=relations)


def _kind_of_constraint(constraint: object) -> RelationKind:
    for kind, cls in _CONSTRAINT_CLASSES.items():
        if isinstance(constraint, cls):
            return kind
    return RelationKind.CONSTRAINT
