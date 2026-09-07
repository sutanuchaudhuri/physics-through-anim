"""Scene 25 -- M13 flagship (probe B): a Kepler elliptical orbit.

The Sun sits at one focus of an ``OrbitPath`` (geometry only); the planet's motion
comes from ``KeplerEllipseTrajectory`` (analytic equal-areas timing, solver-free).
Overlays read off the live position: the Sun->planet radius vector, the gravity
arrow always pointing at the Sun, and an r-vs-t graph whose cursor tracks the
planet. Two shaded focus sectors -- one at periapsis, one at apoapsis -- have
**equal area** because they are swept in **equal time** (Kepler's second law).
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, UP, WHITE, FadeIn, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.refs import QuantityRef
from physics_through_anim.physics.mechanics import (
    CentralBody,
    KeplerEllipseTrajectory,
    OrbitPath,
    Particle,
    focus_marker,
)
from physics_through_anim.physics.overlays.graphs import GraphBinding, QuantitySignal, TimeSignal
from physics_through_anim.physics.overlays.orbit import (
    central_force_arrow,
    radius_vector,
    swept_area,
)

FOCUS = (-1.2, 0.3)
A, E = 2.4, 0.45
PERIOD = 8.0


class KeplerOrbit(AssetDemoScene):
    """Elliptical orbit + radius vector + gravity + r-t graph + Kepler-II sectors."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("25", "A Kepler orbit", "equal areas in equal times")
        self.play(FadeIn(header))

        sun = CentralBody(name="sun", position=FOCUS, radius=0.34, label="M")
        orbit = OrbitPath(a=A, e=E, focus=FOCUS)
        planet = Particle(name="m", position=tuple(orbit.periapsis()[:2]), radius=0.11, label="m")
        sun_cm = sun.keypoint("CM")
        self.add(orbit.mobject, sun.mobject, focus_marker(orbit), planet.mobject)
        self.play(FadeIn(orbit.mobject), FadeIn(sun.mobject), FadeIn(planet.mobject))

        # Kepler II: sectors swept in equal time dt at periapsis vs apoapsis.
        traj = KeplerEllipseTrajectory(orbit=orbit, period=PERIOD)
        dt = 0.6

        def theta(t):
            return traj.state_at(t).observables["theta"]

        peri_sector = swept_area(orbit, theta(0.0), theta(dt), color="#FFD43B", opacity=0.5)
        apo_sector = swept_area(orbit, theta(PERIOD / 2), theta(PERIOD / 2 + dt),
                                color="#FFD43B", opacity=0.5)
        cap = Text("equal areas swept in equal times (Kepler II)",
                   font_size=22, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(peri_sector), FadeIn(apo_sector), FadeIn(cap))
        self.wait(0.4)

        # Live overlays + the r-vs-t graph.
        radius = radius_vector(sun_cm, planet)
        gravity = central_force_arrow(planet, sun_cm, scale=0.9)
        graph = GraphBinding(x=TimeSignal(), y=QuantitySignal(ref=QuantityRef("r")),
                             x_range=(0.0, PERIOD), y_range=(0.0, A * (1 + E) + 0.3))
        graph_group = graph.build(traj, 0.0, PERIOD, n=120).scale(0.62)
        graph_group.to_corner(np.array([1.0, 1.0, 0.0]), buff=0.4)
        gl = Text("r vs t", font_size=18, color=WHITE).next_to(graph_group, UP, buff=0.08)
        cap2 = Text("radius + gravity track the planet; r rises to apoapsis and falls back",
                    font_size=20, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(radius), FadeIn(gravity), FadeIn(graph_group), FadeIn(gl),
                  cap.animate.become(cap2))

        clock = ValueTracker(0.0)

        def orbit_update(_m):
            t = clock.get_value()
            pos = traj.state_at(t).entities["m"].pose.position
            planet.mobject.move_to([pos[0], pos[1], 0.0])
            planet.keypoints["CM"] = np.array([pos[0], pos[1], 0.0])
            radius.become(radius_vector(sun_cm, planet))
            gravity.become(central_force_arrow(planet, sun_cm, scale=0.9))

        planet.mobject.add_updater(orbit_update)
        graph.bind(self, clock)
        self.play(clock.animate.set_value(PERIOD), run_time=10.0, rate_func=lambda x: x)
        planet.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
