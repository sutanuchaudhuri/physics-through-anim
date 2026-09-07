"""M4 spec -- connectors (rope/hinge), typed constraints, assembly wiring."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.assembly import Assembly
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.circular import Pulley
from physics_through_anim.physics.mechanics.connectors import Cable, Hinge, Rope
from physics_through_anim.physics.mechanics.constraints import (
    ContactLockConstraint,
    FixedAxleConstraint,
    RopeLengthConstraint,
)
from physics_through_anim.physics.mechanics.environment import Ceiling
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.palette import (
    COLOR_REACTION,
    COLOR_TENSION,
    FORCE_COLORS,
)


def test_typed_constraints_are_inspectable() -> None:
    assert RopeLengthConstraint(length=2.0).length == 2.0
    assert FixedAxleConstraint(at="pulley.axle", to="ceiling.H").active is True
    assert ContactLockConstraint(participants=("m1", "m2")).gap == 0.0


def test_rope_defaults_and_cable_subclass() -> None:
    r = Rope(from_ref="pulley.A", to_ref="m1.top", tension_label="T_A")
    assert r.slips is False
    assert isinstance(Cable(), Rope)


def test_rope_keypoints_and_set_endpoints() -> None:
    r = Rope(from_point=(0.0, 0.0), to_point=(0.0, -2.0))
    np.testing.assert_allclose(r.keypoint("mid"), [0.0, -1.0, 0.0])
    r.set_endpoints(np.array([1.0, 1.0, 0.0]), np.array([1.0, -1.0, 0.0]))
    np.testing.assert_allclose(r.keypoint("from"), [1.0, 1.0, 0.0])
    np.testing.assert_allclose(r.keypoint("mid"), [1.0, 0.0, 0.0])


def test_rope_tension_on_declares_tension_toward_point() -> None:
    block = Block(position=(0.0, 0.0), width=0.8, label="m")
    rope = Rope(tension_label="T_A")
    rope.tension_on(block, at="top", toward=(0.0, 3.0))  # pull straight up
    tensions = [f for f in block.forces if f.kind is ForceKind.TENSION]
    assert len(tensions) == 1
    assert tensions[0].label == "T_A"
    np.testing.assert_allclose(tensions[0].direction, (0.0, 1.0), atol=1e-9)


def test_hinge_registers_H_and_declares_reaction() -> None:
    hinge = Hinge(at=(-2.0, 1.0))
    np.testing.assert_allclose(hinge.keypoint("H"), [-2.0, 1.0, 0.0])
    rod = Block(position=(-2.0, 1.0), width=0.6)
    rod.set_keypoint("A", rod.keypoint("CM"))
    hinge.reaction_on(rod, at="A", label="R")
    reactions = [f for f in rod.forces if f.kind is ForceKind.REACTION]
    assert len(reactions) == 1 and reactions[0].at == "A"


def test_assembly_resolve_and_connect_a_rope() -> None:
    a = Assembly()
    ceiling = Ceiling(y=3.0)
    pulley = Pulley(center=(0.0, 2.0), radius=0.5, rope_angles={"A": 210.0, "B": 330.0})
    a.add(ceiling)
    a.hang(pulley, from_ceiling=ceiling)
    rim_a = a.resolve("pulley.A")
    mass = Block(name="m_1", position=(rim_a[0], rim_a[1] - 1.5), width=0.7, label="m_1")
    a.add(mass)
    rope = Rope(from_ref="pulley.A", to_ref="m_1.top", tension_label="T_A")
    a.connect(rope)
    np.testing.assert_allclose(rope.keypoint("from"), a.resolve("pulley.A"), atol=1e-9)
    np.testing.assert_allclose(rope.keypoint("to"), a.resolve("m_1.top"), atol=1e-9)


def test_slip_marks_present_only_when_slipping() -> None:
    plain = Rope(from_point=(0.0, 0.0), to_point=(2.0, 0.0), slips=False)
    slipping = Rope(from_point=(0.0, 0.0), to_point=(2.0, 0.0), slips=True)
    assert len(slipping.mobject.submobjects) > len(plain.mobject.submobjects)


def test_tension_and_reaction_colours() -> None:
    assert FORCE_COLORS[ForceKind.TENSION] == COLOR_TENSION
    assert FORCE_COLORS[ForceKind.REACTION] == COLOR_REACTION

