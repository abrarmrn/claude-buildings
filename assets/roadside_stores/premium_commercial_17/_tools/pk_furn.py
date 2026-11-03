"""Premium Commercial 17 - furniture, retail fixtures and workshop equipment.

Every function: f(acc, L, x, y, z, ang, ...) - placed at floor height z, rotated by ang degrees about Z.
L2 skips small items entirely (long distance), L1 uses simplified silhouettes.
"""
import math, random
import bmesh
from mathutils import Matrix, Vector
from pk_core import bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_quad, bm_hquad, bm_vquad, bm_sphere, rounded_rect, mat_by_normal
from pk_arch import T, bm_xz_prism, quad_world


def _bv(L, v=0.015):
    return v if L == 0 else 0.0


def _seg(L, a=16, b=8, c=6):
    return {0: a, 1: b, 2: c}[L]


def bm_rbox(x0, y0, z0, x1, y1, z1, r, L):
    """Rounded-corner (plan) box."""
    pts = rounded_rect(x0, y0, x1, y1, min(r, (x1 - x0) / 2 - 1e-3, (y1 - y0) / 2 - 1e-3), 4 if L == 0 else 2)
    return bm_prism(pts, z0, z1)


# ---------------------------------------------------------------------------- seating
def sofa(acc, L, x, y, z, ang, length=2.2, depth=0.9, mat='PC_FabricGrey', leg='PC_SteelDark', arms=True):
    if L == 2:
        return
    M = T(x, y, z, ang)
    hl = length / 2
    acc.add(bm_box(-hl, -depth / 2, 0.12, hl, depth / 2, 0.42, bevel=_bv(L, 0.04)), mat, matrix=M)            # seat base
    acc.add(bm_box(-hl, depth / 2 - 0.22, 0.42, hl, depth / 2, 0.82, bevel=_bv(L, 0.04)), mat, matrix=M)       # back
    if arms:
        for s in (-1, 1):
            acc.add(bm_box(s * hl - (0.2 if s > 0 else 0), -depth / 2, 0.42, s * hl + (0 if s > 0 else 0.2), depth / 2 - 0.22, 0.62,
                           bevel=_bv(L, 0.03)), mat, matrix=M)
    if L == 0:
        for sx in (-hl + 0.1, hl - 0.1):
            for sy in (-depth / 2 + 0.1, depth / 2 - 0.1):
                acc.add(bm_box(sx - 0.02, sy - 0.02, 0, sx + 0.02, sy + 0.02, 0.12), leg, matrix=M)


def armchair(acc, L, x, y, z, ang, mat='PC_Leather', leg='PC_SteelDark'):
    sofa(acc, L, x, y, z, ang, 0.85, 0.82, mat, leg)


def lounge_chair(acc, L, x, y, z, ang, mat='PC_FabricCream', frame='PC_Walnut'):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-0.32, -0.32, 0.36, 0.32, 0.3, 0.46, bevel=_bv(L, 0.03)), mat, matrix=M)
    acc.add(quad_world((-0.32, 0.3, 0.46), (0.32, 0.3, 0.46), (0.32, 0.42, 0.95), (-0.32, 0.42, 0.95)), mat, matrix=M)
    if L == 0:
        for sx in (-0.28, 0.28):
            acc.add(bm_cyl_between((sx, -0.25, 0), (sx, -0.28, 0.36), 0.018, 6), frame, matrix=M)
            acc.add(bm_cyl_between((sx, 0.25, 0), (sx, 0.28, 0.36), 0.018, 6), frame, matrix=M)


def chair(acc, L, x, y, z, ang, mat='PC_SteelDark', seat='PC_FabricGrey', h=0.46):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-0.22, -0.22, h - 0.05, 0.22, 0.22, h, bevel=_bv(L, 0.012)), seat, matrix=M)
    acc.add(bm_box(-0.22, 0.18, h, 0.22, 0.23, h + 0.42, bevel=_bv(L, 0.012)), seat, matrix=M)
    if L == 0:
        for sx in (-0.19, 0.19):
            for sy in (-0.19, 0.19):
                acc.add(bm_box(sx - 0.012, sy - 0.012, 0, sx + 0.012, sy + 0.012, h - 0.05), mat, matrix=M)
    else:
        acc.add(bm_box(-0.2, -0.2, 0, 0.2, 0.2, h - 0.05), mat, matrix=M)


def stool(acc, L, x, y, z, h=0.75, mat='PC_SteelDark', seat='PC_LeatherBlack'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, z, z + h - 0.05, 0.022, 6), mat)
    acc.add(bm_cyl(x, y, z + h - 0.06, z + h, 0.18, _seg(L, 14, 7)), seat)
    if L == 0:
        acc.add(bm_cyl(x, y, z, z + 0.02, 0.2, 12), mat)
        acc.add(bm_cyl(x, y, z + 0.28, z + 0.3, 0.17, 12), mat)


# ---------------------------------------------------------------------------- tables
def table_round(acc, L, x, y, z, r=0.45, h=0.75, top='PC_StoneTop', base='PC_SteelDark'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, z + h - 0.035, z + h, r, _seg(L, 24, 10)), top)
    acc.add(bm_cyl(x, y, z, z + h - 0.035, 0.035, _seg(L, 8, 5), open_bottom=True), base)
    if L == 0:
        acc.add(bm_cyl(x, y, z, z + 0.025, 0.25, 14), base)


def table_rect(acc, L, x, y, z, ang, w=1.6, d=0.9, h=0.75, top='PC_Walnut', leg='PC_SteelDark'):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, -d / 2, h - 0.04, w / 2, d / 2, h, bevel=_bv(L, 0.008)), top, matrix=M)
    for sx in (-w / 2 + 0.08, w / 2 - 0.08):
        if L == 0:
            for sy in (-d / 2 + 0.08, d / 2 - 0.08):
                acc.add(bm_box(sx - 0.025, sy - 0.025, 0, sx + 0.025, sy + 0.025, h - 0.04), leg, matrix=M)
        else:
            acc.add(bm_box(sx - 0.025, -d / 2 + 0.08, 0, sx + 0.025, d / 2 - 0.08, h - 0.04), leg, matrix=M)


