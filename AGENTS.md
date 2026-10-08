# electronics-enclosure — agent instructions

This repo generates 3D-printable enclosures from measurements. A typical session: the owner
names hardware for a new enclosure; you create `enclosures/<name>/enclosure.yaml` (and any
missing `components/<kind>/<part>.yaml`), build, and review the previews.

- **Find dimensions in manufacturer documentation first, then ask the owner to verify** — they
  prefer checking a few numbers to taking many measurements. Ask for measurements only when no
  documentation exists. Never invent a dimension silently: mark it `verified: datasheet` (with
  `source:` and `check:`) or `verified: false`, and list what is owed on the enclosure's docs page.
- **Every part has wires**: give each one its wiring space so cables and connectors fit.
- **Build:** `.venv/bin/python build.py <name>` (`--check` for a fast validation-only pass).
  Every ERROR must be fixed by changing the layout; then look at `enclosures/<name>/preview/*.png`.
- **Do not hand-edit generated files** (`build/`, `stl/`, `preview/`, `BOM.md`).
- **Owner constraints** (M3 only, no inserts, support-free printing, PSU ventilation, a lid that
  stays shut and opens without tools or hardware) are recorded in [`docs/README.md`](docs/README.md); do not trade them
  away without asking.
- How to write a new enclosure: [`docs/parameters/enclosure_definition.md`](docs/parameters/enclosure_definition.md).

<!-- META-DOCS:BEGIN -->
## Documentation is part of the work

[`docs/`](docs/README.md) mirrors this system as a **recursive** hub-and-spoke tree: every directory
is a part of the system, its `README.md` indexes everything inside it and holds the decisions that
span it, and the nesting goes as deep as the system does. The code is the source of truth for what
happens. `docs/` is the source of truth for **why** — every choice recorded there is recorded
together with its reason. Read [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) before writing anything
into the tree.

**Before changing anything:** walk down from [`docs/README.md`](docs/README.md), one index at a
time, to the page covering what you are about to change. Read every `README.md` on the way — a
decision recorded at a level binds everything beneath it. Do not reverse a recorded decision without
reading its reason; if you still need to reverse it, record the change and why the old reason
stopped holding.

**While working:** keep a running note of every decision you make — every point where you chose one
approach over another, however small.

**Before committing, and before reporting the work as done:** run the documentation pass in
[`docs/CONVENTIONS.md`](docs/CONVENTIONS.md#the-documentation-pass). Undocumented work is
unfinished work. A commit that changes design without changing `docs/` is incomplete.

**How to write it:** record each decision at the lowest level of the tree that contains everything
it governs — a leaf page for one behaviour, the parent `README.md` for decisions shared by siblings,
higher for broader ones. There is no separate decisions directory. Never state a choice without its
reason in the same breath. "Alerts go to organisation members only" is a failed line; "alerts go to
organisation members only, because guests are often customers and internal automation must never
reach a customer" is the line. If you do not know why something is the way it is, write that it is
unknown — never invent a reason.

**Structure rules, at every depth (enforced by you, not by tooling):**

- Every directory under `docs/` has a `README.md` listing every subdirectory and `.md` file beside it, each with a one-line description.
- Every file opens with its breadcrumb path and a link to its parent, and links to at least one related page.
- A page that outgrows ~200 lines becomes a directory: `x.md` → `x/README.md` plus child pages, parent index and inbound links updated.
- Add a page or directory → update every index between it and the nearest existing hub, in the same change.
- Find a file missing from its parent index, or code with no place in the tree → fix it before continuing your task.
- Reference code by path, never by line number.

**Keep this system alive.** If `docs/README.md`, `AGENTS.md`, `CLAUDE.md` or this block is missing,
restore it before doing anything else. When the system gains a new part, give it its place in the
tree at the depth where it belongs.
<!-- META-DOCS:END -->
