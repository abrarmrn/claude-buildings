"""ASSET 09 - KFC (standalone quick-service restaurant with drive-through; drive-through cluster).

Plot 56 m x 42 m, road side faces -Y, origin = plot centre at finished ground.
Massing: white volume under a red mono-pitch roof wedge, red/white striped awning over a glass front, rooftop
back-lit 'KFC' box sign, drive-through lane up the east side to a pickup window (order board, canopy), exit loop,
parking row, pole sign topped with a red/white striped bucket. The Colonel portrait is not reproduced.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-28.0, -21.0, 28.0, 21.0)
BX0, BY0, BX1, BY1 = -12.0, 2.0, 8.0, 13.0
H = 4.7
GX0, GX1, GZ1 = -10.8, 5.6, 3.5
DOOR_X = -2.0
PICK_Y = (8.0, 9.6)
ENTRY, EXIT = (8.5, 14.5), (21.0, 27.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.2) + [(-28.0, -19.0, -27.2, 21.0), (27.2, -19.0, 28.0, 21.0), (-27.0, 19.0, 27.0, 21.0)]
PAVED = [(-13.0, -5.5, 6.5, BY0)]

defmat('KF_Red', '#e4002b', rough=0.3, spec=0.6)
defmat('KF_RedLit', '#d8002a', rough=0.32, emit='#ff1a40', es=0.35)
defmat('KF_White', '#f6f4f1', rough=0.3, metal=0.05)
defmat('KF_BoxWhite', '#ffffff', rough=0.3, emit='#ffffff', es=2.2)
defmat('KF_Letter', '#e4002b', rough=0.3, emit='#ff1030', es=1.6)
defmat('KF_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('KF_Dark', '#2a2a2c', rough=0.4, metal=0.2)
defmat('KF_Menu', '#0e0e0f', rough=0.25, emit='#ffe0b0', es=1.0)
defmat('KF_Wood', '#6b4630', rough=0.55)


def bucket(acc, L, x, y, z, s=1.0):
    """Red/white striped bucket sign (faces alternate colour by angle)."""
    seg = {0: 24, 1: 12, 2: 8}[L]
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=0.95 * s, radius2=1.2 * s, depth=1.9 * s)
    bmesh.ops.translate(bm, vec=(x, y, z + 0.95 * s), verts=bm.verts)
    bm.normal_update()

    def pick(f):
        if f.normal.z > 0.5:
            return 'KF_White'
        if f.normal.z < -0.5:
            return 'KF_Red'
        c = f.calc_center_median()
        k = int(((math.atan2(c.y - y, c.x - x) + math.pi) / (2 * math.pi)) * seg)
        return 'KF_RedLit' if k % 2 == 0 else 'KF_White'
    acc.add(bm, 'KF_Red', mat_fn=pick)
    acc.add(bm_cyl(x, y, z + 1.9 * s, z + 2.0 * s, 1.26 * s, seg), 'KF_White')


def kfc_letters(acc, L, M, size, depth=0.08, front='KF_Letter', side='KF_Red'):
    txt(acc, L, 'KFC', M, size, depth, 'black', front, side, spacing=1.04)


# ------------------------------------------------------------------ ground & drive-thru
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (15.0, -20.6, 18.0, -19.0)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(26.5, -17.0), (-26.5, 10.0), (26.5, 10.0), (-14.0, 19.8), (6.0, 19.8)], 210)
    rng = random.Random(51)
    for i in range(30):
        x = -20.0 + i * 1.5
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or 14.0 < x < 19.0:
            continue
        (R.grass_clump(land, L, x, -20.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -20.0, 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, 11.5, 24.0, depth=2.2)
    if L < 2:
        mk = A.m(L, 'Markings')
        for (x0, y0, x1, y1) in ((8.9, -4.0, 9.0, 16.7), (12.6, -4.0, 12.7, 16.7), (8.9, 16.6, 22.0, 16.7), (12.6, 20.3, 22.0, 20.4), (19.4, -4.0, 19.5, 16.7), (22.9, -4.0, 23.0, 20.4)):
            mk.add(bm_hquad(x0, y0, x1, y1, 0.006), 'RS_LineWhite')
        for y in (-2.0, 6.0, 13.0):
            R.arrow_mark(mk, 10.8, y, 90, 3.0)
        for x in (15.0, 20.0):
            R.arrow_mark(mk, x, 18.5, 0, 3.0)
        for y in (14.0, 5.0, -2.0):
            R.arrow_mark(mk, 21.2, y, -90, 3.0)
    cars = {0: ('RS_CarWhite', 'suv'), 3: ('RS_CarBlack', 'sedan'), 6: ('RS_CarBlue', 'hatch')}
    parking_row(A, L, -13.0, -15.0, -9.5, 8, 2.6, cars)
    disabled_bay(A, L, -13.0 + 2.6 * 8 + 1.3, -15.0, -9.5)
    v = A.m(L, 'Vehicles')
    car(v, L, 10.8, 8.9, 90, 'RS_CarRed', 'suv')
    car(v, L, 10.8, 3.2, 90, 'RS_CarSilver', 'sedan')
    menu_board(A, L, 13.9, 4.0, '-X', body='KF_Dark', w=1.7, trim='KF_Dark')
    if L < 2:
        s = A.m(L, 'Signage')
        txt(s, L, 'ORDER HERE', place('-X', (13.76, 4.0, 2.1)), 0.14, 0.01, 'bold', 'KF_SignWhite', min_size_lod2=9)
    height_bar(A.m(L, 'DriveThru'), L, 10.8, -3.5, 4.0, 2.3)
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(4)
    for i, (x, y) in enumerate(((-9.5, -3.0), (-6.0, -3.8), (-2.5, -3.0), (1.0, -3.8), (4.2, -3.0))):
        cafe_set(fur, L, x, y, 4 if i % 2 else 2, ang=rng2.uniform(0, 90), table_mat='KF_White', chair_mat='RS_MetalDark', seat_mat='KF_Red', r=0.34)
    planter(fur, L, -13.0, -5.4, -4.0, -4.8, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=3)
    bin_(fur, L, 5.8, -0.5, 'KF_Dark')


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.3
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'KF_White', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='KF_White', roof_mat='KF_White', skip=('right', 'roof'), rooftop=False)
    # east wall with the drive-thru pickup window
    rects = rect_subtract([(BY0 + t, 0.15, BY1 - t, H - 0.3)], (PICK_Y[0], 1.15, PICK_Y[1], 2.4))
    for (y0, z0, y1, z1) in rects:
        b.add(bm_box(BX1 - t, y0, z0, BX1, y1, z1, open_bottom=z0 <= 0.2), 'KF_White')
    b.add(bm_box(BX1, BY0 + 0.3, 0.0, BX1 + 0.06, BY1 - 0.3, 1.0, bevel=bv, open_bottom=True), 'KF_Wood')
    # dark timber-look plinth on the front and red mono-pitch roof wedge (profile in YZ, rises toward the back)
    b.add(bm_box(GX1, BY0 - 0.1, 0.15, BX1, BY0, GZ1 + 0.4, bevel=bv, open_bottom=True), 'KF_Wood')
    prof = [(BY0 - 1.0, 4.45), (BY1 + 0.3, 5.6), (BY1 + 0.3, 6.15), (BY0 - 1.0, 5.0)]
    b.add(bm_prism_local(prof, (BX1 + 0.4) - (BX0 - 0.4)), 'KF_Red', matrix=place('+X', (BX0 - 0.4, 0, 0)))
    b.add(bm_box(BX0 - 0.4, BY0 - 1.05, 4.4, BX1 + 0.4, BY0 - 0.9, 5.05, bevel=bv), 'KF_RedLit')
    b.add(bm_box(BX0 - 0.4, BY0 - 1.06, 4.38, BX1 + 0.4, BY0 - 0.9, 4.46), 'KF_White')
    # white wall above the glazing under the roof
    b.add(bm_box(BX0, BY0 - 0.08, GZ1, BX1, BY0, 4.4, bevel=bv), 'KF_White')
    # striped awning over the glass front
    aw = A.m(L, 'Awnings')
    awning(aw, L, GX0, GX1, BY0 - 0.12, GZ1 + 0.05, 0.6, 1.9, ('KF_Red', 'KF_White'), strip=0.6, valance=0.3)
    # roof sign: back-lit white box with red letters, on a short frame on the roof edge
    for x in (-10.0, -2.5):
        b.add(bm_box(x - 0.08, BY0 + 0.4, 5.0, x + 0.08, BY0 + 0.6, 5.6), 'RS_MetalDark')
    b.add(bm_box(-11.5, BY0 + 0.3, 5.5, -1.0, BY0 + 0.7, 7.5, bevel=bv), 'KF_BoxWhite')
    b.add(bm_box(-11.6, BY0 + 0.25, 5.45, -0.9, BY0 + 0.75, 5.55), 'KF_Red')
    b.add(bm_box(-11.6, BY0 + 0.25, 7.5, -0.9, BY0 + 0.75, 7.6), 'KF_Red')
    # pickup window glazing, shelf, canopy, sign
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    gl.add(bm_quad((BX1 + 0.02, PICK_Y[1], 1.15), (BX1 + 0.02, PICK_Y[0], 1.15), (BX1 + 0.02, PICK_Y[0], 2.4), (BX1 + 0.02, PICK_Y[1], 2.4)), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
    if L < 2:
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 1.07, BX1 + 0.12, PICK_Y[1] + 0.08, 1.15), 'RS_MetalBrushed')
        fr.add(bm_box(BX1, PICK_Y[0] - 0.08, 2.4, BX1 + 0.12, PICK_Y[1] + 0.08, 2.48), 'RS_MetalDark')
    cp = A.m(L, 'Canopy')
    cp.add(bm_box(BX1, 7.0, 3.0, BX1 + 3.0, 10.6, 3.3, bevel=bv), 'KF_Red')
    for (px, py) in ((BX1 + 2.8, 7.1), (BX1 + 2.8, 10.5)):
        cp.add(bm_cyl(px, py, 0.0, 3.0, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    kfc_letters(s, L, place('-Y', (-6.25, BY0 + 0.3, 6.75)), 1.7, 0.1)
    txt(s, L, 'KENTUCKY FRIED CHICKEN', place('-Y', (-6.25, BY0 + 0.3, 5.85)), 0.2, 0.04, 'bold', 'KF_Letter', 'KF_Red', spacing=1.15, min_size_lod2=9)
    kfc_letters(s, L, place('+X', (BX1 + 0.03, 8.8, 3.75)), 0.55, 0.05, 'KF_SignWhite', 'RS_PaintWhite')
    txt(s, L, 'DRIVE-THRU', place('+X', (BX1 + 0.03, 8.8, 3.35)), 0.2, 0.03, 'bold', 'KF_SignWhite', 'RS_PaintWhite', min_size_lod2=9)
    if L == 0:
        register_sign(A, 'KFC roof sign', (-6.25, BY0 + 0.18, 6.75), 1.22, width=3.6)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=8, trans=(2.5,), doors=((DOOR_X, 2.2),), frame='KF_Dark', door_h=2.3, bottom_rail=0.1)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.6, 'RS_TileFloor', 'KF_White', lights=light_grid((ix0, iy0, ix1, iy1), 5, 3, (1.3, 0.28), 1.2), back_mat='KF_Red')
    counter(it, L, -10.0, 9.5, 1.0, 10.7, 1.05, 'KF_Red', 'KF_White')
    it.add(bm_box(ix0, iy1 - 0.9, 0.15, ix1, iy1, 2.5, open_bottom=True), 'KF_Dark')
    for i in range(5):
        x = -9.0 + i * 3.6
        it.add(bm_box(x - 1.2, 9.5, 2.55, x + 1.2, 9.56, 3.45), 'KF_Menu')
    for j, y in enumerate((4.6, 7.0)):
        for i, x in enumerate((-9.0, -5.5, -2.0, 1.5, 4.5)):
            cafe_set(it, L, x, y, 4 if (i + j) % 2 == 0 else 2, ang=45 * j, table_mat='KF_White', chair_mat='RS_MetalDark', seat_mat='KF_Red' if (i + j) % 2 == 0 else 'KF_Wood', r=0.33)
    it.add(bm_box(3.0, 10.4, 0.15, 7.2, 11.2, 1.1, open_bottom=True), 'RS_MetalBrushed')


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = 16.5, -19.8
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.1, cy - 0.5, 0.0, cx + 1.1, cy + 0.5, 0.4, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_cyl(cx, cy, 0.4, 6.0, 0.28, 12 if L == 0 else 6, open_bottom=True), 'KF_Dark')
    p.add(bm_box(cx - 1.2, cy - 0.28, 1.2, cx + 1.2, cy + 0.28, 3.2, bevel=bv), 'KF_White')
    p.add(bm_box(cx - 1.2, cy - 0.3, 3.2, cx + 1.2, cy + 0.3, 3.35), 'KF_Red')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.28), ('+Y', cy + 0.28)):
        kfc_letters(s, L, place(face, (cx, yy, 2.4)), 1.1, 0.06)
        txt(s, L, 'DRIVE THRU', place(face, (cx, yy, 1.6)), 0.24, 0.03, 'bold', 'KF_Red', 'KF_Red', min_size_lod2=9)
    bucket(s, L, cx, cy, 6.0, 1.0)
    if L == 0:
        register_sign(A, 'KFC pole sign', (cx, cy - 0.34, 2.4), 0.8, width=2.2)


LAMPS = [(-8.0, -19.0, 0, 1), (4.0, -19.0, 0, 1), (-26.0, 2.0, 1, 0), (26.0, 2.0, -1, 0), (16.0, 19.8, 0, -1)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H)
    A.col_box('Roof', BX0 - 0.4, BY0 - 1.0, 4.4, BX1 + 0.4, BY1 + 0.3, 6.2)
    A.col_box('RoofSign', -11.6, BY0 + 0.25, 5.45, -0.9, BY0 + 0.75, 7.6)
    A.col_box('PickupCanopy', BX1, 7.0, 3.0, BX1 + 3.0, 10.6, 3.3)
    A.col_box('Pylon', 15.2, -20.3, 0.0, 17.8, -19.3, 8.1)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-8.0, -2.0, 3.0)):
        A.light(f'Awning{i}', 'SPOT', (x, BY0 - 1.7, 3.2), 1000, '#fff0e0', spot_deg=125, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-6.0, 6.0, 3.3), (-1.0, 6.0, 3.3), (4.0, 6.0, 3.3), (-4.0, 10.0, 3.3)], energy=1000, color='#fff0e0')
    sign_light(A, 'RoofSignGlow', (-6.25, -3.0, 6.5), 2400, '#ffe6e6')
    sign_light(A, 'PylonGlow', (16.5, -23.0, 3.0), 1800, '#ffe6e6')
    A.light('BucketGlow', 'POINT', (16.5, -22.0, 7.0), 1400, '#ffd8d8', radius=0.6)
    A.light('PickupGlow', 'SPOT', (BX1 + 1.6, 8.8, 2.95), 700, '#fff2e0', rot=(180, 0, 0), spot_deg=110, blend=0.8, radius=0.2)
    lamp_lights(A, LAMPS)


def main():
    A = Store('09', '09_kfc', 'kfc', 'KFC', 'Restaurant', 'KFC')
    A.dims = dict(plot=[56.0, 42.0], building=[BX1 - BX0, BY1 - BY0, H], roof_sign_height=7.6, pylon_height=8.1)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-21.0, -27.0, 4.0), (-2.0, 4.0, 3.3), 32)
    A.camera('road', (-34.0, PLOT[1] - 8.6, 1.25), (-4.0, -4.0, 4.4), 30)
    A.camera('detail', (-1.0, -11.0, 1.8), (-4.0, 2.0, 4.2), 26)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
