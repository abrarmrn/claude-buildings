"""ASSET 07 - Baskin Robbins (modern ice-cream outlet; general commercial retail).

Plot 38 m x 30 m, road side faces -Y, origin = plot centre at finished ground.
Massing: compact colourful shop, pink/white striped awning, pink 'drip' fascia edge, rooftop ice-cream cone with scoops,
glass display frontage with tub freezer, '31' badge wall. Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-19.0, -15.0, 19.0, 15.0)
BX0, BY0, BX1, BY1 = -6.0, 1.0, 6.0, 9.5
H = 5.0
GX0, GX1, GZ1 = -5.4, 3.2, 3.55
DOOR_X = -1.0
ENTRY, EXIT = (-18.0, -13.0), (13.0, 18.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-19.0, -13.0, -18.2, 15.0), (18.2, -13.0, 19.0, 15.0), (-18.0, 13.5, 18.0, 15.0)]
PAVED = [(-9.0, -5.0, 9.0, BY0)]

defmat('BR_Pink', '#e8318c', rough=0.32, spec=0.6)
defmat('BR_PinkLit', '#e8318c', rough=0.3, emit='#ff3fa0', es=0.7)
defmat('BR_Blue', '#0d3c93', rough=0.32, spec=0.6)
defmat('BR_BlueLit', '#0d3c93', rough=0.3, emit='#2a62ff', es=1.4)
defmat('BR_White', '#f6f4f2', rough=0.3, metal=0.05)
defmat('BR_Cone', '#d8a050', rough=0.7)
defmat('BR_Mint', '#9fe3cf', rough=0.5)
defmat('BR_Choc', '#5a3220', rough=0.45)
defmat('BR_Menu', '#10101a', rough=0.25, emit='#cfe4ff', es=0.9)
defmat('BR_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)


def br_logo(acc, L, M, size=0.95, depth=0.07, badge=True):
    """'Baskin Robbins' wordmark in blue + pink '31' badge (simplified recreation)."""
    txt(acc, L, 'Baskin Robbins', M, size, depth, 'black', 'BR_BlueLit', 'BR_Blue', spacing=0.98)
    if badge:
        disc(acc, L, M @ Matrix.Translation((size * 4.2, 0, 0)), size * 0.62, depth, 'BR_PinkLit', 'BR_Pink')
        txt(acc, L, '31', M @ Matrix.Translation((size * 4.2, 0, depth)), size * 0.7, depth * 0.7, 'black', 'BR_SignWhite', 'BR_White', min_size_lod2=0.3)


def scoop_cone(acc, L, x, y, z, s=1.0):
    seg = {0: 24, 1: 12, 2: 8}[L]
    acc.add(bm_cyl(x, y, z, z + 1.9 * s, 0.03 * s, seg, r2=0.78 * s), 'BR_Cone')
    if L == 0:
        for k in range(5):
            zz = z + (0.35 + 0.3 * k) * s
            acc.add(bm_cyl(x, y, zz, zz + 0.05 * s, (0.03 + 0.78 * (zz - z) / (1.9 * s)) * s * 1.02, 24, caps=False), 'BR_Choc')
    sub = 2 if L == 0 else 1
    acc.add(bm_sphere((x, y, z + 2.2 * s), 0.72 * s, sub, (1, 1, 0.92), 0.0 if L else 0.04), 'BR_Pink')
    acc.add(bm_sphere((x, y, z + 2.9 * s), 0.62 * s, sub, (1, 1, 0.92)), 'BR_White' if L else 'BR_Mint')
    acc.add(bm_sphere((x, y, z + 3.5 * s), 0.52 * s, sub, (1, 1, 0.92)), 'BR_Choc')
    if L < 2:
        acc.add(bm_sphere((x, y, z + 4.0 * s), 0.14 * s, 1), 'RS_ReflectorRed')


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (11.0, -14.6, 14.0, -13.2)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(18.0, -12.0), (-18.0, 6.0), (18.0, 6.0), (-8.0, 13.8), (8.0, 13.8)], 190)
    rng = random.Random(31)
    for i in range(18):
        x = -11.0 + i * 1.4
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 14.5:
            continue
        (R.grass_clump(land, L, x, -14.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -14.0, 0.75, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -15.5, 15.5, depth=1.8)
    cars = {0: ('RS_CarBlue', 'hatch'), 4: ('RS_CarWhite', 'sedan')}
    parking_row(A, L, -9.0, -12.0, -7.0, 7, 2.6, cars)
    disabled_bay(A, L, -9.0 + 2.6 * 7 + 1.3, -12.0, -7.0)
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(2)
    for i, (x, y) in enumerate(((-7.0, -2.6), (-3.8, -3.2), (3.2, -2.8), (6.4, -3.3))):
        cafe_set(fur, L, x, y, 3 if i % 2 else 2, ang=rng2.uniform(0, 90), table_mat='BR_White', chair_mat='RS_MetalDark', seat_mat='BR_Pink' if i % 2 else 'BR_Blue',
                 umb='BR_Pink' if i % 2 else 'BR_Blue', umb2='BR_White', r=0.32)
    planter(fur, L, -9.0, -0.6, -7.2, 0.6, 0.55, 'BR_White', 'RS_Foliage2', seed=1)
    bench(fur, L, 8.2, 3.0, 1.8, 90, 'BR_Pink')
    bin_(fur, L, -8.0, -0.5)


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'BR_White', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='BR_White', roof_mat='BR_White', parapet=0.35, parapet_mat='BR_Blue')
    # white sign band (above awning) with blue stripe; pink drips hanging from the band's lower edge
    b.add(bm_box(BX0 - 0.1, BY0 - 0.35, GZ1 + 0.2, BX1 + 0.1, BY0, H - 0.05, bevel=bv), 'BR_White')
    b.add(bm_box(BX0 - 0.1, BY0 - 0.37, H - 0.2, BX1 + 0.1, BY0, H + 0.4, bevel=bv), 'BR_Blue')
    b.add(bm_box(BX0 - 0.1, BY0 - 0.37, GZ1 + 0.1, BX1 + 0.1, BY0, GZ1 + 0.3, bevel=bv), 'BR_PinkLit')
    if L < 2:
        rng = random.Random(7)
        n = int((BX1 - BX0) / 0.5)
        for i in range(n):
            x = BX0 + 0.35 + i * 0.5
            h = rng.uniform(0.15, 0.5)
            if L == 0:
                b.add(bm_cyl(x, BY0 - 0.2, GZ1 + 0.1 - h, GZ1 + 0.12, 0.13, 10), 'BR_PinkLit')
                b.add(bm_sphere((x, BY0 - 0.2, GZ1 + 0.1 - h), 0.13, 1), 'BR_PinkLit')
            else:
                b.add(bm_box(x - 0.12, BY0 - 0.32, GZ1 + 0.1 - h, x + 0.12, BY0 - 0.08, GZ1 + 0.12), 'BR_PinkLit')
    # pink wall panel with the 31 badge (right of the glazing)
    b.add(bm_box(GX1 + 0.1, BY0 - 0.1, 0.15, BX1 - 0.05, BY0, GZ1 + 0.1, bevel=bv, open_bottom=True), 'BR_PinkLit')
    # striped awning over the glazing
    aw = A.m(L, 'Awnings')
    awning(aw, L, GX0 - 0.2, GX1 + 0.2, BY0 - 0.12, GZ1 + 0.05, 0.75, 1.9, ('BR_Pink', 'BR_White'), strip=0.5, valance=0.28)
    # rooftop cone sculpture on a steel stand
    for (px, py) in ((3.6, 1.8), (5.6, 1.8), (3.6, 3.4), (5.6, 3.4)):
        b.add(bm_box(px - 0.05, py - 0.05, H + 0.4, px + 0.05, py + 0.05, H + 0.9, open_bottom=True), 'RS_MetalDark')
    b.add(bm_box(3.4, 1.6, H + 0.4, 5.8, 3.6, H + 0.5), 'BR_Blue')
    scoop_cone(b, L, 4.6, 2.6, H + 0.5, 0.78)
    s = A.m(L, 'Signage')
    br_logo(s, L, place('-Y', (-2.9, BY0 - 0.4, H - 0.55 + 0.0 - 0.35)), 0.95, 0.07)
    disc(s, L, place('-Y', (4.6, BY0 - 0.1, 2.1)), 1.15, 0.07, 'BR_BlueLit', 'BR_Blue')
    txt(s, L, '31', place('-Y', (4.6, BY0 - 0.17, 2.1)), 1.35, 0.06, 'black', 'BR_SignWhite', 'BR_White')
    txt(s, L, 'FLAVORS', place('-Y', (4.6, BY0 - 0.1, 3.05)), 0.26, 0.03, 'bold', 'BR_SignWhite', 'BR_White', spacing=1.4, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Baskin Robbins wordmark', (-2.9 + 1.5, BY0 - 0.45, 3.95), 0.7, width=4.6)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=5, trans=(), doors=((DOOR_X, 2.0),), frame='BR_Blue', door_h=2.3)
    if L < 2:
        gl = A.m(L, 'Glass')
        gl.add(bm_vquad(GX0, GX1, 0.9, 1.05, BY0 + 0.07), 'BR_Pink')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.8, 'RS_TileFloor', 'BR_White', lights=light_grid((ix0, iy0, ix1, iy1), 4, 2, (1.3, 0.25), 1.2), back_mat='BR_Pink')
    # tub freezer: long display case with pastel tubs visible through the glass
    counter(it, L, -5.0, 3.4, 2.4, 4.7, 1.0, 'BR_Blue', 'BR_White')
    it.add(bm_box(-4.9, 3.5, 1.0, 2.3, 4.6, 1.25), 'RS_Glass')
    cols = ['BR_Pink', 'BR_Mint', 'BR_Choc', 'RS_Cream', 'RS_Pink', 'BR_Cone', 'BR_White']
    rng = random.Random(4)
    for i in range(12):
        for j in range(2):
            x, y = -4.55 + i * 0.6, 3.85 + j * 0.55
            if L == 0:
                it.add(bm_cyl(x, y, 0.82, 1.0, 0.2, 10), cols[rng.randrange(7)])
                it.add(bm_cyl(x, y, 1.0, 1.04, 0.17, 10), cols[rng.randrange(7)])
            else:
                it.add(bm_box(x - 0.2, y - 0.2, 0.82, x + 0.2, y + 0.2, 1.02), cols[rng.randrange(7)])
    it.add(bm_box(-5.0, iy1 - 0.7, 0.15, 5.0, iy1, 1.0, open_bottom=True), 'BR_Blue')
    for i in range(3):
        x = -3.5 + i * 3.5
        it.add(bm_box(x - 1.2, iy1 - 0.06, 1.4, x + 1.2, iy1 - 0.03, 2.8), 'BR_Menu')
    for i, x in enumerate((-4.0, -1.5, 1.0)):
        stool(it, L, x, 5.7, 0.65, 'BR_Blue', 'BR_Pink')
    for (x, y) in ((-3.0, 7.4), (0.0, 7.4), (3.0, 7.4)):
        it.add(bm_sphere((x, y, 3.0), 0.2, 1), 'RS_LightWarm')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.2, -13.9
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.2, cy - 0.4, 0.0, cx + 1.2, cy + 0.4, 0.35, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 0.9, cy - 0.3, 0.35, cx + 0.9, cy + 0.3, 4.2, bevel=bv), 'BR_White')
    t.add(bm_box(cx - 0.92, cy - 0.32, 3.2, cx + 0.92, cy + 0.32, 4.25, bevel=bv), 'BR_BlueLit')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.3), ('+Y', cy + 0.3)):
        txt(s, L, 'Baskin', place(face, (cx, yy, 3.95 - 0.0)), 0.55, 0.05, 'black', 'BR_SignWhite', 'BR_White', min_size_lod2=9)
        txt(s, L, 'Robbins', place(face, (cx, yy, 3.4)), 0.5, 0.05, 'black', 'BR_SignWhite', 'BR_White', min_size_lod2=9)
        disc(s, L, place(face, (cx, yy, 2.0)), 0.7, 0.06, 'BR_PinkLit', 'BR_Pink')
        txt(s, L, '31', place(face, (cx, yy, 2.0)), 0.85, 0.05, 'black', 'BR_SignWhite', 'BR_White')
    scoop_cone(t, L, cx, cy, 4.3, 0.5)


LAMPS = [(9.0, -13.5, 0, 1), (-17.0, 2.0, 1, 0), (17.0, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.4, 0.0, BX1, BY1, H + 0.4)
    A.col_box('ConeSculpture', 3.4, 1.6, H + 0.4, 5.8, 3.6, H + 4.3)
    A.col_box('Awning', GX0 - 0.2, BY0 - 2.0, 2.8, GX1 + 0.2, BY0, 3.6)
    A.col_box('Totem', 11.2, -14.3, 0.0, 13.2, -13.5, 6.0)
    lamp_collision(A, LAMPS)


def build_lights(A):
    glow_lights(A, 'Interior', [(-3.5, 5.0, 3.3), (0.0, 5.0, 3.3), (3.0, 5.0, 3.3), (-2.0, 8.0, 3.3)], energy=900, color='#fff0f5')
    for i, x in enumerate((-4.0, -0.5, 3.0)):
        A.light(f'Awning{i}', 'SPOT', (x, BY0 - 1.8, 2.9), 700, '#ffe8f0', spot_deg=125, blend=0.8, radius=0.2)
    sign_light(A, 'FasciaGlow', (-2.0, -4.0, 4.4), 1800, '#e6f0ff')
    sign_light(A, 'ConeGlow', (4.6, -3.0, 7.0), 1000, '#ffd0e8')
    sign_light(A, 'TotemGlow', (12.2, -17.0, 3.5), 1000, '#e6f0ff')
    lamp_lights(A, LAMPS)


def main():
    A = Store('07', '07_baskin_robbins', 'baskin_robbins', 'BR', 'IceCreamShop', 'Baskin Robbins')
    A.dims = dict(plot=[38.0, 30.0], building=[BX1 - BX0, BY1 - BY0, H], cone_height=H + 0.5 + 0.78 * 4.2, totem_height=6.0)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-14.0, -21.0, 3.6), (0.5, 3.0, 3.0), 32)
    A.camera('road', (-5.0, PLOT[1] - 8.6, 1.25), (0.0, -3.0, 3.8), 32)
    A.camera('detail', (2.0, -9.0, 1.7), (-0.5, 1.0, 3.2), 28)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
