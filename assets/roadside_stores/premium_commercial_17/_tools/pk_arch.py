"""Premium Commercial 17 - architectural helpers (curtain walls, slabs, walls, stairs, escalators, railings).

All functions take the LOD level L and reduce detail for L1/L2. Outlines are CCW in plan (seen from above), so the
left normal of every segment points INTO the building and the right normal points OUT (towards the road for the
front segment, which runs from -X to +X).
"""
import math
import bmesh
from mathutils import Vector, Matrix
from pk_core import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_quad, bm_hquad, bm_vquad, bm_poly_flat, rect_subtract,
                     seg_frame, bm_slab, mat_by_normal, rotz, arc_pts, poly_rect, R)


def T(x, y, z=0.0, ang=0.0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(ang), 4, 'Z')


def bm_xz_prism(pts, y0, y1):
    """Prism whose profile is given in the local XZ plane (x, z) and extruded along Y from y0 to y1."""
    bm = bm_prism(pts, y0, y1)
    sw = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    bmesh.ops.transform(bm, matrix=sw, verts=bm.verts)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.normal_update()
    return bm


def quad_world(p0, p1, p2, p3):
    return bm_quad(tuple(p0), tuple(p1), tuple(p2), tuple(p3))


def path_segments(pts, closed=False):
    n = len(pts)
    return [(pts[i], pts[(i + 1) % n]) for i in range(n if closed else n - 1)]


