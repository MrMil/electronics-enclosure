// Parametric electronics enclosure — geometry only.
//
// This file defines modules and draws nothing by itself. Every dimension comes
// from globals written by the Python builder into enclosures/<name>/build/params.scad;
// the wrapper files next to it `include` this library, then the params, then call
// one of the part modules at the bottom. Layout decisions (where things go, which
// bolt length, vent placement) are made in Python — see docs/enclosure/README.md.
//
// Frame: interior corner at the origin. x = length, y = width, z = up,
// z = 0 is the top of the floor. Walls and floor are outside the interior box
// [0,L] x [0,W] x [0,H]. Units: mm.

$fn = 48;
EPS = 0.01;
STANDOFF_FOOT = 3;   // radial (= vertical) size of the 45° foot under each standoff

// ---------------------------------------------------------------- frames

// Local wall frame: local x runs along the wall (u), local z is up, local y
// points outward through the wall; local y = 0 is the interior face.
module wall_frame(wall, u, z) {
    if (wall == "front")      multmatrix([[1,0,0,u],[0,-1,0,0],[0,0,1,z],[0,0,0,1]]) children();
    else if (wall == "back")  multmatrix([[1,0,0,u],[0,1,0,W],[0,0,1,z],[0,0,0,1]]) children();
    else if (wall == "left")  multmatrix([[0,-1,0,0],[1,0,0,u],[0,0,1,z],[0,0,0,1]]) children();
    else if (wall == "right") multmatrix([[0,1,0,L],[1,0,0,u],[0,0,1,z],[0,0,0,1]]) children();
    else assert(false, str("unknown wall ", wall));
}

// Extrude a 2D (u,z) shape along local y, from y0 (inside) to y1 (outside).
module wall_prism(y0, y1) {
    translate([0, y1, 0]) rotate([90, 0, 0]) linear_extrude(y1 - y0) children();
}

// ---------------------------------------------------------------- 2D helpers

module rrect2d(w, h, r) {
    if (r <= 0) square([w, h], center = true);
    else offset(r = r) square([max(w - 2*r, EPS), max(h - 2*r, EPS)], center = true);
}

// Rectangle w x h (centred) with a 45° pointed roof on top, for openings in
// vertical walls: the roof prints without support or bridging. `rise` is how
// far the roof goes above the rectangle: w/2 is a full point; less leaves a
// flat top (a bridge) of width w - 2*rise, used where a flange hides the roof.
module pointed2d(w, h, r, rise) {
    rrect2d(w, h, r);
    // the roof starts below the rounded corners so no ledge is left under it
    if (rise > 0) polygon([[-w/2, h/2 - r - EPS], [w/2, h/2 - r - EPS], [w/2, h/2],
                           [w/2 - rise, h/2 + rise], [-w/2 + rise, h/2 + rise], [-w/2, h/2]]);
}

// Teardrop for horizontal holes in vertical walls: the 45° point on top prints
// without supports. trunc > 0 cuts the point flat at that height above center;
// trunc < 0 gives a plain circle (a hole whose point would show past its flange).
module teardrop2d(d, trunc = 0) {
  if (trunc < 0) circle(d = d); else {
    r = d / 2;
    tip = r * sqrt(2);
    intersection() {
        hull() {
            circle(d = d);
            translate([0, r * sqrt(2) / 2]) rotate(45) square(r, center = true);
        }
        if (trunc > 0) translate([-d, -d]) square([2*d, d + trunc]);
        else translate([-d, -d]) square([2*d, d + tip + 1]);
    }
  }
}

module stadium2d(len, d) {   // slot along x, center-to-center length `len`
    hull() { translate([-len/2, 0]) circle(d = d); translate([len/2, 0]) circle(d = d); }
}

// Outside footprint shared by base and lid.
module outline2d() {
    translate([-WALL, -WALL]) offset(r = OUTER_R) offset(delta = -OUTER_R)
        square([L + 2*WALL, W + 2*WALL]);
}

// Extrude a 2D (n, z) profile along local x (= u) from u0 to u1, in a wall
// frame. n is the outward distance from the wall's inner face.
module along_wall(u0, u1) {
    translate([u0, 0, 0]) rotate([90, 0, 90]) linear_extrude(u1 - u0) children();
}

// ---------------------------------------------------------------- printability

