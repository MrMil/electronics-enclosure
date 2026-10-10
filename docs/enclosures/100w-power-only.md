# 100W-power-only

Path: [docs](../README.md) › [enclosures](README.md) › **100w-power-only**
Parent: [README.md](README.md)
**Code:** `enclosures/100W-power-only/enclosure.yaml`, `components/passthrough/xt60-f.yaml`
**Covers:** the S-100-5 box with no electronics, just the inlet and two XT60 outputs: layout
decisions and what the owner should still check.

## What it does

Interior 242 × 168 × 55 mm; base prints at 246.8 × 200.8 × 58, lid at 250.8 × 184.8 × 9.4
(separate plates). Front to back: the C14 lying down in the front wall toward the right, the
S-100-5 running along the length with its terminals facing the right wall (40 mm of terminal
space), 10 mm of air to the back wall. Two XT60 female pigtails leave through slots in the right
wall straight in front of the DC terminals; their bare leads go into the PSU's −V/+V screws.
Slide-lock lid with the zip-tie lock on the back wall; four mounting tabs on the long walls.

## Decisions

- **Outputs are XT60 female pigtails through wall slots, 10 cm leads** (owner, 2026-10-10:
  "pigtails out a slot", rather than a flanged panel-mount XT60). The owner does not want to
  solder extension wires onto them, so the exits must be close enough to the DC terminals for
  the leads to reach. Female on the supply side, because its contacts are shrouded and a live
  output is never exposed.
- **Layout is the 20W's ([20w.md](20w.md)), turned 90° so the PSU runs along x: terminals to
  the right, inlet in the front wall.** Facing the terminals from the right, AC (L, N, FG) is on
  the left (front), toward the inlet, and DC on the right (back), so the inlet's wires and the
  XT60 leads meet the block from opposite ends of it.
  **Rejected:** the 100W arrangement (inlet in a long wall behind the terminal end) — the
  inlet's 60 mm of body and wires then has to sit beyond the PSU's side, making the box over
  158 wide (98 + 60) *and* ~240 long. The upright inlet (rotate 0) beside the terminal space —
  its 35 mm body may not enter the terminal space, so the PSU still starts 35 in, and the box
  grows to 66 tall: 143 × 244 × 66 against 168 × 242 × 55, no smaller, taller, and unlike the
  other 100W boxes.
- **Turned so the inlet shares a wall with the lid-lock slots** (owner, 2026-10-10): the
  base needed supports on three sides. The build flags only the inlet's flat-topped cutout;
  the other two are taken to be the walls carrying the lid-lock slots (the lid slides along x,
  so they are always the front and back) — an inference from "three sides" and the fix the
  owner asked for, not confirmed. With the inlet in the front wall only the
  front and back need supports. The lid slides along the PSU instead of across it, which is what
  the owner asked for as "rotate the lid"; the builder only slides lids along x, so the layout
  was turned instead.
  **Changed 2026-10-10:** was 168 × 242 with the terminals to the front and the inlet in the
  left wall.
- **XT60 slots at u = 118 and 142, z = 12, in the right wall**: in front of the DC terminals,
  which are estimated at y ≈ 109–138 (S-100F block of 7, ~9.5 mm pitch, centred on the PSU at
  y 60–158; FG ≈ 99.5). Each XT60 takes one −V and one +V terminal (the PSU has two of each), so
  each terminal carries one output's current. Low, so the leads run along the floor through
  their zip-tie anchors (12 mm in) and then rise to the screws.
  **Lead budget:** ~2.4 wall + ~15 to the anchor + ~56 up to a screw (x ≈ 195, z ≈ 46) + ~7
  stripped end ≈ 80–85 mm of the 100, with the connector body against the outside of the wall.
- **Terminal space 40 mm, the library value.** The lid (242 + 4.8 + 4 finger pull = 250.8)
  still fits the 254 mm usable bed with 40, so nothing forces it smaller; 40 also covers the
  inlet's body (x 182–230) reaching past the terminal end.
- **PSU at y = 60** = inlet body (35) + its wire zone (25), as in 20W. **10 mm air gap to the
  back wall, 3 mm behind the far end** (left wall): the back gap feeds the back-wall vents along
  the PSU's DC side; the far end is closed sheet metal.
- **Zip-tie lock on the back wall at u = 70, between the left and middle lid tongues** (at
  u = 121 it hit the middle tongue). **Tabs on the front/back walls (front u = 22, 142; back
  u = 22, 212)**. On the left or right walls either would add 12 mm to the 246.8 mm length and
  push base or lid past the bed. The front tab at 142 clears the inlet flange (u 171.5–240.5).
- **The front-right lid tongue sits at u = 165, not 232** (auto-shifted): the lying inlet's
  flange reaches up into the lock zone, as in 100W.
- **Vents in both long walls** (back u 4–200, front u 4–166, z 6–38) plus lid slots over the
  PSU. The front wall's free strip (y 0–60 beside the inlet) gives the AC side an intake too.
  Neither short wall: the right holds the terminal wiring and the XT60s, the left is 3 mm from
  the PSU's closed end.
- **No perfboard** (owner, 2026-10-10: "power only") — the root "every box holds a perfboard"
  requirement is the owner's default, not a rule for this box ([../README.md](../README.md)).

## Still to check (from datasheets, not measured)

- S-100-5 bottom holes — as in [100w.md](100w.md).
- The XT60 on the pigtail (with its heat-shrink, or an XT60H snap-on sheath) passes the
  16.5 × 9.1 mm slot: print `test-prints/xt60-f-coupon.stl` (the slot is sized from the bare
  XT60-F drawing; the XT60H sheath is not documented).
- The leads are ~10 cm from the back of the connector to the bare end and fit the PSU's
  terminal screws (12 AWG is common on XT60 pigtails).

## Gotchas

- Feed the bare lead ends in from outside through the slots, then zip-tie each pair to its
  anchor before screwing them down: a tug on the XT60 must land on the anchor, not on the
  terminal screws.
- The validator does not apply the mains/low-voltage side rule to wire exits (only to panel
  parts and perfboards); the XT60s are on the DC side by this layout, not by a check.
- Each XT60 is rated 30 A; the PSU gives 20 A in total.

## Related

- [20w.md](20w.md) — the same layout with the S-20-5; inlet position and nut-height reasoning.
- [../enclosure/wall_openings.md](../enclosure/wall_openings.md) — the XT60 slot size and why.
- [../enclosure/psu_mount.md](../enclosure/psu_mount.md) — terminal order and the PSU's local frame.
