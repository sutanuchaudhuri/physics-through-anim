"""Impact model (Milestone M12).

Velocity is discontinuous across an impact: a ``PiecewiseTrajectory`` never
interpolates velocity through the impact (STEP_RIGHT at a boundary), while
position stays continuous. The impact law is supplied via ``ImpactData``, never
solved -- the framework renders before/after, it does not compute ``v+``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np

from physics_through_anim.physics.core.state import SystemState


@dataclass(frozen=True)
class ImpactData:
    time: float = 0.0
    before: Mapping = field(default_factory=dict)
    after: Mapping = field(default_factory=dict)
    restitution: float = 1.0
    impulse: float = 0.0


@dataclass
class Segment:
    """A trajectory valid from ``t_start`` until the next segment begins."""

    t_start: float = 0.0
    trajectory: object = None  # any object with state_at(t) -> SystemState


@dataclass
class PiecewiseTrajectory:
    """Pre-impact segment -> impact -> post-impact segment (velocity STEPs).

    ``state_at`` selects the last segment whose ``t_start <= t`` (STEP_RIGHT), so
    velocity jumps at each boundary while each segment keeps position continuous.
    """

    segments: list = field(default_factory=list)
    impacts: list = field(default_factory=list)

    def add_segment(self, t_start: float, trajectory) -> PiecewiseTrajectory:
        self.segments.append(Segment(t_start, trajectory))
        self.segments.sort(key=lambda s: s.t_start)
        return self

    def add_impact(self, impact: ImpactData) -> PiecewiseTrajectory:
        self.impacts.append(impact)
        return self

    def state_at(self, t: float) -> SystemState:
        if not self.segments:
            return SystemState()
        chosen = self.segments[0]
        for seg in self.segments:
            if seg.t_start <= t + 1e-12:  # STEP_RIGHT: the post-impact side wins at a boundary
                chosen = seg
            else:
                break
        return chosen.trajectory.state_at(t)


def reflect_velocity(v, normal, e_n: float = 1.0, e_t: float = 1.0) -> np.ndarray:
    """Restitution reflection of ``v`` off a surface with outward ``normal``.

    The normal component flips and scales by ``e_n`` (``1`` elastic, ``0`` sticks
    normally); the tangential component scales by ``e_t`` (surface friction /
    tangential restitution). Applying a supplied law -- not integrating motion.
    """
    v2 = np.asarray(v, dtype=float)[:2]
    n = np.asarray(normal, dtype=float)[:2]
    n = n / (np.linalg.norm(n) or 1.0)
    v_n = np.dot(v2, n) * n
    v_t = v2 - v_n
    return e_t * v_t - e_n * v_n


@dataclass(frozen=True)
class MomentumFlux:
    """A stream of mass (rate ``dm/dt``) meeting a surface at ``relative_velocity``.

    ``force() = rate * relative_velocity`` -- the reaction that a moving belt,
    wall, floor, or rocket must supply/receive. A local constitutive evaluation
    (like Hooke's law), not integration; the scene renders the resulting force.
    """

    rate: float = 0.0  # dm/dt (kg/s), >= 0
    relative_velocity: float = 0.0  # speed of the mass relative to the surface (m/s)

    def force(self) -> float:
        return self.rate * self.relative_velocity

    @classmethod
    def wind(cls, density: float, area: float, speed: float) -> MomentumFlux:
        """Air hitting an area: ``F = rho A v^2`` (rate ``rho A v``, v_rel ``v``)."""
        return cls(rate=density * area * speed, relative_velocity=speed)

    @classmethod
    def onto_belt(cls, rate: float, v_belt: float, v_sand: float = 0.0) -> MomentumFlux:
        """Sand dropped onto a belt: ``F = (dm/dt)(v_belt - v_sand)`` (motor supplies it)."""
        return cls(rate=rate, relative_velocity=v_belt - v_sand)

    @classmethod
    def chain_pileup(cls, linear_density: float, speed: float) -> MomentumFlux:
        """Arriving links of a chain hitting the floor: flux term ``F = lambda v^2``."""
        return cls(rate=linear_density * speed, relative_velocity=speed)

    @classmethod
    def rocket(cls, mass_rate: float, exhaust_speed: float) -> MomentumFlux:
        """Rocket emission-as-collision: thrust ``F = u |dm/dt|`` opposite the exhaust."""
        return cls(rate=mass_rate, relative_velocity=exhaust_speed)


@dataclass(frozen=True)
class Impulse:
    """A supplied impulse ``J = integral F dt`` applied at world point ``at``."""

    jx: float = 0.0
    jy: float = 0.0
    at: tuple = (0.0, 0.0)

    @property
    def vector(self) -> np.ndarray:
        return np.array([self.jx, self.jy])

    @property
    def magnitude(self) -> float:
        return float(np.hypot(self.jx, self.jy))


@dataclass(frozen=True)
class ImpulseResponse:
    """The instantaneous change an impulse produces: CM velocity + spin."""

    delta_v: np.ndarray  # change of the CM velocity = J / m
    delta_omega: float  # change of angular velocity = (r x J) / I_cm


def impulse_response(mass: float, inertia_cm: float, r_from_cm, J) -> ImpulseResponse:
    """Off-centre impulse ``J`` at offset ``r_from_cm``: returns ``(dv_cm, domega)``.

    ``dv = J/m`` (linear) and ``domega = (r x J)/I_cm`` (angular). A central
    impulse (``r=0``) is pure translation; an end impulse spins the body too. This
    is impulse--momentum bookkeeping of a *supplied* ``J``, not integrating motion.
    """
    r = np.asarray(r_from_cm, dtype=float)[:2]
    j = np.asarray(J, dtype=float)[:2]
    cross = r[0] * j[1] - r[1] * j[0]  # 2-D z-component of r x J
    return ImpulseResponse(delta_v=j / mass, delta_omega=cross / inertia_cm)


def center_of_percussion(inertia_cm: float, mass: float, pivot_to_cm: float) -> float:
    """Distance from a pivot to the center of percussion (the "sweet spot").

    A transverse impulse there produces **no reaction at the pivot**:
    ``q = d + I_cm/(m d)`` where ``d = pivot_to_cm``. For a uniform rod pivoted at
    an end (``I_cm = mL^2/12``, ``d = L/2``) this is ``2L/3``.
    """
    return pivot_to_cm + inertia_cm / (mass * pivot_to_cm)


def perfectly_inelastic(*mass_velocity_pairs) -> float:
    """Common 1-D velocity after a perfectly inelastic merge: ``sum(m v)/sum(m)``.

    The ballistic-pendulum capture: ``perfectly_inelastic((m, v), (M, 0))``.
    """
    total_mass = sum(m for m, _ in mass_velocity_pairs)
    momentum = sum(m * v for m, v in mass_velocity_pairs)
    return momentum / total_mass
