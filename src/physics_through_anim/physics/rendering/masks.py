"""Reusable cosmetic mask library: flames, plumes, rocket bodies (Milestone M17).

Masks are physics-free decoration drawn by the SVG renderer. Each builder draws
an SVG shape for a ``MaskSpec`` at a resolved world anchor. They are transparent
by default (``opacity``). Register a new mask with ``@register_mask("name")``.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from xml.etree.ElementTree import Element, SubElement

__all__ = ["MASK_BUILDERS", "register_mask", "draw_mask"]

# name -> builder(svg, spec, anchor_world, to_px)
MASK_BUILDERS: dict[str, Callable] = {}


def register_mask(*names: str):
    def deco(fn: Callable) -> Callable:
        for name in names:
            MASK_BUILDERS[name] = fn
        return fn

    return deco


def draw_mask(svg: Element, spec, anchor, to_px) -> None:
    """Draw ``spec`` at world ``anchor`` if its kind is a registered mask."""
    builder = MASK_BUILDERS.get(spec.kind)
    if builder is not None:
        builder(svg, spec, anchor, to_px)


def _unit(direction) -> tuple[float, float]:
    dx, dy = float(direction[0]), float(direction[1])
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _poly(svg: Element, points_world, to_px, color: str, opacity: float) -> None:
    pts = " ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in (to_px(*p) for p in points_world))
    SubElement(svg, "polygon", points=pts, fill=color, **{"fill-opacity": f"{opacity:g}"})


@register_mask("plume", "flame", "exhaust")
def _plume(svg: Element, spec, anchor, to_px) -> None:
    """A tapered translucent flame/plume (the fuel-discharge mask)."""
    ux, uy = _unit(spec.direction)
    px, py = -uy, ux  # perpendicular
    ax, ay = anchor
    half = spec.width / 2.0

    def at(fwd: float, side: float) -> tuple[float, float]:
        return (ax + ux * fwd + px * side, ay + uy * fwd + py * side)

    # Outer plume: base -> bulge -> tip -> bulge -> base.
    outer = [at(0.0, half), at(spec.length * 0.45, spec.width * 0.75), at(spec.length, 0.0),
             at(spec.length * 0.45, -spec.width * 0.75), at(0.0, -half)]
    _poly(svg, outer, to_px, spec.color, spec.opacity)
    # Inner hotter core (shorter, brighter, slightly more opaque).
    inner = [at(0.0, half * 0.5), at(spec.length * 0.4, spec.width * 0.4),
             at(spec.length * 0.7, 0.0), at(spec.length * 0.4, -spec.width * 0.4),
             at(0.0, -half * 0.5)]
    _poly(svg, inner, to_px, "#ffd43b", min(spec.opacity + 0.2, 1.0))


@register_mask("rocket", "body")
def _rocket(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic rocket body: barrel + nose cone + two fins (transparent)."""
    ax, ay = anchor
    half_w = spec.width / 2.0
    half_h = spec.length / 2.0
    # Barrel (world up = +y): rectangle from ay-half_h to ay+half_h*0.6.
    top = ay + half_h * 0.6
    outline = [(ax - half_w, ay - half_h), (ax - half_w, top), (ax, ay + half_h),  # nose cone
               (ax + half_w, top), (ax + half_w, ay - half_h)]
    _poly(svg, outline, to_px, spec.color, spec.opacity)
    # Fins at the base.
    _poly(svg, [(ax - half_w, ay - half_h * 0.6), (ax - half_w * 1.8, ay - half_h),
                (ax - half_w, ay - half_h)], to_px, spec.color, spec.opacity)
    _poly(svg, [(ax + half_w, ay - half_h * 0.6), (ax + half_w * 1.8, ay - half_h),
                (ax + half_w, ay - half_h)], to_px, spec.color, spec.opacity)


@register_mask("ellipse", "blob")
def _ellipse(svg: Element, spec, anchor, to_px) -> None:
    """A translucent ellipse/blob (smoke, cloud, generic decoration)."""
    cx, cy = to_px(*anchor)
    edge_x, _ = to_px(anchor[0] + spec.width / 2.0, anchor[1])
    _, edge_y = to_px(anchor[0], anchor[1] + spec.length / 2.0)
    SubElement(svg, "ellipse", cx=str(cx), cy=str(cy),
               rx=str(round(abs(edge_x - cx), 1)), ry=str(round(abs(edge_y - cy), 1)),
               fill=spec.color, **{"fill-opacity": f"{spec.opacity:g}"})


