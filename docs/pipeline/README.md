# Pipeline

Path: [docs](../README.md) › **pipeline**
Parent: [../README.md](../README.md)

**Covers:** `build.py` — from a merged parameter tree to STLs, previews and a BOM.
**Code:** `build.py`, `enclosure_builder/`

## Design

Flow per enclosure: `config.load_enclosure` → `layout.build_model` → `validate.validate` →
`emit.write_scad` + `emit.write_bom` → `render.render_stl` / `render_png`.

### Decisions

- **Validation runs before anything is written.** A layout error must never leave STLs on disk
  that look current; the previous good outputs stay until the layout is fixed.
- **`--check` writes SCAD and BOM but no STLs** — a fast loop (well under a second) for an agent
  iterating on positions; STL + previews take ~10 s.
- **Generated files are kept in the repository next to `enclosure.yaml`**, not git-ignored
  (`build/*.scad`, `stl/`, `preview/`, `BOM.md`). The owner asked for the STLs to live in the
  enclosure's directory, and the previews and BOM let a reader review an enclosure without
  installing OpenSCAD. Every generated text file says GENERATED in its header.
- **Python dependencies are only PyYAML**, installed in `.venv` (`pip install -r
  requirements.txt`). OpenSCAD is an external program found on `PATH` or in `/Applications`.

## Contents

### Pages

- [`layout_model.md`](layout_model.md) — `layout.py`: the Model, primitives, keep-outs, wall footprints, bolt-length picking.
- [`validation.md`](validation.md) — `validate.py`: what is checked and why.
- [`output.md`](output.md) — `emit.py`, `render.py`, `cli.py`: generated SCAD, BOM, STL and PNG rendering.

## Related

- [../parameters/README.md](../parameters/README.md) — the inputs.
- [../enclosure/README.md](../enclosure/README.md) — what each placement function produces.
