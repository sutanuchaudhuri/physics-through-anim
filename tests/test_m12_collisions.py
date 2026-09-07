"""Tests for M12 -- collisions / impulse / event sequences."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.events import EventKind
from physics_through_anim.physics.core.impact import (
    ImpactData,
    Impulse,
    MomentumFlux,
    PiecewiseTrajectory,
    center_of_percussion,
    impulse_response,
    perfectly_inelastic,
    reflect_velocity,
)
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.overlays.events import (
    EventCounter,
    collision,
    impulse_arrow,
    velocity_before_after,
)


def _seq_with_impacts(*times):
    from physics_through_anim.physics.core.events import EventSequence
    seq = EventSequence()
    for t in times:
        seq.add(collision("M", "m", t=t))
    return seq


def test_impact_data_carries_supplied_law() -> None:
    d = ImpactData(time=1.73, before={"m1.v": 4.2}, after={"m1.v": 1.4}, restitution=0.8)
    assert d.restitution == 0.8
    assert d.before["m1.v"] == 4.2
    assert EventCounter().kinds == (EventKind.IMPACT,)


def test_collision_builds_impact_event() -> None:
    ev = collision("M", "m", t=1.0, restitution=1.0)
    assert ev.kind is EventKind.IMPACT
    assert ev.participants == ("M", "m")
    assert ev.payload["restitution"] == 1.0


def test_event_counter_counts_impacts_up_to_t() -> None:
    counter = EventCounter(seq=_seq_with_impacts(0.5, 1.0, 2.0))
    assert counter.count_at(0.4) == 0
    assert counter.count_at(1.0) == 2
    assert counter.count_at(5.0) == 3
    assert EventCounter().count_at(9.0) == 0  # no seq -> 0


def test_event_counter_glyph_shows_count() -> None:
    glyph = EventCounter(seq=_seq_with_impacts(0.5, 1.0)).glyph(1.0)
    assert "2" in glyph.tex_string  # n = 2 impacts by t = 1.0


def test_impulse_arrow_scales_with_magnitude() -> None:
    body = Block(name="m")
    small = impulse_arrow(body, impulse=1.0, scale=0.5)[0]
    big = impulse_arrow(body, impulse=3.0, scale=0.5)[0]
    assert np.linalg.norm(big.get_vector()) > np.linalg.norm(small.get_vector())


def test_velocity_before_after_has_two_arrows() -> None:
    body = Block(name="m")
    group = velocity_before_after(body, v_before=2.0, v_after=-1.0)
    from manim import Arrow
    arrows = [m for m in group.submobjects if isinstance(m, Arrow)]
    assert len(arrows) == 2


# --- PiecewiseTrajectory: velocity STEPs, position continuous -------------


def _seg(x_ref, v, t_ref=0.0):
    def fn(t: float) -> SystemState:
        pose = Pose2D(position=(x_ref + v * (t - t_ref), 0.0))
        return SystemState(entities={"m": RigidKinematicState(pose=pose, velocity=(v, 0.0))})
    return AnalyticTrajectory(fn)


def test_piecewise_empty_returns_system_state() -> None:
    assert isinstance(PiecewiseTrajectory().state_at(0.5), SystemState)


def test_piecewise_velocity_steps_position_continuous() -> None:
    # Segment A: x = t (v=+1) until t=1; segment B starts at x=1 moving v=-1.
    traj = PiecewiseTrajectory()
    traj.add_segment(0.0, _seg(0.0, 1.0, 0.0))
    traj.add_segment(1.0, _seg(1.0, -1.0, 1.0))  # x(1)=1 matches -> position continuous
    v_before = traj.state_at(0.999).entities["m"].velocity[0]
    v_after = traj.state_at(1.0).entities["m"].velocity[0]
    assert v_before > 0 and v_after < 0  # velocity is discontinuous across the impact
    x_before = traj.state_at(0.999).entities["m"].pose.position[0]
    x_after = traj.state_at(1.0).entities["m"].pose.position[0]
    assert abs(x_after - x_before) < 1e-2  # position stays continuous


# --- reflection off a surface (ball on incline/wall) ---------------------


def test_reflect_elastic_off_floor() -> None:
    out = reflect_velocity((1.0, -1.0), (0.0, 1.0), e_n=1.0, e_t=1.0)
    assert np.allclose(out, (1.0, 1.0))  # normal flips, tangential kept


def test_reflect_restitution_and_friction() -> None:
    out = reflect_velocity((2.0, -1.0), (0.0, 1.0), e_n=0.5, e_t=0.8)
    assert np.allclose(out, (1.6, 0.5))  # v_t*0.8, -v_n*0.5


def test_reflect_off_incline_normal_is_unit_agnostic() -> None:
    n = (-np.sin(np.radians(30.0)), np.cos(np.radians(30.0)))
    out = reflect_velocity((1.0, -1.0), np.array(n) * 3.0, e_n=1.0, e_t=1.0)
    # elastic reflection preserves speed
    assert np.isclose(np.linalg.norm(out), np.linalg.norm((1.0, -1.0)))


# --- momentum flux / variable mass ---------------------------------------


def test_momentum_flux_force_is_rate_times_vrel() -> None:
    assert np.isclose(MomentumFlux(rate=2.0, relative_velocity=3.0).force(), 6.0)


def test_momentum_flux_wind_is_rho_a_v_squared() -> None:
    assert np.isclose(MomentumFlux.wind(density=1.2, area=2.0, speed=5.0).force(), 1.2 * 2.0 * 25.0)


def test_momentum_flux_onto_belt_uses_relative_speed() -> None:
    assert np.isclose(MomentumFlux.onto_belt(rate=4.0, v_belt=3.0, v_sand=1.0).force(), 8.0)


def test_momentum_flux_chain_and_rocket() -> None:
    assert np.isclose(MomentumFlux.chain_pileup(linear_density=2.0, speed=3.0).force(), 18.0)
    assert np.isclose(MomentumFlux.rocket(mass_rate=0.5, exhaust_speed=100.0).force(), 50.0)


# --- off-centre impulse / angular impulse --------------------------------


def test_central_impulse_is_pure_translation() -> None:
    resp = impulse_response(mass=2.0, inertia_cm=0.5, r_from_cm=(0.0, 0.0), J=(4.0, 0.0))
    assert np.allclose(resp.delta_v, (2.0, 0.0))
    assert resp.delta_omega == 0.0


def test_end_impulse_translates_and_spins() -> None:
    # Upward impulse at the left end of a horizontal rod: CM rises, rod spins CW.
    resp = impulse_response(mass=1.0, inertia_cm=0.75, r_from_cm=(-1.5, 0.0), J=(0.0, 2.0))
    assert np.allclose(resp.delta_v, (0.0, 2.0))
    assert resp.delta_omega < 0.0  # (r x J)_z = (-1.5)(2) = -3 -> clockwise
    assert np.isclose(resp.delta_omega, -3.0 / 0.75)


def test_center_of_percussion_of_end_pivoted_rod() -> None:
    # Uniform rod L=1: I_cm=1/12, pivot at end so d=L/2 -> CoP at 2L/3.
    q = center_of_percussion(inertia_cm=1.0 / 12.0, mass=1.0, pivot_to_cm=0.5)
    assert np.isclose(q, 2.0 / 3.0)


def test_ballistic_pendulum_capture() -> None:
    # A light fast bullet embeds in a heavy bob -> slow common velocity.
    v = perfectly_inelastic((0.01, 300.0), (2.0, 0.0))
    assert np.isclose(v, (0.01 * 300.0) / (0.01 + 2.0))


def test_impulse_dataclass_vector_and_magnitude() -> None:
    imp = Impulse(jx=3.0, jy=4.0, at=(1.0, 0.0))
    assert np.allclose(imp.vector, (3.0, 4.0))
    assert np.isclose(imp.magnitude, 5.0)
