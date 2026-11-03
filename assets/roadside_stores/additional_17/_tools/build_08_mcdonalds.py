"""ASSET 08 - McDonald's (modern standalone roadside restaurant; drive-through cluster).

Plot 64 m x 48 m, road side faces -Y, origin = plot centre at finished ground.
Massing: dark-grey modern box with timber accent, red glazed tower carrying golden arches, slim entrance canopy,
full-width glass front with seating visible, double-lane drive-through looping east -> back -> west with order
canopy, two rear pickup windows, height bar, parking row, arches pylon.
Golden arches are built as two extruded half-ellipse rings (simplified geometry, not the official artwork).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-32.0, -24.0, 32.0, 24.0)
BX0, BY0, BX1, BY1 = -14.0, 3.0, 12.0, 19.0
H, TH = 5.2, 7.8
TX1 = -7.4                                  # tower x range: BX0..TX1
GX0, GX1, GZ1 = -7.0, 11.4, 3.9
DOOR_X = 3.0
ENTRY, EXIT = (20.0, 28.0), (-30.0, -21.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.2) + [(-32.0, -22.0, -31.0, 24.0), (31.0, -22.0, 32.0, 24.0), (-31.0, 22.5, 31.0, 24.0)]
PAVED = [(-16.0, -6.0, 13.5, BY0)]

defmat('MD_Red', '#da291c', rough=0.3, spec=0.6)
defmat('MD_RedLit', '#c8231a', rough=0.32, emit='#e0281c', es=0.12)
defmat('MD_Yellow', '#ffc72c', rough=0.3, emit='#ffc72c', es=1.8)
defmat('MD_Grey', '#3a3e43', rough=0.45, metal=0.2)
defmat('MD_LightGrey', '#b9bcc0', rough=0.45)
defmat('MD_White', '#f2f1ee', rough=0.35)
defmat('MD_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('MD_Menu', '#0e0f10', rough=0.25, emit='#ffe9b0', es=1.1)
defmat('MD_Seat', '#d6281b', rough=0.6)
defmat('MD_SeatY', '#f0b429', rough=0.6)


def arch_ring(a, b, t, seg, depth):
    """One arch: half-ellipse ring (outer semi-axes a,b; thickness t), legs on z=0. Returns local-polygon points (x,y)."""
    outer = [(a * math.cos(math.pi * i / seg), b * math.sin(math.pi * i / seg)) for i in range(seg + 1)]
    inner = [((a - t) * math.cos(math.pi * i / seg), (b - t) * math.sin(math.pi * i / seg)) for i in range(seg, -1, -1)]
    return outer + inner


def golden_arches(acc, L, M, w=4.0, h=3.0, depth=0.25, mat='MD_Yellow'):
    """Two overlapping arches forming the 'M' (simplified geometry). M frame: origin at base centre, +Z out of the face."""
    seg = {0: 20, 1: 10, 2: 6}[L]
    aw = w * 0.30
    t = w * 0.155
    for sx in (-1, 1):
        pts = arch_ring(aw, h, t, seg, depth)
        pts = [(x + sx * (w / 2 - aw), y) for x, y in pts]
        acc.add(bm_prism_local(pts, depth), mat, matrix=M)


def md_wordmark(acc, L, M, size, depth=0.06):
    txt(acc, L, "McDonald's", M, size, depth, 'black', 'MD_SignWhite', 'RS_PaintWhite', spacing=0.98)


# ------------------------------------------------------------------ ground & drive-thru
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (22.0, -22.6, 25.2, -21.2)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(30.0, -20.0), (-30.0, 10.0), (30.0, 10.0), (-24.0, 22.8), (-2.0, 22.8), (24.0, 22.8)], 200)
    rng = random.Random(41)
    for i in range(30):
        x = -17.0 + i * 1.5
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or 20.0 < x < 26.0:
            continue
        (R.grass_clump(land, L, x, -22.9, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -22.9, 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, 24.0, -25.5, y=-19.0, depth=2.2)
    if L < 2:
        mk = A.m(L, 'Markings')
        # east double lane (x 14.8..22.0) running north, back lane (y 20.2..23.0) running west, west lane (x -21..-17.6) running south
        for (x0, y0, x1, y1) in ((14.7, -4.0, 14.8, 19.8), (22.0, -4.0, 22.1, 22.9), (18.35, -2.0, 18.45, 14.0), (-21.0, -4.0, -20.9, 23.0), (-17.6, 0.0, -17.5, 20.0),
                                 (-17.5, 19.9, 14.8, 20.0)):
            mk.add(bm_hquad(x0, y0, x1, y1, 0.006), 'RS_LineWhite' if (x1 - x0) < 0.2 else 'RS_LineYellow')
        for y in (0.0, 5.0, 12.0):
            R.arrow_mark(mk, 16.6, y, 90, 3.0); R.arrow_mark(mk, 20.2, y, 90, 3.0)
        for x in (10.0, -2.0, -12.0):
            R.arrow_mark(mk, x, 21.6, 180, 3.0)
        for y in (18.0, 8.0, 0.0):
            R.arrow_mark(mk, -19.3, y, -90, 3.0)
        # DRIVE THRU stencil
        txt(mk, L, 'DRIVE THRU', Matrix.Translation((18.4, -9.0, 0.008)) @ Matrix.Rotation(math.radians(90), 4, 'Z'), 0.9, 0.0, 'bold', 'RS_LineWhite', min_size_lod2=9)
    cars = {1: ('RS_CarRed', 'suv'), 4: ('RS_CarWhite', 'sedan'), 8: ('RS_CarBlack', 'hatch')}
    parking_row(A, L, -13.0, -16.0, -10.0, 10, 2.6, cars)
    disabled_bay(A, L, -13.0 + 2.6 * 10 + 1.3, -16.0, -10.0)
    v = A.m(L, 'Vehicles')
    car(v, L, 16.4, 8.2, 90, 'RS_CarSilver', 'sedan')
    car(v, L, 20.2, 8.0, 90, 'RS_CarBlue', 'suv')
    car(v, L, 9.0, 21.6, 180, 'RS_CarGrey', 'hatch')
    car(v, L, -19.3, 12.0, -90, 'RS_CarGold', 'sedan')
    # order canopy + two order boards + height bar
    dt = A.m(L, 'DriveThru')
    bv = 0.03 if L == 0 else 0.0
    dt.add(bm_box(14.0, 7.0, 3.3, 22.8, 11.0, 3.6, bevel=bv), 'MD_Red')
    for (px, py) in ((14.2, 7.2), (22.6, 7.2), (14.2, 10.8), (22.6, 10.8)):
        dt.add(bm_cyl(px, py, 0.0, 3.3, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    if L < 2:
        for x in (16.4, 20.2):
            dt.add(bm_box(x - 0.6, 8.0, 3.28, x + 0.6, 10.0, 3.3), 'RS_LightPanel')
    menu_board(A, L, 13.6, 9.0, '+X', body='MD_Grey', w=1.6)
    menu_board(A, L, 23.4, 9.0, '-X', body='MD_Grey', w=1.6)
    height_bar(dt, L, 18.4, 1.5, 7.6, 2.3)
    if L < 2:
        s = A.m(L, 'Signage')
        for (x, face) in ((13.46, '+X'), (23.54, '-X')):
            txt(s, L, 'ORDER HERE', place(face, (x, 9.0, 2.1)), 0.14, 0.01, 'bold', 'MD_SignWhite', min_size_lod2=9)
    # back pickup canopy over the rear lane
    dt.add(bm_box(1.0, BY1, 3.3, 12.5, BY1 + 3.4, 3.6, bevel=bv), 'MD_Red')
    for (px, py) in ((1.4, BY1 + 3.1), (12.1, BY1 + 3.1)):
        dt.add(bm_cyl(px, py, 0.0, 3.3, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    # outdoor seating at the front paved area
    fur = A.m(L, 'Furniture')
    rng2 = random.Random(3)
    for i, (x, y) in enumerate(((-12.0, -2.6), (-8.5, -3.4), (8.0, -3.0), (11.5, -2.4))):
        cafe_set(fur, L, x, y, 3 if i % 2 else 4, ang=rng2.uniform(0, 90), table_mat='MD_White', chair_mat='RS_MetalDark', seat_mat='MD_Seat', r=0.34)
    planter(fur, L, -16.0, -5.6, -5.0, -5.0, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=2)
    bin_(fur, L, 6.2, -1.0, 'MD_Grey')


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.35
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'MD_Grey', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='MD_Grey', roof_mat='MD_LightGrey', roof_t=0.35,
          parapet=0.5, parapet_mat='MD_Grey', skip=('back',))
    # back wall with two pickup windows
    holes_b = [(4.2, 1.25, 5.8, 2.5), (8.2, 1.25, 9.8, 2.5)]
    rects = [(BX0, 0.15, BX1, H - 0.35)]
    for hh in holes_b:
        rects = rect_subtract(rects, hh)
    for (x0, z0, x1, z1) in rects:
        b.add(bm_box(x0, BY1 - t, z0, x1, BY1, z1, open_bottom=z0 <= 0.2), 'MD_Grey')
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    for (x0, z0, x1, z1) in holes_b:
        gl.add(bm_quad((x1, BY1 - 0.1, z0), (x0, BY1 - 0.1, z0), (x0, BY1 - 0.1, z1), (x1, BY1 - 0.1, z1)), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
        if L < 2:
            fr.add(bm_box(x0 - 0.08, BY1, z0 - 0.08, x1 + 0.08, BY1 + 0.12, z0), 'RS_MetalBrushed')
            fr.add(bm_box(x0 - 0.08, BY1, z1, x1 + 0.08, BY1 + 0.12, z1 + 0.08), 'RS_MetalDark')
            for x in (x0 - 0.08, x1):
                fr.add(bm_box(x, BY1, z0, x + 0.08, BY1 + 0.12, z1), 'RS_MetalDark')
    # timber accent band + red band above the glazing
    b.add(bm_box(GX0, BY0 - 0.12, GZ1, BX1, BY0, H - 0.35, bevel=bv), 'RS_WoodV', uv='box')
    b.add(bm_box(BX0, BY0 - 0.14, H - 0.55, BX1, BY0, H + 0.1, bevel=bv), 'MD_Red')
    # red glazed tower (corner volume) carrying the arches
    b.add(bm_box(BX0, BY0 - 0.5, 0.0, TX1, BY0 + 6.0, TH, bevel=bv, open_bottom=True), 'MD_RedLit')
    b.add(bm_box(BX0 - 0.05, BY0 - 0.55, TH - 0.2, TX1 + 0.05, BY0 + 6.05, TH + 0.25, bevel=bv), 'MD_Grey')
    # slim cantilever entrance canopy with LED underside
    b.add(bm_box(-1.0, BY0 - 3.2, 4.3, 7.0, BY0, 4.6, bevel=bv), 'MD_LightGrey')
    b.add(bm_box(-1.02, BY0 - 3.25, 4.25, 7.02, BY0 - 3.1, 4.65, bevel=bv), 'MD_Red')
    if L < 2:
        b.add(bm_box(-0.6, BY0 - 2.9, 4.27, 6.6, BY0 - 2.6, 4.3), 'RS_LightWarm')
    for x in (-0.9, 6.9):
        b.add(bm_cyl(x, BY0 - 3.0, 0.0, 4.25, 0.09, 12 if L == 0 else 6, open_bottom=True), 'RS_MetalDark')
    s = A.m(L, 'Signage')
    golden_arches(s, L, place('-Y', ((BX0 + TX1) / 2, BY0 - 0.55, 2.3)), 4.4, 3.3, 0.25)
    md_wordmark(s, L, place('-Y', ((BX0 + TX1) / 2, BY0 - 0.55, 1.3)), 0.78, 0.06)
    golden_arches(s, L, place('-X', (BX0 - 0.03, BY0 + 3.2, 2.3)), 3.6, 2.7, 0.2)
    md_wordmark(s, L, place('-Y', (4.0, BY0 - 0.14, H - 0.2)), 0.55, 0.05)
    if L == 0:
        register_sign(A, 'McDonalds tower arches', ((BX0 + TX1) / 2, BY0 - 0.85, 4.1), 3.0, width=4.2)
        register_sign(A, 'McDonalds wordmark', ((BX0 + TX1) / 2, BY0 - 0.6, 1.3), 0.56, width=4.6)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=9, trans=(2.7,), doors=((DOOR_X, 2.4),), frame='RS_MetalDark', door_h=2.4, bottom_rail=0.1)
    # tower glazing strip (east face) lets the red volume read as glazed
    if L < 2:
        gl.add(bm_vquad(BX0 + 0.5, TX1 - 0.5, 4.0, 6.8, BY0 - 0.51), 'RS_Glass')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = TX1 + 0.1, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 4.1, 'RS_TileFloor', 'MD_White', lights=light_grid((ix0, iy0, ix1, iy1), 6, 3, (1.4, 0.3), 1.2), back_mat='MD_Red')
    # service counter + back kitchen line + menu screens
    counter(it, L, -5.5, 12.0, 8.5, 13.2, 1.05, 'MD_Red', 'MD_White')
    it.add(bm_box(ix0, iy1 - 5.8, 0.15, ix1, iy1, 2.4, open_bottom=True), 'RS_MetalBrushed')
    for i in range(5):
        x = -4.5 + i * 3.2
        it.add(bm_box(x - 1.1, 12.0, 2.55, x + 1.1, 12.06, 3.5), 'MD_Menu')
    # seating: tables with red/yellow chairs and wall booths
    k = 0
    for j, y in enumerate((5.2, 8.4)):
        for i, x in enumerate((-4.5, -0.5, 3.5, 7.5)):
            cafe_set(it, L, x, y, 4 if (i + j) % 2 == 0 else 2, ang=45 * ((i + j) % 2), table_mat='MD_White', chair_mat='RS_MetalDark',
                     seat_mat='MD_Seat' if (i + j) % 2 == 0 else 'MD_SeatY', r=0.34)
            k += 1
    # booth bench along the glazing
    it.add(bm_box(ix0 + 0.3, 3.6, 0.15, GX1 - 0.3, 4.1, 0.9, bevel=0.02 if L == 0 else 0, open_bottom=True), 'MD_Seat')
    # back-of-house pickup shelves at the rear windows
    it.add(bm_box(3.6, 17.6, 0.15, 10.4, 18.4, 1.1, open_bottom=True), 'RS_MetalBrushed')
    # tower interior glow panel
    it.add(bm_hquad(BX0 + 0.4, BY0 - 0.4, TX1 - 0.4, BY0 + 5.8, 0.16), 'MD_White')
    it.add(bm_hquad(BX0 + 0.4, BY0 - 0.4, TX1 - 0.4, BY0 + 5.8, 7.5, down=True), 'RS_LightPanel')


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = 22.6, -21.9
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.0, cy - 0.5, 0.0, cx + 1.0, cy + 0.5, 0.5, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 0.35, cy - 0.3, 0.5, cx + 0.35, cy + 0.3, 7.5, bevel=bv), 'MD_Grey')
    p.add(bm_box(cx - 1.6, cy - 0.3, 6.0, cx + 1.6, cy + 0.3, 9.4, bevel=bv), 'MD_RedLit')
    p.add(bm_box(cx - 1.62, cy - 0.32, 9.4, cx + 1.62, cy + 0.32, 9.5), 'MD_Grey')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.3), ('+Y', cy + 0.3)):
        golden_arches(s, L, place(face, (cx, yy, 6.9)), 2.5, 1.9, 0.18)
        txt(s, L, "McDonald's", place(face, (cx, yy, 6.3)), 0.4, 0.04, 'black', 'MD_SignWhite', 'RS_PaintWhite', min_size_lod2=9)
    if L == 0:
        register_sign(A, 'McDonalds pylon arches', (cx, cy - 0.52, 8.0), 1.9, width=2.5)


LAMPS = [(-8.0, -22.0, 0, 1), (6.0, -22.0, 0, 1), (-30.0, -2.0, 1, 0), (30.0, -2.0, -1, 0), (-30.0, 16.0, 1, 0), (30.0, 16.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H + 0.6)
    A.col_box('Tower', BX0, BY0 - 0.55, 0.0, TX1, BY0 + 6.05, TH + 0.25)
    A.col_box('EntranceCanopy', -1.0, BY0 - 3.2, 4.25, 7.0, BY0, 4.65)
    A.col_box('OrderCanopy', 14.0, 7.0, 3.3, 22.8, 11.0, 3.6)
    A.col_box('PickupCanopy', 1.0, BY1, 3.3, 12.5, BY1 + 3.4, 3.6)
    A.col_box('Pylon', 21.0, -22.2, 0.0, 24.2, -21.6, 9.5)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-2.0, 3.0, 8.0)):
        A.light(f'Canopy{i}', 'SPOT', (x, BY0 - 1.8, 4.2), 1000, '#fff0d8', spot_deg=125, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-2.0, 7.0, 3.7), (4.0, 7.0, 3.7), (9.0, 7.0, 3.7), (3.0, 14.0, 3.7), (-10.5, 6.0, 6.5)], energy=1200, color='#fff0e0')
    sign_light(A, 'ArchGlow', (-10.7, -4.0, 4.0), 2200, '#ffd890')
    sign_light(A, 'PylonGlow', (22.6, -26.0, 8.0), 2600, '#ffd0c0')
    A.light('OrderCanopy', 'SPOT', (18.4, 9.0, 3.2), 900, '#fff0d8', rot=(180, 0, 0), spot_deg=130, blend=0.8, radius=0.3)
    A.light('PickupCanopy', 'SPOT', (6.0, BY1 + 1.7, 3.2), 900, '#fff0d8', rot=(180, 0, 0), spot_deg=130, blend=0.8, radius=0.3)
    lamp_lights(A, LAMPS)


def main():
    A = Store('08', '08_mcdonalds', 'mcdonalds', 'MCD', 'Restaurant', "McDonald's")
    A.dims = dict(plot=[64.0, 48.0], building=[BX1 - BX0, BY1 - BY0, H], tower_height=TH + 0.25, pylon_height=9.5)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-27.0, -33.0, 4.4), (-2.0, 4.0, 3.0), 32)
    A.camera('road', (-38.0, PLOT[1] - 8.6, 1.25), (-8.0, -4.0, 4.0), 30)
    A.camera('detail', (-4.0, -12.5, 1.8), (-6.0, 3.0, 3.8), 28)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
