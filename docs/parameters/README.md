# Parameters

Path: [docs](../README.md) › **parameters**
Parent: [../README.md](../README.md)

**Covers:** the YAML inputs and how they combine into one parameter tree per enclosure; the
coordinate frame every other part uses.
**Code:** `config/defaults.yaml`, `components/`, `enclosures/*/enclosure.yaml`, `enclosure_builder/config.py`

## Design

### Decisions

- **Layers, merged in order: `config/defaults.yaml` ← the enclosure it `extends:` (if any) ←
  `enclosures/<name>/enclosure.yaml` ← per-instance `override:`.** `extends` exists because the
  owner needs the same enclosure with and without an RJ45; a variant states only its
  differences, so a layout fix in the base enclosure reaches both. Defaults hold the house
  style (wall thickness, M3 dimensions, lid design) so an enclosure file only states what is
  specific to it. Mappings merge key by key;
  lists replace wholesale, because merging lists element-wise (e.g. hole lists) would silently mix
  two parts' geometry.
- **Parts are referenced by name from a component library** (`components/<kind>/<part>.yaml`)
  rather than dimensioned inline. A measured part is measured once and reused by every enclosure;
  an enclosure can still correct one value through `override:` without forking the file.
  See [component_library.md](component_library.md).
- **`psu:` is mandatory.** The owner requires every enclosure to house a power supply; making it
  required catches a forgotten PSU at load time instead of producing an empty box.
- **The enclosure's `name:` must equal its directory name**, so a copied directory with a stale
  name fails loudly instead of overwriting another enclosure's outputs.

### Coordinate frame

Interior corner at the origin. `x` runs along the length (left wall → right wall), `y` across
(front wall → back wall), `z` up, with `z = 0` the top surface of the floor. Walls, floor
and tabs lie outside the interior box `[0,L] × [0,W] × [0,H]`.

Wall features are placed with `(wall, u, z)`: `wall` ∈ front/back/left/right, `u` measured along
the wall from its end with the smaller `x` (front/back) or smaller `y` (left/right).

**Why.** Interior coordinates are what a person measures from ("PSU 4 mm off the front wall"), and
they stay valid when wall thickness changes. `u` follows the global axes rather than "left to right
as seen from outside" so that one number means the same position on the inside and outside faces
and no wall needs a mirrored convention.
**Constrains.** Seen from outside, `u` grows to the left on the back and left walls. Documented in
every `enclosure.yaml` header so nobody "fixes" it.

## Contents

### Pages

- [`defaults.md`](defaults.md) — the house-style values in `config/defaults.yaml` and why each was chosen.
- [`component_library.md`](component_library.md) — the `components/` directory: kinds, schema, `verified` flag.
- [`enclosure_definition.md`](enclosure_definition.md) — the schema of `enclosures/<name>/enclosure.yaml`.

## Related

- [../pipeline/README.md](../pipeline/README.md) — consumes the merged tree.
- [../enclosure/README.md](../enclosure/README.md) — what each parameter turns into.
