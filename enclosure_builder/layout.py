"""Turn a merged parameter tree into geometry primitives for scad/enclosure.scad.

All component knowledge lives here; the SCAD side only knows generic primitives
(wall rects/rounds/slots, floor bolts, standoffs, pads, lock tongues, tabs, ...).
Each placement also records keep-out volumes and wall footprints so that
validate.py can check the layout, and hardware so that emit.py can write a BOM.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

WALLS = ("front", "back", "left", "right")
STANDOFF_OD = 7.0
WIRING_COLOR = ("Orange", 0.22)


@dataclass
class Box3:
    """Axis-aligned keep-out volume in interior coordinates."""
    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float
    label: str
    kind: str = "solid"   # solid | wiring | anchor | clearance
    connector: bool = False   # low-voltage wall connector body (may sit in a perfboard clearance)


@dataclass
class WallFeat:
    """Footprint of something on a wall, in that wall's (u, z) plane."""
    wall: str
    u0: float
    u1: float
    z0: float
    z1: float
    label: str
    through: bool = True   # cuts through the wall (vs. only occupies its outside face)
    group: str = ""        # features of one part share a group and are not checked against each other
    at_top: bool = False   # deliberately reaches the wall top (lid lock); exempt from the lip limit
    edge_margin: float | None = None   # floor/lip clearance if not box.feature_margin


@dataclass
class Model:
    cfg: dict
    L: float
    W: float
    H: float
    scalars: dict = field(default_factory=dict)
    prims: dict = field(default_factory=lambda: {k: [] for k in (
        "PADS", "STANDOFFS", "TIE_ANCHORS", "FLOOR_BOLTS", "FLOOR_MOUNTS", "FLOOR_SLOTS",
        "TABS", "WALL_RECTS", "WALL_ROUNDS", "WALL_SLOTS", "WALL_POCKETS",
        "LOCK_SLOTS", "LID_TONGUES", "LIP_GAPS", "LID_SLOTS", "LOCK_LUGS", "WIRE_GUIDES", "GHOSTS")})
    keepouts: list = field(default_factory=list)
    wall_feats: list = field(default_factory=list)
    bom: list = field(default_factory=list)       # (qty, item, purpose)
    warnings: list = field(default_factory=list)
    checks: list = field(default_factory=list)    # datasheet values the owner should confirm
    support_notes: list = field(default_factory=list)  # openings left without a self-supporting top
    support_walls: set = field(default_factory=set)    # walls carrying such openings (need bed room for supports)
    errors: list = field(default_factory=list)
    lid_extra_x: float = 0.0                      # finger pull sticking out past the left wall
    lug_reach: dict = field(default_factory=dict)  # wall -> how far a lock lug sticks out

    def wall_len(self, wall: str) -> float:
        return self.L if wall in ("front", "back") else self.W

    def wall_to_xy(self, wall: str, u: float, depth: float) -> tuple[float, float]:
        """Interior point `depth` mm in from `wall` at position u along it."""
        return {
            "front": (u, depth),
            "back": (u, self.W - depth),
            "left": (depth, u),
            "right": (self.L - depth, u),
        }[wall]

    def wall_box(self, wall, u0, u1, z0, z1, depth, label, kind="solid", start=0.0) -> Box3:
        """Keep-out volume from `start` to `depth` mm in from a wall."""
        if wall == "front":
            return Box3(u0, start, z0, u1, depth, z1, label, kind)
        if wall == "back":
            return Box3(u0, self.W - depth, z0, u1, self.W - start, z1, label, kind)
        if wall == "left":
            return Box3(start, u0, z0, depth, u1, z1, label, kind)
        return Box3(self.L - depth, u0, z0, self.L - start, u1, z1, label, kind)

    def ghost(self, k: Box3, color, alpha):
        self.prims["GHOSTS"].append([k.x0, k.y0, k.z0, k.x1 - k.x0, k.y1 - k.y0, k.z1 - k.z0, color, alpha])

    def wiring(self, k: Box3):
        """Space wires need. Shown orange in the interior preview."""
        k.kind = "wiring"
        self.keepouts.append(k)
        self.ghost(k, *WIRING_COLOR)

    def note_verification(self, spec: dict, label: str):
        """Report each library part once, however many times it is placed."""
        v = spec.get("verified")
        seen = self.__dict__.setdefault("_noted", set())
        if v is True or spec.get("part") in seen:
            return
        seen.add(spec.get("part"))
        if v == "datasheet":
            self.checks.append(f"{label}: from {spec.get('source', 'a datasheet')} — {spec.get('check', 'confirm against the part')}")
        else:
            self.warnings.append(f"{label}: dimensions NOT verified against the real part")


def pick_length(lengths, minimum) -> float | None:
    for n in sorted(lengths):
        if n >= minimum - 1e-6:
            return n
    return None