# ---------------------------------------------------------------------------
# curtain wall
# ---------------------------------------------------------------------------
def curtain(A, L, pts, z0, z1, module=1.5, transoms=(), mull=0.06, mdepth=0.16, frame='PC_AluSilver', glass='PC_Glass',
            comp='GLASS_SYSTEM', sub='Curtain', doors=(), spandrels=(), closed=False, fins=None, lod2_every=3,
            head=True, sill=True, cap_mat=None, skip_mullions_at=()):
    """Stick curtain wall along a plan polyline.
    transoms: z heights of horizontal bars.  spandrels: [(za, zb, mat)] opaque bands (floor edges).
    doors: [dict(seg=i, u0=.., u1=.., h=.., kind='slide'|'pivot'|'open', leaves=2)] (u along the segment).
    fins: dict(depth=.., t=.., every=1, mat=.., z0=.., z1=..) external vertical fins on the mullion lines."""
    g = A.m(L, comp, sub + 'Glass')
    f = A.m(L, comp, sub + 'Frame')
    zs = sorted(set([z0, z1] + [t for t in transoms if z0 < t < z1] +
                    [v for (a, b, _m) in spandrels for v in (a, b) if z0 < v < z1]))
    rows = list(zip(zs[:-1], zs[1:]))

    def span_mat(za, zb):
        for (a, b, m) in spandrels:
            if za >= a - 1e-4 and zb <= b + 1e-4:
                return m
        return None
    segs = path_segments(pts, closed)
    for si, (p0, p1) in enumerate(segs):
        M, Ls = seg_frame(p0, p1)
        if Ls < 1e-3:
            continue
        n = max(1, int(round(Ls / module)))
        if L == 2:
            n = max(1, n // lod2_every)
        us = [Ls * k / n for k in range(n + 1)]
        segdoors = [d for d in doors if d['seg'] == si] if L < 2 else []

        def in_door(u, z):
            for d in segdoors:
                if d['u0'] - 1e-3 <= u <= d['u1'] + 1e-3 and z < d['h'] - 1e-3:
                    return d
            return None
        # glass + spandrels
        for k in range(n):
            ua, ub = us[k], us[k + 1]
            for (za, zb) in (rows if L < 2 else [(z0, z1)] if not spandrels else rows):
                sm = span_mat(za, zb)
                # cut the cell around doors
                cells = [(ua, za, ub, zb)]
                for d in segdoors:
                    cells = rect_subtract(cells, (d['u0'], z0 - 1, d['u1'], d['h']))
                for (ca, cza, cb, czb) in cells:
                    if sm:
                        f.add(bm_box(ca, -0.02, cza, cb, 0.03, czb), sm, matrix=M)
                    else:
                        g.add(bm_vquad(ca, cb, cza, czb, 0.0, '-Y'), glass, matrix=M)
        if L == 2:
            # mullions only on the coarse grid, flat transoms at spandrel edges
            for k, u in enumerate(us):
                if si > 0 and k == 0 and not closed:
                    continue
                f.add(bm_box(u - mull, -0.03, z0, u + mull, 0.06, z1), frame, matrix=M)
            continue
        # vertical mullions
        for k, u in enumerate(us):
            if k == 0 and si > 0:
                continue                      # shared corner with previous segment
            if k == n and closed and si == len(segs) - 1:
                continue
            if any(abs(u - s) < 1e-3 for s in skip_mullions_at):
                continue
            zcuts = [(z0, z1)]
            for d in segdoors:
                if d['u0'] + 1e-3 < u < d['u1'] - 1e-3:
                    zcuts = [(max(d['h'], z0), z1)]
            for (za, zb) in zcuts:
                if zb - za > 1e-3:
                    f.add(bm_box(u - mull / 2, -mdepth * 0.25, za, u + mull / 2, mdepth * 0.75, zb), frame, matrix=M)
            if fins and (k % fins.get('every', 1) == 0):
                fz0, fz1 = fins.get('z0', z0), fins.get('z1', z1)
                fd, ft = fins['depth'], fins.get('t', 0.08)
                if not (segdoors and any(d['u0'] - 0.3 < u < d['u1'] + 0.3 for d in segdoors) and fins.get('skip_doors', True)):
                    f.add(bm_box(u - ft / 2, -fd, fz0, u + ft / 2, -mdepth * 0.25, fz1, bevel=0.01 if L == 0 else 0),
                          fins.get('mat', frame), matrix=M)
        # transoms (+ head / sill)
        tz = [t for t in transoms if z0 < t < z1]
        if head:
            tz.append(z1 - mull / 2)
        if sill:
            tz.append(z0 + mull / 2)
        for t in tz:
            spans = [(0.0, Ls)]
            for d in segdoors:
                if t < d['h']:
                    spans = [(a, b) for (a0, b0) in spans for (a, b) in ((a0, min(b0, d['u0'])), (max(a0, d['u1']), b0)) if b - a > 1e-3]
            for (a, b) in spans:
                f.add(bm_box(a, -mdepth * 0.2, t - mull / 2, b, mdepth * 0.6, t + mull / 2), frame, matrix=M)
        for d in segdoors:
            door(A, L, M, d, frame, glass, comp, sub)


def door(A, L, M, d, frame, glass, comp, sub):
    g = A.m(L, comp, sub + 'Glass')
    f = A.m(L, comp, sub + 'Frame')
    u0, u1, h = d['u0'], d['u1'], d['h']
    kind = d.get('kind', 'slide')
    fw = 0.09
    f.add(bm_box(u0, -0.12, h - 0.18, u1, 0.18, h), d.get('head_mat', frame), matrix=M)          # head / transom box
    for u in (u0, u1):
        f.add(bm_box(u - fw / 2, -0.12, 0.0, u + fw / 2, 0.18, h), frame, matrix=M)
    if kind == 'open':
        return
    nl = d.get('leaves', 2)
    w = (u1 - u0 - fw) / nl
    for i in range(nl):
        a = u0 + fw / 2 + i * w
        b = a + w
        y = 0.0 if (kind != 'slide' or i % 2 == 0) else 0.06
        g.add(bm_vquad(a + 0.03, b - 0.03, 0.04, h - 0.2, y, '-Y'), glass, matrix=M)
        if L == 0:
            for (aa, bb, za, zb) in ((a, b, 0.0, 0.1), (a, b, h - 0.26, h - 0.18), (a, a + 0.04, 0.0, h - 0.18), (b - 0.04, b, 0.0, h - 0.18)):
                f.add(bm_box(aa, y - 0.025, za, bb, y + 0.025, zb), frame, matrix=M)
            hx = b - 0.18 if i % 2 == 0 else a + 0.18
            f.add(bm_cyl_between((hx, y - 0.09, 0.8), (hx, y - 0.09, 1.9), 0.018, 8), 'PC_Stainless', matrix=M)
            f.add(bm_box(hx - 0.012, y - 0.09, 0.85, hx + 0.012, y, 0.87), 'PC_Stainless', matrix=M)
            f.add(bm_box(hx - 0.012, y - 0.09, 1.83, hx + 0.012, y, 1.85), 'PC_Stainless', matrix=M)


# ---------------------------------------------------------------------------
# slabs, walls, columns, roofs
# ---------------------------------------------------------------------------
def slab(A, L, outer, z_top, t=0.3, holes=(), top='PC_FloorDark', bottom='PC_Ceiling', edge='PC_SlabEdge',
         comp='BUILDING_INTERIOR', sub='Slabs'):
    A.m(L, comp, sub).add(bm_slab(outer, list(holes), z_top - t, z_top), top, mat_fn=mat_by_normal(top, bottom, edge),
                          uv='box')


def wall(acc, p0, p1, z0, z1, t, out_mat, in_mat=None, edge_mat=None, holes=(), outset=0.0):
    """Wall on segment p0->p1, outer face on the segment line (offset by -outset outward), thickness t inward.
    holes: [(u0, u1, za, zb)] openings."""
    in_mat = in_mat or out_mat
    edge_mat = edge_mat or out_mat
    M, Ls = seg_frame(p0, p1)
    rects = [(0.0, z0, Ls, z1)]
    for (u0, u1, za, zb) in holes:
        rects = rect_subtract(rects, (u0, za, u1, zb))
    fn = lambda f: out_mat if f.normal.y < -0.5 else (in_mat if f.normal.y > 0.5 else edge_mat)
    for (a, za, b, zb) in rects:
        acc.add(bm_box(a, -outset, za, b, t - outset, zb), out_mat, matrix=M, mat_fn=fn)


def walls_loop(acc, pts, z0, z1, t, out_mat, in_mat=None, edge_mat=None, holes=None, closed=True):
    holes = holes or {}
    for i, (p0, p1) in enumerate(path_segments(pts, closed)):
        wall(acc, p0, p1, z0, z1, t, out_mat, in_mat, edge_mat, holes.get(i, ()))


def block(acc, pts, z0, z1, side, top=None, bottom=None):
    top = top or side
    acc.add(bm_prism(pts, z0, z1), side, mat_fn=mat_by_normal(top, bottom or side, side))


def box(acc, x0, y0, z0, x1, y1, z1, mat, top=None, bevel=0.0, M=None):
    if top:
        acc.add(bm_box(x0, y0, z0, x1, y1, z1, bevel=bevel), mat, matrix=M, mat_fn=mat_by_normal(top, mat, mat))
    else:
        acc.add(bm_box(x0, y0, z0, x1, y1, z1, bevel=bevel), mat, matrix=M)


def column(acc, L, x, y, z0, z1, r=0.25, mat='PC_PanelWhite', square=False):
    if square:
        acc.add(bm_box(x - r, y - r, z0, x + r, y + r, z1, bevel=0.01 if L == 0 else 0), mat)
    else:
        acc.add(bm_cyl(x, y, z0, z1, r, {0: 20, 1: 10, 2: 6}[L], open_bottom=True), mat)


def parapet(acc, pts, z0, h, t, mat, cap=None, closed=True):
    for (p0, p1) in path_segments(pts, closed):
        wall(acc, p0, p1, z0, z0 + h, t, mat, mat, cap or mat)


def light_grid(acc, L, rect, z, nx, ny, w=1.2, d=0.3, mat='PC_LightPanel', drop=0.02):
    """Recessed linear / square light panels under a ceiling at height z (facing down)."""
    if L == 2:
        return
    x0, y0, x1, y1 = rect
    for i in range(nx):
        for j in range(ny):
            cx = x0 + (x1 - x0) * (i + 0.5) / nx
            cy = y0 + (y1 - y0) * (j + 0.5) / ny
            acc.add(bm_hquad(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2, z - drop, down=True), mat)


def downlights(acc, L, pts, z, r=0.09, mat='PC_LightPanel'):
    if L == 2:
        return
    seg = 10 if L == 0 else 6
    for (x, y) in pts:
        acc.add(bm_cyl(x, y, z - 0.02, z - 0.005, r, seg), mat)


def grid_pts(rect, nx, ny):
    x0, y0, x1, y1 = rect
    return [(x0 + (x1 - x0) * (i + 0.5) / nx, y0 + (y1 - y0) * (j + 0.5) / ny) for i in range(nx) for j in range(ny)]


# ---------------------------------------------------------------------------
# railings, stairs, escalators
# ---------------------------------------------------------------------------
def glass_rail(A, L, pts, z, h=1.05, closed=False, comp='BUILDING_INTERIOR', sub='Rail', glass='PC_GlassRail',
               rail='PC_Stainless', shoe='PC_AluDark', handrail=True):
    g = A.m(L, comp, sub + 'Glass')
    f = A.m(L, comp, sub + 'Frame')
    for (p0, p1) in path_segments(pts, closed):
        M, Ls = seg_frame(p0, p1)
        g.add(bm_vquad(0, Ls, z + 0.08, z + h - 0.04, 0.0, '-Y'), glass, matrix=M)
        if L == 2:
            continue
        f.add(bm_box(0, -0.04, z, Ls, 0.04, z + 0.1), shoe, matrix=M)
        if handrail:
            if L == 0:
                f.add(bm_cyl_between((0, 0, z + h), (Ls, 0, z + h), 0.025, 8), rail, matrix=M)
            else:
                f.add(bm_box(0, -0.02, z + h - 0.04, Ls, 0.02, z + h), rail, matrix=M)


def stair(A, L, x, y, ang, w, z0, z1, kind='floating', tread='PC_FloorOak', struct='PC_SteelDark', comp='BUILDING_INTERIOR',
          sub='Stair', rails=(True, True), landing_len=1.3, glass='PC_GlassRail', rail_mat='PC_Stainless', max_flight=4.6):
    """Straight stair starting at (x, y, z0) running along local +X (rotated by ang).  If the rise exceeds max_flight a
    straight mid landing is inserted.  Returns the horizontal length."""
    acc = A.m(L, comp, sub)
    H = z1 - z0
    n = max(2, int(math.ceil(H / 0.178)))
    rise = H / n
    run = 0.29
    nland = 1 if H > max_flight else 0
    M = T(x, y, 0, ang)
    pts = []           # (x, z) of tread fronts for rails
    xx = 0.0
    zz = z0
    split = n // 2 if nland else None
    for i in range(n):
        ztop = z0 + (i + 1) * rise
        if L == 2:
            break
        th = 0.06 if kind == 'floating' else 0.0
        if kind == 'floating':
            acc.add(bm_box(xx, -w / 2, ztop - th, xx + run + 0.02, w / 2, ztop, bevel=0.005 if L == 0 else 0), tread, matrix=M)
        else:
            acc.add(bm_box(xx, -w / 2, ztop - rise, xx + run + 0.02, w / 2, ztop), tread, matrix=M,
                    mat_fn=mat_by_normal(tread, struct, struct))
        pts.append((xx, ztop))
        xx += run
        if split is not None and i + 1 == split:
            acc.add(bm_box(xx, -w / 2, ztop - 0.08, xx + landing_len, w / 2, ztop), tread, matrix=M,
                    mat_fn=mat_by_normal(tread, struct, struct))
            pts.append((xx + landing_len, ztop))
            xx += landing_len
    total = xx if L < 2 else (n * run + nland * landing_len)
    # stringers / soffit: sloped plates either side (or a solid sloped block at L2)
    if L == 2:
        acc.add(bm_xz_prism([(0, z0), (total, z1), (total, z1 - 0.4), (0, z0 - 0.0)], -w / 2, w / 2), struct, matrix=M)
        return total
    prof = [(0, z0), (0, z0 + 0.25)] + [(px + run, pz + 0.12) for (px, pz) in pts] + [(total, z1 - 0.35)]
    prof = [(0.0, z0), (total, z1 - 0.0), (total, z1 - 0.38), (0.35, z0)]
    for s in (-1, 1):
        y0 = s * w / 2
        acc.add(bm_xz_prism(prof, min(y0, y0 + s * 0.05), max(y0, y0 + s * 0.05)), struct, matrix=M)
    for s, on in zip((-1, 1), rails):
        if not on:
            continue
        yy = s * (w / 2 + 0.07)
        gacc = A.m(L, comp, sub + 'Glass')
        zb0, zb1 = z0 + 0.05, z1 + 0.05
        gacc.add(quad_world((0, yy, zb0), (total, yy, zb1), (total, yy, zb1 + 0.95), (0, yy, zb0 + 0.95)), glass, matrix=M)
        if L == 0:
            acc.add(bm_cyl_between((0, yy, zb0 + 1.0), (total, yy, zb1 + 1.0), 0.024, 8), rail_mat, matrix=M)
    return total


def spiral_stair(A, L, cx, cy, r_in, r_out, z0, z1, a0=0.0, sweep=300.0, tread='PC_PanelWhite', struct='PC_PanelWhite',
                 glass='PC_GlassRail', comp='BUILDING_INTERIOR', sub='SpiralStair'):
    """Sculptural helical stair with a solid white outer stringer band and glass balustrade."""
    acc = A.m(L, comp, sub)
    gacc = A.m(L, comp, sub + 'Glass')
    H = z1 - z0
    n = max(8, int(math.ceil(H / 0.175)))
    da = sweep / n
    rise = H / n
    sub_n = {0: 3, 1: 2, 2: 1}[L]
    if L < 2:
        acc.add(bm_cyl(cx, cy, z0, z1 + 1.0, r_in, 16 if L == 0 else 8), struct)
    for i in range(n):
        aA = math.radians(a0 + i * da); aB = math.radians(a0 + (i + 1) * da)
        zt = z0 + (i + 1) * rise
        if L < 2:
            pts = [(cx + r_in * math.cos(aA), cy + r_in * math.sin(aA))]
            for k in range(sub_n + 1):
                a = aA + (aB - aA) * k / sub_n
                pts.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
            pts.append((cx + r_in * math.cos(aB), cy + r_in * math.sin(aB)))
            acc.add(bm_prism(pts, zt - 0.06, zt), tread)
        # outer stringer band (helical ribbon) and glass
        for k in range(sub_n):
            a = aA + (aB - aA) * k / sub_n; b = aA + (aB - aA) * (k + 1) / sub_n
            za = z0 + i * rise + rise * k / sub_n; zb = z0 + i * rise + rise * (k + 1) / sub_n
            ro = r_out + 0.03
            pa = (cx + ro * math.cos(a), cy + ro * math.sin(a)); pb = (cx + ro * math.cos(b), cy + ro * math.sin(b))
            acc.add(quad_world((pa[0], pa[1], za - 0.45), (pb[0], pb[1], zb - 0.45), (pb[0], pb[1], zb + 0.12), (pa[0], pa[1], za + 0.12)),
                    struct)
            acc.add(quad_world((pb[0], pb[1], zb - 0.45), (pa[0], pa[1], za - 0.45), (pa[0], pa[1], za + 0.12), (pb[0], pb[1], zb + 0.12)),
                    struct)
            if L < 2:
                gacc.add(quad_world((pa[0], pa[1], za + 0.12), (pb[0], pb[1], zb + 0.12), (pb[0], pb[1], zb + 1.0), (pa[0], pa[1], za + 1.0)),
                         glass)
            if L == 0:
                acc.add(bm_cyl_between((pa[0], pa[1], za + 1.0), (pb[0], pb[1], zb + 1.0), 0.022, 6), 'PC_Stainless')


def escalator(A, L, x, y, ang, z0, z1, w=1.0, body='PC_Stainless', steps='PC_SteelDark', glass='PC_GlassRail',
              comp='BUILDING_INTERIOR', sub='Escalator', landing=2.2, handrail='PC_RubberBlack'):
    """Single escalator rising along local +X from (x, y, z0) to z1 at 30 degrees. Returns plan length."""
    acc = A.m(L, comp, sub)
    gacc = A.m(L, comp, sub + 'Glass')
    H = z1 - z0
    Li = H / math.tan(math.radians(30))
    Lt = landing * 2 + Li
    M = T(x, y, 0, ang)
    hw = w / 2 + 0.22
    top = [(0, z0 + 0.12), (landing, z0 + 0.12), (landing + Li, z1 + 0.12), (Lt, z1 + 0.12)]
    prof = top + [(Lt, z1 - 0.6), (landing + Li + 0.6, z1 - 0.6), (landing + 0.6, z0 - 0.0), (0, z0 - 0.0)]
    acc.add(bm_xz_prism(list(reversed(prof)), -hw, hw), body, matrix=M)
    if L < 2:
        # step band (dark) slightly above the truss top
        if L == 0:
            n = int(Li / 0.4)
            for i in range(n):
                xa = landing + Li * i / n; xb = landing + Li * (i + 1) / n
                za = z0 + H * i / n + 0.12; zb = z0 + H * (i + 1) / n + 0.12
                acc.add(bm_box(xa, -w / 2, za, xb, w / 2, zb + 0.02), steps, matrix=M)
        else:
            acc.add(quad_world((landing, -w / 2, z0 + 0.14), (landing + Li, -w / 2, z1 + 0.14), (landing + Li, w / 2, z1 + 0.14),
                               (landing, w / 2, z0 + 0.14)), steps, matrix=M)
        for s in (-1, 1):
            yy = s * (w / 2 + 0.1)
            pts = [(0.5, z0 + 0.12), (landing, z0 + 0.12), (landing + Li, z1 + 0.12), (Lt - 0.5, z1 + 0.12)]
            for (a, b) in zip(pts[:-1], pts[1:]):
                gacc.add(quad_world((a[0], yy, a[1]), (b[0], yy, b[1]), (b[0], yy, b[1] + 0.9), (a[0], yy, a[1] + 0.9)), glass, matrix=M)
                if L == 0:
                    acc.add(bm_cyl_between((a[0], yy, a[1] + 0.95), (b[0], yy, b[1] + 0.95), 0.04, 6), handrail, matrix=M)
            if L == 0:
                # skirt light strip
                acc.add(quad_world((landing, yy * 0.98, z0 + 0.16), (landing + Li, yy * 0.98, z1 + 0.16), (landing + Li, yy * 0.98, z1 + 0.2),
                                   (landing, yy * 0.98, z0 + 0.2)), 'PC_LightStrip', matrix=M)
    return Lt


def roller_door(acc, L, M, u0, u1, h, open_frac=1.0, mat='PC_SteelPaintGrey', frame='PC_AluDark'):
    """Sectional / roller door in a local segment frame M (u along, outward = -Y). open_frac 1 = fully raised."""
    zb = h * open_frac
    acc.add(bm_box(u0 - 0.15, -0.05, 0, u0, 0.25, h + 0.4), frame, matrix=M)
    acc.add(bm_box(u1, -0.05, 0, u1 + 0.15, 0.25, h + 0.4), frame, matrix=M)
    acc.add(bm_box(u0 - 0.15, -0.05, h, u1 + 0.15, 0.6, h + 0.45), frame, matrix=M)         # head box
    if open_frac < 0.999:
        acc.add(bm_box(u0, 0.0, zb, u1, 0.06, h), mat, matrix=M)
        if L == 0:
            k = int((h - zb) / 0.5)
            for i in range(k):
                z = zb + (i + 1) * 0.5
                acc.add(bm_box(u0, -0.01, z - 0.02, u1, 0.0, z), frame, matrix=M)


def slab_r(A, L, rect, holes, z_top, t=0.35, top='PC_FloorDark', bottom='PC_Ceiling', edge='PC_SlabEdge',
           comp='BUILDING_INTERIOR', sub='Slabs'):
    """Rectangular slab minus rectangular holes (atria, stair wells), built from boxes."""
    rects = [rect]
    for h in holes:
        rects = rect_subtract(rects, h)
    acc = A.m(L, comp, sub)
    for r in rects:
        acc.add(bm_box(r[0], r[1], z_top - t, r[2], r[3], z_top), top, mat_fn=mat_by_normal(top, bottom, edge))
    return rects


def ceiling_panels(A, L, rects, z, pitch=(3.0, 2.4), w=1.6, d=0.22, mat='PC_LightPanel', comp='BUILDING_INTERIOR', sub='CeilingLights',
                   lod2_glow=None):
    """Linear light panels under ceilings (rects = ceiling areas). L2 gets one large dim glow plane per rect (proxy)."""
    acc = A.m(L, comp, sub)
    for (x0, y0, x1, y1) in rects:
        if L == 2:
            if lod2_glow:
                acc.add(bm_hquad(x0 + 0.3, y0 + 0.3, x1 - 0.3, y1 - 0.3, z - 0.03, down=True), lod2_glow)
            continue
        nx = max(1, int((x1 - x0) / pitch[0])); ny = max(1, int((y1 - y0) / pitch[1]))
        if L == 1:
            nx = max(1, nx // 2)
        light_grid(acc, L, (x0, y0, x1, y1), z, nx, ny, w if L == 0 else w * 2, d, mat)


def heightfield_slab(acc, xs, yf, yb, ztop, thick, nx, ny, top, bottom, edge):
    """Sculpted roof / canopy: plan region x in xs=(x0,x1), y from yf(x) (front) to yb(x) (back);
    top surface z = ztop(x, y); constant thickness.  Faces top / bottom / 4 edges (watertight)."""
    bm = bmesh.new()
    x0, x1 = xs
    T_, B_ = [], []
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx
        rowt, rowb = [], []
        for j in range(ny + 1):
            y = yf(x) + (yb(x) - yf(x)) * j / ny
            z = ztop(x, y)
            rowt.append(bm.verts.new((x, y, z)))
            rowb.append(bm.verts.new((x, y, z - thick)))
        T_.append(rowt); B_.append(rowb)
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((T_[i][j], T_[i + 1][j], T_[i + 1][j + 1], T_[i][j + 1]))
            bm.faces.new((B_[i][j + 1], B_[i + 1][j + 1], B_[i + 1][j], B_[i][j]))
    for i in range(nx):
        bm.faces.new((B_[i][0], B_[i + 1][0], T_[i + 1][0], T_[i][0]))
        bm.faces.new((T_[i][ny], T_[i + 1][ny], B_[i + 1][ny], B_[i][ny]))
    for j in range(ny):
        bm.faces.new((B_[0][j + 1], B_[0][j], T_[0][j], T_[0][j + 1]))
        bm.faces.new((B_[nx][j], B_[nx][j + 1], T_[nx][j + 1], T_[nx][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    acc.add(bm, top, mat_fn=lambda f: top if f.normal.z > 0.6 else (bottom if f.normal.z < -0.6 else edge))


def bm_yz_prism(pts, x0, x1):
    """Prism whose profile is given in the YZ plane (y, z), extruded along X from x0 to x1."""
    bm = bm_prism(pts, x0, x1)
    cyc = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    bmesh.ops.transform(bm, matrix=cyc, verts=bm.verts)
    bm.normal_update()
    return bm


def ibeam(acc, p0, p1, h=0.6, b=0.3, tw=0.02, tf=0.03, mat='PC_SteelDark', L=0):
    """Steel I-beam between two points at the same height (top of beam at p.z)."""
    M, Ls = seg_frame(p0[:2], p1[:2], 0)
    z = p0[2]
    if L == 0:
        acc.add(bm_box(0, -b / 2, z - tf, Ls, b / 2, z), mat, matrix=M)
        acc.add(bm_box(0, -b / 2, z - h, Ls, b / 2, z - h + tf), mat, matrix=M)
        acc.add(bm_box(0, -tw * 2, z - h + tf, Ls, tw * 2, z - tf), mat, matrix=M)
    else:
        acc.add(bm_box(0, -b / 2, z - h, Ls, b / 2, z), mat, matrix=M)
