"""Scene 0 -- Opening Hook.

Four *simulated* friction scenarios (manim-physics / pymunk contact friction,
not scripted `.shift`) shown at once, to make the opening introspection
question -- "which way does friction point?" -- concrete: the same contact
force points a different way in each case.

Per SKILL.md Rule 10 this is a `SpaceScene` (not `RollingLessonScene`): it
needs the manual `add_narration` copy (Rule 10.5), markers attached only
*after* `make_rigid_body` (Rule 10.2), and initial spins/velocities tuned so
every body stays inside its cell (Rule 10.3). Friction vectors use
`COLOR_FRICTION`/`force_arrow` (Rule 2) and carry symbol-only labels (Rule 9).

RENDER AT `--quality high` ONLY. pymunk steps at the frame dt, so at 15 fps
(low quality) the contacts mis-resolve and bodies misbehave without erroring
(Rule 10.7). The physics grounds use `stroke_width=4.05` so their pymunk
segment collision cushion is thin (~0.1), not ~2 units, which would otherwise
eject the bodies on the first step (Rule 10.6).
"""

import os
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    GRAY,
    ORANGE,
    UP,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Rectangle,
    Text,
    VGroup,
    Write,
)

from physics_through_anim.lessons.rolling_slipping.common import force_arrow
from physics_through_anim.sim import SpaceScene


class OpeningHook(SpaceScene):
    """Scene 0 -- Opening Hook, driven by real contact-friction simulation."""

    GRAVITY = (0, -9.8)

    def add_narration(self) -> None:
        # SpaceScene doesn't inherit RollingLessonScene, so narration needs its
        # own copy of this one-liner rather than silently doing nothing.
        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)

    def construct(self) -> None:
        self.add_narration()

        # --- Introspection question ---------------------------------------
        question = Text("Which way does friction point?", font_size=38, weight="BOLD")
        self.play(Write(question))
        self.wait(1.0)
        self.play(FadeOut(question))

        # --- Static stage: dividers, four grounds, four case numerals -----
        # NOTE: manim-physics turns a Line static body into a pymunk segment
        # whose collision radius is (stroke_width - 3.95). Keep the *physics*
        # grounds near stroke_width 4 so that cushion is ~0.1, not ~2 units --
        # a fat cushion embeds the bodies and ejects them on the first step.
        v_divider = Line([0, 2.7, 0], [0, -2.7, 0], color=GRAY, stroke_width=2)
        h_divider = Line([-6.9, 0, 0], [6.9, 0, 0], color=GRAY, stroke_width=2)

        tl_ground = Line([-6.8, 1.0, 0], [-0.5, 1.0, 0], color=GRAY, stroke_width=4.05)
        tr_ground = Line([0.5, 1.0, 0], [6.8, 1.0, 0], color=GRAY, stroke_width=4.05)
        bl_ground = Line([-6.8, -1.0, 0], [-0.5, -1.0, 0], color=GRAY, stroke_width=4.05)
        br_incline = Line([0.8, -0.6, 0], [6.6, -2.2, 0], color=GRAY, stroke_width=4.05)

        numerals = VGroup(
            Text("I", font_size=26, color=GRAY).move_to([-6.5, 2.4, 0]),
            Text("II", font_size=26, color=GRAY).move_to([6.4, 2.4, 0]),
            Text("III", font_size=26, color=GRAY).move_to([-6.4, -0.25, 0]),
            Text("IV", font_size=26, color=GRAY).move_to([6.4, -0.25, 0]),
        )
        stage = VGroup(v_divider, h_divider, tl_ground, tr_ground, bl_ground, br_incline, numerals)
        self.play(FadeIn(stage))

        for ground in (tl_ground, tr_ground, bl_ground, br_incline):
            self.make_static_body(ground, friction=0.9, elasticity=0.05)

        # --- Friction-direction arrows (drawn before release) -------------
        # I: block slides right  -> f_k backward (left)
        f1 = force_arrow([-5.6, 1.0, 0], [-6.3, 1.0, 0], "f_k")
        # II: spun-up disk moves right -> f_k forward (right)
        f2 = force_arrow([1.7, 1.0, 0], [2.4, 1.0, 0], "f_k")
        # III: skidding disk moves right -> f_k backward (left)
        f3 = force_arrow([-5.7, -1.0, 0], [-6.4, -1.0, 0], "f_k")
        # IV: disk rolls down-slope -> f_s up the slope
        up_slope = np.array([-0.964, 0.266, 0.0])
        contact_iv = np.array([1.9, -0.904, 0.0])
        f4 = force_arrow(contact_iv, contact_iv + 0.7 * up_slope, "f_s")
        arrows = VGroup(f1, f2, f3, f4)
        self.play(FadeIn(arrows))
        self.wait(0.7)

        # --- Four rigid bodies, released simultaneously -------------------
        # Each starts with a small gap above its ground (top of the ~0.1
        # collision cushion) so it settles by falling a hair, never embedded.
        block = Rectangle(width=0.8, height=0.34, color="#4C6EF5", fill_opacity=0.35)
        block.move_to([-5.6, 1.42, 0])

        disk_ii = Circle(radius=0.42, color="#4C6EF5", stroke_width=6).move_to([1.7, 1.67, 0])
        disk_iii = Circle(radius=0.42, color="#4C6EF5", stroke_width=6).move_to([-5.7, -0.33, 0])
        disk_iv = Circle(radius=0.40, color="#4C6EF5", stroke_width=6).move_to([2.05, -0.37, 0])

        # Wire physics BEFORE attaching any visual-only marker (Rule 10.2).
        self.make_rigid_body(block, friction=0.5, elasticity=0.05)
        self.make_rigid_body(disk_ii, friction=0.9, elasticity=0.05)
        self.make_rigid_body(disk_iii, friction=0.5, elasticity=0.05)
        self.make_rigid_body(disk_iv, friction=0.95, elasticity=0.05)

        # Tuned so each body stays inside its cell over the sim window (Rule 10.3).
        block.body.velocity = (1.3, 0.0)  # I: pushed, then kinetic friction brakes it
        disk_ii.body.angular_velocity = -3.6  # II: pure spin, zero initial v_CM
        disk_iii.body.velocity = (1.4, 0.0)  # III: skids forward, no initial spin
        # IV: released from rest, gravity rolls it down the incline

        for disk in (disk_ii, disk_iii, disk_iv):
            disk.add(Dot(disk.get_top(), color=ORANGE, radius=0.06))  # marker rides along

        self.wait(1.4)

        # Freeze the simulation so the closing overlay can fade in cleanly (an
        # active pymunk updater rebuilds each body every frame and would
        # otherwise fight the added title/takeaway).
        for body in (block, disk_ii, disk_iii, disk_iv):
            body.clear_updaters()
        self.space.clear_updaters()

        # --- Title + takeaway ---------------------------------------------
        title = Text("ROLLING, SLIPPING AND FRICTION", font_size=30, weight="BOLD")
        title.to_edge(UP, buff=0.3)
        takeaway = MathTex(
            r"\text{Friction opposes }\textbf{slipping}\text{, not motion.}",
            font_size=30,
            color=ORANGE,
        )
        if takeaway.width > 12.5:
            takeaway.scale_to_fit_width(12.5)
        takeaway.to_edge(DOWN, buff=0.35)
        frame_note = Text("(ground frame)", font_size=18, color=GRAY)
        frame_note.next_to(takeaway, UP, buff=0.1)
        self.play(FadeIn(title), Write(takeaway), FadeIn(frame_note))
        self.wait(2)

