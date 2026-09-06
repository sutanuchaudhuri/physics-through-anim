"""Distributed-mass bodies / chains (Milestone M11). Scaffold.

Shape travels in the generic SystemState via ``AssetState.shape`` -- no special
trajectory pathway.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

import numpy as np


class ChainRender(StrEnum):
    CONTINUOUS = "continuous"
    LINKED = "linked"


@dataclass(frozen=True)
class ChainShapeState:
    """Material coord s in [0, 1] -> world point, carried in AssetState.shape."""

    path: Callable[[float], np.ndarray] | None = None


@dataclass
class DistributedBody:
    """Base for any body with a material coordinate + evolving shape."""

    render: ChainRender = ChainRender.CONTINUOUS


@dataclass
class Chain(DistributedBody):
    mass: float = 1.0
    length: float = 3.0
    n_links: int = 20
    path: Callable[[float], np.ndarray] | None = None
    material_markers: tuple[float, ...] = ()
    label: str = "chain"

    def com(self) -> np.ndarray:
        """Mass-weighted centre of mass of the current shape."""
        raise NotImplementedError("M11 Chain.com")

    def portion(self, s0: float, s1: float):
        """Highlight a sub-length (supported vs free)."""
        raise NotImplementedError("M11 Chain.portion")


@dataclass
class ElasticString(DistributedBody):
    natural_length: float = 1.0


@dataclass
class MassiveSpring(DistributedBody):
    natural_length: float = 1.0


@dataclass
class FlexibleRod(DistributedBody):
    length: float = 2.0
