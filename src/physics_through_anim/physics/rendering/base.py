"""Pluggable render engines: turn a ``ProblemScenePlan`` into a file (Milestone M17).

One spec, many back-ends. ``manim`` is the prime engine (video); the others are
snapshot/preview engines. Only ``svg`` is wired end-to-end today (dependency-free,
proves "XML -> picture"); the rest are scaffolds that raise an informative error.

    from physics_through_anim.physics.rendering import render_plan_file
    render_plan_file("scene.xml", renderer="svg", output="scene.svg")
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.serialization.codec import from_json, from_xml
from physics_through_anim.physics.serialization.validation import (
    PlanError,
    PlanValidationError,
    validate_plan,
)

__all__ = [
    "Renderer",
    "RENDERERS",
    "register",
    "get_renderer",
    "available_renderers",
    "load_plan",
    "validate_plan_file",
    "render_plan_file",
]


class Renderer(ABC):
    """A render back-end: consumes a plan, writes a file, returns its path."""

    name: str = "base"
    kind: str = "snapshot"  # "video" | "snapshot"
    default_suffix: str = ".out"

    @abstractmethod
    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        """Render ``plan`` to ``output`` and return the written path."""


RENDERERS: dict[str, type[Renderer]] = {}


def register(cls: type[Renderer]) -> type[Renderer]:
    """Class decorator: add a renderer to the registry under its ``name``."""
    RENDERERS[cls.name] = cls
    return cls


def get_renderer(name: str) -> Renderer:
    """Instantiate the registered renderer named ``name``."""
    if name not in RENDERERS:
        raise KeyError(f"Unknown renderer {name!r}. Available: {available_renderers()}")
    return RENDERERS[name]()


def available_renderers() -> list[str]:
    """Sorted names of all registered renderers."""
    return sorted(RENDERERS)


def load_plan(path: str | Path) -> ProblemScenePlan:
    """Load a ``ProblemScenePlan`` from a ``.json`` or ``.xml`` file.

    Loads leniently (``strict=False``) so an invalid enum value is preserved for
    the validator to report rather than crashing the parse.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return from_json(ProblemScenePlan, text, strict=False)
    if suffix == ".xml":
        return from_xml(ProblemScenePlan, text, strict=False)
    raise ValueError(f"Unsupported plan format {suffix!r}; use .json or .xml.")


def validate_plan_file(path: str | Path) -> list[PlanError]:
    """Load a plan file and return its (deterministic) list of validation errors."""
    try:
        plan = load_plan(path)
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 -- malformed JSON/XML becomes a single error
        return [PlanError(str(path), f"could not parse plan: {exc}")]
    return validate_plan(plan)


def render_plan_file(path: str | Path, *, renderer: str = "svg",
                     output: str | Path | None = None, validate: bool = True) -> Path:
    """Load a plan file, validate it, and render it with the named engine."""
    plan = load_plan(path)
    if validate:
        errors = validate_plan(plan)
        if errors:
            raise PlanValidationError(errors)
    engine = get_renderer(renderer)
    if output is None:
        output = Path(path).with_suffix(engine.default_suffix)
    return engine.render(plan, Path(output))
