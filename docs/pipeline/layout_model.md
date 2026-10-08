# Layout model

Path: [docs](../README.md) › [pipeline](README.md) › **layout_model**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/layout.py`
**Covers:** the data structure the placement functions fill in, and the rules shared by all of
them. The individual `place_*` functions are documented on their feature pages under
[../enclosure/](../enclosure/README.md).

## What it does

`build_model` creates a `Model` and calls the placement functions in a fixed order: box scalars,
lid lock, PSU, perfboards, panel parts, wire exits, mounting, vents. Each appends to:

- `prims` — named lists that become SCAD globals (`PADS`, `WALL_RECTS`, `LID_TONGUES`, …);
- `keepouts` — `Box3` volumes in interior coordinates, kind `solid`, `wiring` or `anchor`;
- `wall_feats` — `WallFeat` rectangles in a wall's (u, z) plane, `through` or outside-only,
  with a `group` so a part's own features are not checked against each other;
- `bom`, `checks` (datasheet values to confirm), `warnings`, `errors`.

`Model.wiring()` adds a wiring keep-out and its orange preview ghost in one call, so no part can
reserve wire space without it being visible. `Model.note_verification()` reports each library
part once however many times it is placed.

## Decisions

- **Primitives are flat lists of numbers and strings**, not SCAD objects. OpenSCAD has no
  dictionaries in stable releases; positional lists are what its `for` loops consume. The list
  layouts are documented by comments at each use in `scad/enclosure.scad`.
- **A part's own body and cable zone do not overlap**: the cable zone starts where the body
  ends (`wall_box(start=...)`), so the generic overlap check needs no same-part exception.
- **Vents are placed last** because they fill whatever wall area is left (see
  [../enclosure/ventilation.md](../enclosure/ventilation.md)).
- **`clearance` keep-outs** (perfboard side room) may overlap wiring, anchors and other
  clearance, plus solids flagged `connector` (non-mains wall connector bodies); see
  [../enclosure/perfboard_mount.md](../enclosure/perfboard_mount.md).
- **Three keep-out kinds.** `solid` (PSU body, perfboard + parts, panel bodies) may not overlap
  anything; `wiring` (PSU terminals, panel cables, wire exits) may overlap other wiring; `anchor` (zip-tie anchors) may
  sit in wiring space because that is where wires are. Without the distinction a tie anchor next
  to the PSU terminals would be a false collision.
- **`pick_length` chooses the shortest standard M3 length meeting a minimum** from
  `hardware.m3.lengths`; geometry is then derived from it (root decision in
  [../README.md](../README.md)).
- **Placement functions append errors instead of raising**, so one build reports every problem
  in the file at once.

## Gotchas

- Keep-outs are axis-aligned boxes; that is why PSUs and boards only rotate in 90° steps.

## Related

- [validation.md](validation.md) — consumes `keepouts` and `wall_feats`.
- [output.md](output.md) — consumes `prims`, `scalars`, `bom`.
