# M17 — Problem / Corpus Orchestration Layer

Status: **DRAFT FOR REVIEW** (NEW — architecture review 2026-09-05, points 30–31)
Depends on: M15 (recipes). Files: `src/physics_through_anim/problems/` (NEW
package, **outside** `mechanics/`). This is the layer that turns an indexed
physics problem (F=ma, Krotov, Holics, …) into a teaching scene.

## Why this layer exists (reviews 30, 31, 32)

The goal is: *take an indexed physics problem → produce a Manim teaching scene.*
The LLM must **not** jump from spreadsheet text straight into asset construction.
And `mechanics/` must **not** contain `KrotovProblem47`/`FMA2025Q18` — the corpus
knows *which* problem/source/concept/technique; `mechanics/` knows *how to
represent* mechanics. This mirrors the math corpus governance model (a stable
central registry rather than agents inventing disconnected records).

## Boundary rule

```
mechanics/  receives only:  ProblemRef("KRO-045")  + resolved structured metadata
mechanics/  must NOT:       search Drive, parse spreadsheets, know source formats
```

## `problems/refs.py`

```python
@dataclass(frozen=True)
class ProblemRef:
    problem_id: str                 # stable id, e.g. "KRO-045"
    source_id: str                  # "krotov"
    problem_number: str             # "45"
    source_title: str | None = None
    source_url: str | None = None
```

## `problems/scene_plan.py` — the declarative bridge

```python
@dataclass
class EntitySpec:   kind: str; name: str; params: dict          # "disk", {"radius":0.5}
@dataclass
class RelationSpec: kind: str; participants: tuple[str,...]; params: dict
@dataclass
class PhaseSpec:    tag: str; t_start: float; t_end: float
@dataclass
class MomentSpec:   tag: str; t: float
@dataclass
class OverlaySpec:  kind: str; target: str; params: dict         # render-independent (review 29)

@dataclass
class ProblemScenePlan:
    problem: ProblemRef
    entities: list[EntitySpec]
    relations: list[RelationSpec]
    phases: list[PhaseSpec]
    moments: dict[str, MomentSpec]
    required_overlays: list[OverlaySpec]
    trajectory_provider: str | None          # dotted path into motion/analytic or an adapter
    learning_objectives: list[str]
    concepts: list[str]
    misconceptions: list[str]
```

## `problems/adapters.py` — plan → generic Recipe

```python
def plan_to_recipe(plan: ProblemScenePlan) -> Recipe:
    asm = Assembly()
    for e in plan.entities:  asm.add(build_entity(e))           # EntitySpec -> generic asset
    for r in plan.relations: asm.add_relation(build_relation(r))# RelationSpec -> Contact/Constraint
    traj = resolve_trajectory(plan.trajectory_provider)         # from motion/analytic or adapter
    overlays = {o.kind: o for o in plan.required_overlays}      # kept as specs (review 29)
    events = phases_to_timeline(plan.phases, plan.moments)
    return Recipe(assembly=asm, events=events, overlays=overlays,
                  trajectories={"system": traj}, moments={...})
```

## The pipeline (reviews 30–31)

```
Corpus problem row
      ↓  (problems/ connector — Drive/sheets stay here)
ProblemRef
      ↓  physics interpretation (LLM or human)
ProblemScenePlan            # entities/relations/phases/overlays — typed, inspectable
      ↓  problems/adapters.plan_to_recipe
generic mechanics Recipe    # M15, only generic assets
      ↓  trajectory_provider (motion/analytic or external adapter)
Timeline + overlays
      ↓  MechanicsRenderer
Manim scene
```

## Registry governance (review 31, mirrors the math corpus)

```
problems/registry.py maintains stable maps (SQLite/CSV-backed, like the math corpus):
    Problem Registry            problem_id -> ProblemRef + metadata
    Problem→Concept Map         problem_id -> [concept_id]
    Problem→Technique Map       problem_id -> [technique_id]
    Problem→Misconception Map   problem_id -> [misconception_id]
    Problem→Scene Recipe Map    problem_id -> recipe name + params
    Scene Artifact Registry     problem_id -> rendered scene/video artifact ids
    Problem Visual Evidence     problem_id -> evidence/provenance
Agents resolve ProblemRef("KRO-045") -> structured metadata; they do NOT invent rows.
```

## Tests (`tests/test_problems.py`)

```
- ProblemRef round-trips id/source/number.
- ProblemScenePlan is fully typed (no dict-of-anything for physics quantities).
- plan_to_recipe builds a valid Recipe: entities/relations resolved, trajectory
  provider resolved, overlays carried as specs (not VGroups).
- A sample KRO-045 plan (cylinder on incline) -> recipe with a RollingConstraint
  and a rolling trajectory provider.
- registry resolves a ProblemRef to concept/technique/misconception ids.
- mechanics/ imports do NOT import problems/ (one-way dependency check).
```

## Use cases unlocked
Corpus-driven scene generation: an F=ma / Krotov / Holics problem id becomes a
`ProblemScenePlan`, then a generic `Recipe`, then a rendered teaching scene —
with concepts/misconceptions/objectives attached, and the mechanics framework
kept ignorant of source formats. This is the scalable architecture for the
stated end goal.

## Revisions (architecture review 2026-09-05)
- **NEW milestone** from review points 30–31. Adds the missing top layer so the
  LLM never jumps from spreadsheet text to asset construction, and so problem
  identity/governance lives in a corpus registry, not in `mechanics/`.
- **Rationale:** keeps the mechanics framework reusable and source-agnostic;
  mirrors the proven math-corpus registry pattern; enforces a one-way dependency
  (`problems/ → mechanics/`, never the reverse).
