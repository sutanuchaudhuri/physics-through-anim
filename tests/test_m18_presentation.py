"""TDD spec for M18 -- presentation contract + declarative authoring."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.core.scene_data import (
    BindingSpec,
    EquationSpec,
    NamedState,
    QuantitySpec,
    ScenePhysicsData,
    TransitionSpec,
    VectorSpec,
)
from physics_through_anim.physics.core.state import SystemState
from physics_through_anim.physics.overlays.views import ViewSpec, energy_view

TDD = pytest.mark.xfail(reason="M18 not implemented (TDD spec)", strict=False)


def test_presentation_specs_are_data_only() -> None:
    q = QuantitySpec(symbol="v", value=4.2, unit="m/s", latex="v")
    assert q.value == 4.2
    v = VectorSpec(anchor="rod.B", role="velocity", perpendicular_to=("IC", "rod.B"))
    assert v.role == "velocity"
    assert EquationSpec(id="p", latex="p_i=p_f").highlight == {}
    assert BindingSpec(source="state.spring.extension", target="spring.length").target
    ns = NamedState(name="left")
    assert isinstance(ns.state, SystemState)
    assert TransitionSpec().motion == "interpolate"
    assert isinstance(ScenePhysicsData().states, dict)
    assert ViewSpec(name="spring_energy").show == ()


@TDD
def test_energy_view_renders_supplied_values() -> None:
    energy_view(ViewSpec(name="energy"), ScenePhysicsData())