def check_wall(model: Model, wall: str, where: str) -> bool:
    if wall not in WALLS:
        model.errors.append(f"{where}: wall must be one of {WALLS}, got {wall!r}")
        return False
    return True


def lip_bottom(m: Model) -> float:
    return m.H - m.cfg["lid"]["lip_h"]


# --------------------------------------------------------------------------- box


def place_box(m: Model) -> None:
    c = m.cfg
    hw = c["hardware"]["m3"]
    box, lid = c["box"], c["lid"]
    m.scalars.update(
        L=m.L, W=m.W, H=m.H,
        WALL=box["wall"], FLOOR=box["floor"], OUTER_R=box["outer_radius"],
        LAYER=c["printer"]["layer_h"],
        M3_CLEAR=hw["clear_d"], HEAD_CB_D=hw["head_cb_d"],
        NUT_POCKET_AF=hw["nut_af"] + hw["nut_pocket_clearance"],
        NUT_POCKET_H=hw["nut_h"] + hw["nut_pocket_clearance"],
        LID_T=lid["thickness"], LIP_H=lid["lip_h"], LIP_T=lid["lip_t"], LIP_CLR=lid["lip_clearance"],
        TIE_W=c["wire_tie"]["w"], TIE_H=c["wire_tie"]["h"], TIE_LEN=c["wire_tie"]["len"],
    )


# --------------------------------------------------------------------------- lid lock


def place_lid_lock(m: Model) -> None:
    """Drop-and-slide lid: tongues on the lid lip slide under ledges in the long
    walls; a flexible tab with a tooth stops the lid sliding back. See
    docs/enclosure/lid_closure.md."""
    c = m.cfg
    lid = c["lid"]
    wall = c["box"]["wall"]
    s, tw, reach, clr = lid["slide"], lid["tongue_w"], lid["tongue_reach"], lid["tongue_clearance"]
    rim, lip_h = lid["rim"], lid["lip_h"]

    z_ceil = m.H - rim                  # slot ceiling at the wall's inner face (slopes 45° down outward)
    z_tongue_top = z_ceil - 0.25        # tongue's top at the inner face, parallel to the ceiling
    z_tongue_bot = m.H - lip_h + 0.5
    z_slot_bot = z_tongue_bot - 0.5
    if (z_tongue_top - reach) - z_tongue_bot < 1.0:
        m.errors.append("lid: tongue tip thinner than 1 mm; raise lid.lip_h or lower lid.rim")
    if z_ceil - wall <= z_slot_bot + 0.3:
        m.errors.append("lid: lock slot closes before the outer wall face; raise lid.lip_h")
    if s < tw + clr + 0.5:
        m.errors.append("lid.slide must exceed tongue_w + clearance so the locked tongue is fully under the ledge")

    margin = c["box"]["feature_margin"]

    def span(u):          # u-range a tongue occupies on its wall: entry notch .. locked slot end
        return u - s - tw / 2 - clr, u + tw / 2 + clr

    def clear(wname, u):
        a0, a1 = span(u)
        return all(not (f.wall == wname and a0 < f.u1 + margin and f.u0 < a1 + margin
                        and z_slot_bot < f.z1 + margin and f.z0 < m.H + margin)
                   for f in m.wall_feats)

    lo, hi = s + tw + 4, m.L - tw / 2 - clr - 6       # first/last positions the lip can carry
    for wname in ("front", "back"):
        us = lid.get("tongues")
        if isinstance(us, dict):
            us = us.get(wname)
        if us in (None, "auto"):
            # Ends + middle, each slid toward the centre until it clears the wall's
            # other features (e.g. a flange reaching up into the lock zone).
            wanted = [(lo, 1), (hi, -1)] + ([(m.L / 2, 1)] if m.L > 150 else [])
            us = []
            for u0, step in wanted:
                u = u0
                while not clear(wname, u) and lo <= u <= hi:
                    u += step
                if not lo <= u <= hi:
                    m.errors.append(f"lid: no room for a lock tongue on the {wname} wall near u={u0:.0f}")
                    continue
                if abs(u - u0) > 1e-6:
                    m.checks.append(f"lid: {wname}-wall tongue moved from u={u0:.0f} to u={u:.0f} to clear other features")
                us.append(u)
        for u in us:
            n0, n1 = u - s - tw / 2 - clr, u - s + tw / 2 + clr     # entry notch
            s1 = u + tw / 2 + clr                                    # end of the slot when locked
            m.prims["WALL_RECTS"].append([wname, (n0 + n1) / 2, (z_slot_bot + m.H + 1) / 2,
                                          n1 - n0, m.H + 1 - z_slot_bot, 0, 0])   # open top: no roof
            m.prims["LOCK_SLOTS"].append([wname, n0, s1, z_slot_bot, z_ceil])
            m.prims["LID_TONGUES"].append([wname, u, tw, z_tongue_bot, z_tongue_top, reach])
            m.wall_feats.append(WallFeat(wname, n0, s1, z_slot_bot, m.H, "lid lock",
                                         group="lid lock", at_top=True))

    tab_u = lid.get("tab_u")
    if tab_u is None:
        tab_u = m.W / 2
    tw2 = lid["tab_w"] / 2 + lid["tab_slit"]
    m.scalars.update(
        LOCK_SLIDE=s, TAB_U=tab_u, TAB_W=lid["tab_w"], TAB_LEN=lid["tab_len"], TAB_SLIT=lid["tab_slit"],
        TAB_PULL=lid["tab_pull"], TOOTH_H=lid["tooth_h"], TOOTH_LEN=lid["tooth_len"], TOOTH_W=lid["tooth_w"],
    )
    m.prims["LIP_GAPS"].append([tab_u - tw2 - 1, tab_u + tw2 + 1])
    # The tooth crosses the left wall's top and hangs outside it while unlocked.
    m.wall_feats.append(WallFeat("left", tab_u - tw2, tab_u + tw2, m.H - lid["tooth_h"] - 1, m.H,
                                 "lid lock tab", through=False, group="lid lock", at_top=True))
    m.lid_extra_x = lid["tab_pull"]

    # Zip-tie lock: a lug on the lid plate over a lug on the wall, holes aligned
    # only when the lid is closed. A tie through both stops sliding and lifting.
    lug = lid.get("lock_lug")
    if lug:
        lw, lr = lid["lug_w"], lid["lug_reach"]
        if lug["wall"] not in WALLS:
            m.errors.append(f"lid.lock_lug.wall must be one of {WALLS}")
        else:
            u = lug["u"]
            m.prims["LOCK_LUGS"].append([lug["wall"], u])
            m.scalars.update(LUG_W=lw, LUG_REACH=lr, LUG_HOLE=lid["lug_hole"], LUG_T=lid["lug_t"])
            m.lug_reach[lug["wall"]] = lr
            m.wall_feats.append(WallFeat(lug["wall"], u - lw / 2, u + lw / 2, m.H - 0.4 - lid["lug_t"] - lr - 1, m.H,
                                         "lid lock lug", through=False, group="lid lock lug", at_top=True))
    if "LUG_W" not in m.scalars:
        m.scalars.update(LUG_W=0, LUG_REACH=0, LUG_HOLE=0, LUG_T=0)