def dining_set(acc, L, x, y, z, ang, n_side=2, w=None, d=0.9, top='PC_Walnut', chair_mat='PC_SteelDark', seat='PC_FabricGrey',
               ends=False):
    w = w or max(0.9, n_side * 0.65)
    table_rect(acc, L, x, y, z, ang, w, d, top=top)
    if L == 2:
        return
    M = T(x, y, z, ang)
    for i in range(n_side):
        u = -w / 2 + w * (i + 0.5) / n_side
        for s in (-1, 1):
            p = M @ Vector((u, s * (d / 2 + 0.3), 0))
            chair(acc, L, p.x, p.y, z, ang + (0 if s > 0 else 180), chair_mat, seat)
    if ends:
        for s in (-1, 1):
            p = M @ Vector((s * (w / 2 + 0.32), 0, 0))
            chair(acc, L, p.x, p.y, z, ang + (90 if s < 0 else -90), chair_mat, seat)


def round_set(acc, L, x, y, z, n=4, r=0.5, top='PC_StoneTop', chair_mat='PC_SteelDark', seat='PC_FabricGrey', a0=45):
    table_round(acc, L, x, y, z, r, top=top)
    if L == 2:
        return
    for k in range(n):
        a = math.radians(a0 + 360 * k / n)
        d = r + 0.33
        chair(acc, L, x + d * math.cos(a), y + d * math.sin(a), z, math.degrees(a) - 90, chair_mat, seat)


def booth(acc, L, x, y, z, ang, length=1.8, mat='PC_Leather', base='PC_TimberDark', table_top='PC_StoneTop'):
    """Banquette pair facing each other across a table (local X = length direction)."""
    if L == 2:
        return
    M = T(x, y, z, ang)
    for s in (-1, 1):
        y0 = s * 0.85
        acc.add(bm_box(-length / 2, min(y0, y0 - s * 0.55), 0, length / 2, max(y0, y0 - s * 0.55), 0.44), base, matrix=M,
                mat_fn=mat_by_normal(mat, base, base))
        acc.add(bm_box(-length / 2, min(y0, y0 + s * 0.15), 0, length / 2, max(y0, y0 + s * 0.15), 1.15, bevel=_bv(L, 0.03)), mat, matrix=M)
    table_rect(acc, L, x, y, z, ang, length - 0.2, 0.75, top=table_top)


# ---------------------------------------------------------------------------- counters, desks
def counter(acc, L, x0, y0, x1, y1, z, h=1.05, body='PC_PanelBlack', top='PC_StoneTop', strip=None):
    acc.add(bm_box(x0, y0, z, x1, y1, z + h - 0.04, bevel=_bv(L, 0.01)), body)
    acc.add(bm_box(x0 - 0.03, y0 - 0.03, z + h - 0.04, x1 + 0.03, y1 + 0.03, z + h, bevel=_bv(L, 0.006)), top)
    if strip and L < 2:
        acc.add(bm_box(x0 + 0.02, y0 - 0.012, z + 0.08, x1 - 0.02, y0 - 0.002, z + 0.11), strip)


def reception_desk(acc, L, x, y, z, ang, length=3.0, body='PC_PanelWhite', top='PC_StoneTop', strip='PC_LightStrip', curved=True):
    M = T(x, y, z, ang)
    if curved and L < 2:
        n = 12 if L == 0 else 6
        R0, R1 = length * 0.9, length * 0.9 + 0.65
        pts_o = [(R1 * math.sin(math.radians(-35 + 70 * i / n)), -R1 * math.cos(math.radians(-35 + 70 * i / n)) + R1 * 0.9) for i in range(n + 1)]
        pts_i = [(R0 * math.sin(math.radians(-35 + 70 * i / n)), -R0 * math.cos(math.radians(-35 + 70 * i / n)) + R1 * 0.9) for i in range(n + 1)]
        pts = pts_o + list(reversed(pts_i))
        acc.add(bm_prism(pts, 0, 1.0), body, matrix=M)
        acc.add(bm_prism(pts, 1.0, 1.06), top, matrix=M)
        if strip:
            for (a, b) in zip(pts_o[:-1], pts_o[1:]):
                d = Vector((b[0] - a[0], b[1] - a[1], 0)).normalized()
                nrm = Vector((d.y, -d.x, 0)) * 0.012
                acc.add(quad_world((a[0] + nrm.x, a[1] + nrm.y, 0.05), (b[0] + nrm.x, b[1] + nrm.y, 0.05),
                                   (b[0] + nrm.x, b[1] + nrm.y, 0.09), (a[0] + nrm.x, a[1] + nrm.y, 0.09)), strip, matrix=M)
    else:
        acc.add(bm_box(-length / 2, -0.35, 0, length / 2, 0.35, 1.0), body, matrix=M)
        acc.add(bm_box(-length / 2 - 0.03, -0.38, 1.0, length / 2 + 0.03, 0.38, 1.06), top, matrix=M)
    if L == 0:
        monitor(acc, L, x, y, z + 0.76, ang)


def monitor(acc, L, x, y, z, ang, w=0.55):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, 0.05, 0.12, w / 2, 0.08, 0.45), 'PC_DeviceBlack', matrix=M)
    acc.add(bm_box(-0.02, 0.08, 0, 0.02, 0.1, 0.14), 'PC_DeviceSilver', matrix=M)


def desk(acc, L, x, y, z, ang, w=1.6, d=0.8, top='PC_WhiteGloss', chairs=2, chair_mat='PC_LeatherBlack'):
    table_rect(acc, L, x, y, z, ang, w, d, top=top, leg='PC_AluSilver')
    if L == 2:
        return
    monitor(acc, L, x, y, z + 0.75, ang + 180, 0.5)
    M = T(x, y, z, ang)
    p = M @ Vector((0, 0.75, 0))
    chair(acc, L, p.x, p.y, z, ang + 180, 'PC_AluSilver', chair_mat)
    for i in range(chairs):
        p = M @ Vector((-0.4 + 0.8 * i, -0.75, 0))
        chair(acc, L, p.x, p.y, z, ang, 'PC_AluSilver', chair_mat)


def coffee_table(acc, L, x, y, z, r=0.45, h=0.38, top='PC_StoneTop', base='PC_Brass'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, z + h - 0.04, z + h, r, _seg(L, 22, 10)), top)
    acc.add(bm_cyl(x, y, z, z + h - 0.04, r * 0.55, _seg(L, 16, 8), open_bottom=True), base)


