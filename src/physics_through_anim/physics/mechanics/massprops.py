"""Mass properties (Milestone M1.5).

Plan: plans/asset_library/M01_5_pose_rigidbody.md. Mass + rotational inertia with
the parallel-axis theorem, so any point's effective inertia is a pure function of
the body-frame offset from the centre of mass.

Status: SCAFFOLD (M1.5). ``inertia_about`` is unimplemented; see the test plan.
"""

from __future__ import annotations

from dataclasses import dataclass

Vec2 = tuple[float, float]


@dataclass(frozen=True)
class MassProperties:
    """Mass and moment of inertia about the centre of mass."""

    mass: float = 1.0
    inertia_cm: float = 0.0  # I about the CM (0 for a particle)

    def inertia_about(self, r_from_cm: Vec2) -> float:
        """Parallel axis: ``I = I_cm + m * |r_from_cm|^2``."""
        raise NotImplementedError("M1.5 massprops.inertia_about")
