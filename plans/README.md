# Plans & Specifications

All planning, roadmap, and design-spec documents for **physics-through-anim** live
here. Rendered videos are never committed (see the repository `.gitignore`); this
folder is the durable, human-readable record of *what* we are building and *why*.

## Issue tracking (Jira)

The composable **physics asset library** and **fluids** roadmap are tracked in Jira:

- **Project:** PAC — *Physics Animation Creator*
- **Board / issues:** https://sutanuchaudhuri.atlassian.net/browse/PAC

Each milestone below is a Jira **Epic** with one **Story** (whose description holds
the full plan-doc contents) and three subtasks (*Dev milestones*, *Test cases*,
*Definition of Done*). Epics are linked with `is blocked by` dependencies. When a
milestone's status changes, update the Jira issue — Jira is the source of truth for
status; these documents are the source of truth for design.

## Contents

| Document | What it covers |
| --- | --- |
| [ROADMAP.md](ROADMAP.md) | Studio production rules, course map, lesson template, and milestones |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Scalable, cross-domain namespace & layering of the physics framework |
| [DIAGRAMS.md](DIAGRAMS.md) | Entity/class, flow, and sequence diagrams (Mermaid + PlantUML) |
| [physics_asset_library.md](physics_asset_library.md) | Signed-off overview of the composable asset library |
| [asset_library/](asset_library/) | Per-milestone plans M1–M18 (see [asset_library/README.md](asset_library/README.md)) |
| [fluids/](fluids/) | Fluids domain plans F1–F6 (see [fluids/README.md](fluids/README.md)) |
| [rolling_slipping_concepts_misconcepts.md](rolling_slipping_concepts_misconcepts.md) | Source spec for the flagship 28-scene rolling/slipping lesson |
| [rod_slipping_new_edge.md](rod_slipping_new_edge.md) | Plan for the rod-slipping-at-an-edge lesson |

## Conventions

- One Markdown file per milestone or lesson spec; keep pseudocode close to the
  design so it can be implemented without re-deriving decisions.
- Record decisions and their rationale in a `## Revisions` section rather than
  rewriting history in place.
- Milestone IDs (`M1`, `M1.5`, `F1`, …) are stable and map 1:1 to Jira epics.