# --------------------------------------------------------------------------- psu


PSU_TERMINALS = ("left", "right", "front", "back")


def psu_frame(term, ax, ay, sx, sy):
    """Map the PSU's local frame to interior coordinates.

    Local frame: px along the length from the terminal end, py across, growing
    toward the left of someone facing the terminal block from outside. The
    four orientations are rotations (never mirror images), so asymmetric hole
    patterns land where they physically are. Returns (to_global, footprint)."""
    if term == "left":     # terminals face -x; viewer looks +x, their left is +y
        f = lambda px, py: (ax + px, ay + py)
        return f, (sx, sy)
    if term == "right":    # viewer looks -x, their left is -y
        f = lambda px, py: (ax + sx - px, ay + sy - py)
        return f, (sx, sy)
    if term == "front":    # terminals face -y; viewer looks +y, their left is -x
        f = lambda px, py: (ax + sy - py, ay + px)
        return f, (sy, sx)
    f = lambda px, py: (ax + py, ay + sx - px)   # back: viewer looks -y, their left is +x
    return f, (sy, sx)


def local_box(to_g, px0, py0, px1, py1):
    (x0, y0), (x1, y1) = to_g(px0, py0), to_g(px1, py1)
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def place_psu(m: Model) -> None:
    inst = m.cfg["psu"]
    spec = inst["spec"]
    hw = m.cfg["hardware"]["m3"]
    F = m.cfg["box"]["floor"]
    sx, sy, sz = spec["size"]
    ax, ay = inst["at"]
    term = inst.get("terminals", "left")
    if term not in PSU_TERMINALS:
        m.errors.append(f"psu.terminals must be one of {PSU_TERMINALS}")
        return
    label = f"psu {spec['part']}"
    to_g, (fw, fd) = psu_frame(term, ax, ay, sx, sy)
    along_x = term in ("left", "right")

    # Bolts come up through the floor into the PSU's own M3 threads. Pad height
    # is derived from the bolt length so the head is recessed and the tip enters
    # the case by exactly max_penetration. The head seats on the second bridge
    # layer, one layer above the counterbore.
    bolt, pen = spec["bolt_len"], spec["max_penetration"]
    cb_depth = hw["head_h"] + hw["head_recess"]
    seat = cb_depth + m.cfg["printer"]["layer_h"]
    pad_h = seat + (bolt - pen) - F
    if pad_h < 1.0:
        m.errors.append(f"{label}: bolt_len {bolt} too short for a {F} mm floor; pad would be {pad_h:.1f} mm")
        pad_h = 1.0
    slack = spec.get("hole_slack", 0)

    # holes_alt: positions cut and padded but not bolted — used when it is not
    # known which of two mirror-image positions the real holes are at.
    for hx, hy in list(spec["holes"]) + list(spec.get("holes_alt") or []):
        x, y = to_g(hx, hy)
        m.prims["FLOOR_BOLTS"].append([x, y, 2 * slack, pad_h, cb_depth, 0 if along_x else 90])
        x0, y0, x1, y1 = local_box(to_g, max(0, hx - slack - 6), max(0, hy - 6),
                                   min(sx, hx + slack + 6), min(sy, hy + 6))
        m.prims["PADS"].append([x0, y0, x1, y1, pad_h])
    alt = " — use whichever floor slots line up with the PSU's holes" if spec.get("holes_alt") else ""
    m.bom.append((len(spec["holes"]), f"M3 x {bolt} socket head",
                  f"{label}, from under the floor into the PSU (enters {pen} mm — do not substitute a longer bolt){alt}"))

    top = pad_h + sz
    m.keepouts.append(Box3(ax, ay, 0, ax + fw, ay + fd, top, label))
    clr = spec.get("terminal_clearance", 0)
    tx0, ty0, tx1, ty1 = local_box(to_g, -clr, 0, 0, sy)
    m.wiring(Box3(tx0, ty0, 0, tx1, ty1, lip_bottom(m), f"{label} terminal wiring"))
    m.terminal_box = (tx0, ty0, tx1, ty1)

    m.prims["GHOSTS"].append([ax, ay, pad_h, fw, fd, sz, "Silver", 0.9])
    tb = spec.get("terminal_block", {"len": 15, "h": 10})
    bx0, by0, bx1, by1 = local_box(to_g, 0, 8, tb["len"], sy - 8)
    m.prims["GHOSTS"].append([bx0, by0, top, bx1 - bx0, by1 - by0, tb["h"], "DimGray", 1])

    # Which way the AC terminals face across the PSU. Spec ac_side says whether
    # AC is on the left or right of someone facing the terminal block; in the
    # local frame "left" is +py, so map +py to an interior axis and sign.
    ac_side = spec.get("ac_side", "left")
    (gx0, gy0), (gx1, gy1) = to_g(0, 0), to_g(0, 1)
    axis = "y" if abs(gy1 - gy0) > 0.5 else "x"
    sign = (gy1 - gy0) if axis == "y" else (gx1 - gx0)
    ac_dir = int(sign) if ac_side == "left" else -int(sign)
    # terminal-end coordinate along the length, and direction away from it
    (ex, ey), (fx, fy) = to_g(0, 0), to_g(1, 0)
    m.psu_info = dict(ax=ax, ay=ay, sx=sx, sy=sy, fw=fw, fd=fd, term=term, tb_len=tb["len"], top=top,
                      to_g=to_g, axis=axis, mid=(ax + fw / 2) if axis == "x" else (ay + fd / 2),
                      mid_y=ay + fd / 2, ac_dir=ac_dir,
                      len_axis="x" if along_x else "y", end=ex if along_x else ey,
                      len_dir=(fx - ex) if along_x else (fy - ey))
    m.note_verification(spec, label)


