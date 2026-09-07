"""Pluggable render engines for spec-driven scenes (Milestone M17).

Importing this package registers every engine. ``manim`` is the prime (video)
engine; ``svg`` is the working dependency-free snapshot engine; ``matplotlib``,
``plotly`` and ``pymunk`` are scaffolds.
"""

from __future__ import annotations

# Import for side effects: each module registers its engines.
from physics_through_anim.physics.rendering import engines as _engines  # noqa: F401
from physics_through_anim.physics.rendering import svg_renderer as _svg  # noqa: F401
from physics_through_anim.physics.rendering.base import (
    RENDERERS,
    Renderer,
    available_renderers,
    get_renderer,
    load_plan,
    register,
    render_plan_file,
    validate_plan_file,
)

__all__ = [
    "RENDERERS",
    "Renderer",
    "available_renderers",
    "get_renderer",
    "load_plan",
    "register",
    "render_plan_file",
    "validate_plan_file",
]
