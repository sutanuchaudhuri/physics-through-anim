"""SVG snapshot renderer: a dependency-free, real "spec -> picture" engine.

Builds the assembly from the plan, freezes its live keypoints, and draws a static
SVG: blocks as rectangles, round bodies as circles, everything else as a labelled
dot, plus a line for every rope/relation. Proves an XML/JSON plan becomes a real
viewable image without Manim.
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.rendering.base import Renderer, register
from physics_through_anim.physics.rendering.masks import draw_mask
from physics_through_anim.physics.rendering.style import ResolvedStyle, resolve_style
from physics_through_anim.physics.serialization.assembly_io import plan_to_assembly
from physics_through_anim.physics.serialization.state_io import AssetSnapshot, snapshot_assembly

_W, _H, _MARGIN = 800, 600, 40
_DEFAULT_STYLE = ResolvedStyle()
# Ghost frames (timestep transforms shown statically in SVG): faded + dotted.
_GHOST_STYLE = ResolvedStyle(stroke_opacity=0.4, fill_opacity=0.08, dash="2,3")
# label placement -> (dx_px, dy_px, text-anchor)
_LABEL_OFFSET = {
    "top": (0, -10, "middle"), "bottom": (0, 18, "middle"),
    "left": (-9, 4, "end"), "right": (9, 4, "start"),
    "top_left": (-8, -8, "end"), "top_right": (8, -8, "start"),
    "bottom_left": (-8, 16, "end"), "bottom_right": (8, 16, "start"),
    "center": (0, 4, "middle"), "auto": (6, -6, "start"),
}


def _draw_text(svg: Element, text: str, anchor_px, placement: str, color: str,
               *, size: str = "14", bold: bool = False) -> None:
    dx, dy, text_anchor = _LABEL_OFFSET.get(str(placement), _LABEL_OFFSET["auto"])
    attrs = {"font-size": size, "font-family": "sans-serif", "text-anchor": text_anchor}
    if bold:
        attrs["font-weight"] = "bold"
    el = SubElement(svg, "text", x=str(round(anchor_px[0] + dx, 1)),
                    y=str(round(anchor_px[1] + dy, 1)), fill=color, **attrs)
    el.text = text


def _effective(placement, default: str) -> str:
    """A node's placement, or the plan default when the node says ``auto``."""
    p = str(placement)
    return default if p == "auto" else p


def _resolve_masks(plan, assembly) -> list:
    """Resolve each MaskSpec to (spec, anchor_world)."""
    out = []
    for mask in plan.masks:
        if mask.at:
            try:
                p = assembly.resolve(mask.at)
                anchor = (float(p[0]), float(p[1]))
            except KeyError:
                continue
        elif mask.point is not None:
            anchor = (float(mask.point[0]), float(mask.point[1]))
        elif mask.points:  # path mask (chain) -- anchor at its first point
            anchor = (float(mask.points[0][0]), float(mask.points[0][1]))
        else:
            continue
        out.append((mask, anchor))
    return out
_ROUND = {"Disk", "Ring", "Hoop", "Sphere2D", "Cylinder", "CircularBody", "Pulley"}
# Relation kinds drawn as a connecting line (physical links); ropes draw via their
# own connector entity, so they are omitted here.
_LINK_KINDS = {"distance", "rope_length", "hang"}
# VectorSpec.role -> arrow colour (SKILL Rule 2 palette, as standalone hex).
_ROLE_COLORS = {
    "velocity": "#4dabf7", "acceleration": "#ff2d95", "angular": "#20c997",
    "force": "#ffd43b", "weight": "#e64980", "normal": "#51cf66",
    "friction": "#ffa94d", "tension": "#0ca678", "momentum": "#845ef7",
    "position": "#ffd43b", "radius": "#ff922b",
}


def _representative(snap: AssetSnapshot) -> tuple[float, float]:
    if "CM" in snap.keypoints:
        return snap.keypoints["CM"]
    pts = list(snap.keypoints.values())
    if not pts:
        return (0.0, 0.0)
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


