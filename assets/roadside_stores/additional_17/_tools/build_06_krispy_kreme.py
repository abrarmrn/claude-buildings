"""ASSET 06 - Krispy Kreme (modern donut + coffee shop with drive-through; drive-through cluster).

Plot 48 m x 38 m, road side faces -Y, origin = plot centre at finished ground.
Massing: white volume with a deep glass 'doughnut theatre' window, green barrel-vault entrance canopy, oval
sign, red neon 'Hot Now', side pickup window with a U-shaped drive-through lane, giant glazed-donut pole sign.
Branding is a simplified recreation (sheared bold italic lettering, not the official script).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-24.0, -18.0, 24.0, 20.0)
BX0, BY0, BX1, BY1 = -10.0, 2.0, 8.0, 12.0
H = 4.8
GX0, GX1, GZ1 = -9.2, 6.2, 3.9
DOOR_X = 4.6
VAULT = dict(xc=DOOR_X, r=2.4, z0=2.6, y0=BY0 - 3.2, y1=BY0 - 0.05)
PICK_Y = (6.6, 8.2)
ENTRY, EXIT = (-23.0, -17.0), (17.0, 23.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.0) + [(-24.0, 0.0, -21.0, 20.0), (-24.0, 17.8, 15.0, 20.0), (15.2, -2.0, 17.0, 17.8), (23.0, -16.0, 24.0, 20.0), (17.0, 17.8, 24.0, 20.0)]

defmat('KK_Green', '#00694c', rough=0.32, spec=0.6)
defmat('KK_GreenLit', '#00694c', rough=0.3, emit='#00a070', es=0.5)
defmat('KK_Red', '#d71f3c', rough=0.3)
defmat('KK_RedLit', '#d71f3c', rough=0.3, emit='#ff2a4a', es=0.8)
defmat('KK_Neon', '#ff3050', rough=0.3, emit='#ff2a48', es=6.0)
defmat('KK_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('KK_Clad', '#f2f1ee', rough=0.3, metal=0.1)
defmat('KK_Glaze', '#e9c27a', rough=0.35)
defmat('KK_Menu', '#10100f', rough=0.25, emit='#bfffe0', es=0.9)


def kk_logo(acc, L, M, w=7.0, h=1.7, depth=0.08):
    """Green oval badge with red outline and the (simplified) wordmark."""
    oval = lambda ww, hh: rounded_rect(-ww / 2, -hh / 2, ww / 2, hh / 2, hh / 2, {0: 8, 1: 5, 2: 3}[L])
    acc.add(bm_prism(oval(w + 0.2, h + 0.2), 0.0, depth * 0.5), 'KK_RedLit', matrix=M)
    acc.add(bm_prism(oval(w, h), 0.0, depth), 'KK_GreenLit', matrix=M @ Matrix.Translation((0, 0, depth * 0.45)))
    txt(acc, L, 'Krispy Kreme', M @ Matrix.Translation((0, 0.0, depth * 1.4)), h * 0.5, depth * 0.7, 'black_i', 'KK_SignWhite', 'RS_PaintWhite', spacing=0.97, shear=0.12)


def sprinkle_donut(acc, L, x, y, z, icing, r=0.11):
    if L == 0:
        acc.add(bm_cyl(x, y, z, z + 0.05, r, 9), 'KK_Glaze')
        acc.add(bm_cyl(x, y, z + 0.05, z + 0.065, r * 0.92, 9), icing)
    else:
        acc.add(bm_cyl(x, y, z, z + 0.06, r, 5), icing)


# ------------------------------------------------------------------ ground & drive-thru
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (14.0, -17.6, 17.0, -16.0)]
    walk = (-10.5, -2.0, 8.5, BY0)
    site_ground(A, L, PLOT, holes, [walk, (VAULT['xc'] - 3.0, -3.0, VAULT['xc'] + 3.0, -2.0)], BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(22.5, -14.0), (-22.5, 10.0), (22.5, 12.0), (-8.0, 19.0), (10.0, 19.0)], 180)
    rng = random.Random(21)
    for i in range(24):
        x = -16.0 + i * 1.4
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 13.0 < x < 17.5:
            continue
        (R.grass_clump(land, L, x, -17.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -17.0 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage' if i % 2 else 'RS_Foliage2'))
    entry_exit(A, L, PLOT, -20.0, 20.0, depth=2.0)
    if L < 2:
        mk = A.m(L, 'Markings')
        for (x0, y0, x1, y1) in ((-20.0, -3.0, -19.9, 17.8), (-16.5, 0.0, -16.4, 13.4), (-20.0, 17.7, 15.0, 17.8), (-16.5, 13.4, 11.3, 13.5),
                                 (11.3, -4.0, 11.4, 13.5), (15.0, -4.0, 15.1, 17.8)):
            mk.add(bm_hquad(x0, y0, x1, y1, 0.006), 'RS_LineWhite')
        R.arrow_mark(mk, -18.2, 3.0, 90, 3.2); R.arrow_mark(mk, -18.2, 10.5, 90, 3.2)
        R.arrow_mark(mk, -8.0, 15.6, 0, 3.2); R.arrow_mark(mk, 2.0, 15.6, 0, 3.2)
        R.arrow_mark(mk, 13.2, 11.0, -90, 3.2); R.arrow_mark(mk, 13.2, 2.0, -90, 3.2)
    cars = {0: ('RS_CarRed', 'hatch'), 6: ('RS_CarSilver', 'sedan')}
    parking_row(A, L, -16.0, -15.0, -10.0, 8, 2.6, cars)
    disabled_bay(A, L, -16.0 + 2.6 * 8 + 1.3, -15.0, -10.0)
    v = A.m(L, 'Vehicles')
    car(v, L, 13.2, 7.4, -90, 'RS_CarBlue', 'suv')
    car(v, L, -18.2, 7.0, 90, 'RS_CarWhite', 'sedan')
    menu_board(A, L, -20.8, 6.0, '+X', body='KK_Green', w=1.5)
    menu_board(A, L, -20.8, 10.0, '+X', body='KK_Green', w=1.5)
    height_bar(A.m(L, 'DriveThru'), L, -18.2, -2.0, 4.0, 2.3)
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(9)
    for i, (x, y) in enumerate(((-7.0, -4.8), (-3.0, -5.6), (-9.5, -1.0))):
        cafe_set(fur, L, x, y, 3, ang=rng2.uniform(0, 90), table_mat='KK_Clad', chair_mat='RS_MetalDark', seat_mat='KK_Green', umb='KK_Green' if i < 2 else None, umb2='KK_Clad')
    planter(fur, L, -10.5, -6.8, 0.5, -6.2, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=5)


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'KK_Clad', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='KK_Clad', roof_mat='KK_Clad', parapet=0.5,
          parapet_mat='KK_Green', skip=('right',))
    # east wall with pickup window
    rects = [(BY0 + t, 0.15, BY1 - t, H - 0.3)]
    rects = rect_subtract(rects, (PICK_Y[0], 1.15, PICK_Y[1], 2.4))
    for (y0, z0, y1, z1) in rects:
        b.add(bm_box(BX1 - t, y0, z0, BX1, y1, z1, open_bottom=z0 <= 0.2), 'KK_Clad')
    # green stripe + white sign band above the glazing
    b.add(bm_box(BX0 - 0.1, BY0 - 0.35, GZ1, BX1 + 0.1, BY0, H - 0.35, bevel=bv), 'KK_Clad')
    b.add(bm_box(BX0 - 0.1, BY0 - 0.38, H - 0.35, BX1 + 0.1, BY0 + 0.05, H + 0.1, bevel=bv), 'KK_Green')
    b.add(bm_box(BX0 - 0.1, BY0 - 0.38, GZ1 - 0.08, BX1 + 0.1, BY0 - 0.2, GZ1 + 0.02), 'KK_Red')
    # solid wall right of the glazing
    # barrel-vault entrance canopy (green, half pipe along Y) + columns
    v = VAULT
    arc_o = [(v['xc'] + (v['r'] + 0.25) * math.cos(math.radians(a)), v['z0'] + (v['r'] + 0.25) * math.sin(math.radians(a))) for a in [180.0 * i / {0: 14, 1: 8, 2: 4}[L] for i in range(({0: 14, 1: 8, 2: 4}[L]) + 1)]]
    arc_i = [(v['xc'] + v['r'] * math.cos(math.radians(a)), v['z0'] + v['r'] * math.sin(math.radians(a))) for a in [180.0 * i / {0: 14, 1: 8, 2: 4}[L] for i in range(({0: 14, 1: 8, 2: 4}[L]) + 1)]]
    pts = arc_o + list(reversed(arc_i))
    cp = A.m(L, 'Canopy')
    M = place('-Y', (0.0, v['y1'], 0.0))
    cp.add(bm_prism_local(pts, v['y1'] - v['y0']), 'KK_Green', matrix=M, mat_fn=front_back('KK_GreenLit', 'KK_Green'))
    for x in (v['xc'] - v['r'] - 0.1, v['xc'] + v['r'] + 0.1):
        cp.add(bm_cyl(x, v['y0'] + 0.2, 0.0, v['z0'], 0.09, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    if L < 2:
        cp.add(bm_box(v['xc'] - v['r'], v['y0'] + 0.05, v['z0'] - 0.04, v['xc'] + v['r'], v['y1'], v['z0'], open_bottom=False), 'RS_LightWarm')
    # pickup window glazing + shelf + canopy + sign
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    gl.add(bm_quad((BX1 + 0.02, PICK_Y[1], 1.15), (BX1 + 0.02, PICK_Y[0], 1.15), (BX1 + 0.02, PICK_Y[0], 2.4), (BX1 + 0.02, PICK_Y[1], 2.4)), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
    if L < 2:
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 1.07, BX1 + 0.12, PICK_Y[1] + 0.08, 1.15), 'RS_MetalBrushed')
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 2.4, BX1 + 0.12, PICK_Y[1] + 0.08, 2.48), 'RS_MetalDark')
    cp.add(bm_box(BX1, 5.6, 2.9, BX1 + 2.4, 9.2, 3.2, bevel=bv), 'KK_Green')
    for (px, py) in ((BX1 + 2.2, 5.7), (BX1 + 2.2, 9.1)):
        cp.add(bm_cyl(px, py, 0.0, 2.9, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    txt(s, L, 'DRIVE-THRU', place('+X', (BX1 + 0.04, 7.4, 3.5)), 0.4, 0.04, 'xbold_i', 'KK_SignWhite', 'RS_PaintWhite', min_size_lod2=9)
    kk_logo(s, L, place('-Y', (-3.4, BY0 - 0.4, 4.35)), 7.2, 1.35, 0.08)
    kk_logo(s, L, place('+X', (BX1 + 0.1, 3.4, 3.9)), 3.2, 0.9, 0.06)
    # red neon 'Hot Now' inside the window
    txt(s, L, 'Hot Now', place('-Y', (-5.5, BY0 + 0.4, 2.95)), 0.62, 0.04, 'xbold_i', 'KK_Neon', 'KK_Neon', shear=0.12, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Krispy Kreme oval badge', (-3.4, BY0 - 0.5, 4.35), 0.68, width=5.0)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=8, trans=(2.5,), doors=((DOOR_X, 2.2),), frame='RS_MetalBrushed', door_h=2.3, bottom_rail=0.1)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.6, 'RS_TileFloor', 'KK_Clad', lights=light_grid((ix0, iy0, ix1, iy1), 5, 2, (1.4, 0.3), 1.2), back_mat='KK_Green')
    # doughnut theatre: glass-enclosed fryer line, conveyor, cooling racks
    it.add(bm_box(-9.0, 4.0, 0.15, 2.0, 6.6, 1.0, bevel=0.02 if L == 0 else 0, open_bottom=True), 'RS_MetalBrushed')
    it.add(bm_box(-9.0, 4.0, 1.0, 2.0, 6.6, 2.5), 'RS_Glass')
    for x in (-9.0, -5.0, -1.0, 2.0):
        it.add(bm_box(x - 0.03, 3.97, 1.0, x + 0.03, 4.03, 2.5), 'RS_MetalBrushed')
    it.add(bm_box(-8.9, 4.5, 1.0, 1.9, 6.1, 1.1), 'KK_RedLit')
    rng = random.Random(5)
    icing = ['RS_Pink', 'RS_Choc', 'RS_Cream', 'KK_Red', 'RS_Pastry']
    for i in range(36):
        sprinkle_donut(it, L, -8.6 + i * 0.3, 4.9 + (i % 2) * 0.6, 1.12, icing[rng.randrange(5)], 0.1)
    counter(it, L, -9.0, 8.4, 5.0, 9.4, 1.05, 'KK_Green', 'RS_PaintWhite')
    it.add(bm_box(-9.0, iy1 - 0.7, 0.15, 5.0, iy1, 1.0, open_bottom=True), 'RS_PaintCharcoal')
    for i in range(4):
        x = -7.5 + i * 3.4
        it.add(bm_box(x - 1.1, iy1 - 0.06, 1.5, x + 1.1, iy1 - 0.03, 2.7), 'KK_Menu')
    # donut display case on the counter
    it.add(bm_box(-6.0, 8.5, 1.1, -1.0, 9.3, 1.55), 'RS_Glass')
    for i in range(14):
        sprinkle_donut(it, L, -5.8 + i * 0.34, 8.9, 1.12, icing[rng.randrange(5)], 0.1)
    for i, x in enumerate((-8.0, -5.0, -2.0)):
        cafe_set(it, L, x, 2.9, 2, ang=90 * i, table_mat='KK_Clad', chair_mat='RS_MetalDark', seat_mat='KK_Green', r=0.3)


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = 15.6, -16.8
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.3, cy - 0.5, 0.0, cx + 1.3, cy + 0.5, 0.4, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 0.9, cy - 0.3, 0.4, cx + 0.9, cy + 0.3, 5.0, bevel=bv), 'KK_GreenLit')
    p.add(bm_box(cx - 1.0, cy - 0.32, 5.0, cx + 1.0, cy + 0.32, 5.2, bevel=bv), 'KK_RedLit')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.3), ('+Y', cy + 0.3)):
        txt(s, L, 'Krispy', place(face, (cx, yy, 3.7)), 0.75, 0.05, 'black_i', 'KK_SignWhite', 'RS_PaintWhite', shear=0.12)
        txt(s, L, 'Kreme', place(face, (cx, yy, 2.7)), 0.75, 0.05, 'black_i', 'KK_SignWhite', 'RS_PaintWhite', shear=0.12)
        txt(s, L, 'Hot Now', place(face, (cx, yy, 1.5)), 0.42, 0.04, 'xbold_i', 'KK_Neon', 'KK_Neon', shear=0.12, min_size_lod2=9)
    donut(s, L, (cx, cy, 6.55), 0.85, 0.34, axis='Y', icing='RS_Pink')
    if L == 0:
        register_sign(A, 'Krispy Kreme pole sign', (cx, cy - 0.36, 3.7), 0.55, width=1.8)


LAMPS = [(-5.0, -16.0, 0, 1), (8.0, -16.0, 0, 1), (-22.0, 3.0, 1, 0), (22.0, 3.0, -1, 0), (0.0, 18.8, 0, -1)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.4, 0.0, BX1, BY1, H + 0.5)
    A.col_box('Vault', VAULT['xc'] - VAULT['r'] - 0.3, VAULT['y0'], VAULT['z0'], VAULT['xc'] + VAULT['r'] + 0.3, VAULT['y1'], VAULT['z0'] + VAULT['r'] + 0.3)
    A.col_box('PickupCanopy', BX1, 5.6, 2.9, BX1 + 2.4, 9.2, 3.2)
    A.col_box('Pylon', 14.2, -17.3, 0.0, 17.0, -16.3, 7.5)
    lamp_collision(A, LAMPS)


def build_lights(A):
    glow_lights(A, 'Interior', [(-6.0, 6.5, 3.2), (-1.0, 6.5, 3.2), (3.0, 9.0, 3.2)], energy=800, color='#ffeedd')
    for i, x in enumerate((-7.0, -2.0, 3.0)):
        A.light(f'Sign{i}', 'SPOT', (x, BY0 - 2.5, 4.4), 800, '#ffffff', rot=(0, 0, 0), spot_deg=120, blend=0.8, radius=0.2)
    A.light('Vault', 'SPOT', (DOOR_X, BY0 - 1.5, 4.9), 900, '#fff0e0', spot_deg=120, blend=0.8, radius=0.2)
    A.light('NeonGlow', 'POINT', (-5.5, BY0 - 1.5, 2.9), 500, '#ff4060', radius=0.6)
    sign_light(A, 'PylonGlow', (15.6, -20.0, 4.0), 1600, '#ffe0e8')
    A.light('PickupGlow', 'SPOT', (BX1 + 1.4, 7.4, 2.85), 600, '#fff2e0', rot=(180, 0, 0), spot_deg=110, blend=0.8, radius=0.2)
    lamp_lights(A, LAMPS)


def main():
    A = Store('06', '06_krispy_kreme', 'krispy_kreme', 'KK', 'DonutShop', 'Krispy Kreme')
    A.dims = dict(plot=[48.0, 38.0], building=[BX1 - BX0, BY1 - BY0, H], pylon_height=7.6, vault_height=VAULT['z0'] + VAULT['r'] + 0.25)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-22.0, -29.0, 3.8), (-1.0, 3.0, 2.9), 32)
    A.camera('road', (-30.0, PLOT[1] - 8.6, 1.25), (0.0, -5.0, 3.6), 30)
    A.camera('detail', (2.0, -10.5, 1.7), (-3.5, 2.0, 3.0), 26)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
