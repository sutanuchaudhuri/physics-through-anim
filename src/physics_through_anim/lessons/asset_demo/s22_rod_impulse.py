"""Scene 22 -- M12 extension: an off-centre impulse on a horizontal rod.

A rod at rest is struck at one end by an impulse J. The library turns the supplied
J into the response with ``impulse_response``: the CM gains dv = J/m (pure
translation) AND the rod gains spin domega = (r x J)/I about the CM. A central hit
would only translate; an end hit does both. The same tool drives a bat hitting a
ball, a rod striking a wall, or a pendulum given a sudden blow -- and its sweet
spot is the center of percussion.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, WHITE, FadeIn, Flash, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.impact import impulse_response
from physics_through_anim.physics.mechanics.rod import Rod
from physics_through_anim.physics.overlays.events import angular_impulse_markers

LENGTH = 3.0
MASS = 1.0
J = np.array([0.0, 1.3])  # upward impulse at the left end
T_FLY = 0.45  # stop before the rod spins past ~70 deg, so "struck end leads" stays legible


class RodImpulse(AssetDemoScene):
    """End impulse -> CM translation dv=J/m plus spin domega=(r x J)/I."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("22", "An off-centre impulse", "one blow: translate + spin")
        self.play(FadeIn(header))

        rod = Rod(name="rod", mass=MASS, length=LENGTH, angle_deg=0.0, center=(-0.3, 0.4),
                  label="m")
        cm0 = rod.keypoint("CM").copy()
        end = rod.keypoint("A").copy()  # struck end (left)
        self.add(rod.mobject)
        cap1 = Text("a rod at rest, struck at its left end", font_size=22, color=WHITE)
        cap1.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(rod.mobject), FadeIn(cap1))

        # The supplied impulse -> its response (dv of CM, spin about CM).
        r_from_cm = (end - cm0)[:2]
        resp = impulse_response(MASS, rod.inertia_cm, r_from_cm, J)

        markers = angular_impulse_markers(end, J, cm0, resp.delta_v, resp.delta_omega,
                                          j_scale=0.9, v_scale=0.7, spin_radius=0.6)
        cap2 = Text("J at the end -> dv = J/m (translate) AND domega = (r x J)/I (spin)",
                    font_size=20, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(Flash(end, color="#F783AC", flash_radius=0.4), FadeIn(markers),
                  cap1.animate.become(cap2))
        self.wait(0.5)

        # Free motion from the response: CM drifts by dv, rod spins by domega (no gravity,
        # to isolate the impulse's effect).
        base = rod.mobject.copy()
        dv = np.array([resp.delta_v[0], resp.delta_v[1], 0.0])
        clock = ValueTracker(0.0)

        def fly(m):
            t = clock.get_value()
            m.become(base.copy())
            m.rotate(resp.delta_omega * t, about_point=cm0)
            m.shift(dv * t)

        cap3 = Text("the end that was hit leads; the CM travels straight",
                    font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(cap1.animate.become(cap3), markers.animate.set_opacity(0.35))
        rod.mobject.add_updater(fly)
        self.play(clock.animate.set_value(T_FLY), run_time=2.4)
        rod.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