// Counterbore / nut pocket opened from the underside of a bed-side face, with
// the two sacrificial bridge layers that let it print without supports:
// layer 1 opens a band as wide as the hole across the whole pocket (so the
// first bridges only span the pocket width), layer 2 is the hole itself.
// `pocket` is the 2D pocket outline, `hole_len` / `hole_d` the hole stadium.
module bridged_pocket(z0, depth, hole_len, hole_d) {
    translate([0, 0, z0 - 1]) linear_extrude(depth + 1) children();
    translate([0, 0, z0 + depth - EPS]) linear_extrude(LAYER + EPS)
        intersection() {
            children();
            square([hole_len + hole_d, 100], center = true);
        }
}

// ---------------------------------------------------------------- base parts

// Lid-lock ledges: the slot each lid tongue slides into. Its ceiling slopes 45°
// down toward the outside so it prints without support and matches the tongue.
module lock_cutters() {
    for (k = LOCK_SLOTS) wall_frame(k[0], 0, 0) along_wall(k[1], k[2])
        polygon([[-1, k[3]], [WALL + 1, k[3]], [WALL + 1, k[4] - (WALL + 1)], [-1, k[4] + 1]]);
}

module tab(t) {   // t = [wall, u, len, width, thick, hole_d, csk_d, rib_h, rib_t]
    len = t[2]; w = t[3]; th = t[4]; hd = t[5]; csk = t[6]; rh = t[7]; rt = t[8];
    hole_y = WALL + len * 0.55;
    wall_frame(t[0], t[1], 0) difference() {
        union() {
            // plate, rounded at the free end
            translate([0, 0, -FLOOR]) linear_extrude(th) hull() {
                translate([-w/2, WALL - 1]) square([w, 1]);
                translate([0, WALL + len - w/2]) circle(d = w);
            }
            // side ribs: triangular gussets, printable as 45°-or-shallower slopes
            for (sx = [-1, 1]) translate([sx * (w/2 - rt/2), 0, 0])
                rotate([90, 0, 90]) translate([0, 0, -rt/2]) linear_extrude(rt)
                    polygon([[WALL - 1, -FLOOR + th], [WALL - 1, -FLOOR + th + rh],
                             [WALL + rh, -FLOOR + th]]);
        }
        translate([0, hole_y, -FLOOR - 1]) cylinder(d = hd, h = th + 2);
        if (csk > hd)
            translate([0, hole_y, -FLOOR + th - (csk - hd) / 2 + EPS])
                cylinder(d1 = hd, d2 = csk, h = (csk - hd) / 2);
    }
}

module tie_anchor(a) {   // a = [x, y, angle]: zip-tie tunnel parallel to local x
    // the tunnel has a pointed roof, so the anchor prints without bridging
    translate([a[0], a[1], 0]) rotate(a[2]) difference() {
        translate([-TIE_LEN/2, -TIE_W/2 - 2, -EPS]) cube([TIE_LEN, TIE_W + 4, TIE_H + TIE_W/2 + 1.6]);
        translate([-TIE_LEN/2 - 1, 0, 0]) rotate([90, 0, 90]) linear_extrude(TIE_LEN + 2)
            translate([0, TIE_H/2 - 0.5]) pointed2d(TIE_W, TIE_H + 1, 0, TIE_W/2);
    }
}

// Wire loop for the low-voltage route, leaning on a wall: the wall is one side
// of the tunnel; a leg GUIDE_W out stands on the floor and a 45° roof rises from
// it back into the wall. Prints in place without support; wires run along the wall.
module wire_guide(g) {   // g = [wall, u]
    w = GUIDE_W; t = GUIDE_T; h = GUIDE_H;
    wall_frame(g[0], 0, 0) along_wall(g[1] - GUIDE_LEN / 2, g[1] + GUIDE_LEN / 2) difference() {
        // n < 0 is inside the box; the roof's outer face is t thick, measured square to it
        polygon([[-w - t, 0], [0.5, 0], [0.5, h + w + t * 1.414 + 0.5], [-w - t, h + t * 0.414]]);
        polygon([[-w, -1], [0, -1], [0, h + w], [-w, h]]);
    }
}

