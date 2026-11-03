"""ASSET 11 - Shake Shack (standalone modern restaurant; premium restaurant frontage).

Plot 44 m x 34 m, road side faces -Y, origin = plot centre at finished ground.
Massing: timber-slat volume + glass pavilion, signature gable-roofed entrance porch, cream sign band with green
lettering and a shack-roof mark, large timber terrace with pergola, string lights and landscape planters.
Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-22.0, -17.0, 22.0, 17.0)
BX0, BY0, BX1, BY1 = -9.0, 2.0, 6.0, 11.0
H = 4.9
SX1 = -3.4                                  # timber volume x range: BX0..SX1
GX0, GX1, GZ1 = -3.2, 5.6, 4.05
DOOR_X = 1.2
PORCH = (-0.7, 3.1)
DECK = (-13.0, -6.5, 11.0, BY0)
ENTRY, EXIT = (-21.0, -15.5), (15.5, 21.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.0) + [(-22.0, -15.0, -21.0, 17.0), (21.0, -15.0, 22.0, 17.0), (-21.0, 15.0, 21.0, 17.0)]

defmat('SS_Green', '#4f8f2c', rough=0.38, spec=0.5)
defmat('SS_GreenLit', '#4f8f2c', rough=0.35, emit='#7bd04a', es=1.1)
defmat('SS_DarkGreen', '#27502a', rough=0.4)
defmat('SS_Cream', '#e9e2d3', rough=0.45)
defmat('SS_Panel', '#f4efe3', rough=0.4, emit='#fff1d8', es=1.6)
defmat('SS_Roof', '#3d6b30', rough=0.4, metal=0.4)
defmat('SS_Menu', '#12130f', rough=0.25, emit='#ffe9b8', es=0.9)
defmat('SS_Bulb', '#ffffff', rough=0.3, emit='#ffd28a', es=7.0)


def shack_mark(acc, L, M, w=1.6, depth=0.07, mat='SS_GreenLit'):
    """Simplified shack-roof mark (gable house silhouette)."""
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, w * 0.45), (0.0, w * 0.95), (-w / 2, w * 0.45)]
    pts = [(x, y - w * 0.45) for x, y in pts]
    acc.add(bm_prism_local(pts, depth), mat, matrix=M, mat_fn=front_back(mat, 'SS_Green'))
    acc.add(bm_box(-w * 0.12, -w * 0.45, 0.0, w * 0.12, -w * 0.05, depth * 1.5), 'SS_Cream', matrix=M)


def string_lights(acc, L, x0, y0, x1, y1, z, n=12, sag=0.35):
    if L > 0:
        return
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        zz = z - sag * 4 * t * (1 - t)
        acc.add(bm_sphere((x, y, zz), 0.07, 1), 'SS_Bulb')
        if i < n:
            t2 = (i + 1) / n
            acc.add(bm_cyl_between((x, y, zz), (x0 + (x1 - x0) * t2, y0 + (y1 - y0) * t2, z - sag * 4 * t2 * (1 - t2)), 0.008, 3, caps=False), 'RS_PlasticBlack')


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (10.5, -16.7, 13.8, -15.0)]
    site_ground(A, L, PLOT, holes, [DECK], BEDS, paver_h=0.15, mat_paved='RS_Wood')
    land = A.m(L, 'Landscape')
    palms(A, L, [(20.5, -14.0), (-20.5, 8.0), (20.5, 8.0), (-6.0, 15.8), (8.0, 15.8)], 230)
    rng = random.Random(61)
    for i in range(20):
        x = -14.0 + i * 1.5
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 14.5:
            continue
        R.shrub(land, L, x, -16.0 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage' if i % 2 else 'RS_Foliage2')
    entry_exit(A, L, PLOT, -18.5, 18.5, depth=2.0)
    cars = {1: ('RS_CarSilver', 'suv'), 6: ('RS_CarBlue', 'sedan')}
    parking_row(A, L, -11.0, -14.0, -9.0, 8, 2.6, cars)
    disabled_bay(A, L, -11.0 + 2.6 * 8 + 1.3, -14.0, -9.0)
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(2)
    pergola(fur, L, -11.5, -5.8, -3.0, -0.8, 2.9, mat='RS_WoodV')
    for i, (x, y) in enumerate(((-9.5, -3.6), (-6.5, -2.6), (-4.2, -4.4), (5.0, -3.4), (8.0, -2.4), (9.2, -5.0))):
        cafe_set(fur, L, x, y, 4 if i % 2 else 2, ang=rng2.uniform(0, 90), table_mat='SS_Cream', chair_mat='SS_DarkGreen', seat_mat='SS_Green', r=0.36)
    string_lights(fur, L, -11.5, -5.8, -3.0, -5.8, 2.85)
    string_lights(fur, L, -11.5, -0.8, -3.0, -0.8, 2.85)
    string_lights(fur, L, -11.5, -3.3, -3.0, -3.3, 2.85)
    # landscape planters: long timber planters with shrubs and small trees
    for (x0, y0, x1, y1) in ((-13.0, -6.6, -4.0, -5.9), (3.0, -6.6, 11.0, -5.9), (-13.0, -0.6, -12.2, 1.8), (10.2, -0.6, 11.0, 1.8)):
        planter(fur, L, x0, y0, x1, y1, 0.6, 'RS_WoodV', 'RS_Foliage', seed=int(x0 + y0))
    for x in (-8.0, 7.0):
        topiary(fur, L, x, -7.4, 2.0, 0.55, 'SS_DarkGreen', 'RS_Foliage')
    bench(fur, L, 8.5, 0.6, 2.2, 0, 'RS_WoodV')
    bin_(fur, L, -2.0, -5.4, 'SS_DarkGreen')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'SS_Cream', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='SS_Cream', roof_mat='SS_Cream', roof_t=0.35, parapet=0.4, parapet_mat='SS_DarkGreen')
    # timber slat volume on the left
    b.add(bm_box(BX0 - 0.02, BY0 - 0.15, 0.0, SX1, BY0, H - 0.1, bevel=bv, open_bottom=True), 'RS_WoodV')
    b.add(bm_box(BX0 - 0.15, BY0 - 0.15, 0.0, BX0, BY1 - 1.0, H - 0.1, bevel=bv, open_bottom=True), 'RS_WoodV')
    # cream sign band along the whole front above the glazing + green roof edge
    b.add(bm_box(GX0, BY0 - 0.12, GZ1, BX1, BY0, H + 0.4, bevel=bv), 'SS_Panel')
    b.add(bm_box(BX0 - 0.2, BY0 - 0.1, H - 0.1, BX1 + 0.2, BY0 + 1.2, H + 0.2, bevel=bv), 'SS_DarkGreen')
    b.add(bm_box(BX0 - 0.2, BY0 - 0.55, H + 0.38, GX0, BY0 + 1.2, H + 0.6, bevel=bv), 'SS_DarkGreen')
    # signature gable-roofed entrance porch (triangular prism, wood gable face, green roof planes)
    px0, px1 = PORCH
    gp = [(px0 - 0.4, 3.1), (px1 + 0.4, 3.1), ((px0 + px1) / 2, 4.2)]
    cp = A.m(L, 'Canopy')
    cp.add(bm_prism_local(gp, 3.1), 'SS_Roof', matrix=place('-Y', (0.0, BY0, 0.0)), mat_fn=front_back('RS_WoodV', 'SS_Roof'))
    if L < 2:
        cp.add(bm_box(px0 - 0.4, BY0 - 3.05, 3.05, px1 + 0.4, BY0, 3.15), 'SS_DarkGreen')
    for x in (px0, px1):
        cp.add(bm_box(x - 0.1, BY0 - 2.9, 0.1, x + 0.1, BY0 - 2.7, 3.05, open_bottom=False), 'RS_WoodV')
    s = A.m(L, 'Signage')
    # sign band lettering
    txt(s, L, 'SHAKE SHACK', place('-Y', (1.5, BY0 - 0.12, 4.95)), 0.8, 0.07, 'black', 'SS_GreenLit', 'SS_Green', spacing=1.06)
    shack_mark(s, L, place('-Y', (-1.65, BY0 - 0.12, 4.95)), 0.9, 0.07)
    txt(s, L, 'SHAKE SHACK', place('-Y', ((BX0 + SX1) / 2, BY0 - 0.15, 3.2)), 0.45, 0.05, 'black', 'SS_Cream', 'SS_Cream', spacing=1.04, min_size_lod2=9)
    shack_mark(s, L, place('-X', (BX0 - 0.17, 5.0, 3.2)), 1.1, 0.06)
    if L == 0:
        register_sign(A, 'SHAKE SHACK sign band', (1.5, BY0 - 0.22, 4.95), 0.58, width=5.4)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=7, trans=(2.6,), doors=((DOOR_X, 2.2),), frame='SS_DarkGreen', door_h=2.3, frameless=False)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = SX1 + 0.1, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.85, 'RS_TileFloor', 'SS_Cream', lights=[], back_mat='SS_DarkGreen')
    for (x, y) in ((-1.5, 4.0), (1.5, 4.0), (4.5, 4.0), (-0.5, 7.0), (3.0, 7.0)):
        it.add(bm_cyl(x, y, 2.7, 3.85, 0.01, 4, caps=False), 'RS_PlasticBlack')
        it.add(bm_cyl(x, y, 2.45, 2.75, 0.3, 12 if L == 0 else 6, r2=0.1), 'SS_Bulb')
    counter(it, L, -3.0, 8.4, 5.0, 9.4, 1.05, 'RS_WoodV', 'SS_Cream')
    it.add(bm_box(ix0, iy1 - 0.8, 0.15, ix1, iy1, 2.2, open_bottom=True), 'RS_PaintCharcoal')
    for i in range(3):
        x = -1.5 + i * 3.2
        it.add(bm_box(x - 1.1, iy1 - 0.84, 2.3, x + 1.1, iy1 - 0.8, 3.5), 'SS_Menu')
    for j, y in enumerate((4.3, 6.5)):
        for i, x in enumerate((-1.5, 1.5, 4.2)):
            cafe_set(it, L, x, y, 2, ang=90 * ((i + j) % 2), table_mat='SS_Cream', chair_mat='SS_DarkGreen', seat_mat='RS_WoodV', r=0.32)
    # interior of the timber volume (lit service area)
    it.add(bm_hquad(BX0 + 0.3, BY0 + 0.3, SX1 - 0.1, BY1 - 0.3, 3.85, down=True), 'RS_LightWarm')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.2, -15.9
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.4, cy - 0.3, 0.0, cx + 1.4, cy + 0.3, 0.3, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 1.2, cy - 0.22, 0.3, cx + 1.2, cy + 0.22, 3.6, bevel=bv), 'RS_WoodV')
    t.add(bm_box(cx - 1.25, cy - 0.25, 3.6, cx + 1.25, cy + 0.25, 4.6, bevel=bv), 'SS_Panel')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.25), ('+Y', cy + 0.25)):
        txt(s, L, 'SHAKE', place(face, (cx, yy, 4.25)), 0.5, 0.05, 'black', 'SS_GreenLit', 'SS_Green', min_size_lod2=9)
        txt(s, L, 'SHACK', place(face, (cx, yy, 3.82)), 0.5, 0.05, 'black', 'SS_GreenLit', 'SS_Green', min_size_lod2=9)
        shack_mark(s, L, place(face, (cx, yy - 0.0, 2.2)), 1.1, 0.06)
    if L == 0:
        register_sign(A, 'SHAKE SHACK totem', (cx, cy - 0.3, 4.25), 0.36, width=2.0)


LAMPS = [(-4.0, -15.5, 0, 1), (5.0, -15.5, 0, 1), (18.0, -15.5, 0, 1), (-20.0, 3.0, 1, 0), (20.0, 3.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0 - 0.15, BY0 - 0.15, 0.0, BX1, BY1, H + 0.4)
    A.col_box('Porch', PORCH[0] - 0.4, BY0 - 3.1, 3.05, PORCH[1] + 0.4, BY0, 4.2)
    A.col_box('Deck', *DECK[:2], 0.0, *DECK[2:], 0.15)
    A.col_box('Totem', 10.8, -16.2, 0.0, 13.6, -15.6, 4.6)
    lamp_collision(A, LAMPS)


def build_lights(A):
    glow_lights(A, 'Interior', [(-1.0, 5.0, 3.4), (2.5, 5.0, 3.4), (4.5, 8.0, 3.4), (-6.0, 6.0, 3.4)], energy=1000, color='#ffd9a0')
    glow_lights(A, 'Terrace', [(-9.0, -3.3, 2.8), (-5.0, -3.3, 2.8), (7.0, -3.0, 2.8)], energy=800, color='#ffcf8a')
    A.light('Porch', 'SPOT', (1.2, BY0 - 1.5, 3.1), 800, '#ffe9c8', rot=(180, 0, 0), spot_deg=120, blend=0.8, radius=0.2)
    sign_light(A, 'BandGlow', (1.5, -4.0, 4.6), 1800, '#fff0d8')
    sign_light(A, 'TotemGlow', (12.2, -19.0, 3.8), 1000, '#fff0d8')
    lamp_lights(A, LAMPS)


def main():
    A = Store('11', '11_shake_shack', 'shake_shack', 'SHACK', 'Restaurant', 'Shake Shack')
    A.dims = dict(plot=[44.0, 34.0], building=[BX1 - BX0, BY1 - BY0, H], porch_ridge_height=4.2, totem_height=4.6)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-17.0, -25.0, 3.8), (-1.0, 3.0, 3.0), 32)
    A.camera('road', (-27.0, PLOT[1] - 8.6, 1.25), (0.0, -4.0, 3.6), 32)
    A.camera('detail', (3.0, -10.0, 1.7), (-1.0, 2.0, 3.4), 27)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
