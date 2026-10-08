# Documentation Conventions

Path: **docs** › CONVENTIONS
Parent: [README.md](README.md)

The rules for this tree. They exist so a fresh agent, reading cold, can find the reason behind any
part of the system by walking down the indexes.

## Who this is for

LLM coding agents. Consequences:

- **No prose padding.** No introductions, no restating the heading, no motivational framing.
- **Do not describe the code.** Behaviour is recoverable by reading the source. Reasons are not. A page that only describes behaviour has wasted its reader's time.
- **Point at code by path, never by line number.** Line numbers rot within a day.
- **Keep pages under ~200 lines.** Past that, split (see *Growing the tree*).
- **State things once.** If two pages need the same fact, one owns it and the other links to it.

## The rule that matters

**Never record a choice without recording why it was made.**

Weak — describes behaviour, which the code already does:

> Notifications are only sent to users in the organisation.

Correct — records the decision and the reason, so the next agent cannot undo it by accident:

> Notifications are only sent to users in the organisation. Guest accounts in the workspace are
> frequently customers, and automated internal messages must never reach a customer. The filter is
> therefore on membership, not on activity or role, because a customer with an active account would
> pass an activity check.

The second version survives contact with an agent who has been asked to "make notifications reach
everyone who was mentioned". The first does not.

Apply this to everything, at every size. A timeout value, a sort order, a nullable column, a chosen
library, a rejected refactor — if someone chose it, the reason is written down next to it. Nothing
in this system is decided silently.

Where the reason involves something outside the code — a customer commitment, a rate limit, a
regulation, an incident that happened once — say so explicitly. That reasoning exists nowhere else
and is the most expensive kind to lose.

**If you do not know why something is the way it is, write that it is unknown.** Never invent a
plausible reason. "Reason unknown — do not assume this is arbitrary" is useful; a fabricated
rationale is worse than an empty page, because it will be trusted.

## The recursive structure

The tree is one unit repeated at every depth:

- A **directory** is a part of the system.
- Its **`README.md`** is that part's hub: it indexes every subdirectory and page beside it, and it holds the design and decisions that apply across the part as a whole.
- A **page** (`<name>.md`) is a leaf: one behaviour or component, with its own design and decisions.

The same rules apply at depth one and at depth seven. There is no maximum depth and no preferred
depth — the tree is as deep as the system's own decomposition. Nest by containment, in the words you
would use to say where something lives: area › the thing inside it › the thing inside that › the
specific behaviour. Name directories after parts of the system, not after source paths.

Every index and page opens with:

    Path: [docs](<rel>) › [<ancestor>](<rel>) › … › **<this>**
    Parent: [../README.md](../README.md)

The breadcrumb lets a reader who lands mid-tree see where they are without walking back up.

## Which level a decision belongs at

**Record a decision at the lowest level that contains everything it governs.**

- It affects one behaviour → that behaviour's page.
- It affects several siblings → their parent's `README.md`, under *Design*.
- It affects several areas → the lowest common ancestor, up to `docs/README.md` for system-wide decisions.

Do not copy a decision down into every page it affects. Link from the lower pages to where it is
recorded if the connection is not obvious. This is why readers must read every index on the way
down: an ancestor's decisions bind its descendants.

If a decision recorded on a page turns out to govern its siblings too, move it up to the parent and
leave a link.

## Growing the tree

The tree grows by the same two moves at any depth.

**A page becomes a hub.** When a page passes ~200 lines, or one of its sections starts accumulating
decisions of its own:

1. `x.md` becomes `x/README.md`. Its breadcrumb, *Covers*, *Code*, and the decisions that apply to the whole of `x` stay there, under *Design*.
2. Each section that is really its own behaviour moves to `x/<section>.md`, with its own decisions.
3. In the parent index, the entry moves from *Pages* to *Directories* and its link changes from `x.md` to `x/README.md`.
4. Search the tree for links to `x.md` and repoint them.

**A leaf gets written.** A part listed under *Not yet documented* gets its page the first time work
touches it: create `<name>.md` beside the index, move the entry from *Not yet documented* to *Pages*,
and write the decisions you can actually account for.

**A new part appears.** Create its directory or page at the right place in the tree, with its index
if it is a hub, and list it in its parent's index. If the right parent does not exist yet, create
that too — recursively, up to an existing hub.

Never create a directory to hold a single page. Keep the page one level up and split later.

## Page shape (leaves)

    # <Behaviour or component>

    Path: [docs](<rel>) › … › [<parent>](README.md) › **<this>**
    Parent: [README.md](README.md)
    **Code:** `path/to/thing`, `path/to/other`
    **Covers:** <one sentence: what this page is about and, if useful, what it is not.>

    ## What it does

    <The minimum needed to make the rest legible. Two paragraphs at most. Not a code walkthrough.>

    ## Decisions

    <The payload. Small decisions are one bullet: the decision, then the reason.
    Large ones get their own `###` subsection with the reason, what was rejected and why,
    and what the choice now constrains. Size the entry to the decision.>

    - **<Decision, stated flatly.>** <Why. Including anything outside the code that forced it.>

    ### <A larger decision, stated as the heading>

    **Why.** <Reasoning.>
    **Rejected.** <Alternative — and the reason it lost. Omit only if nothing else was considered.>
    **Constrains.** <What now has to stay true because of this. Omit if nothing does.>

    ## Gotchas

    <Things that will bite an agent changing this. Omit if none.>

    ## Related

    - [<page>](<path>) — <why a reader here would want it>

Hub `README.md` files use the same *Decisions*, *Gotchas* and *Related* sections under their
*Design* heading, for decisions that span their children, followed by *Contents*.

## Linking

- Every file links up to its parent (the `Parent:` line) and down to everything it contains (hubs, via *Contents*).
- Every file links sideways to at least one related page — a sibling it interacts with, a page in another branch that depends on it, the ancestor where a decision governing it is recorded.
- Sideways links carry a reason: `[slack_alert.md](…) — shares the recipient filter defined here`, not just a bare link.
- Use relative links. They survive the repository being moved or forked.

## When a decision changes

Update the page to describe the new decision and its reason, and keep one line recording what it
replaced and why that changed:

> **Changed <date>:** previously <old decision>, because <old reason>. Changed because <what made
> the old reason stop holding>.

Do not simply overwrite. The expensive failure mode is an agent re-proposing an approach that was
already tried and abandoned. Prune these once they are several changes old and no longer informative.

## The documentation pass

Documentation is not a phase at the end of a project. It is a step at the end of **every unit of
work**, run before the work is committed and before the work is reported as done.

1. List the decisions you made during this task — including the ones you made without noticing. Every point where you picked one approach over another was a decision.
2. For each, find the level of the tree that contains everything it governs. If the page or hub does not exist yet, create it — and any missing ancestors — per *Growing the tree*.
3. Write each decision with its reason. If only one part survives, it should be the why.
4. Update the surrounding page where the design changed, not only where you added.
5. Update every affected index, at every level between the change and the nearest existing hub.
6. Check the links you touched resolve.

If the work was purely mechanical — a rename, a dependency bump with no behavioural change — record
nothing and say so. Empty entries dilute the tree.

## Maintenance

- A page that contradicts the code is a bug. Fix it in the same change that revealed it.
- A file missing from its parent index is a bug. Add it before continuing your task.
- A part of the code with no place in the tree is a gap. Add it to the right index under *Not yet documented* before continuing your task.
- A reason that is no longer true gets corrected using the *When a decision changes* form.
- Touching a part that has no page yet, as part of other work? Write the page for what you touched, with the decisions you can actually account for. Do not reconstruct the rest.