@register
class SvgRenderer(Renderer):
    """Render a static SVG snapshot of a plan's assembly (no external deps)."""

    name = "svg"
    kind = "snapshot"
    default_suffix = ".svg"

    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        assembly = plan_to_assembly(plan)
        snapshot = snapshot_assembly(assembly)
        reps = {a.name: _representative(a) for a in snapshot.assets}
        markers = _resolve_markers(plan, assembly)
        vectors = _resolve_vectors(plan, assembly)
        ghosts = _resolve_ghosts(plan, assembly, snapshot)
        masks = _resolve_masks(plan, assembly)
        default_placement = str(plan.label_placement)

        xs = [p[0] for a in snapshot.assets for p in a.keypoints.values()]
        ys = [p[1] for a in snapshot.assets for p in a.keypoints.values()]
        for pt, _, _, _ in markers:
            xs.append(pt[0])
            ys.append(pt[1])
        for base, tip, _, _, _ in vectors:
            xs += [base[0], tip[0]]
            ys += [base[1], tip[1]]
        for path in plan.paths:
            pts = _path_points(path)
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
        for ghost in ghosts:
            xs += [p[0] for p in ghost.keypoints.values()]
            ys += [p[1] for p in ghost.keypoints.values()]
        for spec, anchor in masks:
            tip = (anchor[0] + spec.direction[0] * spec.length,
                   anchor[1] + spec.direction[1] * spec.length)
            xs += [anchor[0] - spec.width, anchor[0] + spec.width, tip[0]]
            ys += [anchor[1] - spec.length, anchor[1] + spec.length, tip[1]]
            xs += [p[0] for p in spec.points]
            ys += [p[1] for p in spec.points]
        to_px = _projector(min(xs or [0.0]), max(xs or [0.0]),
                           min(ys or [0.0]), max(ys or [0.0]))

        svg = Element("svg", xmlns="http://www.w3.org/2000/svg",
                      width=str(_W), height=str(_H),
                      viewBox=f"0 0 {_W} {_H}")
        defs = SubElement(svg, "defs")
        SubElement(SubElement(defs, "pattern", id="hatch", width="6", height="6",
                              patternTransform="rotate(45)",
                              patternUnits="userSpaceOnUse"),
                   "line", x1="0", y1="0", x2="0", y2="6",
                   stroke="#c8d0da", **{"stroke-width": "1.2"})
        SubElement(svg, "rect", width=str(_W), height=str(_H), fill="#0f1117")

        for spec, anchor in masks:  # cosmetic, physics-free overlays (bottom layer)
            draw_mask(svg, spec, anchor, to_px)

        styles = {e.name: resolve_style(e.style) for e in plan.entities}
        labels = {e.name: e.label for e in plan.entities}
        # World y of horizontal supports (ceilings/floors) -> hinge brackets mount to them.
        support_ys = [a.keypoints["start"][1] for a in snapshot.assets
                      if {"start", "end"} <= a.keypoints.keys()]

        for rel in assembly.relations:
            if len(rel.participants) < 2 or rel.kind.value not in _LINK_KINDS:
                continue
            a, b = rel.participants[0], rel.participants[1]
            if a in reps and b in reps:
                x1, y1 = to_px(*reps[a])
                x2, y2 = to_px(*reps[b])
                SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                           stroke="#8bd", **{"stroke-width": "2"})

        for asset in snapshot.assets:
            if asset.kind in ("Hinge", "PinJoint") and "H" in asset.keypoints:
                _draw_hinge(svg, asset, to_px, support_ys)
            else:
                _draw_asset(svg, asset, to_px, styles.get(asset.name, _DEFAULT_STYLE),
                            labels.get(asset.name), default_placement)
        for ghost in ghosts:  # timestep transforms shown as fading/dotted ghosts
            _draw_asset(svg, ghost, to_px, _GHOST_STYLE, None)
        for path in plan.paths:
            _draw_path(svg, path, to_px)
        for base, tip, label, color, placement in vectors:
            _draw_vector(svg, base, tip, label, color, _effective(placement, default_placement),
                         to_px)
        for pt, label, color, placement in markers:
            _draw_marker(svg, pt, label, color, _effective(placement, default_placement), to_px)

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(tostring(svg, encoding="unicode"), encoding="utf-8")
        return output


