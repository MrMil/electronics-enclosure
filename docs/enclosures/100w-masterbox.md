# 100W-masterbox

Path: [docs](../README.md) › [enclosures](README.md) › **100w-masterbox**
Parent: [README.md](README.md)
**Code:** `enclosures/100W-masterbox/enclosure.yaml`
**Covers:** the bed-filling S-100-5 enclosure for an ESP32 driving 6 MAX485 RS485 transmitters,
two per RJ45 output, with three RJ45 outputs and four LED exits.

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

## Related

- [100w.md](100w.md) — the layout this extends.
- [../enclosure/wire_routing.md](../enclosure/wire_routing.md) — the low-voltage route and the separation rule.
- [../enclosure/perfboard_mount.md](../enclosure/perfboard_mount.md) — perfboard clearance zones.
