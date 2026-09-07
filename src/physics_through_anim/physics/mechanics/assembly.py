"""Compose multiple assets, place bodies on supports, and build a combined FBD.

An ``Assembly`` groups sub-assets into one ``VGroup``, resolves simple relative
placement (drop a body so it rests on a floor), namespaces every keypoint by
asset name (``"block.CM"``), and can render the union of all members' free-body
diagrams.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from manim import VGroup

from physics_through_anim.physics.core.events import EventSequence
from physics_through_anim.physics.mechanics.base import PhysicsAsset, Ref
from physics_through_anim.physics.mechanics.contact import Contact
from physics_through_anim.physics.mechanics.geometry import (
    TOUCH_TOL,
    body_shape,
    clearance,
    corner_seat,
    seat_circle_on_surface,
)
from physics_through_anim.physics.mechanics.kinds import RelationKind
from physics_through_anim.physics.mechanics.supports import Floor, Wall

# Which RelationKind a typed constraint dataclass maps to (by class name).
_CONSTRAINT_KINDS: dict[str, RelationKind] = {
    "PinConstraint": RelationKind.PIN,
    "FixedPointConstraint": RelationKind.FIXED_POINT,
    "DistanceConstraint": RelationKind.DISTANCE,
    "RopeLengthConstraint": RelationKind.ROPE_LENGTH,
    "RollingConstraint": RelationKind.ROLLING,
    "PathConstraint": RelationKind.PATH,
    "SlotConstraint": RelationKind.SLOT,
    "FixedAxleConstraint": RelationKind.AXLE,
    "ContactLockConstraint": RelationKind.CONTACT_LOCK,
}


@dataclass(frozen=True)
class Relation:
    """A typed relationship between named assets, queryable on an ``Assembly``.

    ``participants`` are member asset names in a kind-defined order -- e.g.
    ``HANG -> (hung, support)``, ``ROPE -> (from, to)``, ``TOUCH -> (body, surface)``.
    Recorded automatically by ``hang``/``connect``/``add_relation``.
    """

    kind: RelationKind
    participants: tuple[str, ...]
    name: str | None = None



class Assembly:
    """A named collection of placed assets."""

    def __init__(self, *, contact_tol: float = TOUCH_TOL, check_penetration: bool = True) -> None:
        self.members: list[PhysicsAsset] = []
        self.mobject = VGroup()
        self.keypoints: dict[str, np.ndarray] = {}
        # bodies within this band of a wall are touching, not piercing:
        self.contact_tol = contact_tol
        self.check_penetration = check_penetration
        self.contacts: list[Contact] = []
        self.constraints_by_name: dict[str, object] = {}
        self.relations: list[Relation] = []
        self.timeline = EventSequence()

    def add(self, asset: PhysicsAsset, place_on: PhysicsAsset | None = None) -> PhysicsAsset:
        """Add an asset, optionally resting it on ``place_on`` (a Floor or two walls)."""
        if place_on is not None:
            self._place_on(asset, place_on)
        self.members.append(asset)
        self.mobject.add(asset.mobject)
        for key, point in asset.keypoints.items():
            self.keypoints[f"{asset.name}.{key}"] = point
        self._assert_no_penetration()
        return asset

    def _place_on(self, body: PhysicsAsset, support) -> None:
        """Seat ``body`` on a support surface (a Floor, an inclined/vertical wall,
        or two walls for a corner). Seating is the tangency (non-penetration)
        constraint at equality -- the body rests exactly on the surface."""
        if isinstance(support, (list, tuple)):
            self._seat_in_corner(body, support)
            return
        if isinstance(support, Floor):
            self._seat_on_floor(body, support)
            return
        if isinstance(support, Wall):
            self._seat_on_wall(body, support)
            return
        if hasattr(support, "top_y") and hasattr(support, "top_surface"):  # a Table top
            self._seat_on_floor(body, Floor(y=float(support.top_y)))
            return
        raise NotImplementedError(f"cannot place a body on '{type(support).__name__}'.")

    def _seat_on_floor(self, body: PhysicsAsset, support: Floor) -> None:
        if "bottom" not in body.keypoints:
            raise KeyError(f"'{body.name}' has no 'bottom' keypoint to rest on the floor.")
        gap = support.y - body.keypoint("bottom")[1]
        body.shift([0.0, gap])
        contact_x = body.keypoint("CM")[0]
        body.set_keypoint("contact", support.contact_under(contact_x))

    def _seat_on_wall(self, body: PhysicsAsset, wall: Wall) -> None:
        """Seat a body tangent to any wall (incline/ramp/vertical) -- the same
        no-pierce/always-in-contact constraint used for floors and corners."""
        cm = body.keypoint("CM")
        if hasattr(body, "radius"):
            seat, contact = seat_circle_on_surface(float(body.radius), wall, (cm[0], cm[1]))
            delta = seat - cm
            body.shift([float(delta[0]), float(delta[1])])
            body.set_keypoint("contact", contact)
            return
        # Polygon body (a block): rotate its base parallel to the surface, then seat
        # flush so its lowest corner touches -- min clearance driven to 0.
        if "bottom" not in body.keypoints:
            raise NotImplementedError(f"cannot seat '{body.name}' on '{wall.name}'.")
        tangent = wall.tangent()
        body.rotate(float(np.arctan2(tangent[1], tangent[0])))
        normal = np.asarray(wall.normal(), dtype=float)
        gap = clearance(body_shape(body), wall)  # min corner distance (flush => 0)
        body.shift([float(-gap * normal[0]), float(-gap * normal[1])])
        body.set_keypoint("contact", body.keypoint("bottom"))

    def _seat_in_corner(self, body: PhysicsAsset, walls) -> None:
        """Seat a round ``body`` tangent to two walls (the wedge/corner case)."""
        if len(walls) != 2:
            raise ValueError("corner placement needs exactly two walls.")
        if not hasattr(body, "radius"):
            raise NotImplementedError("corner seating is defined for round bodies (needs .radius).")
        seat = corner_seat(float(body.radius), walls[0], walls[1])
        delta = seat - body.keypoint("CM")
        body.shift([float(delta[0]), float(delta[1])])
        for i, wall in enumerate(walls):
            body.set_keypoint(f"contact_{i}", seat - float(body.radius) * wall.normal())

    def _assert_no_penetration(self) -> None:
        """No dynamic body may cross to a wall's solid side, beyond the contact band."""
        if not self.check_penetration:
            return
        walls = [m for m in self.members if isinstance(m, Wall)]
        for body in self.members:
            if isinstance(body, Wall) or "CM" not in getattr(body, "keypoints", {}):
                continue
            shape = body_shape(body)
            for wall in walls:
                gap = clearance(shape, wall)
                if gap < -self.contact_tol:  # within the band == touching (contact), not piercing
                    raise ValueError(
                        f"'{body.name}' penetrates '{wall.name}' (clearance {gap:+.4f}); "
                        "walls are impenetrable."
                    )

    def keypoint(self, key: str) -> np.ndarray:
        if key not in self.keypoints:
            raise KeyError(f"Unknown keypoint '{key}'. Known: {list(self.keypoints)}")
        return self.keypoints[key]

    def resolve(self, ref: str | Ref) -> np.ndarray:
        """Resolve a keypoint ref to a world point.

        Accepts a typed ``Ref`` from ``asset.port(key)`` or the equivalent
        namespaced string (e.g. ``'pulley.left'``).
        """
        return self.keypoint(str(ref))

    def body(self, name: str) -> PhysicsAsset:
        """The member asset named ``name`` (semantic query)."""
        for member in self.members:
            if member.name == name:
                return member
        raise KeyError(f"No asset named '{name}'. Known: {[m.name for m in self.members]}")

    def assets(self, kind: type | None = None) -> list:
        """Members, optionally filtered to a class (e.g. ``assets(CircularBody)``)."""
        return [m for m in self.members if kind is None or isinstance(m, kind)]

    def forces_on(self, name: str) -> list:
        """The declared ``ForceSpec``s on the named asset."""
        return list(self.body(name).forces)

    # --- relations + event timeline (M7) ---------------------------------

    def add_relation(self, relation, *, name: str | None = None):
        """Store a ``Contact`` or a typed constraint (relations, not drawables).

        Also records a typed ``Relation`` in ``self.relations`` so the topology is
        queryable via ``relations_of``/``relations_with``/``relations_between``.
        """
        if isinstance(relation, Contact):
            self.contacts.append(relation)
            self.record_relation(RelationKind.TOUCH, (relation.body, relation.surface))
        else:
            key = name or f"constraint_{len(self.constraints_by_name)}"
            self.constraints_by_name[key] = relation
            kind = _CONSTRAINT_KINDS.get(type(relation).__name__, RelationKind.CONSTRAINT)
            self.record_relation(kind, tuple(getattr(relation, "participants", ())), name=key)
        return relation

    def record_relation(self, kind: RelationKind, participants: tuple[str, ...],
                        *, name: str | None = None) -> Relation:
        """Append a typed ``Relation`` between named assets and return it."""
        rel = Relation(kind=kind, participants=participants, name=name)
        self.relations.append(rel)
        return rel

    def relations_of(self, kind: RelationKind) -> list[Relation]:
        """Every recorded relation of a given ``kind``."""
        return [r for r in self.relations if r.kind == kind]

    def relations_with(self, asset: str) -> list[Relation]:
        """Every relation that names ``asset`` as a participant."""
        return [r for r in self.relations if asset in r.participants]

    def relations_between(self, a: str, b: str) -> list[Relation]:
        """Every relation whose participants include both ``a`` and ``b``."""
        return [r for r in self.relations if a in r.participants and b in r.participants]

    @property
    def constraints(self) -> list:
        """The typed constraints, in insertion order."""
        return list(self.constraints_by_name.values())

    def at(self, t: float) -> None:
        """Apply the constraint set valid at time ``t`` (toggle per timeline events)."""
        for constraint in self.constraints_by_name.values():
            if hasattr(constraint, "active"):
                constraint.active = True
        for event in sorted(self.timeline.events, key=lambda e: e.time):
            if event.time > t:
                break
            if event.changes is None:
                continue
            for key in event.changes.deactivate:
                if key in self.constraints_by_name:
                    self.constraints_by_name[key].active = False
            for key in event.changes.activate:
                if key in self.constraints_by_name:
                    self.constraints_by_name[key].active = True

    def apply_states(self, mapping) -> None:
        """Apply a ``{name: kinematic state}`` mapping to member bodies (absolute)."""
        for name, state in mapping.items():
            self.body(name).apply_state(state)

    def animate_trajectory(self, scene, trajectory, t0: float, t1: float,
                           *, run_time: float = 5.0) -> None:
        """Drive member bodies from a ``Trajectory``: each frame samples
        ``state_at(t).entities`` and applies it (M1.6 absolute pose, no drift)."""
        from manim import ValueTracker

        scene.add(self.mobject)  # ensure the group is in the scene so its updater fires
        tracker = ValueTracker(t0)

        def update(_):
            entities = trajectory.state_at(tracker.get_value()).entities
            for name, state in entities.items():
                self.body(name).apply_state(state)

        self.mobject.add_updater(update)
        scene.play(tracker.animate.set_value(t1), run_time=run_time)
        self.mobject.clear_updaters()

    def connect(self, connector) -> PhysicsAsset:
        """Resolve a connector's ``from_ref``/``to_ref`` to world points and add it.

        Records a ``ROPE`` relation between the two endpoint assets (the part of
        each ref before the ``.``).
        """
        a = self.resolve(str(connector.from_ref))
        b = self.resolve(str(connector.to_ref))
        connector.set_endpoints(a, b)
        from_asset = str(connector.from_ref).split(".", 1)[0]
        to_asset = str(connector.to_ref).split(".", 1)[0]
        self.record_relation(RelationKind.ROPE, (from_asset, to_asset), name=connector.name)
        return self.add(connector)

    def hang(self, pulley, from_ceiling, *, drop: float = 0.8) -> PhysicsAsset:
        """Placement sugar: seat a pulley's axle ``drop`` below a ceiling anchor."""
        anchor = from_ceiling.anchor(pulley.keypoint("axle")[0])
        target = anchor - np.array([0.0, drop, 0.0])
        pulley.shift(target - pulley.keypoint("axle"))
        self.record_relation(RelationKind.HANG, (pulley.name, from_ceiling.name))
        return self.add(pulley)

    def fbd(self, include=None) -> VGroup:
        """Union of every member's free-body diagram."""
        group = VGroup()
        for asset in self.members:
            group.add(asset.fbd(include=include))
        return group
