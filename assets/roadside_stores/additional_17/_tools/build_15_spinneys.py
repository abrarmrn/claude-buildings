"""ASSET 15 - Spinneys Market (premium supermarket; general commercial retail).

Plot 64 m x 44 m, road side faces -Y, origin = plot centre at finished ground.
Massing: tall white volume with travertine side wings, wide glass hall behind a deep entrance portico (green
fascia, slim columns), large green wordmark, produce tables + aisles of shelves visible through the glazing,
two parking rows with trolley shelters, pylon sign. Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-32.0, -22.0, 32.0, 22.0)
BX0, BY0, BX1, BY1 = -18.0, 3.0, 18.0, 19.0
H = 7.4
GX0, GX1, GZ1 = -12.0, 12.0, 5.2
DOORS = ((-3.0, 3.0), (3.0, 3.0))
POR = (-14.0, -3.0, 14.0, BY0)                  # portico footprint
ZP0, ZP1 = 4.6, 5.1
ENTRY, EXIT = (-31.0, -24.0), (24.0, 31.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.0) + [(-32.0, -20.0, -31.2, 22.0), (31.2, -20.0, 32.0, 22.0), (-31.0, 20.0, 31.0, 22.0)]
PAVED = [(-16.0, -3.0, 16.0, BY0)]

defmat('SP_Green', '#0b7a43', rough=0.35, spec=0.6)
defmat('SP_GreenLit', '#0b7a43', rough=0.32, emit='#18b868', es=0.8)
defmat('SP_White', '#f3f2ee', rough=0.35, metal=0.05)
defmat('SP_Fascia', '#f6f5f1', rough=0.4, emit='#fff6e8', es=0.5)
defmat('SP_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('SP_Menu', '#10120f', rough=0.25, emit='#e8ffe8', es=0.9)
defmat('SP_Apple', '#c4231c', rough=0.5)
defmat('SP_Orange', '#ee8a1c', rough=0.5)
defmat('SP_Lemon', '#f1d229', rough=0.5)
defmat('SP_Leaf', '#4fa83a', rough=0.6)
defmat('SP_Crate', '#8a6a44', rough=0.7)
defmat('SP_Trolley', '#a9aeb2', rough=0.35, metal=1.0)


def sp_logo(acc, L, M, size=1.6, depth=0.08):
    txt(acc, L, 'Spinneys', M, size, depth, 'bold', 'SP_GreenLit', 'SP_Green', spacing=0.99)


def trolley_shelter(acc, L, x, y, n=8):
    bv = 0.02 if L == 0 else 0.0
    acc.add(bm_box(x - 1.6, y - 0.6, 1.9, x + 1.6, y + 0.6, 2.05, bevel=bv), 'SP_Green')
    for sx in (-1.5, 1.5):
        for sy in (-0.5, 0.5):
            acc.add(bm_box(x + sx - 0.03, y + sy - 0.03, 0.0, x + sx + 0.03, y + sy + 0.03, 1.9, open_bottom=True), 'RS_MetalDark')
    for i in range(n if L == 0 else 3):
        acc.add(bm_box(x - 1.4 + i * 0.35, y - 0.35, 0.15, x - 1.4 + i * 0.35 + 0.3, y + 0.35, 0.95), 'SP_Trolley')


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (-27.0, -21.6, -23.8, -20.0)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(-30.5, -18.0), (30.5, -18.0), (-30.5, 6.0), (30.5, 6.0), (-30.5, 18.0), (30.5, 18.0), (-24.0, 20.8), (24.0, 20.8), (0.0, 20.8)], 270)
    rng = random.Random(91)
    for i in range(34):
        x = -26.0 + i * 1.6
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or -28.0 < x < -23.0:
            continue
        (R.grass_clump(land, L, x, -21.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -21.0, 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -27.5, 27.5, depth=2.0)
    cols = ['RS_CarWhite', 'RS_CarSilver', 'RS_CarBlack', 'RS_CarBlue', 'RS_CarGrey', 'RS_CarRed', 'RS_CarGold']
    kinds = ['sedan', 'suv', 'hatch', 'suv', 'sedan']
    rng2 = random.Random(7)
    carsA = {i: (cols[rng2.randrange(7)], kinds[rng2.randrange(5)]) for i in (0, 2, 3, 6, 9, 11, 12)}
    carsB = {i: (cols[rng2.randrange(7)], kinds[rng2.randrange(5)]) for i in (1, 4, 5, 8, 10)}
    parking_row(A, L, -16.0, -18.5, -13.0, 12, 2.6, carsA)
    parking_row(A, L, -16.0, -11.0, -5.5, 12, 2.6, carsB)
    disabled_bay(A, L, -16.0 + 2.6 * 12 + 1.3, -18.5, -13.0)
    disabled_bay(A, L, -16.0 - 1.3, -11.0, -5.5)
    # trolley shelters at the aisle ends
    f = A.m(L, 'Furniture')
    for (x, y) in ((-17.5, -12.0), (16.5, -12.0), (-17.5, -4.2)):
        trolley_shelter(f, L, x, y)
    planter(f, L, -16.0, -3.2, -14.2, -2.4, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=1)
    planter(f, L, 14.2, -3.2, 16.0, -2.4, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=2)
    for x in (-13.0, 13.0):
        bin_(f, L, x, -2.0, 'SP_Green')
    bench(f, L, -15.0, 1.2, 2.0, 0, 'RS_WoodV')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.4
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'SP_White', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='SP_White', roof_mat='SP_White', roof_t=0.45,
          parapet=0.6, parapet_mat='SP_White')
    # travertine wings with green vertical accent fins
    for (xa, xb) in ((BX0, GX0), (GX1, BX1)):
        b.add(bm_box(xa, BY0 - 0.15, 0.0, xb, BY0, H - 1.9, bevel=bv, open_bottom=True), 'RS_Travertine')
    for x in (GX0 - 0.6, GX1 + 0.1):
        b.add(bm_box(x, BY0 - 0.3, 0.0, x + 0.5, BY0, H - 0.6, bevel=bv, open_bottom=True), 'SP_Green')
    # tall white fascia above the glass hall + green stripe + green band
    b.add(bm_box(GX0, BY0 - 0.2, GZ1, GX1, BY0 + 0.1, H + 0.5, bevel=bv), 'SP_Fascia')
    b.add(bm_box(BX0, BY0 - 0.25, H + 0.15, BX1, BY0 + 0.1, H + 0.6, bevel=bv), 'SP_Green')
    # entrance portico: slab, green fascia, slim columns, light panels
    x0, y0, x1, y1 = POR
    b.add(bm_box(x0, y0, ZP0, x1, y1, ZP1, bevel=bv), 'SP_White')
    b.add(bm_box(x0 - 0.05, y0 - 0.05, ZP0 - 0.1, x1 + 0.05, y0 + 0.2, ZP1 + 0.35, bevel=bv), 'SP_Green')
    for x in (-13.4, -7.0, 0.0, 7.0, 13.4):
        b.add(bm_box(x - 0.2, y0 + 0.5, 0.12, x + 0.2, y0 + 0.9, ZP0, bevel=bv, open_bottom=True), 'RS_MetalBrushed')
    if L < 2:
        for x in range(-12, 13, 4):
            b.add(bm_box(x - 0.8, -1.5, ZP0 - 0.03, x + 0.8, -1.2, ZP0), 'RS_LightPanel')
            b.add(bm_box(x - 0.8, 0.8, ZP0 - 0.03, x + 0.8, 1.1, ZP0), 'RS_LightPanel')
    s = A.m(L, 'Signage')
    sp_logo(s, L, place('-Y', (0.0, BY0 - 0.2, 6.95)), 1.35, 0.09)
    sp_logo(s, L, place('+X', (BX1 + 0.02, 6.0, 5.9)), 1.2, 0.07)
    sp_logo(s, L, place('-X', (BX0 - 0.02, 6.0, 5.9)), 1.2, 0.07)
    if L == 0:
        register_sign(A, 'Spinneys fascia wordmark', (0.0, BY0 - 0.32, 6.95), 0.97, width=6.4)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=12, trans=(2.5,), doors=DOORS, frame='RS_MetalBrushed', door_h=2.5, fd=0.14)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.4, BY0 + 0.4, BX1 - 0.4, BY1 - 0.4
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 6.0, 'RS_TileFloor', 'SP_White', lights=light_grid((ix0, iy0, ix1, iy1), 8, 4, (2.4, 0.3), 1.5), back_mat='SP_White')
    it.add(bm_vquad(ix0, ix1, 4.2, 4.9, iy1 - 0.004), 'SP_GreenLit')
    # produce tables right behind the glass: crates with fruit
    rng = random.Random(3)
    fm = ['SP_Apple', 'SP_Orange', 'SP_Lemon', 'SP_Leaf', 'SP_Apple', 'SP_Orange']
    for k, x in enumerate((-10.5, -7.0, -3.0, 3.0, 7.0, 10.5)):
        it.add(bm_box(x - 1.3, 4.0, 0.15, x + 1.3, 5.2, 0.8, bevel=0.02 if L == 0 else 0, open_bottom=True), 'SP_Crate')
        if L == 0:
            for i in range(6):
                for j in range(3):
                    it.add(bm_sphere((x - 1.0 + i * 0.4, 4.35 + j * 0.35, 0.92), 0.14, 1, jitter=0.05, seed=i + j), fm[(k + i + j) % 6])
        else:
            it.add(bm_box(x - 1.2, 4.1, 0.8, x + 1.2, 5.1, 1.0), fm[k % 6])
    # gondola aisles with product shelves
    kk = 0
    for y in (8.5, 11.2, 13.9):
        for xa, xb in ((-16.0, -9.0), (-7.5, -0.5), (1.0, 8.0), (9.5, 16.0)):
            R.product_shelf(it, L, xa, y - 0.45, xb, y + 0.45, 1.9, 5, seed=400 + kk)
            kk += 1
    # checkout lanes + back wall chillers
    for i in range(5):
        counter(it, L, -12.0 + i * 5.0, 6.2, -10.2 + i * 5.0, 7.2, 1.0, 'SP_Green', 'SP_White')
    it.add(bm_box(ix0, iy1 - 1.0, 0.15, ix1, iy1, 2.6, open_bottom=True), 'RS_PaintCharcoal')
    it.add(bm_vquad(ix0 + 0.5, ix1 - 0.5, 0.4, 2.5, iy1 - 1.005), 'RS_Cooler')
    for i in range(6):
        x = -13.0 + i * 5.2
        it.add(bm_box(x - 1.4, 8.3, 3.6, x + 1.4, 8.36, 4.4), 'SP_Menu')


def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = 24.5, -20.8
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.8, cy - 0.5, 0.0, cx + 1.8, cy + 0.5, 0.4, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 1.4, cy - 0.3, 0.4, cx + 1.4, cy + 0.3, 3.2, bevel=bv), 'RS_Travertine')
    p.add(bm_box(cx - 1.5, cy - 0.33, 3.2, cx + 1.5, cy + 0.33, 8.0, bevel=bv), 'SP_Fascia')
    p.add(bm_box(cx - 1.55, cy - 0.35, 7.8, cx + 1.55, cy + 0.35, 8.1), 'SP_Green')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.33), ('+Y', cy + 0.33)):
        txt(s, L, 'Spinneys', place(face, (cx, yy, 6.0)), 0.95, 0.07, 'bold', 'SP_GreenLit', 'SP_Green', spacing=0.99)
        txt(s, L, 'MARKET', place(face, (cx, yy, 5.1)), 0.34, 0.05, 'semi', 'SP_GreenLit', 'SP_Green', spacing=2.0, min_size_lod2=9)
        txt(s, L, 'OPEN DAILY', place(face, (cx, yy, 4.3)), 0.22, 0.03, 'bold', 'SP_Green', 'SP_Green', spacing=1.3, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Spinneys pylon', (cx, cy - 0.4, 6.0), 0.68, width=2.9)


LAMPS = [(28.0, -20.0, 0, 1), (20.0, -20.0, 0, 1), (-30.0, -4.0, 1, 0), (30.0, -4.0, -1, 0), (-30.0, 12.0, 1, 0), (30.0, 12.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.3, 0.0, BX1, BY1, H + 0.6)
    A.col_box('Portico', POR[0], POR[1], ZP0 - 0.1, POR[2], POR[3], ZP1 + 0.35)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    A.col_box('Pylon', 22.9, -21.3, 0.0, 26.1, -20.4, 8.1)
    for i, (x, y) in enumerate(((-17.5, -12.0), (16.5, -12.0), (-17.5, -4.2))):
        A.col_box(f'TrolleyShelter{i}', x - 1.6, y - 0.6, 0.0, x + 1.6, y + 0.6, 2.05)
    lamp_collision(A, LAMPS, 8.5)


def build_lights(A):
    for i, x in enumerate((-10.0, -4.0, 4.0, 10.0)):
        A.light(f'Portico{i}', 'SPOT', (x, -1.0, ZP0 - 0.1), 1100, '#fff4e4', rot=(180, 0, 0), spot_deg=130, blend=0.8, radius=0.3)
    glow_lights(A, 'Interior', [(-8.0, 8.0, 5.6), (0.0, 8.0, 5.6), (8.0, 8.0, 5.6), (-8.0, 14.0, 5.6), (8.0, 14.0, 5.6)], energy=2000, color='#fff4e4', radius=0.8)
    sign_light(A, 'FasciaGlow', (0.0, -8.0, 6.5), 3500, '#e8fff0')
    sign_light(A, 'PylonGlow', (24.5, -24.0, 6.0), 1800, '#e8fff0')
    lamp_lights(A, LAMPS, 8.4, 1.3, 2400)


def main():
    A = Store('15', '15_spinneys', 'spinneys', 'SPIN', 'Supermarket', 'Spinneys Market')
    A.dims = dict(plot=[64.0, 44.0], building=[BX1 - BX0, BY1 - BY0, H], portico_depth=BY0 - POR[1], pylon_height=8.1)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_pylon(A, L)
        lamp_set(A, L, LAMPS, 8.5, 1.3)
    build_collision(A); build_lights(A)
    A.camera('day', (-30.0, -38.0, 5.0), (0.0, 4.0, 3.6), 32)
    A.camera('road', (-12.0, PLOT[1] - 8.6, 1.25), (0.0, -4.0, 5.0), 30)
    A.camera('detail', (-9.0, -4.3, 1.7), (0.0, 3.0, 4.0), 22)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