# --------------------------------------------------------------------------- perfboards


def place_perfboards(m: Model) -> None:
    c = m.cfg
    hw = c["hardware"]["m3"]
    F = c["box"]["floor"]
    for i, inst in enumerate(c["perfboards"]):
        spec = inst["spec"]
        label = f"perfboard[{i}] {spec['part']}"
        bx, by = inst["at"]
        w, d = spec["size"]
        t = spec["thickness"]
        rot = inst.get("rotate", 0)
        if rot not in (0, 90):
            m.errors.append(f"{label}: rotate must be 0 or 90")
            continue
        if rot == 90:
            w, d = d, w

        # Bolt from the top through the board and a printed standoff into a hex
        # nut in a pocket under the floor. Standoff height is derived from a
        # standard bolt length so the tip ends 0.5 mm inside the floor's underside.
        min_so = inst.get("min_standoff", c["perfboard"]["min_standoff"])
        bolt = pick_length(hw["lengths"], min_so + t + F - 0.5)
        if bolt is None:
            m.errors.append(f"{label}: no standard M3 length long enough")
            continue
        standoff = bolt + 0.5 - t - F
        for hx, hy in spec["holes"]:
            if rot == 90:
                hx, hy = spec["size"][1] - hy, hx
            m.prims["STANDOFFS"].append([bx + hx, by + hy, STANDOFF_OD, standoff])
        n = len(spec["holes"])
        m.bom += [(n, f"M3 x {bolt} socket head", f"{label}, from the top"),
                  (n, "M3 hex nut", f"{label}, in pockets under the floor")]
        top = standoff + t + spec.get("component_h", 25)
        m.keepouts.append(Box3(bx, by, 0, bx + w, by + d, top, label))
        m.sided = getattr(m, "sided", []) + [(label, (bx, by, bx + w, by + d), False)]
        # `clearance: {left|right|front|back: mm}` — free room beside the board's
        # edges for its side connectors and their cables (see perfboard_mount.md).
        for side, mm in (inst.get("clearance") or {}).items():
            cx0, cy0, cx1, cy1 = {"left": (bx - mm, by, bx, by + d), "right": (bx + w, by, bx + w + mm, by + d),
                                  "front": (bx, by - mm, bx + w, by), "back": (bx, by + d, bx + w, by + d + mm)}.get(
                                      side, (None,) * 4)
            if cx0 is None:
                m.errors.append(f"{label}: clearance side must be left/right/front/back, got {side!r}")
                continue
            k = Box3(cx0, cy0, 0, cx1, cy1, lip_bottom(m), f"{label} clearance ({side})", "clearance")
            m.keepouts.append(k)
            m.ghost(k, "DeepSkyBlue", 0.18)
        m.prims["GHOSTS"].append([bx, by, standoff, w, d, t, "ForestGreen", 1])
        m.prims["GHOSTS"].append([bx + 2, by + 2, standoff + t, w - 4, d - 4, spec.get("component_h", 25),
                                  "LimeGreen", 0.15])
        m.note_verification(spec, label)


