"""TDD spec for M9 -- overlays + graph binding."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.core.refs import QuantityRef
from physics_through_anim.physics.overlays.graphs import GraphBinding, QuantitySignal, TimeSignal
from physics_through_anim.physics.overlays.kinematics import rolling_velocity_field

TDD = pytest.mark.xfail(reason="M9 not implemented (TDD spec)", strict=False)


def test_time_signal_resolves_to_t() -> None:
    assert TimeSignal().resolve(0.7, None) == 0.7


def test_quantity_signal_holds_ref() -> None:
    q = QuantitySignal(ref=QuantityRef("body:disk:KE"))
    assert str(q.ref) == "body:disk:KE"
    assert GraphBinding().cursor is True


@TDD
def test_quantity_signal_resolves_from_observables() -> None:
    QuantitySignal(ref=QuantityRef("x")).resolve(0.0, None)


@TDD
def test_rolling_velocity_field_builds() -> None:
    rolling_velocity_field(object(), v_cm=1.0)
