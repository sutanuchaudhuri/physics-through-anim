"""Scene 03 -- M2 supports, contact, and the non-penetration constraint.

Shows the conveyor cases (running / stopped belt with FBD + contact glyph) and
the wedge: a cylinder rolls into a floor+ramp corner and seats tangent to *both*
walls -- the non-penetration clamp keeps it from ever piercing either wall.
"""

from __future__ import annotations

from manim import (
    BLUE,
    DOWN,
    ORIGIN,
    YELLOW,
    Circle,
    FadeIn,
    FadeOut,
    Line,
    Text,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.kinematics import RollingKinematicRelation, RollingPoseBinding
from physics_through_anim.physics.mechanics import (
    Assembly,
    Block,
    Conveyor,
    Floor,
    Incline,
    corner_seat,
    no_penetration_clamp,
)
from physics_through_anim.physics.mechanics.contact import ContactFrame
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.massprops import MassProperties
from physics_through_anim.physics.mechanics.rigidbody import RigidBody2D
from physics_through_anim.physics.overlays.contact import contact_frame, contact_marker
from physics_through_anim.physics.render.tokens import Beat, Dir, Size, Span

GROUND_Y = -2.0


def _place(mob, base, pose: Pose2D) -> None:
    mob.become(base.copy())
    mob.rotate(pose.angle, about_point=ORIGIN)
    mob.shift([pose.position[0], pose.position[1], 0.0])


class SupportsAndContact(AssetDemoScene):
    """M2: conveyor contact cases plus the impenetrable-wall wedge seat."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("03", "Supports & contact", "walls cannot be pierced")
        self.play(FadeIn(header))

        self._conveyor_case(belt_speed=2.0, caption="running belt: block slides (contact CHANGING)")
        self._conveyor_case(belt_speed=0.0, caption="stopped belt: block rests (contact SAME)")
        self._wedge_case()

        self.finish_with_narration()

    def _caption(self, text: str) -> Text:
        return Text(text, font_size=22, color=YELLOW).to_edge(DOWN, buff=0.5)

    def _conveyor_case(self, *, belt_speed: float, caption: str) -> None:
        assembly = Assembly()
        conveyor = Conveyor(belt_speed=belt_speed, half_width=Span.NORMAL)
        block = Block(width=Size.LARGE, label="m")
        assembly.add(conveyor)
        assembly.add(block, place_on=conveyor)
        block.add_force(ForceKind.NORMAL, at="contact", label="N", direction="up")
        fbd = assembly.fbd()

        contact = block.keypoint("contact")
        frame = ContactFrame(point=contact, tangent=Dir.RIGHT, normal=Dir.UP)
        glyph = VGroup(contact_marker(frame), contact_frame(frame, scale=0.6))
        label = self._caption(caption)

        self.play(FadeIn(assembly.mobject), FadeIn(fbd), FadeIn(glyph), FadeIn(label),
                  run_time=Beat.NORMAL)
        conveyor.animate(self, run_time=Beat.HOLD)  # scroll chevrons, or hold if stopped
        self.play(
            FadeOut(assembly.mobject), FadeOut(fbd), FadeOut(glyph), FadeOut(label),
            run_time=Beat.QUICK,
        )

    def _wedge_case(self) -> None:
        radius = 0.5
        floor = Floor(y=GROUND_Y, half_width=Span.WIDE)
        ramp = Incline(angle_deg=32.0, length=4.0, base=(1.2, GROUND_Y))
        self.play(FadeIn(floor.mobject), FadeIn(ramp.mobject), run_time=0.4)  # custom tempo
        label = self._caption("cylinder rolls into the corner -- seats on both walls")
        self.play(FadeIn(label), run_time=Beat.QUICK)

        seat = corner_seat(radius, floor, ramp)
        start_x = -3.6
        origin = Pose2D(position=(start_x, GROUND_Y + radius))
        body = RigidBody2D(
            mass_props=MassProperties(mass=1.0, inertia_cm=0.5), local_keypoints={"CM": (0.0, 0.0)}
        )
        clamp = no_penetration_clamp(radius, [floor, ramp])
        binding = RollingPoseBinding(
            body, RollingKinematicRelation(radius=radius, direction=1), origin=origin, clamp=clamp
        )

        base = VGroup(
            Circle(radius=radius, color=BLUE),
            Line(ORIGIN, [radius, 0.0, 0.0], color=YELLOW, stroke_width=5),
        )
        wheel = base.copy()
        s = ValueTracker(0.0)

        def upd(m):
            binding.s = s.get_value()
            binding.apply()
            _place(m, base, body.pose)

        wheel.add_updater(upd)
        self.play(FadeIn(wheel), run_time=Beat.QUICK)
        self.play(s.animate.set_value(float(seat[0] - start_x)), run_time=2.4)  # custom tempo
        wheel.clear_updaters()

        # Mark the two contact points where the seated cylinder touches each wall.
        floor_n = tuple(floor.normal()[:2])
        ramp_n = tuple(ramp.normal()[:2])
        ramp_t = tuple(ramp.tangent()[:2])
        c_floor = ContactFrame(point=seat - radius * floor.normal(), tangent=(1.0, 0.0),
                               normal=floor_n)
        c_ramp = ContactFrame(point=seat - radius * ramp.normal(), tangent=ramp_t, normal=ramp_n)
        self.play(FadeIn(contact_marker(c_floor)), FadeIn(contact_marker(c_ramp)),
                  run_time=Beat.QUICK)
        self.wait(0.5)
