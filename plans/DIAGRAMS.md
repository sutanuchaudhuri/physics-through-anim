# Asset Library — Diagrams

Entity, flow, and sequence views of the composable physics asset library.
Namespace is the promoted `physics_through_anim.physics.*` (see
[ARCHITECTURE.md](ARCHITECTURE.md)). Mermaid blocks render inline in VS Code /
GitHub; equivalent **PlantUML** is provided for each where you prefer that toolchain.

---

## 1. Entity / class diagram

The core model: renderable entities, the relations that connect them, the
solver-supplied state, and the composition/orchestration layers.

```mermaid
classDiagram
  direction LR

  class PhysicsAsset {
    +str name
    +Pose2D pose
    +dict local_keypoints
    +list~ForceSpec~ forces
    +build() VGroup
    +keypoint(key) ndarray
    +set_pose(pose) void
    +fbd() VGroup
  }
  class RigidBody2D {
    +MassProperties mass_props
    +point_velocity(ref, state) ndarray
    +point_acceleration(ref, state) ndarray
  }
  class Block
  class Disk
  class Rod
  class Support
  class Floor
  class Incline
  class Assembly {
    +list~PhysicsAsset~ members
    +Timeline timeline
    +add(asset, place_on) void
    +resolve(ref) ndarray
    +fbd() VGroup
  }
  class Contact {
    +ContactLocator locator
    +frame_at(state) ContactFrame
  }
  class Constraint
  class ForceSpec {
    +InteractionKind kind
    +str at
    +QuantityRef value
  }
  class Pose2D {
    +tuple position
    +float angle
    +world_point(local) ndarray
  }
  class MassProperties
  class SystemState {
    +Mapping entities
    +Mapping fields
    +Mapping observables
  }
  class RigidKinematicState
  class Trajectory {
    +state_at(t) SystemState
  }
  class Timeline
  class EventSequence
  class Binding {
    +apply(assembly, state) void
  }
  class Recipe {
    +Assembly assembly
    +Trajectory trajectory
    +EventSequence events
  }
  class ProblemScenePlan
  class MechanicsRenderer

  PhysicsAsset <|-- RigidBody2D
  PhysicsAsset <|-- Support
  RigidBody2D <|-- Block
  RigidBody2D <|-- Disk
  RigidBody2D <|-- Rod
  Support <|-- Floor
  Support <|-- Incline

  PhysicsAsset "1" o-- "1" Pose2D : pose
  PhysicsAsset "1" *-- "0..*" ForceSpec : declares
  RigidBody2D "1" o-- "1" MassProperties

  Assembly "1" o-- "1..*" PhysicsAsset : members
  Assembly "1" o-- "0..*" Contact
  Assembly "1" o-- "0..*" Constraint
  Assembly "1" o-- "1" Timeline

  Timeline o-- Trajectory
  Timeline o-- EventSequence
  Trajectory ..> SystemState : produces
  SystemState "1" o-- "1..*" RigidKinematicState : entities

  Binding ..> SystemState : reads
  Binding ..> PhysicsAsset : set_pose

  Recipe o-- Assembly
  Recipe o-- Trajectory
  Recipe o-- EventSequence
  ProblemScenePlan ..> Recipe : plan_to_recipe
  MechanicsRenderer ..> Assembly : renders
  MechanicsRenderer ..> SystemState : reads
```

<details><summary>PlantUML equivalent</summary>