# --------------------------------------------------------------------------- wall parts


def _rot(u, z, rot):
    return (-z, u) if rot == 90 else (u, z)


def _cutout(m: Model, wall, u, z, cut, rot, cover_above, top_limit, label=""):
    """Emit a rect or round cutout; return its (half-width, below, above) extents.
    It gets a full 45° point only if the whole point stays hidden behind the
    part's flange (`cover_above` - 1 mm) and below `top_limit` (the wall under
    the lid lip). Otherwise it keeps its plain shape: a partial point saves
    little support and could show past the flange."""
    if cut["shape"] == "rect":
        cw, ch = (cut["h"], cut["w"]) if rot == 90 else (cut["w"], cut["h"])
        top = z + ch / 2 + cw / 2
        rise = cw / 2 if (ch / 2 + cw / 2 <= cover_above - 1 and top <= top_limit) else 0
        if not rise:
            m.support_notes.append(f"{label} cutout: flat {cw:g} mm top (bridge, or support if your slicer wants it)")
            m.support_walls.add(wall)
        m.prims["WALL_RECTS"].append([wall, u, z, cw, ch, cut.get("r", 0), rise])
        return cw / 2, ch / 2, ch / 2 + rise
    dd = cut["d"]
    tip = dd / 2 * math.sqrt(2)
    full = tip <= cover_above - 1 and z + tip <= top_limit
    if not full:
        m.support_notes.append(f"{label} hole: round {dd:g} mm top (overhang; may want support)")
        m.support_walls.add(wall)
    m.prims["WALL_ROUNDS"].append([wall, u, z, dd, 0 if full else -1])   # -1: plain circle
    return dd / 2, dd / 2, tip if full else dd / 2


