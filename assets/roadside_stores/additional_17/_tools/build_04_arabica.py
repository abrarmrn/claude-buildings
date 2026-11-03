"""ASSET 04 - % Arabica (minimalist premium coffee shop; premium restaurant frontage).

Plot 40 m x 32 m, road side faces -Y, origin = plot centre at finished ground.
Massing: white concrete volume, thin cantilevered roof slab on slim black posts, frameless glass front,
solid sign wall with an oversized '%' mark, pale stone terrace with slim black furniture, back-lit white stele.
Branding is a simplified recreation (light geometric sans), not the official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-20.0, -16.0, 20.0, 16.0)
BX0, BY0, BX1, BY1 = -6.0, 1.0, 6.0, 9.5
H = 4.6
SLAB = (-7.5, -4.6, 7.5, BY1)             # one thin roof slab running over the terrace
GX0, GX1 = -5.4, 1.9                        # frameless glazing
WALL = (2.2, 6.0)                           # solid sign wall (x range)
DECK = (-10.0, -5.2, 10.0, BY0)
ENTRY, EXIT = (-19.0, -14.0), (14.0, 19.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-20.0, -14.0, -19.2, 16.0), (19.2, -14.0, 20.0, 16.0), (-19.0, 14.5, 19.0, 16.0)]

defmat('AR_White', '#f2f1ee', rough=0.5)
defmat('AR_WhiteGlow', '#f2f1ee', rough=0.5, emit='#fff1dc', es=0.25)
defmat('AR_Panel', '#ffffff', rough=0.4, emit='#fff4e4', es=2.2)
defmat('AR_Black', '#101112', rough=0.35, metal=0.3)
defmat('AR_Letter', '#0c0c0d', rough=0.4)
defmat('AR_Stone', '#cfcac0', rough=0.6)
defmat('AR_Wood', '#b58a5b', rough=0.5)
defmat('AR_Warm', '#ffffff', rough=0.3, emit='#ffc78a', es=3.0)
defmat('AR_Menu', '#17130f', rough=0.25, emit='#ffe2b8', es=0.7)


def arabica_mark(acc, L, M, scale=1.0, depth=0.05, with_sub=True):
    """Black '% ARABICA' lockup (simplified, light geometric sans)."""
    txt(acc, L, '%', M @ Matrix.Translation((0, 0.65 * scale, 0)), 2.0 * scale, depth, 'light', 'AR_Letter', 'AR_Letter')
    if with_sub:
        txt(acc, L, 'ARABICA', M @ Matrix.Translation((0, -0.95 * scale, 0)), 0.64 * scale, depth, 'semi', 'AR_Letter', 'AR_Letter', spacing=1.55)


# ------------------------------------------------------------------ ground
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (9.8, -15.4, 12.4, -14.0)]
    site_ground(A, L, PLOT, holes, [DECK], BEDS, paver_h=0.1, mat_paved='RS_Travertine')
    land = A.m(L, 'Landscape')
    palms(A, L, [(18.5, -13.0), (-18.5, 8.0), (18.5, 8.0)], 160)
    for i in range(14):
        x = -12.0 + i * 1.7
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 9.0 < x < 13.5:
            continue
        R.grass_clump(land, L, x, -15.0, 0.9, seed=i)
    for i in range(10):
        R.grass_clump(land, L, -19.6, -11.0 + i * 2.2, 0.8, seed=30 + i)
        R.grass_clump(land, L, 19.6, -11.0 + i * 2.2, 0.8, seed=50 + i)
    entry_exit(A, L, PLOT, -16.5, 16.5, depth=1.8)
    cars = {1: ('RS_CarWhite', 'sedan')}
    parking_row(A, L, -9.0, -12.5, -7.5, 7, 2.6, cars)
    disabled_bay(A, L, -9.0 + 2.6 * 7 + 1.3, -12.5, -7.5)
    fur = A.m(L, 'Furniture')
    rng = random.Random(6)
    for i, (x, y) in enumerate(((-7.5, -3.2), (-4.2, -3.6), (-1.0, -3.2), (2.3, -3.6), (5.6, -3.2), (8.3, -1.0))):
        cafe_set(fur, L, x, y, 2 if i % 2 else 3, ang=rng.uniform(0, 120), table_mat='AR_White', chair_mat='AR_Black', seat_mat='AR_Black', r=0.32)
    for x in (-8.5, 7.0):
        planter(fur, L, x - 0.8, -0.1, x + 0.8, 0.8, 0.5, 'AR_White', 'RS_Foliage2', seed=int(x * 3))
    bench(fur, L, 8.6, 3.0, 2.2, 90, 'AR_Wood')
    bin_(fur, L, 9.2, -4.2, 'AR_Black')
    # in-ground uplights along the facade (read as small emissive discs)
    if L < 2:
        up = A.m(L, 'FacadeLights')
        for x in (-4.5, -2.5, -0.5, 1.5, 3.5, 5.5):
            up.add(bm_cyl(x, BY0 - 0.9, 0.1, 0.125, 0.09, 10), 'AR_Warm')


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.02 if L == 0 else 0.0
    t = 0.3
    hx0, hx1 = GX0 - 0.0, GX1
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'AR_White', t=t, holes=[(hx0, 0.15, hx1, 4.05)], front_mat='AR_WhiteGlow', roof_mat='AR_White',
          roof_t=0.28, rooftop=True, skip=('roof',))
    # single thin roof slab running 5.6 m over the terrace
    x0, y0, x1, y1 = SLAB
    b.add(bm_box(x0, y0, H - 0.28, x1, y1, H, bevel=bv), 'AR_White')
    if L < 2:
        b.add(bm_box(x0 + 0.1, y0 + 0.05, H - 0.31, x1 - 0.1, y0 + 0.2, H - 0.28), 'AR_Warm')
        n = 3
        for i in range(n):
            cx = -4.0 + i * 4.0
            b.add(bm_box(cx - 0.9, BY1 - 3.5, H, cx + 0.9, BY1 - 2.2, H + 0.8, bevel=bv, open_bottom=True), 'RS_MetalGalv')
    for (px, py) in ((-7.1, -4.2), (7.1, -4.2)):
        b.add(bm_box(px - 0.06, py - 0.06, 0.1, px + 0.06, py + 0.06, H - 0.28, open_bottom=False), 'AR_Black')
    # sign wall: slightly raised white panel carrying the black lockup
    b.add(bm_box(WALL[0] + 0.1, BY0 - 0.1, 0.15, WALL[1], BY0, 4.3, bevel=bv, open_bottom=True), 'AR_Panel')
    s = A.m(L, 'Signage')
    arabica_mark(s, L, place('-Y', ((WALL[0] + WALL[1]) / 2 + 0.05, BY0 - 0.1, 2.85)), 1.0, 0.05)
    # fascia line text on the slab edge
    if L == 0:
        register_sign(A, '% ARABICA wall lockup', ((WALL[0] + WALL[1]) / 2 + 0.05, BY0 - 0.14, 1.9), 0.46, width=2.9)
    glazing(A, L, hx0, hx1, 0.15, 4.05, BY0 + 0.1, nx=4, trans=(), doors=((-1.6, 2.0),), frame='AR_Black', door_h=2.4, frameless=True)
    # glass fin returns
    if L < 2:
        gl = A.m(L, 'Glass')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.95, 'RS_TileFloor', 'AR_White',
                        lights=light_grid((ix0, iy0, ix1, iy1), 4, 2, (1.3, 0.12), 1.1), back_mat='AR_White')
    counter(it, L, -4.5, 6.0, 4.0, 7.0, 1.05, 'AR_White', 'AR_Wood')
    it.add(bm_box(-5.0, iy1 - 0.6, 0.15, 5.2, iy1, 1.0, open_bottom=True), 'AR_White')
    for i in range(3):
        x = -3.5 + i * 3.4
        it.add(bm_box(x - 1.0, iy1 - 0.06, 1.5, x + 1.0, iy1 - 0.03, 2.8), 'AR_Menu')
    if L == 0:
        for x in (-3.0, -1.6):
            it.add(bm_box(x - 0.3, 6.2, 1.1, x + 0.3, 6.8, 1.5, bevel=0.02), 'RS_MetalBrushed')
        for i in range(4):
            stool(it, L, -2.0 + i * 1.5, 5.3, 0.65, 'AR_Black', 'AR_Wood')
    for i, (x, y) in enumerate(((-3.5, 3.0), (-0.5, 3.2), (3.0, 3.0))):
        cafe_set(it, L, x, y, 2, ang=90 * i, table_mat='AR_White', chair_mat='AR_Black', seat_mat='AR_Wood', r=0.3)
    # pendant globes
    for (x, y) in ((-3.5, 3.0), (-0.5, 3.2), (3.0, 3.0), (-2.0, 6.5), (2.0, 6.5)):
        it.add(bm_sphere((x, y, 2.9), 0.2, 2 if L == 0 else 1), 'AR_Warm')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 11.2, -14.7
    bv = 0.02 if L == 0 else 0.0
    t.add(bm_box(cx - 1.4, cy - 0.25, 0.0, cx + 1.4, cy + 0.25, 4.6, bevel=bv, open_bottom=True), 'AR_Panel')
    t.add(bm_box(cx - 1.4, cy - 0.27, 0.0, cx + 1.4, cy - 0.25, 0.2), 'AR_Black')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.25), ('+Y', cy + 0.25)):
        arabica_mark(s, L, place(face, (cx, yy, 2.55)), 0.85, 0.05)
    if L == 0:
        register_sign(A, '% ARABICA stele lockup', (cx, cy - 0.3, 1.6), 0.4, width=2.4)


LAMPS = [(-16.0, -13.5, 0, 1), (0.0, -13.5, 0, 1), (16.0, -13.5, 0, 1), (-18.5, 2.0, 1, 0), (18.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0, 0.0, BX1, BY1, H)
    A.col_box('RoofSlab', SLAB[0], SLAB[1], H - 0.28, SLAB[2], BY0, H)
    A.col_box('Deck', *DECK[:2], 0.0, *DECK[2:], 0.1)
    A.col_box('Stele', 9.8, -14.95, 0.0, 12.6, -14.45, 4.6)
    for i, x in enumerate((-7.1, 7.1)):
        A.col_box(f'Post{i}', x - 0.1, -4.3, 0.0, x + 0.1, -4.1, H - 0.28)
    lamp_collision(A, LAMPS, 7.0)


def build_lights(A):
    for i, x in enumerate((-4.0, 0.0, 4.0)):
        A.light(f'Soffit{i}', 'SPOT', (x, -2.5, H - 0.35), 700, '#ffe1bd', spot_deg=125, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-3.0, 4.0, 3.5), (1.0, 4.0, 3.5), (3.5, 7.0, 3.5)], energy=700, color='#ffd9a8')
    sign_light(A, 'WallGlow', (4.0, -3.0, 3.0), 1500, '#fff0dc')
    sign_light(A, 'SteleGlow', (11.2, -18.0, 2.8), 1000, '#fff0dc')
    lamp_lights(A, LAMPS, 6.9, 1.0, 1600)


def main():
    A = Store('04', '04_percent_arabica', 'percent_arabica', 'ARAB', 'CoffeeShop', '% Arabica')
    A.dims = dict(plot=[40.0, 32.0], building=[BX1 - BX0, BY1 - BY0, H], roof_cantilever=BY0 - SLAB[1], stele_height=4.6)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS, 7.0, 1.0)
    build_collision(A); build_lights(A)
    A.camera('day', (-15.0, -23.0, 3.5), (0.5, 3.0, 2.4), 34)
    A.camera('road', (-21.0, PLOT[1] - 8.6, 1.25), (4.0, -3.0, 2.4), 32)
    A.camera('detail', (-2.0, -10.0, 1.7), (3.5, 1.0, 2.5), 30)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
