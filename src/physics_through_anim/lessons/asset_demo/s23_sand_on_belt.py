"""Scene 23 -- momentum flux: sand onto a moving conveyor belt.

Sand pours onto a belt moving at ``v_belt``; each grain must be sped up to the
belt speed, so the belt (its motor) supplies a forward force
``F = (dm/dt)(v_belt - v_sand)`` -- a supplied ``MomentumFlux`` the library renders
as a force arrow. It also shows the annotation tools: a **static** point marker P
at the impact with a "Look at point P" callout, and a **dynamic** marker Q that
rides a grain along the belt (fades in, tracks, fades out).
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    UP,
    WHITE,
    Arrow,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Text,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.impact import MomentumFlux
from physics_through_anim.physics.mechanics import Conveyor
from physics_through_anim.physics.mechanics.palette import COLOR_APPLIED
from physics_through_anim.physics.overlays.annotations import callout, point_marker

BELT_Y = -1.6
V_BELT = 1.3
RATE = 0.8  # dm/dt of the falling sand
IMPACT_X = -1.2
SAND = "#D9C089"


class SandOnBelt(AssetDemoScene):
    """Belt momentum flux force + static point P and dynamic point Q markers."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("23", "Sand on a moving belt", "momentum flux F = (dm/dt) v")
        self.play(FadeIn(header))

        belt = Conveyor(y=BELT_Y, half_width=4.8, belt_speed=V_BELT, direction=1, chevrons=14)
        impact = np.array([IMPACT_X, BELT_Y, 0.0])

        # A hopper + a dotted stream of sand falling to the impact point.
        spout = np.array([IMPACT_X, BELT_Y + 2.3, 0.0])
        hopper = VGroup(
            Line(spout + [-0.7, 0.5, 0], spout + [-0.12, 0.0, 0], color=SAND, stroke_width=4),
            Line(spout + [0.7, 0.5, 0], spout + [0.12, 0.0, 0], color=SAND, stroke_width=4),
        )
        stream = VGroup(*[Dot([IMPACT_X, y, 0.0], color=SAND, radius=0.05)
                          for y in np.linspace(spout[1] - 0.1, BELT_Y + 0.05, 9)])
        self.add(belt.mobject)
        self.play(FadeIn(belt.mobject), FadeIn(hopper), FadeIn(stream))

        # The supplied momentum-flux force the motor must add to keep v_belt.
        flux = MomentumFlux.onto_belt(rate=RATE, v_belt=V_BELT, v_sand=0.0)
        f_arrow = Arrow(impact, impact + np.array([0.7 + flux.force(), 0.0, 0.0]),
                        buff=0.0, color=COLOR_APPLIED, stroke_width=6)
        f_label = MathTex(r"F = \dot{m}\,v_{belt}", color=COLOR_APPLIED, font_size=32)
        f_label.next_to(f_arrow, UP, buff=0.12)

        # STATIC point of interest P at the impact, with a "Look at point P" callout.
        marker_p = point_marker(impact, "P", label_direction=DOWN)
        call_p = callout(impact, "Look at point P", offset=(-1.7, 1.1))
        self.play(FadeIn(marker_p), FadeIn(call_p))
        self.play(FadeIn(f_arrow), FadeIn(f_label))

        cap = Text("the belt speeds each grain up to v_belt -> forward force here",
                   font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap))

        # Scroll the belt chevrons while we watch.
        wrap = 2 * belt.half_width / belt.chevrons
        travelled = 0.0

        def scroll(mob, dt):
            nonlocal travelled
            step = belt.direction * belt.belt_speed * dt
            travelled += step
            mob.shift([step, 0.0, 0.0])
            if abs(travelled) > wrap:
                mob.shift([-np.sign(step) * wrap, 0.0, 0.0])
                travelled = 0.0

        belt._chevrons.add_updater(scroll)

        # DYNAMIC point of interest Q: a marked grain riding the belt.
        clock = ValueTracker(0.0)
        grain = Dot(impact, color=SAND, radius=0.09)
        marker_q = point_marker(impact, "Q", color="#FF922B", label_direction=UP)

        def ride(_m):
            x = IMPACT_X + belt.belt_speed * clock.get_value()
            grain.move_to([x, BELT_Y + 0.09, 0.0])
            marker_q.submobjects[0].move_to([x, BELT_Y + 0.09, 0.0])
            marker_q.submobjects[1].next_to(marker_q.submobjects[0], UP, buff=0.14)

        cap2 = Text("a marked grain Q rides along -- a dynamic point of interest",
                    font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(grain), FadeIn(marker_q), FadeOut(call_p), cap.animate.become(cap2))
        grain.add_updater(ride)
        self.play(clock.animate.set_value(3.0), run_time=2.6)
        grain.clear_updaters()
        self.play(FadeOut(grain), FadeOut(marker_q))

        belt._chevrons.clear_updaters()
        self.wait(0.3)
        self.finish_with_narration()