def place_panel_parts(m: Model) -> None:
    c = m.cfg
    hw = c["hardware"]["m3"]
    wall_t = c["box"]["wall"]
    for i, inst in enumerate(c["panel_parts"]):
        spec = inst["spec"]
        label = f"panel[{i}] {spec['part']}"
        wall, u, z = inst["wall"], inst["u"], inst["z"]
        if not check_wall(m, wall, label):
            continue
        rot = inst.get("rotate", 0)
        cut = spec["cutout"]
        if cut["shape"] not in ("rect", "round"):
            m.errors.append(f"{label}: unknown cutout shape {cut['shape']!r}")
            continue
        panel_t = wall_t
        if spec.get("max_panel_t") is not None and spec["max_panel_t"] < wall_t:
            panel_t = spec["max_panel_t"]

        fh_ = spec["flange"][0] if rot == 90 else spec["flange"][1]
        hx, below, above = _cutout(m, wall, u, z, cut, rot, fh_ / 2,
                                   lip_bottom(m) - c["box"]["feature_margin"], spec["part"])
        m.wall_feats.append(WallFeat(wall, u - hx, u + hx, z - below, z + above, label + " cutout", group=label))

        bolts = spec.get("bolts") or []
        # The nut on the inside face must clear the floor and the lid lip; it
        # only needs room to sit and turn, not wall material around it.
        nut_r = hw["nut_af"] / 2 / math.cos(math.radians(30))
        for bu, bz in bolts:
            bu, bz = _rot(bu, bz, rot)
            m.prims["WALL_ROUNDS"].append([wall, u + bu, z + bz, hw["clear_d"], 0])
            m.wall_feats.append(WallFeat(wall, u + bu - nut_r, u + bu + nut_r, z + bz - nut_r, z + bz + nut_r,
                                         label + " nut", group=label, edge_margin=0.5))
        if bolts:
            bolt = pick_length(hw["lengths"], spec.get("bolt_stack", 3) + panel_t + hw["nut_h"] + 1)
            m.bom += [(len(bolts), f"M3 x {bolt} socket head", f"{label} flange, head outside"),
                      (len(bolts), "M3 hex nut", f"{label} flange, inside")]

        fw, fh = spec["flange"]
        if rot == 90:
            fw, fh = fh, fw
        m.wall_feats.append(WallFeat(wall, u - fw / 2, u + fw / 2, z - fh / 2, z + fh / 2,
                                     label + " flange", through=False, group=label))
        if panel_t < wall_t:
            m.prims["WALL_POCKETS"].append([wall, u, z, fw, fh, wall_t - panel_t])

        # Solid body behind the panel, then the space its cable or wires need.
        body, cable = spec["inside"], spec.get("cable")
        bw, bh = (body["h"], body["w"]) if rot == 90 else (body["w"], body["h"])
        k = m.wall_box(wall, u - bw / 2, u + bw / 2, z - bh / 2, z + bh / 2, body["depth"], label + " body")
        k.connector = not spec.get("mains")
        m.sided = getattr(m, "sided", []) + [(label, (k.x0, k.y0, k.x1, k.y1), bool(spec.get("mains")))]
        m.keepouts.append(k)
        m.ghost(k, "Black", 0.85)
        if spec.get("mains"):
            m.mains_boxes = getattr(m, "mains_boxes", []) + [(k.x0, k.y0, k.x1, k.y1)]
        if cable:
            cw, ch = (cable["h"], cable["w"]) if rot == 90 else (cable["w"], cable["h"])
            ck = m.wall_box(wall, u - cw / 2, u + cw / 2, max(0, z - ch / 2), min(lip_bottom(m), z + ch / 2),
                            cable["depth"], label + " cable", start=body["depth"])
            m.wiring(ck)
            if spec.get("mains"):
                m.mains_boxes.append((ck.x0, ck.y0, ck.x1, ck.y1))
        m.note_verification(spec, label)


def place_wire_holes(m: Model) -> None:
    """Wire exits: round holes (`d`) or pass-through slots for connectors
    (`part:` from components/passthrough), in a wall or in the floor."""
    c = m.cfg
    wt = c["wire_tie"]
    for i, h in enumerate(c["wire_holes"]):
        label = f"wire_hole[{i}]"
        spec = h.get("spec") or {}
        slot = spec.get("slot")
        d = h.get("d", spec.get("d"))
        if not slot and not d:
            m.errors.append(f"{label}: needs `d` or a passthrough `part`")
            continue
        inside = h.get("inside_depth", spec.get("inside_depth", 15))
        anchor = h.get("tie_anchor", spec.get("tie_anchor", True))
        if spec:
            label += f" {spec['part']}"
            m.note_verification(spec, spec["part"])

        if h["wall"] == "floor":
            x, y = h["at"]
            rot = h.get("rotate", 0)
            # A part's `round` hole wins in the floor: the board under the box
            # is drilled straight through it, which a slot does not allow.
            rnd = spec.get("round")
            if rnd:
                d = rnd["d"]
            w, hh, r = (d, d, d / 2) if rnd or not slot else (slot["w"], slot["h"], slot.get("r", 0))
            m.prims["FLOOR_SLOTS"].append([x, y, w, hh, r, rot])
            ex, ey = (w / 2, hh / 2) if rot == 0 else (hh / 2, w / 2)
            m.wiring(Box3(x - ex, y - ey, 0, x + ex, y + ey, min(inside, lip_bottom(m)), label))
            m.floor_exits = getattr(m, "floor_exits", []) + [(x, y, ex, ey, label)]
            m.floor_drills = getattr(m, "floor_drills", []) + [(x, y, w, hh, rnd.get("drill") if rnd else None)]
            if anchor:
                # `anchor_at: [dx, dy]` places the zip-tie anchor relative to the
                # hole when the default spot (just behind it; `rotate: 90` puts
                # it to the right) is taken.
                if h.get("anchor_at"):
                    ax_, ay_ = x + h["anchor_at"][0], y + h["anchor_at"][1]
                else:
                    ax_, ay_ = (x, y + ey + 8) if rot == 0 else (x + ex + 8, y)
                _tie_anchor(m, ax_, ay_, 0 if rot == 0 else 90, label)
            continue

        wall, u, z = h["wall"], h["u"], h["z"]
        if not check_wall(m, wall, label):
            continue
        # Nothing covers a wire exit, so it gets a full 45° point: no bridge at all.
        if slot:
            sw, sh = (slot["h"], slot["w"]) if h.get("rotate", 0) == 90 else (slot["w"], slot["h"])
            m.prims["WALL_RECTS"].append([wall, u, z, sw, sh, slot.get("r", 0), sw / 2])
            hx, below, above = sw / 2, sh / 2, sh / 2 + sw / 2
        else:
            m.prims["WALL_ROUNDS"].append([wall, u, z, d, 0])
            hx, below, above = d / 2, d / 2, d / 2 * math.sqrt(2)
        m.wall_feats.append(WallFeat(wall, u - hx, u + hx, z - below, z + above, label))
        m.wiring(m.wall_box(wall, u - hx, u + hx, max(0, z - below), min(lip_bottom(m), z + above), inside, label))
        if anchor:
            x, y = m.wall_to_xy(wall, u, wt["anchor_distance"])
            _tie_anchor(m, x, y, 0 if wall in ("front", "back") else 90, label)


