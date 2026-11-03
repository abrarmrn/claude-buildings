"""ASSET 12 - Subway (compact roadside sandwich shop; general commercial retail).

Plot 36 m x 26 m, road side faces -Y, origin = plot centre at finished ground.
Massing: compact glass-fronted unit, yellow sloping entrance canopy, green sign board with the double-arrow
wordmark (simplified polygons), visible sandwich counter, pole sign, shared parking frontage.
Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-18.0, -13.0, 18.0, 13.0)
BX0, BY0, BX1, BY1 = -5.5, 1.0, 5.5, 8.0
H = 5.6
GX0, GX1, GZ1 = -4.9, 4.9, 3.35
DOOR_X = 0.8
ENTRY, EXIT = (-17.0, -12.0), (12.0, 17.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-18.0, -11.0, -17.2, 13.0), (17.2, -11.0, 18.0, 13.0), (-17.0, 11.5, 17.0, 13.0)]
PAVED = [(-7.5, -3.0, 7.5, BY0)]

defmat('SW_Green', '#0a8f3c', rough=0.35, spec=0.6)
defmat('SW_GreenLit', '#0a8f3c', rough=0.32, emit='#18c050', es=0.6)
defmat('SW_Yellow', '#ffc20e', rough=0.35, spec=0.6)
defmat('SW_YellowLit', '#ffc20e', rough=0.32, emit='#ffc828', es=1.1)
defmat('SW_White', '#f6f4ee', rough=0.4)
defmat('SW_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('SW_Menu', '#10120f', rough=0.25, emit='#fff0c0', es=0.9)
defmat('SW_Tomato', '#c8281c', rough=0.5)
defmat('SW_Lettuce', '#6dbb3a', rough=0.6)
defmat('SW_Cheese', '#f2c230', rough=0.5)
defmat('SW_Onion', '#a56bb5', rough=0.6)
defmat('SW_Olive', '#222a1a', rough=0.5)


def arrow(acc, L, M, w=0.6, h=0.5, depth=0.06, mat='SW_YellowLit', flip=False):
    s = -1 if flip else 1
    pts = [(-0.5 * w * s, -0.15 * h), (0.15 * w * s, -0.15 * h), (0.15 * w * s, -0.5 * h), (0.5 * w * s, 0.0), (0.15 * w * s, 0.5 * h), (0.15 * w * s, 0.15 * h), (-0.5 * w * s, 0.15 * h)]
    acc.add(bm_prism_local(pts, depth), mat, matrix=M, mat_fn=front_back(mat, 'SW_Yellow'))


def sw_logo(acc, L, M, size=1.0, depth=0.07):
    """SUBWAY wordmark with arrow end-caps (simplified polygons, not the official artwork)."""
    txt(acc, L, 'SUBWAY', M, size, depth, 'black', 'SW_SignWhite', 'SW_White', spacing=1.06)
    arrow(acc, L, M @ Matrix.Translation((-size * 2.25, size * 0.18, 0)), size * 0.7, size * 0.6, depth)
    arrow(acc, L, M @ Matrix.Translation((size * 2.25, -size * 0.18, 0)), size * 0.7, size * 0.6, depth, flip=True)


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (11.0, -12.6, 14.0, -11.0)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(16.5, -10.0), (-16.5, 6.0), (16.5, 6.0), (-8.0, 11.8), (8.0, 11.8)], 240)
    for i in range(16):
        x = -11.0 + i * 1.4
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 10.0 < x < 14.5 or ENTRY[0] - 1 < x < ENTRY[1] + 1:
            continue
        (R.grass_clump(land, L, x, -12.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -12.0, 0.7, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -14.5, 14.5, depth=1.8)
    cars = {4: ('RS_CarBlue', 'suv'), 7: ('RS_CarSilver', 'sedan')}
    parking_row(A, L, -11.7, -10.5, -5.5, 9, 2.6, cars)
    disabled_bay(A, L, -11.7 + 2.6 * 9 + 1.3, -10.5, -5.5)
    fur = A.m(L, 'Furniture')
    for i, (x, y) in enumerate(((-5.5, -1.6), (-2.8, -2.2), (5.0, -1.8))):
        cafe_set(fur, L, x, y, 2, ang=30 * i, table_mat='SW_White', chair_mat='RS_MetalDark', seat_mat='SW_Yellow', r=0.32)
    planter(fur, L, -7.4, -0.5, -6.2, 0.7, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=1)
    planter(fur, L, 6.2, -0.5, 7.4, 0.7, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=4)
    bin_(fur, L, 3.2, -1.5, 'SW_Green')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'SW_White', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='SW_White', roof_mat='SW_White', roof_t=0.35, parapet=0.35, parapet_mat='SW_Green')
    # green side panels, yellow band, sign board
    b.add(bm_box(BX0 - 0.02, BY0 - 0.12, 0.0, GX0, BY0, GZ1 + 0.2, bevel=bv, open_bottom=True), 'SW_Green')
    b.add(bm_box(GX1, BY0 - 0.12, 0.0, BX1 + 0.02, BY0, GZ1 + 0.2, bevel=bv, open_bottom=True), 'SW_Green')
    b.add(bm_box(BX0, BY0 - 0.15, GZ1 + 0.1, BX1, BY0, H - 0.1, bevel=bv), 'SW_GreenLit')
    b.add(bm_box(BX0 - 0.05, BY0 - 0.2, GZ1 + 0.05, BX1 + 0.05, BY0, GZ1 + 0.3), 'SW_YellowLit')
    # sloping yellow canopy over the entrance (wedge, profile in YZ)
    prof = [(BY0, 3.95), (BY0 - 2.3, 3.4), (BY0 - 2.3, 3.7), (BY0, 4.25)]
    cp = A.m(L, 'Canopy')
    cp.add(bm_prism_local(prof, 7.0), 'SW_Yellow', matrix=place('+X', (-3.0, 0, 0)))
    cp.add(bm_box(-3.0, BY0 - 2.32, 3.4, 4.0, BY0 - 2.25, 3.7, bevel=bv), 'SW_Green')
    for x in (-2.8, 3.8):
        cp.add(bm_cyl(x, BY0 - 2.0, 0.0, 3.4, 0.06, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    sw_logo(s, L, place('-Y', (0.0, BY0 - 0.15, 4.8)), 0.85, 0.07)
    txt(s, L, 'EAT FRESH', place('+X', (BX1 + 0.02, 4.0, 2.4)), 0.4, 0.03, 'xbold_i', 'SW_YellowLit', 'SW_Yellow', min_size_lod2=9)
    sw_logo(s, L, place('+X', (BX1 + 0.02, 4.0, 4.6)), 0.55, 0.05)
    if L == 0:
        register_sign(A, 'SUBWAY wordmark', (0.0, BY0 - 0.26, 4.8), 0.62, width=4.0)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=6, trans=(), doors=((DOOR_X, 2.0),), frame='SW_Green', door_h=2.3)
    if L < 2:
        gl = A.m(L, 'Glass')
        gl.add(bm_vquad(GX0, GX1, 0.85, 1.0, BY0 + 0.07), 'SW_Yellow')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.2, 'RS_TileFloor', 'SW_White', lights=light_grid((ix0, iy0, ix1, iy1), 3, 2, (1.3, 0.25), 1.0), back_mat='SW_Green')
    # sandwich line: counter, food pans, sneeze guard, bread rack
    counter(it, L, -4.8, 4.4, 4.8, 5.4, 1.0, 'SW_Green', 'SW_Yellow')
    mats = ['SW_Tomato', 'SW_Lettuce', 'SW_Cheese', 'SW_Onion', 'SW_Olive', 'SW_Lettuce', 'SW_Tomato', 'SW_Cheese']
    for i in range(10):
        x = -4.3 + i * 0.95
        it.add(bm_box(x, 4.55, 0.98, x + 0.8, 5.25, 1.12), 'RS_MetalBrushed')
        if L == 0:
            it.add(bm_box(x + 0.05, 4.6, 1.1, x + 0.75, 5.2, 1.2), mats[i % 8])
        else:
            it.add(bm_box(x + 0.05, 4.6, 1.1, x + 0.75, 5.2, 1.18), mats[i % 8])
    it.add(bm_quad((-4.8, 5.35, 1.15), (4.8, 5.35, 1.15), (4.8, 4.85, 1.65), (-4.8, 4.85, 1.65)), 'RS_Glass')
    it.add(bm_box(ix0, iy1 - 0.7, 0.15, ix1, iy1, 1.2, open_bottom=True), 'RS_PaintCharcoal')
    for i in range(3):
        x = -3.2 + i * 3.2
        it.add(bm_box(x - 1.1, iy1 - 0.06, 1.6, x + 1.1, iy1 - 0.03, 2.8), 'SW_Menu')
    for i, x in enumerate((-3.0, 0.0, 3.0)):
        cafe_set(it, L, x, 2.6, 2, ang=90 * (i % 2), table_mat='SW_White', chair_mat='RS_MetalDark', seat_mat='SW_Green', r=0.3)


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 12.5, -11.7
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.0, cy - 0.35, 0.0, cx + 1.0, cy + 0.35, 0.3, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_cyl(cx, cy, 0.3, 6.0, 0.22, 12 if L == 0 else 6, open_bottom=True), 'RS_MetalDark')
    t.add(bm_box(cx - 1.7, cy - 0.25, 4.4, cx + 1.7, cy + 0.25, 6.4, bevel=bv), 'SW_GreenLit')
    t.add(bm_box(cx - 1.72, cy - 0.27, 4.3, cx + 1.72, cy + 0.27, 4.45), 'SW_YellowLit')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.25), ('+Y', cy + 0.25)):
        sw_logo(s, L, place(face, (cx, yy, 5.4)), 0.5, 0.05)
    if L == 0:
        register_sign(A, 'SUBWAY pole sign', (cx, cy - 0.31, 5.4), 0.36, width=2.0)


LAMPS = [(8.0, -12.0, 0, 1), (-16.5, 2.0, 1, 0), (16.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H + 0.35)
    A.col_box('Canopy', -3.0, BY0 - 2.3, 3.3, 4.0, BY0, 4.3)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    A.col_box('PoleSign', 11.0, -12.0, 0.0, 14.0, -11.4, 6.4)
    lamp_collision(A, LAMPS, 7.5)


def build_lights(A):
    for i, x in enumerate((-2.5, 0.8, 3.5)):
        A.light(f'Canopy{i}', 'SPOT', (x, BY0 - 1.5, 3.35), 600, '#fff0d8', rot=(180, 0, 0), spot_deg=120, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-2.5, 4.0, 3.0), (1.5, 4.0, 3.0), (-1.0, 6.5, 3.0)], energy=800, color='#fff4e0')
    sign_light(A, 'BoardGlow', (0.0, -3.0, 4.8), 1700, '#e8fff0')
    sign_light(A, 'PoleGlow', (12.5, -14.0, 5.0), 1200, '#e8fff0')
    lamp_lights(A, LAMPS, 7.4, 1.2, 1900)


def main():
    A = Store('12', '12_subway', 'subway', 'SUB', 'SandwichShop', 'Subway')
    A.dims = dict(plot=[36.0, 26.0], building=[BX1 - BX0, BY1 - BY0, H], pole_sign_height=6.4)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS, 7.5, 1.2)
    build_collision(A); build_lights(A)
    A.camera('day', (-13.0, -18.5, 3.6), (0.5, 3.0, 2.9), 32)
    A.camera('road', (-20.0, PLOT[1] - 8.6, 1.25), (1.0, -3.0, 3.6), 32)
    A.camera('detail', (3.0, -8.0, 1.7), (0.0, 1.0, 3.4), 28)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
