# Documentation Hub

**Audience: LLM coding agents working in this repository. Not human onboarding material.**
Optimise for a reader with no memory of previous sessions, who can read files fast, and who needs
to know *why* the code is the way it is before changing it.

This tree mirrors the system as a recursive hub-and-spoke: every directory is a part of the system,
its `README.md` indexes what is inside it, and the nesting goes as deep as the system does. Each
page explains its piece and records the reason behind every choice made there. The code is the
source of truth for what happens. These docs are the source of truth for why.

## How to use this tree

1. Start here and navigate down, one index at a time, to the page covering what you are about to change. Never guess paths.
2. **Read every `README.md` on the way down.** Decisions recorded at a level apply to everything beneath it. The reason a leaf behaves as it does may be recorded two levels up.
3. Before finishing work, run the documentation pass in [CONVENTIONS.md](CONVENTIONS.md#the-documentation-pass).

## Design

The system turns measurements of specific hardware into printable enclosures. Each enclosure is a
named directory under `enclosures/` holding its `enclosure.yaml` and the generated STLs. Every
enclosure houses a power supply.

### Decisions

- **The owner's requirements are the root constraints.** Every
  enclosure: houses a PSU and keeps it ventilated; holds a perfboard by its holes (2 for the first
  board, 4 for most); has a C13-cord inlet (a C14 module) in a side wall; has wire exits for LED
  strips (a power-only box, with the PSU's outputs on connectors instead of a board, is the owner's
  call per enclosure: `100W-power-only`, 2026-10-10); may have an RJ45 bulkhead; has a lid that cannot come undone but opens repeatedly
  without tools, bolts or nuts (hardware is fine for assembly, not for opening); leaves room for
  the wires and cables every part has; has parametric holes for fixing it in place; prints with minimal supports; uses as few non-printed
  parts as possible, one bolt size, and no threaded inserts — bolts through printed walls into
  nuts are preferred. Agents must not trade any of these away without asking the owner.
- **One bolt size: M3 socket head everywhere.** The owner asked for a single small bolt size and
  the S-100-5 PSU's own mounting holes are M3, so M3 is the size that needs no adapter. The only
  non-M3 fasteners are the screws that fix the enclosure to its surface (owner's choice, a
  parameter) and the RJ45 coupler's own nut.
- **No threaded inserts, no tapping plastic.** Every M3 joint ends in a metal thread: the PSU's
  own threads, or a hex nut held in a printed pocket or slot. Owner preference; it also means
  threads never wear out with repeated opening.
- **Geometry adapts to standard bolt lengths, not the reverse.** Printed heights (PSU pads,
  standoffs, nut-slot depth) are computed from a chosen standard M3 length, because printed
  dimensions are free and bolt lengths are discrete. The BOM then lists only lengths you can buy.
- **Everything prints without supports**, by fixed print orientation (base floor-down, lid
  top-down) plus the tricks in [enclosure/printability.md](enclosure/printability.md). Owner
  requirement.
- **Find dimensions in manufacturer documentation first; the owner verifies.** The owner would
  rather check a few numbers than take many caliper measurements (and finds some, like flange
  overhangs, hard to measure). Component files record `source:` and `verified: true | datasheet |
  false`. `datasheet` values are listed in the BOM under "Check before printing" with the one
  measurement that confirms them; `false` (guessed) values are build warnings. A guessed number
  can therefore never silently become "known".
- **Units are millimetres; one coordinate frame everywhere** — defined in
  [parameters/README.md](parameters/README.md).
- **Print in PETG or ASA, not PLA.** The PSU case runs warm at full load, and PLA creeps under the
  bolted PSU pads over time. Recorded in every generated BOM.

### YAML → Python → OpenSCAD

**Why.** The person (or agent) creating an enclosure writes measurements; YAML is the easiest
format to write and diff. Layout logic (deriving heights from bolt lengths, generating vents that
avoid other features, checking collisions, writing a BOM) is awkward in OpenSCAD's language and
easy in Python. OpenSCAD is the standard tool in 3D printing for parametric solids, and the
generated `.scad` files can be opened in its GUI for inspection.
**Rejected.** CadQuery: no wheels for the Python in use (3.14) and a heavy OCC dependency. Pure
OpenSCAD with the Customizer: no validation, no BOM, and parameters would live in a format nobody
else reads.
**Constrains.** The SCAD library is geometry-only and knows nothing about specific components;
all component knowledge lives in Python and the component YAML files. Requires an OpenSCAD
snapshot with the manifold backend (2021.01 stable is far too slow for the vent patterns).

## Areas

- [`parameters/`](parameters/README.md) — the YAML inputs: defaults, component library, enclosure definitions, coordinate frame.
- [`enclosure/`](enclosure/README.md) — the printed object: shell, lid closure, PSU and perfboard mounts, wall openings, ventilation, mounting, printability.
- [`pipeline/`](pipeline/README.md) — `build.py`: layout model, validation, SCAD/BOM output and rendering.
- [`enclosures/`](enclosures/README.md) — the concrete, named enclosures and what is still unmeasured in each.

## Files

- [CONVENTIONS.md](CONVENTIONS.md) — the rules for writing and maintaining these docs. Read before adding anything here.

## Invariants

These hold at every depth. If you find one broken, fix it before continuing your task.

- Every directory under `docs/` contains a `README.md` listing every subdirectory and every `.md` file beside it, each with a one-line description.
- Every page and every index links to its parent, carries its breadcrumb path, and links to at least one related page.
- No statement of a design choice appears anywhere in this tree without its reason.
- Every decision is recorded at the lowest level that contains everything it governs.
- No code change ships without the corresponding documentation change in the same commit.
