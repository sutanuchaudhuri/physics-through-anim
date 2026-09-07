"""Pseudo-force overlays (Milestone M14).

Fictitious forces in a non-inertial frame, drawn **dashed** in a neutral colour so
a viewer never mistakes them for real interaction forces (the non-inertial
analogue of the FBD-vs-kinematics colour rule). Directions come from the supplied
``FrameState`` -- nothing is integrated.
"""

from __future__ import annotations

import numpy as np
from manim import DashedLine as _DashedLine
from manim import MathTex, VGroup

from physics_through_anim.physics.mechanics.reference_frames import FrameState, PseudoForceKind

COLOR_PSEUDO = "#CED4DA"  # washed-out grey: reads as "fictitious"

_SYMBOL = {
    PseudoForceKind.INERTIAL_PSEUDO: r"-m\,a_f",
    PseudoForceKind.CENTRIFUGAL: r"m\,\Omega^2 r",
    PseudoForceKind.CORIOLIS: r"-2m\,\Omega\times v",
    PseudoForceKind.EULER: r"-m\,\dot\Omega\times r",
}


def _v3(v) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    return a if a.shape[0] == 3 else np.array([a[0], a[1], 0.0])


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else np.array([0.0, 0.0, 0.0])


def _direction(kind, anchor, frame_state, center, v_rel) -> np.ndarray:
    omega = frame_state.angular_velocity
    if kind is PseudoForceKind.INERTIAL_PSEUDO:
        return -_unit(_v3(frame_state.acceleration))  # opposite the frame's acceleration
    if kind is PseudoForceKind.CENTRIFUGAL:
        return _unit(anchor - _v3(center))  # outward, away from the rotation centre
    if kind is PseudoForceKind.CORIOLIS:
        v = _v3(v_rel)  # -2 Omega z-hat x v_rel
        return _unit(2.0 * omega * np.array([v[1], -v[0], 0.0]))
    # EULER: -m d(Omega)/dt z-hat x r
    r = anchor - _v3(center)
    return _unit(frame_state.angular_acceleration * np.array([r[1], -r[0], 0.0]))


def pseudo_force_arrow(body, kind: PseudoForceKind, frame_state: FrameState, *,
                       center=(0.0, 0.0), v_rel=(0.0, 0.0), scale: float = 0.9) -> VGroup:
    """A dashed pseudo-force arrow at the body CM (fictitious force in the frame)."""
    anchor = _v3(body.keypoint("CM"))
    tip = anchor + _direction(kind, anchor, frame_state, center, v_rel) * scale
    arrow = _DashedLine(anchor, tip, color=COLOR_PSEUDO, stroke_width=4,
                        dash_length=0.1).add_tip(tip_length=0.2)
    label = MathTex(_SYMBOL[kind], color=COLOR_PSEUDO).scale(0.55).next_to(tip, buff=0.1)
    return VGroup(arrow, label)


def frame_badge(frame, frame_state: FrameState | None = None) -> VGroup:
    """The frame's observer icon + its ``S``/``S'`` label (Rules 1 & 6)."""
    return frame.icon(frame_state, scale=0.9)
