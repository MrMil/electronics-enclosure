# Validation

Path: [docs](../README.md) › [pipeline](README.md) › **validation**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/validate.py`
**Covers:** the checks that stop a bad layout from producing STLs.

## What it does

1. Keep-outs lie inside the interior and below the lid lip.
2. Keep-outs do not overlap (except wiring/anchor combinations — see
   [layout_model.md](layout_model.md)).
3. Wall through-cuts stay `feature_margin` from wall ends, the floor and the lid lip (the lid-lock
   notches are exempt: they are meant to reach the top); outside-only
   footprints stay within the wall's height; features of different parts on one wall keep
   `feature_margin` apart (two outside-only footprints may touch). Panel-part flange nuts use a
   0.5 mm floor/lip clearance instead (`WallFeat.edge_margin`).
4. Floor mounting holes and floor wire exits are not under any solid keep-out; floor wire exits
   also keep `feature_margin` from the walls (reason in
   [../enclosure/wall_openings.md](../enclosure/wall_openings.md)).
5. Mains panel parts are on the PSU's AC side; perfboards and low-voltage panel parts on its DC
   side, or on the AC side ≥ `lv_gap` from the mains region when `lv_route: far_end` (rules in
   [../enclosure/README.md](../enclosure/README.md) and [../enclosure/wire_routing.md](../enclosure/wire_routing.md)).
6. Base and lid footprints fit the bed minus `printer.bed_margin`, in either orientation; the
   spare millimetres are written to the BOM. The base also keeps `printer.support_margin` of bed
   outside each wall whose holes need slicer supports (C14 cutout, plain round holes), so tree
   supports have somewhere to stand. Default 0; the 100W-masterbox uses 5 (owner, 2026-10-08).

## Decisions

- **Errors, not auto-fixes.** Moving a part is a design decision for the owner or the agent;
  the validator only says what collides and by how much.
- **Two outside-only footprints may touch** (e.g. a tab beside a flange): they are both solid
  plastic that merges, while a through-cut must keep material around it.
- **Bed fit keeps a 2 mm margin and reports what is left**, because the owner expected the
  layout constraints to push against the bed and wants to see how close it is.
- **Bed fit includes tabs and the lid's finger pull**, the parts most often forgotten when
  sizing a box.
- **Unverified components are warnings, datasheet ones are "checks", neither is an error.** A
  test-fit print is often how a guess gets verified; refusing to build would prevent it.

## Gotchas

- Validation knows nothing about wire routing or bend radii beyond the keep-out boxes; mains
  separation from low voltage is a layout choice recorded per enclosure.

## Related

- [../enclosure/lid_closure.md](../enclosure/lid_closure.md) — the lip limit.
- [../parameters/enclosure_definition.md](../parameters/enclosure_definition.md) — the file being checked.
