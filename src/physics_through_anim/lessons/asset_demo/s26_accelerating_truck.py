"""Scene 26 -- M14 flagship: a block in an accelerating truck (two frames).

Same block, two observers. In the **ground frame S** the block accelerates with
the truck and only real forces act (N, mg, friction). In the **truck frame S'**
the block is at rest, so we add a **dashed pseudo-force** ``-m a_f`` -- fictitious,
drawn grey/dashed so it is never confused with a real force. Each panel carries
its frame badge (Rule 1 icon + label).
"""

from __future__ import annotations

from manim import DOWN, UP, WHITE, Arrow, FadeIn, MathTex, Rectangle, Text, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.palette import (
    COLOR_ACCEL,
    COLOR_FRICTION,
    COLOR_NORMAL,
    COLOR_WEIGHT,
)
from physics_through_anim.physics.mechanics.reference_frames import (
    FrameKind,
    FrameState,
    PseudoForceKind,
    ReferenceFrame,
)
from physics_through_anim.physics.overlays.frames import frame_badge, pseudo_force_arrow
from physics_through_anim.physics.render.layout import Anchor, stage_region

A_TRUCK = 2.0


def _truck_with_block(cx: float, cy: float):
    """A little truck box + a block sitting in it; returns (group, block)."""
    truck = VGroup(
        Rectangle(width=2.4, height=0.12, color="#ADB5BD", fill_color="#ADB5BD",
                  fill_opacity=1.0).move_to([cx, cy - 0.35, 0.0]),
        Rectangle(width=0.12, height=0.7, color="#ADB5BD", fill_color="#ADB5BD",
                  fill_opacity=1.0).move_to([cx - 1.2, cy, 0.0]),
    )
    block = Block(name="m", width=0.7, height=0.6, position=(cx, cy), label="m")
    return VGroup(truck, block.mobject), block


def _real_forces(block, *, friction=True):
    cm = block.keypoint("CM")
    top = block.keypoint("top")
    bottom = block.keypoint("bottom")
    left = block.keypoint("left")
    forces = VGroup(
        Arrow(top, top + [0.0, 0.9, 0.0], buff=0.0, color=COLOR_NORMAL, stroke_width=5),
        Arrow(bottom, bottom + [0.0, -0.9, 0.0], buff=0.0, color=COLOR_WEIGHT, stroke_width=5),
        MathTex("N", color=COLOR_NORMAL).scale(0.55).next_to(top + [0.0, 0.9, 0.0], UP, buff=0.05),
        MathTex("mg", color=COLOR_WEIGHT).scale(0.5).next_to(bottom + [0.0, -0.9, 0.0], DOWN,
                                                             buff=0.05),
    )
    if friction:
        forces.add(Arrow(cm, cm + [0.9, 0.0, 0.0], buff=0.0, color=COLOR_FRICTION, stroke_width=5))
        forces.add(MathTex("f", color=COLOR_FRICTION).scale(0.55).next_to(
            cm + [0.9, 0.0, 0.0], buff=0.06))
    _ = left
    return forces


class AcceleratingTruck(AssetDemoScene):
    """Ground frame (real forces) vs truck frame (add the dashed pseudo-force)."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("26", "Two frames, one block", "real force vs pseudo-force")
        self.play(FadeIn(header))

        # Two panels from the stage region -- no eyeballed coordinates.
        left, right = stage_region(ground_y=-1.3, top=1.7).columns(2, gap=0.5)

        # --- LEFT panel: ground frame S ----------------------------------
        ground = ReferenceFrame(kind=FrameKind.INERTIAL, label="S")
        left_truck, left_block = _truck_with_block(*left.anchor(Anchor.CENTER)[:2])
        left_forces = _real_forces(left_block)
        left_accel = Arrow(left.anchor(Anchor.TOP, offset=(-0.6, -0.1)),
                           left.anchor(Anchor.TOP, offset=(0.6, -0.1)),
                           buff=0.0, color=COLOR_ACCEL, stroke_width=6)
        left_accel_lbl = MathTex("a", color=COLOR_ACCEL).scale(0.6)
        left_accel_lbl.next_to(left_accel, UP, buff=0.05)
        left_badge = frame_badge(ground).move_to(left.anchor(Anchor.TOP_LEFT, pad=0.3))
        left_title = Text("ground frame S: block accelerates, real forces only",
                          font_size=19, color=WHITE).move_to(left.anchor(Anchor.BOTTOM,
                                                                        offset=(0.0, -0.35)))

        # --- RIGHT panel: truck frame S' ---------------------------------
        truck_frame = ReferenceFrame(kind=FrameKind.TRANSLATING, label="S'")
        fs = FrameState(acceleration=(A_TRUCK, 0.0))
        right_truck, right_block = _truck_with_block(*right.anchor(Anchor.CENTER)[:2])
        right_forces = _real_forces(right_block)
        pseudo = pseudo_force_arrow(right_block, PseudoForceKind.INERTIAL_PSEUDO, fs, scale=1.0)
        right_badge = frame_badge(truck_frame, fs).move_to(right.anchor(Anchor.TOP_RIGHT, pad=0.3))
        right_title = Text("truck frame S': block at rest, add dashed -m a_f",
                           font_size=19, color=WHITE).move_to(right.anchor(Anchor.BOTTOM,
                                                                          offset=(0.0, -0.35)))

        self.play(FadeIn(left_truck), FadeIn(left_badge), FadeIn(left_title))
        self.play(FadeIn(left_forces), FadeIn(left_accel), FadeIn(left_accel_lbl))
        self.wait(0.3)
        self.play(FadeIn(right_truck), FadeIn(right_badge), FadeIn(right_title))
        self.play(FadeIn(right_forces))
        self.play(FadeIn(pseudo))

        cap = Text("the dashed pseudo-force is fictitious -- never a real force",
                   font_size=21, color="#CED4DA").to_edge(DOWN, buff=0.35)
        self.play(FadeIn(cap))
        self.wait(0.5)
        self.finish_with_narration()
