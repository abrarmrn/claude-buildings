"""ASSET 10 - Five Guys (premium burger restaurant; premium restaurant frontage).

Plot 40 m x 32 m, road side faces -Y, origin = plot centre at finished ground.
Massing: industrial brick box with a black steel factory-style window wall, red/white checker-tile bulkheads,
red sign board with gooseneck lamps, steel-and-corrugated entrance canopy, patio with high tables and stools,
peanut-box stacks inside. Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-20.0, -16.0, 20.0, 16.0)
BX0, BY0, BX1, BY1 = -7.0, 1.0, 7.0, 11.0
H = 5.8
GX0, GX1, GZ1 = -5.8, 5.8, 4.0
DOOR_X = 3.6
ENTRY, EXIT = (-19.0, -14.0), (14.0, 19.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-20.0, -14.0, -19.2, 16.0), (19.2, -14.0, 20.0, 16.0), (-19.0, 14.5, 19.0, 16.0)]
PATIO = (-13.0, -6.0, 13.0, BY0)

defmat('FG_Red', '#d2232a', rough=0.32, spec=0.6)
defmat('FG_RedLit', '#c81e25', rough=0.32, emit='#e0242b', es=0.12)
defmat('FG_White', '#f4f2ee', rough=0.4)
defmat('FG_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('FG_Steel', '#1b1c1e', rough=0.45, metal=0.7)
defmat('FG_Corr', '#b8201f', rough=0.5, metal=0.5)
defmat('FG_Menu', '#0f0f10', rough=0.25, emit='#fff0d0', es=0.9)
defmat('FG_Lamp', '#ffffff', rough=0.3, emit='#ffc98a', es=4.5)


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (9.8, -15.4, 12.4, -14.0)]
    site_ground(A, L, PLOT, holes, [PATIO], BEDS, paver_h=0.1, mat_paved='RS_Concrete')
    land = A.m(L, 'Landscape')
    palms(A, L, [(18.5, -13.0), (-18.5, 8.0), (18.5, 8.0)], 220)
    for i in range(14):
        x = -12.0 + i * 1.8
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 9.0 < x < 13.5 or ENTRY[0] - 1 < x < ENTRY[1] + 1:
            continue
        R.grass_clump(land, L, x, -15.0, 0.9, seed=i)
    entry_exit(A, L, PLOT, -16.5, 16.5, depth=1.8)
    cars = {0: ('RS_CarGrey', 'suv'), 6: ('RS_CarRed', 'hatch')}
    parking_row(A, L, -9.0, -12.5, -7.5, 7, 2.6, cars)
    disabled_bay(A, L, -9.0 + 2.6 * 7 + 1.3, -12.5, -7.5)
    fur = A.m(L, 'Furniture')
    rng = random.Random(8)
    # high tables with steel stools (industrial) and wire chairs with red cushions
    for i, (x, y) in enumerate(((-10.5, -2.8), (-7.5, -3.6), (-4.5, -2.8), (4.5, -3.6), (7.5, -2.8), (10.5, -3.6))):
        if i % 2 == 0:
            fur.add(bm_cyl(x, y, 0.0, 1.05, 0.03, 6, open_bottom=True), 'FG_Steel')
            fur.add(bm_cyl(x, y, 1.02, 1.07, 0.38, 14 if L == 0 else 8), 'FG_White')
            for a in (0, 120, 240):
                stool(fur, L, x + 0.6 * math.cos(math.radians(a + 20)), y + 0.6 * math.sin(math.radians(a + 20)), 0.7, 'FG_Steel', 'FG_Red')
        else:
            cafe_set(fur, L, x, y, 3, ang=rng.uniform(0, 90), table_mat='FG_White', chair_mat='FG_Steel', seat_mat='FG_Red', r=0.34)
    for x in (-12.0, 12.0):
        planter(fur, L, x - 0.9, -5.6, x + 0.9, -4.8, 0.55, 'FG_Steel', 'RS_Foliage2', seed=int(x))
    bin_(fur, L, -1.5, -5.4, 'FG_Steel')
    bin_(fur, L, 1.0, -5.4, 'FG_Steel')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.02 if L == 0 else 0.0
    t = 0.35
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'RS_Brick', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='RS_Brick', roof_mat='FG_Steel', roof_t=0.4,
          parapet=0.45, parapet_mat='FG_Steel')
    # checker-tile bulkhead under the windows (leaving the door gap) + checker band on the east wall
    for (xa, xb) in ((GX0, DOOR_X - 1.15), (DOOR_X + 1.15, GX1)):
        b.add(bm_box(xa, BY0 - 0.08, 0.15, xb, BY0, 0.95, bevel=bv, open_bottom=True), 'RS_Checker')
    b.add(bm_box(BX1, BY0, 0.15, BX1 + 0.06, BY1, 1.5, open_bottom=True), 'RS_Checker')
    # steel lintel + corrugated band
    b.add(bm_box(GX0 - 0.15, BY0 - 0.18, GZ1, GX1 + 0.15, BY0 + 0.06, GZ1 + 0.25, bevel=bv), 'FG_Steel')
    b.add(bm_box(BX0 - 0.05, BY0 - 0.06, H - 0.9, BX1 + 0.05, BY0, H + 0.1), 'FG_Corr')
    # red sign board (on the brick above the window wall)
    b.add(bm_box(-5.2, BY0 - 0.2, GZ1 + 0.4, 5.2, BY0 - 0.04, 5.35, bevel=bv), 'FG_RedLit')
    b.add(bm_box(-5.3, BY0 - 0.22, GZ1 + 0.35, 5.3, BY0 - 0.12, GZ1 + 0.42), 'FG_White')
    b.add(bm_box(-5.3, BY0 - 0.22, 5.33, 5.3, BY0 - 0.12, 5.4), 'FG_White')
    # gooseneck lamps over the board
    if L < 2:
        for x in (-3.5, 0.0, 3.5):
            b.add(bm_cyl_between((x, BY0 - 0.05, 5.55), (x, BY0 - 0.55, 5.95), 0.03, 6), 'FG_Steel')
            b.add(bm_cyl(x, BY0 - 0.6, 5.88, 6.0, 0.16, 10 if L == 0 else 6), 'FG_Steel')
            b.add(bm_cyl(x, BY0 - 0.6, 5.86, 5.89, 0.13, 10 if L == 0 else 6), 'FG_Lamp')
    # steel + corrugated entrance canopy
    cp = A.m(L, 'Canopy')
    cp.add(bm_box(DOOR_X - 1.8, BY0 - 2.4, 3.3, DOOR_X + 1.8, BY0, 3.5, bevel=bv), 'FG_Corr')
    for x in (DOOR_X - 1.7, DOOR_X + 1.7):
        cp.add(bm_box(x - 0.05, BY0 - 2.35, 0.1, x + 0.05, BY0 - 2.25, 3.3), 'FG_Steel')
        cp.add(bm_box(x - 0.04, BY0 - 2.4, 3.2, x + 0.04, BY0, 3.3), 'FG_Steel')
    # side wall industrial windows (east)
    gl_, fr_ = A.m(L, 'Glass'), A.m(L, 'Frames')
    s = A.m(L, 'Signage')
    txt(s, L, 'FIVE GUYS', place('-Y', (0.0, BY0 - 0.2, 4.85)), 1.0, 0.07, 'black', 'FG_SignWhite', 'FG_White', spacing=1.08)
    txt(s, L, 'BURGERS & FRIES', place('-Y', (0.0, BY0 - 0.2, 4.3)), 0.25, 0.04, 'bold', 'FG_SignWhite', 'FG_White', spacing=1.4, min_size_lod2=9)
    txt(s, L, 'FIVE GUYS', place('+X', (BX1 + 0.1, 5.2, 3.6)), 0.55, 0.05, 'black', 'FG_SignWhite', 'FG_White')
    if L == 0:
        register_sign(A, 'FIVE GUYS sign board', (0.0, BY0 - 0.32, 4.85), 0.72, width=5.2)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=8, trans=(1.35, 2.35, 3.2), doors=((DOOR_X, 2.3),), frame='FG_Steel', door_h=2.4, fd=0.14)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.35, BY0 + 0.35, BX1 - 0.35, BY1 - 0.35
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 4.5, 'RS_Checker', 'RS_Brick', lights=[], back_mat='RS_Brick')
    for (x, y) in ((-4.5, 4.0), (-2.0, 4.0), (0.5, 4.0), (-4.0, 6.6), (-1.0, 6.6), (2.0, 6.6), (-3.0, 8.4), (0.5, 8.4)):
        it.add(bm_cyl(x, y, 3.0, 4.5, 0.01, 4, caps=False), 'RS_PlasticBlack')
        it.add(bm_cyl(x, y, 2.7, 3.05, 0.22, 12 if L == 0 else 6, r2=0.08), 'FG_Lamp')
    counter(it, L, -5.5, 8.6, 3.0, 9.6, 1.05, 'FG_Red', 'RS_PaintWhite')
    it.add(bm_box(ix0, iy1 - 0.8, 0.15, ix1, iy1, 2.2, open_bottom=True), 'FG_Steel')
    for i in range(3):
        x = -4.0 + i * 3.6
        it.add(bm_box(x - 1.2, iy1 - 0.84, 2.3, x + 1.2, iy1 - 0.8, 3.7), 'FG_Menu')
    # peanut boxes (stacked cardboard) and potato sacks near the entrance
    rng = random.Random(2)
    for i in range(5):
        for j in range(3 - (i % 2)):
            it.add(bm_box(4.4 + i * 0.45, 1.9 + j * 0.5, 0.15, 4.4 + i * 0.45 + 0.4, 1.9 + j * 0.5 + 0.42, 0.65), 'RS_Cardboard')
            if L == 0:
                it.add(bm_box(4.4 + i * 0.45 + 0.02, 1.9 + j * 0.5 + 0.02, 0.65, 4.4 + i * 0.45 + 0.38, 1.9 + j * 0.5 + 0.4, 1.1), 'RS_Cardboard')
    for k in range(4):
        it.add(bm_sphere((-5.0 + k * 0.5, 2.2, 0.45), 0.28, 1 if L else 2, (1, 0.8, 1.2)), 'RS_Pastry')
    for i, (x, y) in enumerate(((-4.0, 3.2), (-1.0, 3.2), (-3.5, 5.6), (-0.5, 5.6), (2.5, 5.2))):
        cafe_set(it, L, x, y, 2, ang=90 * (i % 2), table_mat='FG_White', chair_mat='FG_Steel', seat_mat='FG_Red', r=0.32)
    it.add(bm_quad((ix1 - 0.002, iy0 + 4.0, 0.16), (ix1 - 0.002, iy0, 0.16), (ix1 - 0.002, iy0, 1.4), (ix1 - 0.002, iy0 + 4.0, 1.4)), 'RS_Checker')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 11.2, -14.7
    bv = 0.02 if L == 0 else 0.0
    t.add(bm_box(cx - 1.3, cy - 0.3, 0.0, cx + 1.3, cy + 0.3, 0.3, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 1.15, cy - 0.22, 0.3, cx + 1.15, cy + 0.22, 4.2, bevel=bv), 'FG_RedLit')
    t.add(bm_box(cx - 1.2, cy - 0.24, 4.2, cx + 1.2, cy + 0.24, 4.3), 'FG_White')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.22), ('+Y', cy + 0.22)):
        txt(s, L, 'FIVE', place(face, (cx, yy, 3.3)), 0.85, 0.05, 'black', 'FG_SignWhite', 'FG_White', min_size_lod2=9)
        txt(s, L, 'GUYS', place(face, (cx, yy, 2.4)), 0.85, 0.05, 'black', 'FG_SignWhite', 'FG_White', min_size_lod2=9)
        txt(s, L, 'BURGERS & FRIES', place(face, (cx, yy, 1.5)), 0.2, 0.03, 'bold', 'FG_SignWhite', 'FG_White', spacing=1.2, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'FIVE GUYS totem', (cx, cy - 0.27, 3.3), 0.62, width=2.0)


LAMPS = [(-16.0, -13.5, 0, 1), (0.0, -13.5, 0, 1), (16.0, -13.5, 0, 1), (-18.5, 2.0, 1, 0), (18.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H + 0.5)
    A.col_box('Canopy', DOOR_X - 1.8, BY0 - 2.4, 3.2, DOOR_X + 1.8, BY0, 3.5)
    A.col_box('Patio', *PATIO[:2], 0.0, *PATIO[2:], 0.1)
    A.col_box('Totem', 9.9, -15.0, 0.0, 12.5, -14.4, 4.3)
    lamp_collision(A, LAMPS, 7.0)


def build_lights(A):
    for i, x in enumerate((-3.5, 0.0, 3.5)):
        A.light(f'Gooseneck{i}', 'SPOT', (x, BY0 - 0.65, 5.85), 500, '#ffc98a', rot=(-120, 0, 0), spot_deg=100, blend=0.9, radius=0.1)
    A.light('Canopy', 'SPOT', (DOOR_X, BY0 - 1.2, 3.25), 600, '#fff0e0', rot=(180, 0, 0), spot_deg=110, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-3.5, 4.5, 3.5), (0.0, 4.5, 3.5), (-2.0, 7.5, 3.5)], energy=1000, color='#ffd9a6')
    sign_light(A, 'TotemGlow', (11.2, -18.0, 3.0), 1200, '#ffe0e0')
    lamp_lights(A, LAMPS, 6.9, 1.0, 1700)


def main():
    A = Store('10', '10_five_guys', 'five_guys', 'FG', 'Restaurant', 'Five Guys')
    A.dims = dict(plot=[40.0, 32.0], building=[BX1 - BX0, BY1 - BY0, H], totem_height=4.3)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS, 7.0, 1.0)
    build_collision(A); build_lights(A)
    A.camera('day', (-14.0, -22.0, 3.6), (0.0, 3.0, 3.3), 32)
    A.camera('road', (-24.0, PLOT[1] - 8.6, 1.25), (1.0, -4.0, 3.4), 32)
    A.camera('detail', (2.0, -9.5, 1.7), (-0.5, 1.0, 3.2), 28)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
