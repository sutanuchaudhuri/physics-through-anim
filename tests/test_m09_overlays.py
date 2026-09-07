"""Tests for M9 -- overlays + graph binding (state-driven, render-independent)."""

from __future__ import annotations

import numpy as np
from manim import ManimColor

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.refs import QuantityRef
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.circular import Disk
from physics_through_anim.physics.mechanics.palette import COLOR_VELOCITY
from physics_through_anim.physics.overlays.graphs import (
    GraphBinding,
    QuantitySignal,
    TimeSignal,
)
from physics_through_anim.physics.overlays.kinematics import (
    rolling_velocity_field,
    trajectory_trail,
    velocity_vector,
)
from physics_through_anim.physics.overlays.momentum import (
    momentum_vector,
    system_com_marker,
)

# --- Signals -------------------------------------------------------------


def test_time_signal_resolves_to_t() -> None:
    assert TimeSignal().resolve(0.7, None) == 0.7


def test_quantity_signal_holds_ref() -> None:
    q = QuantitySignal(ref=QuantityRef("body:disk:KE"))
    assert str(q.ref) == "body:disk:KE"
    assert GraphBinding().cursor is True


def test_quantity_signal_resolves_scalar_from_observables() -> None:
    state = SystemState(observables={"N": 4.2})
    assert QuantitySignal(ref=QuantityRef("N")).resolve(0.0, state) == 4.2


def test_quantity_signal_resolves_callable_from_observables() -> None:
    state = SystemState(observables={"r": lambda t, s: 2.0 * t})
    assert QuantitySignal(ref=QuantityRef("r")).resolve(1.5, state) == 3.0


# --- GraphBinding --------------------------------------------------------


def _linear_traj():
    def fn(t: float) -> SystemState:
        body = RigidKinematicState(pose=Pose2D(position=(t, 0.0)))
        return SystemState(entities={"m": body}, observables={"y": 2.0 * t})
    return AnalyticTrajectory(fn)


def test_graph_binding_build_plots_and_places_cursor() -> None:
    graph = GraphBinding(
        x=TimeSignal(),
        y=QuantitySignal(ref=QuantityRef("y")),
        x_range=(0.0, 1.0),
        y_range=(0.0, 2.0),
    )
    group = graph.build(_linear_traj(), 0.0, 1.0, n=20)
    assert group is not None
    assert graph.curve is not None and graph.curve.get_num_points() > 0
    # Cursor starts at (x(s0), y(s0)) == axes.c2p(0, 0).
    assert np.allclose(graph.cursor_dot.get_center(), graph.axes.c2p(0.0, 0.0), atol=1e-6)


def test_graph_binding_bind_moves_cursor() -> None:
    from manim import ValueTracker

    graph = GraphBinding(x=TimeSignal(), y=QuantitySignal(ref=QuantityRef("y")),
                         x_range=(0.0, 1.0), y_range=(0.0, 2.0))
    graph.build(_linear_traj(), 0.0, 1.0, n=20)
    tracker = ValueTracker(0.0)
    graph.bind(None, tracker)
    tracker.set_value(1.0)
    graph.cursor_dot.update()
    assert np.allclose(graph.cursor_dot.get_center(), graph.axes.c2p(1.0, 2.0), atol=1e-6)


# --- Kinematics overlays -------------------------------------------------


def test_velocity_vector_is_proportional_and_coloured() -> None:
    body = Block(mass=1.0)
    body.build()
    body.apply_state(RigidKinematicState(pose=Pose2D(), velocity=(2.0, 0.0)))
    group = velocity_vector(body, scale=1.0)
    arrow = group[0]
    assert np.isclose(np.linalg.norm(arrow.get_vector()), 2.0, atol=1e-3)
    assert arrow.get_color().to_hex() == ManimColor(COLOR_VELOCITY).to_hex()
    assert np.allclose(arrow.get_start(), body.keypoint("CM"), atol=1e-6)


def test_rolling_velocity_field_perpendicular_and_zero_at_contact() -> None:
    disk = Disk(radius=1.0)
    disk.build()
    field = rolling_velocity_field(disk, v_cm=1.0, points=("top", "3", "9"))
    contact = disk.contact_point()
    for arrow in field.submobjects[:3]:
        rim = arrow.get_start()
        r = np.asarray(rim) - np.asarray(contact)
        v = arrow.get_vector()
        assert abs(float(np.dot(r[:2], v[:2]))) < 1e-6  # v perp to (point - contact)
    assert np.allclose(disk.point_velocity(contact, 1.0), 0.0, atol=1e-9)


def test_trajectory_trail_has_points() -> None:
    trail = trajectory_trail(Block(), _linear_traj(), 0.0, 1.0, n=30)
    assert trail.get_num_points() > 0


# --- Momentum overlays ---------------------------------------------------


def test_momentum_vector_scales_with_mass() -> None:
    body = Block(mass=3.0)
    body.build()
    body.apply_state(RigidKinematicState(pose=Pose2D(), velocity=(2.0, 0.0)))
    arrow = momentum_vector(body, scale=1.0)[0]
    assert np.isclose(np.linalg.norm(arrow.get_vector()), 6.0, atol=1e-3)


def test_system_com_marker_at_mass_weighted_mean() -> None:
    a = Block(mass=1.0)
    a.build()
    b = Block(mass=3.0)
    b.build()
    b.shift((4.0, 0.0))
    marker = system_com_marker([a, b])
    assert np.allclose(marker.get_center(), [3.0, 0.0, 0.0], atol=1e-6)
