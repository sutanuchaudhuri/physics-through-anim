"""Reference frames + pseudo-forces (Milestone M14).

A frame consumes a supplied ``FrameState``; it **never integrates**. ``to_frame``
is a pure kinematic map built on ``core.frames.Frame2D``. Pseudo-forces are a
separate semantic class (drawn dashed, neutral colour) so a fictitious force is
never mistaken for a real one.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from physics_through_anim.physics.core.frames import Frame2D
from physics_through_anim.physics.core.pose import Pose2D, Vec2


class FrameKind(StrEnum):
    INERTIAL = "inertial"
    TRANSLATING = "translating"
    ROTATING = "rotating"


class PseudoForceKind(StrEnum):
    INERTIAL_PSEUDO = "inertial"
    CENTRIFUGAL = "centrifugal"
    CORIOLIS = "coriolis"
    EULER = "euler"


@dataclass(frozen=True)
class FrameState:
    """Supplied frame motion (never integrated)."""

    pose: Pose2D = Pose2D()
    velocity: Vec2 = (0.0, 0.0)
    angular_velocity: float = 0.0
    acceleration: Vec2 = (0.0, 0.0)
    angular_acceleration: float = 0.0


def _v2(p) -> np.ndarray:
    return np.asarray(p, dtype=float)[:2]


@dataclass
class ReferenceFrame:
    kind: FrameKind = FrameKind.INERTIAL
    label: str = "S"

    def to_frame(self, point: Vec2, frame_state: FrameState) -> np.ndarray:
        """World point -> frame-relative point (translation, plus rotation if ROTATING)."""
        if self.kind is FrameKind.ROTATING:
            return Frame2D(pose=frame_state.pose).to_local_point(point)[:2]
        return _v2(point) - _v2(frame_state.pose.position)  # inertial/translating: no rotation

    def is_inertial(self, frame_state: FrameState | None = None) -> bool:
        """True only if the frame neither accelerates nor rotates."""
        if self.kind is not FrameKind.INERTIAL:
            return False
        if frame_state is None:
            return True
        accel = any(abs(a) > 1e-9 for a in frame_state.acceleration)
        spin = abs(frame_state.angular_velocity) > 1e-9 or \
            abs(frame_state.angular_acceleration) > 1e-9
        return not (accel or spin)

    def icon(self, frame_state: FrameState | None = None, scale: float = 1.0):
        """A small frame glyph (Rule 1); a curved arrow is added when non-inertial."""
        from manim import WHITE, Arc, Line, MathTex, VGroup

        o = np.array([0.0, 0.0, 0.0])
        glyph = VGroup(
            Line(o, o + [0.5 * scale, 0.0, 0.0], color=WHITE, stroke_width=3),
            Line(o, o + [0.0, 0.5 * scale, 0.0], color=WHITE, stroke_width=3),
            MathTex(self.label, color=WHITE).scale(0.5 * scale).move_to(
                o + [0.62 * scale, 0.62 * scale, 0.0]),
        )
        if not self.is_inertial(frame_state):
            glyph.add(Arc(radius=0.32 * scale, start_angle=0.3, angle=2.0,
                          arc_center=o, color="#CED4DA", stroke_width=3).add_tip(tip_length=0.12))
        return glyph

