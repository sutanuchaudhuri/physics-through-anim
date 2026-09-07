"""Tests for M14 -- reference frames / non-inertial overlays."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.reference_frames import (
    FrameKind,
    FrameState,
    PseudoForceKind,
    ReferenceFrame,
)
from physics_through_anim.physics.overlays.frames import (
    COLOR_PSEUDO,
    frame_badge,
    pseudo_force_arrow,
)


def test_frame_and_pseudo_force_kinds() -> None:
    assert {k.value for k in FrameKind} == {"inertial", "translating", "rotating"}
    assert {k.value for k in PseudoForceKind} >= {"centrifugal", "coriolis", "euler"}
    assert FrameState().angular_velocity == 0.0
    assert ReferenceFrame().kind is FrameKind.INERTIAL


def test_to_frame_translating_subtracts_origin() -> None:
    frame = ReferenceFrame(kind=FrameKind.TRANSLATING)
    fs = FrameState(pose=Pose2D(position=(2.0, 0.0)))
    assert np.allclose(frame.to_frame((5.0, 1.0), fs), (3.0, 1.0))


def test_inertial_frame_is_identity() -> None:
    frame = ReferenceFrame(kind=FrameKind.INERTIAL)
    assert np.allclose(frame.to_frame((5.0, 1.0), FrameState()), (5.0, 1.0))


def test_rotating_frame_rotates_by_minus_theta() -> None:
    frame = ReferenceFrame(kind=FrameKind.ROTATING)
    fs = FrameState(pose=Pose2D(position=(0.0, 0.0), angle=np.pi / 2))
    # a world point on +x becomes -y in a frame rotated +90 deg.
    assert np.allclose(frame.to_frame((1.0, 0.0), fs), (0.0, -1.0), atol=1e-9)


def test_is_inertial_detects_acceleration_and_spin() -> None:
    frame = ReferenceFrame(kind=FrameKind.INERTIAL)
    assert frame.is_inertial(FrameState()) is True
    assert frame.is_inertial(FrameState(acceleration=(1.0, 0.0))) is False
    assert frame.is_inertial(FrameState(angular_velocity=2.0)) is False
    assert ReferenceFrame(kind=FrameKind.TRANSLATING).is_inertial() is False


def test_pseudo_force_arrow_is_dashed_and_neutral() -> None:
    from manim import DashedLine, ManimColor

    body = Block(name="m")
    fs = FrameState(acceleration=(2.0, 0.0))
    group = pseudo_force_arrow(body, PseudoForceKind.INERTIAL_PSEUDO, fs)
    arrow = group[0]
    assert isinstance(arrow, DashedLine)
    assert arrow.get_color().to_hex() == ManimColor(COLOR_PSEUDO).to_hex()
    # -m a_f opposes the frame acceleration (+x) -> points -x.
    assert arrow.get_vector()[0] < 0


def test_centrifugal_outward_coriolis_perpendicular() -> None:
    body = Block(name="m", position=(2.0, 0.0))
    fs = FrameState(angular_velocity=1.5)
    cf = pseudo_force_arrow(body, PseudoForceKind.CENTRIFUGAL, fs, center=(0.0, 0.0))[0]
    assert cf.get_vector()[0] > 0  # outward from centre at origin toward +x body

    v_rel = (0.0, 1.0)
    cor = pseudo_force_arrow(body, PseudoForceKind.CORIOLIS, fs, v_rel=v_rel)[0]
    assert abs(float(np.dot(cor.get_vector()[:2], v_rel))) < 1e-6  # perpendicular to v_rel


def test_frame_badge_has_icon_and_label() -> None:
    badge = frame_badge(ReferenceFrame(kind=FrameKind.TRANSLATING, label="S'"))
    assert len(badge.submobjects) >= 3  # two axes + label (+ curved arrow when non-inertial)

