# Shell

Path: [docs](../README.md) › [enclosure](README.md) › **shell**
Parent: [README.md](README.md)
**Code:** `scad/enclosure.scad` (`outline2d`, `base`, `wall_frame`, `wall_prism`), `enclosure_builder/layout.py` (`place_box`)
**Covers:** the box itself — floor, walls, the outline shared with the lid — and the wall frame
every wall feature is placed in.

## What it does

`outline2d()` is the outer footprint: the wall rectangle with rounded vertical edges. The base
extrudes it from the floor's underside to the wall top and subtracts the interior box; the lid
plate is the same outline plus its finger pull.

`wall_frame(wall, u, z)` maps a local frame (x along the wall, y outward through it, z up, origin
on the interior face) onto any wall, so every wall cutter is written once.

## Decisions

- **Base and lid share one outline.** The lid's edge lines up with the walls exactly,
  with no separate dimension to keep in sync.
- **`wall_frame` uses a mirroring matrix for the front and right walls** so that local x always
  runs in the global +x/+y direction (the `u` convention in
  [../parameters/README.md](../parameters/README.md)). All cutters are symmetric or built from
  explicit `u` offsets, so the mirror has no visible effect.

## Gotchas

- Wall cutters extend 1 mm beyond both faces (`wall_prism(-1, WALL + 1)`) to avoid coplanar
  faces; anything that must stop inside the wall (pockets) passes its own depth.

## Related

- [lid_closure.md](lid_closure.md) — the lid plate cut from the same outline.
- [wall_openings.md](wall_openings.md) — the main user of `wall_frame`.
