# Wire routing

Path: [docs](../README.md) › [enclosure](README.md) › **wire_routing**
Parent: [README.md](README.md)
**Code:** `enclosure_builder/layout.py` (`place_lv_route`), `enclosure_builder/validate.py` (side rule), `scad/enclosure.scad` (`wire_guide`), `config/defaults.yaml` (`wire_guides:`)
**Covers:** how low-voltage wires get from the PSU's DC terminals to the electronics without
meeting mains wiring, and the printed loops that hold them.

## What it does

With `psu.lv_route: far_end`, the build reserves a wiring channel along the PSU's DC-side long
face (between the PSU and that wall) and another between the PSU's far end and the end wall,
and puts printed wire loops on the walls of both: every `spacing` mm along the side channel's
wall and two on the far-end wall. Low-voltage wires leave the DC terminals,
thread through the loops along the PSU, and come round its far end to the AC side.

## Decisions

### Low voltage may sit on the AC side if its wires go round the far end

**Why.** Owner design (2026-10-07). Putting the inlet and the perfboard in the same band (the
AC side) avoids a wasted band on each side of the PSU; routing the DC wires the long way round
the PSU means they never pass the terminal end on the AC side, where the mains wires are.
**Rule (validator).** A low-voltage part on the AC side is allowed only with `lv_route` set, and
only if it is at least `psu.lv_gap` (20 mm) from the mains region: the bounding box of every
mains body, mains cable zone and the PSU's terminal space (the inlet's wires run somewhere
inside that hull). Without `lv_route`, low-voltage parts must be on the DC side.
**Changed 2026-10-08:** the distance used to be measured only along the PSU's length, which
banned low voltage from the whole width of the box near the mains end — e.g. behind an inlet
mounted next to the terminals, where no mains wire goes (owner pointed out the wasted space).
**Rejected.** PSU centred with mains on one side and electronics on the other (the previous
layout): a 60 mm mains band with one inlet in it and empty floor beside, which made the box
239 mm wide and too wide for mounting tabs.

### Loops lean on the wall, sized for loose wires

**Why.** Owner (2026-10-08): with the wall as one side the loop is stronger — it is anchored
along its whole height, not only by two thin feet — and it uses less plastic. Each loop is a leg
standing on the floor `w` out from the wall plus a 45° roof rising from the leg's top back into
the wall, so it prints in place without support; the roof is kept `t` thick square to its face.
The tunnel is 7 mm out from the wall and 8 mm tall before the roof — two 14 AWG power leads plus
several signal wires, threaded through without connectors.
**Rejected.** Free-standing arches: weaker, and two walls instead of one. Tunnels big enough for
an XT60 (9 × 17 mm): asked for, then dropped by the owner (2026-10-08) — wires only. The optional
`wire_guides.fits: [a, b]` check remains for an enclosure that does need a connector to pass.
**Constrains.** Loops are wall features: vents skip them, and through-cuts keep
`feature_margin` from them. The roof's top (~17 mm) must stay below the lid lip; the build checks.
**Changed 2026-10-08:** previously free-standing pointed arches centred in the channel.

- **Channel width is checked against the loop's reach from the wall** (w + t + 1 mm), so a layout cannot squeeze
  the route shut. The channels are `wiring` keep-outs and loops are `anchor`s, so nothing solid
  may be put in the route.
- **Loops every 45 mm** keep a bundle from sagging into the PSU's side; two in the far-end
  channel hold the turn.

## Related

- [README.md](README.md) — the mains/low-voltage side rule this extends.
- [psu_mount.md](psu_mount.md) — `ac_side` and the terminal zone the route starts from.
- [printability.md](printability.md) — why every overhang here is 45°.
