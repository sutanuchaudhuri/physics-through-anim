"""Scene 01 -- cumulative asset demo: what M1 + M1.5 render today.

M1 (shipped) draws the body + free-body diagram; M1.5 (implemented) is the model
layer that computes the velocity vector the scene then draws. Layout uses the
``physics/render`` regions: the STAGE shows only vector *symbols*, while the
formula ``v = omega x r`` sits in the EQUATION region so it never overlaps the FBD.
"""

from __future__ import annotations

from manim import BLUE, DOWN, LEFT, RIGHT, UP, Arrow, FadeIn, MathTex, Write

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.mechanics import Assembly, Block, Floor
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.massprops import MassProperties
from physics_through_anim.physics.mechanics.rigidbody import BodyState2D, RigidBody2D
from physics_through_anim.physics.render import Layout, avoid_overlap


class CumulativeAssets(AssetDemoScene):
    """Block-on-floor FBD (M1) plus an M1.5-computed velocity vector."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("01", "Asset library so far", "M1 renders, M1.5 computes")
        self.play(FadeIn(header))

        # --- M1 (shipped): drawable assets + free-body diagram ---------------
        assembly = Assembly()
        floor = Floor()
        block = Block(width=1.4, label="m")
        assembly.add(floor)
        assembly.add(block, place_on=floor)
        block.add_force(ForceKind.NORMAL, at="contact", label="N", direction="up")
        fbd = assembly.fbd()  # mg (down) + N (up) -- symbols only
        self.play(FadeIn(assembly.mobject))
        self.play(FadeIn(fbd))
        self.wait(0.8)

        # --- M1.5 (implemented): model layer computes v = omega x r ----------
        cm = block.keypoint("CM")
        body = RigidBody2D(
            mass_props=MassProperties(mass=1.0, inertia_cm=0.5),
            pose=Pose2D(position=(float(cm[0]), float(cm[1])), angle=0.0),
            local_keypoints={"CM": (0.0, 0.0), "P": (0.7, 0.0)},
        )
        state = BodyState2D(pose=body.pose, velocity=(0.0, 0.0), omega=3.0)
        p_world = body.point_position("P", state)
        v = body.point_velocity("P", state)  # perpendicular to (P - CM)
        v_arrow = Arrow(p_world, p_world + 0.25 * v, buff=0, color=BLUE, stroke_width=6)

        # STAGE region: kinematics *symbol* only, placed clear of the FBD arrows.
        v_symbol = MathTex("v", color=BLUE)
        avoid_overlap(v_symbol, v_arrow, [*fbd, block.mobject], dirs=(RIGHT, UP, DOWN, LEFT))
        self.play(FadeIn(v_arrow), Write(v_symbol))

        # EQUATION region: the formula lives here, never on top of the diagram.
        formula = MathTex("v = \\omega \\times r", color=BLUE)
        Layout.standard().place(formula, "equation")
        self.play(Write(formula))
        self.finish_with_narration()
