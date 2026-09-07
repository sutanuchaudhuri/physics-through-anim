"""Deterministic plan validator: clear, ordered errors for a ``ProblemScenePlan``.

``validate_plan`` never raises on bad *content*; it returns a list of
``PlanError(path, message)`` in a stable order (entities, then relations, then
connector refs, then steps). It checks unknown kinds, unknown/typed params,
duplicate and dangling names, connector keypoint refs, and step values -- so a
bad JSON/XML file explains itself instead of crashing deep in a builder.
"""

from __future__ import annotations

import types
from dataclasses import dataclass, fields
from enum import Enum
from typing import Union, get_args, get_origin, get_type_hints

from physics_through_anim.physics.mechanics import RelationKind
from physics_through_anim.physics.problems.scene_plan import (
    LabelPlacement,
    ProblemScenePlan,
    StepKind,
)
from physics_through_anim.physics.serialization.assets import ASSET_BUILDERS, build_entity

__all__ = ["PlanError", "PlanValidationError", "validate_plan"]

_CONNECTOR_KINDS = {"rope", "cable"}
# Relation kinds that describe a link and therefore need at least two participants.
_BINARY_RELATIONS = {"hang", "rope", "touch", "pin", "distance", "rolling", "rope_length"}
_NONE_TYPE = type(None)
_DISPLAY_MODES = ("solid", "fade", "dotted", "dashed")
_FILL_MODES = ("solid", "hashed", "none")
_LABEL_PLACEMENTS = tuple(p.value for p in LabelPlacement)


