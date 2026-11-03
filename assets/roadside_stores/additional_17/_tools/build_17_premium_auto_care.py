"""ASSET 17 - Premium Auto Care / Detailing Centre (E11 roadside).

Plot 52 m x 40 m, road side faces -Y, origin = plot centre at finished ground.
Massing: glass-fronted showroom (display car on a turntable) + service block with three detailing bays behind raised
roller doors (one car on a lift), polishing / pressure-wash equipment, covered wash canopy with foam stands and
vacuum posts, concrete wash apron, customer parking, branded pylon.
'Premium Auto Care' is an original generic brand created for this asset: no third-party partnership is implied.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-26.0, -20.0, 26.0, 20.0)
BX0, BY0, BX1, BY1 = -15.0, 2.0, 15.0, 17.0
SX1 = -3.0                                     # showroom x range: BX0..SX1 ; service block: SX1..BX1
H_SHOW, H_SRV = 5.6, 6.4
GX0, GX1, GZ1 = -14.4, -3.6, 4.4
BAYS = [(1.2, 4.2), (7.0, 4.2), (12.8, 4.2)]   # (xc, width)
BAY_H = 3.7
APRON = (-4.0, -10.0, 15.6, BY0)
CANOPY = (17.5, 3.0, 25.0, 14.0)
ENTRY, EXIT = (-25.0, -19.0), (19.0, 25.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.2) + [(-26.0, -18.0, -25.2, 20.0), (25.2, -18.0, 26.0, 20.0), (-25.0, 18.5, 25.0, 20.0)]

defmat('AC_Charcoal', '#2a2d32', rough=0.4, metal=0.3)
defmat('AC_Dark', '#1b1d21', rough=0.45, metal=0.4)
defmat('AC_Orange', '#ff6a13', rough=0.32, spec=0.6)
defmat('AC_OrangeLit', '#ff6a13', rough=0.3, emit='#ff7a24', es=1.4)
defmat('AC_White', '#f1f2f3', rough=0.3, metal=0.05)
defmat('AC_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('AC_Epoxy', '#cfd3d6', rough=0.15)
defmat('AC_LED', '#ffffff', rough=0.3, emit='#f4f8ff', es=6.0)
defmat('AC_Yellow', '#f2c200', rough=0.4)
defmat('AC_Red', '#c4201c', rough=0.4)
defmat('AC_Foam', '#fdfdfd', rough=0.9)
defmat('AC_Menu', '#0e1013', rough=0.25, emit='#dfe9ff', es=0.9)


def ac_badge(acc, L, M, r=0.6, depth=0.07):
    """Hexagonal orange shield with a white 'P' (original generic mark)."""
    pts = [(r * math.cos(math.radians(30 + 60 * i)), r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    acc.add(bm_prism_local(pts, depth), 'AC_OrangeLit', matrix=M, mat_fn=front_back('AC_OrangeLit', 'AC_Orange'))
    txt(acc, L, 'P', M @ Matrix.Translation((0, 0, depth)), r * 1.25, depth * 0.7, 'black', 'AC_SignWhite', 'AC_White', min_size_lod2=0.3)


def ac_lockup(acc, L, M, size=0.9, depth=0.07):
    txt(acc, L, 'PREMIUM AUTO CARE', M, size, depth, 'black', 'AC_SignWhite', 'AC_White', spacing=1.04)


def lift(acc, L, x, y, h=1.6):
    if L == 2:
        return
    for sx in (-1.5, 1.5):
        acc.add(bm_box(x + sx - 0.12, y - 0.5, 0.15, x + sx + 0.12, y - 0.2, 2.6, bevel=0.02 if L == 0 else 0, open_bottom=True), 'AC_Yellow')
        acc.add(bm_box(x + sx - 0.05, y - 0.2, h - 0.12, x + sx + 0.05, y + 1.8, h - 0.04), 'AC_Yellow')
    acc.add(bm_box(x - 1.5, y - 0.5, 2.5, x + 1.5, y - 0.2, 2.6), 'AC_Yellow')


def foam_stand(acc, L, x, y):
    if L == 2:
        return
    acc.add(bm_box(x - 0.3, y - 0.2, 0.0, x + 0.3, y + 0.2, 1.3, bevel=0.02 if L == 0 else 0, open_bottom=True), 'AC_Dark')
    acc.add(bm_box(x - 0.25, y - 0.21, 0.9, x + 0.25, y - 0.2, 1.2), 'AC_OrangeLit')
    acc.add(bm_cyl(x + 0.4, y, 0.0, 0.9, 0.12, 10 if L == 0 else 5), 'AC_Orange')


def vacuum_post(acc, L, x, y):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, 0.0, 2.6, 0.09, 8 if L == 0 else 5, open_bottom=True), 'AC_Dark')
    acc.add(bm_box(x - 0.3, y - 0.2, 1.1, x + 0.3, y + 0.2, 1.7, bevel=0.03 if L == 0 else 0), 'AC_Orange')
    if L == 0:
        for i in range(8):
            t0, t1 = i / 8, (i + 1) / 8
            acc.add(bm_cyl_between((x + 0.3, y, 1.4 - 0.9 * t0), (x + 0.3 + 0.45 * math.sin(math.pi * t1), y, 1.4 - 0.9 * t1), 0.04, 5, caps=False), 'RS_Rubber')


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (CANOPY[0] - 0.2, CANOPY[1] - 0.2, CANOPY[2] + 0.2, CANOPY[3] + 0.2), (-4.4, -19.6, -1.0, -18.0)]
    wash = (CANOPY[0] - 0.5, CANOPY[1] - 3.0, CANOPY[2] + 0.5, CANOPY[3] + 1.0)
    site_ground(A, L, PLOT, holes, [APRON, wash], BEDS, paver_h=0.1, mat_paved='RS_Concrete')
    land = A.m(L, 'Landscape')
    palms(A, L, [(24.5, -17.0), (-24.5, 10.0), (24.5, 16.0), (-12.0, 18.8), (12.0, 18.8)], 290)
    rng = random.Random(15)
    for i in range(30):
        x = -22.0 + i * 1.5
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or -5.0 < x < -0.5:
            continue
        (R.grass_clump(land, L, x, -19.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -19.0, 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -22.0, 22.0, depth=2.2)
    cars = {1: ('RS_CarBlack', 'suv'), 4: ('RS_CarSilver', 'sedan')}
    parking_row(A, L, -24.0, -15.5, -10.5, 7, 2.6, cars)
    disabled_bay(A, L, -24.0 + 2.6 * 7 + 1.3, -15.5, -10.5)
    # wash-apron drain strips (LOD0/1)
    if L < 2:
        mk = A.m(L, 'Markings')
        for k in range(3):
            mk.add(bm_box(-3.8, -3.0 - k * 2.4, 0.1, 15.4, -2.9 - k * 2.4, 0.115), 'AC_Dark')
    v = A.m(L, 'Vehicles')
    # covered wash canopy: slab on four posts, foam stands, vacuum posts, a foamed car
    c = A.m(L, 'Canopy')
    bv = 0.03 if L == 0 else 0.0
    x0, y0, x1, y1 = CANOPY
    c.add(bm_box(x0, y0, 4.4, x1, y1, 4.7, bevel=bv), 'AC_Charcoal')
    c.add(bm_box(x0 - 0.05, y0 - 0.05, 4.35, x1 + 0.05, y0 + 0.2, 4.95, bevel=bv), 'AC_Orange')
    for (px, py) in ((x0 + 0.3, y0 + 0.3), (x1 - 0.3, y0 + 0.3), (x0 + 0.3, y1 - 0.3), (x1 - 0.3, y1 - 0.3)):
        c.add(bm_box(px - 0.15, py - 0.15, 0.1, px + 0.15, py + 0.15, 4.4, open_bottom=False), 'AC_Dark')
    if L < 2:
        for yy in (5.5, 8.5, 11.5):
            c.add(bm_box(x0 + 1.0, yy - 0.15, 4.37, x1 - 1.0, yy + 0.15, 4.4), 'AC_LED')
    car(v, L, 21.3, 8.0, 90, 'RS_CarBlue', 'sedan')
    if L < 2:
        for i in range(14 if L == 0 else 5):
            a = random.Random(i).uniform(0, math.tau)
            v.add(bm_sphere((21.3 + 0.55 * math.cos(a), 8.0 + 0.9 * math.sin(a * 1.7), 1.45 + 0.04 * (i % 3)), 0.22, 1, (1, 1, 0.5)), 'AC_Foam')
    eq = A.m(L, 'Equipment')
    foam_stand(eq, L, 18.3, 4.2); foam_stand(eq, L, 24.2, 4.2)
    vacuum_post(eq, L, 18.3, 13.0); vacuum_post(eq, L, 21.0, 13.0); vacuum_post(eq, L, 23.8, 13.0)
    # concrete wash apron lamp + bin + towel rack
    f = A.m(L, 'Furniture')
    bin_(f, L, 16.2, 1.5, 'AC_Dark')
    planter(f, L, -14.0, -4.0, -5.0, -3.2, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=3)


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.35
    # showroom shell (glass front) + service block shell (bay openings)
    shell(b, L, (BX0, BY0, SX1, BY1), H_SHOW, 'AC_Charcoal', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='AC_Charcoal', roof_mat='AC_White', roof_t=0.4,
          parapet=0.0, skip=('right',), rooftop=False)
    holes = [(xc - w / 2, 0.15, xc + w / 2, BAY_H) for xc, w in BAYS]
    shell(b, L, (SX1, BY0, BX1, BY1), H_SRV, 'AC_Charcoal', t=t, holes=holes, front_mat='AC_Charcoal', roof_mat='AC_White', roof_t=0.4, parapet=0.4, parapet_mat='AC_Charcoal',
          skip=('left',))
    # showroom: deep roof overhang + orange fascia; service block: orange stripe above the doors
    b.add(bm_box(BX0 - 0.2, BY0 - 3.0, H_SHOW - 0.4, SX1 + 0.2, BY0, H_SHOW, bevel=bv), 'AC_White')
    b.add(bm_box(BX0 - 0.22, BY0 - 3.05, H_SHOW - 0.45, SX1 + 0.22, BY0 - 2.9, H_SHOW + 0.05), 'AC_Orange')
    for x in (BX0 + 0.5, SX1 - 0.5):
        b.add(bm_cyl(x, BY0 - 2.7, 0.0, H_SHOW - 0.4, 0.1, 12 if L == 0 else 6, open_bottom=True), 'AC_Dark')
    b.add(bm_box(SX1, BY0 - 0.15, BAY_H + 0.1, BX1, BY0, BAY_H + 0.35, bevel=bv), 'AC_Orange')
    b.add(bm_box(SX1, BY0 - 0.12, BAY_H + 0.35, BX1, BY0, H_SRV - 0.4, bevel=bv), 'AC_Dark')
    # raised roller doors (coil box above the opening + side guides)
    for xc, w in BAYS:
        b.add(bm_box(xc - w / 2 - 0.1, BY0 - 0.3, BAY_H, xc + w / 2 + 0.1, BY0 + 0.1, BAY_H + 0.55, bevel=bv), 'AC_Dark')
        if L < 2:
            for sx in (xc - w / 2 - 0.12, xc + w / 2 + 0.02):
                b.add(bm_box(sx, BY0 - 0.2, 0.15, sx + 0.1, BY0 + 0.1, BAY_H, open_bottom=True), 'RS_MetalBrushed')
            for k in range(6):
                b.add(bm_box(xc - w / 2, BY0 - 0.26, BAY_H + 0.04 + k * 0.08, xc + w / 2, BY0 - 0.12, BAY_H + 0.08 + k * 0.08), 'RS_MetalGalv') if L == 0 else None
    s = A.m(L, 'Signage')
    ac_lockup(s, L, place('-Y', (7.4, BY0 - 0.12, 5.6)), 0.92, 0.07)
    ac_badge(s, L, place('-Y', (-0.9, BY0 - 0.12, 5.6)), 0.62, 0.07)
    ac_badge(s, L, place('-Y', ((BX0 + SX1) / 2 - 4.2, BY0 - 3.0, H_SHOW - 0.2)), 0.45, 0.06)
    txt(s, L, 'DETAILING • CERAMIC COATING • PPF • WASH', place('-Y', ((BX0 + SX1) / 2 + 0.8, BY0 - 3.07, H_SHOW - 0.2)), 0.22, 0.04, 'bold', 'AC_OrangeLit', 'AC_Orange', spacing=1.1, min_size_lod2=9)
    ac_lockup(s, L, place('+X', (BX1 + 0.02, 9.0, 5.0)), 0.7, 0.06)
    if L == 0:
        register_sign(A, 'PREMIUM AUTO CARE wordmark', (7.4, BY0 - 0.24, 5.6), 0.66, width=9.0)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=6, trans=(2.8,), doors=((-9.0, 2.2),), frame='AC_Dark', door_h=2.4, fd=0.14)


def build_interior(A, L):
    if L == 2:
        return
    # showroom
    ix0, iy0, ix1, iy1 = BX0 + 0.35, BY0 + 0.35, SX1 - 0.05, BY1 - 0.35
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 5.0, 'RS_TileFloor', 'AC_White', lights=light_grid((ix0, iy0, ix1, iy1), 4, 3, (1.6, 0.2), 1.2), back_mat='AC_Charcoal')
    # display car on a turntable with spotlights
    it.add(bm_cyl(-9.0, 6.0, 0.15, 0.4, 2.8, 24 if L == 0 else 12), 'AC_Dark')
    it.add(bm_cyl(-9.0, 6.0, 0.4, 0.43, 2.7, 24 if L == 0 else 12), 'AC_OrangeLit')
    car(A.m(L, 'Vehicles'), L, -9.0, 6.0, 35, 'RS_CarGold', 'sedan', z=0.43)
    counter(it, L, -13.5, 11.5, -6.0, 12.6, 1.05, 'AC_Charcoal', 'AC_White')
    for i in range(3):
        x = -12.5 + i * 2.4
        it.add(bm_box(x - 1.0, BY1 - 0.7, 1.4, x + 1.0, BY1 - 0.66, 3.0), 'AC_Menu')
    R.product_shelf(it, L, -14.0, 8.5, -11.0, 9.3, 1.8, 4, seed=700)
    # service bays interior
    sx0, sy0, sx1, sy1 = SX1 + 0.3, BY0 + 0.35, BX1 - 0.35, BY1 - 0.35
    sv = interior_shell(A, L, (sx0, sy0, sx1, sy1), 5.8, 'AC_Epoxy', 'AC_White', lights=[], back_mat='AC_Charcoal')
    for k, xc in enumerate((1.2, 7.0, 12.8)):
        sv.add(bm_box(xc - 1.9, 4.0, 5.77, xc + 1.9, 4.3, 5.8), 'AC_LED')
        sv.add(bm_box(xc - 1.9, 8.5, 5.77, xc + 1.9, 8.8, 5.8), 'AC_LED')
        sv.add(bm_box(xc - 1.9, 13.0, 5.77, xc + 1.9, 13.3, 5.8), 'AC_LED')
    v = A.m(L, 'Vehicles')
    car(v, L, 1.2, 8.0, 90, 'RS_CarRed', 'hatch')                  # bay 1: car being detailed
    lift(sv, L, 7.0, 6.0, 1.5)                                       # bay 2: car on a lift
    car(v, L, 7.0, 7.8, 90, 'RS_CarSilver', 'suv', z=1.5)
    if L == 0:
        # bay 3: polishing stand, tool chest, pressure-washer unit
        sv.add(bm_cyl(12.0, 7.0, 0.15, 1.3, 0.04, 6), 'AC_Dark')
        sv.add(bm_cyl(12.0, 7.0, 1.3, 1.36, 0.3, 14), 'AC_Orange')
        sv.add(bm_box(14.0, 6.0, 0.15, 14.6, 7.4, 1.2, bevel=0.02), 'AC_Red')
        sv.add(bm_box(10.6, 11.0, 0.15, 11.5, 11.7, 1.0, bevel=0.02), 'AC_Orange')
        sv.add(bm_cyl(11.05, 11.35, 1.0, 1.1, 0.1, 10), 'RS_MetalBrushed')
        for i in range(5):
            sv.add(bm_cyl(14.2, 12.0 + i * 0.1, 0.15 + i * 0.12, 0.25 + i * 0.12, 0.3, 12), 'RS_Rubber')   # tyre stack


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = -2.6, -18.8
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.6, cy - 0.5, 0.0, cx + 1.6, cy + 0.5, 0.4, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 1.3, cy - 0.3, 0.4, cx + 1.3, cy + 0.3, 8.4, bevel=bv), 'AC_Charcoal')
    p.add(bm_box(cx - 1.32, cy - 0.32, 6.1, cx + 1.32, cy + 0.32, 8.45, bevel=bv), 'AC_Dark')
    p.add(bm_box(cx - 1.35, cy - 0.34, 5.95, cx + 1.35, cy + 0.34, 6.1), 'AC_OrangeLit')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.32), ('+Y', cy + 0.32)):
        ac_badge(s, L, place(face, (cx, yy, 7.5)), 0.6, 0.07)
        txt(s, L, 'PREMIUM', place(face, (cx, yy, 6.6)), 0.4, 0.05, 'black', 'AC_SignWhite', 'AC_White', spacing=1.1, min_size_lod2=9)
        txt(s, L, 'AUTO CARE', place(face, (cx, yy, 5.0)), 0.52, 0.05, 'black', 'AC_SignWhite', 'AC_White', spacing=1.06, min_size_lod2=9)
        txt(s, L, 'DETAILING CENTRE', place(face, (cx, yy, 4.3)), 0.2, 0.03, 'bold', 'AC_OrangeLit', 'AC_Orange', spacing=1.3, min_size_lod2=9)
        txt(s, L, 'OPEN 7 DAYS', place(face, (cx, yy, 3.6)), 0.2, 0.03, 'bold', 'AC_White', 'AC_White', spacing=1.3, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'PREMIUM AUTO CARE pylon', (cx, cy - 0.38, 5.0), 0.38, width=2.4)


LAMPS = [(4.0, -19.0, 0, 1), (16.0, -19.0, 0, 1), (-25.0, 4.0, 1, 0), (25.0, 4.0, -1, 0), (0.0, 19.0, 0, -1)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Showroom', BX0, BY0, 0.0, SX1, BY1, H_SHOW)
    A.col_box('ServiceBlock', SX1, BY0 - 0.1, 0.0, BX1, BY1, H_SRV + 0.4)
    A.col_box('ShowroomRoof', BX0 - 0.2, BY0 - 3.0, H_SHOW - 0.45, SX1 + 0.2, BY0, H_SHOW + 0.05)
    A.col_box('WashCanopy', CANOPY[0], CANOPY[1], 4.35, CANOPY[2], CANOPY[3], 4.95)
    for i, (px, py) in enumerate(((CANOPY[0] + 0.3, CANOPY[1] + 0.3), (CANOPY[2] - 0.3, CANOPY[1] + 0.3), (CANOPY[0] + 0.3, CANOPY[3] - 0.3), (CANOPY[2] - 0.3, CANOPY[3] - 0.3))):
        A.col_box(f'CanopyPost{i}', px - 0.2, py - 0.2, 0.0, px + 0.2, py + 0.2, 4.4)
    A.col_box('Apron', *APRON[:2], 0.0, *APRON[2:], 0.1)
    A.col_box('Pylon', -4.2, -19.2, 0.0, -1.0, -18.4, 8.45)
    lamp_collision(A, LAMPS, 8.0)


def build_lights(A):
    glow_lights(A, 'Showroom', [(-12.0, 5.0, 4.6), (-9.0, 5.0, 4.6), (-6.0, 5.0, 4.6), (-9.0, 10.0, 4.6)], energy=1500, color='#f4f8ff')
    for i, (x, y) in enumerate(((-9.0, 3.0), (-9.0, 9.0))):
        A.light(f'Spot{i}', 'SPOT', (x, y, 4.9), 900, '#fff4e0', rot=(180, 0, 0), spot_deg=60, blend=0.7, radius=0.1)
    for i, xc in enumerate((1.2, 7.0, 12.8)):
        glow_lights(A, f'Bay{i}_', [(xc, 5.0, 5.4), (xc, 11.0, 5.4)], energy=1400, color='#f2f6ff', radius=0.6)
    for i, x in enumerate((19.5, 23.0)):
        A.light(f'Wash{i}', 'SPOT', (x, 8.5, 4.3), 1400, '#f4f8ff', rot=(180, 0, 0), spot_deg=120, blend=0.8, radius=0.3)
    A.light('ShowroomEave', 'SPOT', (-9.0, BY0 - 1.5, 5.1), 1100, '#fff4e4', rot=(180, 0, 0), spot_deg=130, blend=0.8, radius=0.3)
    sign_light(A, 'BoardGlow', (7.4, -6.0, 5.6), 2600, '#fff0e0')
    sign_light(A, 'PylonGlow', (-2.6, -23.0, 6.5), 2200, '#fff0e0')
    lamp_lights(A, LAMPS, 7.9, 1.3, 2200)


def main():
    A = Store('17', '17_premium_auto_care', 'premium_auto_care', 'PAC', 'DetailingCentre', 'Premium Auto Care')
    A.dims = dict(plot=[52.0, 40.0], building=[BX1 - BX0, BY1 - BY0, H_SRV], showroom_height=H_SHOW, pylon_height=8.45, bays=3)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L)
        lamp_set(A, L, LAMPS, 8.0, 1.3)
    build_collision(A); build_lights(A)
    A.camera('day', (-24.0, -33.0, 4.6), (1.0, 6.0, 3.4), 32)
    A.camera('road', (-23.0, PLOT[1] - 8.6, 1.25), (4.0, -4.0, 4.6), 30)
    A.camera('detail', (4.0, -12.0, 1.7), (5.0, 3.0, 3.4), 27)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
