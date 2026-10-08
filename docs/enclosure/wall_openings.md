# Wall openings

Path: [docs](../README.md) › [enclosure](README.md) › **wall_openings**
Parent: [README.md](README.md)
**Code:** `components/panel/`, `components/passthrough/`, `enclosure_builder/layout.py` (`place_panel_parts`, `place_wire_holes`), `scad/enclosure.scad` (`wall_cutters`, `FLOOR_SLOTS`, `tie_anchor`)
**Covers:** everything wires or connectors pass through, except vents: panel parts (C14 inlet,
RJ45 bulkhead) and wire exits (round holes or connector pass-through slots, in a wall or the floor).

## What it does

A **panel part** (`components/panel/`) is a cutout (`rect` or `round`), optional M3 flange bolts
relative to the cutout centre, a `flange` footprint on the outside face, an `inside` solid body
keep-out, a `cable` wiring zone behind the body, optional `max_panel_t`, and `mains: true` for
parts carrying mains (they must sit on the PSU's AC side, see [README.md](README.md)).

A **wire exit** (`wire_holes[]`) is either a round hole (`d`) or a library pass-through
(`part:` from `components/passthrough/`, a rounded slot), on a wall (`wall, u, z`) or in the
floor (`wall: floor, at: [x, y], rotate`). Each gets a wiring zone `inside_depth` deep and, by
default, a printed zip-tie anchor.

## Decisions

- **Panel parts declare their cable space separately from their body.** The body is solid; the
  cable zone is `wiring` and may meet other wiring zones (C14 wires meeting the PSU terminal
  zone) but no solid part. Added because V1 placed the RJ45 coupler with no room for its patch
  cable and the inlet with no room for its wires (owner feedback 2026-10-07).
- **C14: measured by the owner.** 27 × 47 body (cut 27.5 × 47.5), M3 through 3.6 mm flange holes
  39.8 mm apart, flange 50.4 × 69 × 2.6, wires to ~60 mm behind the panel. Body depth 35 mm is an
  estimate inside that 60. Nut inside, head outside (owner's preferred joint).
- **Flange-bolt nuts are checked**: each nut's footprint on the inside face must clear the floor
  and the lid lip by 0.5 mm (`edge_margin`; a nut needs room to sit and turn, not wall material
  around it). Added after a lying-down C14 put its nuts into the floor and the lip.
- **C14 orientation is per enclosure.** Upright, its 69 mm flange sets the box height; with
  `rotate: 90` it needs ~50 mm. 100W uses 90 so the box can be PSU-height.
- **RJ45: measured by the owner.** 23.4 mm thread (cut 24.0), 29 mm nut, 18 mm behind the panel.
  The cable zone (60 mm) is plug ~22 + boot ~15 + a Cat6A bend. Outside flange not measured;
  assumed ≤ the nut.
- **LED exits are pass-through slots for JST SM 3-pin connectors**, so the owner can solder
  pigtails to the perfboard outside the box and feed them out (owner request). Slot 15.6 × 10.2:
  the full outside envelope of either 3-pin housing from JST's drawings — plug SMP-03V-BC 8 × 7.4
  plus latch flaps standing ~3.2 mm out each side (14.6 across the pins), receptacle SMR-03V-B
  10.5 × 7.5 plus a 1.7 mm lock bump (9.2 thick) — + 0.5 mm per side, so a connector passes
  without squeezing its flaps. Envelopes for connectors passing through holes always include
  latches, flaps and bumps, never just the body.
  **Changed 2026-10-08:** was 11.5 × 8.5, from the receptacle's body only; the owner printed the
  20W and the connectors did not fit. `build.py --coupon jst-sm-3pin` prints a test plate.
  Wiring zone 20 mm: the pigtails are fed
  out before the board is screwed down, so afterwards only wire stays inside and needs room to
  bend. (Was 30 mm, sized for the 18.2 mm housing; that made the box too deep for the bed.)
- **Pass-throughs are a library kind, not inline sizes**, because the same connector will be used
  on every LED enclosure and its size came from a datasheet that should be cited once.
- **Floor exits take `anchor_at: [dx, dy]`** to move the zip-tie anchor when the default spot
  (just behind the slot) is under a part, as in the 20W.
- **Wire exits can be in the floor** (owner's option 3). Floor exits are rejected if they lie
  under a solid keep-out. The surface below must have matching holes (the owner drills the
  wooden mounting board); the BOM's "Drilling the mounting surface" gives their positions from a
  mounting hole and a drill size covering the slot's diagonal.
- **Every opening has a 45° pointed top**, full on wire exits; on panel parts only when the whole
  point is hidden by the flange, otherwise none. Wall-feature extents include the roof, so the validator spaces it. See
  [printability.md](printability.md).
- **Wall pass-throughs accept `rotate: 90`** (slot stood on end), for walls where a narrower,
  taller opening fits better.
- **Zip-tie anchors next to each exit** so a tug outside never reaches the solder joints or the
  PSU terminals.
- **RJ45 has no M3 bolts** — it clamps with its own nut.

## Gotchas

- JST SM is rated 3 A per contact. Four exits carry at most 12 A of the PSU's 20 A; longer strips
  need separate power injection, not more current through these connectors.
- JST also documents panel-mounting the SM plug in a 0.5–2.0 mm panel; the 2.4 mm wall would need
  `max_panel_t`-style thinning. Not used: the owner wants the connector to pass through.

## Related

- [README.md](README.md) — wiring zones.
- [../pipeline/validation.md](../pipeline/validation.md) — wall-feature and floor-exit checks.
- [ventilation.md](ventilation.md) — vents fill the wall area these features leave free.