@dataclass(frozen=True)
class PlanError:
    """One validation problem: a dotted ``path`` into the plan and a message."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class PlanValidationError(ValueError):
    """Raised when a plan is used despite validation errors; carries the list."""

    def __init__(self, errors: list[PlanError]) -> None:
        self.errors = errors
        super().__init__("Invalid plan:\n" + "\n".join(f"  - {e}" for e in errors))


def validate_plan(plan: ProblemScenePlan) -> list[PlanError]:
    """Return a deterministic list of problems in ``plan`` (empty == valid)."""
    errors: list[PlanError] = []
    names = _check_entities(plan, errors)
    built = _build_valid_entities(plan, errors)
    _augment_placed_keypoints(plan, built)  # seating adds keypoints (e.g. 'contact')
    _check_relations(plan, names, errors)
    _check_connector_refs(plan, built, errors)
    _check_markers(plan, built, errors)
    _check_vectors(plan, built, errors)
    _check_paths(plan, errors)
    _check_masks(plan, built, errors)
    _check_steps(plan, names, built, errors)
    return errors


def _check_masks(plan: ProblemScenePlan, built: dict, errors: list[PlanError]) -> None:
    from physics_through_anim.physics.rendering.masks import MASK_BUILDERS
    for i, mask in enumerate(plan.masks):
        at = f"masks[{i}]"
        if mask.kind not in MASK_BUILDERS:
            errors.append(PlanError(
                f"{at}.kind", f"unknown mask kind {mask.kind!r}; known: {sorted(MASK_BUILDERS)}"))
        if not mask.at and mask.point is None and not mask.points:
            errors.append(PlanError(at, "mask needs 'at', 'point', or 'points' (chain)"))
        if mask.kind == "chain" and len(mask.points) < 2:
            errors.append(PlanError(f"{at}.points", "a chain mask needs at least two points"))
        if mask.at:
            a_name, _, kp = mask.at.partition(".")
            asset = built.get(a_name)
            if "." not in mask.at or asset is None:
                errors.append(PlanError(f"{at}.at", f"unknown anchor ref {mask.at!r}"))
            elif kp not in asset.keypoints:
                errors.append(PlanError(
                    f"{at}.at",
                    f"asset {a_name!r} has no keypoint {kp!r}; known: {sorted(asset.keypoints)}"))
        if not 0.0 <= mask.opacity <= 1.0:
            errors.append(PlanError(f"{at}.opacity",
                                    f"opacity must be in [0, 1], got {mask.opacity}"))


def _check_entities(plan: ProblemScenePlan, errors: list[PlanError]) -> set[str]:
    names: set[str] = set()
    for i, entity in enumerate(plan.entities):
        at = f"entities[{i}]"
        if not entity.name:
            errors.append(PlanError(f"{at}.name", "entity name is required"))
        elif entity.name in names:
            errors.append(PlanError(f"{at}.name", f"duplicate entity name {entity.name!r}"))
        else:
            names.add(entity.name)

        if not entity.kind:
            errors.append(PlanError(f"{at}.kind", "entity kind is required"))
            continue
        if entity.kind not in ASSET_BUILDERS:
            errors.append(PlanError(
                f"{at}.kind",
                f"unknown kind {entity.kind!r}; known: {sorted(ASSET_BUILDERS)}"))
            continue
        _check_params(entity.kind, entity.params, f"{at}.params", errors)
        _check_style(entity.style, f"{at}.style", errors)
        if str(entity.label.placement) not in _LABEL_PLACEMENTS:
            errors.append(PlanError(
                f"{at}.label.placement",
                f"unknown placement {entity.label.placement!r}; "
                f"options: {list(_LABEL_PLACEMENTS)}"))
    _check_placements(plan, names, errors)
    return names


def _check_placements(plan: ProblemScenePlan, names: set[str],
                      errors: list[PlanError]) -> None:
    built = {}
    for e in plan.entities:
        if e.name and e.kind in ASSET_BUILDERS and e.name not in built:
            try:
                built[e.name] = build_entity(e)
            except Exception:  # noqa: BLE001 -- reported elsewhere
                pass
    for i, entity in enumerate(plan.entities):
        place = entity.place
        if place is None:
            continue
        at = f"entities[{i}].place"
        if place.on and place.on not in names:
            errors.append(PlanError(f"{at}.on", f"seats on unknown entity {place.on!r}"))
        if place.at:
            a_name, _, kp = place.at.partition(".")
            asset = built.get(a_name)
            if "." not in place.at or a_name not in names:
                errors.append(PlanError(f"{at}.at", f"unknown anchor ref {place.at!r}"))
            elif asset is not None and kp not in asset.keypoints:
                errors.append(PlanError(
                    f"{at}.at",
                    f"asset {a_name!r} has no keypoint {kp!r}; known: {sorted(asset.keypoints)}"))
        mine = built.get(entity.name)
        if place.my and place.my != "CM" and mine is not None and place.my not in mine.keypoints:
            errors.append(PlanError(
                f"{at}.my",
                f"{entity.name!r} has no keypoint {place.my!r}; known: {sorted(mine.keypoints)}"))


def _check_style(style, at: str, errors: list[PlanError]) -> None:
    if style.display not in _DISPLAY_MODES:
        errors.append(PlanError(
            f"{at}.display", f"unknown display {style.display!r}; options: {list(_DISPLAY_MODES)}"))
    if style.fill not in _FILL_MODES:
        errors.append(PlanError(
            f"{at}.fill", f"unknown fill {style.fill!r}; options: {list(_FILL_MODES)}"))
    if style.opacity is not None and not 0.0 <= style.opacity <= 1.0:
        errors.append(PlanError(f"{at}.opacity", f"opacity must be in [0, 1], got {style.opacity}"))


def _check_params(kind: str, params: dict, at: str, errors: list[PlanError]) -> None:
    cls = ASSET_BUILDERS[kind]
    valid = {f.name for f in fields(cls) if f.init}
    try:
        hints = get_type_hints(cls)
    except Exception:  # noqa: BLE001 -- unresolved annotations: skip value typing, keep key check
        hints = {}
    for key, value in params.items():
        if key not in valid:
            errors.append(PlanError(
                f"{at}.{key}",
                f"unknown param for kind {kind!r}; valid: {sorted(valid - {'name'})}"))
            continue
        problem = _value_error(hints.get(key, object), value)
        if problem:
            errors.append(PlanError(f"{at}.{key}", problem))


def _build_valid_entities(plan: ProblemScenePlan, errors: list[PlanError]) -> dict:
    """Build each well-formed entity so keypoint refs can be checked; report failures."""
    built: dict = {}
    for i, entity in enumerate(plan.entities):
        if not entity.name or entity.kind not in ASSET_BUILDERS or entity.name in built:
            continue
        try:
            built[entity.name] = build_entity(entity)
        except Exception as exc:  # noqa: BLE001 -- surface the constructor error deterministically
            errors.append(PlanError(f"entities[{i}]", f"cannot build {entity.name!r}: {exc}"))
    return built


def _augment_placed_keypoints(plan: ProblemScenePlan, built: dict) -> None:
    """Merge assembled keypoints (seating adds e.g. ``contact``) into the built assets."""
    from physics_through_anim.physics.serialization.assembly_io import plan_to_assembly
    try:
        assembly = plan_to_assembly(plan)
    except Exception:  # noqa: BLE001 -- a broken plan; standalone keypoints are enough
        return
    for full, point in assembly.keypoints.items():
        asset_name, _, key = full.partition(".")
        asset = built.get(asset_name)
        if asset is not None and key not in asset.keypoints:
            asset.keypoints[key] = point


def _check_relations(plan: ProblemScenePlan, names: set[str],
                     errors: list[PlanError]) -> None:
    valid = {k.value for k in RelationKind}
    for i, rel in enumerate(plan.relations):
        at = f"relations[{i}]"
        if not rel.kind:
            errors.append(PlanError(f"{at}.kind", "relation kind is required"))
        elif rel.kind not in valid:
            errors.append(PlanError(
                f"{at}.kind", f"unknown relation kind {rel.kind!r}; known: {sorted(valid)}"))
        if not rel.participants:
            errors.append(PlanError(f"{at}.participants", "at least one participant is required"))
        elif rel.kind in _BINARY_RELATIONS and len(rel.participants) < 2:
            errors.append(PlanError(
                f"{at}.participants",
                f"kind {rel.kind!r} needs >=2 participants, got {len(rel.participants)}"))
        for j, member in enumerate(rel.participants):
            if member not in names:
                errors.append(PlanError(
                    f"{at}.participants[{j}]", f"references unknown entity {member!r}"))


def _check_connector_refs(plan: ProblemScenePlan, built: dict,
                          errors: list[PlanError]) -> None:
    for i, entity in enumerate(plan.entities):
        if entity.kind not in _CONNECTOR_KINDS:
            continue
        for ref_key in ("from_ref", "to_ref"):
            at = f"entities[{i}].params.{ref_key}"
            ref = entity.params.get(ref_key)
            if not isinstance(ref, str) or "." not in ref:
                errors.append(PlanError(at, "connector needs an 'asset.keypoint' ref string"))
                continue
            asset_name, _, keypoint = ref.partition(".")
            asset = built.get(asset_name)
            if asset is None:
                errors.append(PlanError(at, f"unknown asset {asset_name!r} in ref {ref!r}"))
            elif keypoint not in asset.keypoints:
                errors.append(PlanError(
                    at,
                    f"asset {asset_name!r} has no keypoint {keypoint!r}; "
                    f"known: {sorted(asset.keypoints)}"))


def _check_markers(plan: ProblemScenePlan, built: dict, errors: list[PlanError]) -> None:
    for i, marker in enumerate(plan.markers):
        at = f"markers[{i}]"
        if not marker.at and marker.point is None:
            errors.append(PlanError(at, "marker needs 'at' (asset.keypoint) or 'point' [x, y]"))
        if marker.at:
            if "." not in marker.at:
                errors.append(PlanError(f"{at}.at", "marker 'at' must be an 'asset.keypoint' ref"))
            else:
                asset_name, _, keypoint = marker.at.partition(".")
                asset = built.get(asset_name)
                if asset is None:
                    errors.append(PlanError(f"{at}.at", f"unknown asset {asset_name!r}"))
                elif keypoint not in asset.keypoints:
                    errors.append(PlanError(
                        f"{at}.at",
                        f"asset {asset_name!r} has no keypoint {keypoint!r}; "
                        f"known: {sorted(asset.keypoints)}"))
        if marker.point is not None and len(marker.point) != 2:
            errors.append(PlanError(f"{at}.point", "point must be [x, y]"))
        if str(marker.placement) not in _LABEL_PLACEMENTS:
            errors.append(PlanError(
                f"{at}.placement",
                f"unknown placement {marker.placement!r}; options: {list(_LABEL_PLACEMENTS)}"))


def _check_vectors(plan: ProblemScenePlan, built: dict, errors: list[PlanError]) -> None:
    for i, vec in enumerate(plan.vectors):
        at = f"vectors[{i}]"
        if not vec.anchor:
            errors.append(PlanError(f"{at}.anchor", "vector anchor 'asset.keypoint' is required"))
            continue
        if "." not in vec.anchor:
            errors.append(PlanError(f"{at}.anchor", "anchor must be an 'asset.keypoint' ref"))
            continue
        asset_name, _, keypoint = vec.anchor.partition(".")
        asset = built.get(asset_name)
        if asset is None:
            errors.append(PlanError(f"{at}.anchor", f"unknown asset {asset_name!r}"))
        elif keypoint not in asset.keypoints:
            errors.append(PlanError(
                f"{at}.anchor",
                f"asset {asset_name!r} has no keypoint {keypoint!r}; "
                f"known: {sorted(asset.keypoints)}"))
        if vec.vector is None and vec.magnitude is None:
            errors.append(PlanError(at, "vector needs 'vector' components or a 'magnitude'"))
        if str(vec.placement) not in _LABEL_PLACEMENTS:
            errors.append(PlanError(
                f"{at}.placement",
                f"unknown placement {vec.placement!r}; options: {list(_LABEL_PLACEMENTS)}"))


def _check_paths(plan: ProblemScenePlan, errors: list[PlanError]) -> None:
    for i, path in enumerate(plan.paths):
        at = f"paths[{i}]"
        if path.kind not in ("polyline", "parabola"):
            errors.append(PlanError(
                f"{at}.kind",
                f"unknown path kind {path.kind!r}; options: ['polyline', 'parabola']"))
        if len(path.points) < 2:
            errors.append(PlanError(f"{at}.points", "a path needs at least two points"))
        for j, point in enumerate(path.points):
            if len(point) != 2:
                errors.append(PlanError(f"{at}.points[{j}]", "each point must be [x, y]"))


def _check_steps(plan: ProblemScenePlan, names: set[str], built: dict,
                 errors: list[PlanError]) -> None:
    valid = {k.value for k in StepKind}
    for i, step in enumerate(plan.steps):
        at = f"steps[{i}]"
        kind_value = step.kind.value if isinstance(step.kind, StepKind) else step.kind
        if kind_value not in valid:
            errors.append(PlanError(
                f"{at}.kind", f"unknown step kind {kind_value!r}; known: {sorted(valid)}"))
        if step.at < 0:
            errors.append(PlanError(f"{at}.at", f"time must be >= 0, got {step.at}"))
        if step.dt < 0:
            errors.append(PlanError(f"{at}.dt", f"dt must be >= 0, got {step.dt}"))
        for j, tf in enumerate(step.transforms):
            tat = f"{at}.transforms[{j}]"
            if tf.target not in names:
                errors.append(PlanError(f"{tat}.target",
                                        f"references unknown entity {tf.target!r}"))
            if tf.translate is None and tf.rotate_deg == 0.0:
                errors.append(PlanError(tat, "transform needs 'translate' or 'rotate_deg'"))
            if tf.about:
                a_name, _, kp = tf.about.partition(".")
                asset = built.get(a_name)
                if "." not in tf.about or asset is None:
                    errors.append(PlanError(f"{tat}.about", f"unknown pivot ref {tf.about!r}"))
                elif kp not in asset.keypoints:
                    errors.append(PlanError(
                        f"{tat}.about",
                        f"asset {a_name!r} has no keypoint {kp!r}; "
                        f"known: {sorted(asset.keypoints)}"))


def _value_error(hint: object, value: object) -> str | None:
    """A message if ``value`` cannot be a ``hint``, else ``None`` (best-effort)."""
    origin = get_origin(hint)
    if origin in (Union, types.UnionType):
        if value is None:
            return None
        options = [a for a in get_args(hint) if a is not _NONE_TYPE]
        if any(_value_error(opt, value) is None for opt in options):
            return None
        return f"expected one of {[_name(o) for o in options]}, got {type(value).__name__}"
    if origin in (list, tuple):
        if not isinstance(value, list):
            return f"expected a list, got {type(value).__name__}"
        args = get_args(hint)
        if origin is tuple and args and args[-1] is not Ellipsis and len(args) != len(value):
            return f"expected {len(args)} items, got {len(value)}"
        elem = args[0] if args else object
        return next((e for x in value if (e := _value_error(elem, x))), None)
    if origin is dict:
        if not isinstance(value, dict):
            return f"expected an object, got {type(value).__name__}"
        return None
    if isinstance(hint, type) and issubclass(hint, Enum):
        try:
            hint(value)
        except ValueError:
            return f"{value!r} is not a valid {hint.__name__}; options: {[m.value for m in hint]}"
        return None
    if hint in (float, int):
        ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        return None if ok else f"expected a number, got {type(value).__name__}"
    if hint is bool:
        if not isinstance(value, bool):
            return f"expected a boolean, got {type(value).__name__}"
        return None
    if hint is str:
        return None if isinstance(value, str) else f"expected a string, got {type(value).__name__}"
    return None


def _name(tp: object) -> str:
    return getattr(tp, "__name__", str(tp))
