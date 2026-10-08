# Output

Path: [docs](../README.md) › [pipeline](README.md) › **output**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/emit.py`, `enclosure_builder/render.py`, `enclosure_builder/cli.py`, `build.py`
**Covers:** what a build writes and how OpenSCAD is driven.

## What it does

Per enclosure, under `enclosures/<name>/`:

- `build/params.scad` — every scalar and primitive list as SCAD globals.
- `build/{base,lid,assembly,interior}.scad` — wrappers: include the library, include the params,
  call one part module. Open these in the OpenSCAD GUI to inspect.
- `stl/<name>-enclosure-base.stl`, `stl/<name>-enclosure-lid.stl` — already in print
  orientation.
- `stl/<name>-enclosure-plate.stl` — base and lid arranged together, written only when both fit
  on one bed (`validate.plate_layout`: lid behind the base, else beside it, 5 mm apart, within
  `bed - bed_margin`). The owner asked to print an enclosure in one go (2026-10-08); a stale plate
  file is deleted when the parts stop fitting together. The enclosure name is in the file name (owner's convention, 2026-10-08) so a file
  copied into a slicer or another folder still says which enclosure it belongs to.
- `preview/*.png` — closed box from two sides, open box with parts as coloured blocks and wiring
  zones in translucent orange (also from above), the empty base without lid from two sides and straight down, lid
  as printed.
- `BOM.md` — the three key renders at the top (empty base, base with parts, closed — the owner
  wants them visible for every enclosure, 2026-10-08), printed parts with sizes and which
  openings were left without a self-supporting top
  (so the slicer's support settings can be chosen knowingly), how to close/open the lid, hardware totals with what each
  is for, where to drill the mounting surface under floor wire exits (for a round hole: the drill
  to put straight through it, see [../enclosure/wall_openings.md](../enclosure/wall_openings.md)), "Check before printing"
  (datasheet values), warnings.

`build.py --coupon <passthrough part>` writes `test-prints/<part>-coupon.stl`: a wall-thick plate
with one slot cut exactly as in a wall, printed standing up, to test-fit a connector in minutes
before printing a base (added after the 20W's first LED slots were too small, 2026-10-08).

## Decisions

- **Wrappers `include` the library by relative path**, so the repository can move and the
  generated files still open in the GUI.
- **STLs are exported in print orientation** (lid flipped), so they can be dropped onto the
  slicer bed without rotating — the orientation is part of the support-free design.
- **Manifold backend, previews with `--render`.** Manifold renders in seconds where CGAL takes
  minutes on the vent patterns; preview-mode PNGs showed see-through artefacts on differenced
  geometry that looked like real holes.
- **Parts in previews are coloured blocks (`GHOSTS`)**, not models: enough to judge clearances
  and spot a misplaced part, with no CAD files of third-party parts to maintain.
- **OpenSCAD output containing `ERROR` fails the build**; warnings are printed.

## Related

- [validation.md](validation.md) — runs before anything here is written.
- [../enclosure/printability.md](../enclosure/printability.md) — why the orientations are fixed.