@register_mask("box", "rect")
def _box(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic rectangle (a point-mass block skin). Physics point is the anchor."""
    cx, cy = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    corners = [(cx - hw, cy - hh), (cx - hw, cy + hh), (cx + hw, cy + hh), (cx + hw, cy - hh)]
    _poly(svg, corners, to_px, spec.color, spec.opacity)


@register_mask("hopper", "funnel")
def _hopper(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic hopper/funnel: a wide mouth narrowing to a spout (transparent)."""
    ax, ay = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    spout = hw * 0.22
    outline = [(ax - hw, ay + hh), (ax + hw, ay + hh),
               (ax + spout, ay - hh), (ax - spout, ay - hh)]
    _poly(svg, outline, to_px, spec.color, spec.opacity)


@register_mask("belt", "conveyor_belt")
def _belt(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic conveyor belt: a band on two rollers with motion chevrons."""
    ax, ay = anchor
    hw = spec.width / 2.0
    r = spec.length / 2.0
    op = {"stroke-opacity": f"{spec.opacity:g}"}
    for sx in (-hw, hw):  # end rollers
        cx, cy = to_px(ax + sx, ay)
        ex, _ = to_px(ax + sx + r, ay)
        SubElement(svg, "circle", cx=str(cx), cy=str(cy), r=str(round(abs(ex - cx), 1)),
                   fill="none", stroke=spec.color, **{"stroke-width": "2"}, **op)
    for sy in (r, -r):  # top & bottom of the band
        x1, y1 = to_px(ax - hw, ay + sy)
        x2, y2 = to_px(ax + hw, ay + sy)
        SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                   stroke=spec.color, **{"stroke-width": "2"}, **op)
    n = max(3, int(spec.width / 0.7))
    for i in range(n):  # motion chevrons (point along +x)
        cx = ax - hw + (i + 0.5) / n * spec.width
        p1 = to_px(cx - 0.12, ay + r * 0.45)
        p2 = to_px(cx + 0.12, ay)
        p3 = to_px(cx - 0.12, ay - r * 0.45)
        SubElement(svg, "polyline",
                   points=f"{p1[0]},{p1[1]} {p2[0]},{p2[1]} {p3[0]},{p3[1]}",
                   fill="none", stroke=spec.color, **{"stroke-width": "1.5"}, **op)


@register_mask("sand", "grains")
def _sand(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic 'block of sand': a clump of jittered grains filling a box."""
    ax, ay = anchor
    hw, hh = spec.width / 2.0, spec.length / 2.0
    cols = max(3, int(spec.width / 0.16))
    rows = max(2, int(spec.length / 0.16))
    for row in range(rows):
        for col in range(cols):
            k = row * cols + col
            jx, jy = 0.05 * math.sin(12.9898 * k), 0.05 * math.cos(7.7233 * k)
            wx = ax - hw + (col + 0.5) / cols * spec.width + jx
            wy = ay - hh + (row + 0.5) / rows * spec.length + jy
            px, py = to_px(wx, wy)
            SubElement(svg, "circle", cx=str(round(px, 1)), cy=str(round(py, 1)),
                       r="2.4", fill=spec.color, **{"fill-opacity": f"{spec.opacity:g}"})


def _spring_axis(spec, anchor) -> tuple[float, float, float, float]:
    """The two spring ends ``(ax, ay, bx, by)`` from ``points`` or anchor+direction."""
    if len(spec.points) >= 2:
        (ax, ay), (bx, by) = spec.points[0], spec.points[1]
        return float(ax), float(ay), float(bx), float(by)
    ux, uy = _unit(spec.direction)
    ax, ay = anchor
    return ax, ay, ax + ux * spec.length, ay + uy * spec.length


def _spring_samples(ax, ay, bx, by, spec) -> list[tuple[float, float]]:
    """World-space points of a helix/coil between the two ends (straight lead-ins)."""
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy) or 1.0
    px, py = -dy / length, dx / length  # perpendicular unit
    amp = spec.width / 2.0
    coils = max(1, spec.coils)
    lead = 0.15  # straight lead-in fraction at each end
    n = max(coils * 12, 24)
    pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        s = i / n
        if lead <= s <= 1.0 - lead:
            u = (s - lead) / (1.0 - 2.0 * lead)
            side = amp * math.sin(2.0 * math.pi * coils * u)
        else:
            side = 0.0
        pts.append((ax + dx * s + px * side, ay + dy * s + py * side))
    return pts


@register_mask("spring", "helix", "coil")
def _spring(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic, massless helix/coil between its two key ends (separation may vary)."""
    ax, ay, bx, by = _spring_axis(spec, anchor)
    pts = [to_px(x, y) for x, y in _spring_samples(ax, ay, bx, by, spec)]
    SubElement(svg, "polyline",
               points=" ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in pts),
               fill="none", stroke=spec.color,
               **{"stroke-width": "2.5", "stroke-opacity": f"{spec.opacity:g}",
                  "stroke-linejoin": "round", "stroke-linecap": "round"})
    for x, y in (pts[0], pts[-1]):  # the two key points (spring ends)
        SubElement(svg, "circle", cx=str(round(x, 1)), cy=str(round(y, 1)), r="4",
                   fill=spec.color, stroke="#0f1117", **{"stroke-width": "1"})


@register_mask("chain")
def _chain(svg: Element, spec, anchor, to_px) -> None:
    """A cosmetic chain of interlocked oval links along ``points``; ends shown."""
    pts = [to_px(*p) for p in (list(spec.points) or [anchor])]
    if len(pts) < 2:
        return
    link_op = min(spec.opacity + 0.4, 1.0)  # links read stronger than a flat ribbon
    # Faint guide ribbon under the links.
    SubElement(svg, "polyline",
               points=" ".join(f"{round(x, 1)},{round(y, 1)}" for x, y in pts),
               fill="none", stroke=spec.color,
               **{"stroke-width": "2", "stroke-opacity": f"{spec.opacity * 0.5:g}"})
    # Walk the polyline in screen space, placing alternating oval links so they interlock.
    step = 18.0
    idx = 0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:], strict=False):
        seg = math.hypot(x1 - x0, y1 - y0)
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        for k in range(max(int(seg / step), 1)):
            t = (k + 0.5) / max(int(seg / step), 1)
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            rx, ry = (12, 6) if idx % 2 == 0 else (6, 12)  # alternate to interlock
            SubElement(svg, "ellipse", cx=str(round(cx, 1)), cy=str(round(cy, 1)),
                       rx=str(rx), ry=str(ry), fill="none", stroke=spec.color,
                       transform=f"rotate({ang:.1f} {cx:.1f} {cy:.1f})",
                       **{"stroke-width": "2.5", "stroke-opacity": f"{link_op:g}"})
            idx += 1
    for x, y in (pts[0], pts[-1]):  # the ends, shown clearly
        SubElement(svg, "circle", cx=str(round(x, 1)), cy=str(round(y, 1)), r="5",
                   fill=spec.color, stroke="#0f1117", **{"stroke-width": "1"})


