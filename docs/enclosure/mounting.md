# Mounting

Path: [docs](../README.md) › [enclosure](README.md) › **mounting**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/layout.py` (`place_mounting`), `scad/enclosure.scad` (`tab`, `FLOOR_MOUNTS` in `floor_cutters`), `config/defaults.yaml` (`mounting:`)
**Covers:** how the enclosure is fixed to whatever it is mounted on.

## What it does

`style: tabs` (default) adds flat ears flush with the floor's underside on any wall at any `u`,
each with one countersunk hole and two triangular side ribs. `style: floor` instead puts
countersunk holes through the floor at given interior `[x, y]`.

## Decisions

- **Tabs by default.** Screws are driven from above with the lid on and the parts installed,
  and nothing inside has to avoid them. Floor holes are the fallback when tabs would push the
  base past the bed; the validator rejects floor holes under any solid
  keep-out, so they always land in reachable free floor.
- **Screw size is a parameter (`screw_d`, `head_d`) and is not M3.** The owner asked for these
  holes to be parameters; they take whatever suits the surface (wood screws, M4). Default 4.5 mm
  through / 9 mm countersink fits #8 and M4 screws.
- **Ribs on the tab's side edges, not across its middle**, so a screwdriver and screw head reach
  the hole straight down. The rib slope is 45°, so it prints without supports.
- **Hole centre at 55 % of the tab length from the wall** — clear of the wall for the screw head,
  but not so far out that the tab levers off.

## Related

- [shell.md](shell.md) — tabs extend the base's footprint, which the bed check includes.
- [../pipeline/validation.md](../pipeline/validation.md) — floor-hole and bed-fit checks.
