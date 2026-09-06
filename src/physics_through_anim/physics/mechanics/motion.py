"""Framework-level rolling animation helper (Milestone M3). Scaffold.

``roll_group`` translates + spins a group at v = omega R with no drift, so the
asset layer never imports a lesson's ``common.py``.
"""

from __future__ import annotations


def roll_group(scene, group, radius: float, distance: float, *, rightward: bool = True) -> None:
    """Translate + spin ``group`` over ``distance`` at v = omega R (no drift)."""
    raise NotImplementedError("M3 motion.roll_group")
