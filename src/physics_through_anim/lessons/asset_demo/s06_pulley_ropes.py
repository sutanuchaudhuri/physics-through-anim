"""Scene 06 -- M4 flagship: a pulley hung from a ceiling with two ropes + tensions.

The pulley is hung from the ceiling (placement sugar), two masses hang from ropes
resolved by name (``pulley.A`` -> ``m_1.top``), and each mass's FBD shows its
weight down and rope tension up along the rope. Rope B slips (hash marks). Nothing
is placed by hand: the assembly resolves every attachment point.
"""

from __future__ import annotations

from manim import WHITE, FadeIn, FadeOut, Rotate, Text

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import (
    Assembly,
    Block,
    Ceiling,
    Pulley,
    Rope,
)
from physics_through_anim.physics.render import Layout


class PulleyTwoRopes(AssetDemoScene):
    """A ceiling-mounted pulley with two hanging masses and their tensions."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("06", "Pulley + two ropes", "tensions resolved by name")
        self.play(FadeIn(header))

        a = Assembly()
        ceiling = Ceiling(y=3.2, half_width=5.0)
        pulley = Pulley(center=(0.0, 2.0), radius=0.7, rope_angles={"A": 205.0, "B": 335.0})
        a.add(ceiling)
        a.hang(pulley, from_ceiling=ceiling, drop=0.8)

        rim_a, rim_b = a.resolve("pulley.A"), a.resolve("pulley.B")
        m1 = Block(name="m_1", position=(rim_a[0], rim_a[1] - 1.6), width=0.8, label="m_1")
        m2 = Block(name="m_2", position=(rim_b[0], rim_b[1] - 2.2), width=0.8, label="m_2")
        a.add(m1)
        a.add(m2)

        rope_a = Rope(from_ref="pulley.A", to_ref="m_1.top", tension_label="T_A")
        rope_b = Rope(from_ref="pulley.B", to_ref="m_2.top", tension_label="T_B", slips=True)
        a.connect(rope_a)
        a.connect(rope_b)

        # Tensions on the masses: up along each rope toward the wheel (SKILL colour).
        rope_a.tension_on(m1, at="top", toward=a.resolve("pulley.A"))
        rope_b.tension_on(m2, at="top", toward=a.resolve("pulley.B"))

        caption = Text("ropes resolve pulley.A -> m_1.top; T up, mg down",
                       font_size=22, color=WHITE)
        Layout.standard().place(caption, "caption")
        self.play(FadeIn(a.mobject), FadeIn(caption))
        self.play(FadeIn(a.fbd()))
        self.wait(0.4)
        # The wheel spins as the ropes pay out (visual only; A/B stay put here).
        self.play(Rotate(pulley.mobject, angle=-0.6, about_point=pulley.keypoint("axle")))
        self.wait(0.3)
        self.play(FadeOut(caption))
        self.finish_with_narration()
