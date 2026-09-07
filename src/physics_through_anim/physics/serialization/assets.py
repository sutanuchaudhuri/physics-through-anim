"""Asset builder registry: ``EntitySpec`` <-> ``PhysicsAsset`` (Milestone M17).

A spec names an asset by a stable ``kind`` string plus constructor ``params``;
this module maps ``kind`` to the mechanics class and back. Assets are rebuilt
from their *constructor* arguments (not internal geometry), so a spec is the
authoring source of truth -- author absolute positions in the spec rather than
relying on placement sugar (``Assembly.hang``) being reversed.

Extend ``ASSET_BUILDERS`` (and ``CANONICAL_KIND``) to register more assets.
"""

from __future__ import annotations

import importlib
import pkgutil
import re
from dataclasses import fields
from enum import Enum
from typing import get_type_hints

from physics_through_anim.physics import mechanics as _mechanics
from physics_through_anim.physics.mechanics import (
    Block,
    Cable,
    Ceiling,
    Cylinder,
    Disk,
    Floor,
    Hinge,
    Hoop,
    Incline,
    Peg,
    PhysicsAsset,
    PinJoint,
    Pulley,
    Ring,
    Rope,
    SharpEdge,
    Sphere2D,
    Table,
    Wall,
)
from physics_through_anim.physics.problems.scene_plan import EntitySpec
from physics_through_anim.physics.serialization.codec import from_jsonable, to_jsonable

__all__ = ["ASSET_BUILDERS", "CANONICAL_KIND", "build_entity", "entity_spec_of"]

# kind string -> asset class. Multiple kinds may map to one class (aliases).
ASSET_BUILDERS: dict[str, type[PhysicsAsset]] = {
    "block": Block,
    "disk": Disk,
    "ring": Ring,
    "hoop": Hoop,
    "sphere": Sphere2D,
    "cylinder": Cylinder,
    "pulley": Pulley,
    "ceiling": Ceiling,
    "incline": Incline,
    "floor": Floor,
    "wall": Wall,
    "table": Table,
    "edge": SharpEdge,
    "peg": Peg,
    "rope": Rope,
    "cable": Cable,
    "hinge": Hinge,
    "pin_joint": PinJoint,
}

# The reverse map used for export: one canonical kind per class.
CANONICAL_KIND: dict[type[PhysicsAsset], str] = {
    Block: "block",
    Disk: "disk",
    Ring: "ring",
    Sphere2D: "sphere",
    Cylinder: "cylinder",
    Pulley: "pulley",
    Ceiling: "ceiling",
    Incline: "incline",
    Floor: "floor",
    Wall: "wall",
    Table: "table",
    SharpEdge: "edge",
    Peg: "peg",
    Rope: "rope",
    Cable: "cable",
    Hinge: "hinge",
    PinJoint: "pin_joint",
}

# Values that survive a JSON/XML round-trip; other fields (e.g. a Mobject skin) are
# dropped from an exported spec because they cannot be serialised.
_SERIALISABLE = (str, int, float, bool, tuple, list, dict, Enum, type(None))


def _camel_to_snake(name: str) -> str:
    """``RopeOverPulley`` -> ``rope_over_pulley``; ``Sphere2D`` -> ``sphere2_d``."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _register_all_assets() -> None:
    """Auto-register every concrete drawable asset so *all* are serializable.

    Imports every ``mechanics`` submodule (so subclasses are defined), then adds
    any ``PhysicsAsset`` subclass that overrides ``build()`` under a snake_case
    kind -- curated names above win (``setdefault``). Abstract bases whose
    ``build`` is the base's (``Connector``/``Support``) are skipped.
    """
    for module in pkgutil.iter_modules(_mechanics.__path__):
        importlib.import_module(f"physics_through_anim.physics.mechanics.{module.name}")

    seen: set[type] = set()

    def walk(cls: type) -> None:
        for sub in cls.__subclasses__():
            if sub not in seen:
                seen.add(sub)
                if sub.build is not PhysicsAsset.build and sub not in CANONICAL_KIND:
                    kind = _camel_to_snake(sub.__name__)
                    ASSET_BUILDERS.setdefault(kind, sub)
                    CANONICAL_KIND[sub] = kind
                walk(sub)

    walk(PhysicsAsset)


_register_all_assets()


def build_entity(spec: EntitySpec) -> PhysicsAsset:
    """Instantiate the mechanics asset named by ``spec.kind`` from its params."""
    if spec.kind not in ASSET_BUILDERS:
        raise KeyError(f"Unknown asset kind {spec.kind!r}. Known: {sorted(ASSET_BUILDERS)}")
    cls = ASSET_BUILDERS[spec.kind]
    hints = get_type_hints(cls)
    kwargs: dict[str, object] = {}
    if spec.name:
        kwargs["name"] = spec.name
    for key, value in spec.params.items():
        kwargs[key] = from_jsonable(hints.get(key, object), value)
    return cls(**kwargs)


def entity_spec_of(asset: PhysicsAsset) -> EntitySpec:
    """Export a placed asset back to an ``EntitySpec`` (constructor params only)."""
    cls = type(asset)
    if cls not in CANONICAL_KIND:
        raise KeyError(f"{cls.__name__} is not registered for export (add it to CANONICAL_KIND).")
    params: dict[str, object] = {}
    for f in fields(asset):
        if not f.init or f.name == "name":
            continue
        value = getattr(asset, f.name)
        if not isinstance(value, _SERIALISABLE) or value is None:
            continue
        params[f.name] = to_jsonable(value)
    return EntitySpec(kind=CANONICAL_KIND[cls], name=asset.name, params=params)
