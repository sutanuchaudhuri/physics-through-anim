"""Deterministic layout regions for the render engine.

Content is placed into named rectangular *regions* (panels / bands) so a scene is
laid out deterministically -- never by eyeballed offsets. The free-body /
kinematics diagram (the ``stage``) carries only vector arrows and their *symbol*
labels (``F``, ``N``, ``v``, ``omega``); equations/formulas belong in the
``equation`` region and full-sentence captions in the ``caption`` region, so a
formula can never land on top of a force arrow.

The boundaries are explicit and reproducible: given the same content, placement is
identical every render. ``avoid_overlap`` resolves symbol-label collisions by
trying candidate sides in a fixed order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Mobject, Rectangle, VGroup, config


class Anchor(StrEnum):
    """A named position inside a region -- use instead of eyeballed coordinates.

    Numeric coordinates are the *last resort* (``CUSTOM``); prefer a named anchor
    plus an optional ``offset`` override.
    """

    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


def _aabb(mob: Mobject) -> tuple[float, float, float, float]:
    """Axis-aligned bounding box ``(x_min, x_max, y_min, y_max)`` of a mobject."""
    return (mob.get_left()[0], mob.get_right()[0], mob.get_bottom()[1], mob.get_top()[1])


def _intersects(a, b, buffer: float = 0.0) -> bool:
    ax0, ax1, ay0, ay1 = a
    bx0, bx1, by0, by1 = b
    return not (
        ax1 + buffer < bx0 or bx1 + buffer < ax0 or ay1 + buffer < by0 or by1 + buffer < ay0
    )


@dataclass(frozen=True)
class Region:
    """An axis-aligned rectangular panel in scene coordinates."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    name: str = ""

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> np.ndarray:
        return np.array([(self.x_min + self.x_max) / 2.0, (self.y_min + self.y_max) / 2.0, 0.0])

    def anchor(self, where: Anchor = Anchor.CENTER, *, offset=(0.0, 0.0),
               pad: float = 0.0) -> np.ndarray:
        """The scene point at a named ``Anchor`` inside this region (+ optional ``offset``).

        e.g. ``left.anchor(Anchor.BOTTOM)`` for a panel title, instead of a magic
        ``[3.4, -1.7, 0.0]``. ``offset`` is the escape hatch when a nudge is needed.
        """
        x0, x1 = self.x_min + pad, self.x_max - pad
        y0, y1 = self.y_min + pad, self.y_max - pad
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        table = {
            Anchor.CENTER: (cx, cy),
            Anchor.TOP: (cx, y1), Anchor.BOTTOM: (cx, y0),
            Anchor.LEFT: (x0, cy), Anchor.RIGHT: (x1, cy),
            Anchor.TOP_LEFT: (x0, y1), Anchor.TOP_RIGHT: (x1, y1),
            Anchor.BOTTOM_LEFT: (x0, y0), Anchor.BOTTOM_RIGHT: (x1, y0),
        }
        px, py = table[Anchor(where)]
        return np.array([px + offset[0], py + offset[1], 0.0])

    def columns(self, n: int, *, gap: float = 0.0) -> list[Region]:
        """Split into ``n`` equal side-by-side sub-regions (e.g. two panels)."""
        w = (self.width - gap * (n - 1)) / n
        return [Region(self.x_min + i * (w + gap), self.x_min + i * (w + gap) + w,
                       self.y_min, self.y_max, f"{self.name}:col{i}") for i in range(n)]

    def rows(self, n: int, *, gap: float = 0.0) -> list[Region]:
        """Split into ``n`` equal stacked sub-regions (top row first)."""
        h = (self.height - gap * (n - 1)) / n
        return [Region(self.x_min, self.x_max,
                       self.y_max - i * (h + gap) - h, self.y_max - i * (h + gap),
                       f"{self.name}:row{i}") for i in range(n)]

    def grid(self, rows: int, cols: int, *, gap: float = 0.0) -> list[Region]:
        """A row-major list of ``rows*cols`` equal cells (a thumbnail grid)."""
        return [cell for row in self.rows(rows, gap=gap) for cell in row.columns(cols, gap=gap)]

    def contains(self, mob: Mobject, *, padding: float = 0.0) -> bool:
        x0, x1, y0, y1 = _aabb(mob)
        return (
            x0 >= self.x_min + padding
            and x1 <= self.x_max - padding
            and y0 >= self.y_min + padding
            and y1 <= self.y_max - padding
        )

    def as_rect(self, **kwargs) -> Rectangle:
        """A boundary rectangle for visually debugging the region."""
        return Rectangle(width=self.width, height=self.height, **kwargs).move_to(self.center)

    def fit(self, mob: Mobject, *, align: str = "center", padding: float = 0.15) -> Mobject:
        """Scale ``mob`` down to fit inside the region (if needed), then align it."""
        avail_w = max(self.width - 2 * padding, 1e-3)
        avail_h = max(self.height - 2 * padding, 1e-3)
        if mob.width > avail_w:
            mob.scale_to_fit_width(avail_w)
        if mob.height > avail_h:
            mob.scale_to_fit_height(avail_h)
        cx, cy = self.center[0], self.center[1]
        hw, hh = mob.width / 2.0, mob.height / 2.0
        targets = {
            "center": (cx, cy),
            "top": (cx, self.y_max - padding - hh),
            "bottom": (cx, self.y_min + padding + hh),
            "left": (self.x_min + padding + hw, cy),
            "right": (self.x_max - padding - hw, cy),
        }
        if align not in targets:
            raise ValueError(f"unknown align {align!r}")
        tx, ty = targets[align]
        mob.move_to([tx, ty, 0.0])
        return mob


