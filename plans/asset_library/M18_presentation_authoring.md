# M18 — Presentation Contract & Declarative Lesson Authoring

Status: **DRAFT FOR REVIEW** (NEW — presentation review 2026-09-05, **all MUST**)
Depends on: M6 (state), M9 (overlays/views), M15 (recipes). Files:
`core/scene_data.py` (NEW), `overlays/views.py` (spec-driven views),
`lessons_api.py` (NEW authoring API). This is the **capstone**: a human/AI solves
the physics once and feeds structured results in; the framework turns them into a
polished narrated Manim scene fast.

## Governing principle (MUST)

> The framework does **not** solve the physics. It turns already-computed physics
> into a polished narrated Manim scene extremely quickly.

Four strict layers (MUST):

```
Calculation layer   human/AI/SymPy/SciPy/Krotov/CSV -> states, quantities, vectors,
                    forces, events, equations, relationships   (the physics)
Asset layer         those validated results -> block, rod, spring, arrows, energy
                    bars, momentum arrows, IC marker, graph, FBD  (visual objects)
Lesson composition  what the student sees and when -> named snapshots, transitions,
                    zoom/focus, equation reveals, comparison views, narration beats
Renderer            executes the presentation (Manim)
```

## `core/scene_data.py` (MUST) — the presentation contract

```python
@dataclass(frozen=True)
class QuantitySpec:                 # a supplied physical value + how to name it
    symbol: str; value: float | None = None; unit: str | None = None
    latex: str | None = None        # render as label / equation / bar / graph point / HUD

@dataclass(frozen=True)
class VectorSpec:                   # a supplied vector to draw (role -> colour)
    anchor: PointRef | str          # "rod.B"
    vector: Vec2 | None = None      # explicit components...
    magnitude: float | None = None  # ...or magnitude + a direction rule
    label: str = ""
    role: str = "velocity"          # velocity|acceleration|force|momentum|angular...
    perpendicular_to: tuple[str, str] | None = None   # e.g. ("IC","rod.B") -> right-angle marker
    show_components: bool = False; show_angle: bool = False

@dataclass(frozen=True)
class EquationSpec:
    id: str; latex: str
    highlight: dict[str, str] = field(default_factory=dict)   # term -> asset to co-highlight

@dataclass(frozen=True)
class BindingSpec:                  # bind a supplied value to a visual property
    source: QuantityRef | str       # "state.spring.extension"
    target: str                     # "spring.geometry.length" / "velocity_arrow" / "energy_bar"

@dataclass(frozen=True)
class NamedState:                   # elevates M6 StateSnapshot into a first-class teaching state
    name: str
    state: SystemState
    quantities: dict[str, QuantitySpec] = field(default_factory=dict)
    vectors: dict[str, VectorSpec] = field(default_factory=dict)
    annotations: tuple = ()          # PointSpec, LabelSpec, ...

@dataclass(frozen=True)
class TransitionSpec:
    from_state: str; to_state: str; duration: float = 2.0
    motion: str = "interpolate"      # interpolate | follow_trajectory | impact

@dataclass(frozen=True)
class ScenePhysicsData:              # the whole supplied payload
    states: dict[str, NamedState]
    quantities: dict[str, QuantitySpec] = field(default_factory=dict)
    vectors: dict[str, VectorSpec] = field(default_factory=dict)
    equations: dict[str, EquationSpec] = field(default_factory=dict)
    events: dict[str, "EventSpec"] = field(default_factory=dict)
```

> Manim never computes `½kx²`, `½mv²`, the instantaneous centre, or which way
> friction points. It receives the numbers/vectors and renders them.

## `overlays/views.py` (MUST) — spec-driven teaching views

```python
ViewSpec(name, show=(...))          # declarative "what to show" (MUST)
# examples:
ViewSpec("spring_energy", show=("system","fbd:mass","dimension:spring.extension",
                                "vector:mass.velocity","vector:mass.acceleration","energy_bars"))
ViewSpec("rolling_ic",    show=("disk","contact","instantaneous_center","velocity_field","omega"))
ViewSpec("collision_momentum", show=("before_after","momentum_vectors","system_boundary",
                                     "equation:p_i=p_f"))
```

These render from supplied data (no calculation):
- `EnergyView` / `EnergyComparisonView` — bars/curves from supplied `EnergyState`
  values; can assert `E_A = E_B` only if the caller says conservation applies.
