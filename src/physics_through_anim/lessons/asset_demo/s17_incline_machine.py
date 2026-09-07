"""Scene 17 -- M10 stress test: how little code composes a whole machine.

Chain along an incline, foot to apex:
    fixed support --spring1-- block --spring2-- rope over a pulley --> hanging M.
Release the mass: it falls, hauling the block up the ramp; spring1 stretches,
spring2 stretches, and the rope stays taut over the pulley. Every piece is a
library asset wired by its endpoints -- the scene body is a dozen asset lines
plus one coordinating tracker. No component re-derives another's geometry.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    WHITE,
    YELLOW,
    Dot,
    FadeIn,
    Line,
    MathTex,
    Text,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import (
    Block,
    Floor,
    Incline,
    LinearSpring,
    RopeOverPulley,
)
from physics_through_anim.physics.mechanics.palette import COLOR_SPRING

GROUND_Y = -2.7
ANGLE = 27.0
HALF_W = 0.42  # block half-width along the slope
HALF_H = 0.3


def _support_glyph(point: np.ndarray, normal: np.ndarray, color=WHITE) -> VGroup:
    """A small hatched pad reading as 'bolted to the incline'."""
    tang = np.array([-normal[1], normal[0], 0.0])
    base = point - normal * 0.04
    pad = Line(base - tang * 0.35, base + tang * 0.35, color=color, stroke_width=5)
    hatch = VGroup(*[
        Line(base + tang * x, base + tang * x - normal * 0.18 - tang * 0.12,
             color=color, stroke_width=2)
        for x in np.linspace(-0.3, 0.3, 5)
    ])
    return VGroup(pad, hatch)


class InclineSpringPulleyMachine(AssetDemoScene):
    """Support -> spring -> block -> spring -> rope -> pulley -> hanging mass."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("17", "One machine, minimal code",
                                   "spring - block - spring - rope - pulley - mass")
        self.play(FadeIn(header))

        # --- geometry helpers from the incline itself ---------------------
        incline = Incline(angle_deg=ANGLE, length=6.4, base=(-3.9, GROUND_Y))
        theta = np.radians(ANGLE)
        u = np.array([np.cos(theta), np.sin(theta), 0.0])   # up-slope unit
        nrm = np.array([-np.sin(theta), np.cos(theta), 0.0])  # outward normal
        floor = Floor(y=GROUND_Y, half_width=7.0)

        def on_slope(s: float) -> np.ndarray:  # a point a block-height above the ramp
            return incline.surface_at(s) + nrm * HALF_H

        support_pt = on_slope(0.05)
        block_c0 = on_slope(0.34)
        junction0 = on_slope(0.66)
        # Flavour 1: the pulley axle is held above the apex by an immovable bracket.
        mounted = incline.mount_pulley(radius=0.34, flavour="on_support", standoff=0.5,
                                       rope_angles={"in": 150.0, "out": 30.0})
        pulley, bracket = mounted.pulley, mounted.bracket
        mass = Block(name="M", width=0.72, height=0.72,
                     position=(float(pulley.center[0]) + 1.05, float(pulley.center[1]) - 1.7))

        # --- the wired chain (this is the whole machine) ------------------
        block = Block(name="m", width=2 * HALF_W, height=2 * HALF_H,
                      position=tuple(block_c0[:2]))
        block.rotate(theta)
        spring1 = LinearSpring(from_point=support_pt[:2], to_point=(block_c0 - u * HALF_W)[:2],
                               natural_length=1.4, k=6.0, coils=6, width=0.16)
        spring2 = LinearSpring(from_point=(block_c0 + u * HALF_W)[:2], to_point=junction0[:2],
                               natural_length=1.4, k=4.0, coils=6, width=0.16)
        rope = RopeOverPulley(pulley=pulley, from_point=junction0[:2],
                              to_point=(mass.keypoint("top"))[:2], tension_label="T")

        support = _support_glyph(support_pt, nrm)
        pc = np.asarray([pulley.center[0], pulley.center[1], 0.0])
        labels = VGroup(
            MathTex("k_1", color=COLOR_SPRING, font_size=30).next_to(
                spring1.mobject, DOWN, buff=0.12),
            MathTex("k_2", color=COLOR_SPRING, font_size=30).move_to(junction0 + nrm * 0.35),
            MathTex("m", color=WHITE, font_size=30).move_to(block_c0),
            MathTex("M", color=WHITE, font_size=32).move_to(mass.keypoint("CM")),
            MathTex("T", color=rope.color, font_size=30).move_to(pc + np.array([0.55, 0.3, 0.0])),
        )
        junction_dot = Dot(junction0, color=YELLOW, radius=0.06)

        self.add(floor.mobject, incline.mobject, support, spring1.mobject, block.mobject,
                 spring2.mobject, junction_dot, bracket.mobject, pulley.mobject, rope.mobject,
                 mass.mobject, labels)
        self.play(FadeIn(floor.mobject), FadeIn(incline.mobject), FadeIn(support))
        self.play(FadeIn(spring1.mobject), FadeIn(block.mobject), FadeIn(spring2.mobject),
                  FadeIn(junction_dot))
        self.play(FadeIn(bracket.mobject), FadeIn(pulley.mobject), FadeIn(rope.mobject),
                  FadeIn(mass.mobject), FadeIn(labels))

        cap = Text("release: M falls, hauls the block up; both springs stretch",
                   font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap))

        # --- one tracker couples the whole chain --------------------------
        drop = ValueTracker(0.0)
        block_base = block.mobject.copy()
        mass_base = mass.mobject.copy()

        def refresh(_m):
            d = drop.get_value()
            bc = block_c0 + u * d          # block creeps up-slope
            r = junction0 + u * (1.6 * d)  # rope-side end advances toward the pulley
            block.mobject.become(block_base.copy()).shift(u * d)
            spring1.set_endpoints(support_pt[:2], (bc - u * HALF_W)[:2])
            spring2.set_endpoints((bc + u * HALF_W)[:2], r[:2])
            junction_dot.move_to(r)
            mass.mobject.become(mass_base.copy()).shift(np.array([0.0, -1.6 * d, 0.0]))
            mass_top = mass.keypoint("top") + np.array([0.0, -1.6 * d, 0.0])
            rope.set_endpoints(r[:2], mass_top[:2])

        anchor = Dot(fill_opacity=0.0, stroke_opacity=0.0)  # invisible updater carrier
        anchor.add_updater(refresh)
        self.add(anchor)
        self.play(drop.animate.set_value(0.5), run_time=2.6)
        anchor.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