```plantuml
@startuml
skinparam classAttributeIconSize 0
abstract class PhysicsAsset {
  +pose : Pose2D
  +local_keypoints : dict
  +forces : ForceSpec[]
  +keypoint(key) : ndarray
  +set_pose(pose)
  +fbd() : VGroup
}
class RigidBody2D {
  +mass_props : MassProperties
  +point_velocity(ref, state) : ndarray
}
class Assembly {
  +members : PhysicsAsset[]
  +timeline : Timeline
  +resolve(ref) : ndarray
}
class SystemState {
  +entities : Map
  +fields : Map
  +observables : Map
}
interface Trajectory {
  +state_at(t) : SystemState
}
interface Binding {
  +apply(assembly, state)
}
class Recipe
class ProblemScenePlan
class MechanicsRenderer

PhysicsAsset <|-- RigidBody2D
PhysicsAsset <|-- Support
RigidBody2D <|-- Block
RigidBody2D <|-- Disk
RigidBody2D <|-- Rod
Support <|-- Floor
Support <|-- Incline

PhysicsAsset "1" o-- "1" Pose2D
PhysicsAsset "1" *-- "0..*" ForceSpec : declares
RigidBody2D "1" o-- "1" MassProperties
Assembly "1" o-- "1..*" PhysicsAsset : members
Assembly "1" o-- "0..*" Contact
Assembly "1" o-- "0..*" Constraint
Assembly "1" o-- "1" Timeline
Timeline o-- Trajectory
Timeline o-- EventSequence
Trajectory ..> SystemState : produces
SystemState "1" o-- "1..*" RigidKinematicState
Binding ..> SystemState : reads
Binding ..> PhysicsAsset : set_pose
Recipe o-- Assembly
Recipe o-- Trajectory
ProblemScenePlan ..> Recipe : plan_to_recipe
MechanicsRenderer ..> Assembly
MechanicsRenderer ..> SystemState
@enduml
```

</details>

---

## 2. Flow diagrams

### 2a. Build & render pipeline

The solver-free contract: physics is computed *outside* the framework, fed in as
a plan, turned into generic assets + a trajectory, then rendered.

```mermaid
flowchart LR
  subgraph Calc["Calculation layer (human / AI / SciPy / Krotov)"]
    P["Physics problem / corpus row"]
  end
  P --> PR["ProblemRef"]
  PR --> PSP["ProblemScenePlan<br/>entities / relations / phases / overlays"]
  PSP -->|plan_to_recipe| R["Recipe<br/>(specs, not VGroups)"]
  R --> ASM["Assembly<br/>generic assets"]
  R --> TRAJ["Trajectory provider<br/>state_at(t) -> SystemState"]
  R --> OV["Overlays / Views"]
  R --> EV["Timeline / EventSequence"]
  ASM --> RND["Renderer<br/>(spec -> Manim)"]
  TRAJ --> RND
  OV --> RND
  EV --> RND
  RND --> SC["Manim Scene"]
  SC --> ST["stitch-lesson"]
  ST --> VID[("final video")]
```

### 2b. Milestone dependency flow (development order)

Green = shipped. Each node is a Jira epic in project **PAC**; edges are the
`is blocked by` links (blocker -> blocked).

```mermaid
flowchart TD
  M1["M1 core+block (shipped)"]:::done
  M1_5["M1.5 pose / RigidBody2D"]
  M1_6["M1.6 kinematics + bindings"]
  M2["M2 supports / contact"]
  M3["M3 rolling / rotation"]
  M4["M4 connectors"]
  M5["M5 skill + gallery"]
  M6["M6 state / trajectory"]
  M7["M7 constraints / events"]
  M8["M8 curved surfaces"]
  M9["M9 overlays / graphs"]
  M10["M10 springs"]
  M11["M11 chains"]
  M12["M12 collisions"]
  M13["M13 orbital"]
  M14["M14 reference frames"]
  M15["M15 recipes gallery"]
  M16["M16 3D"]
  M17["M17 problem orchestration"]
  M18["M18 presentation"]
  F1["F1 fluid region"]
  F2["F2 hydrostatics"]
  F3["F3 pipes"]
  F4["F4 draining"]
  F5["F5 control volume"]
  F6["F6 fluid recipes"]

  M1 --> M1_5 --> M1_6
  M1_6 --> M2 --> M3 --> M4 --> M5
  M1_6 --> M6 --> M7
  M2 --> M8
  M6 --> M8
  M6 --> M9
  M9 --> M10
  M6 --> M10
  M7 --> M10
  M6 --> M11
  M8 --> M11
  M6 --> M12
  M7 --> M12
  M6 --> M13
  M9 --> M13
  M6 --> M14
  M9 --> M14
  M4 --> M15
  M9 --> M15
  M13 --> M15
  M6 --> M16
  M15 --> M16
  M15 --> M17
  M6 --> M18
  M9 --> M18
  M15 --> M18
  M6 --> F1
  F1 --> F2
  M9 --> F2
  F1 --> F3
  F1 --> F4
  F3 --> F4
  F1 --> F5
  F4 --> F5
  F1 --> F6
  F2 --> F6
  F3 --> F6
  F4 --> F6
  F5 --> F6
  M15 --> F6

  classDef done fill:#2b8a3e,color:#fff,stroke:#1b5e20;
```

