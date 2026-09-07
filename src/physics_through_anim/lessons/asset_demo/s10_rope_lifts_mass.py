"""Scene 10 -- a rope over a pulley, pulled at 120 deg, lifts a mass (no slip).

The rope wraps the pulley: two tangent **contact points**, an **arc (arch)** on
the rim, and two straight free ends -- one pulled by a hand at ~120 deg, the other
hanging to a mass ``m``. Pulling the rope out rotates the wheel **without
slipping** (rim arc = rope paid) and the mass rises by the same length.
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
    Line,
    Text,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import Assembly, Block, Pulley, RopeOverPulley

CENTER = np.array([0.0, 1.9, 0.0])
RADIUS = 0.8


class RopeLiftsMass(AssetDemoScene):
    """A hand pulls a rope over a pulley at 120 deg; the mass on the other end rises."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("10", "Rope over a pulley", "pulled at 120 deg, lifts m")
        self.play(FadeIn(header))

        a = Assembly()
        pulley = Pulley(center=(CENTER[0], CENTER[1]), radius=RADIUS)
        a.add(pulley)
        spoke_base = VGroup(Line(CENTER, CENTER + [RADIUS, 0.0, 0.0], color=YELLOW, stroke_width=5))
        spoke = spoke_base.copy()
        self.add(spoke)

        mass = Block(name="m", position=(2.2, -1.4), width=0.9, label="m")
        a.add(mass)

        pull0 = np.array([-2.6, -1.2, 0.0])  # hand end below-left -> rope arches over the top
        rope = RopeOverPulley(pulley=pulley, from_point=(pull0[0], pull0[1]),
                              to_point=(mass.keypoint("top")[0], mass.keypoint("top")[1]),
                              stroke_width=5)
        self.add(rope.mobject)

        # Mark the two contact points where the rope meets the rim.
        contacts = VGroup(
            Dot(rope.keypoint("contact_a"), color=RED, radius=0.06),
            Dot(rope.keypoint("contact_b"), color=RED, radius=0.06),
        )

        # The pull force, drawn to the side of the rope so it stays legible.
        pull_dir = (pull0 - rope.keypoint("contact_a"))
        pull_dir = pull_dir / float(np.linalg.norm(pull_dir))
        pull_arrow = Arrow(pull0, pull0 + 1.1 * pull_dir, buff=0, color=GREEN, stroke_width=6)
        pull_label = Text("pull", font_size=20, color=GREEN)
        pull_label.next_to(pull_arrow.get_end(), DOWN, buff=0.1)
        angle_label = Text("120 deg", font_size=22, color=WHITE)
        angle_label.next_to(rope.keypoint("arc_mid"), DOWN, buff=0.2)

        caption = Text("rope wraps: 2 contacts + arch on the rim; pulley spins, no slip",
                       font_size=21, color=WHITE).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(a.mobject), FadeIn(rope.mobject), FadeIn(contacts),
                  FadeIn(pull_arrow), FadeIn(pull_label), FadeIn(angle_label), FadeIn(caption))
        self.wait(0.4)

        lift = 1.4
        s = ValueTracker(0.0)
        mass0 = mass.keypoint("CM").copy()

        def update(_):
            ds = s.get_value()
            # mass rises by ds; hand pays the rope out by ds; rim turns arc ds / R.
            mass.shift(mass0 + np.array([0.0, ds, 0.0]) - mass.keypoint("CM"))
            pull = pull0 - ds * pull_dir
            rope.set_endpoints(pull, mass.keypoint("top"))
            contacts[0].move_to(rope.keypoint("contact_a"))
            contacts[1].move_to(rope.keypoint("contact_b"))
            spoke.become(spoke_base.copy())
            spoke.rotate(-ds / RADIUS, about_point=CENTER)
            pull_arrow.put_start_and_end_on(pull, pull + 1.1 * pull_dir)

        mass.mobject.add_updater(update)
        self.play(s.animate.set_value(lift), run_time=3.0)
        mass.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
