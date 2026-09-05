---
name: video-compilation
description: 'Build custom, arbitrary-order videos ("compilations"/playlists) from a lesson''s rendered scenes in physics-through-anim, distinct from the whole-lesson stitch. Use when the user wants to stitch all videos in a folder, stitch a scene range like "scene 1 to 10", insert a scene between two existing scenes (e.g. "introduce scene 21 between 12 and 13"), remove a scene and regenerate the video, or maintain multiple named groupings of the same lesson''s scenes -- including overlapping ones like "1-10" and "6-11" existing side by side. Covers the compile/stitch-compilation/list-compilations CLI, the compilations.toml registry, and the scene-selector syntax (ranges, inserts, comma lists).'
---

# Video Compilation (Custom Scene Stitching)

This is a companion to `.github/skills/physics-animation-standards/SKILL.md`
Rule 13 (which stitches **one lesson's entire scene set, in its own fixed
order**, into `media/final/<lesson_name>_full.mp4`). This skill is for
everything else: an arbitrary subset, a custom order, an inserted scene, a
removed scene, or several different named groupings of the same lesson's
scenes that may overlap each other. Never hand-roll a new `ffmpeg concat`
invocation for any of this — always go through the `compile`/
`stitch-compilation` commands described below, which read/write the same
persisted registry every time.

## 1. The core mechanism

- **`lessons/compilations.toml`** is the source of truth: a named, ordered
  list of scene ids per compilation, e.g.:

  ```toml
  [compilations.rod_1_10]
  lesson = "rod_slipping"
  scenes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
  output = "rod_1_10.mp4"
  ```

  Read/written through `CompilationRegistry` in
  `physics_through_anim.lessons.compilation_registry` — never hand-edit this
  file directly if a CLI command can do it; the CLI guarantees valid TOML and
  a consistent shape.
- **`compile`** (in `render.py`, wired to the `compile` CLI subcommand)
  parses a scene selector into an explicit scene id list, **persists** it
  under a given `--name` in `compilations.toml` (creating it, or overwriting
  it in place if that name already exists), then renders any scenes that
  aren't already rendered at the requested quality and concatenates them in
  exactly that order.
- **`stitch-compilation`** rebuilds an already-defined compilation purely
  from the registry — use this after re-rendering one of its scenes, without
  needing to retype the scene list.

## 2. Scene selector syntax

Passed as the `scenes` argument to `compile`. Comma-separated tokens, each
either a single zero-padded scene id (`"07"`) or an inclusive numeric range
(`"01-10"`); tokens are kept in **exactly the order given**, so this is also
how custom ordering, insertion, and removal are expressed — there is no
separate "insert" or "remove" flag, it's just a different selector string:

| Request | Selector |
| --- | --- |
| Stitch every scene in the lesson | `all` |
| Stitch scene 1 to scene 10 | `01-10` |
| Introduce scene 21 between scenes 12 and 13 | `01-12,21,13-44` |
| Remove scene 5 from an existing 1–10 compilation | `01-04,06-10` |
| A reversed/out-of-order clip | `10-06` (descending ranges work too) |

## 3. Command-line workflow

```bash
# Stitch every scene in a lesson into one named, ad-hoc video (same content
# as Rule 13's whole-lesson stitch, but under a name you control and without
# needing the lesson's own final_output setting)
uv run python main.py compile rod_slipping all --name rod_full_copy --quality high

# Stitch scenes 1 through 10
uv run python main.py compile rod_slipping 01-10 --name rod_intro --quality high

# Insert scene 21 between scenes 12 and 13
uv run python main.py compile rod_slipping 01-12,21,13-44 --name rod_with_21 --quality high

# Remove scene 5 and regenerate: re-run `compile` for the SAME --name with the
# scene omitted from the selector -- this overwrites that compilation's
# persisted definition in place, it does not create a duplicate
uv run python main.py compile rod_slipping 01-04,06-10 --name rod_intro --quality high

# A second, overlapping grouping of the same scenes is fully independent --
# just give it a different --name; both "rod_intro" (01-10) and "rod_6_11"
# (06-11) can coexist, nothing about defining one affects the other
uv run python main.py compile rod_slipping 06-11 --name rod_6_11 --quality high

# Rebuild an existing compilation from the registry without retyping the
# scene list (e.g. after re-rendering one of its scenes at a new quality)
uv run python main.py stitch-compilation rod_intro --quality high

# See every compilation currently defined and its scene list
uv run python main.py list-compilations
```

Makefile equivalents exist too (`make compile LESSON=... SCENES=... NAME=...`,
`make stitch-compilation NAME=...`, `make list-compilations`) — prefer these
for the user if the repo's `Makefile` is already the entry point they've been
using for `render-lesson`/`stitch-lesson`.

## 4. Rules to follow every time

- **Reordering, inserting, or removing a scene always means re-running
  `compile` with the same `--name` and an updated selector** — never edit
  `compilations.toml` by hand, and never treat a one-off `ffmpeg` command as
  the fix. The registry must end up reflecting the new scene list, or the
  next `stitch-compilation` call will silently rebuild the old version.
- **Overlapping/duplicate scene membership across compilations is explicitly
  allowed** — do not warn the user or refuse just because scene 7 already
  appears in another named compilation; each compilation is an independent,
  named definition.
- **`--name` identifies the compilation, not the output file** — `--output`
  defaults to `<name>.mp4` but can be set independently; don't assume the two
  must match if the user asks for a specific output filename.
- Scene ids are always the lesson's own zero-padded ids from `lessons.toml`
  (via `LessonRegistry`) — a range like `01-10` is resolved against that
  lesson's actual registered scenes, and an unknown id raises a clear
  `KeyError` naming exactly which id wasn't found, rather than silently
  skipping it.
- Quality must match between what's already rendered and what you ask
  `compile`/`stitch-compilation` for, same as Rule 13's whole-lesson stitch —
  `compile` renders any missing scene at the requested quality automatically,
  but won't re-render a scene that already exists at a *different* quality
  just because a new one was requested elsewhere in the same compilation.
- Compilation videos land in `media/final/<output>`, same folder as the
  whole-lesson stitches — pick a `--name`/`--output` that won't collide with
  a lesson's own `<lesson_name>_full.mp4`.
