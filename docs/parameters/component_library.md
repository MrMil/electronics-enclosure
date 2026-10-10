# Component library

Path: [docs](../README.md) › [parameters](README.md) › **component_library**
Parent: [README.md](README.md)
**Code:** `components/psu/`, `components/perfboard/`, `components/panel/`, `enclosure_builder/config.py`
**Covers:** how reusable part descriptions are stored and loaded. What each kind's fields mean is
on the feature page that consumes it.

## What it does

`components/<kind>/<part>.yaml` describes one physical part in its own local frame. An enclosure
names it with `part: <part>`; `config.load_component` loads it, checks `kind:` matches the
directory, and merges the instance's `override:` mapping over it.

Kinds and their consumers:

| kind | consumer page |
|---|---|
| `psu` | [../enclosure/psu_mount.md](../enclosure/psu_mount.md) |
| `perfboard` | [../enclosure/perfboard_mount.md](../enclosure/perfboard_mount.md) |
| `panel` (C14 inlet, RJ45, anything clamped in a wall cutout) | [../enclosure/wall_openings.md](../enclosure/wall_openings.md) |
| `passthrough` (connector-sized wall slots and floor holes with their drill size, e.g. JST SM, XT60 pigtails) | [../enclosure/wall_openings.md](../enclosure/wall_openings.md) |

## Decisions

- **Parts are described in their own frame (e.g. PSU holes measured from its terminal end),
  never in enclosure coordinates.** That is how a datasheet or a caliper reports them, and it
  lets the same file be placed, mirrored or rotated in any enclosure.
- **`kind:` is checked against the directory.** A PSU file accidentally put in `panel/` would
  otherwise be read with the wrong schema and produce plausible but wrong geometry.
- **`verified: true | datasheet | false` on every component.** `true`: measured on the real part
  (record date and what was measured in comments). `datasheet`: from the manufacturer's
  documentation for this exact part; `check:` names the one measurement that confirms it, and it
  is listed once per part under "Check before printing" in the BOM. `false`: guessed (photo,
  similar part); a build warning. See the root decision in [../README.md](../README.md).
- **`source:` records where unmeasured numbers came from**, so a later agent can tell a
  datasheet value from a guess.
- **Panel parts are one generic kind (cutout + optional M3 bolts + flange + inside keep-out)**
  rather than a kind per connector. C14 modules, RJ45 couplers, switches, DC jacks and glands all
  reduce to that shape, so new connectors need a YAML file, not code.

## Gotchas

- `override:` replaces lists wholesale: overriding one PSU hole means restating all four.

## Related

- [enclosure_definition.md](enclosure_definition.md) — how enclosures reference parts.
- [../enclosures/100w.md](../enclosures/100w.md) — which library parts are still unmeasured.