<details><summary>PlantUML activity (pipeline)</summary>

```plantuml
@startuml
start
:Physics problem (corpus row);
:ProblemRef;
:ProblemScenePlan;
:plan_to_recipe -> Recipe;
fork
  :Assembly (generic assets);
fork again
  :Trajectory provider;
fork again
  :Overlays / Views;
fork again
  :Timeline / Events;
end fork
:Renderer (spec -> Manim);
:Manim Scene;
:stitch -> final video;
stop
@enduml
```

</details>

---

## 3. Sequence diagrams

### 3a. Rendering one animated scene (runtime)

Every rigid body is driven by one binding mechanism reading solver-supplied
state; `set_pose` is absolute so repeated frames never accumulate drift.

```mermaid
sequenceDiagram
  autonumber
  participant Scene
  participant Assembly
  participant Traj as Trajectory
  participant Bind as Binding
  participant Body as RigidBody2D
  participant Ov as Overlay
  participant Manim

  Scene->>Assembly: animate_trajectory(traj, t0, t1)
  loop each frame t in [t0, t1]
    Assembly->>Traj: state_at(t)
    Traj-->>Assembly: SystemState
    Assembly->>Bind: apply(SystemState)
    Bind->>Body: set_pose(pose)
    Note over Body: absolute pose - no drift
    Body-->>Bind: keypoints recomputed
    Assembly->>Ov: update(SystemState)
    Ov-->>Assembly: overlay VGroup
    Assembly->>Manim: render frame
  end
  Scene->>Scene: finish_with_narration()
```

### 3b. TDD development loop (per milestone)

How each milestone is built: acceptance criteria (the story's *Test cases*
subtask) become failing tests first, then the minimal asset makes them pass.

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer / AI
  participant Test as pytest
  participant Src as physics.domain
  participant Ruff as ruff
  participant Jira as Jira PAC
  participant Git

  Note over Dev,Jira: acceptance criteria come from the story's Test-cases subtask
  Dev->>Test: write failing test from acceptance criteria
  Test-->>Dev: RED (not implemented)
  Dev->>Src: implement minimal asset
  Dev->>Test: run pytest
  Test-->>Dev: GREEN (passes)
  Dev->>Ruff: ruff check + format
  Ruff-->>Dev: clean
  Dev->>Jira: move subtasks to Done
  Dev->>Git: commit milestone slice
  Note over Dev,Git: repeat per milestone M1.5 -> M18, F1 -> F6
```

<details><summary>PlantUML sequence (runtime render)</summary>

```plantuml
@startuml
Scene -> Assembly : animate_trajectory(traj, t0, t1)
loop each frame t
  Assembly -> Trajectory : state_at(t)
  Trajectory --> Assembly : SystemState
  Assembly -> Binding : apply(state)
  Binding -> RigidBody2D : set_pose(pose)
  note right of RigidBody2D : absolute pose - no drift
  Assembly -> Overlay : update(state)
  Assembly -> Manim : render frame
end
Scene -> Scene : finish_with_narration()
@enduml
```

</details>

---

## Rendering these locally

- **Mermaid**: renders inline in VS Code (Markdown preview) and on GitHub.
- **PlantUML**: install a PlantUML extension or run
  `plantuml file.puml`; the fenced ` ```plantuml ` blocks above are ready to copy.
