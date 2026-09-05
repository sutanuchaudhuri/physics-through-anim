"""Bonus scene: friction converts pure spin into rolling, simulated with the
manim-physics plugin (pymunk) instead of hand-scripted kinematics.

See SKILL.md Rule 10 for why this uses SpaceScene directly instead of
RollingLessonScene, and for the make_rigid_body ordering gotcha this scene
exists to demonstrate correctly.
"""

import os
from pathlib import Path

from manim import BLUE, DOWN, GRAY, ORANGE, UP, Circle, Dot, Line, MathTex, Text, Write

from physics_through_anim.sim import SpaceScene


class PymunkSpinToRoll(SpaceScene):
    """A disk spinning in place, with zero initial translation, is dropped
    onto rough ground. Friction alone (pymunk contact physics, not a
    scripted animation) converts the spin into forward rolling."""

    GRAVITY = (0, -9.8)

    def add_narration(self) -> None:
        # SpaceScene doesn't inherit RollingLessonScene, so narration needs
        # its own copy of this one-liner rather than silently doing nothing.
        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)

    def construct(self) -> None:
        self.add_narration()
        title = Text("Bonus: Friction Converts Spin Into Rolling", font_size=30, weight="BOLD")
        title.to_edge(UP, buff=0.3)
        subtitle = Text(
            "Simulated with manim-physics (pymunk contact friction), not scripted",
            font_size=20,
            color=GRAY,
        ).next_to(title, DOWN, buff=0.1)
        self.add(title, subtitle)

        ground = Line([-5.5, -2, 0], [5.5, -2, 0], color=GRAY, stroke_width=6)
        self.add(ground)
        self.make_static_body(ground, friction=0.9, elasticity=0.1)

        disk = Circle(radius=0.9, color=BLUE, stroke_width=6)
        disk.move_to([-4.6, -2 + 0.9, 0])
        # Wire the disk into pymunk BEFORE attaching any visual-only marker:
        # make_rigid_body turns every shape-having family member into its own
        # independent rigid body, so a marker added first would fly off on
        # its own instead of spinning with the disk.
        self.make_rigid_body(disk, friction=0.9, elasticity=0.1)
        # Final rolling speed is v_f = omega_0 * R / 3 (angular momentum about
        # the contact point is conserved for a solid disk with zero initial
        # v_CM). Keep omega_0 small enough that v_f * wait_time stays inside
        # the visible frame -- a naive |omega_0| ~ 9 sends the disk off-screen
        # in under 4 seconds at this radius.
        disk.body.angular_velocity = -4.0  # spinning clockwise, zero initial v_CM

        marker = Dot(disk.get_top(), color=ORANGE, radius=0.07)
        disk.add(marker)  # now a submobject: rotates and moves with the disk

        self.wait(6)

        note = MathTex(
            r"\text{Friction alone reached } v_{\rm CM}=\omega R",
            font_size=30,
        ).to_edge(DOWN, buff=0.35)
        self.play(Write(note))
        self.wait(2)
