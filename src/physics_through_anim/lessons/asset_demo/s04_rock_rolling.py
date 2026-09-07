"""Scene 04 -- M3 rock rolling: a customizable skin over a rolling disk.

A boulder (a ``rock_skin`` over a ``Disk``) rolls along the ground. The *picture*
is a rock; the *physics* is a disk -- contact ``P``, CM, weight, and the Rule 5
rolling velocity field. Swap the skin for a wheel/barrel/image and nothing else
changes.
"""

from __future__ import annotations

from math import pi

from manim import BLUE, DOWN, WHITE, Arrow, Dot, FadeIn, FadeOut, Text, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import Assembly, Disk, Floor, motion
from physics_through_anim.physics.render import rock_skin

GROUND_Y = -2.2


class RockRolling(AssetDemoScene):
    """A rock (skin) rolling as a disk (physics), then its rolling velocity field."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("04", "Rock rolling", "skin cosmetic, disk physics")
        self.play(FadeIn(header))

        floor = Floor(y=GROUND_Y, half_width=6.0)
        assembly = Assembly()
        assembly.add(floor)
        rock = rock_skin(radius=0.7, sides=10, jitter=0.22, seed=5)
        boulder = Disk(radius=0.7, position=(-4.0, 3.0), skin=rock, show_spoke=True, label="m")
        assembly.add(boulder, place_on=floor)

        caption = Text("a rock is just a skin over a rolling disk", font_size=22, color=WHITE)
        caption.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(assembly.mobject), FadeIn(caption))
        motion.roll_group(self, boulder, distance=6.0, run_time=3.0)
        self.play(FadeOut(caption))

        # Frozen frame: the Rule 5 rolling velocity field + contact P (the physics).
        v_cm = 2.0
        contact = boulder.contact_point()
        field = VGroup(Dot(contact, color=WHITE, radius=0.06))
        for theta in (pi / 2, pi / 6, 5 * pi / 6):  # top and two upper rim points
            p = boulder.rim_at(theta)
            v = boulder.point_velocity(p, v_cm)
            field.add(Arrow(p, p + 0.35 * v, buff=0, color=BLUE, stroke_width=5))
        label = Text("v = omega x (point - P), perp to P->point (Rule 5)",
                     font_size=20, color=BLUE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(field), FadeIn(label))
        self.wait(0.5)
        self.finish_with_narration()
