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
- **100W boxes put their LED exits in a side wall, never the floor** (owner, 2026-10-08). Floor
  exits are only for the 20W, where the owner asked for them and drills the mounting board.
- **Variants of one layout share a page and use `extends`** (`100W-rj45` extends
  `100W`), so their layout reasoning is written once.
- **Enclosure names are the owner's**, after the PSU's power (`100W`), with a `-<variant>`
  suffix for variants (`100W-rj45`). A new revision with incompatible hole positions gets a new
  name rather than silently replacing STLs someone may already have printed.
  **Changed 2026-10-08:** previously agent-chosen descriptive names (`led-controller-1`).

## Contents

### Pages

- [`20w.md`](20w.md) — `20W`: S-20-5 PSU facing the front, inlet left, perfboard beside it, two JST-SM LED exits.
- [`100w-masterbox.md`](100w-masterbox.md) — `100W-masterbox`: bed-filling S-100-5 box, ESP32 board + MAX485 board with side clearance, three RJ45s, four floor LED exits.
- [`100w.md`](100w.md) — `100W` and `100W-rj45`: S-100-5 PSU, DIKAVS perfboard, C14 inlet, four JST-SM LED exits, optional RJ45.

## Related

- [../parameters/enclosure_definition.md](../parameters/enclosure_definition.md) — how to write a new one.
