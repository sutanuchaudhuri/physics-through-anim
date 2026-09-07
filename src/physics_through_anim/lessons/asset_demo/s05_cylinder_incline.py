"""Scene 05 -- M3 flagship: a cylinder on an incline (seated by the constraint).

The cylinder is placed with ``place_on=ramp`` -- no manual coordinates: seating is
the tangency (non-penetration) constraint at equality. It then rolls *down* the
slope with ``roll_along_surface``, which parametrises the centre along the surface
tangent at a fixed offset ``R`` -- so the body is *always in contact* and can never
pierce the ramp. FBD: ``mg`` down at CM, ``N`` out of the slope and ``f`` up-slope
at the contact ``P``.
"""

from __future__ import annotations

from manim import DOWN, WHITE, FadeIn, FadeOut, Text

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import Assembly, Cylinder, Floor, Incline, motion
from physics_through_anim.physics.mechanics.kinds import ForceKind

GROUND_Y = -2.4


class CylinderOnIncline(AssetDemoScene):
    """Seat a cylinder on a ramp by the constraint, then roll it down in contact."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("05", "Cylinder on an incline", "seated by the constraint")
        self.play(FadeIn(header))

        floor = Floor(y=GROUND_Y, half_width=6.0)
        ramp = Incline(angle_deg=28.0, length=6.0, base=(-3.6, GROUND_Y))
        seat = ramp.surface_at(0.78)
        cyl = Cylinder(radius=0.5, position=(seat[0], seat[1] + 0.5), label="m")

        assembly = Assembly()
        assembly.add(floor)
        assembly.add(ramp)
        assembly.add(cyl, place_on=ramp)  # <- constraint seats it tangent to the slope

        # FBD at the right keypoints (SKILL Rule 2 colours via the FBD layer).
        up_slope = tuple(ramp.tangent()[:2])
        cyl.add_force(ForceKind.NORMAL, at="contact", label="N", direction=tuple(ramp.normal()[:2]))
        cyl.add_force(ForceKind.FRICTION, at="contact", label="f", direction=up_slope)
        fbd = assembly.fbd()

        caption = Text("place_on=ramp: no manual coordinates, always in contact",
                       font_size=22, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(assembly.mobject), FadeIn(caption))
        self.play(FadeIn(fbd))
        self.wait(0.6)
        self.play(FadeOut(fbd), FadeOut(caption))

        motion.roll_along_surface(self, cyl, ramp, distance=3.4, run_time=2.6, down=True)
        self.wait(0.4)
        self.finish_with_narration()
