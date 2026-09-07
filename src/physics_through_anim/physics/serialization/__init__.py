"""Spec-driven (de)serialisation: build scenes from JSON/XML config, and back.

Public surface:

* :mod:`~physics_through_anim.physics.serialization.codec` -- generic dataclass
  <-> dict / JSON / XML round-trip (``to_json``/``from_json``/``to_xml``/``from_xml``).
* :mod:`~physics_through_anim.physics.serialization.assets` -- ``EntitySpec`` <->
  ``PhysicsAsset`` (``build_entity``/``entity_spec_of``, ``ASSET_BUILDERS``).
* :mod:`~physics_through_anim.physics.serialization.assembly_io` -- ``ProblemScenePlan``
  <-> ``Assembly`` (``plan_to_assembly``/``assembly_to_plan``).
"""

from __future__ import annotations

from physics_through_anim.physics.serialization.assembly_io import (
    assembly_to_plan,
    plan_to_assembly,
)
from physics_through_anim.physics.serialization.assets import (
    ASSET_BUILDERS,
    CANONICAL_KIND,
    build_entity,
    entity_spec_of,
)
from physics_through_anim.physics.serialization.codec import (
    from_json,
    from_jsonable,
    from_xml,
    to_json,
    to_jsonable,
    to_xml,
)
from physics_through_anim.physics.serialization.state_io import (
    AssemblySnapshot,
    AssetSnapshot,
    snapshot_assembly,
    snapshot_asset,
)
from physics_through_anim.physics.serialization.validation import (
    PlanError,
    PlanValidationError,
    validate_plan,
)

__all__ = [
    "ASSET_BUILDERS",
    "CANONICAL_KIND",
    "AssemblySnapshot",
    "AssetSnapshot",
    "PlanError",
    "PlanValidationError",
    "assembly_to_plan",
    "build_entity",
    "entity_spec_of",
    "from_json",
    "from_jsonable",
    "from_xml",
    "plan_to_assembly",
    "snapshot_assembly",
    "snapshot_asset",
    "to_json",
    "to_jsonable",
    "to_xml",
    "validate_plan",
]
