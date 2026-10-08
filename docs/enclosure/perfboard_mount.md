# Perfboard mount

Path: [docs](../README.md) › [enclosure](README.md) › **perfboard_mount**
Parent: [README.md](README.md)
**Code:** `components/perfboard/`, `enclosure_builder/layout.py` (`place_perfboards`), `scad/enclosure.scad` (`floor_additions` standoffs, `floor_cutters` nut pockets)
**Covers:** the perfboard component schema and how boards are held.

## What it does

Each board hole gets a printed standoff on the floor. An M3 bolt goes down through the board and
the standoff into a hex nut sitting in a pocket opened from the floor's underside.

Perfboard fields: `size` (outline), `thickness`, `hole_d`, `holes` (any number — 2 for the
DIKAVS board, 4 for most), `component_h` (keep-out above the board).

The DIKAVS board was measured by the owner: 81 × 55, 3.1 mm holes whose edges are 9.6 mm from
the short sides; the holes are assumed centred across the width (they sit on the centre channel
in the photo). An M3 bolt passes a 3.1 mm hole.

## Decisions

### Bolt from the top into a nut under the floor

**Why.** The board can be removed with the lid off while the enclosure stays fixed in place (the
nut cannot fall out: the mounting surface closes the pocket). No inserts (owner).
**Rejected.** Bolt from below with the nut on top of the board: the bolt spins when undoing the
nut once the box is mounted. Nut trapped inside the standoff via a side slot: weakens a 7 mm
standoff.
**Constrains.** Nuts go in before the enclosure is fixed down.

- **Standoff height is derived from the shortest standard bolt that gives at least
  `min_standoff`**, positioned so the bolt tip ends 0.5 mm inside the floor's underside — fully
  through the nut, never proud of the surface the box sits on.
- **Any number of holes.** The owner's first board is held by 2; most boards have 4. The schema
  is a list so neither is special.
- **Standoff OD 7 mm with a 45° foot 3 mm wide.** The nut pocket takes 2.9 of the 3 mm floor
  under each standoff, so without the foot the standoff would hang on a 0.1 mm skin. The foot
  carries the load into the surrounding full-thickness floor and prints without supports.
- **Optional side clearance per board** (`clearance: {left|right|front|back: mm}`, interior
  directions after rotation): free room beside the board's edges for its side connectors and
  their cables. It is a `clearance` keep-out: other wiring may share it, and so may a low-voltage
  wall connector body (an RJ45 coupler at the wall end of the strip — that is the kind of thing
  the room is for); the PSU, other boards and mains parts may not. Added for the 100W-masterbox:
  3 cm on both long sides of the MAX485 board (modules overhang) and 3 cm on one long side of the
  ESP32 board (USB-C cable), owner 2026-10-08. Shown light blue in previews.
- **`rotate: 0 | 90` only.** Boards are laid parallel to the walls; arbitrary angles would break
  the axis-aligned keep-out check.

## Related

- [printability.md](printability.md) — bridged nut pocket.
- [psu_mount.md](psu_mount.md) — the other floor-bolted part; same bolt-length-first approach.