def _resolve_markers(plan, assembly) -> list:
    """Resolve each MarkerSpec to a world point (from ``at`` ref or explicit ``point``)."""
    out = []
    for marker in plan.markers:
        if marker.at:
            try:
                p = assembly.resolve(marker.at)
                point = (float(p[0]), float(p[1]))
            except KeyError:
                continue
        elif marker.point is not None:
            point = (float(marker.point[0]), float(marker.point[1]))
        else:
            continue
        label = marker.label if marker.show_label else ""  # dot always; label optional
        out.append((point, label, marker.color or "#ff4444", marker.placement))
    return out


def _draw_marker(svg: Element, point, label: str, color: str, placement, to_px) -> None:
    anchor = to_px(*point)
    SubElement(svg, "circle", cx=str(anchor[0]), cy=str(anchor[1]), r="6",
               fill=color, stroke="#ffffff", **{"stroke-width": "1.5"})
    if label:
        _draw_text(svg, label, anchor, placement, color, bold=True)


def _resolve_vectors(plan, assembly) -> list:
    """Resolve each VectorSpec to (base, tip, label, colour, placement)."""
    out = []
    for vec in plan.vectors:
        if not vec.anchor or vec.vector is None:
            continue
        try:
            p = assembly.resolve(vec.anchor)
        except KeyError:
            continue
        base = (float(p[0]), float(p[1]))
        tip = (base[0] + float(vec.vector[0]), base[1] + float(vec.vector[1]))
        label = vec.label if vec.show_label else ""
        out.append((base, tip, label, _ROLE_COLORS.get(vec.role, "#ffd43b"), vec.placement))
    return out


def _draw_vector(svg: Element, base, tip, label: str, color: str, placement: str, to_px) -> None:
    x1, y1 = to_px(*base)
    x2, y2 = to_px(*tip)
    SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
               stroke=color, **{"stroke-width": "3"})
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 10.0
    left = (x2 - size * math.cos(ang - 0.5), y2 - size * math.sin(ang - 0.5))
    right = (x2 - size * math.cos(ang + 0.5), y2 - size * math.sin(ang + 0.5))
    SubElement(svg, "polygon",
               points=f"{x2},{y2} {left[0]:.1f},{left[1]:.1f} {right[0]:.1f},{right[1]:.1f}",
               fill=color)
    if label:
        _draw_text(svg, label, (x2, y2), placement, color, size="13")


def _path_points(path) -> list:
    """A path's world points, expanding ``kind="parabola"`` into an arch."""
    if path.kind == "parabola" and len(path.points) >= 2:
        (x0, y0), (x1, y1) = path.points[0], path.points[-1]
        n = max(int(path.samples), 2)
        out = []
        for i in range(n + 1):
            t = i / n
            # linear chord + parabolic bulge (4h t(1-t)) upward at the midpoint
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + path.height * 4.0 * t * (1.0 - t)))
        return out
    return list(path.points)


def _draw_path(svg: Element, path, to_px) -> None:
    pts = _path_points(path)
    if len(pts) < 2:
        return
    coords = " ".join(f"{x},{y}" for x, y in (to_px(*p) for p in pts))
    tag = "polygon" if path.closed else "polyline"
    SubElement(svg, tag, points=coords, fill="none", stroke=path.color,
               **{"stroke-width": "2", "stroke-dasharray": "5,4"})
    if path.label:
        lx, ly = to_px(*pts[-1])
        text = SubElement(svg, "text", x=str(lx + 6), y=str(ly),
                          fill=path.color, **{"font-size": "13", "font-family": "sans-serif"})
        text.text = path.label


def _rotate_point(p, pivot, angle_rad):
    dx, dy = p[0] - pivot[0], p[1] - pivot[1]
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return (pivot[0] + dx * c - dy * s, pivot[1] + dx * s + dy * c)