def lounge_group(acc, L, x, y, z, ang, sofa_mat='PC_FabricGrey', chair_mat='PC_Leather'):
    M = T(x, y, z, ang)
    p = M @ Vector((0, 1.1, 0)); sofa(acc, L, p.x, p.y, z, ang + 180, 2.2, 0.9, sofa_mat)
    for s in (-1, 1):
        p = M @ Vector((s * 1.45, 0.0, 0)); armchair(acc, L, p.x, p.y, z, ang + (90 if s > 0 else -90), chair_mat)
    coffee_table(acc, L, x, y, z, 0.5)


# ---------------------------------------------------------------------------- lighting fixtures (emissive)
def pendant(acc, L, x, y, z_ceiling, drop=1.2, shape='globe', r=0.22, mat='PC_LampGlobe', cord='PC_AluBlack'):
    if L == 2:
        return
    zb = z_ceiling - drop
    if L == 0:
        acc.add(bm_cyl(x, y, zb + r * 0.8, z_ceiling, 0.006, 4), cord)
    if shape == 'globe':
        acc.add(bm_sphere((x, y, zb), r, 2 if L == 0 else 1), mat)
    elif shape == 'cone':
        acc.add(bm_cyl(x, y, zb - r * 0.4, zb + r * 0.8, r, _seg(L, 16, 8), r2=0.05, caps=True), cord)
        acc.add(bm_cyl(x, y, zb - r * 0.42, zb - r * 0.38, r * 0.92, _seg(L, 16, 8)), mat)
    elif shape == 'cyl':
        acc.add(bm_cyl(x, y, zb - r * 1.6, zb + r * 0.4, r * 0.5, _seg(L, 12, 6)), mat)
    elif shape == 'lantern':
        acc.add(bm_box(x - r, y - r, zb - r * 1.5, x + r, y + r, zb + r * 1.5), mat)
        if L == 0:
            for (a, b) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                acc.add(bm_box(x + a * r - 0.012, y + b * r - 0.012, zb - r * 1.6, x + a * r + 0.012, y + b * r + 0.012, zb + r * 1.6), cord)
            acc.add(bm_box(x - r * 1.1, y - r * 1.1, zb + r * 1.5, x + r * 1.1, y + r * 1.1, zb + r * 1.62), cord)
    elif shape == 'disc':
        acc.add(bm_cyl(x, y, zb, zb + 0.05, r, _seg(L, 24, 10)), cord)
        acc.add(bm_cyl(x, y, zb - 0.004, zb, r * 0.95, _seg(L, 24, 10)), mat)


def ring_light(acc, L, x, y, z, R=1.2, t=0.05, mat='PC_LightStrip', seg=None):
    """Suspended circular LED ring (chandelier-like), made of short boxes."""
    if L == 2:
        return
    n = seg or (32 if L == 0 else 14)
    for i in range(n):
        a = 2 * math.pi * i / n; b = 2 * math.pi * (i + 1) / n
        p0 = (x + R * math.cos(a), y + R * math.sin(a)); p1 = (x + R * math.cos(b), y + R * math.sin(b))
        acc.add(quad_world((p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z + t), (p0[0], p0[1], z + t)), mat)
        acc.add(quad_world((p1[0], p1[1], z), (p0[0], p0[1], z), (p0[0], p0[1], z + t), (p1[0], p1[1], z + t)), mat)


def linear_pendant(acc, L, x, y, z, ang, length=2.4, mat='PC_LightStrip', body='PC_AluBlack', drop=0.0):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-length / 2, -0.04, 0.0, length / 2, 0.04, 0.07), body, matrix=M)
    acc.add(bm_hquad(-length / 2 + 0.03, -0.03, length / 2 - 0.03, 0.03, -0.002, down=True), mat, matrix=M)


# ---------------------------------------------------------------------------- showroom display
def turntable(acc, L, x, y, z, r=3.0, h=0.18, top='PC_FloorMarble', edge='PC_AluSilver', led='PC_LightStrip'):
    seg = _seg(L, 48, 20, 10)
    acc.add(bm_cyl(x, y, z, z + h, r, seg), top, mat_fn=mat_by_normal(top, edge, edge))
    if L < 2 and led:
        acc.add(bm_cyl(x, y, z, z + 0.035, r + 0.03, seg, caps=False), led)


def plinth(acc, L, x0, y0, x1, y1, z, h=0.25, top='PC_WhiteGloss', edge='PC_AluSilver', led='PC_LightStrip'):
    acc.add(bm_box(x0, y0, z, x1, y1, z + h), top, mat_fn=mat_by_normal(top, edge, edge))
    if L < 2 and led:
        acc.add(bm_box(x0 - 0.02, y0 - 0.02, z, x1 + 0.02, y1 + 0.02, z + 0.03, open_bottom=True), led)


def stanchion_sign(acc, L, x, y, z, ang, screen='PC_Screen'):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-0.2, -0.15, 0, 0.2, 0.15, 0.03), 'PC_AluDark', matrix=M)
    acc.add(bm_box(-0.03, -0.03, 0.03, 0.03, 0.03, 1.0), 'PC_AluDark', matrix=M)
    acc.add(bm_box(-0.25, -0.03, 1.0, 0.25, 0.0, 1.35), 'PC_AluDark', matrix=M)
    acc.add(bm_vquad(-0.23, 0.23, 1.02, 1.33, -0.035, '-Y'), screen, matrix=M, uv='fit', cell=(0.0, 0.0, 0.25, 0.5))


