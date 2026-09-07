"""Shared render styling: map a ``StyleSpec`` to concrete draw attributes.

Both the SVG and Manim renderers resolve a ``StyleSpec`` through here so a scene
looks the same across engines. Kept renderer-agnostic (plain numbers/flags).
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.problems.scene_plan import StyleSpec

__all__ = ["DISPLAY_MODES", "FILL_MODES", "ResolvedStyle", "resolve_style"]

DISPLAY_MODES = ("solid", "fade", "dotted", "dashed")
FILL_MODES = ("solid", "hashed", "none")

_DASH = {"dotted": "2,3", "dashed": "7,5"}


@dataclass(frozen=True)
class ResolvedStyle:
    """Concrete draw attributes for one entity."""

    stroke_opacity: float = 1.0
    fill_opacity: float = 0.35
    dash: str | None = None  # SVG stroke-dasharray (also drives Manim dashing)
    hashed: bool = False
    show_corners: bool = False
    corner_labels: bool = False
    end_dots: bool = False


def resolve_style(style: StyleSpec) -> ResolvedStyle:
    """Turn a ``StyleSpec`` into concrete opacities / dash / flags."""
    display = style.display or "solid"
    fill = style.fill or "solid"
    stroke_opacity = 0.4 if display == "fade" else 1.0
    fill_opacity = 0.15 if display == "fade" else 0.35
    if style.opacity is not None:
        stroke_opacity = style.opacity
        fill_opacity = min(fill_opacity, style.opacity)
    if fill == "none":
        fill_opacity = 0.0
    return ResolvedStyle(
        stroke_opacity=stroke_opacity,
        fill_opacity=fill_opacity,
        dash=_DASH.get(display),
        hashed=(fill == "hashed"),
        show_corners=style.show_corners,
        corner_labels=style.corner_labels,
        end_dots=style.end_dots,
    )
