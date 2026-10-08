# Ventilation

Path: [docs](../README.md) › [enclosure](README.md) › **ventilation**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/layout.py` (`place_vents`), `scad/enclosure.scad` (`WALL_SLOTS` in `wall_cutters`, `LID_SLOTS` in `lid`), `config/defaults.yaml` (`vents:`)
**Covers:** passive cooling for the PSU.

## What it does

Each `vents.walls[]` region (`wall`, `u` range, `z` range) is filled with vertical slots at
`pitch`, skipping any slot that would come within `feature_margin` of another wall feature. With
`lid_over_psu`, the lid gets slots across the PSU's width over its body, but not over its
terminal end.

## Decisions

### Passive convection: low wall intake, lid exhaust

**Why.** The owner requires the PSU to be well ventilated. A 100 W supply at ~85 % efficiency
dissipates ~15 W; the S-series case is itself perforated and designed for free air. Cool air
enters through low slots in the walls beside the PSU, the PSU's pads leave a gap under it, and
warm air leaves through the lid above it.
**Rejected.** A fan: an extra part, noise, and a failure point; not needed at this dissipation if
the slots are kept clear. Revisit if the PSU runs near 20 A continuously in a warm place.
Floor vents: blocked whenever the enclosure is fixed flat to a surface.
**Constrains.** Do not place parts that block the wall regions beside the PSU, and do not mount
the enclosure lid-down.

- **Vents are placed last and skip conflicts instead of erroring.** A vent region is "as many
  slots as fit here", so a new wire hole should not force the agent to re-plan the vents.
- **Slots are almond-topped**: the 45° point ends at the region's top `z`, so the slats print with
  no bridge (see [printability.md](printability.md)).
- **Slot width 2.5 mm.** Well under the 12.5 mm finger probe (mains is inside), and small enough
  to keep out most debris; 2.5 also bridges cleanly at the slot tops.
- **No lid slots over the PSU terminals** (`terminal_block.len + 10` mm skipped): anything
  dropped through the lid must not land on mains screw terminals.
- **No lid slots within `tab_len + 4` of the left edge or over the slide strip**, so the detent
  tab and its slits stay solid plate.
- **Slot pitch 6 mm** leaves 3.5 mm pillars — stiff enough that a 2.4 mm wall with 30 slots does
  not become floppy.

## Related

- [psu_mount.md](psu_mount.md) — pads that create the under-PSU air gap.
- [lid_closure.md](lid_closure.md) — lid slots stay inside the lip.
- [wall_openings.md](wall_openings.md) — features vents avoid.
