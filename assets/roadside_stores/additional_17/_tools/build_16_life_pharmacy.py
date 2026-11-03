"""ASSET 16 - Life Pharmacy (modern pharmacy; general commercial retail).

Plot 36 m x 28 m, road side faces -Y, origin = plot centre at finished ground.
Massing: white panelled volume, blue sign band with 'life PHARMACY' lockup + green cross emblem, two large shop
windows showing shelves, clean sliding-door entrance under a slim canopy, projecting blade cross, totem sign.
Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-18.0, -14.0, 18.0, 14.0)
BX0, BY0, BX1, BY1 = -7.0, 1.0, 7.0, 10.0
H = 5.4
WIN = [(-6.4, -2.3), (2.3, 6.4)]
ENT = (-1.5, 1.5)
GZ1 = 3.6
ENTRY, EXIT = (-17.0, -12.0), (12.0, 17.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-18.0, -12.0, -17.2, 14.0), (17.2, -12.0, 18.0, 14.0), (-17.0, 12.5, 17.0, 14.0)]
PAVED = [(-8.0, -2.5, 8.0, BY0)]

defmat('LP_Blue', '#0a58a8', rough=0.35, spec=0.6)
defmat('LP_BlueLit', '#0a58a8', rough=0.3, emit='#2f86ff', es=0.9)
defmat('LP_White', '#f6f7f8', rough=0.3, metal=0.05)
defmat('LP_Panel', '#f2f5f8', rough=0.35, emit='#f2f8ff', es=0.35)
defmat('LP_Green', '#1fae5b', rough=0.3, emit='#2ee07a', es=3.5)
defmat('LP_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('LP_Menu', '#0f1216', rough=0.25, emit='#dff0ff', es=0.9)


def cross(acc, L, M, s=1.0, depth=0.12, mat='LP_Green', edge='LP_White'):
    """Pharmacy cross (plus sign) built from two boxes with a white outline plate behind."""
    a = s * 0.18
    acc.add(bm_box(-s * 0.5 - 0.06, -a - 0.06, -0.02, s * 0.5 + 0.06, a + 0.06, depth * 0.5), edge, matrix=M)
    acc.add(bm_box(-a - 0.06, -s * 0.5 - 0.06, -0.02, a + 0.06, s * 0.5 + 0.06, depth * 0.5), edge, matrix=M)
    acc.add(bm_box(-s * 0.5, -a, 0.0, s * 0.5, a, depth), mat, matrix=M)
    acc.add(bm_box(-a, -s * 0.5, 0.0, a, s * 0.5, depth), mat, matrix=M)


def life_lockup(acc, L, M, size=1.0, depth=0.07):
    txt(acc, L, 'life', M, size, depth, 'bold', 'LP_SignWhite', 'LP_White', spacing=1.02)
    txt(acc, L, 'PHARMACY', M @ Matrix.Translation((size * 0.1, -size * 0.55, 0)), size * 0.36, depth * 0.7, 'semi', 'LP_SignWhite', 'LP_White', spacing=1.5, min_size_lod2=0.3)
    cross(acc, L, M @ Matrix.Translation((-size * 1.35, size * 0.02, 0)), size * 0.75, depth * 1.4)


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (11.0, -13.6, 14.0, -12.0)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(16.5, -11.0), (-16.5, 6.0), (16.5, 6.0), (-8.0, 12.5), (8.0, 12.5)], 280)
    for i in range(16):
        x = -11.0 + i * 1.4
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 14.5 or ENTRY[0] - 1 < x < ENTRY[1] + 1:
            continue
        (R.grass_clump(land, L, x, -13.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -13.0, 0.7, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -14.5, 14.5, depth=1.8)
    cars = {6: ('RS_CarSilver', 'sedan')}
    parking_row(A, L, -9.0, -11.5, -6.5, 7, 2.6, cars)
    disabled_bay(A, L, -9.0 + 2.6 * 7 + 1.3, -11.5, -6.5)
    f = A.m(L, 'Furniture')
    planter(f, L, -8.0, -2.4, -6.4, -1.6, 0.5, 'LP_White', 'RS_Foliage2', seed=1)
    planter(f, L, 6.4, -2.4, 8.0, -1.6, 0.5, 'LP_White', 'RS_Foliage2', seed=2)
    bench(f, L, -4.2, -1.6, 1.8, 0, 'LP_Blue')
    bench(f, L, 4.2, -1.6, 1.8, 0, 'LP_Blue')
    bin_(f, L, 0.0, -2.0, 'LP_Blue')
    bollards = A.m(L, 'Props')
    for x in (-8.0, -4.0, 4.0, 8.0):
        R.bollard(bollards, L, x, -2.4, 0.9, 0.08)


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    holes = [(WIN[0][0], 0.15, WIN[0][1], GZ1), (ENT[0], 0.15, ENT[1], GZ1), (WIN[1][0], 0.15, WIN[1][1], GZ1)]
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'LP_White', t=t, holes=holes, front_mat='LP_White', roof_mat='LP_White', roof_t=0.35, parapet=0.3, parapet_mat='LP_Blue')
    # white panelled piers and blue sign band + stripe
    for (xa, xb) in ((BX0, WIN[0][0]), (WIN[1][1], BX1)):
        b.add(bm_box(xa, BY0 - 0.12, 0.0, xb, BY0, GZ1, bevel=bv, open_bottom=True), 'LP_Panel')
    for (xa, xb) in ((WIN[0][1], ENT[0]), (ENT[1], WIN[1][0])):
        b.add(bm_box(xa, BY0 - 0.18, 0.0, xb, BY0, GZ1 + 0.15, bevel=bv, open_bottom=True), 'LP_Blue')
    b.add(bm_box(BX0, BY0 - 0.2, GZ1 + 0.05, BX1, BY0 + 0.05, H - 0.1, bevel=bv), 'LP_BlueLit')
    b.add(bm_box(BX0, BY0 - 0.22, GZ1, BX1, BY0 - 0.1, GZ1 + 0.08), 'LP_White')
    # slim entrance canopy with LED edge
    b.add(bm_box(-3.2, BY0 - 2.2, 3.85, 3.2, BY0, 4.05, bevel=bv), 'LP_White')
    b.add(bm_box(-3.22, BY0 - 2.24, 3.82, 3.22, BY0 - 2.12, 4.08), 'LP_Blue')
    if L < 2:
        b.add(bm_box(-3.0, BY0 - 2.0, 3.83, 3.0, BY0 - 1.8, 3.85), 'RS_LightPanel')
    for x in (-3.0, 3.0):
        b.add(bm_cyl(x, BY0 - 2.0, 0.1, 3.85, 0.06, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    # projecting blade cross on the right edge (faces +/-X, readable along the road)
    b.add(bm_box(BX1 - 0.05, BY0 - 0.9, 3.2, BX1 + 0.05, BY0 - 0.1, 3.3), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    life_lockup(s, L, place('-Y', (0.6, BY0 - 0.2, 4.6)), 1.15, 0.07)
    for sx, face in ((BX1 + 0.05, '+X'), (BX1 - 0.05, '-X')):
        cross(s, L, place(face, (sx, BY0 - 0.9, 4.2)), 1.4, 0.12)
    life_lockup(s, L, place('+X', (BX1 + 0.02, 5.5, 3.2)), 0.7, 0.05)
    if L == 0:
        register_sign(A, 'life PHARMACY lockup', (1.15, BY0 - 0.3, 4.6), 0.82, width=3.8)
    glazing(A, L, WIN[0][0], WIN[0][1], 0.15, GZ1, BY0 + 0.1, nx=4, trans=(), frame='LP_Blue', bottom_rail=0.12)
    glazing(A, L, WIN[1][0], WIN[1][1], 0.15, GZ1, BY0 + 0.1, nx=4, trans=(), frame='LP_Blue', bottom_rail=0.12)
    glazing(A, L, ENT[0], ENT[1], 0.15, GZ1, BY0 + 0.1, nx=2, trans=(), doors=((0.0, 2.4),), frame='RS_MetalBrushed', door_h=2.4)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 4.0, 'RS_TileFloor', 'LP_White', lights=light_grid((ix0, iy0, ix1, iy1), 5, 3, (1.3, 0.25), 1.0), back_mat='LP_Blue')
    # wall shelving (full height) along both side walls and the back, centre gondolas
    kk = 0
    for y in (3.6, 5.6, 7.6):
        for xa, xb in ((-5.8, -2.4), (2.4, 5.8)):
            R.product_shelf(it, L, xa, y - 0.4, xb, y + 0.4, 1.8, 5, seed=500 + kk)
            kk += 1
    R.product_shelf(it, L, -6.3, 2.3, -6.0, 8.8, 2.3, 5, seed=600, two_sided=False)
    R.product_shelf(it, L, 6.0, 2.3, 6.3, 8.8, 2.3, 5, seed=601, two_sided=False)
    # pharmacy counter at the back with a lit green cross
    counter(it, L, -3.0, 8.6, 3.0, 9.4, 1.05, 'LP_Blue', 'LP_White')
    it.add(bm_box(ix0, iy1 - 0.5, 0.15, ix1, iy1, 2.6, open_bottom=True), 'LP_White')
    cross(it, L, Matrix.Translation((0.0, iy1 - 0.52, 2.9)) @ Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))).to_4x4(), 0.9, 0.1)
    it.add(bm_box(-2.6, iy1 - 0.52, 1.2, 2.6, iy1 - 0.5, 2.3), 'LP_Menu')
    # checkout till
    counter(it, L, 3.3, 3.0, 5.6, 3.8, 1.0, 'LP_Blue', 'LP_White')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.5, -12.7
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.2, cy - 0.35, 0.0, cx + 1.2, cy + 0.35, 0.3, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 0.95, cy - 0.25, 0.3, cx + 0.95, cy + 0.25, 5.2, bevel=bv), 'LP_BlueLit')
    t.add(bm_box(cx - 1.0, cy - 0.27, 5.2, cx + 1.0, cy + 0.27, 5.3), 'LP_White')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.25), ('+Y', cy + 0.25)):
        txt(s, L, 'life', place(face, (cx, yy, 4.0)), 1.0, 0.06, 'bold', 'LP_SignWhite', 'LP_White', min_size_lod2=9)
        txt(s, L, 'PHARMACY', place(face, (cx, yy, 3.3)), 0.3, 0.04, 'semi', 'LP_SignWhite', 'LP_White', spacing=1.5, min_size_lod2=9)
        cross(s, L, place(face, (cx, yy, 1.8)), 1.2, 0.1)
    if L == 0:
        register_sign(A, 'life PHARMACY totem', (cx, cy - 0.31, 4.0), 0.72, width=1.7)


LAMPS = [(8.0, -12.5, 0, 1), (-16.5, 2.0, 1, 0), (16.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H + 0.3)
    A.col_box('Canopy', -3.2, BY0 - 2.24, 3.82, 3.2, BY0, 4.08)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    A.col_box('Totem', 11.3, -13.05, 0.0, 13.7, -12.35, 5.3)
    lamp_collision(A, LAMPS, 7.5)


def build_lights(A):
    for i, x in enumerate((-2.0, 0.0, 2.0)):
        A.light(f'Canopy{i}', 'SPOT', (x, BY0 - 1.2, 3.8), 600, '#e8f2ff', rot=(180, 0, 0), spot_deg=120, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-3.0, 4.5, 3.5), (3.0, 4.5, 3.5), (0.0, 7.5, 3.5)], energy=1100, color='#f2f8ff')
    sign_light(A, 'BandGlow', (0.6, -3.5, 4.6), 1800, '#e0eeff')
    sign_light(A, 'TotemGlow', (12.5, -15.5, 4.0), 1100, '#e0eeff')
    A.light('BladeGlow', 'POINT', (BX1 + 1.2, BY0 - 1.5, 4.2), 600, '#7dffb0', radius=0.5)
    lamp_lights(A, LAMPS, 7.4, 1.2, 1800)


def main():
    A = Store('16', '16_life_pharmacy', 'life_pharmacy', 'LIFE', 'Pharmacy', 'Life Pharmacy')
    A.dims = dict(plot=[36.0, 28.0], building=[BX1 - BX0, BY1 - BY0, H], totem_height=5.3, blade_cross_height=4.9)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS, 7.5, 1.2)
    build_collision(A); build_lights(A)
    A.camera('day', (-13.0, -19.0, 3.8), (0.5, 3.0, 3.1), 32)
    A.camera('road', (-21.0, PLOT[1] - 8.6, 1.25), (1.0, -3.0, 3.8), 32)
    A.camera('detail', (3.5, -8.0, 1.7), (0.0, 1.0, 3.4), 27)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
