"""Spec-driven teaching views (Milestone M18). Scaffold.

Views render supplied values -- they never calculate. ``ViewSpec`` is the
declarative "what to show".
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ViewSpec:
    name: str = ""
    show: tuple[str, ...] = ()


def energy_view(spec, data):
    """Bars/curves from a supplied EnergyState (asserts conservation only if told)."""
    raise NotImplementedError("M18 energy_view")


def momentum_comparison_view(spec, data):
    raise NotImplementedError("M18 momentum_comparison_view")