# ---------------------------------------------------------------------------- electronics retail
def screen_quad(acc, M, x0, x1, z0, z1, y=0.0, mat='PC_Screen', tile=0):
    u = (tile % 4) * 0.25; v = (tile // 4) * 0.5
    acc.add(bm_vquad(x0, x1, z0, z1, y, '-Y'), mat, matrix=M, uv='fit', cell=(u, 1 - v - 0.5, u + 0.25, 1 - v))


def tv_wall(acc, L, x, y, z, ang, cols=4, rows=2, w=1.65, h=0.95, gap=0.12, z0=0.9, frame='PC_DeviceBlack', mat='PC_Screen', seed=0):
    """Wall of large screens; the screens face local -Y."""
    M = T(x, y, z, ang)
    W = cols * w + (cols - 1) * gap
    rng = random.Random(seed)
    for i in range(cols):
        for j in range(rows):
            a = -W / 2 + i * (w + gap); zz = z0 + j * (h + gap)
            if L < 2:
                acc.add(bm_box(a, 0.0, zz, a + w, 0.05, zz + h), frame, matrix=M)
            screen_quad(acc, M, a + 0.015, a + w - 0.015, zz + 0.015, zz + h - 0.015, -0.002, mat, rng.randrange(8))


def phone(acc, L, M, u, v, zt, ang=0.0, tile=0, flat=False, mat='PC_Screen'):
    """Smartphone on a stand (or flat) at local (u, v) on a table surface zt in frame M."""
    if L != 0:
        return
    Mp = M @ T(u, v, zt, ang)
    if flat:
        acc.add(bm_box(-0.038, -0.08, 0, 0.038, 0.08, 0.009), 'PC_DeviceBlack', matrix=Mp)
        acc.add(bm_hquad(-0.034, -0.076, 0.034, 0.076, 0.0095), mat, matrix=Mp, uv='fit',
                cell=((tile % 4) * 0.25, 0.5 - (tile // 4) * 0.5, (tile % 4) * 0.25 + 0.25, 1.0 - (tile // 4) * 0.5))
    else:
        tilt = Matrix.Rotation(math.radians(-18), 4, 'X')
        acc.add(bm_box(-0.02, -0.03, 0, 0.02, 0.03, 0.05), 'PC_DeviceSilver', matrix=Mp)
        acc.add(bm_box(-0.038, -0.006, 0.03, 0.038, 0.002, 0.19), 'PC_DeviceBlack', matrix=Mp @ tilt)
        acc.add(bm_vquad(-0.034, 0.034, 0.034, 0.186, -0.0065, '-Y'), mat, matrix=Mp @ tilt, uv='fit',
                cell=((tile % 4) * 0.25, 0.5 - (tile // 4) * 0.5, (tile % 4) * 0.25 + 0.25, 1.0 - (tile // 4) * 0.5))


def laptop(acc, L, M, u, v, zt, ang=0.0, tile=3, body='PC_DeviceSilver', mat='PC_Screen'):
    if L == 2:
        return
    Mp = M @ T(u, v, zt, ang)
    acc.add(bm_box(-0.16, -0.11, 0, 0.16, 0.11, 0.015), body, matrix=Mp)
    tilt = Matrix.Translation((0, 0.11, 0.015)) @ Matrix.Rotation(math.radians(-15), 4, 'X')
    acc.add(bm_box(-0.16, -0.008, 0, 0.16, 0.0, 0.21), body, matrix=Mp @ tilt)
    acc.add(bm_vquad(-0.15, 0.15, 0.01, 0.2, -0.009, '-Y'), mat, matrix=Mp @ tilt, uv='fit',
            cell=((tile % 4) * 0.25, 0.5 - (tile // 4) * 0.5, (tile % 4) * 0.25 + 0.25, 1.0 - (tile // 4) * 0.5))


def tablet(acc, L, M, u, v, zt, ang=0.0, tile=5, mat='PC_Screen'):
    if L != 0:
        return
    Mp = M @ T(u, v, zt, ang)
    tilt = Matrix.Rotation(math.radians(-25), 4, 'X')
    acc.add(bm_box(-0.03, -0.04, 0, 0.03, 0.04, 0.04), 'PC_DeviceSilver', matrix=Mp)
    acc.add(bm_box(-0.125, -0.005, 0.03, 0.125, 0.002, 0.21), 'PC_DeviceBlack', matrix=Mp @ tilt)
    acc.add(bm_vquad(-0.118, 0.118, 0.037, 0.203, -0.0055, '-Y'), mat, matrix=Mp @ tilt, uv='fit',
            cell=((tile % 4) * 0.25, 0.5 - (tile // 4) * 0.5, (tile % 4) * 0.25 + 0.25, 1.0 - (tile // 4) * 0.5))


def product_table(acc, L, x, y, z, ang, w=3.2, d=1.1, h=0.9, top='PC_WoodLight', base='PC_WoodLight', items='phones', seed=1,
                  round_r=0.0):
    """Long retail table with devices; items: phones | laptops | tablets | mixed | watches | none."""
    M = T(x, y, z, ang)
    if round_r > 0:
        acc.add(bm_rbox(-w / 2, -d / 2, h - 0.05, w / 2, d / 2, h, round_r, L), top, matrix=M)
        acc.add(bm_rbox(-w / 2 + 0.25, -d / 2 + 0.2, 0, w / 2 - 0.25, d / 2 - 0.2, h - 0.05, round_r * 0.6, L), base, matrix=M)
    else:
        acc.add(bm_box(-w / 2, -d / 2, h - 0.05, w / 2, d / 2, h, bevel=_bv(L, 0.01)), top, matrix=M)
        if L == 2:
            acc.add(bm_box(-w / 2 + 0.2, -d / 2 + 0.2, 0, w / 2 - 0.2, d / 2 - 0.2, h - 0.05), base, matrix=M)
        else:
            for s in (-1, 1):
                acc.add(bm_box(s * (w / 2 - 0.25) - 0.04, -d / 2 + 0.12, 0, s * (w / 2 - 0.25) + 0.04, d / 2 - 0.12, h - 0.05), base, matrix=M)
    if L != 0 or items == 'none':
        if L == 1 and items != 'none':
            for i in range(int(w / 0.6)):
                u = -w / 2 + 0.3 + i * 0.6
                acc.add(bm_box(u - 0.15, -0.1, h, u + 0.15, 0.1, h + 0.06), 'PC_DeviceBlack', matrix=M)
        return
    rng = random.Random(seed)
    n = int((w - 0.2) / 0.42)
    for i in range(n):
        u = -w / 2 + 0.31 + i * 0.42
        for s in (-1, 1):
            v = s * (d / 2 - 0.22)
            a = 0 if s < 0 else 180
            kind = items if items != 'mixed' else rng.choice(['phones', 'phones', 'tablets', 'laptops', 'watches'])
            if kind == 'phones':
                phone(acc, L, M, u, v, h, a, rng.randrange(8))
            elif kind == 'tablets':
                tablet(acc, L, M, u, v, h, a, rng.randrange(8))
            elif kind == 'laptops' and i % 2 == 0:
                laptop(acc, L, M, u + 0.2, v * 0.85, h, a, rng.randrange(8))
            elif kind == 'watches':
                Mp = M @ T(u, v, h, a)
                acc.add(bm_box(-0.022, -0.026, 0, 0.022, 0.026, 0.012), 'PC_DeviceBlack', matrix=Mp)
                acc.add(bm_box(-0.012, -0.08, 0, 0.012, 0.08, 0.004), 'PC_RubberBlack', matrix=Mp)


def wall_shelf(acc, L, x, y, z, ang, w=3.0, h=2.4, levels=4, body='PC_WhiteGloss', back='PC_WoodLight', items='boxes', seed=2,
               light='PC_LightStrip'):
    """Wall display unit (shelves face local -Y)."""
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, 0.0, 0, w / 2, 0.06, h), back, matrix=M)
    if L == 2:
        return
    acc.add(bm_box(-w / 2, -0.45, 0, w / 2, 0.0, 0.25), body, matrix=M)
    rng = random.Random(seed)
    for k in range(levels):
        zz = 0.6 + k * (h - 0.8) / max(1, levels - 1)
        acc.add(bm_box(-w / 2, -0.35, zz - 0.025, w / 2, 0.0, zz), body, matrix=M)
        if light and L == 0:
            acc.add(bm_hquad(-w / 2 + 0.05, -0.3, w / 2 - 0.05, -0.27, zz - 0.026, down=True), light, matrix=M)
        if L == 0 and items:
            u = -w / 2 + 0.15
            while u < w / 2 - 0.25:
                bw = rng.uniform(0.12, 0.3); bh = rng.uniform(0.12, 0.3)
                col = rng.choice(['PC_PlasticWhite', 'PC_DeviceBlack', 'PC_PlasticGrey', 'PC_WhiteGloss'])
                acc.add(bm_box(u, -0.28, zz, u + bw, -0.08, zz + bh), col, matrix=M)
                u += bw + rng.uniform(0.06, 0.2)


def island(acc, L, x, y, z, r=1.2, h=0.95, top='PC_WhiteGloss', body='PC_WhiteGloss', items='phones', seed=3, led='PC_LightStrip'):
    """Round product island."""
    seg = _seg(L, 32, 14, 8)
    acc.add(bm_cyl(x, y, z, z + h - 0.04, r * 0.85, seg, open_bottom=True), body)
    acc.add(bm_cyl(x, y, z + h - 0.04, z + h, r, seg), top)
    if L < 2 and led:
        acc.add(bm_cyl(x, y, z + 0.02, z + 0.05, r * 0.86, seg, caps=False), led)
    if L != 0:
        return
    rng = random.Random(seed)
    n = int(2 * math.pi * r * 0.8 / 0.38)
    M = T(x, y, z, 0)
    for k in range(n):
        a = 2 * math.pi * k / n
        u, v = (r - 0.2) * math.cos(a), (r - 0.2) * math.sin(a)
        ang = math.degrees(a) + 90
        if items == 'phones':
            phone(acc, L, M, u, v, h, ang, rng.randrange(8))
        elif items == 'watches':
            Mp = M @ T(u, v, h, ang)
            acc.add(bm_box(-0.022, -0.026, 0, 0.022, 0.026, 0.012), 'PC_DeviceBlack', matrix=Mp)


def kiosk(acc, L, x, y, z, ang, w=2.4, d=1.2, body='PC_WhiteGloss', top='PC_StoneTop', screen=True):
    M = T(x, y, z, ang)
    acc.add(bm_rbox(-w / 2, -d / 2, 0, w / 2, d / 2, 1.0, 0.4, L), body, matrix=M)
    acc.add(bm_rbox(-w / 2 - 0.05, -d / 2 - 0.05, 1.0, w / 2 + 0.05, d / 2 + 0.05, 1.06, 0.42, L), top, matrix=M)
    if screen and L < 2:
        acc.add(bm_box(-0.03, -0.03, 1.06, 0.03, 0.03, 2.1), 'PC_AluDark', matrix=M)
        acc.add(bm_box(-0.5, -0.04, 2.1, 0.5, 0.04, 2.7), 'PC_DeviceBlack', matrix=M)
        screen_quad(acc, M, -0.47, 0.47, 2.13, 2.67, -0.042, 'PC_Screen', 1)


def mannequin(acc, L, x, y, z, ang=0, body='PC_WhiteGloss', cloth='PC_FabricNavy'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, z, z + 0.02, 0.18, 10), 'PC_AluDark')
    acc.add(bm_cyl(x, y, z + 0.02, z + 0.95, 0.015, 6), 'PC_AluDark')
    acc.add(bm_cyl(x, y, z + 0.8, z + 1.45, 0.17, _seg(L, 12, 6), r2=0.2), cloth)
    acc.add(bm_cyl(x, y, z + 1.45, z + 1.52, 0.06, 8), body)
    acc.add(bm_sphere((x, y, z + 1.64), 0.1, 1), body)


def clothes_rail(acc, L, x, y, z, ang, w=1.6, seed=4):
    if L == 2:
        return
    M = T(x, y, z, ang)
    for s in (-1, 1):
        acc.add(bm_box(s * w / 2 - 0.02, -0.02, 0, s * w / 2 + 0.02, 0.02, 1.55), 'PC_Brass', matrix=M)
    acc.add(bm_cyl_between((-w / 2, 0, 1.52), (w / 2, 0, 1.52), 0.012, 6), 'PC_Brass', matrix=M)
    if L == 0:
        rng = random.Random(seed)
        cols = ['PC_FabricCream', 'PC_FabricNavy', 'PC_FabricRust', 'PC_FabricTeal', 'PC_FabricGrey', 'PC_LeatherBlack']
        n = int(w / 0.09)
        for i in range(n):
            u = -w / 2 + 0.08 + i * (w - 0.16) / max(1, n - 1)
            acc.add(bm_box(u - 0.02, -0.24, 0.75 + rng.uniform(-0.1, 0.1), u + 0.02, 0.24, 1.45), rng.choice(cols), matrix=M)


def display_case(acc, L, x0, y0, x1, y1, z, h=1.25, body='PC_PanelBlack', glass='PC_GlassClear', light='PC_LightWarm', goods=None, seed=5):
    """Glass-topped counter / pastry cabinet."""
    acc.add(bm_box(x0, y0, z, x1, y1, z + 0.85), body)
    if L == 2:
        return
    g = goods or 'PC_Pastry'
    acc.add(bm_hquad(x0 + 0.03, y0 + 0.03, x1 - 0.03, y1 - 0.03, z + 0.86), light)
    if L == 0:
        rng = random.Random(seed)
        nx = int((x1 - x0) / 0.22)
        for i in range(nx):
            for j in range(2):
                cx = x0 + 0.15 + i * (x1 - x0 - 0.3) / max(1, nx - 1)
                cy = y0 + (y1 - y0) * (0.3 + 0.4 * j)
                acc.add(bm_cyl(cx, cy, z + 0.87, z + 0.87 + rng.uniform(0.04, 0.09), 0.07, 8), g)
    acc.add(bm_box(x0, y0, z + h - 0.03, x1, y1, z + h), body)
    for (a, b, c, d) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        acc.add(quad_world((a, b, z + 0.85), (c, d, z + 0.85), (c, d, z + h - 0.03), (a, b, z + h - 0.03)), glass)


def espresso_machine(acc, L, x, y, z, ang, body='PC_Stainless', accent='PC_BlackGloss'):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-0.45, -0.28, 0, 0.45, 0.28, 0.48, bevel=_bv(L, 0.02)), body, matrix=M)
    acc.add(bm_box(-0.45, -0.3, 0.3, 0.45, -0.27, 0.42), accent, matrix=M)
    if L == 0:
        for u in (-0.25, 0.0, 0.25):
            acc.add(bm_box(u - 0.035, -0.4, 0.24, u + 0.035, -0.28, 0.29), 'PC_Chrome', matrix=M)
        acc.add(bm_cyl(0.6, 0.0, 0, 0.42, 0.09, 10), body, matrix=M)
        acc.add(bm_cyl(0.6, 0.0, 0.42, 0.6, 0.11, 10, r2=0.06), 'PC_GlassSatin', matrix=M)


def bottle_shelf(acc, L, x, y, z, ang, w=2.4, rows=3, seed=6, back='PC_TimberDark', light='PC_LightWarm'):
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, 0.0, 0.0, w / 2, 0.05, 2.2), back, matrix=M)
    if L == 2:
        return
    rng = random.Random(seed)
    for k in range(rows):
        zz = 1.1 + k * 0.38
        acc.add(bm_box(-w / 2, -0.25, zz - 0.02, w / 2, 0.0, zz), 'PC_Brass', matrix=M)
        if L == 0:
            acc.add(bm_hquad(-w / 2, -0.2, w / 2, -0.15, zz - 0.021, down=True), light, matrix=M)
            u = -w / 2 + 0.08
            while u < w / 2 - 0.08:
                acc.add(bm_cyl(u, -0.12, zz, zz + rng.uniform(0.18, 0.3), 0.035, 6), rng.choice(['PC_GlassBlue', 'PC_BlackGloss', 'PC_Copper', 'PC_GlassSatin']), matrix=M)
                u += 0.1


# ---------------------------------------------------------------------------- workshop / car wash equipment
def tool_cabinet(acc, L, x, y, z, ang, w=1.4, h=1.0, d=0.5, mat='PC_ToolRed', top_box=True):
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, -d / 2, 0.08, w / 2, d / 2, h, bevel=_bv(L, 0.01)), mat, matrix=M)
    if L == 2:
        return
    acc.add(bm_box(-w / 2 - 0.01, -d / 2 - 0.01, h, w / 2 + 0.01, d / 2 + 0.01, h + 0.03), 'PC_RubberBlack', matrix=M)
    if top_box:
        acc.add(bm_box(-w / 2 + 0.05, -d / 2 + 0.05, h + 0.03, w / 2 - 0.05, d / 2 - 0.02, h + 0.45), mat, matrix=M)
    if L == 0:
        for k in range(6):
            zz = 0.18 + k * (h - 0.25) / 6
            acc.add(bm_box(-w / 2 + 0.05, -d / 2 - 0.012, zz, w / 2 - 0.05, -d / 2, zz + 0.012), 'PC_Stainless', matrix=M)
        for sx in (-w / 2 + 0.08, w / 2 - 0.08):
            acc.add(bm_cyl(sx, -d / 2 + 0.08, 0, 0.08, 0.04, 8), 'PC_RubberBlack', matrix=M)


def workbench(acc, L, x, y, z, ang, w=2.4, d=0.75, top='PC_Walnut', frame='PC_SteelPaintGrey', pegboard=True):
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, -d / 2, 0.86, w / 2, d / 2, 0.92), top, matrix=M)
    if L == 2:
        return
    for sx in (-w / 2 + 0.05, w / 2 - 0.05):
        acc.add(bm_box(sx - 0.03, -d / 2 + 0.03, 0, sx + 0.03, d / 2 - 0.03, 0.86), frame, matrix=M)
    acc.add(bm_box(-w / 2, -d / 2 + 0.05, 0.12, w / 2, d / 2 - 0.05, 0.15), frame, matrix=M)
    if pegboard:
        acc.add(bm_box(-w / 2, d / 2 - 0.03, 0.92, w / 2, d / 2, 2.0), 'PC_SteelPaintGrey', matrix=M)
        if L == 0:
            rng = random.Random(int(x * 10 + y))
            for i in range(14):
                u = rng.uniform(-w / 2 + 0.1, w / 2 - 0.1); zz = rng.uniform(1.1, 1.85)
                acc.add(bm_box(u - 0.015, d / 2 - 0.06, zz - 0.12, u + 0.015, d / 2 - 0.03, zz + 0.04), rng.choice(['PC_ToolRed', 'PC_Chrome', 'PC_ToolBlack']), matrix=M)


def lift_2post(acc, L, x, y, z, ang, raise_h=1.6, span=3.2, mat='PC_LiftBlue', arms='PC_SteelDark'):
    """Two-post vehicle lift; posts at local +/-Y (car runs along local X). Returns the lifted car height."""
    M = T(x, y, z, ang)
    for s in (-1, 1):
        yy = s * span / 2
        acc.add(bm_box(-0.25, yy - 0.2, 0, 0.25, yy + 0.2, 3.6, bevel=_bv(L, 0.01)), mat, matrix=M)
        acc.add(bm_box(-0.35, yy - 0.3, 0, 0.35, yy + 0.3, 0.02), mat, matrix=M)
        if L < 2:
            acc.add(bm_box(-0.15, yy - s * 0.15 - 0.1, raise_h - 0.25, 0.15, yy - s * 0.15 + 0.1, raise_h + 0.05), arms, matrix=M)
            for sx in (-1, 1):
                acc.add(bm_box(min(0, sx * 1.35), min(yy, yy - s * 1.1), raise_h - 0.12, max(0, sx * 1.35), max(yy, yy - s * 1.1), raise_h - 0.02),
                        arms, matrix=M)
    if L < 2:
        acc.add(bm_box(-0.18, -span / 2, 3.6, 0.18, span / 2, 3.8), mat, matrix=M)
    return raise_h


def lift_4post(acc, L, x, y, z, ang, raise_h=1.2, length=5.2, width=2.6, mat='PC_LiftYellow', deck='PC_SteelPaintGrey'):
    M = T(x, y, z, ang)
    for sx in (-1, 1):
        for sy in (-1, 1):
            acc.add(bm_box(sx * length / 2 - 0.15, sy * width / 2 - 0.15, 0, sx * length / 2 + 0.15, sy * width / 2 + 0.15, 2.4), mat, matrix=M)
    for sy in (-0.75, 0.75):
        acc.add(bm_box(-length / 2 + 0.2, sy - 0.3, raise_h - 0.15, length / 2 - 0.2, sy + 0.3, raise_h), deck, matrix=M)
    for sx in (-1, 1):
        acc.add(bm_box(sx * length / 2 - 0.2, -width / 2, raise_h - 0.25, sx * length / 2 + 0.2, width / 2, raise_h - 0.05), mat, matrix=M)
    return raise_h


def wash_gantry(acc, L, x, y, z, ang, width=3.6, h=3.2, frame='PC_Stainless', brush='PC_BrushBlue', brush2='PC_BrushRed'):
    """Roll-over / tunnel wash portal with two vertical brushes and one top brush (car runs along local X)."""
    M = T(x, y, z, ang)
    for s in (-1, 1):
        acc.add(bm_box(-0.3, s * width / 2 - 0.15, 0, 0.3, s * width / 2 + 0.15, h), frame, matrix=M)
        acc.add(bm_box(-0.45, s * width / 2 - 0.25, 0, 0.45, s * width / 2 + 0.25, 0.05), frame, matrix=M)
    acc.add(bm_box(-0.35, -width / 2 - 0.15, h, 0.35, width / 2 + 0.15, h + 0.45), frame, matrix=M)
    if L == 2:
        return
    seg = _seg(L, 16, 8)
    for s in (-1, 1):
        acc.add(bm_cyl(0.0, s * (width / 2 - 0.55), 0.15, h - 0.2, 0.42, seg), brush, matrix=M)
        if L == 0:
            acc.add(bm_cyl(0.0, s * (width / 2 - 0.55), h - 0.2, h, 0.06, 8), frame, matrix=M)
    acc.add(bm_cyl_between((0.0, -width / 2 + 0.25, h - 0.55), (0.0, width / 2 - 0.25, h - 0.55), 0.35, seg), brush2, matrix=M)


def wash_arch(acc, L, x, y, z, ang, width=3.6, h=3.0, mat='PC_PlasticWhite', nozzle_led='PC_LEDCyan'):
    """Spray / foam arch (thin portal with nozzle bars and LED edge)."""
    M = T(x, y, z, ang)
    for s in (-1, 1):
        acc.add(bm_box(-0.08, s * width / 2 - 0.08, 0, 0.08, s * width / 2 + 0.08, h), mat, matrix=M)
    acc.add(bm_box(-0.08, -width / 2 - 0.08, h, 0.08, width / 2 + 0.08, h + 0.16), mat, matrix=M)
    if L < 2:
        acc.add(bm_box(-0.09, -width / 2 + 0.1, h - 0.02, 0.09, width / 2 - 0.1, h + 0.0), nozzle_led, matrix=M)
        for s in (-1, 1):
            acc.add(bm_box(-0.09, s * width / 2 - s * 0.09 - 0.01, 0.3, 0.09, s * width / 2 - s * 0.09 + 0.01, h - 0.1), nozzle_led, matrix=M)


def blower(acc, L, x, y, z, ang, width=3.4, h=2.9, mat='PC_PanelSilver'):
    M = T(x, y, z, ang)
    for s in (-1, 1):
        acc.add(bm_box(-0.25, s * width / 2 - 0.25, 0, 0.25, s * width / 2 + 0.25, h), mat, matrix=M)
    acc.add(bm_box(-0.4, -width / 2 - 0.25, h, 0.4, width / 2 + 0.25, h + 0.6), mat, matrix=M)
    if L == 0:
        for u in (-0.9, 0.0, 0.9):
            acc.add(bm_box(-0.2, u - 0.3, h - 0.15, 0.2, u + 0.3, h), 'PC_RubberBlack', matrix=M)


def drain_grate(acc, L, x0, y0, x1, y1, z, along='x'):
    acc.add(bm_box(x0, y0, z - 0.004, x1, y1, z + 0.004), 'PC_Grate')
    if L != 0:
        return
    if along == 'x':
        n = int((x1 - x0) / 0.06)
        for i in range(n):
            xx = x0 + (i + 0.5) * (x1 - x0) / n
            acc.add(bm_box(xx - 0.008, y0 + 0.01, z + 0.004, xx + 0.008, y1 - 0.01, z + 0.012), 'PC_Stainless')
    else:
        n = int((y1 - y0) / 0.06)
        for i in range(n):
            yy = y0 + (i + 0.5) * (y1 - y0) / n
            acc.add(bm_box(x0 + 0.01, yy - 0.008, z + 0.004, x1 - 0.01, yy + 0.008, z + 0.012), 'PC_Stainless')


def tyre_stack(acc, L, x, y, z, n=4, r=0.34, w=0.24):
    if L == 2:
        return
    for k in range(n):
        acc.add(bm_cyl(x, y, z + k * w, z + (k + 1) * w - 0.01, r, _seg(L, 16, 8)), 'PC_Tyre')
        if L == 0:
            acc.add(bm_cyl(x, y, z + (k + 1) * w - 0.009, z + (k + 1) * w - 0.008, r * 0.62, 12), 'PC_RubberBlack')


def tyre_rack(acc, L, x, y, z, ang, w=3.0, levels=3):
    M = T(x, y, z, ang)
    for s in (-1, 1):
        acc.add(bm_box(s * w / 2 - 0.04, -0.3, 0, s * w / 2 + 0.04, 0.3, 2.2), 'PC_SteelPaintGrey', matrix=M)
    if L == 2:
        return
    for k in range(levels):
        zz = 0.25 + k * 0.7
        acc.add(bm_box(-w / 2, -0.3, zz, w / 2, 0.3, zz + 0.04), 'PC_SteelPaintGrey', matrix=M)
        n = int(w / 0.28)
        for i in range(n):
            u = -w / 2 + 0.16 + i * 0.28
            acc.add(bm_cyl_between((u - 0.11, 0, zz + 0.36), (u + 0.11, 0, zz + 0.36), 0.32, _seg(L, 14, 6)), 'PC_Tyre', matrix=M)


def vinyl_rack(acc, L, x, y, z, ang, w=2.4, seed=7):
    """Wall rack of vinyl wrap rolls in many colours (customisation shop)."""
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, 0.0, 0, w / 2, 0.05, 2.4), 'PC_SteelDark', matrix=M)
    if L == 2:
        return
    rng = random.Random(seed)
    cols = ['PC_LEDMagenta', 'PC_CarPaintBlue', 'PC_CarPaintRed', 'PC_CarPaintYellow', 'PC_CarPaintGreen', 'PC_CarWrapMatte',
            'PC_CarPaintBlack', 'PC_CarPaintWhite', 'PC_CarPaintOrange', 'PC_Copper', 'PC_Chrome']
    for k in range(4):
        zz = 0.4 + k * 0.52
        n = int(w / 0.17)
        for i in range(n):
            u = -w / 2 + 0.1 + i * 0.17
            acc.add(bm_cyl(u, -0.16, zz - 0.07, zz + 0.07, 0.075, _seg(L, 10, 6)), rng.choice(cols), matrix=M)


