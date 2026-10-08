# Enclosure

Path: [docs](../README.md) › **enclosure**
Parent: [../README.md](../README.md)

**Covers:** the printed object — two parts, base and lid — and every feature on them. Each page
covers one feature end to end: its component YAML (if any), its placement in Python, and its
geometry in SCAD.
**Code:** `scad/enclosure.scad`, `enclosure_builder/layout.py`, `components/`

## Design

### Decisions

- **Two printed parts: an open-top base and a flat lid.** All components mount to the floor and
  walls of the base, so the lid carries nothing and can be removed without disturbing wiring.
  Rejected: a clamshell split at mid-height — panel parts would straddle the seam, and the PSU
  would have to be mounted to a part that is lifted off.
- **Base prints floor-down, lid prints top-face-down.** Both put their largest flat face on the
  bed, which leaves every hole either vertical or in a vertical wall — the two cases that print
  without supports. See [printability.md](printability.md).
- **The SCAD library only knows generic primitives** (wall rects/rounds/slots, floor bolts,
  standoffs, pads, lock slots and tongues, tabs, tie anchors, lid slots, ghosts). Every feature page below
  describes the Python function that emits them. See the root
  [YAML → Python → OpenSCAD](../README.md#yaml--python--openscad) decision.
- **Every part declares the space its wires need, as a `wiring` keep-out.** PSU terminals,
  panel-part cables and wire exits all get one; wiring zones may meet each other (that is where
  connections are made) but nothing solid may enter them. Shown orange in `interior*.png`.
  **Why:** V1 only reserved space for part bodies, and the owner found the RJ45 had no room for
  its cable and the inlet none for its wires (2026-10-07). A zone is checked by the validator,
  so a later layout cannot quietly crowd it. **Not checked:** that a wire can actually route
  from one zone to another — that remains a layout decision, recorded per enclosure.
- **Mains and low voltage live on opposite sides of the PSU, so their wires never cross.** The
  PSU component says which side of its terminal block is AC (`ac_side`, as seen facing the
  block); panel parts marked `mains: true` must sit on that side of the PSU's centre line, and
  perfboards and other panel parts on the DC side — or on the AC side beyond the mains parts,
  if their wires go round the PSU's far end ([wire_routing.md](wire_routing.md)). The validator
  enforces it. **Why:** owner
  requirement (2026-10-07) after V2 put the inlet on the AC side but the perfboard there too, so
  the DC wires had to cross the mains wires. A box-level rule, not a per-enclosure note, because
  every enclosure has a PSU, an inlet and electronics.
- **Interior corners are sharp, outer corners are rounded** (`box.outer_radius`). Sharp inside
  corners keep the full interior rectangle usable for the lid lip and component keep-outs;
  rounded outside corners only affect looks and handling.

## Contents

### Pages

- [`shell.md`](shell.md) — walls, floor and the shared outline of base and lid.
- [`lid_closure.md`](lid_closure.md) — tool-free drop-and-slide lid: tongues, ledges, detent tab, zip-tie lock.
- [`psu_mount.md`](psu_mount.md) — the PSU component and how it is bolted through the floor.
- [`perfboard_mount.md`](perfboard_mount.md) — perfboard component, standoffs and floor nut pockets.
- [`wall_openings.md`](wall_openings.md) — panel parts (C14 inlet, RJ45), wire exits (holes, JST pass-throughs, floor exits), zip-tie anchors.
- [`wire_routing.md`](wire_routing.md) — low-voltage route round the PSU's far end, printed wire loops.
- [`ventilation.md`](ventilation.md) — wall slots and lid slots for the PSU.
- [`mounting.md`](mounting.md) — tabs or floor holes for fixing the enclosure in place.
- [`printability.md`](printability.md) — print orientation, teardrops, bridged pockets.

## Related

- [../pipeline/validation.md](../pipeline/validation.md) — checks that these features do not collide.
- [../parameters/defaults.md](../parameters/defaults.md) — default values for these features.
