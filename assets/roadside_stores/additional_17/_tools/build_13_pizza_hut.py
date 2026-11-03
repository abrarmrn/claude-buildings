"""ASSET 13 - Pizza Hut (standalone pizza restaurant; E11 roadside).

Plot 48 m x 36 m, road side faces -Y, origin = plot centre at finished ground.
Massing: brick walls under a large red hip roof (the signature 'red roof' silhouette) with deep overhang,
glass front with booths visible, side carry-out pickup entrance with canopy, roof-slope sign, pole sign with
hut-roof board. Branding is a simplified recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-24.0, -18.0, 24.0, 18.0)
BX0, BY0, BX1, BY1 = -9.0, 3.0, 8.0, 15.0
WALL_H = 3.6
ROOF_BOT = (BX0 - 1.4, BY0 - 1.6, BX1 + 1.4, BY1 + 1.2)
ROOF_TOP = (-4.5, 7.5, 3.5, 10.5)
Z_ROOF0, Z_ROOF1 = 3.5, 7.6
GX0, GX1, GZ1 = -8.2, 3.6, 3.4
DOOR_X = -1.8
PICK_Y = (6.5, 8.0)
ENTRY, EXIT = (-23.0, -17.0), (17.0, 23.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.2) + [(-24.0, -16.0, -23.2, 18.0), (23.2, -16.0, 24.0, 18.0), (-23.0, 16.5, 23.0, 18.0)]
PAVED = [(-11.0, -4.0, 8.0, BY0 - 1.6)]

defmat('PH_Red', '#e3262d', rough=0.35, spec=0.6)
defmat('PH_RedLit', '#d9232a', rough=0.35, emit='#ff2a30', es=0.25)
defmat('PH_Roof', '#c8201f', rough=0.45, metal=0.3)
defmat('PH_Dark', '#2b2b2d', rough=0.45, metal=0.3)
defmat('PH_Cream', '#e8dcc4', rough=0.6)
defmat('PH_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('PH_Booth', '#8e1a1e', rough=0.6)
defmat('PH_Menu', '#10100f', rough=0.25, emit='#ffe8b8', es=0.9)
defmat('PH_Oven', '#7a3a24', rough=0.8)


def hip_roof(acc, L, bot, top, z0, z1, mat):
    bx0, by0, bx1, by1 = bot; tx0, ty0, tx1, ty1 = top
    bm = bmesh.new()
    b = [bm.verts.new(p) for p in ((bx0, by0, z0), (bx1, by0, z0), (bx1, by1, z0), (bx0, by1, z0))]
    t = [bm.verts.new(p) for p in ((tx0, ty0, z1), (tx1, ty0, z1), (tx1, ty1, z1), (tx0, ty1, z1))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((b[i], b[j], t[j], t[i]))
    bm.faces.new(t)
    bm.faces.new(list(reversed(b)))
    acc.add(bm, mat)


def pizza_logo(acc, L, M, size=1.0, depth=0.07):
    txt(acc, L, 'Pizza Hut', M, size, depth, 'black_i', 'PH_SignWhite', 'RS_PaintWhite', spacing=1.0, shear=0.06)


def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (-0.5, -17.6, 2.8, -16.0)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    land = A.m(L, 'Landscape')
    palms(A, L, [(22.5, -15.0), (-22.5, 10.0), (22.5, 10.0), (-10.0, 16.8), (10.0, 16.8)], 250)
    rng = random.Random(81)
    for i in range(30):
        x = -17.0 + i * 1.4
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or -1.0 < x < 3.5:
            continue
        (R.grass_clump(land, L, x, -17.0, 0.8, seed=i) if i % 3 == 0 else R.shrub(land, L, x, -17.0 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage'))
    entry_exit(A, L, PLOT, -20.0, 20.0, depth=2.2)
    cars = {0: ('RS_CarRed', 'hatch'), 4: ('RS_CarSilver', 'suv'), 8: ('RS_CarWhite', 'sedan')}
    parking_row(A, L, -13.0, -15.0, -9.5, 10, 2.6, cars)
    disabled_bay(A, L, -13.0 + 2.6 * 10 + 1.3, -15.0, -9.5)
    # carry-out parking on the east side
    mk = A.m(L, 'Markings')
    if L < 2:
        for i in range(4):
            mk.add(bm_hquad(11.2, 4.0 + i * 2.8 - 0.05, 15.6, 4.0 + i * 2.8 + 0.05, 0.006), 'RS_LineYellow')
    car(A.m(L, 'Vehicles'), L, 13.4, 5.4, 0, 'RS_CarBlue', 'sedan')
    fur = A.m(L, 'Furniture')
    for i, (x, y) in enumerate(((-9.0, -1.0), (-5.0, -1.8), (-1.0, -1.0))):
        cafe_set(fur, L, x, y, 4 if i % 2 == 0 else 2, ang=30 * i, table_mat='RS_PaintWhite', chair_mat='RS_MetalDark', seat_mat='PH_Red', umb='PH_Red', umb2='RS_PaintWhite', r=0.34)
    planter(fur, L, -11.0, -5.6, -3.0, -5.0, 0.5, 'RS_Concrete', 'RS_Foliage2', seed=3)
    planter(fur, L, 2.0, -5.6, 8.0, -5.0, 0.5, 'RS_Concrete', 'RS_Foliage', seed=9)
    bin_(fur, L, 6.5, -2.0, 'PH_Dark')


def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.03 if L == 0 else 0.0
    t = 0.35
    shell(b, L, (BX0, BY0, BX1, BY1), WALL_H + 0.1, 'RS_Brick', t=t, holes=[(GX0, 0.15, GX1, GZ1)], front_mat='RS_Brick', roof_mat='PH_Dark', roof_t=0.3, skip=('right', 'roof'), rooftop=False)
    # east wall with the carry-out door opening
    rects = rect_subtract([(BY0 + t, 0.15, BY1 - t, WALL_H - 0.2)], (PICK_Y[0], 0.15, PICK_Y[1], 2.45))
    for (y0, z0, y1, z1) in rects:
        b.add(bm_box(BX1 - t, y0, z0, BX1, y1, z1, open_bottom=z0 <= 0.2), 'RS_Brick')
    b.add(bm_box(BX0, BY0, WALL_H - 0.35, BX1, BY1, WALL_H + 0.1), 'PH_Dark')
    # hip roof (signature) + dark eave band + ridge vent
    hip_roof(b, L, ROOF_BOT, ROOF_TOP, Z_ROOF0, Z_ROOF1, 'PH_Roof')
    outer = [(ROOF_BOT[0], ROOF_BOT[1]), (ROOF_BOT[2], ROOF_BOT[1]), (ROOF_BOT[2], ROOF_BOT[3]), (ROOF_BOT[0], ROOF_BOT[3])]
    inner = [(ROOF_BOT[0] + 0.3, ROOF_BOT[1] + 0.3), (ROOF_BOT[2] - 0.3, ROOF_BOT[1] + 0.3), (ROOF_BOT[2] - 0.3, ROOF_BOT[3] - 0.3), (ROOF_BOT[0] + 0.3, ROOF_BOT[3] - 0.3)]
    b.add(bm_ring_prism(outer, inner, Z_ROOF0 - 0.25, Z_ROOF0 + 0.1, bottom=True), 'PH_Dark')
    if L < 2:
        b.add(bm_box(-2.0, 8.5, Z_ROOF1, 1.0, 9.6, Z_ROOF1 + 0.5, bevel=bv, open_bottom=True), 'PH_Dark')
    # brick piers holding the front overhang
    for x in (-9.2, -4.0, 3.8, 8.9):
        b.add(bm_box(x - 0.25, ROOF_BOT[1] + 0.25, 0.0, x + 0.25, ROOF_BOT[1] + 0.75, Z_ROOF0 - 0.25, bevel=bv, open_bottom=True), 'RS_Brick')
    # carry-out canopy + door
    cp = A.m(L, 'Canopy')
    cp.add(bm_box(BX1, 5.4, 2.9, BX1 + 2.6, 9.1, 3.15, bevel=bv), 'PH_Red')
    for (px, py) in ((BX1 + 2.4, 5.5), (BX1 + 2.4, 9.0)):
        cp.add(bm_cyl(px, py, 0.0, 2.9, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalBrushed')
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    gl.add(bm_quad((BX1 + 0.04, PICK_Y[1], 0.15), (BX1 + 0.04, PICK_Y[0], 0.15), (BX1 + 0.04, PICK_Y[0], 2.45), (BX1 + 0.04, PICK_Y[1], 2.45)), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
    if L < 2:
        for y in (PICK_Y[0] - 0.06, PICK_Y[1], (PICK_Y[0] + PICK_Y[1]) / 2 - 0.03):
            fr.add(bm_box(BX1, y, 0.15, BX1 + 0.1, y + 0.06, 2.45), 'PH_Dark')
        fr.add(bm_box(BX1, PICK_Y[0] - 0.06, 2.45, BX1 + 0.1, PICK_Y[1] + 0.06, 2.53), 'PH_Dark')
    s = A.m(L, 'Signage')
    txt(s, L, 'CARRYOUT', place('+X', (BX1 + 0.04, 7.25, 3.5)), 0.36, 0.04, 'xbold_i', 'PH_SignWhite', 'RS_PaintWhite', min_size_lod2=9)
    txt(s, L, 'PICK UP', place('+X', (BX1 + 0.04, 7.25, 3.05)), 0.25, 0.03, 'bold', 'PH_Red', 'PH_Red', min_size_lod2=9) if L < 2 else None
    # logo laid on the tilted front roof slope
    dy, dz = ROOF_TOP[1] - ROOF_BOT[1], Z_ROOF1 - Z_ROOF0
    ydir = Vector((0, dy, dz)).normalized()
    xdir = Vector((1, 0, 0))
    zdir = xdir.cross(ydir)
    tt = 0.38
    ctr = Vector((-0.5, ROOF_BOT[1] + dy * tt, Z_ROOF0 + dz * tt)) + zdir * 0.03
    Mroof = Matrix.Translation(ctr) @ Matrix(((1, 0, 0), (0, ydir.y, zdir.y), (0, ydir.z, zdir.z))).to_4x4()
    pizza_logo(s, L, Mroof, 1.5, 0.08)
    txt(s, L, 'PIZZA • PASTA • WINGS', Mroof @ Matrix.Translation((0, -0.85, 0)), 0.28, 0.04, 'bold', 'PH_SignWhite', 'RS_PaintWhite', spacing=1.2, min_size_lod2=9)
    if L == 0:
        c = ctr + zdir * 0.12
        register_sign(A, 'Pizza Hut roof-slope logo', tuple(c), 1.1, normal=tuple(zdir), width=6.0)
    glazing(A, L, GX0, GX1, 0.15, GZ1, BY0 + 0.1, nx=8, trans=(2.6,), doors=((DOOR_X, 2.2),), frame='PH_Dark', door_h=2.3)
    if L < 2:
        gl.add(bm_vquad(GX0, GX1, 0.95, 1.1, BY0 + 0.07), 'PH_Red')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.35, BY0 + 0.35, BX1 - 0.35, BY1 - 0.35
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.3, 'RS_TileFloor', 'PH_Cream', lights=light_grid((ix0, iy0, ix1, iy1), 5, 3, (1.0, 0.25), 1.2), back_mat='PH_Cream')
    # red booths along the glazing + checkered tables
    for i in range(4):
        x = -7.0 + i * 2.8
        it.add(bm_box(x - 0.9, 3.5, 0.15, x + 0.9, 4.2, 0.55, bevel=0.03 if L == 0 else 0, open_bottom=True), 'PH_Booth')
        it.add(bm_box(x - 0.9, 3.5, 0.55, x + 0.9, 3.7, 1.35, bevel=0.03 if L == 0 else 0), 'PH_Booth')
        it.add(bm_cyl(x, 5.0, 0.15, 0.78, 0.03, 5), 'RS_MetalDark')
        it.add(bm_cyl(x, 5.0, 0.72, 0.78, 0.5, 16 if L == 0 else 8), 'RS_Checker', uv='box')
        it.add(bm_box(x - 0.9, 5.8, 0.15, x + 0.9, 6.5, 0.55, bevel=0.03 if L == 0 else 0, open_bottom=True), 'PH_Booth')
    for i, (x, y) in enumerate(((-6.0, 9.0), (-3.0, 9.4), (0.0, 9.0))):
        cafe_set(it, L, x, y, 4, ang=45, table_mat='RS_Checker', chair_mat='RS_MetalDark', seat_mat='PH_Booth', r=0.4)
    # service counter + brick pizza oven (dome) with glowing mouth
    counter(it, L, 2.0, 11.5, 7.0, 12.6, 1.05, 'PH_Red', 'RS_PaintWhite')
    it.add(bm_box(ix0, iy1 - 0.8, 0.15, ix1, iy1, 2.4, open_bottom=True), 'PH_Dark')
    it.add(bm_sphere((-5.0, 13.4, 1.5), 1.1, 2 if L == 0 else 1, (1.2, 1.0, 0.9)), 'PH_Oven')
    it.add(bm_box(-5.5, 12.4, 0.15, -4.5, 12.45, 1.2), 'RS_LightWarm')
    for i in range(3):
        x = 3.0 + i * 1.6
        it.add(bm_box(x - 0.6, iy1 - 0.06, 2.4, x + 0.6, iy1 - 0.03, 3.1), 'PH_Menu')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = 1.2, -16.8
    bv = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.4, cy - 0.4, 0.0, cx + 1.4, cy + 0.4, 0.35, bevel=bv, open_bottom=True), 'RS_Concrete')
    t.add(bm_cyl(cx, cy, 0.35, 6.6, 0.22, 12 if L == 0 else 6, open_bottom=True), 'PH_Dark')
    # hut-roof silhouette board
    pts = [(-1.9, 0.0), (1.9, 0.0), (1.5, 1.4), (-1.5, 1.4)]
    t.add(bm_prism_local(pts, 0.4), 'PH_RedLit', matrix=place('-Y', (cx, cy + 0.2, 6.0)), mat_fn=front_back('PH_RedLit', 'PH_Red'))
    t.add(bm_box(cx - 1.9, cy - 0.2, 4.4, cx + 1.9, cy + 0.2, 6.0, bevel=bv), 'PH_RedLit')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.2), ('+Y', cy + 0.2)):
        txt(s, L, 'Pizza Hut', place(face, (cx, yy, 5.2)), 0.75, 0.05, 'black_i', 'PH_SignWhite', 'RS_PaintWhite', shear=0.06, min_size_lod2=9)
        txt(s, L, 'DINE IN • CARRYOUT', place(face, (cx, yy, 4.7)), 0.2, 0.03, 'bold', 'PH_SignWhite', 'RS_PaintWhite', spacing=1.2, min_size_lod2=9)
    if L == 0:
        register_sign(A, 'Pizza Hut pole sign', (cx, cy - 0.26, 5.2), 0.54, width=3.0)


LAMPS = [(12.0, -17.0, 0, 1), (-22.0, 3.0, 1, 0), (22.0, 3.0, -1, 0), (0.0, 16.8, 0, -1)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0, 0.0, BX1, BY1, WALL_H + 0.1)
    A.col_box('Roof', ROOF_BOT[0], ROOF_BOT[1], Z_ROOF0 - 0.25, ROOF_BOT[2], ROOF_BOT[3], Z_ROOF1)
    A.col_box('CarryoutCanopy', BX1, 5.4, 2.9, BX1 + 2.6, 9.1, 3.15)
    A.col_box('Paved', *PAVED[0][:2], 0.0, *PAVED[0][2:], 0.12)
    A.col_box('PoleSign', -0.4, -17.2, 0.0, 2.8, -16.4, 7.4)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-7.0, -3.0, 1.5)):
        A.light(f'Eave{i}', 'SPOT', (x, ROOF_BOT[1] + 0.5, Z_ROOF0 - 0.3), 900, '#fff0dc', rot=(180, 0, 0), spot_deg=125, blend=0.8, radius=0.2)
    glow_lights(A, 'Interior', [(-6.0, 6.0, 3.0), (-1.0, 6.0, 3.0), (-4.0, 10.0, 3.0), (4.0, 10.0, 3.0)], energy=900, color='#ffe0b8')
    sign_light(A, 'RoofLogoGlow', (-0.5, -5.0, 6.0), 2200, '#fff0e8')
    sign_light(A, 'PoleGlow', (1.2, -20.5, 5.2), 1600, '#ffe4e0')
    A.light('Carryout', 'SPOT', (BX1 + 1.3, 7.25, 2.85), 600, '#fff2e0', rot=(180, 0, 0), spot_deg=110, blend=0.8, radius=0.2)
    lamp_lights(A, LAMPS)


def main():
    A = Store('13', '13_pizza_hut', 'pizza_hut', 'PHUT', 'Restaurant', 'Pizza Hut')
    A.dims = dict(plot=[48.0, 36.0], building=[BX1 - BX0, BY1 - BY0, WALL_H], roof_top_height=Z_ROOF1, roof_footprint=[ROOF_BOT[2] - ROOF_BOT[0], ROOF_BOT[3] - ROOF_BOT[1]], pole_sign_height=7.4)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L); build_totem(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-20.0, -28.0, 4.4), (-1.0, 5.0, 3.6), 32)
    A.camera('road', (-14.0, PLOT[1] - 8.6, 1.25), (0.0, -2.0, 4.6), 30)
    A.camera('detail', (3.0, -11.0, 1.7), (-2.0, 3.0, 3.6), 26)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
