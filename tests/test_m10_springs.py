"""TDD spec for M10 -- springs / dampers + constitutive laws."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.springs import (
    HookeLaw,
    LinearSpring,
    Spring,
)

TDD = pytest.mark.xfail(reason="M10 not implemented (TDD spec)", strict=False)


def test_spring_alias_and_defaults() -> None:
    assert Spring is LinearSpring
    assert LinearSpring(natural_length=2.0).natural_length == 2.0
    assert HookeLaw(k=3.0).k == 3.0


@TDD
def test_deformation_sign() -> None:
    s = LinearSpring(natural_length=1.0, current_length=1.5)
    assert s.deformation() > 0  # stretched


@TDD
def test_hooke_law_force() -> None:
    assert abs(HookeLaw(k=2.0).force(3.0) - (-6.0)) < 1e-9
