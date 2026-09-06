"""Kinematic overlays (Milestone M9). Scaffold — render VGroups from supplied state."""

from __future__ import annotations


def velocity_vector(body, scale: float = 1.0):
    raise NotImplementedError("M9 velocity_vector")


def acceleration_vector(body, scale: float = 1.0):
    raise NotImplementedError("M9 acceleration_vector")


def rolling_velocity_field(disk, v_cm: float, points: tuple[str, ...] = ("top", "3", "9")):
    """Rule-5 exact field: v perp to (point - contact); contact marked v = 0."""
    raise NotImplementedError("M9 rolling_velocity_field")