// Zip-tie lock lug on the wall: flat top just under the lid's lug, 45° below.
module wall_lug(l) {     // l = [wall, u]
    top = H - 0.4;
    wall_frame(l[0], l[1], 0) difference() {
        along_wall(-LUG_W / 2, LUG_W / 2) polygon([
            [WALL - 1, top], [WALL + LUG_REACH, top], [WALL + LUG_REACH, top - LUG_T],
            [WALL - 1, top - LUG_T - LUG_REACH - 1]]);
        translate([0, WALL + LUG_REACH / 2, top - LUG_T - LUG_REACH - 2])
            cylinder(d = LUG_HOLE, h = LUG_T + LUG_REACH + 4);
    }
}

module floor_additions() {
    for (p = PADS) translate([p[0], p[1], -EPS]) cube([p[2] - p[0], p[3] - p[1], p[4] + EPS]);
    // Standoffs get a 45° foot: the nut pocket below takes almost the whole
    // floor thickness, so the foot is what ties the standoff to the floor.
    for (s = STANDOFFS) translate([s[0], s[1], -EPS]) {
        cylinder(d = s[2], h = s[3] + EPS);
        cylinder(d1 = s[2] + 2 * STANDOFF_FOOT, d2 = s[2], h = min(STANDOFF_FOOT, s[3]) + EPS);
    }
    for (a = TIE_ANCHORS) tie_anchor(a);
    for (g = WIRE_GUIDES) wire_guide(g);
}

module floor_cutters() {
    // bolts entering from below (PSU): slotted through-hole + recessed head
    for (b = FLOOR_BOLTS) translate([b[0], b[1], 0]) rotate(b[5]) {
        translate([0, 0, -FLOOR - 1]) linear_extrude(b[3] + FLOOR + 2) stadium2d(b[2], M3_CLEAR);
        bridged_pocket(-FLOOR, b[4], b[2], M3_CLEAR) stadium2d(b[2], HEAD_CB_D);
    }
    // standoffs: through-hole + hex nut pocket opened from below
    for (s = STANDOFFS) translate([s[0], s[1], 0]) {
        translate([0, 0, -FLOOR - 1]) cylinder(d = M3_CLEAR, h = s[3] + FLOOR + 2);
        bridged_pocket(-FLOOR, NUT_POCKET_H, 0, M3_CLEAR)
            circle(r = NUT_POCKET_AF / 2 / cos(30), $fn = 6);
    }
    // wire exits through the floor
    for (f = FLOOR_SLOTS) translate([f[0], f[1], -FLOOR - 1]) rotate(f[5])
        linear_extrude(FLOOR + 2) rrect2d(f[2], f[3], f[4]);
    // holes for mounting the enclosure through its floor, countersunk from inside
    for (m = FLOOR_MOUNTS) translate([m[0], m[1], 0]) {
        translate([0, 0, -FLOOR - 1]) cylinder(d = m[2], h = FLOOR + 2);
        if (m[3] > m[2]) translate([0, 0, -(m[3] - m[2]) / 2 + EPS])
            cylinder(d1 = m[2], d2 = m[3], h = (m[3] - m[2]) / 2);
    }
}

module wall_cutters() {
    for (r = WALL_RECTS) wall_frame(r[0], r[1], r[2])
        wall_prism(-1, WALL + 1) pointed2d(r[3], r[4], r[5], r[6]);
    for (c = WALL_ROUNDS) wall_frame(c[0], c[1], c[2])
        wall_prism(-1, WALL + 1) teardrop2d(c[3], c[4]);
    // vent slots: vertical, pointed top ending at z1
    for (s = WALL_SLOTS) wall_frame(s[0], s[1], s[2])
        wall_prism(-1, WALL + 1) translate([0, (s[3] - s[2] - s[4]/2) / 2])
            pointed2d(s[4], s[3] - s[2] - s[4]/2, 0, s[4]/2);
    // thin the wall from inside where a panel part needs a thinner panel
    for (p = WALL_POCKETS) wall_frame(p[0], p[1], p[2])
        wall_prism(-1, p[5]) rrect2d(p[3], p[4], 0);
}

module base() {
    difference() {
        union() {
            difference() {
                translate([0, 0, -FLOOR]) linear_extrude(H + FLOOR) outline2d();
                cube([L, W, H + 1]);
            }
            floor_additions();
            for (t = TABS) tab(t);
            for (l = LOCK_LUGS) wall_lug(l);
        }
        lock_cutters();
        floor_cutters();
        wall_cutters();
    }
}

// ---------------------------------------------------------------- lid