def plotter(acc, L, x, y, z, ang, w=2.0):
    M = T(x, y, z, ang)
    acc.add(bm_box(-w / 2, -0.35, 0.75, w / 2, 0.35, 1.15, bevel=_bv(L, 0.02)), 'PC_PlasticWhite', matrix=M)
    if L == 2:
        return
    for s in (-1, 1):
        acc.add(bm_box(s * (w / 2 - 0.1) - 0.04, -0.3, 0, s * (w / 2 - 0.1) + 0.04, 0.3, 0.75), 'PC_SteelDark', matrix=M)
    acc.add(bm_box(-w / 2 + 0.1, -0.36, 0.95, w / 2 - 0.1, -0.35, 1.0), 'PC_LEDCyan', matrix=M)


def compressor(acc, L, x, y, z, ang):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_cyl_between((-0.6, 0, 0.35), (0.6, 0, 0.35), 0.3, _seg(L, 14, 8)), 'PC_ToolRed', matrix=M)
    acc.add(bm_box(-0.4, -0.25, 0.65, 0.4, 0.25, 1.05), 'PC_ToolBlack', matrix=M)


def ceiling_strip_lights(acc, L, rect, z, n, along='x', w=0.18, mat='PC_LightCool', body='PC_AluDark', length=None):
    """Industrial linear high-bay fixtures hanging at z."""
    if L == 2:
        return
    x0, y0, x1, y1 = rect
    for i in range(n):
        if along == 'x':
            yy = y0 + (y1 - y0) * (i + 0.5) / n
            a, b = (x0, x1) if length is None else ((x0 + x1) / 2 - length / 2, (x0 + x1) / 2 + length / 2)
            acc.add(bm_box(a, yy - w / 2 - 0.03, z, b, yy + w / 2 + 0.03, z + 0.08), body)
            acc.add(bm_hquad(a + 0.02, yy - w / 2, b - 0.02, yy + w / 2, z - 0.002, down=True), mat)
        else:
            xx = x0 + (x1 - x0) * (i + 0.5) / n
            a, b = (y0, y1) if length is None else ((y0 + y1) / 2 - length / 2, (y0 + y1) / 2 + length / 2)
            acc.add(bm_box(xx - w / 2 - 0.03, a, z, xx + w / 2 + 0.03, b, z + 0.08), body)
            acc.add(bm_hquad(xx - w / 2, a + 0.02, xx + w / 2, b - 0.02, z - 0.002, down=True), mat)


