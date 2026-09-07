"""Manim counterparts of the SVG cosmetic mask library (Milestone M17).

Each builder turns a ``MaskSpec`` at a resolved world anchor into a Manim
mobject (in world coordinates), mirroring ``rendering.masks`` so the ``manim``
video engine decorates scenes with the same flames/plumes/rockets/boxes/chains
the SVG renderer draws. Register a new mask with ``@register_manim_mask("name")``.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from manim import Circle, Dot, Ellipse, Line, Polygon, VGroup, VMobject

__all__ = ["MANIM_MASK_BUILDERS", "register_manim_mask", "build_manim_mask"]

# name -> builder(spec, anchor_world) -> VMobject
MANIM_MASK_BUILDERS: dict[str, Callable] = {}


def register_manim_mask(*names: str):
    def deco(fn: Callable) -> Callable:
        for name in names:
            MANIM_MASK_BUILDERS[name] = fn
        return fn

    return deco


def build_manim_mask(spec, anchor) -> VMobject | None:
    """Return a Manim mobject for ``spec`` at world ``anchor`` (or ``None``)."""
    builder = MANIM_MASK_BUILDERS.get(spec.kind)
    return builder(spec, anchor) if builder is not None else None


def _unit(direction) -> tuple[float, float]:
    dx, dy = float(direction[0]), float(direction[1])
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _p(x: float, y: float):
    return [float(x), float(y), 0.0]


def _fill(mobject: VMobject, color: str, opacity: float) -> VMobject:
    mobject.set_fill(color, opacity=opacity)
    mobject.set_stroke(width=0)
    return mobject


@register_manim_mask("plume", "flame", "exhaust")
def _plume(spec, anchor) -> VMobject:
    """A tapered translucent flame/plume with a brighter inner core."""
    ux, uy = _unit(spec.direction)
    px, py = -uy, ux
    ax, ay = anchor
    half = spec.width / 2.0

    def at(fwd: float, side: float):
        return _p(ax + ux * fwd + px * side, ay + uy * fwd + py * side)

    outer = Polygon(
        at(0.0, half), at(spec.length * 0.45, spec.width * 0.75), at(spec.length, 0.0),
        at(spec.length * 0.45, -spec.width * 0.75), at(0.0, -half))
    inner = Polygon(
        at(0.0, half * 0.5), at(spec.length * 0.4, spec.width * 0.4),
        at(spec.length * 0.7, 0.0), at(spec.length * 0.4, -spec.width * 0.4),
        at(0.0, -half * 0.5))
    return VGroup(_fill(outer, spec.color, spec.opacity),
                  _fill(inner, "#ffd43b", min(spec.opacity + 0.2, 1.0)))


@register_manim_mask("rocket", "body")
def _rocket(spec, anchor) -> VMobject:
    """A cosmetic rocket body: barrel + nose cone + two fins."""
    ax, ay = anchor
    half_w = spec.width / 2.0
    half_h = spec.length / 2.0
    top = ay + half_h * 0.6
    body = Polygon(_p(ax - half_w, ay - half_h), _p(ax - half_w, top),
                   _p(ax, ay + half_h), _p(ax + half_w, top), _p(ax + half_w, ay - half_h))
    fin_l = Polygon(_p(ax - half_w, ay - half_h * 0.6),
                    _p(ax - half_w * 1.8, ay - half_h), _p(ax - half_w, ay - half_h))
    fin_r = Polygon(_p(ax + half_w, ay - half_h * 0.6),
                    _p(ax + half_w * 1.8, ay - half_h), _p(ax + half_w, ay - half_h))
    return VGroup(*(_fill(m, spec.color, spec.opacity) for m in (body, fin_l, fin_r)))


@register_manim_mask("ellipse", "blob")
def _ellipse(spec, anchor) -> VMobject:
    """A translucent ellipse/blob (smoke, cloud, generic decoration)."""
    ell = Ellipse(width=spec.width, height=spec.length)
    ell.move_to(_p(*anchor))
    return _fill(ell, spec.color, spec.opacity)


@register_manim_mask("box", "rect")
def _box(spec, anchor) -> VMobject:
    """A cosmetic rectangle (a point-mass block skin). Physics point is the anchor."""
    cx, cy = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    rect = Polygon(_p(cx - hw, cy - hh), _p(cx - hw, cy + hh),
                   _p(cx + hw, cy + hh), _p(cx + hw, cy - hh))
    return _fill(rect, spec.color, spec.opacity)


@register_manim_mask("hopper", "funnel")
def _hopper(spec, anchor) -> VMobject:
    """A cosmetic hopper/funnel: a wide mouth narrowing to a spout (transparent)."""
    ax, ay = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    spout = hw * 0.22
    poly = Polygon(_p(ax - hw, ay + hh), _p(ax + hw, ay + hh),
                   _p(ax + spout, ay - hh), _p(ax - spout, ay - hh))
    return _fill(poly, spec.color, spec.opacity)


@register_manim_mask("belt", "conveyor_belt")
def _belt(spec, anchor) -> VMobject:
    """A cosmetic conveyor belt: a band on two rollers with motion chevrons."""
    ax, ay = anchor
    hw, r = spec.width / 2.0, spec.length / 2.0
    group = VGroup()
    for sx in (-hw, hw):
        roller = Circle(radius=r, stroke_color=spec.color, stroke_width=2,
                        stroke_opacity=spec.opacity).move_to(_p(ax + sx, ay))
        group.add(roller)
    for sy in (r, -r):
        band = Line(_p(ax - hw, ay + sy), _p(ax + hw, ay + sy),
                    stroke_color=spec.color, stroke_width=2)
        band.set_stroke(opacity=spec.opacity)
        group.add(band)
    n = max(3, int(spec.width / 0.7))
    for i in range(n):
        cx = ax - hw + (i + 0.5) / n * spec.width
        chev = VMobject(stroke_color=spec.color, stroke_width=1.5, stroke_opacity=spec.opacity)
        chev.set_points_as_corners([_p(cx - 0.12, ay + r * 0.45), _p(cx + 0.12, ay),
                                    _p(cx - 0.12, ay - r * 0.45)])
        group.add(chev)
    return group


@register_manim_mask("sand", "grains")
def _sand(spec, anchor) -> VMobject:
    """A cosmetic 'block of sand': a clump of jittered grains filling a box."""
    ax, ay = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    cols = max(3, int(spec.width / 0.16))
    rows = max(2, int(spec.length / 0.16))
    group = VGroup()
    for row in range(rows):
        for col in range(cols):
            k = row * cols + col
            jx, jy = 0.05 * math.sin(12.9898 * k), 0.05 * math.cos(7.7233 * k)
            wx = ax - hw + (col + 0.5) / cols * spec.width + jx
            wy = ay - hh + (row + 0.5) / rows * spec.length + jy
            group.add(Dot(_p(wx, wy), radius=0.05, color=spec.color, fill_opacity=spec.opacity))
    return group


@register_manim_mask("spring", "helix", "coil")
def _spring(spec, anchor) -> VMobject:
    """A cosmetic, massless helix/coil between its two key ends (separation may vary)."""
    if len(spec.points) >= 2:
        (ax, ay), (bx, by) = spec.points[0], spec.points[1]
        ax, ay, bx, by = float(ax), float(ay), float(bx), float(by)
    else:
        ux, uy = _unit(spec.direction)
        ax, ay = anchor
        bx, by = ax + ux * spec.length, ay + uy * spec.length
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy) or 1.0
    px, py = -dy / length, dx / length
    amp = spec.width / 2.0
    coils = max(1, spec.coils)
    lead = 0.15
    n = max(coils * 12, 24)
    pts = []
    for i in range(n + 1):
        s = i / n
        if lead <= s <= 1.0 - lead:
            u = (s - lead) / (1.0 - 2.0 * lead)
            side = amp * math.sin(2.0 * math.pi * coils * u)
        else:
            side = 0.0
        pts.append(_p(ax + dx * s + px * side, ay + dy * s + py * side))
    coil = VMobject(stroke_color=spec.color, stroke_width=2.5, stroke_opacity=spec.opacity)
    coil.set_points_as_corners(pts)
    group = VGroup(coil)
    for x, y, _ in (pts[0], pts[-1]):  # the two key points (spring ends)
        end = Circle(radius=0.09, stroke_color="#0f1117", stroke_width=1)
        end.set_fill(spec.color, opacity=1.0).move_to(_p(x, y))
        group.add(end)
    return group


@register_manim_mask("chain")
def _chain(spec, anchor) -> VMobject:
    """A cosmetic chain of interlocked oval links along ``points``; ends shown."""
    pts = [(_p(*p)) for p in (list(spec.points) or [anchor])]
    if len(pts) < 2:
        return VGroup()
    group = VGroup()
    ribbon = VMobject(stroke_color=spec.color, stroke_width=2,
                      stroke_opacity=spec.opacity * 0.5)
    ribbon.set_points_as_corners(pts)
    group.add(ribbon)
    link_op = min(spec.opacity + 0.4, 1.0)
    step = 0.28  # world-unit spacing between links
    idx = 0
    for (x0, y0, _), (x1, y1, _) in zip(pts[:-1], pts[1:], strict=False):
        seg = math.hypot(x1 - x0, y1 - y0)
        ang = math.atan2(y1 - y0, x1 - x0)
        n = max(int(seg / step), 1)
        for k in range(n):
            t = (k + 0.5) / n
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            rw, rh = (0.36, 0.18) if idx % 2 == 0 else (0.18, 0.36)  # alternate to interlock
            link = Ellipse(width=rw, height=rh, stroke_color=spec.color,
                           stroke_width=2.5, stroke_opacity=link_op)
            link.rotate(ang).move_to(_p(cx, cy))
            group.add(link)
            idx += 1
    for x, y, _ in (pts[0], pts[-1]):
        end = Circle(radius=0.09, stroke_color="#0f1117", stroke_width=1)
        end.set_fill(spec.color, opacity=1.0).move_to(_p(x, y))
        group.add(end)
    return group