def _resolve_ghosts(plan, assembly, snapshot):
    """Ghost snapshots for each timestep transform (a static strobe of the motion)."""
    base = {a.name: a for a in snapshot.assets}
    current: dict[str, dict] = {}
    ghosts = []
    for step in sorted(plan.steps, key=lambda s: s.at):
        for tf in step.transforms:
            src = base.get(tf.target)
            if src is None:
                continue
            kp = current.get(tf.target) or dict(src.keypoints)
            if tf.translate:
                dx, dy = float(tf.translate[0]), float(tf.translate[1])
                kp = {k: (v[0] + dx, v[1] + dy) for k, v in kp.items()}
            if tf.rotate_deg:
                angle = math.radians(tf.rotate_deg)
                pivot = None
                if tf.about:
                    try:
                        p = assembly.resolve(tf.about)
                        pivot = (float(p[0]), float(p[1]))
                    except KeyError:
                        pivot = None
                if pivot is None:
                    pivot = kp.get("CM", (0.0, 0.0))
                kp = {k: _rotate_point(v, pivot, angle) for k, v in kp.items()}
            current[tf.target] = kp
            ghosts.append(AssetSnapshot(name=src.name, kind=src.kind,
                                        color=src.color, keypoints=kp))
    return ghosts


def _projector(min_x, max_x, min_y, max_y):
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)
    scale = min((_W - 2 * _MARGIN) / span_x, (_H - 2 * _MARGIN) / span_y)

    def to_px(wx: float, wy: float) -> tuple[float, float]:
        px = _MARGIN + (wx - min_x) * scale
        py = _H - (_MARGIN + (wy - min_y) * scale)  # flip y (world up -> screen down)
        return (round(px, 2), round(py, 2))

    return to_px


def _draw_asset(svg: Element, asset: AssetSnapshot, to_px, style: ResolvedStyle,
                label_spec=None, default_placement: str = "auto") -> None:
    kp = asset.keypoints
    stroke = asset.color or "#8bd"
    fill = "url(#hatch)" if style.hashed else (asset.color or "#2a3f6b")
    attrs = {
        "fill": fill,
        "fill-opacity": "1" if style.hashed else f"{style.fill_opacity:g}",
        "stroke": stroke,
        "stroke-opacity": f"{style.stroke_opacity:g}",
        "stroke-width": "2",
    }
    if style.dash:
        attrs["stroke-dasharray"] = style.dash
    corners = {"left", "right", "top", "bottom"}
    if asset.kind == "Pulley" and "axle" in kp:
        cx, cy = to_px(*kp["axle"])
        rim = [to_px(*v) for k, v in kp.items() if k != "axle"]
        r = max((math.hypot(px - cx, py - cy) for px, py in rim), default=14.0)
        SubElement(svg, "circle", cx=str(cx), cy=str(cy), r=str(round(r, 2)), **attrs)
        SubElement(svg, "circle", cx=str(cx), cy=str(cy), r="3", fill=stroke)  # axle
        for px, py in rim:  # rope-departure points on the rim
            SubElement(svg, "circle", cx=str(px), cy=str(py), r="4",
                       fill="#ffd43b", stroke="#0f1117", **{"stroke-width": "1"})
    elif asset.kind in _ROUND and "CM" in kp and "right" in kp:
        cx, cy = to_px(*kp["CM"])
        rx, _ = to_px(*kp["right"])
        SubElement(svg, "circle", cx=str(cx), cy=str(cy), r=str(round(abs(rx - cx), 2)), **attrs)
    elif corners <= kp.keys():
        x1, y1 = to_px(kp["left"][0], kp["top"][1])
        x2, y2 = to_px(kp["right"][0], kp["bottom"][1])
        SubElement(svg, "rect", x=str(min(x1, x2)), y=str(min(y1, y2)),
                   width=str(abs(x2 - x1)), height=str(abs(y2 - y1)), **attrs)
    elif {"start", "end"} <= kp.keys():
        x1, y1 = to_px(*kp["start"])
        x2, y2 = to_px(*kp["end"])
        line = {"stroke": asset.color or "#9aa4b2", "stroke-width": "4",
                "stroke-opacity": f"{style.stroke_opacity:g}"}
        if style.dash:
            line["stroke-dasharray"] = style.dash
        SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2), **line)
    elif {"top_left", "top_right"} <= kp.keys():
        x1, y1 = to_px(*kp["top_left"])
        x2, y2 = to_px(*kp["top_right"])
        SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                   stroke=asset.color or "#9aa4b2", **{"stroke-width": "4"})
    elif {"from", "to"} <= kp.keys():
        # A connector (rope/cable/link): draw the segment between its ends.
        x1, y1 = to_px(*kp["from"])
        x2, y2 = to_px(*kp["to"])
        line = {"stroke": asset.color or "#0ca678", "stroke-width": "3",
                "stroke-opacity": f"{style.stroke_opacity:g}"}
        if style.dash:
            line["stroke-dasharray"] = style.dash
        SubElement(svg, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2), **line)
        for end in ("from", "to"):  # rope end points
            ex, ey = to_px(*kp[end])
            SubElement(svg, "circle", cx=str(ex), cy=str(ey), r="3", fill=asset.color or "#0ca678")
    else:
        for point in kp.values():
            cx, cy = to_px(*point)
            SubElement(svg, "circle", cx=str(cx), cy=str(cy), r="3", fill=stroke)
    _draw_style_marks(svg, asset, to_px, style)
    if label_spec is not None and label_spec.show:
        if label_spec.at is not None:
            anchor = to_px(float(label_spec.at[0]), float(label_spec.at[1]))
            placement = "center"
        else:
            anchor = to_px(*_representative(asset))
            placement = _effective(label_spec.placement, default_placement)
        _draw_text(svg, label_spec.text or asset.name, anchor, placement, "#e6e6e6")