def bench(acc, L, x, y, z, ang, length=2.0, seat='PC_Walnut', base='PC_StoneTop'):
    if L == 2:
        return
    M = T(x, y, z, ang)
    acc.add(bm_box(-length / 2, -0.22, 0.38, length / 2, 0.22, 0.46, bevel=_bv(L, 0.01)), seat, matrix=M)
    for s in (-1, 1):
        acc.add(bm_box(s * (length / 2 - 0.25) - 0.15, -0.2, 0, s * (length / 2 - 0.25) + 0.15, 0.2, 0.38), base, matrix=M)


def empty_planter(acc, L, x0, y0, x1, y1, z, h=0.55, mat='PC_StoneTop', fill='PC_RoofGravel'):
    """Architectural planter box left EMPTY (landscaping will be added later from the user's own library)."""
    acc.add(bm_box(x0, y0, z, x1, y1, z + h, bevel=_bv(L, 0.015)), mat)
    if L < 2:
        acc.add(bm_hquad(x0 + 0.06, y0 + 0.06, x1 - 0.06, y1 - 0.06, z + h + 0.002), fill)


def bollard(acc, L, x, y, z=0.0, h=0.9, r=0.1, mat='PC_AluDark', led='PC_LightStrip'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, z, z + h, r, _seg(L, 12, 6)), mat)
    if led and L == 0:
        acc.add(bm_cyl(x, y, z + h - 0.12, z + h - 0.06, r + 0.003, 12, caps=False), led)
