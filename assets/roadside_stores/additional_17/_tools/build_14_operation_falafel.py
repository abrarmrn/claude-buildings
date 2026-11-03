"""ASSET 14 - Operation Falafel (modern Middle Eastern fast-casual restaurant; boulevard podium retail).

Plot 40 m x 32 m, road side faces -Y, origin = plot centre at finished ground.
Massing: sandy rendered volume with three arched openings, diamond mashrabiya lattice band, merlon parapet,
star-tile band, wind-tower (badgir) element carrying Arabic + Latin signage, pergola terrace with lanterns.
Branding is a simplified recreation (generic sans + Arabic text), not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-20.0, -16.0, 20.0, 16.0)
BX0, BY0, BX1, BY1 = -7.0, 1.0, 7.0, 11.0
H = 7.0
TX0, TX1, TH = -7.0, -4.2, 10.0                       # wind tower
OPEN = [(-2.3, 2.0, 0.8, 2.0), (1.6, 3.4, 0.15, 2.4), (5.4, 2.0, 0.8, 2.0)]
GROUND_TOP = 4.35
TERRACE = (-13.0, -6.5, 12.0, BY0)
ENTRY, EXIT = (-19.0, -14.0), (14.0, 19.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-20.0, -14.0, -19.2, 16.0), (19.2, -14.0, 20.0, 16.0), (-19.0, 14.5, 19.0, 16.0)]

defmat('OF_Sand', '#d8c3a0', rough=0.85)
defmat('OF_SandLit', '#d8c3a0', rough=0.8, emit='#ffcf90', es=0.12)
defmat('OF_Terracotta', '#b0633c', rough=0.7)
defmat('OF_Olive', '#4a5527', rough=0.55)
defmat('OF_OliveLit', '#4a5527', rough=0.5, emit='#7f9a3a', es=0.6)
defmat('OF_Orange', '#ee7d1a', rough=0.35)
defmat('OF_OrangeLit', '#ee7d1a', rough=0.3, emit='#ff9a2e', es=2.4)
defmat('OF_Brass', '#b88a3a', rough=0.3, metal=1.0)
defmat('OF_Lantern', '#ffffff', rough=0.3, emit='#ffb860', es=6.0)
defmat('OF_Glow', '#ffd9a0', rough=0.5, emit='#ffb55c', es=1.6)
defmat('OF_Wood', '#6e4a2c', rough=0.55)
defmat('OF_Menu', '#14100c', rough=0.25, emit='#ffd9a0', es=0.9)


def lattice(acc, L, x0, x1, z0, z1, y, mat='OF_Wood', back='OF_Glow'):
    """Diamond mashrabiya panel on the plane y (facing -Y): glowing back panel + diamond ring cells."""
    acc.add(bm_vquad(x0, x1, z0, z1, y + 0.02), back)
    if L == 2:
        return
    s = 0.34 if L == 0 else 0.7
    b = 0.05 if L == 0 else 0.09
    nx = int((x1 - x0) / (s * 2)) + 1
    nz = int((z1 - z0) / s) + 1
    for i in range(nx):
        for j in range(nz):
            cx = x0 + s + i * 2 * s + (s if j % 2 else 0.0)
            cz = z0 + s * 0.5 + j * s
            if cx + s > x1 + 1e-6 or cz + s * 0.5 > z1 + 1e-6 or cx - s < x0 - 1e-6:
                continue
            outer = [(s, 0), (0, s * 0.5), (-s, 0), (0, -s * 0.5)]
            inner = [(s - b * 1.6, 0), (0, s * 0.5 - b), (-(s - b * 1.6), 0), (0, -(s * 0.5 - b))]
            acc.add(bm_ring_prism(outer, inner, 0.0, 0.05), mat, matrix=place('-Y', (cx, y, cz)))


def star8(acc, L, M, r=0.28, depth=0.04, mat='OF_Terracotta'):
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.62
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    acc.add(bm_prism_local(pts, depth), mat, matrix=M)


def lantern(acc, L, x, y, z, r=0.14, drop=0.5):
    if L > 1:
        return
    acc.add(bm_cyl_between((x, y, z), (x, y, z + drop), 0.01, 3, caps=False), 'RS_PlasticBlack')
    acc.add(bm_sphere((x, y, z), r, 1 if L else 2, (1, 1, 1.3)), 'OF_Lantern')
    if L == 0:
        acc.add(bm_cyl(x, y, z + r * 1.3, z + r * 1.5, r * 0.5, 8), 'OF_Brass')


def of_sign(acc, L, M, size=0.9, depth=0.07):
    txt(acc, L, 'OPERATION', M @ Matrix.Translation((0, size * 0.55, 0)), size * 0.75, depth, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.1)
    txt(acc, L, 'FALAFEL', M @ Matrix.Translation((0, -size * 0.45, 0)), size, depth, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.12)


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (11.0, -15.4, 13.6, -14.0)]
    site_ground(A, L, PLOT, holes, [TERRACE], BEDS, paver_h=0.12, mat_paved='RS_Paver')
    land = A.m(L, 'Landscape')
    palms(A, L, [(18.5, -13.0), (-18.5, 8.0), (18.5, 8.0), (9.0, 13.5), (-9.0, 13.5)], 260)
    for i in range(14):
        x = -12.0 + i * 1.7
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 14.0 or ENTRY[0] - 1 < x < ENTRY[1] + 1:
            continue
        R.grass_clump(land, L, x, -15.0, 0.9, seed=i)
    entry_exit(A, L, PLOT, -16.5, 16.5, depth=1.8)
    cars = {6: ('RS_CarBlack', 'sedan')}
    parking_row(A, L, -9.0, -12.5, -7.5, 7, 2.6, cars)
    disabled_bay(A, L, -9.0 + 2.6 * 7 + 1.3, -12.5, -7.5)
    fur = A.m(L, 'Furniture')
    pergola(fur, L, -11.5, -5.5, -3.5, -0.5, 3.0, mat='OF_Wood')
    for (x, y) in ((-10.0, -4.0), (-8.0, -2.0), (-6.0, -4.0), (-4.5, -2.0), (-9.0, -0.8)):
        lantern(fur, L, x, y, 2.5, 0.15, 0.5)
    rng = random.Random(5)
    for i, (x, y) in enumerate(((-9.5, -3.0), (-6.0, -2.4), (3.5, -3.4), (7.0, -2.6), (10.0, -4.0))):
        cafe_set(fur, L, x, y, 3 if i % 2 else 4, ang=rng.uniform(0, 90), table_mat='OF_Brass', chair_mat='OF_Wood', seat_mat='OF_Terracotta', r=0.36)
    for (x0, y0, x1, y1) in ((-13.0, -6.5, -4.0, -5.9), (2.0, -6.5, 12.0, -5.9)):
        planter(fur, L, x0, y0, x1, y1, 0.6, 'OF_Sand', 'RS_Foliage', seed=int(x0))
    bench(fur, L, 9.5, -0.2, 2.4, 0, 'OF_Wood')
    bin_(fur, L, 3.0, -5.3, 'OF_Olive')
    if L < 2:
        for x in (-12.5, 11.5):
            fur.add(bm_cyl(x, -1.0, 0.1, 0.55, 0.12, 10), 'OF_Lantern')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.025 if L == 0 else 0.0
    t = 0.35
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'OF_Sand', t=t, holes=[], roof_mat='OF_Sand', roof_t=0.4, skip=('front',), rooftop=True)
    # ground-floor wall with three arched openings, upper band solid
    arch_wall(b, L, BX0, BX1, BY0, t, 0.15, GROUND_TOP, OPEN, 'OF_Sand', bevel=bv)
    b.add(bm_box(BX0, BY0, GROUND_TOP, BX1, BY0 + t, H - 0.4, bevel=bv), 'OF_Sand')
    # tower (badgir) with vertical slots and a stepped cap, merlon parapet along the roofline
    b.add(bm_box(TX0 - 0.2, BY0 - 0.6, 0.0, TX1 + 0.2, BY0 + 3.6, TH, bevel=bv, open_bottom=True), 'OF_SandLit')
    b.add(bm_box(TX0 - 0.35, BY0 - 0.75, TH, TX1 + 0.35, BY0 + 3.75, TH + 0.3, bevel=bv), 'OF_Terracotta')
    b.add(bm_box(TX0 + 0.5, BY0 - 0.4, TH + 0.3, TX1 - 0.5, BY0 + 3.4, TH + 0.9, bevel=bv), 'OF_Sand')
    if L < 2:
        for k in range(4):
            x = TX0 + 0.1 + k * 0.7
            b.add(bm_box(x, BY0 - 0.64, 7.4, x + 0.3, BY0 - 0.6, 9.5), 'OF_Glow')
    if L == 0:
        n = int((BX1 - TX1) / 1.0)
        for i in range(n):
            x = TX1 + 0.3 + i * 1.0
            b.add(bm_box(x, BY0, H, x + 0.5, BY0 + 0.3, H + 0.5, open_bottom=True), 'OF_Sand')
    # star-tile band + terracotta cornice
    b.add(bm_box(TX1 + 0.2, BY0 - 0.12, GROUND_TOP, BX1, BY0, GROUND_TOP + 0.12, bevel=bv), 'OF_Terracotta')
    if L < 2:
        for i in range(int((BX1 - TX1 - 0.8) / 0.9)):
            star8(b, L, place('-Y', (TX1 + 0.9 + i * 0.9, BY0, GROUND_TOP + 0.45)), 0.3, 0.05)
    # mashrabiya band above the stars
    lattice(b, L, TX1 + 0.3, -1.4, GROUND_TOP + 0.7, H - 0.5, BY0 - 0.02)
    lattice(b, L, 4.6, BX1 - 0.3, GROUND_TOP + 0.7, H - 0.5, BY0 - 0.02)
    # openings: arched glass + frames, lantern lights in the main arch
    wy = BY0 + 0.12
    for xc, w, zb, zs in OPEN:
        arch_window(A, L, xc, w, zb, zs, wy, 'OF_Brass', 0.07, 2 if w > 3 else 1)
    # main entrance doors inside the central arch
    fr = A.m(L, 'Frames')
    if L < 2:
        for sx in (-0.45, 0.45):
            fr.add(bm_box(1.6 + sx - 0.04, wy - 0.12, 0.15, 1.6 + sx + 0.04, wy + 0.05, 2.35), 'OF_Brass')
        fr.add(bm_box(0.2, wy - 0.12, 2.3, 3.0, wy + 0.05, 2.36), 'OF_Brass')
        for x in (-4.6, 5.0):
            lantern(b, L, 1.6 + (x < 0) * -1.4 + (x > 0) * 1.4, BY0 - 0.5, 3.6, 0.13, 0.4)
    s = A.m(L, 'Signage')
    # tower signage: Arabic on top, Latin below (both back-lit)
    txt(s, L, arabic('عملية فلافل'), place('-Y', ((TX0 + TX1) / 2, BY0 - 0.62, 6.6)), 0.62, 0.05, 'arabic', 'OF_OrangeLit', 'OF_Orange', min_size_lod2=0.3)
    txt(s, L, 'OPERATION', place('-Y', ((TX0 + TX1) / 2, BY0 - 0.62, 5.5)), 0.4, 0.05, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.0, min_size_lod2=0.3)
    txt(s, L, 'FALAFEL', place('-Y', ((TX0 + TX1) / 2, BY0 - 0.62, 4.8)), 0.5, 0.05, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.04, min_size_lod2=0.3)
    # long facade fascia sign above the main arch (olive board with orange lettering)
    b.add(bm_box(-1.2, BY0 - 0.14, 4.95, 4.4, BY0 - 0.02, 6.55, bevel=bv), 'OF_OliveLit')
    txt(s, L, 'OPERATION', place('-Y', (1.6, BY0 - 0.14, 6.05)), 0.58, 0.06, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.12)
    txt(s, L, 'FALAFEL', place('-Y', (1.6, BY0 - 0.14, 5.4)), 0.8, 0.06, 'black', 'OF_OrangeLit', 'OF_Orange', spacing=1.1)
    txt(s, L, arabic('عملية فلافل'), place('-X', (BX0 - 0.0, BY0 + 6.0, 5.0)), 0.5, 0.05, 'arabic', 'OF_OrangeLit', 'OF_Orange', min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Operation Falafel tower', ((TX0 + TX1) / 2, BY0 - 0.72, 4.8), 0.36, width=2.3)
        register_sign(A, 'Operation Falafel fascia wordmark', (1.6, BY0 - 0.25, 5.4), 0.58, width=4.2)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = TX1 + 0.3, BY0 + 0.35, BX1 - 0.35, BY1 - 0.35
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 4.1, 'RS_TileFloor', 'OF_Sand', lights=[], back_mat='OF_Terracotta')
    counter(it, L, -3.0, 8.4, 6.0, 9.4, 1.05, 'OF_Terracotta', 'OF_Brass')
    it.add(bm_box(ix0, iy1 - 0.8, 0.15, ix1, iy1, 2.2, open_bottom=True), 'OF_Wood')
    for i in range(4):
        x = -2.0 + i * 2.6
        it.add(bm_box(x - 1.0, iy1 - 0.84, 2.3, x + 1.0, iy1 - 0.8, 3.5), 'OF_Menu')
    rng = random.Random(6)
    for (x, y) in ((-1.5, 3.6), (2.0, 3.6), (5.0, 3.6), (0.0, 6.0), (4.0, 6.0)):
        lantern(it, L, x, y, 3.1, 0.18, 0.9)
    for i, (x, y) in enumerate(((-2.0, 3.0), (1.6, 3.0), (5.0, 3.0), (-1.0, 5.6), (3.0, 5.6))):
        cafe_set(it, L, x, y, 2, ang=90 * (i % 2), table_mat='OF_Brass', chair_mat='OF_Wood', seat_mat='OF_Terracotta', r=0.3)
    for i in range(4):
        stool(it, L, -2.4 + i * 1.6, 7.6, 0.65, 'OF_Brass', 'OF_Terracotta')
    it.add(bm_hquad(TX0 + 0.3, BY0 - 0.4, TX1 - 0.3, BY0 + 3.3, 0.16), 'OF_Terracotta')


def build_stele(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.3, -14.7
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.4, cy - 0.3, 0.0, cx + 1.4, cy + 0.3, 0.3, bevel=bv, open_bottom=True), 'RS_Concrete')
    w, zb, zs = 2.4, 0.3, 2.6
    M = place('-Y', (cx, cy + 0.2, 0.0))
    t.add(bm_prism_local([(x - cx, z) for x, z in arch_poly(cx, w, zb, zs, 10 if L == 0 else 5)], 0.4), 'OF_OliveLit', matrix=place('-Y', (cx, cy + 0.2, 0.0)),
          mat_fn=front_back('OF_OliveLit', 'OF_Olive'))
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.2), ('+Y', cy + 0.2)):
        txt(s, L, 'OPERATION', place(face, (cx, yy, 3.2)), 0.36, 0.05, 'black', 'OF_OrangeLit', 'OF_Orange', min_size_lod2=9)
        txt(s, L, 'FALAFEL', place(face, (cx, yy, 2.6)), 0.46, 0.05, 'black', 'OF_OrangeLit', 'OF_Orange', min_size_lod2=9)
        txt(s, L, arabic('عملية فلافل'), place(face, (cx, yy, 1.8)), 0.42, 0.05, 'arabic', 'OF_OrangeLit', 'OF_Orange', min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Operation Falafel stele', (cx, cy - 0.26, 2.6), 0.33, width=2.0)


LAMPS = [(-16.0, -13.5, 0, 1), (0.0, -13.5, 0, 1), (16.0, -13.5, 0, 1), (-18.5, 2.0, 1, 0), (18.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.1, 0.0, BX1, BY1, H + 0.3)
    A.col_box('Tower', TX0 - 0.35, BY0 - 0.75, 0.0, TX1 + 0.35, BY0 + 3.75, TH + 0.9)
    A.col_box('Terrace', *TERRACE[:2], 0.0, *TERRACE[2:], 0.12)
    A.col_box('Stele', 10.9, -15.0, 0.0, 13.7, -14.4, 3.5)
    lamp_collision(A, LAMPS, 7.5)


def build_lights(A):
    glow_lights(A, 'Interior', [(-1.0, 4.0, 3.5), (3.0, 4.0, 3.5), (1.5, 7.0, 3.5)], energy=800, color='#ffc27a')
    for i, x in enumerate((-9.0, -5.5)):
        A.light(f'Pergola{i}', 'POINT', (x, -3.0, 2.3), 400, '#ffb860', radius=0.4)
    A.light('Arch', 'SPOT', (1.6, BY0 - 2.5, 4.0), 900, '#ffd9a0', spot_deg=120, blend=0.8, radius=0.2)
    A.light('TowerUp', 'SPOT', (-5.6, -3.0, 0.3), 1800, '#ffcf90', rot=(-75, 0, 0), spot_deg=70, blend=0.9, radius=0.3)
    sign_light(A, 'FasciaGlow', (1.6, -4.0, 5.0), 1500, '#ffd9b0')
    sign_light(A, 'SteleGlow', (12.3, -18.0, 2.6), 900, '#ffd9b0')
    lamp_lights(A, LAMPS, 7.4, 1.2, 1700)


def main():
    A = Store('14', '14_operation_falafel', 'operation_falafel', 'OPF', 'Restaurant', 'Operation Falafel')
    A.dims = dict(plot=[40.0, 32.0], building=[BX1 - BX0, BY1 - BY0, H], tower_height=TH + 0.9, stele_height=3.5)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_stele(A, L)
        lamp_set(A, L, LAMPS, 7.5, 1.2)
    build_collision(A); build_lights(A)
    A.camera('day', (-15.0, -23.0, 4.0), (0.0, 3.0, 4.0), 32)
    A.camera('road', (-6.0, PLOT[1] - 8.6, 1.25), (1.0, -3.0, 4.8), 32)
    A.camera('detail', (4.0, -10.0, 1.7), (-0.5, 1.0, 3.6), 28)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
