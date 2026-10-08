# Defaults

Path: [docs](../README.md) › [parameters](README.md) › **defaults**
Parent: [README.md](README.md)
**Code:** `config/defaults.yaml`
**Covers:** the house-style values every enclosure inherits. Values whose reason is a feature's
design are explained on that feature's page; this page covers the global ones.

## What it does

Supplies every key an enclosure may omit. Anything here can be overridden in an `enclosure.yaml`.

## Decisions

- **`printer.bed: [256, 256]`** — the Bambu Lab A1, the owner's main printer (confirmed
  2026-10-07; a Voron Trident may come later and is larger, so A1 stays the limit).
- **`printer.bed_margin: 2`** — total mm per axis kept free so a part is never exactly the bed's
  size (slicers and bed clips need a little room).
- **`printer.support_margin: 0`** — bed room outside walls whose holes need supports; off by
  default because the earlier enclosures were sized before it existed and print with bridges.
- **`printer.layer_h: 0.2`** is the sacrificial bridge-layer height, matching the common 0.2 mm
  profile. It must equal the slicer's layer height for the bridge trick to land on a layer
  boundary (see [../enclosure/printability.md](../enclosure/printability.md)).
- **`box.wall: 2.4`** = six 0.4 mm perimeters: solid walls with no infill pattern, stiff enough
  for a 230 mm span, thin enough that panel parts' screws reach through.
- **`box.floor: 3.0`.** Must hold M3 nut pockets (2.7 deep) and carry the PSU; thinner floors
  leave the nut pockets breaking through.
- **`box.feature_margin: 2.0`** — minimum solid material between two wall features, roughly the
  minimum that prints as a reliable bridge/pillar at 0.4 mm nozzle.
- **M3 numbers** (`hardware.m3`): 3.4 clearance (3.2 binds on printed holes, which print
  undersize); 6.4 counterbore for a 5.5 head; 0.3 recess so heads never stand proud of the floor's
  underside (the enclosure must sit flat on its mounting surface). Nut pocket clearance 0.3
  (dropped in from below, must slide in freely).
- **`hardware.m3.lengths`** is the list of lengths actually sold in common M3 assortments;
  [length picking](../pipeline/layout_model.md) only chooses from it.
- **`perfboard.min_standoff: 6`** — room under a perfboard for solder joints, clipped leads and a
  wire or two; 3 mm is the bare minimum, 6 avoids shorts against the nut pocket bridges.

## Related

- [component_library.md](component_library.md) — per-part values live there, not here.
- [../enclosure/lid_closure.md](../enclosure/lid_closure.md) — reasons for the `lid:` values (slide-lock geometry).
- [../enclosure/ventilation.md](../enclosure/ventilation.md) — reasons for the `vents:` values.
- [../enclosure/mounting.md](../enclosure/mounting.md) — reasons for the `mounting:` values.
