"""Presentation contract (Milestone M18). Scaffold.

The framework renders already-computed physics: supplied values become labels,
equations, bars, arrows, and named states -- it never solves.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from physics_through_anim.physics.core.state import SystemState


@dataclass(frozen=True)
class QuantitySpec:
    symbol: str = ""
    value: float | None = None
    unit: str | None = None
    latex: str | None = None


@dataclass(frozen=True)
class VectorSpec:
    anchor: str = ""
    vector: tuple[float, float] | None = None
    magnitude: float | None = None
    label: str = ""
    role: str = "velocity"  # role -> colour (SKILL Rule 2)
    perpendicular_to: tuple[str, str] | None = None
    show_components: bool = False
    show_angle: bool = False


@dataclass(frozen=True)
class EquationSpec:
    id: str = ""
    latex: str = ""
    highlight: dict = field(default_factory=dict)


@dataclass(frozen=True)
class BindingSpec:
    source: str = ""  # e.g. "state.spring.extension"
    target: str = ""  # e.g. "spring.geometry.length"


@dataclass(frozen=True)
class NamedState:
    name: str = ""
    state: SystemState = field(default_factory=SystemState)
    quantities: dict = field(default_factory=dict)
    vectors: dict = field(default_factory=dict)
    annotations: tuple = ()


@dataclass(frozen=True)
class TransitionSpec:
    from_state: str = ""
    to_state: str = ""
    duration: float = 2.0
    motion: str = "interpolate"  # interpolate | follow_trajectory | impact


@dataclass(frozen=True)
class ScenePhysicsData:
    states: dict = field(default_factory=dict)
    quantities: dict = field(default_factory=dict)
    vectors: dict = field(default_factory=dict)
    equations: dict = field(default_factory=dict)
    events: dict = field(default_factory=dict)
