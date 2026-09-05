"""3D scene support for the physics-through-anim framework.

The lesson base classes (`RollingLessonScene`, `RodLessonScene`) extend
`MovingCameraScene`, which is inherently 2D (its `zoom_to`/`zoom_out` drive a
flat camera frame). 3D needs manim's separate `ThreeDScene` camera, so 3D
scenes use `ThreeDLessonScene` here instead -- the same relationship a
`SpaceScene` (Rule 10) has to the 2D base classes.

What this module gives a 3D scene:

- `ThreeDLessonScene` -- `ThreeDScene` + the framework's narration hook and the
  `SceneEventLogMixin` transcript logging (Rule 14), plus convenience camera
  helpers (`standard_view`, `orbit`/`stop_orbit`, `hud`).
- `physics_axes_3d()` -- ready-made `ThreeDAxes` with sane physics ranges.
- `lift_to_3d()` -- the "transform from 2D to 3D" move: start looking straight
  down (the scene reads as flat), then tilt the camera into an isometric view
  while a flat mobject morphs into its solid counterpart.

Standard camera angles here follow manim's convention: `phi` is the polar
angle from the +z axis (0 = straight top-down, ~70 deg = a raised isometric
look) and `theta` is the azimuth.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from manim import (
    DEGREES,
    Mobject,
    ReplacementTransform,
    ThreeDAxes,
    ThreeDScene,
)

from physics_through_anim.scene_logging import SceneEventLogMixin

TOP_DOWN_PHI = 0.0  # camera looks straight down +z -> the scene renders as 2D
ISO_PHI = 70.0  # a raised "isometric-ish" 3D look
ISO_THETA = -45.0


class ThreeDLessonScene(SceneEventLogMixin, ThreeDScene):
    """Base class for 3D lesson scenes: narration + transcript logging + camera helpers.

    Subclasses set ``LESSON_NAME`` (as with the 2D base classes) so the Rule 14
    transcript lands under ``media/logs/<lesson_name>/``.
    """

    LESSON_NAME = "unknown_lesson"

    def add_narration(self) -> None:
        import os
        from pathlib import Path

        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)

    def finish_with_narration(self, min_tail: float = 0.75) -> None:
        """Hold the final frame until the narration ends (see SKILL.md Rule 18)."""
        from physics_through_anim.narration import hold_for_narration

        hold_for_narration(self, min_tail=min_tail)

    def standard_view(self, phi: float = ISO_PHI, theta: float = ISO_THETA) -> None:
        """Snap the camera to a fixed 3D orientation (degrees)."""
        self.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES)

    def top_down_view(self) -> None:
        """Look straight down +z so the scene reads as flat 2D (for lift_to_3d)."""
        self.set_camera_orientation(phi=TOP_DOWN_PHI, theta=-90 * DEGREES)

    def orbit(self, rate: float = 0.15, about: str = "theta") -> None:
        """Start a slow ambient camera rotation; pair with stop_orbit()."""
        self.begin_ambient_camera_rotation(rate=rate, about=about)

    def stop_orbit(self, about: str = "theta") -> None:
        self.stop_ambient_camera_rotation(about=about)

    def hud(self, *mobs: Mobject) -> None:
        """Pin titles/captions to the screen so they don't tilt with the 3D camera.

        Any full-sentence caption or scene title in a 3D scene MUST go through
        here (or it rotates with the world and becomes unreadable) -- the
        bottom-band text rule (Rule 9) still applies, it just needs this call.
        """
        self.add_fixed_in_frame_mobjects(*mobs)

    def play_subscenes(self, subscenes, mode: str = "sequential", **kwargs: Any):
        """Play SubScene segments; see physics_through_anim.subscenes.play_subscenes."""
        from physics_through_anim.subscenes import play_subscenes

        return play_subscenes(self, subscenes, mode, **kwargs)


def physics_axes_3d(
    x_range: Sequence[float] = (-4, 4, 1),
    y_range: Sequence[float] = (-4, 4, 1),
    z_range: Sequence[float] = (0, 4, 1),
    length: float = 6.0,
) -> ThreeDAxes:
    """A ThreeDAxes sized for a physics diagram (z defaults to up/positive-only)."""
    return ThreeDAxes(
        x_range=list(x_range),
        y_range=list(y_range),
        z_range=list(z_range),
        x_length=length,
        y_length=length,
        z_length=length * 0.66,
    )


def lift_to_3d(
    scene: ThreeDScene,
    flat_mob: Mobject,
    solid_mob: Mobject,
    *,
    phi: float = ISO_PHI,
    theta: float = ISO_THETA,
    run_time: float = 2.5,
) -> Mobject:
    """Transform a 2D mobject into its 3D solid while tilting the camera up.

    Precondition: the scene is currently in a top-down view (phi=0, e.g. via
    ``ThreeDLessonScene.top_down_view()``), so the flat mobject reads as plain
    2D. This plays the camera tilt to (phi, theta) and the
    ``ReplacementTransform(flat_mob -> solid_mob)`` together, so the shape
    visibly gains depth as the viewpoint rises. Returns ``solid_mob``.
    """
    log = getattr(scene, "log_event", None)
    if callable(log):
        log("lift_to_3d", flat=type(flat_mob).__name__, solid=type(solid_mob).__name__)
    scene.move_camera(
        phi=phi * DEGREES,
        theta=theta * DEGREES,
        added_anims=[ReplacementTransform(flat_mob, solid_mob)],
        run_time=run_time,
    )
    return solid_mob
