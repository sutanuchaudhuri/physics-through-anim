"""Scene 06 -- M4 flagship: a pulley hung from a ceiling with two ropes + tensions.

The pulley is hung from the ceiling (placement sugar), two masses hang from ropes
resolved by name (``pulley.left`` -> ``m_1.top``), and each mass's FBD shows its
weight down and rope tension up along the rope. The right rope slips (hash marks).
Nothing is placed by hand: the assembly resolves every attachment point.
"""

from __future__ import annotations

from enum import StrEnum

from manim import WHITE, FadeIn, FadeOut, Rotate, Text

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import (
    Assembly,
    Bearing,
    Block,
    Ceiling,
    Keypoint,
    Pulley,
    Rope,
)
from physics_through_anim.physics.render import Layout, Level, Span


class Port(StrEnum):
    """The two rope departure points on the wheel (named once, reused everywhere)."""

    LEFT = "left"
    RIGHT = "right"


class PulleyTwoRopes(AssetDemoScene):
    """A ceiling-mounted pulley with two hanging masses and their tensions."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("06", "Pulley + two ropes", "tensions resolved by name")
        self.play(FadeIn(header))

        a = Assembly()
        ceiling = Ceiling(y=Level.CEILING, half_width=Span.NORMAL)
        # rope_angles keys are our Port labels (-> resolvable via pulley.port(Port.LEFT));
        # values are departure bearings (0=E, CCW) -- Bearing names the common ones.
        pulley = Pulley(center=(0.0, 2.0), radius=0.7,
                        rope_angles={Port.LEFT: Bearing.SW, Port.RIGHT: Bearing.SE})
        a.add(ceiling)
        a.hang(pulley, from_ceiling=ceiling, drop=0.8)

        rim_left, rim_right = a.resolve(pulley.port(Port.LEFT)), a.resolve(pulley.port(Port.RIGHT))
        m1 = Block(name="m_1", position=(rim_left[0], rim_left[1] - 1.6), width=0.8, label="m_1")
        m2 = Block(name="m_2", position=(rim_right[0], rim_right[1] - 2.2), width=0.8, label="m_2")
        a.add(m1)
        a.add(m2)

        rope_a = Rope(from_ref=pulley.port(Port.LEFT), to_ref=m1.port(Keypoint.TOP),
                      tension_label="T_A")
        rope_b = Rope(from_ref=pulley.port(Port.RIGHT), to_ref=m2.port(Keypoint.TOP),
                      tension_label="T_B", slips=True)
        a.connect(rope_a)
        a.connect(rope_b)

        # hang()/connect() record typed Relations, e.g. a.relations_of(RelationKind.HANG)
        # -> [Relation(HANG, ("pulley", "ceiling"))]; a.relations_with("pulley") -> both ropes.

        # Tensions on the masses: up along each rope toward the wheel (SKILL colour).
        # at= is a body attach point (Keypoint); toward= is a resolved world point (getter).
        rope_a.tension_on(m1, at=Keypoint.TOP, toward=a.resolve(pulley.port(Port.LEFT)))
        rope_b.tension_on(m2, at=Keypoint.TOP, toward=a.resolve(pulley.port(Port.RIGHT)))

        caption = Text("ropes resolve pulley.left -> m_1.top; T up, mg down",
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