def _tie_anchor(m: Model, x, y, ang, label):
    wt = m.cfg["wire_tie"]
    m.prims["TIE_ANCHORS"].append([x, y, ang])
    half_l, half_w = wt["len"] / 2, wt["w"] / 2 + 2
    hx, hy = (half_l, half_w) if ang == 0 else (half_w, half_l)
    m.keepouts.append(Box3(x - hx, y - hy, 0, x + hx, y + hy, wt["h"] + wt["w"] / 2 + 1.6,
                           label + " tie anchor", "anchor"))


# --------------------------------------------------------------------------- mounting


def place_lv_route(m: Model) -> None:
    """`psu.lv_route: far_end` — the low-voltage wires leave the DC terminals,
    run in a channel along the PSU's DC side and round its far end, held by
    printed loops. Lets low-voltage parts sit on the AC side, beyond the far
    end of the mains wiring, without any wire crossing the mains end."""
    route = m.cfg["psu"].get("lv_route")
    if not route:
        return
    if route != "far_end":
        m.errors.append("psu.lv_route must be far_end (or omitted)")
        return
    g = m.cfg["wire_guides"]
    p = m.psu_info
    if p["term"] not in ("left", "right"):
        m.errors.append("psu.lv_route: far_end is only implemented for terminals facing left or right")
        return
    # Loops lean on a wall: the wall is one side of the tunnel, so they stick
    # out w + t from it (see docs/enclosure/wire_routing.md).
    outer = g["w"] + g["t"]
    fw, fh = sorted(g["fits"] or [0, 0])  # optional connector cross-section that must pass
    c_ = g["fit_clearance"]
    if g["fits"] and not ((g["w"] >= fw + c_ and g["h"] >= fh + c_) or (g["w"] >= fh + c_ and g["h"] >= fw + c_)):
        m.errors.append(f"wire_guides: a {fw} x {fh} connector does not pass a {g['w']} wide, "
                        f"{g['h']} tall tunnel with {c_} mm clearance")
    lb = lip_bottom(m)
    ax, ay, sx, sy = p["ax"], p["ay"], p["sx"], p["sy"]
    # DC-side channel, between the PSU and the DC-side long wall
    if p["ac_dir"] > 0:
        cy0, cy1 = 0.0, ay
    else:
        cy0, cy1 = ay + sy, m.W
    # far-end channel, between the PSU's far end and that short wall
    if p["term"] == "left":
        fx0, fx1, xs = ax + sx, m.L, list(range(int(ax + 20), int(ax + sx - 10) + 1, int(g["spacing"])))
    else:
        fx0, fx1, xs = 0.0, ax, list(range(int(ax + sx - 20), int(ax + 10) - 1, -int(g["spacing"])))
    for name, width in (("DC-side channel", cy1 - cy0), ("far-end channel", fx1 - fx0)):
        if width < outer + 1:
            m.errors.append(f"psu.lv_route: {name} is {width:.1f} mm; wire loops need {outer + 1:.1f}")
    m.wiring(Box3(min(ax, fx0), cy0, 0, max(ax + sx, fx1), cy1, lb, "low-voltage route (DC side)"))
    far_y0, far_y1 = (min(cy0, ay), ay + sy) if p["ac_dir"] > 0 else (ay, max(cy1, ay + sy))
    m.wiring(Box3(fx0, far_y0, 0, fx1, far_y1, lb, "low-voltage route (far end)"))
    gh = g["h"] + outer + g["t"] * 0.414          # apex where the roof meets the wall
    if gh > lb:
        m.errors.append(f"wire loops reach z {gh:.1f}, into the lid lip (starts at {lb:.1f})")
    side_wall = "front" if p["ac_dir"] > 0 else "back"
    end_wall = "right" if p["term"] == "left" else "left"
    loops = [(side_wall, x) for x in xs] + [(end_wall, y) for y in (ay + 15, ay + sy - 15)]
    for wname, u in loops:
        m.prims["WIRE_GUIDES"].append([wname, u])
        m.keepouts.append(m.wall_box(wname, u - g["len"] / 2, u + g["len"] / 2, 0, gh, outer,
                                     "wire loop", "anchor"))
        m.wall_feats.append(WallFeat(wname, u - g["len"] / 2, u + g["len"] / 2, 0, gh,
                                     "wire loop", through=False, group="wire loops"))
    m.scalars.update(GUIDE_W=g["w"], GUIDE_H=g["h"], GUIDE_T=g["t"], GUIDE_LEN=g["len"])
    m.lv_route = True


