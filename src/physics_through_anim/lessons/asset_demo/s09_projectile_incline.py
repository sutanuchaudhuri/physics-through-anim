"""Scene 09 -- a projectile thrown onto an incline (M6 trajectory + M2 incline).

A particle is launched from a formula (no solver) and lands on a ramp. The
landing point and the incline surface are both derived; the flight is an
``AnalyticTrajectory`` sampled each frame.
"""

from __future__ import annotations

from manim import BLUE, DOWN, WHITE, YELLOW, Arrow, Dot, FadeIn, Text, TracedPath

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics import Assembly, Floor, Incline, Particle

GROUND_Y = -2.6
G = 7.0
X0, Y0 = -1.5, -2.4
VX, VY = 3.0, 5.5


def _pos(t: float):
    return X0 + VX * t, Y0 + VY * t - 0.5 * G * t * t


def _state(t: float) -> SystemState:
    x, y = _pos(t)
    return SystemState(
        entities={
            "ball": RigidKinematicState(pose=Pose2D(position=(x, y)), velocity=(VX, VY - G * t))
        }
    )


class ProjectileOnIncline(AssetDemoScene):
    """Thrown from a formula; lands on the ramp surface."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("09", "Projectile onto an incline", "flight from a formula")
        self.play(FadeIn(header))

        floor = Floor(y=GROUND_Y, half_width=6.0)
        ramp = Incline(angle_deg=32.0, length=5.2, base=(0.2, GROUND_Y))
        foot = ramp.surface_at(0.0)
        slope = (ramp.surface_at(1.0) - foot)
        slope = slope / float((slope[0] ** 2 + slope[1] ** 2) ** 0.5)

        # landing time: first t where the parabola drops onto the ramp surface.
        t_land = 2.0
        t = 0.02
        while t < 4.0:
            x, y = _pos(t)
            if x >= foot[0]:
                surf_y = foot[1] + (x - foot[0]) * (slope[1] / slope[0])
                if y <= surf_y:
                    t_land = t
                    break
            t += 0.01

        ball = Particle(name="ball", position=(X0, Y0), radius=0.12, color=BLUE)
        a = Assembly()
        a.add(floor)
        a.add(ramp)
        a.add(ball)
        trail = TracedPath(lambda: ball.keypoint("CM"), stroke_color=WHITE, stroke_width=2)
        self.add(trail)

        caption = Text("state_at(t) sampled each frame; lands on the ramp",
                       font_size=22, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(a.mobject), FadeIn(caption))
        a.animate_trajectory(self, AnalyticTrajectory(_state), 0.0, t_land, run_time=3.2)

        # Mark the landing contact + the impact velocity.
        land = ball.keypoint("CM")
        v = _state(t_land).entities["ball"].velocity
        v_arrow = Arrow(land, land + [0.3 * v[0], 0.3 * v[1], 0.0], buff=0, color=BLUE,
                        stroke_width=6)
        self.play(FadeIn(Dot(land, color=YELLOW, radius=0.07)), FadeIn(v_arrow))
        self.wait(0.4)
        self.finish_with_narration()
