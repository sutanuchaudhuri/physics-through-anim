"""Scene 20 -- M12 flagship (probe D): the Galperin infinite-collision counter.

A heavy block M and a light block m between it and a wall. Every impact is an
elastic 1-D collision whose post-velocities are computed by a tiny solver *in the
scene* (outside the assets) -- the library only renders the schedule: blocks move
on piecewise-constant velocities, an EventCounter ticks at each impact, and a
phase-space overlay plots each post-collision state on a circle (the reflections
whose count encodes pi). Velocity STEPs across each impact; position stays
continuous.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    UP,
    WHITE,
    Axes,
    Circle,
    Dot,
    FadeIn,
    Flash,
    Text,
    ValueTracker,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.events import EventSequence
from physics_through_anim.physics.mechanics import Block, Floor, Wall
from physics_through_anim.physics.overlays.events import EventCounter, collision

GROUND_Y = -2.2
X_WALL = -4.6
BIG_M, SMALL_M = 9.0, 1.0
W_BIG, W_SMALL = 1.2, 0.5


def simulate() -> tuple[list[dict], list[dict]]:
    """1-D elastic Galperin sequence. Returns (segments, events); solver, not asset."""
    gap_contact = (W_BIG + W_SMALL) / 2.0
    pm_wall = X_WALL + W_SMALL / 2.0
    pM, pm, vM, vm = 1.8, -2.0, -2.2, 0.0
    t = 0.0
    segments: list[dict] = []
    events: list[dict] = []
    for _ in range(80):
        rel = vM - vm  # d(pM - pm)/dt
        t_bb = (gap_contact - (pM - pm)) / rel if rel < -1e-9 else np.inf
        t_wall = (pm_wall - pm) / vm if vm < -1e-9 else np.inf
        t_next = min(t_bb, t_wall)
        if not np.isfinite(t_next) or t_next > 40.0:
            segments.append({"t": t, "dur": 3.0, "pM": pM, "vM": vM, "pm": pm, "vm": vm})
            break
        segments.append({"t": t, "dur": t_next, "pM": pM, "vM": vM, "pm": pm, "vm": vm})
        pM += vM * t_next
        pm += vm * t_next
        t += t_next
        if t_bb <= t_wall:  # elastic block-block
            nvM = ((BIG_M - SMALL_M) * vM + 2 * SMALL_M * vm) / (BIG_M + SMALL_M)
            nvm = ((SMALL_M - BIG_M) * vm + 2 * BIG_M * vM) / (BIG_M + SMALL_M)
            vM, vm = nvM, nvm
            events.append({"t": t, "kind": "bb", "vM": vM, "vm": vm})
        else:  # elastic wall bounce for m
            vm = -vm
            events.append({"t": t, "kind": "wall", "vM": vM, "vm": vm})
    return segments, events


class GalperinCounter(AssetDemoScene):
    """Heavy + light block bounce between a wall; count impacts, plot phase space."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("20", "Counting collisions", "Galperin: impacts encode pi")
        self.play(FadeIn(header))

        segments, events = simulate()

        floor = Floor(y=GROUND_Y, half_width=7.0)
        wall = Wall(angle_deg=90.0, center=(X_WALL, GROUND_Y + 1.0), length=2.0, facing="right")
        y_big, y_small = GROUND_Y + 0.45, GROUND_Y + 0.25
        big = Block(name="M", width=W_BIG, height=0.9, position=(segments[0]["pM"], y_big),
                    label="M")
        small = Block(name="m", width=W_SMALL, height=0.5, position=(segments[0]["pm"], y_small),
                      label="m")
        mass_labels = Text("M = 9 m", font_size=22, color=WHITE)
        mass_labels.next_to(big.mobject, UP, buff=0.15)
        self.add(floor.mobject, wall.mobject, big.mobject, small.mobject)
        self.play(FadeIn(floor.mobject), FadeIn(wall.mobject), FadeIn(big.mobject),
                  FadeIn(small.mobject), FadeIn(mass_labels))

        # Event counter (symbol only) + phase-space axes with the invariant circle.
        seq = EventSequence()
        for ev in events:
            seq.add(collision("M", "m" if ev["kind"] == "bb" else "wall", t=ev["t"]))
        counter = EventCounter(seq=seq)
        counter_glyph = counter.glyph(0.0).to_corner(np.array([-1.0, 1.0, 0.0]), buff=0.6)

        axes = Axes(x_range=(-8, 8, 4), y_range=(-8, 8, 4), x_length=3.2, y_length=3.2,
                    tips=False).to_corner(np.array([1.0, 1.0, 0.0]), buff=0.5)
        radius = float(np.hypot(np.sqrt(BIG_M) * segments[0]["vM"], 0.0))
        r_screen = float(np.linalg.norm(axes.c2p(radius, 0.0) - axes.c2p(0.0, 0.0)))
        circle = Circle(radius=r_screen, color="#495057", stroke_width=2).move_to(axes.c2p(0, 0))
        ps_label = Text("phase space (v_M, v_m)", font_size=18, color=WHITE)
        ps_label.next_to(axes, DOWN, buff=0.12)

        def phase_point(vM, vm):
            return Dot(axes.c2p(np.sqrt(BIG_M) * vM, np.sqrt(SMALL_M) * vm),
                       color="#FFD43B", radius=0.05)

        dots = [phase_point(segments[0]["vM"], segments[0]["vm"])]
        self.play(FadeIn(counter_glyph), FadeIn(axes), FadeIn(circle), FadeIn(ps_label),
                  FadeIn(dots[0]))

        cap = Text("elastic impacts: velocity jumps, position stays continuous",
                   font_size=21, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(cap))

        # Play each segment, then fire the impact at its end.
        for i, seg in enumerate(segments):
            local = ValueTracker(0.0)

            def move(_m, seg=seg, local=local):
                d = local.get_value()
                big.mobject.move_to([seg["pM"] + seg["vM"] * d, y_big, 0.0])
                small.mobject.move_to([seg["pm"] + seg["vm"] * d, y_small, 0.0])

            big.mobject.add_updater(move)
            run_time = float(np.clip(seg["dur"] * 0.5, 0.12, 1.1))
            self.play(local.animate.set_value(seg["dur"]), run_time=run_time)
            big.mobject.clear_updaters()

            if i < len(events):
                ev = events[i]
                hit = (small if ev["kind"] == "wall" else big).mobject.get_center()
                new_glyph = counter.glyph(ev["t"] + 1e-9).move_to(counter_glyph)
                dot = phase_point(ev["vM"], ev["vm"])
                dots.append(dot)
                self.play(Flash(hit, color="#FFD43B", flash_radius=0.5, run_time=0.35),
                          counter_glyph.animate.become(new_glyph), FadeIn(dot), run_time=0.35)

        total = Text(f"total impacts n = {len(events)}", font_size=24, color="#FFD43B")
        total.to_edge(DOWN, buff=0.4)
        self.play(counter_glyph.animate.become(
            counter.glyph(events[-1]["t"] + 1e-9).move_to(counter_glyph)))
        self.play(cap.animate.become(total))
        self.wait(0.5)
        self.finish_with_narration()
