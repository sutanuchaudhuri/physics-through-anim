"""Scene 11 -- a slack string whose length is not fixed (slack -> taut).

A ``SlackString`` has a natural ``rest_length``. When its ends are close it hangs
**slack** (sags); as one end is pulled away it snaps **taut** (straight). The drawn
length follows the ends, not a fixed line.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, WHITE, YELLOW, Dot, FadeIn, FadeOut, Text, ValueTracker, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import SlackString

REST = 4.0
ANCHOR = np.array([-2.4, 1.2, 0.0])


class SlackStringDemo(AssetDemoScene):
    """A string sags when slack and snaps straight when stretched to its rest length."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("11", "Slack string", "length not fixed: sag -> taut")
        self.play(FadeIn(header))

        end0 = np.array([-0.6, 1.0, 0.0])
        string = SlackString(from_point=(ANCHOR[0], ANCHOR[1]),
                             to_point=(end0[0], end0[1]), rest_length=REST, stroke_width=5)
        pegs = VGroup(Dot(ANCHOR, color=YELLOW, radius=0.06), Dot(end0, color=YELLOW, radius=0.06))
        self.add(string.mobject)

        status = Text("slack: ends closer than the rest length", font_size=22, color=WHITE)
        status.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(string.mobject), FadeIn(pegs), FadeIn(status))
        self.wait(0.4)

        # Pull the free end away until the string goes taut (span reaches rest_length).
        s = ValueTracker(0.0)
        moving = pegs[1]

        def update(_):
            end = end0 + np.array([s.get_value(), -0.2 * s.get_value(), 0.0])
            string.set_endpoints(ANCHOR, end)
            moving.move_to(end)

        string.mobject.add_updater(update)
        self.play(s.animate.set_value(4.0), run_time=3.0)
        string.mobject.clear_updaters()

        taut = Text("taut: stretched to the rest length -> straight", font_size=22, color=YELLOW)
        taut.to_edge(DOWN, buff=0.5)
        self.play(FadeOut(status), FadeIn(taut))
        self.wait(0.4)
        self.finish_with_narration()
