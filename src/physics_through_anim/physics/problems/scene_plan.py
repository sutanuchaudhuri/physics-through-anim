"""ProblemScenePlan: the declarative bridge (Milestone M17). Scaffold.

Typed, inspectable specs -- no dict-of-anything for physics quantities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from physics_through_anim.physics.problems.refs import ProblemRef


@dataclass
class EntitySpec:
    kind: str = ""
    name: str = ""
    params: dict = field(default_factory=dict)


@dataclass
class RelationSpec:
    kind: str = ""
    participants: tuple[str, ...] = ()
    params: dict = field(default_factory=dict)


@dataclass
class PhaseSpec:
    tag: str = ""
    t_start: float = 0.0
    t_end: float = 0.0


@dataclass
class MomentSpec:
    tag: str = ""
    t: float = 0.0


@dataclass
class OverlaySpec:
    kind: str = ""
    target: str = ""
    params: dict = field(default_factory=dict)


@dataclass
class ProblemScenePlan:
    problem: ProblemRef = field(default_factory=ProblemRef)
    entities: list = field(default_factory=list)
    relations: list = field(default_factory=list)
    phases: list = field(default_factory=list)
    moments: dict = field(default_factory=dict)
    required_overlays: list = field(default_factory=list)
    trajectory_provider: str | None = None
    learning_objectives: list = field(default_factory=list)
    concepts: list = field(default_factory=list)
    misconceptions: list = field(default_factory=list)
