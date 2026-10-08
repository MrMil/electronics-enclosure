# PSU mount

Path: [docs](../README.md) › [enclosure](README.md) › **psu_mount**
Parent: [README.md](README.md)
**Code:** `components/psu/s-100-5.yaml`, `enclosure_builder/layout.py` (`place_psu`), `scad/enclosure.scad` (`floor_additions` pads, `floor_cutters` floor bolts)
**Covers:** the PSU component schema and how a PSU is fastened to the floor.

## What it does

The PSU lies flat on four printed pads. M3 bolts come up from under the floor, through short
slots in floor and pads, into the PSU's own threaded bottom holes. Heads sit in counterbores in
the floor's underside. The terminal end gets a wiring zone (`terminal_clearance`).

PSU fields: `size` (local frame: x from the terminal end), `holes`, `hole_slack` (± slot along x),
`max_penetration`, `bolt_len`, `terminal_clearance`, `ac_side`, `terminal_block` (preview only), plus the
instance's `lv_route` (see [wire_routing.md](wire_routing.md)) and the
library `source` / `verified` / `check` fields.

## Decisions

### Local frame, four orientations, all rotations

Component holes are given in the PSU's own frame: x from the terminal end, y across, growing
toward the left of someone facing the terminal block — the AC side when `ac_side: left`.
`terminals: left | right | front | back` places that frame by rotation only (`psu_frame`), never
by mirroring, so a PSU whose holes are all on one edge (the S-20-5's are on the AC edge) lands
the way it physically sits. Bolt slots run along the PSU's length whichever way it faces.
**Why.** The 20W enclosure needed the PSU facing the front wall; before that only left/right
existed, and "right" mirrored the PSU, which was harmless only because the S-100-5's holes are
symmetric. `holes_alt` exists for a PSU whose holes are known up to a mirror image: those
positions are cut and padded but not bolted.

### Through the floor into the PSU's own threads

**Why.** No nuts, no inserts, and the PSU's threads are metal (owner: minimal non-printed parts).
Bolting from below leaves the top of the PSU free for airflow and terminal access.
**Rejected.** The three M3 holes on the PSU's long side: the PSU would have to touch that wall,
blocking its side vents. Printed clamps: more plastic under heat and creep load.
**Constrains.** The PSU is fitted before the enclosure is fixed to its surface.

### Bolt depth fixed at 3 mm by the pad height

`pad_h = (head_h + head_recess + layer_h) + (bolt_len − max_penetration) − floor`.
**Why.** The owner flagged that these PSUs have shallow mounting holes and that a deep screw can
short the PCB. The S-100F datasheet (the original this clone copies) gives no limit. Mean Well's
installation manual says screws must keep insulation distance from internal parts and to read
the limit from each case drawing; on the newer drawings that state one, the smallest is 3 mm
(LRS-350 bottom holes, "L=3mm"). So `max_penetration: 3`, and the geometry, not the user, enforces
it: with M3 × 6 the pads are 3.5 mm tall and the tip enters exactly 3 mm. The BOM says not to
substitute a longer bolt.
**Constrains.** Changing `bolt_len` or the floor moves the PSU up or down; keep-outs follow.

- **Hole positions from the Mean Well S-100F drawing (case 902):** 62 and 182 mm from the
  terminal end, rows 9 mm from each long edge (120 × 80 pitch). The clone maker's own drawing
  (Finglai S-100) is identical, and its side-face holes match the owner's unit. An earlier photo
  suggested different positions; that was perspective.
- **`hole_slack: 1.5`** — slots only absorb print and sheet-metal tolerance now that the
  positions come from the manufacturer. (Was ±8 mm while unverified.)
- **`terminal_clearance: 40`.** The 7 terminals (1 L, 2 N, 3 FG, 4–5 −V, 6–7 +V) face up at
  the end, wires leave toward the end wall. 40 mm fits ferrules, the bend of 14 AWG output wire,
  and the inlet's wires arriving from the side. It is a `wiring` zone, so the inlet's cable zone
  may meet it but nothing solid may enter it. (Was 25 mm; the owner pointed out wires need room.)
- **`ac_side: left` for the S-100-5**: facing the block, L, N, FG are on the left, −V/+V on the
  right (owner's photo, matching the S-100F pin numbering). It drives the mains/low-voltage side
  rule in [README.md](README.md).
- **Lid vents skip the terminal end** — see [ventilation.md](ventilation.md).

## Related

- [README.md](README.md) — wiring zones, the rule that gives the terminals their space.
- [printability.md](printability.md) — the bridged counterbore under each bolt.
- [../enclosures/100w.md](../enclosures/100w.md) — what the owner should check on the unit.
