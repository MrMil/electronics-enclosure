"""Layout checks. Errors stop the build; warnings are printed and written to the BOM."""
from __future__ import annotations

from .layout import Model, _overlaps, lip_bottom


def _boxes_overlap(a, b) -> bool:
    return (a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1
            and a.z0 < b.z1 and b.z0 < a.z1)


def bboxes(m: Model) -> dict:
    """Plan-view bounding boxes (x0, y0, x1, y1) of base and lid, in the
    enclosure frame (lid as assembled, not flipped)."""
    c = m.cfg
    wall = c["box"]["wall"]
    r = m.lug_reach
    lx0, lx1 = -wall - m.lid_extra_x - r.get("left", 0), m.L + wall + r.get("right", 0)
    ly0, ly1 = -wall - r.get("front", 0), m.W + wall + r.get("back", 0)
    x0, x1, y0, y1 = -wall - r.get("left", 0), m.L + wall + r.get("right", 0), ly0, ly1
    for t in m.prims["TABS"]:
        reach = wall + t[2]
        if t[0] == "front":
            y0 = min(y0, -reach)
        elif t[0] == "back":
            y1 = max(y1, m.W + reach)
        elif t[0] == "left":
            x0 = min(x0, -reach)
        else:
            x1 = max(x1, m.L + reach)
    return {"base": (x0, y0, x1, y1), "lid": (lx0, ly0, lx1, ly1)}


def footprints(m: Model) -> dict:
    """Sizes of the printed parts in print orientation: (x, y, z) extents."""
    c = m.cfg
    b = bboxes(m)
    (bx0, by0, bx1, by1), (lx0, ly0, lx1, ly1) = b["base"], b["lid"]
    return {"base": (bx1 - bx0, by1 - by0, c["box"]["floor"] + m.H),
            "lid": (lx1 - lx0, ly1 - ly0, c["lid"]["thickness"] + c["lid"]["lip_h"])}


def plate_layout(m: Model, gap: float = 5.0):
    """Offset (dx, dy) that puts the printed lid beside the printed base so both
    fit on one bed, or None. Tries the lid behind the base, then beside it."""
    c = m.cfg
    b = bboxes(m)
    (bx0, by0, bx1, by1), (lx0, ly0, lx1, ly1) = b["base"], b["lid"]
    # print orientation flips the lid about x: y -> -y
    py0, py1 = -ly1, -ly0
    bx, by = c["printer"]["bed"]
    mg = c["printer"].get("bed_margin", 0)
    for dx, dy in ((bx0 - lx0, by1 + gap - py0), (bx1 + gap - lx0, by0 - py0)):
        x0, x1 = min(bx0, lx0 + dx), max(bx1, lx1 + dx)
        y0, y1 = min(by0, py0 + dy), max(by1, py1 + dy)
        w, d = x1 - x0, y1 - y0
        if (w <= bx - mg and d <= by - mg) or (w <= by - mg and d <= bx - mg):
            return dx, dy, w, d
    return None