def standard_bands(*, margin: float = 0.3, ground_y: float = -2.0) -> dict[str, Region]:
    """Default header / stage / equation / caption bands (SKILL Rule 8, as code)."""
    half_w = config.frame_width / 2.0 - margin
    return {
        "header": Region(-half_w, half_w, 2.9, 3.9, "header"),
        "stage": Region(-half_w, half_w, ground_y, 2.6, "stage"),
        "equation": Region(-half_w, half_w, -3.9, -2.3, "equation"),
        "caption": Region(-half_w, half_w, -3.85, -2.4, "caption"),
    }


def stage_region(*, margin: float = 0.4, ground_y: float = -2.2, top: float = 2.4) -> Region:
    """The usable acting area as one :class:`Region` (for ``.columns``/``.anchor``)."""
    half_w = config.frame_width / 2.0 - margin
    return Region(-half_w, half_w, ground_y, top, "stage")


def _p2(point) -> np.ndarray:
    return np.asarray(point, dtype=float)[:2]


@dataclass
class NamedPoints:
    """A registry of developer-named points -- reference coordinates by **id/enum**
    instead of repeating raw tuples. Keys are strings; ``StrEnum`` members work too
    (e.g. ``class P(StrEnum): LEFT_END = "L"`` -> ``pts[P.LEFT_END]``). It also gives
    the **distance/vector between points by id**, so a translation is named, not
    a magic number.
    """

    points: dict = field(default_factory=dict)

    def set(self, key, point) -> np.ndarray:
        """Register (or overwrite) the point named ``key``; returns it."""
        self.points[str(key)] = _p2(point)
        return self.points[str(key)]

    def define(self, **named) -> NamedPoints:
        """Bulk-define points: ``pts.define(A=(-4.5, 1.2), B=(1.5, 1.2))``."""
        for key, point in named.items():
            self.set(key, point)
        return self

    def at(self, key, region: Region, anchor: Anchor = Anchor.CENTER, *,
           offset=(0.0, 0.0), pad: float = 0.0) -> np.ndarray:
        """Register ``key`` at a region anchor (compose the two layout helpers)."""
        return self.set(key, region.anchor(anchor, offset=offset, pad=pad)[:2])

    def __getitem__(self, key) -> np.ndarray:
        return self.points[str(key)]

    def get(self, key, default=None):
        return self.points.get(str(key), default)

    def __contains__(self, key) -> bool:
        return str(key) in self.points

    def vector(self, a, b) -> np.ndarray:
        """The translation ``b - a`` between two named points."""
        return self[b] - self[a]

    def distance(self, a, b) -> float:
        """The translation distance between two named points, by id."""
        return float(np.linalg.norm(self[b] - self[a]))

    def midpoint(self, a, b) -> np.ndarray:
        return (self[a] + self[b]) / 2.0

    def shifted(self, key, offset) -> np.ndarray:
        """A copy of point ``key`` nudged by ``offset`` (not registered)."""
        return self[key] + _p2(offset)



@dataclass
class Layout:
    """A named set of regions plus placement helpers."""

    regions: dict

    @classmethod
    def standard(cls, **kwargs) -> Layout:
        return cls(regions=standard_bands(**kwargs))

    def region(self, name: str) -> Region:
        return self.regions[name]

    def place(
        self, mob: Mobject, name: str, *, align: str = "center", padding: float = 0.15
    ) -> Mobject:
        return self.region(name).fit(mob, align=align, padding=padding)

    def boundary_frame(self, **kwargs) -> VGroup:
        """Boundary rectangles for every region (debugging the panel boundaries)."""
        return VGroup(*[r.as_rect(**kwargs) for r in self.regions.values()])


def avoid_overlap(
    label: Mobject,
    anchor: Mobject,
    obstacles,
    *,
    dirs=(RIGHT, UP, DOWN, LEFT),
    buff: float = 0.12,
) -> Mobject:
    """Place ``label`` beside ``anchor`` on the first side clear of ``obstacles``.

    Deterministic: tries ``dirs`` in order and keeps the first placement whose
    bounding box intersects no obstacle (falls back to the last side tried).
    """
    obstacle_boxes = [_aabb(o) for o in obstacles]
    last = dirs[-1]
    for direction in dirs:
        label.next_to(anchor, direction, buff=buff)
        last = direction
        if not any(_intersects(_aabb(label), ob, buffer=0.03) for ob in obstacle_boxes):
            return label
    label.next_to(anchor, last, buff=buff)
    return label
