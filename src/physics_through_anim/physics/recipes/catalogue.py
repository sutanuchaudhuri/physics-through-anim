"""Recipe catalogue + regression gallery (Milestone M15).

Each recipe is a **composition of generic assets** (never a new physical subclass)
that returns a :class:`Recipe`. The four architecture probes appear here as
first-class recipes (``kepler_orbit``, ``cylinder_at_table_edge``,
``chain_over_edge``, ``galperin``). ``FAMILIES`` is a regression sweep -- one
representative constructor per mechanics family; building them all is the single
best signal of framework health.
"""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.events import Event, EventKind, EventSequence
from physics_through_anim.physics.mechanics import (
    Assembly,
    Block,
    CentralBody,
    Chain,
    ChainRender,
    Conveyor,
    Cylinder,
    Disk,
    Floor,
    Incline,
    KeplerEllipseTrajectory,
    LinearSpring,
    OrbitPath,
    Particle,
    Pulley,
    Rod,
    Table,
    Wall,
)
from physics_through_anim.physics.overlays.events import collision
from physics_through_anim.physics.recipes.base import Recipe

GROUND_Y = -2.0


# --- Probe B: Kepler orbit -----------------------------------------------


def kepler_orbit(a: float = 2.4, e: float = 0.45, period: float = 8.0) -> Recipe:
    focus = (-1.0, 0.0)
    sun = CentralBody(name="sun", position=focus, radius=0.3)
    orbit = OrbitPath(a=a, e=e, focus=focus)
    planet = Particle(name="m", position=tuple(orbit.periapsis()[:2]))
    asm = Assembly()
    asm.add(sun)
    asm.add(orbit)
    asm.add(planet)
    return Recipe(assembly=asm,
                  trajectories={"m": KeplerEllipseTrajectory(orbit=orbit, period=period)},
                  moments={"periapsis": 0.0, "apoapsis": period / 2.0},
                  camera_anchors={"sun": sun.keypoint("CM")})


# --- Probe A: cylinder at a table edge -----------------------------------


def cylinder_at_table_edge() -> Recipe:
    table = Table(top_y=0.6, left=-3.0, right=1.2, leg_bottom=GROUND_Y)
    cyl = Cylinder(name="cyl", radius=0.5, position=(-1.5, 0.6 + 0.5))
    asm = Assembly()
    asm.add(Floor(y=GROUND_Y))
    asm.add(table)
    events = EventSequence()
    events.add(Event(time=2.0, kind=EventKind.CONTACT_CHANGE, participants=("cyl", "edge"),
                     tag="edge_contact"))
    events.add(Event(time=2.6, kind=EventKind.CONTACT_CHANGE, participants=("cyl", "edge"),
                     tag="separation"))
    asm.add(cyl)
    return Recipe(assembly=asm, events=events,
                  moments={"edge_contact": 2.0, "separation": 2.6})


# --- Probe C: chain over a table edge ------------------------------------


def chain_over_edge(length: float = 3.0) -> Recipe:
    table = Table(top_y=0.6, left=-3.0, right=1.0, leg_bottom=GROUND_Y)

    def path(s: float) -> np.ndarray:
        split = 0.6
        if s <= split:
            return np.array([1.0 - (split - s) * length, 0.6, 0.0])
        return np.array([1.0, 0.6 - (s - split) * length, 0.0])

    chain = Chain(name="chain", mass=2.0, length=length, render=ChainRender.CONTINUOUS,
                  material_markers=(0.0, 0.5, 1.0), path=path)
    asm = Assembly()
    asm.add(Floor(y=GROUND_Y))
    asm.add(table)
    asm.add(chain)
    return Recipe(assembly=asm, moments={"start": 0.0},
                  camera_anchors={"edge": table.edge().point()})


# --- Probe D: Galperin repeated collisions -------------------------------


def galperin(big: float = 9.0, small: float = 1.0) -> Recipe:
    asm = Assembly()
    asm.add(Floor(y=GROUND_Y, half_width=7.0))
    asm.add(Wall(angle_deg=90.0, center=(-4.6, GROUND_Y + 1.0), length=2.0, facing="right"))
    asm.add(Block(name="M", width=1.2, height=0.9, mass=big, position=(1.6, GROUND_Y + 0.45)))
    asm.add(Block(name="m", width=0.5, height=0.5, mass=small, position=(-1.8, GROUND_Y + 0.25)))
    events = EventSequence()
    for k, t in enumerate((1.2, 1.9, 2.5), start=1):
        events.add(collision("M", "m", t=t))
        _ = k
    return Recipe(assembly=asm, events=events, moments={"first_impact": 1.2})


# --- A handful more textbook recipes -------------------------------------


def atwood(m1: float = 1.0, m2: float = 2.0) -> Recipe:
    asm = Assembly()
    pulley = Pulley(center=(0.0, 2.0), radius=0.5)
    asm.add(pulley)
    asm.add(Block(name="m1", mass=m1, position=(-0.9, 0.4)))
    asm.add(Block(name="m2", mass=m2, position=(0.9, -0.4)))
    return Recipe(assembly=asm, moments={"release": 0.0}, camera_anchors={"axle": pulley.center})


