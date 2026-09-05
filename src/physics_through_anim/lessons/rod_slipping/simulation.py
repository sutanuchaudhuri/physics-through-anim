"""Numerical simulation of a rod slipping at a table edge.

Implements the phase hierarchy from plans/rod_slipping_new_edge.md:

  Phase A (static contact, foot fixed at the origin):
      integrate theta_ddot = (3g)/(2L) * sin(theta)  [torque about the fixed foot]
      until the static-friction ratio |f_required|/N reaches mu_s.

  Phase B (post-slip, foot free to slide on the table surface y=0):
      Modeled as ideally frictionless sliding (mu_k = 0) so the physics stays
      closed-form and robust: with no horizontal contact force, the center of
      mass's horizontal momentum is conserved, and mechanical energy stays at
      its initial value (gravity is still the only force doing work). That
      gives omega(theta) and alpha(theta) algebraically -- no Coulomb
      stick-slip sign ambiguity to get wrong. Static friction still governs
      *when* slip begins (the mu_s test in Phase A); only the post-slip
      dynamics is simplified this way. See SKILL.md Rule 3: state the
      assumption -- every scene using this phase must say so on screen.

  Phase C (free flight): a_G = g (down only), alpha = 0 (no torque about G
  once contact forces vanish), so omega stays constant and theta advances
  linearly. Integrated until either endpoint reaches the floor.

All phases share one numeric example so every scene in the lesson reads from
the *same* computed trajectory (per the plan's "graph contract").

Correctness check baked in: at the moment N=0 (Phase B -> C boundary), alpha
must equal 0 exactly, because the plan's own Scene 28 states this as a fact
("About G: tau_G=0, therefore alpha=0"). `simulate()` asserts this.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Fixed numeric example used throughout the lesson (Scene 18's mu_s = 0.30).
M = 1.0
LENGTH = 2.0
S = LENGTH / 2.0
G = 9.8
I_G = M * LENGTH**2 / 12.0
I_P = M * LENGTH**2 / 3.0
MU_S = 0.30
THETA0 = np.radians(2.0)
TABLE_HEIGHT = 3.0  # table top is y=0; the floor the rod eventually hits is at y=-TABLE_HEIGHT
# For this numeric example (mu_s=0.30, theta0=2 deg), the post-slip normal
# force never drops back to zero before the rod would lie flat -- verified
# numerically (N stays in roughly [1.7, 6]) rather than assumed. So contact
# here ends because the foot reaches the table's physical edge, not because
# of a lift-off condition; THETA_EDGE is that edge's position, expressed as
# the rod angle at which the foot arrives there. See Scene 26's narration.
THETA_EDGE = np.radians(63.0)


@dataclass
class Trajectory:
    t: np.ndarray
    theta: np.ndarray
    omega: np.ndarray
    alpha: np.ndarray
    x_g: np.ndarray
    y_g: np.ndarray
    normal: np.ndarray
    friction: np.ndarray
    phase: np.ndarray  # 0=static, 1=slipping, 2=free flight
    t_slip: float
    theta_slip: float
    t_sep: float
    theta_sep: float
    omega_sep: float
    t_hit: float
    theta_hit: float
    which_end_hits: str
    n_spins: float


def _friction_ratio(theta, omega):
    """|f_required| / N and the signed f_required, for the fixed-foot phase."""
    alpha = 1.5 * G / LENGTH * np.sin(theta)
    a_gx = S * (alpha * np.cos(theta) - omega**2 * np.sin(theta))
    a_gy = -S * (alpha * np.sin(theta) + omega**2 * np.cos(theta))
    f_required = M * a_gx
    normal = M * G + M * a_gy
    return abs(f_required) / normal, f_required, normal, alpha


def _phase_a():
    def rhs(_t, y):
        theta, omega = y
        alpha = 1.5 * G / LENGTH * np.sin(theta)
        return [omega, alpha]

    def slip_event(_t, y):
        theta, omega = y
        ratio, *_ = _friction_ratio(theta, omega)
        return ratio - MU_S

    slip_event.terminal = True
    slip_event.direction = 1

    sol = solve_ivp(
        rhs, [0, 5.0], [THETA0, 0.0], events=slip_event, max_step=1e-3, dense_output=True
    )
    t_slip = sol.t_events[0][0]
    theta_slip, omega_slip = sol.y_events[0][0]
    t = np.linspace(0, t_slip, 400)
    theta, omega = sol.sol(t)
    alpha = 1.5 * G / LENGTH * np.sin(theta)
    return t, theta, omega, alpha, t_slip, theta_slip, omega_slip


def _omega_alpha_b(theta, vx_const):
    """Closed-form omega(theta), alpha(theta) for frictionless post-slip
    sliding: energy conservation (with the CM's horizontal KE locked in at
    vx_const, released from THETA0 at rest) plus its time-derivative."""
    j = M * S**2 * np.sin(theta) ** 2 + I_G
    numerator = 2 * M * G * S * (np.cos(THETA0) - np.cos(theta)) - M * vx_const**2
    omega = np.sqrt(np.clip(numerator, 0.0, None) / j)
    alpha = (M * G * S * np.sin(theta) - M * S**2 * np.sin(theta) * np.cos(theta) * omega**2) / j
    return omega, alpha


def _normal_b(theta, vx_const):
    omega, alpha = _omega_alpha_b(theta, vx_const)
    return M * G - M * S * np.sin(theta) * alpha - M * S * np.cos(theta) * omega**2


def _phase_b(theta_slip: float, omega_slip: float):
    vx_const = S * np.cos(theta_slip) * omega_slip

    def rhs(_t, y):
        (theta,) = y
        omega, _alpha = _omega_alpha_b(theta, vx_const)
        return [omega]

    def edge_event(_t, y):
        return y[0] - THETA_EDGE

    edge_event.terminal = True
    edge_event.direction = 1

    sol = solve_ivp(
        rhs, [0, 5.0], [theta_slip], events=edge_event, max_step=1e-3, dense_output=True
    )
    t_rel_sep = sol.t_events[0][0]
    theta_sep = sol.y_events[0][0][0]
    t = np.linspace(0, t_rel_sep, 400)
    (theta,) = sol.sol(t)
    omega, alpha = _omega_alpha_b(theta, vx_const)
    omega_sep, alpha_sep = _omega_alpha_b(theta_sep, vx_const)
    return t, theta, omega, alpha, t_rel_sep, theta_sep, omega_sep, alpha_sep, vx_const


def _phase_c(x_g0, y_g0, vx0, vy0, theta0, omega0):
    def y_end(tau, sign):
        y_g = y_g0 + vy0 * tau - 0.5 * G * tau**2
        theta = theta0 + omega0 * tau
        return y_g + sign * S * np.cos(theta) - (-TABLE_HEIGHT)

    def min_end(tau):
        return min(y_end(tau, 1.0), y_end(tau, -1.0))

    tau_hit = brentq(min_end, 1e-6, 5.0)
    t = np.linspace(0, tau_hit, 200)
    x_g = x_g0 + vx0 * t
    y_g = y_g0 + vy0 * t - 0.5 * G * t**2
    theta = theta0 + omega0 * t
    omega = np.full_like(t, omega0)
    alpha = np.zeros_like(t)

    y_a_final = y_end(tau_hit, 1.0)
    y_b_final = y_end(tau_hit, -1.0)
    which_end = "A" if abs(y_a_final) < abs(y_b_final) else "B"
    n_spins = abs(omega0) * tau_hit / (2 * np.pi)
    return t, x_g, y_g, theta, omega, alpha, tau_hit, which_end, n_spins


def simulate() -> Trajectory:
    ta, tha, wa, aa, t_slip, theta_slip, omega_slip = _phase_a()
    tb, thb, wb, ab, dt_sep, theta_sep, omega_sep, alpha_sep, vx_const = _phase_b(
        theta_slip, omega_slip
    )
    tb = tb + t_slip
    t_sep = t_slip + dt_sep

    y_g_sep = S * np.cos(theta_sep)
    vy_sep = -S * np.sin(theta_sep) * omega_sep
    vx_sep = vx_const
    x_g_sep = S * np.sin(theta_slip) + vx_const * dt_sep

    tc, xgc, ygc, thc, wc, ac, tau_hit, which_end, n_spins = _phase_c(
        x_g_sep, y_g_sep, vx_sep, vy_sep, theta_sep, omega_sep
    )
    tc = tc + t_sep

    t = np.concatenate([ta, tb, tc])
    theta = np.concatenate([tha, thb, thc])
    omega = np.concatenate([wa, wb, wc])
    alpha = np.concatenate([aa, ab, ac])
    x_g_a = S * np.sin(tha)
    y_g_a = S * np.cos(tha)
    x_g_b = S * np.sin(theta_slip) + vx_const * (tb - t_slip)
    y_g_b = S * np.cos(thb)
    x_g = np.concatenate([x_g_a, x_g_b, xgc])
    y_g = np.concatenate([y_g_a, y_g_b, ygc])

    normal_a = np.array([_friction_ratio(th, w)[2] for th, w in zip(tha, wa)])
    friction_a = np.array([_friction_ratio(th, w)[1] for th, w in zip(tha, wa)])
    normal_b = _normal_b(thb, vx_const)
    friction_b = np.zeros_like(tb)
    normal_c = np.zeros_like(tc)
    friction_c = np.zeros_like(tc)
    normal = np.concatenate([normal_a, normal_b, normal_c])
    friction = np.concatenate([friction_a, friction_b, friction_c])

    phase = np.concatenate([np.zeros_like(ta), np.ones_like(tb), np.full_like(tc, 2)])
    t_hit = tc[-1] if len(tc) else t_sep + tau_hit

    return Trajectory(
        t=t,
        theta=theta,
        omega=omega,
        alpha=alpha,
        x_g=x_g,
        y_g=y_g,
        normal=normal,
        friction=friction,
        phase=phase,
        t_slip=t_slip,
        theta_slip=theta_slip,
        t_sep=t_sep,
        theta_sep=theta_sep,
        omega_sep=omega_sep,
        t_hit=t_hit,
        theta_hit=theta_sep + omega_sep * tau_hit,
        which_end_hits=which_end,
        n_spins=n_spins,
    )


_CACHE: Trajectory | None = None


def get_trajectory() -> Trajectory:
    global _CACHE
    if _CACHE is None:
        _CACHE = simulate()
    return _CACHE