// Drop-and-slide lid, modelled in its locked position. It is lowered in
// LOCK_SLIDE further toward the left wall, then slid +x: tongues on the lip
// go under the wall ledges and the tooth under the flexible tab drops inside
// the left wall. See docs/enclosure/lid_closure.md.
module lid_plate2d() {
    difference() {
        union() {
            outline2d();
            // finger pull: the tab's tip sticks out past the left wall
            translate([-WALL - TAB_PULL, TAB_U - TAB_W / 2]) square([TAB_PULL + 1, TAB_W]);
            // zip-tie lock lugs, over the wall lugs when closed
            for (l = LOCK_LUGS) wall_frame(l[0], l[1], 0) projection()
                translate([-LUG_W / 2, WALL - 1, 0]) cube([LUG_W, LUG_REACH + 1, 1]);
        }
        for (l = LOCK_LUGS) wall_frame(l[0], l[1], 0) projection()
            translate([0, WALL + LUG_REACH / 2, 0]) cylinder(d = LUG_HOLE, h = 1);
        // two slits free the tab; round ends spread the bending stress
        for (sg = [-1, 1]) {
            y = TAB_U + sg * (TAB_W / 2 + TAB_SLIT / 2);
            translate([-WALL - TAB_PULL - 1, y - TAB_SLIT / 2]) square([TAB_LEN + WALL + TAB_PULL + 1, TAB_SLIT]);
            translate([TAB_LEN, y]) circle(d = TAB_SLIT * 1.6);
        }
    }
}

module lid_lip() {
    x0 = LIP_CLR + LOCK_SLIDE;   // the lip stops short of the left wall by the slide distance
    translate([0, 0, H - LIP_H]) linear_extrude(LIP_H + EPS) difference() {
        translate([x0, LIP_CLR]) square([L - LIP_CLR - x0, W - 2*LIP_CLR]);
        translate([x0 + LIP_T, LIP_CLR + LIP_T]) square([L - 2*LIP_CLR - x0 - 2*LIP_T, W - 2*(LIP_CLR + LIP_T)]);
        for (g = LIP_GAPS) translate([x0 - 1, g[0]]) square([LIP_T + 2, g[1] - g[0]]);
    }
    // tongues: [wall, u, width, z bottom, z top at the wall's inner face, reach]
    for (t = LID_TONGUES) wall_frame(t[0], 0, 0) along_wall(t[1] - t[2] / 2, t[1] + t[2] / 2)
        polygon([[-LIP_CLR - 1, t[3]], [t[5], t[3]], [t[5], t[4] - t[5]], [-LIP_CLR - 1, t[4] + LIP_CLR + 1]]);
}

module lid_tooth() {
    // vertical face toward the left wall holds the lid; 45° ramp on the far
    // side lets the tooth ride up over the wall while sliding in
    x0 = 0.4;
    translate([0, TAB_U + TOOTH_W / 2, 0]) rotate([90, 0, 0]) linear_extrude(TOOTH_W)
        polygon([[x0, H - TOOTH_H], [x0 + TOOTH_LEN - TOOTH_H, H - TOOTH_H], [x0 + TOOTH_LEN, H + EPS], [x0, H + EPS]]);
}

module lid() {
    difference() {
        union() {
            translate([0, 0, H]) linear_extrude(LID_T) lid_plate2d();
            lid_lip();
            lid_tooth();
        }
        for (s = LID_SLOTS) translate([0, 0, H - 1]) linear_extrude(LID_T + 2)
            hull() { translate([s[0], s[1]]) circle(d = s[4]); translate([s[2], s[3]]) circle(d = s[4]); }
    }
}

// ---------------------------------------------------------------- preview

module ghosts() {
    for (g = GHOSTS) color(g[6], g[7]) translate([g[0], g[1], g[2]]) cube([g[3], g[4], g[5]]);
}

// ---------------------------------------------------------------- parts

// Print orientation: base floor-down, lid top-face-down (lip pointing up).
module part_base_print() { translate([0, 0, FLOOR]) base(); }
module part_lid_print()  { translate([0, 0, H + LID_T]) rotate([180, 0, 0]) lid(); }
// Both parts on one bed, lid offset by PLATE_LID (computed in Python).
module part_plate() { part_base_print(); translate([PLATE_LID[0], PLATE_LID[1], 0]) part_lid_print(); }

// Previews: closed box, and open box with the parts it holds as coloured blocks.
module part_assembly() { color("SteelBlue") base(); color("LightSteelBlue") lid(); }
module part_interior() { color("SteelBlue") base(); ghosts(); }