def mass_spring(k: float = 4.0) -> Recipe:
    asm = Assembly()
    asm.add(Floor(y=GROUND_Y))
    wall = Wall(angle_deg=90.0, center=(-3.0, GROUND_Y + 0.5), length=1.6, facing="right")
    asm.add(wall)
    asm.add(Block(name="m", width=0.8, height=0.8, position=(-0.6, GROUND_Y + 0.4)))
    spring = LinearSpring(from_point=(-3.0, GROUND_Y + 0.4), to_point=(-1.0, GROUND_Y + 0.4),
                          natural_length=2.0, k=k)
    return Recipe(assembly=asm, overlays={"spring": spring}, moments={"release": 0.0})


# --- Regression gallery: one representative per family -------------------


def _floor_recipe(body: Block) -> Recipe:
    asm = Assembly()
    floor = Floor(y=GROUND_Y)
    asm.add(floor)
    asm.add(body, place_on=floor)
    return Recipe(assembly=asm, moments={"start": 0.0})


def block_on_floor() -> Recipe:
    return _floor_recipe(Block(name="m"))


def impending_slide() -> Recipe:
    asm = Assembly()
    incline = Incline(angle_deg=25.0, length=5.0, base=(-2.0, GROUND_Y))
    asm.add(Floor(y=GROUND_Y))
    asm.add(incline)
    asm.add(Block(name="m", width=0.7, height=0.5), place_on=incline)
    return Recipe(assembly=asm, moments={"slip_onset": 0.0})


def disk_on_incline() -> Recipe:
    asm = Assembly()
    incline = Incline(angle_deg=25.0, length=5.0, base=(-2.0, GROUND_Y))
    asm.add(Floor(y=GROUND_Y))
    asm.add(incline)
    asm.add(Disk(name="disk", radius=0.5), place_on=incline)
    return Recipe(assembly=asm, moments={"start": 0.0})


def block_on_conveyor() -> Recipe:
    asm = Assembly()
    belt = Conveyor(y=GROUND_Y, belt_speed=1.0)
    asm.add(belt)
    asm.add(Block(name="m"), place_on=belt)
    return Recipe(assembly=asm, moments={"start": 0.0})


def physical_pendulum() -> Recipe:
    asm = Assembly()
    asm.add(Rod(name="rod", length=2.0, angle_deg=-70.0, center=(0.0, 1.0)))
    return Recipe(assembly=asm, moments={"release": 0.0})


def ladder() -> Recipe:
    asm = Assembly()
    asm.add(Floor(y=GROUND_Y))
    asm.add(Wall(angle_deg=90.0, center=(-3.0, GROUND_Y + 1.5), length=3.0, facing="right"))
    asm.add(Rod(name="ladder", length=3.6, angle_deg=62.0, center=(-2.0, GROUND_Y + 1.5)))
    return Recipe(assembly=asm, moments={"slip_onset": 0.0})


def bead_on_circular_track() -> Recipe:
    from physics_through_anim.physics.mechanics import CircularTrack

    asm = Assembly()
    asm.add(Particle(name="bead", position=(0.0, 0.0)))
    return Recipe(assembly=asm, overlays={"track": CircularTrack(center=(0.0, 0.0), radius=1.5)},
                  moments={"start": 0.0})


def body_leaving_convex() -> Recipe:
    from physics_through_anim.physics.mechanics import ConvexSurface

    asm = Assembly()
    asm.add(Particle(name="m", position=(0.0, 1.5)))
    return Recipe(assembly=asm, overlays={"hill": ConvexSurface(center=(0.0, 0.0), radius=1.5)},
                  moments={"separation": 0.0})


def bullet_embeds_in_rod() -> Recipe:
    asm = Assembly()
    asm.add(Rod(name="rod", length=2.0, angle_deg=90.0, center=(0.0, 0.5)))
    asm.add(Particle(name="bullet", position=(-2.0, 0.9)))
    events = EventSequence()
    events.add(collision("bullet", "rod", t=1.0, restitution=0.0))
    return Recipe(assembly=asm, events=events, moments={"embed": 1.0})


def gravity_to_focus() -> Recipe:
    return kepler_orbit()


def block_in_truck() -> Recipe:
    asm = Assembly()
    floor = Floor(y=GROUND_Y)
    asm.add(floor)
    asm.add(Block(name="m"), place_on=floor)
    return Recipe(assembly=asm, moments={"start": 0.0})


def falling_chain_onto_scale() -> Recipe:
    return chain_over_edge()


def person_on_boat() -> Recipe:
    asm = Assembly()
    floor = Floor(y=GROUND_Y)
    asm.add(floor)
    asm.add(Block(name="boat", width=2.4, height=0.4, mass=4.0), place_on=floor)
    asm.add(Block(name="person", width=0.4, height=0.7, mass=1.0, position=(-0.8, GROUND_Y + 0.55)))
    return Recipe(assembly=asm, moments={"start": 0.0})


# One representative recipe per mechanics family (the regression sweep).
FAMILIES = {
    "translation": block_on_floor,
    "friction": impending_slide,
    "rolling": disk_on_incline,
    "moving_surface": block_on_conveyor,
    "pulley": atwood,
    "hinge": physical_pendulum,
    "multi_contact": ladder,
    "curved_contact": bead_on_circular_track,
    "separation": body_leaving_convex,
    "edge": cylinder_at_table_edge,
    "distributed": chain_over_edge,
    "spring": mass_spring,
    "collision": galperin,
    "repeated_collision": galperin,
    "topology": bullet_embeds_in_rod,
    "orbit": kepler_orbit,
    "central_force": gravity_to_focus,
    "noninertial": block_in_truck,
    "variable_mass": falling_chain_onto_scale,
    "com": person_on_boat,
}