def _draw_hinge(svg: Element, asset: AssetSnapshot, to_px, support_ys: list) -> None:
    """A pin/hinge glyph: a triangular bracket from a mount (ceiling above) to the pin ``H``."""
    hx, hy = asset.keypoints["H"]
    above = [y for y in support_ys if y > hy + 0.05]
    mount_y = min(above) if above else hy + 0.9  # nearest support above, else a short bracket
    half = 0.32  # bracket half-width in world units
    apex = to_px(hx, hy)
    base_l = to_px(hx - half, mount_y)
    base_r = to_px(hx + half, mount_y)
    SubElement(svg, "polygon",
               points=f"{apex[0]},{apex[1]} {base_l[0]},{base_l[1]} {base_r[0]},{base_r[1]}",
               fill="#868e96", **{"fill-opacity": "0.35", "stroke": "#adb5bd", "stroke-width": "2"})
    # mounting bar + hatch ticks on the support line
    SubElement(svg, "line", x1=str(base_l[0]), y1=str(base_l[1]),
               x2=str(base_r[0]), y2=str(base_r[1]),
               stroke="#adb5bd", **{"stroke-width": "3"})
    for t in range(5):
        x = base_l[0] + (base_r[0] - base_l[0]) * t / 4.0
        SubElement(svg, "line", x1=str(round(x, 1)), y1=str(base_l[1]),
                   x2=str(round(x - 5, 1)), y2=str(base_l[1] - 6),
                   stroke="#adb5bd", **{"stroke-width": "1.5"})
    SubElement(svg, "circle", cx=str(apex[0]), cy=str(apex[1]), r="4",
               fill="#ffd43b", stroke="#0f1117", **{"stroke-width": "1"})  # the pin


def _corner_points(kp: dict) -> list[tuple[str, tuple[float, float]]]:
    """The labelled corners/ends of a body for ``show_corners``/``end_dots``."""
    if {"left", "right", "top", "bottom"} <= kp.keys():
        return [
            ("TL", (kp["left"][0], kp["top"][1])), ("TR", (kp["right"][0], kp["top"][1])),
            ("BR", (kp["right"][0], kp["bottom"][1])), ("BL", (kp["left"][0], kp["bottom"][1])),
        ]
    for pair in (("from", "to"), ("start", "end"), ("a", "b"), ("A", "B")):
        if set(pair) <= kp.keys():
            return [(pair[0], kp[pair[0]]), (pair[1], kp[pair[1]])]
    return []


def _draw_style_marks(svg: Element, asset: AssetSnapshot, to_px, style: ResolvedStyle) -> None:
    if not (style.show_corners or style.end_dots):
        return
    for name, point in _corner_points(asset.keypoints):
        cx, cy = to_px(*point)
        SubElement(svg, "circle", cx=str(cx), cy=str(cy), r="4",
                   fill="#ffd43b", stroke="#0f1117", **{"stroke-width": "1"})
        if style.corner_labels:
            text = SubElement(svg, "text", x=str(cx + 5), y=str(cy - 5),
                              fill="#ffd43b", **{"font-size": "11", "font-family": "sans-serif"})
            text.text = name
