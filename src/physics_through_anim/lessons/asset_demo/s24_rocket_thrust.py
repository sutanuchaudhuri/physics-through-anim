"""Scene 24 -- momentum flux: rocket thrust (emission-as-collision).

A rocket ejects exhaust downward at rate ``dm/dt`` and speed ``u``; by momentum
flux the reaction is an upward thrust ``F = u |dm/dt|`` -- a supplied
``MomentumFlux`` the library renders as the thrust arrow. A static point marker N
sits at the nozzle with a "Look at the nozzle N" callout.
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
    MathTex,
    Polygon,
    Rectangle,
    Text,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.impact import MomentumFlux
from physics_through_anim.physics.mechanics.palette import COLOR_APPLIED
from physics_through_anim.physics.overlays.annotations import callout, point_marker

MASS_RATE = 0.6
EXHAUST_U = 2.4
FLAME = "#FF922B"


class RocketThrust(AssetDemoScene):
    """Momentum-flux thrust arrow + a static nozzle point marker N."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("24", "Rocket thrust", "emission as a collision")
        self.play(FadeIn(header))

        body_cx, body_cy = 0.0, 0.2
        rocket = VGroup(
            Rectangle(width=0.7, height=1.6, color=WHITE, fill_color="#CED4DA",
                      fill_opacity=1.0).move_to([body_cx, body_cy, 0.0]),
            Polygon([body_cx - 0.35, body_cy + 0.8, 0], [body_cx + 0.35, body_cy + 0.8, 0],
                    [body_cx, body_cy + 1.4, 0], color=WHITE, fill_color="#FA5252",
                    fill_opacity=1.0),
            Polygon([body_cx - 0.35, body_cy - 0.8, 0], [body_cx - 0.6, body_cy - 1.2, 0],
                    [body_cx - 0.35, body_cy - 1.2, 0], color=WHITE, fill_color="#FA5252",
                    fill_opacity=1.0),
            Polygon([body_cx + 0.35, body_cy - 0.8, 0], [body_cx + 0.6, body_cy - 1.2, 0],
                    [body_cx + 0.35, body_cy - 1.2, 0], color=WHITE, fill_color="#FA5252",
                    fill_opacity=1.0),
        )
        nozzle = np.array([body_cx, body_cy - 0.8, 0.0])
        self.play(FadeIn(rocket))

        # Supplied thrust from the momentum flux of the exhaust.
        thrust = MomentumFlux.rocket(mass_rate=MASS_RATE, exhaust_speed=EXHAUST_U)
        thrust_arrow = Arrow(nozzle + [0.9, 0.4, 0.0],
                             nozzle + [0.9, 0.4 + 0.5 + thrust.force(), 0.0],
                             buff=0.0, color=COLOR_APPLIED, stroke_width=7)
        thrust_label = MathTex(r"F = u\,\dot{m}", color=COLOR_APPLIED, font_size=34)
        thrust_label.next_to(thrust_arrow, UP, buff=0.1)

        marker_n = point_marker(nozzle, "N", label_direction=np.array([-1.0, 0.0, 0.0]))
        call_n = callout(nozzle, "Look at the nozzle N", offset=(-2.0, -0.6))
        self.play(FadeIn(marker_n), FadeIn(call_n))

        # A downward exhaust plume of flame dots streaming from the nozzle.
        clock = ValueTracker(0.0)
        plume = VGroup(*[Dot(nozzle + [0.0, -0.15 * i, 0.0], color=FLAME,
                             radius=0.11 - 0.008 * i) for i in range(1, 9)])

        def stream(_m):
            t = clock.get_value()
            for i, d in enumerate(plume.submobjects, start=1):
                y = ((-0.15 * i - EXHAUST_U * t) % 1.4)
                d.move_to(nozzle + [0.0, -0.1 - y, 0.0])

        self.play(FadeIn(plume), FadeIn(thrust_arrow), FadeIn(thrust_label))
        cap = Text("exhaust leaves downward -> thrust pushes the rocket up",
                   font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap), FadeOut(call_n))

        plume.add_updater(stream)
        self.play(clock.animate.set_value(2.2), run_time=2.6)
        plume.clear_updaters()
        self.wait(0.3)
        self.finish_with_narration()
