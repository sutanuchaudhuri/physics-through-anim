"""Tests for M10 -- springs / dampers + constitutive laws."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.springs import (
    Damper,
    HookeLaw,
    LinearDamperLaw,
    LinearSpring,
    Spring,
    TorsionalHookeLaw,
    TorsionSpring,
    parallel_springs,
    series_springs,
)


def test_spring_alias_and_defaults() -> None:
    assert Spring is LinearSpring
    assert LinearSpring(natural_length=2.0).natural_length == 2.0
    assert HookeLaw(k=3.0).k == 3.0


def test_build_keypoints_at_endpoints() -> None:
    s = LinearSpring(from_point=(-1.0, 0.0), to_point=(2.0, 0.0))
    assert np.allclose(s.keypoint("A")[:2], (-1.0, 0.0))
    assert np.allclose(s.keypoint("B")[:2], (2.0, 0.0))
    assert s.mobject[0].get_num_points() > 0  # coil is one drawn VMobject
    assert np.isclose(s.current_length, 3.0)


def test_deformation_sign_stretch_and_compress() -> None:
    stretched = LinearSpring(from_point=(0.0, 0.0), to_point=(1.5, 0.0), natural_length=1.0)
    assert stretched.deformation() > 0
    assert stretched.extension() == stretched.deformation()
    assert stretched.compression() == 0.0
    compressed = LinearSpring(from_point=(0.0, 0.0), to_point=(0.6, 0.0), natural_length=1.0)
    assert compressed.deformation() < 0
    assert np.isclose(compressed.compression(), 0.4)


def test_set_endpoints_updates_length() -> None:
    s = LinearSpring(from_point=(0.0, 0.0), to_point=(1.0, 0.0), natural_length=1.0)
    s.set_endpoints((0.0, 0.0), (2.5, 0.0))
    assert np.isclose(s.current_length, 2.5)
    assert s.deformation() > 0


def test_coil_vertex_count_scales_with_coils() -> None:
    few = LinearSpring(coils=4).mobject[0].get_num_points()
    many = LinearSpring(coils=12).mobject[0].get_num_points()
    assert many > few


def test_spring_force_direction_along_axis() -> None:
    body = Block(name="m", mass=1.0)
    # Stretched spring: restoring force on body at B pulls inward (toward A, -x).
    s = LinearSpring(from_point=(-2.0, 0.0), to_point=(0.0, 0.0), natural_length=1.0)
    spec = s.spring_force_on(body, at="CM")
    assert spec.kind is ForceKind.SPRING
    assert spec.direction[0] < 0 and abs(spec.direction[1]) < 1e-9
    assert body.forces[-1].kind is ForceKind.SPRING


def test_hooke_law_force() -> None:
    assert np.isclose(HookeLaw(k=2.0).force(3.0), -6.0)


def test_damper_law_and_force_opposes_velocity() -> None:
    assert np.isclose(LinearDamperLaw(c=2.0).force(1.5), -3.0)
    body = Block(name="m")
    d = Damper(from_point=(0.0, 0.0), to_point=(1.0, 0.0))
    spec = d.damping_force_on(body, at="CM", v_rel=(1.0, 0.0))
    assert spec.kind is ForceKind.DAMPING
    assert spec.direction[0] < 0  # opposes +x relative velocity


def test_torsion_spring_pivot_and_hint_and_law() -> None:
    t = TorsionSpring(at=(0.5, 0.5))
    assert np.allclose(t.keypoint("H")[:2], (0.5, 0.5))
    assert t.torque_hint().get_num_points() > 0
    assert np.isclose(TorsionalHookeLaw(kappa=2.0).torque(0.5), -1.0)


# --- Series / parallel combinations --------------------------------------


def test_series_effective_stiffness_and_length() -> None:
    group = series_springs(
        [LinearSpring(natural_length=1.0, k=2.0), LinearSpring(natural_length=1.0, k=2.0)],
        from_point=(0.0, 0.0), to_point=(4.0, 0.0),
    )
    assert np.isclose(group.k_eff, 1.0)  # 1/k = 1/2 + 1/2
    assert np.isclose(group.natural_length, 2.0)  # lengths add in series
    assert np.allclose(group.keypoint("A")[:2], (0.0, 0.0))
    assert np.allclose(group.keypoint("B")[:2], (4.0, 0.0))


def test_series_has_junction_connector() -> None:
    two = series_springs([LinearSpring(k=1.0), LinearSpring(k=1.0)])
    three = series_springs([LinearSpring(k=1.0), LinearSpring(k=1.0), LinearSpring(k=1.0)])
    assert len(three.mobject) > len(two.mobject)  # extra coil + junction dot


def test_parallel_effective_stiffness() -> None:
    group = parallel_springs(
        [LinearSpring(k=3.0), LinearSpring(k=5.0)],
        from_point=(0.0, 0.0), to_point=(2.0, 0.0),
    )
    assert np.isclose(group.k_eff, 8.0)  # k = k1 + k2
    assert np.isclose(group.current_length, 2.0)


def test_combination_stiffness_none_without_k() -> None:
    group = series_springs([LinearSpring(), LinearSpring(k=2.0)])
    assert group.k_eff is None  # a member without k -> no effective stiffness
