"""Scene 13 -- M8 flagship: a cylinder reaches a table edge (probe A).

Three contact phases, all from the surface geometry + the M7 event timeline:
roll on the table top -> the contact switches to the sharp **edge** E -> the
normal reaches zero and the body **separates**, leaving as a spinning projectile.
The surface supplies the geometry; the trajectory supplies the timing.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    Arrow,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    Text,
    ValueTracker,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.events import Event, EventKind
from physics_through_anim.physics.mechanics import Assembly, Cylinder, Floor, Table, motion

GROUND_Y = -2.4
G = 8.0


class TableEdge(AssetDemoScene):
    """Roll on top -> pivot/switch at the edge -> separate -> projectile."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("13", "Cylinder at a table edge", "roll -> edge -> separate")
        self.play(FadeIn(header))

        a = Assembly()
        floor = Floor(y=GROUND_Y, half_width=6.0)
        table = Table(top_y=0.6, left=-4.5, right=1.6, leg_bottom=GROUND_Y)
        a.add(floor)
        a.add(table)
        edge = table.edge()

        radius = 0.5
        top_y = table.top_y
        cyl = Cylinder(name="cyl", radius=radius, position=(-3.2, top_y + radius), label="m")
        self.add(cyl.mobject)

        # Normal at the rolling contact (surface frame -> straight up on the flat top).
        def normal_arrow():
            p = cyl.keypoint("CM") - np.array([0.0, radius, 0.0])
            return Arrow(p, p + np.array([0.0, 0.8, 0.0]), buff=0, color=GREEN, stroke_width=5)

        n_arrow = normal_arrow()
        cap1 = Text("rolling on the top: N up at the contact under CM", font_size=21, color=WHITE)
        cap1.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(a.mobject), FadeIn(n_arrow), FadeIn(cap1))

        # --- Phase 1: roll to the edge -----------------------------------
        n_arrow.add_updater(lambda m: m.become(normal_arrow()))
        motion.roll_group(self, cyl, distance=table.right - (-3.2), run_time=2.4)
        n_arrow.clear_updaters()

        # --- Phase 2: contact switches to the sharp edge E ---------------
        a.timeline.add(Event(time=2.0, kind=EventKind.CONTACT_CHANGE,
                             participants=("cyl", "edge"), tag="edge_contact"))
        edge_dot = Dot(edge.point(), color=YELLOW, radius=0.07)
        cap2 = Text("at the edge: contact switches to E (a point)", font_size=21, color=YELLOW)
        cap2.to_edge(DOWN, buff=0.5)
        self.play(Flash(edge.point(), color=RED, flash_radius=0.4), FadeOut(n_arrow),
                  FadeIn(edge_dot), FadeOut(cap1), FadeIn(cap2))
        self.wait(0.3)

        # --- Phase 3: N -> 0, separation, spinning projectile off the edge ---
        a.timeline.add(Event(time=2.6, kind=EventKind.CONTACT_CHANGE,
                             participants=("cyl", "edge"), tag="separation"))
        cap3 = Text("N -> 0: separates -> spinning projectile", font_size=21, color=RED)
        cap3.to_edge(DOWN, buff=0.5)
        self.play(FadeOut(cap2), FadeIn(cap3))

        base = cyl.mobject.copy()
        cm0 = cyl.keypoint("CM").copy()
        vx = 2.4
        y_land = GROUND_Y + radius
        t_land = float((2.0 * (cm0[1] - y_land) / G) ** 0.5)
        s = ValueTracker(0.0)

        def fly(m):
            t = s.get_value()
            x = cm0[0] + vx * t
            y = cm0[1] - 0.5 * G * t * t
            m.become(base.copy())
            m.rotate(-(vx / radius) * t, about_point=cm0)
            m.shift([x - cm0[0], y - cm0[1], 0.0])
            cyl.keypoints["CM"] = np.array([x, y, 0.0])

        cyl.mobject.add_updater(fly)
        self.play(s.animate.set_value(t_land), run_time=1.4)
        cyl.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