def validate(m: Model) -> None:
    c = m.cfg
    margin = c["box"]["feature_margin"]
    lipb = lip_bottom(m)
    F = c["box"]["floor"]

    # 1. keep-outs inside the interior and below the lid lip
    for k in m.keepouts:
        if k.x0 < -1e-6 or k.y0 < -1e-6 or k.x1 > m.L + 1e-6 or k.y1 > m.W + 1e-6:
            m.errors.append(f"{k.label}: extends outside the interior "
                            f"(x {k.x0:.1f}..{k.x1:.1f} of 0..{m.L}, y {k.y0:.1f}..{k.y1:.1f} of 0..{m.W})")
        if k.z0 < -1e-6:
            m.errors.append(f"{k.label}: below the floor (z {k.z0:.1f})")
        if k.z1 > lipb + 1e-6:
            m.errors.append(f"{k.label}: top at z {k.z1:.1f} reaches the lid lip (starts at z {lipb:.1f}); "
                            f"raise box.inner height")

    # 2. keep-outs do not collide. Wiring space may overlap wiring space (wires
    #    from different parts meet there) and tie anchors (they exist to sit in
    #    wiring space); solids may not overlap anything.
    ks = m.keepouts
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            kinds = {a.kind, b.kind}
            if kinds <= {"wiring", "anchor", "clearance"}:
                continue
            # A perfboard's clearance is room for its side connectors and their
            # cables, so a low-voltage wall connector body may stand in it; any
            # other solid (PSU, boards, mains parts) may not.
            if "clearance" in kinds and (a.connector or b.connector):
                continue
            if _boxes_overlap(a, b):
                m.errors.append(f"{a.label} overlaps {b.label}")

    # 3. wall features: within the wall, clear of each other, through-cuts below the lip
    for f in m.wall_feats:
        ln = m.wall_len(f.wall)
        if f.through:
            if f.u0 < margin or f.u1 > ln - margin:
                m.errors.append(f"{f.label}: too close to the end of the {f.wall} wall (u {f.u0:.1f}..{f.u1:.1f} of {ln})")
            em = margin if f.edge_margin is None else f.edge_margin
            if f.z0 < em:
                m.errors.append(f"{f.label}: too close to the floor on the {f.wall} wall (bottom z {f.z0:.1f})")
            if not f.at_top and f.z1 > lipb - em:
                m.errors.append(f"{f.label}: reaches the lid lip on the {f.wall} wall "
                                f"(top z {f.z1:.1f}, limit {lipb - em:.1f})")
        elif f.z0 < -F - 1e-6 or f.z1 > m.H + 1e-6:
            m.errors.append(f"{f.label}: outside the {f.wall} wall's height (z {f.z0:.1f}..{f.z1:.1f})")
    feats = m.wall_feats
    for i in range(len(feats)):
        for j in range(i + 1, len(feats)):
            a, b = feats[i], feats[j]
            if a.wall != b.wall or (a.group and a.group == b.group):
                continue
            # a through-cut must keep `margin` from everything; two outside-only
            # footprints (e.g. a tab next to a flange) may touch.
            mg = margin if (a.through or b.through) else 0
            if _overlaps(a.u0, a.u1, b.u0, b.u1, mg) and _overlaps(a.z0, a.z1, b.z0, b.z1, mg):
                m.errors.append(f"{a.label} collides with {b.label} on the {a.wall} wall")

    # 4. holes in the floor clear of everything standing on the floor
    holes = [(x, y, max(d, csk) / 2, max(d, csk) / 2, f"floor mounting hole at ({x}, {y})")
             for x, y, d, csk in m.prims["FLOOR_MOUNTS"]]
    holes += getattr(m, "floor_exits", [])
    for x, y, ex, ey, label in getattr(m, "floor_exits", []):
        if x - ex < margin or y - ey < margin or x + ex > m.L - margin or y + ey > m.W - margin:
            m.errors.append(f"{label}: closer than {margin} mm to a wall (x {x - ex:.1f}..{x + ex:.1f}, "
                            f"y {y - ey:.1f}..{y + ey:.1f})")
    for x, y, ex, ey, label in holes:
        for k in m.keepouts:
            if k.kind == "solid" and k.x0 - ex - margin < x < k.x1 + ex + margin \
                    and k.y0 - ey - margin < y < k.y1 + ey + margin:
                m.errors.append(f"{label} is under {k.label}")

    # 5. mains and low voltage stay on their own sides of the PSU, so their
    #    wires never cross: mains panel parts on the PSU's AC-terminal side,
    #    perfboards and low-voltage panel parts on its DC side.
    p = getattr(m, "psu_info", None)
    if p:
        sided = getattr(m, "sided", [])
        ax_i = 0 if p["axis"] == "x" else 1              # across the PSU: AC vs DC side
        ln_i = 0 if p["len_axis"] == "x" else 1          # along the PSU: distance from the terminal end

        def across(b):
            return (b[ax_i] + b[ax_i + 2]) / 2

        # The mains region: every mains body and cable zone plus the PSU's
        # terminal space, as one bounding box — the inlet's wires run somewhere
        # between them, so the whole hull is treated as mains wiring.
        mb = list(getattr(m, "mains_boxes", [])) + [m.terminal_box]
        hull = (min(b[0] for b in mb), min(b[1] for b in mb), max(b[2] for b in mb), max(b[3] for b in mb))

        def dist(b):
            dx = max(0.0, b[0] - hull[2], hull[0] - b[2])
            dy = max(0.0, b[1] - hull[3], hull[1] - b[3])
            return (dx * dx + dy * dy) ** 0.5

        gap = c["psu"].get("lv_gap", 20)
        for label, b, mains in sided:
            on_ac = (across(b) - p["mid"]) * p["ac_dir"] > 0
            if mains and not on_ac:
                m.errors.append(f"{label} is mains but sits on the PSU's DC side; its wires would cross the low-voltage side")
            if not mains and on_ac:
                if not getattr(m, "lv_route", False):
                    m.errors.append(f"{label} is low voltage but sits on the PSU's AC side; its wires would cross "
                                    f"the mains side (or set psu.lv_route: far_end)")
                elif dist(b) < gap:
                    m.errors.append(f"{label} is on the AC side but only {dist(b):.0f} mm from the mains "
                                    f"wiring (inlet, its wires and the PSU terminals; need {gap})")

    # 6. the printed parts fit the bed, keeping bed_margin free
    bx, by = c["printer"]["bed"]
    mg = c["printer"].get("bed_margin", 0)
    ux, uy = bx - mg, by - mg
    m.bed_report = []
    # Walls with holes that need slicer supports get bed room outside them for
    # the supports to stand on (printer.support_margin per such wall).
    sm = c["printer"].get("support_margin", 0)
    extra_x = sm * len(m.support_walls & {"left", "right"})
    extra_y = sm * len(m.support_walls & {"front", "back"})
    for part, (sx, sy, sz) in footprints(m).items():
        if part == "base":
            sx, sy = sx + extra_x, sy + extra_y
        fits = (sx <= ux and sy <= uy) or (sx <= uy and sy <= ux)
        m.bed_report.append((part, sx, sy, min(ux - sx, uy - sy) if fits else None))
        if not fits:
            m.errors.append(f"{part}: footprint {sx:.1f} x {sy:.1f} mm does not fit the {bx} x {by} mm bed "
                            f"(keeping {mg} mm margin)")
