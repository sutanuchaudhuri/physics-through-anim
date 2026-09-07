"""Scene 21 -- M12 extension: a ball rebounds off an incline (restitution).

The incline supplies the outward normal; ``reflect_velocity`` turns the incident
velocity into the rebound (normal component flipped and scaled by e_n, tangential
kept). Free flight -> IMPACT at the surface -> new free flight -- a piecewise
trajectory whose velocity STEPs at the bounce. The incident (dim), normal (green)
and rebound (bright) vectors are drawn at the contact.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, GREEN, WHITE, Arrow, FadeIn, FadeOut, Flash, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.impact import reflect_velocity
from physics_through_anim.physics.mechanics import Disk, Floor, Incline
from physics_through_anim.physics.mechanics.palette import COLOR_VELOCITY

GROUND_Y = -2.6
ANGLE = 24.0
G = 6.0
R = 0.22
E_N, E_T = 0.72, 1.0


class BallReboundIncline(AssetDemoScene):
    """Incident velocity reflected about the incline normal with restitution."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("21", "Rebound on an incline", "restitution reflection")
        self.play(FadeIn(header))

        floor = Floor(y=GROUND_Y, half_width=7.0)
        incline = Incline(angle_deg=ANGLE, length=6.4, base=(-3.2, GROUND_Y))
        theta = np.radians(ANGLE)
        normal = np.array([-np.sin(theta), np.cos(theta), 0.0])  # outward incline normal
        contact = incline.surface_at(0.5)
        p_center = contact + normal * R  # ball centre when it touches the ramp
        self.add(floor.mobject, incline.mobject)
        self.play(FadeIn(floor.mobject), FadeIn(incline.mobject))

        v_in = np.array([2.6, -2.3, 0.0])  # incident velocity (into the surface)
        v_out = np.append(reflect_velocity(v_in, normal, e_n=E_N, e_t=E_T), 0.0)
        accel = np.array([0.0, -G, 0.0])
        t_pre, t_post = 0.85, 1.5

        ball = Disk(name="ball", radius=R, position=(p_center[0], p_center[1]))
        start = p_center + v_in * (-t_pre) + 0.5 * accel * t_pre**2
        ball.mobject.move_to(start)
        self.add(ball.mobject)

        cap1 = Text("free flight toward the ramp", font_size=21, color=WHITE)
        cap1.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(ball.mobject), FadeIn(cap1))

        # --- Phase 1: incoming parabola to the contact ---------------------
        tau = ValueTracker(-t_pre)

        def fly(m):
            t = tau.get_value()
            v = v_in if t < 0 else v_out
            m.move_to(p_center + v * t + 0.5 * accel * t * t)

        ball.mobject.add_updater(fly)
        self.play(tau.animate.set_value(0.0), run_time=1.2)
        ball.mobject.clear_updaters()
        ball.mobject.move_to(p_center)

        # --- Impact: draw incident / normal / rebound vectors --------------
        scale = 0.34
        v_in_u = v_in / np.linalg.norm(v_in)
        incident = Arrow(p_center - v_in_u * 0.9, p_center, buff=0.0,
                         color=COLOR_VELOCITY, stroke_width=4).set_opacity(0.5)
        n_arrow = Arrow(p_center, p_center + normal * 0.9, buff=0.0, color=GREEN, stroke_width=4)
        rebound = Arrow(p_center, p_center + v_out * scale, buff=0.0,
                        color=COLOR_VELOCITY, stroke_width=5)
        cap2 = Text("v_out = reflect(v_in, n): normal flips x e_n, tangential kept",
                    font_size=20, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(Flash(p_center, color=GREEN, flash_radius=0.4),
                  FadeIn(incident), FadeIn(n_arrow), FadeIn(rebound),
                  cap1.animate.become(cap2))
        self.wait(0.4)

        # --- Phase 2: rebound parabola -------------------------------------
        cap3 = Text(f"rebound with restitution e_n = {E_N}", font_size=21, color=WHITE)
        cap3.to_edge(DOWN, buff=0.4)
        self.play(cap1.animate.become(cap3), FadeOut(incident))
        tau.set_value(0.0)
        ball.mobject.add_updater(fly)
        self.play(tau.animate.set_value(t_post), run_time=1.6)
        ball.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
