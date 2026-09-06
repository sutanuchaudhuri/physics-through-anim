"""TDD spec for M14 -- reference frames / non-inertial overlays."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.reference_frames import (
    FrameKind,
    FrameState,
    PseudoForceKind,
    ReferenceFrame,
)

TDD = pytest.mark.xfail(reason="M14 not implemented (TDD spec)", strict=False)


def test_frame_and_pseudo_force_kinds() -> None:
    assert {k.value for k in FrameKind} == {"inertial", "translating", "rotating"}
    assert {k.value for k in PseudoForceKind} >= {"centrifugal", "coriolis", "euler"}
    assert FrameState().angular_velocity == 0.0
    assert ReferenceFrame().kind is FrameKind.INERTIAL


@TDD
def test_to_frame_translating() -> None:
    frame = ReferenceFrame(kind=FrameKind.TRANSLATING)
    frame.to_frame((1.0, 0.0), FrameState())