def place_mounting(m: Model) -> None:
    mt = m.cfg["mounting"]
    style = mt.get("style", "tabs")
    csk = mt.get("head_d") or mt["screw_d"]
    F = m.cfg["box"]["floor"]
    if style == "tabs":
        for i, t in enumerate(mt.get("tabs") or []):
            if not check_wall(m, t["wall"], f"mounting.tabs[{i}]"):
                continue
            ln, w = t.get("len", mt["tab_len"]), t.get("w", mt["tab_w"])
            m.prims["TABS"].append([t["wall"], t["u"], ln, w, mt["tab_t"], mt["screw_d"], csk,
                                    mt["rib_h"], mt["rib_t"]])
            m.wall_feats.append(WallFeat(t["wall"], t["u"] - w / 2, t["u"] + w / 2, -F,
                                         -F + mt["tab_t"] + mt["rib_h"], f"mounting tab {i}", through=False))
        n = len(mt.get("tabs") or [])
    elif style == "floor":
        for x, y in mt.get("floor_holes") or []:
            m.prims["FLOOR_MOUNTS"].append([x, y, mt["screw_d"], csk])
        n = len(mt.get("floor_holes") or [])
    else:
        m.errors.append("mounting.style must be tabs or floor")
        return
    if n == 0:
        m.warnings.append("no mounting points defined")
    else:
        m.bom.append((n, f"screw, shank <= {mt['screw_d'] - 0.3:.1f} mm, head <= {csk:.0f} mm",
                      "fixing the enclosure (user's choice of screw)"))


# --------------------------------------------------------------------------- vents


def _overlaps(a0, a1, b0, b1, margin=0.0):
    return a0 < b1 + margin and b0 < a1 + margin


def place_vents(m: Model) -> None:
    c = m.cfg
    v = c["vents"]
    margin = c["box"]["feature_margin"]
    for i, reg in enumerate(v.get("walls") or []):
        wall = reg["wall"]
        if not check_wall(m, wall, f"vents.walls[{i}]"):
            continue
        u0, u1 = reg["u"]
        z0, z1 = reg["z"]
        w, pitch = reg.get("slot_w", v["slot_w"]), reg.get("pitch", v["pitch"])
        z0, z1 = max(z0, margin), min(z1, lip_bottom(m) - margin)
        placed = 0
        u = u0 + w / 2
        while u <= u1 - w / 2 + 1e-6:
            clash = any(f.wall == wall and _overlaps(u - w / 2, u + w / 2, f.u0, f.u1, margin)
                        and _overlaps(z0, z1, f.z0, f.z1, margin) for f in m.wall_feats)
            if not clash:
                m.prims["WALL_SLOTS"].append([wall, u, z0, z1, w])
                placed += 1
            u += pitch
        if placed == 0:
            m.warnings.append(f"vents.walls[{i}]: no slot fits in the region")

    if v.get("lid_over_psu") and hasattr(m, "psu_info"):
        p = m.psu_info
        lid = c["lid"]
        inset = lid["lip_clearance"] + lid["lip_t"] + v["lid_margin"]
        w, pitch = v["lid_slot_w"], v["lid_pitch"]
        # Over the PSU body, skipping its terminal end: nothing should drop
        # through a vent onto mains terminals.
        keep = p["tb_len"] + 10
        x0, y0, x1, y1 = local_box(p["to_g"], keep, 6, p["sx"], p["sy"] - 6)
        x0 = max(x0, inset + lid["slide"], lid["tab_len"] + 4) + w / 2
        x1 = min(x1, m.L - inset) - w / 2
        y0 = max(y0, inset) + w / 2
        y1 = min(y1, m.W - inset) - w / 2
        x = x0
        while x <= x1 + 1e-6 and y1 > y0:
            m.prims["LID_SLOTS"].append([x, y0, x, y1, w])
            x += pitch


# --------------------------------------------------------------------------- entry


def build_model(cfg: dict) -> Model:
    L, W, H = cfg["box"]["inner"]
    m = Model(cfg=cfg, L=L, W=W, H=H)
    place_box(m)
    m.scalars.update(GUIDE_W=0, GUIDE_H=0, GUIDE_T=0, GUIDE_LEN=0)
    place_psu(m)
    place_lv_route(m)
    place_perfboards(m)
    place_panel_parts(m)
    place_wire_holes(m)
    place_mounting(m)
    place_lid_lock(m)   # after the parts: tongues shift to clear their wall features
    place_vents(m)   # last: vents fill whatever wall area the other features left free
    return m
