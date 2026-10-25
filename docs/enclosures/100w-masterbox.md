# 100W-masterbox and masterbox-4-perfboards

Path: [docs](../README.md) › [enclosures](README.md) › **100w-masterbox**
Parent: [README.md](README.md)
**Code:** `enclosures/100W-masterbox/enclosure.yaml`, `enclosures/masterbox-4-perfboards/enclosure.yaml`
**Covers:** the bed-filling S-100-5 enclosure for an ESP32 driving 6 MAX485 RS485 transmitters,
two per RJ45 output, with three RJ45 outputs and four LED exits; and its variant
`masterbox-4-perfboards` (four boards, 7 MAX485s), [below](#masterbox-4-perfboards).

## What it does

Interior 244 × 232 × 55 mm; base prints at 248.8 × 248.8 × 58 (+5 mm of support room outside
the left and back walls), lid at 252.8 × 248.8 × 9.4. The S-100-5 runs along the front with its
terminals to the left; low-voltage wires go through printed loops in a 10 mm front channel and
round the PSU's right end, as in [100w.md](100w.md). Behind the PSU:

- **C14** lying down in the left wall, directly behind the PSU's L/N/FG terminals.
- **MAX485 board** (6 modules), long side along the box, 30 mm free on both long sides for the
  modules that overhang them. Two RJ45s in the back wall inside its rear strip.
- **ESP32 board** beside it, 30 mm free behind its long side for the USB-C debug cable; the third
  RJ45 in the back wall behind that.
- **Four JST-SM LED exits** in the back wall left of the RJ45s, behind the C14.

Slide-lock lid, zip-tie lug on the front wall, four countersunk floor screws.

## Decisions

- **What the boards hold sets their clearance** (owner, 2026-10-08): the MAX485 modules are long
  and overhang both long sides of their board — 3 cm each side is enough; the ESP32 needs room on
  one long side for a USB-C cable. Each RJ45 carries the RS485 outputs of two MAX485s (two data
  pairs and a ground pair), so the RJ45s sit at the MAX485 board's rear strip.
  **Changed 2026-10-08:** earlier versions used two identical boards with 5/3 cm long-side
  clearance, then 4 cm of USB-C room at the short ends; neither matched what is on the boards.
  **Changed 2026-10-09:** the board holds 6 MAX485 modules, two per RJ45 (owner correction;
  earlier pages said 8). The board, its 3 cm strips and the three RJ45s are unchanged — the
  module count never set any dimension.
- **C14 in the left wall right behind the AC terminals, not in the back wall.** Its wires run
  ~10 mm to the terminals, so the mains region is the left-front corner only; the floor behind it
  (x 0–80, y 179–232) is usable; the LED exits' wiring room is there. With the C14 in the back wall the whole
  left column in front of it was mains wiring path — the "huge gap in front of the C13".
- **Boards side by side, both long side along x:** 81 + 81 mm fills the 163 mm between the mains
  separation (x 81) and the right wall; the MAX485 board's 30 + 55 + 30 mm fits the back band's
  121 mm depth.
- **LED exits in the back wall at u = 15–66, z = 17**: the owner wants this box's LED exits in a
  wall, not the floor (see [README.md](README.md)); this stretch is ~50 mm from the mains wiring and left of the RJ45s.
  **Changed 2026-10-08:** briefly in the floor; the owner wants them in the walls.
- **RJ45s behind the MAX485 board get 36 mm of cable room** (library 60): enough for the plug and
  boot, then the cable turns along the 30 mm clearance strip. The one behind the ESP32 keeps 60.
- **Support room 5 mm outside the left (C14) and back (RJ45) walls.** The right wall has only
  pointed vents.
- **Zip-tie lug on the front wall at u = 70**; on a short wall it would push the length past the bed.
- **Length 244 = 35 terminal space (library 40) + 199 PSU + 10 loop channel**, set by the lid
  (+4 finger pull). **Width 232**, set by the base (+12 lug, +5 support room).
- **Floor screws:** tabs would push the base past the bed on either axis.

## Gotchas

- Bed fit: 0.2 mm spare on the base, 1.2 mm on the lid (inside the 2 mm bed margin). Any growth
  needs a shorter `lid.tab_pull`, less support room, or a bigger printer.
- Base and lid do not fit one plate; print them separately.
- Four JST-SM exits carry at most 12 A (3 A per contact) of the PSU's 20 A.

## masterbox-4-perfboards

`extends: 100W-masterbox`: the same box, PSU, C14, LED exits, vents and lid. Four DIKAVS boards
carry 7 MAX485 modules and the ESP32, as two pairs side by side behind the PSU: each pair is two
boards long side to long side, 1.68 mm apart, at x 80–161 and 162–243, y 109–220.68. The ESP32 is
on the left pair's front board. The three RJ45s sit at u 158 / 192 / 226, z 25, over the back
boards' rear strip.

### Decisions

- **Four boards in two pairs, 1.68 mm apart long side to long side** (owner, 2026-10-25, with a
  photo of the boards laid out in a printed 100W-masterbox). The MAX485 modules straddle the gap
  between a pair's boards. 1.68 mm is the gap that continues the boards' 2.54 mm hole pitch
  across from one board to the other (owner), so a module's header pins land in holes on both.
  Do not round it: any other gap puts one row of pins off-grid. Because the modules sit on the pair, **no clearance strips**: nothing overhangs a
  pair's outer edges. The ESP32 needs **no room for its USB-C cable** inside (owner).
- **A new enclosure, not a change to 100W-masterbox** (owner named it): its board, RJ45 and floor
  screw positions are incompatible with the printed 100W-masterbox. The name breaks the
  `100W-<variant>` pattern because the owner chose it.
- **Pairs side by side, not three in a row plus one.** The low-voltage area behind the PSU is
  about 164 × 121 mm: x from 80 (20 mm `lv_gap` from the C14's wire zone) to the right wall, y
  from the PSU to the back wall. Three boards in a row need 168.4 mm, more than either direction,
  at any box height. Two pairs (162 × 111.68) are the only arrangement that fits.
- **55 mm height kept; the RJ45s reach over the boards instead.** A 76 mm tall box with the RJ45s
  above the boards passed validation, but the owner declined it (2026-10-25). At 55 mm the
  couplers stand over the back boards' rear strip. z 25 lifts the 30 mm body box (the 29 mm nut)
  to 0.5 mm above the board top (z 9.5); the 36 mm cable room (plug and boot) lies over the
  boards' components. The validator allows this only for low-voltage connectors, and never into
  the board itself ([perfboard_mount.md](../enclosure/perfboard_mount.md)).
- **RJ45s pushed toward the right wall, at a 34 mm pitch** (owner: keep the left pair's back-left
  corner usable). Rightmost u 226 keeps the body 3 mm from the right wall. The 34 mm pitch leaves
  4 mm between the 30 mm flanges, enough to turn each nut by hand. The leftmost coupler covers x
  143–173, leaving x 80–143 of the left pair's back board free. All flanges are clear of
  the back face's centreline (x 122), so the box still fits the shelf-tower window.
- **Three RJ45s for 7 MAX485s** (owner): one RJ45 carries three. Which modules go to which RJ45
  sets no dimension.
- **1 mm gaps** between the PSU and the front boards, between the pairs, and to the right wall:
  the band is 164 mm for 162 mm of boards. Pushing the front boards forward to y 109 (the parent
  used 111) leaves 11.3 mm behind the back boards for a floor screw.
- **Back-right floor screw moved from (232, 222) to (110, 227.2).** The old spot is under a board.
  No spot right of the RJ45s is reachable with a screwdriver, and the PSU and boards fill the
  rest of the right half. So it sits behind the back boards, left of the couplers, with the
  minimum margins (to the board edge 2 mm; the 9 mm countersink ends 0.3 mm from the wall).

### Gotchas

- The boards fill their band to the millimetre; any board-position change has to move the
  RJ45s or the floor screw too.
- Low-voltage wires from the far-end route reach the right pair's front edge directly (no free
  strip); they run over the boards' components space.

## Related

- [100w.md](100w.md) — the layout this extends.
- [../enclosure/wire_routing.md](../enclosure/wire_routing.md) — the low-voltage route and the separation rule.
- [../enclosure/perfboard_mount.md](../enclosure/perfboard_mount.md) — perfboard clearance zones.
