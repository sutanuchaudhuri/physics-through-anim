"""TDD spec for M4 -- connectors + typed constraints."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.connectors import Cable, Rope
from physics_through_anim.physics.mechanics.constraints import (
    ContactLockConstraint,
    FixedAxleConstraint,
    RopeLengthConstraint,
)

TDD = pytest.mark.xfail(reason="M4 not implemented (TDD spec)", strict=False)


def test_typed_constraints_are_inspectable() -> None:
    assert RopeLengthConstraint(length=2.0).length == 2.0
    assert FixedAxleConstraint(at="pulley.axle", to="ceiling.H").active is True
    assert ContactLockConstraint(participants=("m1", "m2")).gap == 0.0


def test_rope_defaults() -> None:
    r = Rope(from_ref="pulley.A", to_ref="m1.top", tension_label="T_A")
    assert r.slips is False
    assert isinstance(Cable(), Rope)


@TDD
def test_rope_tension_on() -> None:
    Rope(from_ref="a", to_ref="b").tension_on("m1", at="m1.top", toward=(0.0, 1.0))