- `MomentumComparisonView` — before/after arrows + resultant from supplied
  `MomentumState`; highlights equal totals if told they are equal.
- `WorkEnergyLedger` — `K_i + ΣW = K_f` ledger from supplied work terms.
- `AngularMomentumView` — from `AngularMomentumViewData(about, before, after,
  omega_after, conserved)`.
- `InstantaneousCenterOverlay` + `RigidBodyVelocityField` — from
  `InstantaneousCenterSpec` + `PointVelocitySpec`/`VectorSpec.perpendicular_to`
  (draws IC, IB line, right-angle marker, `ω`) — geometry only.
- `VectorSpec` rendering — role→colour (Rule 2), optional components/angle/perp
  marker. `EquationStep` — reveal/transform equations and co-highlight the named
  asset (`highlight={"spring": "kA^2/2"}`).

## `lessons_api.py` (MUST) — the authoring API (capstone)

```python
@dataclass
class LessonSpec:
    recipe: str | None = None
    objects: dict[str, PhysicsAsset] = field(default_factory=dict)
    data: ScenePhysicsData = ...
    sequence: list["Beat"] = field(default_factory=list)

# Beats:
Show(state)                          # show a NamedState
Explain(view, equation=None, narration=None)
Transition(from_state, to_state, motion="interpolate")
Focus(target) / Zoom(target)

def render_lesson(lesson: LessonSpec, scene) -> None:
    # build objects, apply NamedStates via bindings (M1.6), play beats in order,
    # attach narration, finish_with_narration() (SKILL Rule 18).
```

Author example (spring SHM):
```python
lesson = LessonSpec(
    recipe="spring_shm",
    objects={"mass": Block(...), "spring": LinearSpring(...)},
    data=ScenePhysicsData(states={"left":..., "equilibrium":..., "right":...}),
    sequence=[
        Show("left"),
        Explain(view="spring_energy", equation="spring_energy_at_extreme"),
        Transition("left", "equilibrium"),
        Explain(view="equilibrium_energy", equation="energy_conservation"),
        Transition("equilibrium", "right"),
    ],
)
render_lesson(lesson, scene)
```

## What the asset layer MAY vs MUST NOT compute (MUST)

**MAY** (rendering geometry only): normalized arrow direction, arrow endpoints,
right-angle marker, label placement, spring-coil geometry, bar heights relative
to supplied values, surface tangent/normal, keypoint positions, coordinate
transforms, and trivial geometric bindings (a velocity arrow ⟂ I–P *if supplied
in semantic form*).

**MUST NOT decide**: whether momentum/energy is conserved, where the
instantaneous centre is, friction direction, spring extension, `N`, `ω`, energy,
or whether a body separates. Those come from the calculation payload.

## Tests (`tests/test_presentation.py`)

```
- QuantitySpec renders as label/equation/bar/graph-point without recomputation.
- VectorSpec role maps to the Rule 2 colour; perpendicular_to adds a right-angle marker.
- EnergyComparisonView bars match supplied values; asserts E_A=E_B only when told.
- MomentumComparisonView draws before/after + equal resultant from supplied totals.
- WorkEnergyLedger: K_i + ΣW == K_f from supplied terms (renders, does not solve).
- BindingSpec: updating a supplied value updates the bound visual (length/arrow/bar).
- NamedState + Transition drive Show/Transition beats; render_lesson plays a 3-state SHM.
- Asset layer performs NO physics: a mutation test asserts views read supplied values only.
```

## Render smoke
Author + `render_lesson` a 3-state spring SHM lesson from supplied values; a
frame per beat confirms energy bars, FBD, vectors and equation reveal update from
the data alone.

## Revisions (presentation review 2026-09-05)
- **NEW capstone milestone (all MUST)**: the presentation contract
  (`ScenePhysicsData`/`NamedState`/`QuantitySpec`/`VectorSpec`/`EquationSpec`/
  `BindingSpec`/`ViewSpec`/`TransitionSpec`) and the declarative `LessonSpec`
  authoring API. Rationale: the highest-value reuse is a **contract between the
  human/AI physics and the assets**, not another solver — most videos are built
  from a few *named states + transitions + views*, avoiding an ever-growing list
  of bespoke `animate_*` methods (§13).
- Related enrichments land in M6 (data types), M9 (spec-driven views), M15
  (Recipe becomes a presentation recipe) — see those docs' revision sections.
