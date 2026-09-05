"""Compose a scene out of smaller *sub-scenes* played sequentially or together.

A ``SubScene`` is a lazily-built, self-contained visual segment (a callable
that returns the mobject(s) to show, plus how long to hold it). ``play_sub
scenes`` then either:

- ``mode="sequential"`` -- fade each sub-scene in, hold, fade it out, before
  the next one, so the screen shows one segment at a time; or
- ``mode="together"`` -- fade every sub-scene in at once (auto-placed into
  quadrant/row anchors, or at explicit ``positions``), hold, fade out
  together, so several segments share the screen.

Builders are deferred (called only when that segment is about to appear) so a
sequential run never has every segment's mobjects on screen at once. Works
with any manim ``Scene`` subclass (including ``SpaceScene``); if the scene has
the ``log_event`` hook from ``scene_logging`` it is used to record each
segment, otherwise it is skipped.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from manim import FadeIn, FadeOut, Mobject, VGroup

Builder = Callable[[], Mobject]


@dataclass
class SubScene:
    """One self-contained visual segment of a larger scene."""

    build: Builder
    hold: float = 1.5
    name: str = ""
    position: Any | None = None  # explicit target center for "together" mode


@dataclass
class _Options:
    fade_in_time: float = 0.6
    fade_out_time: float = 0.6
    spread_x: float = 3.4
    spread_y: float = 1.6
    anchors: list[np.ndarray] = field(default_factory=list)


def default_anchors(n: int, spread_x: float = 3.4, spread_y: float = 1.6) -> list[np.ndarray]:
    """Non-overlapping centers for ``n`` simultaneous sub-scenes.

    1 -> center, 2 -> left/right, 3-4 -> quadrants, 5-6 -> two rows of three.
    For larger ``n`` pass explicit ``SubScene.position`` values instead.
    """
    if n <= 1:
        return [np.array([0.0, 0.0, 0.0])]
    if n == 2:
        return [np.array([-spread_x, 0.0, 0.0]), np.array([spread_x, 0.0, 0.0])]
    quadrants = [
        np.array([-spread_x, spread_y, 0.0]),
        np.array([spread_x, spread_y, 0.0]),
        np.array([-spread_x, -spread_y, 0.0]),
        np.array([spread_x, -spread_y, 0.0]),
    ]
    if n <= 4:
        return quadrants[:n]
    xs = np.linspace(-spread_x - 1.3, spread_x + 1.3, 3)
    rows = [
        *[np.array([x, spread_y, 0.0]) for x in xs],
        *[np.array([x, -spread_y, 0.0]) for x in xs],
    ]
    return rows[:n]


def _maybe_log(scene: Any, label: str, **fields: Any) -> None:
    log = getattr(scene, "log_event", None)
    if callable(log):
        log(label, **fields)


def _play_sequential(
    scene: Any, subscenes: Sequence[SubScene], opts: _Options, keep_last: bool
) -> list[Mobject]:
    shown: list[Mobject] = []
    last_index = len(subscenes) - 1
    for index, sub in enumerate(subscenes):
        mob = sub.build()
        _maybe_log(scene, "subscene_in", name=sub.name or index, mode="sequential")
        scene.play(FadeIn(mob), run_time=opts.fade_in_time)
        scene.wait(sub.hold)
        if index == last_index and keep_last:
            shown.append(mob)
            break
        scene.play(FadeOut(mob), run_time=opts.fade_out_time)
    return shown


def _play_together(
    scene: Any, subscenes: Sequence[SubScene], opts: _Options, hold: float, fade_out: bool
) -> list[Mobject]:
    anchors = opts.anchors or default_anchors(len(subscenes), opts.spread_x, opts.spread_y)
    mobs: list[Mobject] = []
    for index, sub in enumerate(subscenes):
        mob = sub.build()
        target = sub.position if sub.position is not None else anchors[index]
        mob.move_to(target)
        mobs.append(mob)
        _maybe_log(scene, "subscene_in", name=sub.name or index, mode="together")
    scene.play(*[FadeIn(m) for m in mobs], run_time=opts.fade_in_time)
    scene.wait(hold)
    if fade_out:
        scene.play(*[FadeOut(m) for m in mobs], run_time=opts.fade_out_time)
        return []
    return mobs


def play_subscenes(
    scene: Any,
    subscenes: Sequence[SubScene],
    mode: str = "sequential",
    *,
    hold: float = 2.0,
    keep_last: bool = False,
    fade_out: bool = True,
    fade_in_time: float = 0.6,
    fade_out_time: float = 0.6,
    positions: Sequence[Any] | None = None,
    spread_x: float = 3.4,
    spread_y: float = 1.6,
) -> list[Mobject]:
    """Play a list of ``SubScene``s on ``scene``.

    mode="sequential": fade each in, hold ``sub.hold``, fade out, then next.
        ``keep_last=True`` leaves the final segment on screen (returned).
    mode="together": fade all in at once (auto-anchored, or at ``positions`` /
        each ``SubScene.position``), hold ``hold`` seconds, then fade out
        together unless ``fade_out=False`` (in which case the mobjects are
        returned so the caller can keep animating them).

    Returns the mobjects still on screen after the call (empty if all faded).
    """
    opts = _Options(
        fade_in_time=fade_in_time,
        fade_out_time=fade_out_time,
        spread_x=spread_x,
        spread_y=spread_y,
        anchors=[np.array(p, dtype=float) for p in positions] if positions else [],
    )
    if mode == "sequential":
        return _play_sequential(scene, subscenes, opts, keep_last)
    if mode == "together":
        return _play_together(scene, subscenes, opts, hold, fade_out)
    raise ValueError(f"mode must be 'sequential' or 'together', got {mode!r}")


def subscene_group(subscenes: Sequence[SubScene], **kwargs: Any) -> VGroup:
    """Build and position every sub-scene without playing anything -- handy for
    a static poster frame of a 'together' layout."""
    anchors = default_anchors(
        len(subscenes), kwargs.get("spread_x", 3.4), kwargs.get("spread_y", 1.6)
    )
    group = VGroup()
    for index, sub in enumerate(subscenes):
        mob = sub.build()
        target = sub.position if sub.position is not None else anchors[index]
        group.add(mob.move_to(target))
    return group
