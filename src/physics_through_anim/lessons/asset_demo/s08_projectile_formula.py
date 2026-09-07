"""Scene 08 -- M6 time dimension: a projectile driven by a formula (no solver).

The particle never integrates anything: an ``AnalyticTrajectory`` samples a
``SystemState`` at each time t, and the assembly applies it (absolute pose, no
drift). At the apex the velocity is horizontal (v_y = 0) -- a declarative
freeze-frame teaching moment.
"""

from __future__ import annotations

from manim import BLUE, DOWN, WHITE, Arrow, Dot, FadeIn, FadeOut, Text, TracedPath, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics import Assembly, Particle

G = 6.0
X0, Y0 = -4.5, -1.8
VX, VY = 1.8, 6.0
T_END = 2.0 * VY / G  # flight time back to launch height


def _parabola(t: float) -> SystemState:
    x = X0 + VX * t
    y = Y0 + VY * t - 0.5 * G * t * t
    return SystemState(
        entities={
            "ball": RigidKinematicState(
                pose=Pose2D(position=(x, y)), velocity=(VX, VY - G * t)
            )
        }
    )


class ProjectileFormula(AssetDemoScene):
    """A particle follows an analytic parabola; apex snapshot shows v horizontal."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "08", "Projectile from a formula", "assets consume, never integrate"
        )
        self.play(FadeIn(header))

        a = Assembly()
        ball = Particle(name="ball", position=(X0, Y0), radius=0.12, color=BLUE)
        a.add(ball)
        trail = TracedPath(lambda: ball.keypoint("CM"), stroke_color=WHITE, stroke_width=2)
        self.add(trail)

        caption = Text("state_at(t): pose + velocity, sampled each frame",
                       font_size=22, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(a.mobject), FadeIn(caption))
        a.animate_trajectory(self, AnalyticTrajectory(_parabola), 0.0, T_END, run_time=4.0)

        # Declarative freeze-frame at the apex: v is horizontal (v_y = 0).
        self.remove(trail)  # drop the flight trail before jumping to the apex
        self.play(FadeOut(caption))
        apex = _parabola(T_END / 2.0).entities["ball"]
        a.apply_states({"ball": apex})
        vx, vy = apex.velocity
        v_arrow = Arrow(ball.keypoint("CM"), ball.keypoint("CM") + [0.35 * vx, 0.35 * vy, 0.0],
                        buff=0, color=BLUE, stroke_width=6)
        snap = VGroup(Dot(ball.keypoint("CM"), color=BLUE, radius=0.05), v_arrow)
        label = Text("apex: v horizontal (v_y = 0)", font_size=22, color=BLUE)
        label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(snap))
        self.play(FadeIn(label))
        self.wait(0.4)
        self.finish_with_narration()
