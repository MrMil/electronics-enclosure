# Enclosures

Path: [docs](../README.md) › **enclosures**
Parent: [../README.md](../README.md)

**Covers:** the concrete, named enclosures in `enclosures/`, the layout decisions specific to
each, and which of their parts are still unmeasured.
**Code:** `enclosures/*/enclosure.yaml`

## Design

### Decisions

- **One page per enclosure, named after it.** Layout choices (which wall the inlet is on, where
  mains and low voltage are separated) belong to one enclosure and must not leak into the feature
  pages, which apply to all of them.
- **LED exits go in a wall unless the owner asks for the floor** (owner, 2026-10-08). Floor
  exits need the mounting board drilled, so they are the owner's call per enclosure: `20W` and
  `100W-leds-on-floor` have them; `100W`, `100W-rj45` and `100W-masterbox` keep theirs in the
  back wall.
  **Changed 2026-10-08:** previously "100W boxes never use the floor", from the owner moving the
  masterbox's exits back into a wall; the owner then asked for a 100W variant with floor exits.
- **Variants of one layout share a page and use `extends`** (`100W-rj45` and
  `100W-leds-on-floor` extend `100W`), so their layout reasoning is written once.
- **Enclosure names are the owner's**, after the PSU's power (`100W`), with a `-<variant>`
  suffix for variants (`100W-rj45`). A new revision with incompatible hole positions gets a new
  name rather than silently replacing STLs someone may already have printed.
  **Changed 2026-10-08:** previously agent-chosen descriptive names (`led-controller-1`).

## Contents

### Pages

- [`20w.md`](20w.md) — `20W`: S-20-5 PSU facing the front, inlet left, perfboard beside it, two round JST-SM LED holes in the floor.
- [`100w-masterbox.md`](100w-masterbox.md) — `100W-masterbox`: bed-filling S-100-5 box, ESP32 board + MAX485 board with side clearance, three RJ45s, four back-wall LED exits.
- [`100w.md`](100w.md) — `100W`, `100W-rj45` and `100W-leds-on-floor`: S-100-5 PSU, DIKAVS perfboard, C14 inlet, four JST-SM LED exits (back wall, or floor), optional RJ45.

## Related

- [../parameters/enclosure_definition.md](../parameters/enclosure_definition.md) — how to write a new one.
