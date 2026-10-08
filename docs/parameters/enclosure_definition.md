# Enclosure definition

Path: [docs](../README.md) › [parameters](README.md) › **enclosure_definition**
Parent: [README.md](README.md)
**Code:** `enclosures/<name>/enclosure.yaml`, `enclosure_builder/config.py`
**Covers:** the schema an agent writes to create a new enclosure. Example:
`enclosures/100W/enclosure.yaml`.

## What it does

| key | meaning |
|---|---|
| `name` | must equal the directory name |
| `extends` | optional: another enclosure whose YAML is merged underneath this one |
| `box.inner` | `[L, W, H]` interior size |
| `psu` | `part`, `at: [x, y]` (footprint corner with smallest x, y), `terminals: left\|right\|front\|back` (the wall the terminal end faces), optional `lv_route: far_end` (left/right only), `lv_gap` |
| `perfboards[]` | `part`, `at: [x, y]` (board corner with smallest x, y), `rotate: 0\|90`, optional `min_standoff`, `clearance: {left\|right\|front\|back: mm}` |
| `panel_parts[]` | `part`, `wall`, `u`, `z` (cutout centre), `rotate: 0\|90` |
| `wire_holes[]` | `wall`, `u`, `z` and either `d` (round) or `part` (from `components/passthrough/`); `wall: floor` takes `at: [x, y]`, `rotate` (slot direction; for a round hole, only where the default anchor goes), optional `anchor_at: [dx, dy]`; optional `tie_anchor`, `inside_depth` |
| `vents` | `lid_over_psu: bool`, `walls[]`: `{wall, u: [from, to], z: [from, to]}` regions |
| `mounting` | `style: tabs\|floor`, `screw_d`, `head_d`, `tabs[]: {wall, u}` or `floor_holes[]: [x, y]` |
| `lid.tab_u` | where the lid's detent tab sits on the left wall (keep it clear of left-wall parts) |
| `lid.lock_lug` | `{wall: front\|back, u}` adds the zip-tie lock lugs |
| `lid.tongues` | `auto`, a list of u, or `{front: [...], back: [...]}` |
| `printer.bed` | override if this enclosure is printed elsewhere |
| `printer.support_margin` | bed room (mm) outside each wall whose holes need supports |

Any key from `config/defaults.yaml` may also be overridden here.

## Decisions

- **The interior size is stated, not computed from the parts.** Auto-sizing would need an
  auto-layout engine whose choices (where the inlet goes, which side the perfboard sits) are
  exactly the decisions the owner wants to make. Instead the agent places parts explicitly and
  the [validator](../pipeline/validation.md) rejects anything that collides or does not fit.
- **Positions are corners for boxes (`at`) and centres for wall features (`u`, `z`).** A box is
  measured from a wall to its edge; a hole is measured to its centre. Matching how one measures
  avoids off-by-half-width errors.
- **`terminals:` instead of a free rotation for the PSU.** The PSU is only ever laid flat along
  the box length; the only real choice is which end faces the inlet. A free angle would invite
  layouts the validator cannot check with axis-aligned boxes.
- **Round wire holes are inline; connector slots come from the library.** A round hole is just
  a diameter, but a connector slot carries a datasheet-derived size worth citing once.
- **A variant `extends` its base and restates only lists it changes** (lists replace
  wholesale — see [README.md](README.md)).

## Creating a new enclosure

1. Ask the owner which PSU, perfboard(s) and panel parts. For any part without a library file,
   find the manufacturer's drawing first and ask the owner only to verify it or for what is not
   documented (root decision in [../README.md](../README.md)). Every part needs its wiring space
   (`cable`, `terminal_clearance`, `inside_depth`).
2. Copy an existing `enclosure.yaml` into `enclosures/<new-name>/` (or `extends:` it), set
   `name`, place parts. Put the inlet beside the PSU's terminal end and connectors' cable zones
   where their cables can reach the board they serve.
3. `python build.py <new-name>`; fix every ERROR; look at `preview/*.png`.
4. Add the enclosure to [../enclosures/README.md](../enclosures/README.md) with a page recording
   its layout decisions.

## Related

- [component_library.md](component_library.md) — the files `part:` refers to.
- [../pipeline/validation.md](../pipeline/validation.md) — what the build checks about this file.
