# Lid closure

Path: [docs](../README.md) › [enclosure](README.md) › **lid_closure**
Parent: [README.md](README.md)
**Code:** `scad/enclosure.scad` (`lid`, `lid_plate2d`, `lid_lip`, `lid_tooth`, `lock_cutters`), `enclosure_builder/layout.py` (`place_lid_lock`), `config/defaults.yaml` (`lid:`)
**Covers:** how the lid locates, locks and comes off.

## What it does

Drop-and-slide, no hardware. The lid is lowered onto the box `lid.slide` (10 mm) toward the left
wall from its closed position, then slid right:

- **Tongues** on the lid lip (ends + middle of both long walls) drop through open-top notches in
  the walls, then slide under a 3 mm ledge left above a slot in each wall. They hold the lid down.
- A **flexible tab** cut into the lid plate at the left wall carries a **tooth** underneath. While
  sliding, the tooth rides over the left wall's top on a 45° ramp, then drops inside it; its
  vertical face then stops the lid sliding back. The tab's tip sticks out 4 mm past the wall as a
  finger pull.
- To open: lift the pull with a fingertip (~2.5 mm), slide the lid left, lift it off.

## Decisions

### Drop-and-slide with a detent tab

**Why.** Owner requirement (2026-10-07): the lid must not come undone, must open repeatedly, and
must open without bolts and nuts. The tongues give positive hold against lifting across the whole
length; the only flexing part is the tab, which bends ~1 % (PETG tolerates this indefinitely), and
it only flexes while opening or closing. A 10 mm slide needs no free space around the installed
box, unlike a full-length sliding lid.
**Rejected.** Snap hooks on the lip pressed through wall windows: needs several hooks squeezed at
once, and the hooks' retaining faces would be horizontal overhangs when printed. Full sliding
dovetail lid: needs a lid-length of free space beside the mounted box. Quarter-turn cam latches:
extra printed parts and an M3 axle per latch. Hinge + latch: hinge knuckles add overhangs and
still need a latch.
**Constrains.** The left lip segment stops `slide` short of the left wall, and has a gap under
the tab. Long-wall features must stay clear of the tongue notches/slots (they are wall features,
so the validator enforces it). Nothing may sit on the left wall's outside top where the tooth
travels (`lid lock tab` feature). The C14 flange in 100W is therefore not at the tab.

**Changed 2026-10-07:** previously M3 bolts through the lid into hex nuts side-loaded into bosses
outside the walls, because it was the most secure M3-only closure. Changed because the owner does
not want to undo bolts to reach the electronics; bolts are acceptable for assembly, not for
opening. The bosses are gone, which also shrank the footprint by 15 mm.

### Optional zip-tie lock (`lid.lock_lug`)

**Why.** Owner requirement (2026-10-07): the box will be at a festival (Midburn), and people who
are not thinking clearly must not be able to open the lid and reach 230 V. A lug on the lid plate
sits 0.4 mm above a lug on a long wall; their 5 mm holes line up only when the lid is closed. A
zip tie through both stops the lid sliding (so the tooth cannot be bypassed) and lifting. It
needs cutters to open, which is the point.
**Rejected.** A tie through the detent tab's finger pull: the pull would have to grow ~8 mm to
take a hole, and the lid is already within 1.2 mm of the A1 bed in length. A hole through wall
and lid lip: the tie could not be closed inside the box.
**Constrains.** The lugs may go on any wall: on a long wall they shear apart when the lid
slides, on a short wall they pull apart — the tie stops both. A short wall keeps the lid narrow
(used by 20W so base and lid share one plate). The wall lug's underside is 45° so it prints
without support; the lugs add `lug_reach` (12 mm) to base and lid, which the bed check includes.
**Changed 2026-10-08:** lugs were limited to the long walls; that was an unnecessary restriction.

### Tongue and ledge faces are parallel 45° slopes

**Why.** A flat ledge underside would be a horizontal overhang in the base, and a flat tongue top
would be one in the flipped lid. 45° faces print on both parts without supports. The hold is
still positive: to release by lifting, the lid's lip would have to bend inward 2 mm along its
length, which the lip corners and the closed lip ring prevent.
**Constrains.** `lid.lip_h` must leave the tongue tip ≥ 1 mm thick and the slot open at the
wall's outer face; `place_lid_lock` errors otherwise.

- **Tongues on the long walls only, at both ends and the middle (if > 150 mm).** The slide runs
  along the length, so only long walls can take slots; the middle tongue stops a 240 mm lid from
  bowing up between the ends.
- **In `auto` mode each tongue slides toward the middle until it clears that wall's other
  features**, and the build lists the move under "Check before printing". A flange reaching up
  into the lock zone (the rotated C14 in 100W moves the back-left tongue from 22 to
  88 mm) should not force the box taller. `lid.tongues` may also be a list, or a `{front, back}`
  map of lists, to place them by hand.
- **`slide` > tongue width + clearance** so the locked tongue is fully under the ledge, not half
  over the notch.
- **Tooth 2 mm tall, vertical face 0.4 mm from the wall's inner face.** 2 mm is enough that a knock
  cannot ride the lid back over it; lifting the tab 2.5 mm clears it.
- **Tab 30 mm long, 14 wide, slits end in round reliefs.** Length sets the bending strain (~1 %
  at 2.5 mm lift); the round ends stop cracks starting at the slit tips.
- **Lip 7 mm tall, 1.6 mm thick, 0.3 mm clearance.** Tall enough to carry the tongues; 0.3 mm
  covers PETG's error on a 240 mm part without visible play.

## Gotchas

- `lid.tab_u` must keep the tab clear of whatever is on the left wall; the validator reports a
  collision with `lid lock tab`.
- The lip zone (top `lip_h` of the interior) is reserved: through-cuts stay below
  `H − lip_h − margin`, keep-outs below `H − lip_h`.

## Related

- [printability.md](printability.md) — why every lock face is 45° or vertical.
- [ventilation.md](ventilation.md) — lid slots avoid the tab and the slide strip.
- [shell.md](shell.md) — the shared outline the lid plate is cut from.
