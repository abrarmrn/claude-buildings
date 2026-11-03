"""ASSET 03 - Costa Coffee (premium standalone coffee shop; boulevard podium retail).

Plot 44 m x 34 m, road side faces -Y, origin = plot centre at finished ground.
Massing: burgundy 'cube' with timber slat accent and big wordmark + glass pavilion, cantilevered terrace roof,
timber deck with planters and burgundy chairs, low totem sign. Branding is a simplified recreation.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-22.0, -17.0, 22.0, 17.0)
BX0, BY0, BX1, BY1 = -9.0, 1.0, 7.0, 11.0
H, CUBE_H = 4.3, 5.9
CX0, CX1 = 0.5, 7.0                    # burgundy cube (x range), projects 0.4 m forward
GX0, GX1, GZ1 = -8.4, 0.1, 3.7         # glass pavilion
DECK = (-12.5, -5.0, 3.0, BY0)
ROOF = (-11.0, -3.2, 0.3, BY0)
ENTRY, EXIT = (-21.0, -15.5), (15.5, 21.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.0) + [(-22.0, -15.0, -21.0, 17.0), (21.0, -15.0, 22.0, 17.0), (-21.0, 15.0, 21.0, 17.0)]

defmat('CO_Burgundy', '#7e1428', rough=0.34, spec=0.6)
defmat('CO_BurgundyLit', '#8e1630', rough=0.32, emit='#b81a3c', es=0.5)
defmat('CO_Cream', '#f3e9d6', rough=0.4)
defmat('CO_SignCream', '#f7efe0', rough=0.35, emit='#fff1d6', es=2.6)
defmat('CO_Chair', '#7e1428', rough=0.6)
defmat('CO_Clad', '#e9e4da', rough=0.45)
defmat('CO_Menu', '#1a1210', rough=0.25, emit='#ffd9a0', es=0.9)
defmat('CO_Warm', '#ffffff', rough=0.3, emit='#ffc98a', es=3.2)


def costa_wordmark(acc, L, M, size, depth=0.07):
    txt(acc, L, 'Costa', M, size, depth, 'bold', 'CO_SignCream', 'CO_Cream', spacing=1.02)


# ------------------------------------------------------------------ ground
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.45, BX1 + 0.05, BY1 + 0.05), (10.5, -16.7, 14.0, -15.1)]
    site_ground(A, L, PLOT, holes, [DECK], BEDS, paver_h=0.18, mat_paved='RS_Wood')
    land = A.m(L, 'Landscape')
    palms(A, L, [(-20.5, -15.0), (-20.5, 6.0), (20.5, 6.0), (-6.0, 15.8), (6.0, 15.8)], 140)
    rng = random.Random(11)
    for i in range(22):
        x = -14.0 + i * 1.3
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 15.0:
            continue
        R.shrub(land, L, x, -16.0 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage' if i % 2 else 'RS_Foliage2')
    for i in range(14):
        R.shrub(land, L, -20.4, -12.0 + i * 2.0, 0.8, seed=50 + i)
        R.shrub(land, L, 20.4, -12.0 + i * 2.0, 0.8, seed=80 + i, mat='RS_Foliage2')
    entry_exit(A, L, PLOT, -18.5, 18.5, depth=2.0)
    cars = {1: ('RS_CarGold', 'hatch'), 6: ('RS_CarWhite', 'sedan')}
    parking_row(A, L, -10.0, -14.0, -9.0, 7, 2.6, cars)
    disabled_bay(A, L, -10.0 + 2.6 * 7 + 1.3, -14.0, -9.0)
    # terrace furniture on the timber deck
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(2)
    for i, (x, y) in enumerate(((-10.0, -3.8), (-7.0, -3.3), (-4.0, -3.9), (-1.0, -3.3), (-8.5, -0.6), (-3.2, -0.4))):
        cafe_set(fur, L, x, y, 3 if i % 2 else 4, ang=rng2.uniform(0, 90), table_mat='CO_Cream', chair_mat='RS_MetalDark', seat_mat='CO_Chair', r=0.34)
    for i, x in enumerate((-11.5, -7.5, -3.5, 0.5)):
        planter(fur, L, x, -5.0 + 0.0, x + 3.0, -4.5 + 0.0, 0.62, 'CO_Clad', 'RS_Foliage2', seed=10 * i)
    for x in (2.0,):
        topiary(fur, L, x, -4.1, 1.5, 0.4)
    bench(fur, L, 5.5, -2.0, 1.8, 0)


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, CX0, BY1), H, 'CO_Clad', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='CO_Clad', roof_mat='CO_Clad', parapet=0.35,
          parapet_mat='CO_Clad', rooftop=True, skip=('right',))
    # cube: burgundy, projects forward, slats panel on the left half of its front
    cy0 = BY0 - 0.4
    b.add(bm_box(CX0, cy0, 0.0, CX1, BY1, CUBE_H, bevel=bv, open_bottom=True), 'CO_Burgundy')
    b.add(bm_box(CX0 - 0.05, cy0 - 0.06, CUBE_H - 0.25, CX1 + 0.05, BY1, CUBE_H + 0.12, bevel=bv), 'CO_Cream')
    b.add(bm_box(CX0 + 0.4, cy0 - 0.05, 0.15, CX0 + 2.0, cy0, 2.8), 'RS_WoodV', uv='box')
    b.add(bm_box(CX1 - 2.0, cy0 - 0.05, 0.15, CX1 - 0.4, cy0, 2.8), 'RS_WoodV', uv='box')
    # cantilevered terrace roof with warm light strip, slim columns
    x0, y0, x1, y1 = ROOF
    b.add(bm_box(x0, y0, 3.95, x1, y1, 4.28, bevel=bv), 'CO_Clad')
    b.add(bm_box(x0 - 0.02, y0 - 0.06, 3.88, x1 + 0.02, y0 + 0.05, 4.35, bevel=bv), 'CO_Burgundy')
    if L < 2:
        b.add(bm_box(x0 + 0.3, y0 + 0.2, 3.93, x1 - 0.3, y0 + 0.45, 3.95), 'CO_Warm')
        b.add(bm_box(x0 + 0.3, y1 - 0.8, 3.93, x1 - 0.3, y1 - 0.55, 3.95), 'CO_Warm')
    for (px, py) in ((-10.4, -3.0), (0.6, -3.0)):
        b.add(bm_cyl(px, py, 0.18, 3.95, 0.09, 12 if L == 0 else 6), 'RS_MetalDark')
    s = A.m(L, 'Signage')
    costa_wordmark(s, L, place('-Y', ((CX0 + CX1) / 2, cy0 - 0.02, 4.6)), 1.5)
    txt(s, L, 'COFFEE', place('-Y', ((CX0 + CX1) / 2, cy0 - 0.02, 3.7)), 0.46, 0.05, 'medium', 'CO_SignCream', 'CO_Cream', spacing=1.5)
    for sx, face in ((CX1, '+X'),):
        costa_wordmark(s, L, place(face, (sx + 0.02, 4.5, 3.9)), 0.9, 0.05)
    # small fascia name on the glass pavilion
    if L == 0:
        register_sign(A, 'Costa cube wordmark', ((CX0 + CX1) / 2, cy0 - 0.1, 4.6), 1.08, width=4.6)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=6, trans=(2.6,), doors=((-1.4, 1.9),), frame='RS_MetalDark', door_h=2.3, frameless=False)
    if L < 2:
        gl = A.m(L, 'Glass')
        gl.add(bm_vquad(GX0, GX1, 0.95, 1.1, BY0 + 0.07), 'CO_Burgundy')
        # east wall glass slot


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, CX0 + 0.1, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.55, 'RS_TileFloor', 'CO_Cream',
                        lights=light_grid((ix0, iy0, ix1, iy1), 4, 2, (1.4, 0.26), 1.0), back_mat='CO_Cream')
    # pendant lamps (warm)
    for (x, y) in ((-7.0, 4.0), (-4.0, 4.0), (-1.0, 4.0), (-6.0, 7.2), (-2.5, 7.2)):
        it.add(bm_cyl(x, y, 2.7, 3.55, 0.01, 4, caps=False) if L == 0 else bm_cyl(x, y, 2.7, 3.55, 0.01, 3, caps=False), 'RS_PlasticBlack')
        it.add(bm_cyl(x, y, 2.45, 2.75, 0.32, 14 if L == 0 else 7, r2=0.1), 'CO_Warm')
    counter(it, L, -8.0, 8.4, -1.0, 9.5, 1.05, 'CO_Burgundy', 'RS_PaintWhite')
    it.add(bm_box(-8.0, iy1 - 0.7, 0.15, -0.8, iy1, 1.0, open_bottom=True), 'RS_PaintCharcoal')
    for i in range(4):
        x = -7.4 + i * 1.7
        it.add(bm_box(x - 0.7, iy1 - 0.08, 1.5, x + 0.7, iy1 - 0.04, 2.5), 'CO_Menu')
    it.add(bm_box(-4.5, 8.5, 1.1, -1.6, 9.4, 1.6, bevel=0.01 if L == 0 else 0), 'RS_Cooler')
    if L == 0:
        for x in (-7.5, -6.7):
            it.add(bm_box(x - 0.3, 8.6, 1.1, x + 0.3, 9.2, 1.6, bevel=0.02), 'RS_MetalBrushed')
        for i in range(5):
            stool(it, L, -7.0 + i * 1.3, 7.7)
    # lounge: armchairs and low tables near the glass
    for i, (x, y) in enumerate(((-7.3, 3.6), (-3.6, 3.4), (-6.0, 5.8), (-2.0, 5.5))):
        cafe_set(it, L, x, y, 2 if i % 2 else 3, ang=20 * i, table_mat='CO_Cream', chair_mat='RS_MetalDark', seat_mat='CO_Chair', r=0.3)
    # cube interior
    it.add(bm_hquad(CX0, BY0 - 0.35, CX1 - 0.3, BY1 - 0.3, 0.155), 'RS_Wood')
    for x in (2.0, 4.0, 6.0):
        it.add(bm_box(x - 0.9, 3.0, 0.15, x + 0.9, 4.0, 0.75, bevel=0.03 if L == 0 else 0, open_bottom=True), 'CO_Chair')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.2, -15.9
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.2, cy - 0.45, 0.0, cx + 1.2, cy + 0.45, 0.35, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 0.95, cy - 0.28, 0.35, cx + 0.95, cy + 0.28, 4.6, bevel=bv), 'CO_BurgundyLit')
    t.add(bm_box(cx - 1.0, cy - 0.3, 4.6, cx + 1.0, cy + 0.3, 4.75, bevel=bv), 'CO_Cream')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.28), ('+Y', cy + 0.28)):
        costa_wordmark(s, L, place(face, (cx, yy, 3.4)), 0.95, 0.05)
        txt(s, L, 'COFFEE', place(face, (cx, yy, 2.55)), 0.34, 0.04, 'medium', 'CO_SignCream', 'CO_Cream', spacing=1.5, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Costa totem wordmark', (cx, cy - 0.35, 3.4), 0.7, width=1.8)


LAMPS = [(-2.0, -15.0, 0, 1), (9.0, -15.0, 0, 1), (17.5, -15.0, 0, 1), (-20.0, 3.0, 1, 0), (20.0, 3.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0, 0.0, BX1, BY1, H)
    A.col_box('Cube', CX0, BY0 - 0.4, 0.0, CX1, BY1, CUBE_H)
    A.col_box('TerraceRoof', ROOF[0], ROOF[1], 3.88, ROOF[2], ROOF[3], 4.35)
    A.col_box('Deck', *DECK[:2], 0.0, *DECK[2:], 0.18)
    A.col_box('Totem', 11.2, -16.4, 0.0, 13.2, -15.4, 4.75)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-9.0, -5.0, -1.0)):
        A.light(f'Terrace{i}', 'SPOT', (x, -1.5, 3.9), 900, '#ffd9a6', spot_deg=125, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-6.5, 4.5, 3.1), (-2.5, 4.5, 3.1), (-5.0, 8.0, 3.1), (3.5, 6.0, 3.0)], energy=900, color='#ffc98a')
    sign_light(A, 'CubeGlow', (3.5, -5.0, 4.0), 1800, '#ffe3c8')
    sign_light(A, 'TotemGlow', (12.2, -19.0, 3.4), 1200, '#ffd8d0')
    lamp_lights(A, LAMPS)


def main():
    A = Store('03', '03_costa_coffee', 'costa_coffee', 'COSTA', 'CoffeeShop', 'Costa Coffee')
    A.dims = dict(plot=[44.0, 34.0], building=[BX1 - BX0, BY1 - BY0, H], cube_height=CUBE_H, totem_height=4.75)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-19.0, -26.0, 4.0), (0.0, 3.0, 2.7), 32)
    A.camera('road', (31.0, PLOT[1] - 8.6, 1.25), (-1.0, -2.0, 3.4), 30)
    A.camera('detail', (4.0, -10.0, 1.7), (-1.0, 1.0, 3.2), 26)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
