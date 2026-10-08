# Printability

Path: [docs](../README.md) › [enclosure](README.md) › **printability**
Parent: [README.md](README.md)
**Code:** `scad/enclosure.scad` (`pointed2d`, `teardrop2d`, `bridged_pocket`, `part_base_print`, `part_lid_print`), `enclosure_builder/layout.py` (`_cutout`, roof heights)
**Covers:** what makes every feature print without supports, in the fixed orientations.

## What it does

- **Base**: floor on the bed. Every opening in a wall has a 45° pointed top (`pointed2d`,
  `teardrop2d`): vent slats, wire holes, connector slots, zip-tie tunnels. Panel-part cutouts
  (C14, RJ45) get as much point as their flange hides and the wall height allows. Pockets opened from the underside (PSU bolt heads, perfboard nuts) use
  sacrificial bridge layers. Lid-lock slots have a 45° ceiling; their entry notches are open at
  the top.
- **Lid**: top face on the bed; the lip, the tooth and every hole are vertical; the tongues'
  undersides (their in-use tops) are 45°.

## Decisions

### Sacrificial bridge layers over bed-side pockets (`bridged_pocket`)

**Why.** A counterbore or nut pocket opened from the bed side has a ceiling with a smaller hole
in it — a ring that would otherwise be printed in mid-air. Layer 1 above the pocket leaves a band
as wide as the hole open across the whole pocket, so its material bridges only the short way
between pocket walls; layer 2 then bridges the band, leaving the hole. One layer each, so
`printer.layer_h` must equal the slicer's layer height.
**Rejected.** Support material inside pockets: hard to remove from a 6 mm counterbore, and the
owner wants minimal supports. A 0.2 mm "drill-through" skin: needs a post-print step.
**Constrains.** Heads and nuts seat one layer above the pocket depth; `place_psu` and
`place_perfboards` include `layer_h` in their height maths.

### Pointed (almond) tops instead of bridges

**Why.** Owner request (2026-10-07): openings that can be shaped to print without support or
bridging should be. A 45° roof is self-supporting; a flat top is a bridge that sags and strings.
**Rule.** Openings nothing covers (vent slats, wire holes, JST slots, tie-anchor tunnels) get a
full point, accepting the extra height (half the opening's width). Panel-part cutouts get a full
point only if all of it stays hidden behind the flange (1 mm inside its edge) and below the wall
under the lid lip; otherwise they keep their plain shape (rectangle, circle) and print with a
bridge or a little support. Never a partial point.
**Why no partial points (owner, 2026-10-08).** Avoiding support only pays when it removes it
altogether; once a support or bridge is there, 10 mm vs 15 mm makes little difference, while a
truncated point can show past the flange as a visible notch. In 100W both the C14
(lying down) and the RJ45 are plain for this reason.
Plain cutouts are listed in the BOM's Supports column.
**Changed 2026-10-08:** previously panel cutouts got as much point as fitted (a trapezoid on the
C14, a truncated teardrop on the RJ45).
**Changed 2026-10-07:** previously vent slots and connector slots had flat (bridged) tops and
round holes ≥ 10 mm were truncated at 1.08 r for looks. Changed at the owner's request: fewer
bridges beat a slightly taller opening.
- **45° maximum slope everywhere else** (tab ribs, standoff feet, countersinks open upward,
  lid-lock ledges and tongues, the tooth ramp, wire loops, the zip-tie lug's underside).
- **Retaining faces that must be horizontal are avoided altogether.** In this pair of print
  orientations any horizontal retaining face is an overhang on one of the two parts, so the lid
  lock uses parallel 45° faces (see [lid_closure.md](lid_closure.md)).

## Gotchas

- Slicer "detect bridging perimeters" should be on; nothing here needs supports, so supports
  should be off — auto supports would fill the bed-side pockets.

## Related

- [psu_mount.md](psu_mount.md), [perfboard_mount.md](perfboard_mount.md) — users of `bridged_pocket`.
- [wall_openings.md](wall_openings.md) — users of `teardrop2d`.
- [../parameters/defaults.md](../parameters/defaults.md) — `printer.layer_h`.
