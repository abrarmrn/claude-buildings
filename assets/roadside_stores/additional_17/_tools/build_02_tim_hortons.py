"""ASSET 02 - Tim Hortons (standalone roadside coffee shop with drive-through; drive-through cluster).

Plot 56 m x 42 m, road side faces -Y, origin = plot centre at finished ground.
Massing: brick-plinth glass cafe, deep red projecting fascia, white tower with brand panel + cup icon,
side pickup window with canopy, U-shaped drive-through lane (entry left, pickup east side, exit right),
red-umbrella patio, pole sign. Branding is a simplified recreation (no official script lettering).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-28.0, -21.0, 28.0, 21.0)
BX0, BY0, BX1, BY1 = -15.0, 2.0, 3.0, 13.0
H = 4.4
TX0, TX1, TY1, TH = -1.2, 3.0, 8.0, 6.7           # tower
GX0, GX1, GZ0, GZ1 = -14.2, -1.6, 0.75, 3.55       # glazing
PATIO = (-16.0, -6.5, -0.5, BY0)
ENTRY, EXIT = (-27.0, -20.5), (20.5, 27.0)
PICK_Y = (6.2, 7.9)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.2) + [(-28.0, 0.0, -22.8, 19.0), (-28.0, 18.4, 9.0, 21.0), (7.8, 0.5, 10.0, 18.4),
                                                     (27.0, -18.8, 28.0, 21.0), (10.0, 18.4, 28.0, 21.0)]

defmat('TH_Red', '#c8102e', rough=0.3, spec=0.6)
defmat('TH_RedLit', '#c8102e', rough=0.3, emit='#e8142f', es=0.55)
defmat('TH_RedFabric', '#b80f2a', rough=0.85, double=True)
defmat('TH_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('TH_Clad', '#f0eeea', rough=0.3, metal=0.1)
defmat('TH_Brown', '#4b2e1d', rough=0.5)
defmat('TH_Cup', '#f6f2ea', rough=0.45, emit='#ffffff', es=0.3)
defmat('TH_Menu', '#14100e', rough=0.25, emit='#ffcf9a', es=0.9)


def th_wordmark(acc, L, M, size, depth=0.07):
    """'Tim Hortons' in sheared bold italic (simplified; the official script lettering is not reproduced)."""
    txt(acc, L, 'Tim Hortons', M, size, depth, 'black_i', 'TH_SignWhite', 'RS_PaintWhite', spacing=0.98, shear=0.1)


def cup_icon(acc, L, x, y, z, s=1.0):
    seg = {0: 20, 1: 10, 2: 6}[L]
    acc.add(bm_cyl(x, y, z, z + 0.9 * s, 0.36 * s, seg, r2=0.27 * s), 'TH_Cup')
    acc.add(bm_cyl(x, y, z + 0.28 * s, z + 0.62 * s, 0.335 * s, seg, r2=0.30 * s, caps=False), 'TH_Red')
    acc.add(bm_cyl(x, y, z + 0.9 * s, z + 0.98 * s, 0.38 * s, seg), 'RS_PlasticBlack')


# ------------------------------------------------------------------ ground & drive-thru
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (13.0, -20.6, 16.0, -19.0)]
    site_ground(A, L, PLOT, holes, [PATIO], BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(-26.5, -19.0), (26.5, -19.0), (-26.5, 10.0), (26.5, 8.0), (-24.0, 19.6), (14.0, 19.6)], 120)
    rng = random.Random(8)
    for i in range(24):
        x = -19.0 + i * 1.5
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 12.0 < x < 17.0:
            continue
        if i % 3 == 0:
            R.grass_clump(land, L, x, -20.0, 0.8, seed=i)
        else:
            R.shrub(land, L, x, -20.0 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage' if i % 2 else 'RS_Foliage2')
    for i in range(10):
        R.shrub(land, L, -26.0, 2.0 + i * 1.8, 0.8, seed=60 + i)
        R.shrub(land, L, 8.9, 1.5 + i * 1.7, 0.7, seed=90 + i, mat='RS_Foliage2')
    entry_exit(A, L, PLOT, -23.5, 23.5, depth=2.2)
    if L < 2:
        mk = A.m(L, 'Markings')
        # drive-thru lane: edge lines + direction arrows (west leg up, back leg east, east leg down to the pickup window, then exit)
        for (x0, y0, x1, y1) in ((-21.0, -4.0, -20.9, 17.4), (-17.5, 0.0, -17.4, 13.5), (-21.0, 17.3, 7.7, 17.4), (-17.5, 13.5, 3.0, 13.6),
                                 (3.1, -4.0, 3.2, 13.6), (7.6, -4.0, 7.7, 17.4)):
            mk.add(bm_hquad(x0, y0, x1, y1, 0.006), 'RS_LineWhite' if x1 - x0 < 0.2 else 'RS_LineYellow')
        R.arrow_mark(mk, -19.2, 4.0, 90, 3.2); R.arrow_mark(mk, -19.2, 10.5, 90, 3.2)
        R.arrow_mark(mk, -8.0, 15.5, 0, 3.2); R.arrow_mark(mk, 0.0, 15.5, 0, 3.2)
        R.arrow_mark(mk, 5.4, 11.0, -90, 3.2); R.arrow_mark(mk, 5.4, 2.0, -90, 3.2)
        mk.add(bm_hquad(3.4, 6.0, 7.4, 6.35, 0.006), 'RS_LineWhite')
    # parking in front of the shop
    cars = {0: ('RS_CarWhite', 'sedan'), 9: ('RS_CarGrey', 'suv')}
    parking_row(A, L, -14.0, -17.0, -11.5, 10, 2.6, cars)
    disabled_bay(A, L, -14.0 + 2.6 * 10 + 1.3, -17.0, -11.5)
    v = A.m(L, 'Vehicles')
    car(v, L, 5.3, 9.5, -90, 'RS_CarBlue', 'sedan')
    car(v, L, -19.2, 7.5, 90, 'RS_CarBlack', 'suv')
    # drive-thru kit
    menu_board(A, L, -22.4, 6.0, '+X', body='TH_Brown', w=1.5)
    menu_board(A, L, -22.4, 10.0, '+X', body='TH_Brown', w=1.5)
    height_bar(A.m(L, 'DriveThru'), L, -19.2, -3.0, 4.0, 2.3)
    if L < 2:
        s = A.m(L, 'Signage')
        for y in (6.0, 10.0):
            txt(s, L, 'ORDER HERE', place('+X', (-22.26, y, 2.1)), 0.14, 0.01, 'bold', 'TH_SignWhite', min_size_lod2=9)
    # patio furniture: tables with red umbrellas
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(5)
    for i, (x, y) in enumerate(((-13.5, -3.6), (-10.0, -4.2), (-6.5, -3.6), (-3.0, -4.2), (-12.0, -0.3), (-5.0, -0.2))):
        cafe_set(fur, L, x, y, 4 if i % 2 == 0 else 2, ang=rng2.uniform(0, 90), table_mat='RS_PaintWhite', chair_mat='RS_MetalDark',
                 seat_mat='TH_Red', umb='TH_RedFabric' if i < 4 else None, umb2='RS_PaintWhite' if i < 4 else None)
    planter(fur, L, -16.0, -7.4, -0.5, -6.8, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=3)
    bin_(fur, L, -0.9, -5.0)
    bin_(fur, L, 6.2, -1.0)


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    # shell: front wall (brick plinth + upper wall), back wall, west wall, east wall with pickup window hole, roof
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'TH_Clad', t=t, holes=[(GX0, GZ0, GX1, GZ1)], front_mat='TH_Clad', roof_mat='TH_Clad', skip=('right',),
          parapet=0.4, parapet_mat='TH_Clad')
    # brick plinth strip across the front (outer layer) and brick piers each side
    b.add(bm_box(BX0, BY0 - 0.06, 0.0, BX1, BY0, GZ0, bevel=bv, open_bottom=True), 'RS_Brick')
    b.add(bm_box(BX0, BY0 - 0.06, GZ0, GX0, BY0, GZ1, bevel=bv), 'RS_Brick')
    b.add(bm_box(GX1, BY0 - 0.06, GZ0, BX1, BY0, GZ1, bevel=bv), 'RS_Brick')
    # east wall with the pickup window opening
    holes_e = [(PICK_Y[0], 1.15, PICK_Y[1], 2.45)]
    rects = [(BY0 + t, 0.15, BY1 - t, H - 0.3)]
    for hh in holes_e:
        rects = rect_subtract(rects, hh)
    for (y0, z0, y1, z1) in rects:
        b.add(bm_box(BX1 - t, y0, z0, BX1, y1, z1, open_bottom=z0 <= 0.2), 'TH_Clad')
    b.add(bm_box(BX1, BY0, 0.0, BX1 + 0.06, BY1, 1.15, open_bottom=True), 'RS_Brick')
    # rear service door + rooftop plant already added by shell()
    # tower
    b.add(bm_box(TX0, BY0 - 0.12, H - 0.3, TX1, TY1, TH, bevel=bv), 'TH_Clad')
    b.add(bm_box(TX0 - 0.05, BY0 - 0.2, TH - 0.9, TX1 + 0.05, TY1 + 0.05, TH + 0.2, bevel=bv), 'TH_Red')
    b.add(bm_box(TX0, BY0 - 0.12, 0.0, TX1, BY0 - 0.06, 2.6, bevel=bv, open_bottom=True), 'RS_Brick')
    # deep red projecting fascia over the glazing, white soffit + LED strip
    fy0 = BY0 - 1.1
    b.add(bm_box(BX0 - 0.15, fy0, 3.62, TX0, BY0, 4.95, bevel=bv), 'TH_RedLit')
    b.add(bm_box(BX0 - 0.15, fy0 + 0.04, 3.58, TX0, BY0, 3.62), 'RS_PaintWhite')
    if L < 2:
        b.add(bm_box(BX0 - 0.1, fy0 - 0.01, 3.55, TX0 - 0.05, fy0 + 0.05, 3.6), 'RS_LightWarm')
    # red mono-pitch canopy over the patio edge
    awn = A.m(L, 'Canopy')
    awning(awn, L, BX0 + 0.2, TX0 - 0.1, BY0 - 1.1, 3.45, 0.55, 2.5, ('TH_RedFabric',), strip=1.0, valance=0.2, frame_mat='RS_MetalDark')
    for x in (BX0 + 0.4, -8.0, TX0 - 0.4):
        awn.add(bm_cyl(x, BY0 - 3.55, 0.0, 3.0, 0.05, 8 if L == 0 else 5, open_bottom=True), 'RS_MetalDark')
    # pickup window: frame, sliding glass, shelf + red canopy on posts over the lane
    gl = A.m(L, 'Glass'); fr = A.m(L, 'Frames')
    gl.add(bm_quad((BX1 + 0.02, PICK_Y[1], 1.15), (BX1 + 0.02, PICK_Y[0], 1.15), (BX1 + 0.02, PICK_Y[0], 2.45), (BX1 + 0.02, PICK_Y[1], 2.45)),
           'RS_Glass' if L < 2 else 'RS_GlassLOD')
    if L < 2:
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 1.07, BX1 + 0.12, PICK_Y[1] + 0.08, 1.15), 'RS_MetalBrushed')
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 2.45, BX1 + 0.12, PICK_Y[1] + 0.08, 2.53), 'RS_MetalDark')
        for y in (PICK_Y[0] - 0.08, PICK_Y[1]):
            fr.add(bm_box(BX1, y, 1.07, BX1 + 0.12, y + 0.08, 2.53), 'RS_MetalDark')
        fr.add(bm_box(BX1, PICK_Y[0] + 0.3, 1.15, BX1 + 0.5, PICK_Y[1] - 0.3, 1.2), 'RS_MetalBrushed')
    cp = A.m(L, 'Canopy')
    cp.add(bm_box(BX1, 5.0, 3.0, BX1 + 2.8, 9.0, 3.3, bevel=bv), 'TH_RedLit')
    for (px, py) in ((BX1 + 2.6, 5.1), (BX1 + 2.6, 8.9)):
        cp.add(bm_cyl(px, py, 0.0, 3.0, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    txt(s, L, 'PICK UP', place('+X', (BX1 + 0.04, 7.05, 2.85)), 0.28, 0.03, 'black', 'TH_SignWhite', 'RS_PaintWhite', min_size_lod2=9)
    th_wordmark(s, L, place('+X', (BX1 + 0.04, 7.05, 3.9)), 0.62)
    # main brand sign on the fascia + the tower panel + cup
    th_wordmark(s, L, place('-Y', (-8.4, fy0 - 0.02, 4.28)), 1.0)
    s.add(bm_box(TX0 + 0.35, BY0 - 0.27, 3.4, TX1 - 0.35, BY0 - 0.12, 6.0, bevel=0.02 if L == 0 else 0), 'TH_RedLit')
    txt(s, L, 'Tim', place('-Y', ((TX0 + TX1) / 2, BY0 - 0.27, 5.45)), 0.8, 0.05, 'black_i', 'TH_SignWhite', 'RS_PaintWhite', shear=0.1)
    txt(s, L, 'Hortons', place('-Y', ((TX0 + TX1) / 2, BY0 - 0.27, 4.6)), 0.62, 0.05, 'black_i', 'TH_SignWhite', 'RS_PaintWhite', shear=0.1)
    cup_icon(s, L, (TX0 + TX1) / 2, BY0 - 0.5, TH + 0.2, 1.0)
    register_sign(A, 'Tim Hortons fascia wordmark', (-8.4, fy0 - 0.1, 4.28), 0.72, width=6.0) if L == 0 else None
    register_sign(A, 'Tim Hortons tower panel', ((TX0 + TX1) / 2, BY0 - 0.35, 5.0), 0.58, width=2.8) if L == 0 else None
    # glazing + doors
    glazing(A, L, GX0, GX1, GZ0, GZ1, BY0 + 0.1, nx=7, trans=(2.5,), doors=((-8.0, 2.0),), frame='RS_MetalDark', door_h=2.3, bottom_rail=0.06)
    if L < 2:
        # door handle plates + red vinyl band on the glazing
        gl.add(bm_vquad(GX0, GX1, 0.95, 1.2, BY0 + 0.07), 'TH_Red')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.5, 'RS_TileFloor', 'RS_InteriorWall',
                        lights=light_grid((ix0, iy0, ix1, iy1), 5, 2, (1.5, 0.3), 1.2))
    it.add(bm_vquad(ix0, ix1, 2.25, 3.2, iy1 - 0.004), 'TH_RedLit')
    # counter + back bar + menu screens
    counter(it, L, -13.0, 8.2, 2.0, 9.4, 1.05, 'TH_Brown', 'RS_PaintWhite')
    it.add(bm_box(-13.0, iy1 - 0.8, 0.15, 2.0, iy1, 1.0, open_bottom=True), 'RS_PaintCharcoal')
    for i in range(5):
        x = -12.0 + i * 3.4
        it.add(bm_box(x - 1.1, iy1 - 0.1, 1.55, x + 1.1, iy1 - 0.06, 2.55), 'TH_Menu')
    # donut / bakery display case + coffee machines
    it.add(bm_box(-5.5, 8.35, 1.2, -1.0, 9.25, 1.7, bevel=0.01 if L == 0 else 0), 'RS_Cooler')
    if L == 0:
        rng = random.Random(3)
        for i in range(14):
            x = -5.3 + i * 0.3
            it.add(bm_cyl(x, 8.8, 1.2, 1.26, 0.1, 10), rng.choice(['RS_Pink', 'RS_Choc', 'RS_Cream', 'RS_Pastry']))
        for x in (-11.0, -10.0, -9.0):
            it.add(bm_box(x - 0.25, 8.5, 1.1, x + 0.25, 9.0, 1.55, bevel=0.02), 'RS_MetalBrushed')
    # tables and chairs by the windows
    for i, x in enumerate((-12.5, -9.5, -6.5, -3.5)):
        cafe_set(it, L, x, 4.6, 2, ang=90 if i % 2 else 0, table_mat='RS_PaintWhite', chair_mat='RS_MetalDark', seat_mat='TH_Brown')
    for i, x in enumerate((-12.0, -8.0, -4.0)):
        cafe_set(it, L, x, 6.6, 4, ang=0, table_mat='RS_PaintWhite', chair_mat='RS_MetalDark', seat_mat='TH_Red')
    # brick feature wall (east) and drive-thru handoff shelf
    it.add(bm_quad((BX1 - 0.31, 12.5, 0.15), (BX1 - 0.31, 3.2, 0.15), (BX1 - 0.31, 3.2, 3.3), (BX1 - 0.31, 12.5, 3.3)), 'RS_Brick')


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = 14.5, -19.8
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.5, cy - 0.5, 0, cx + 1.5, cy + 0.5, 0.4, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 0.9, cy - 0.3, 0.4, cx + 0.9, cy + 0.3, 3.2, bevel=bv), 'TH_Clad')
    p.add(bm_box(cx - 1.4, cy - 0.3, 3.2, cx + 1.4, cy + 0.3, 6.6, bevel=bv), 'TH_RedLit')
    p.add(bm_box(cx - 1.45, cy - 0.33, 6.6, cx + 1.45, cy + 0.33, 6.75, bevel=bv), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.3), ('+Y', cy + 0.3)):
        txt(s, L, 'Tim', place(face, (cx, yy, 5.55)), 0.9, 0.06, 'black_i', 'TH_SignWhite', 'RS_PaintWhite', shear=0.1)
        txt(s, L, 'Hortons', place(face, (cx, yy, 4.45)), 0.75, 0.06, 'black_i', 'TH_SignWhite', 'RS_PaintWhite', shear=0.1)
        txt(s, L, 'DRIVE THRU', place(face, (cx, yy, 2.4)), 0.3, 0.03, 'bold', 'TH_Red', 'TH_Red', min_size_lod2=9)
        txt(s, L, '→', place(face, (cx, yy, 1.5)), 0.5, 0.03, 'bold', 'TH_Red', 'TH_Red', min_size_lod2=9)
    cup_icon(s, L, cx, cy, 6.75, 1.0)
    if L == 0:
        register_sign(A, 'Tim Hortons pole sign', (cx, cy - 0.36, 5.0), 0.7, width=2.6)


def build_lamps(A, L):
    lamp_set(A, L, LAMPS)


LAMPS = [(-10.0, -19.8, 0, 1), (4.0, -19.8, 0, 1), (22.0, -19.8, 0, 1), (-26.0, 4.0, 1, 0), (26.0, 4.0, -1, 0), (10.0, 19.6, 0, -1)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0, 0.0, BX1, BY1, H)
    A.col_box('Tower', TX0, BY0 - 0.2, 0.0, TX1, TY1, TH)
    A.col_box('Fascia', BX0 - 0.15, BY0 - 1.1, 3.55, TX0, BY0, 4.95)
    A.col_box('PickupCanopy', BX1, 5.0, 3.0, BX1 + 2.8, 9.0, 3.3)
    A.col_box('Pylon', 13.1, -20.3, 0.0, 15.9, -19.3, 6.75)
    A.col_box('Patio', *PATIO[:2], 0.0, *PATIO[2:], 0.12)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-12.0, -8.0, -4.0)):
        A.light(f'Fascia{i}', 'SPOT', (x, BY0 - 1.0, 3.5), 1100, '#fff0e0', spot_deg=120, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-11.0, 6.5, 3.2), (-6.0, 6.5, 3.2), (-1.0, 6.5, 3.2), (-8.0, 10.5, 3.2)], energy=1100, color='#ffe7c8')
    glow_lights(A, 'Patio', [(-12.0, -2.5, 2.3), (-6.0, -2.5, 2.3)], kind='SPOT', energy=1500, color='#ffe9cf', spot_deg=140, blend=0.8)
    sign_light(A, 'PylonGlow', (14.5, -22.5, 5.0), 1500, '#ffd8d8')
    sign_light(A, 'TowerGlow', (1.0, -3.0, 5.5), 1500, '#ffd8d8')
    A.light('PickupGlow', 'SPOT', (BX1 + 1.5, 7.0, 3.0), 700, '#fff2e0', rot=(180, 0, 0), spot_deg=110, blend=0.8, radius=0.2)
    lamp_lights(A, LAMPS)


def main():
    A = Store('02', '02_tim_hortons', 'tim_hortons', 'TIMS', 'CoffeeShop', 'Tim Hortons')
    A.dims = dict(plot=[56.0, 42.0], building=[BX1 - BX0, BY1 - BY0, H], tower_height=TH + 1.2, pylon_height=6.75)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L); build_lamps(A, L)
    build_collision(A); build_lights(A)
    A.camera('day', (-22.0, -29.0, 3.6), (-5.0, 3.0, 2.9), 32)
    A.camera('road', (-30.0, PLOT[1] - 8.6, 1.25), (2.0, -6.0, 3.3), 30)
    A.camera('detail', (3.0, -10.5, 1.7), (-5.0, 2.0, 3.5), 26)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
