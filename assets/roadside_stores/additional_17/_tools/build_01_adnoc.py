"""ASSET 01 - ADNOC service station (service-station cluster, E11 roadside).

Plot 72 m (X) x 52 m (Y); road side faces -Y; origin = plot centre at finished ground (z = 0).
Distinct from the ENOC prototype: hexagonal wing canopy with angled ends and a blue LED edge, round white
columns, mono-pitch store roof with deep overhang, curtain-wall shop, tall blue price pylon.
Branding (ADNOC, OASIS) is a simplified procedural recreation, not official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-36.0, -26.0, 36.0, 26.0)
CAN_PTS = [(-24.0, -19.0), (16.0, -19.0), (19.5, -10.0), (16.0, -1.0), (-24.0, -1.0), (-27.5, -10.0)]
Z_CAN0, Z_CAN1 = 5.6, 6.35
ISL_X = (-19.0, -4.0, 11.0)
ISL_Y = (-14.0, -6.0)
COLS = [(-24.0, -10.0), (-11.5, -10.0), (3.5, -10.0), (16.0, -10.0)]
BX0, BY0, BX1, BY1 = -14.0, 8.0, 14.0, 20.0
H = 4.5
PYLON = (-21.0, -24.6)
ENTRY = (-34.0, -27.0)
EXIT = (27.0, 34.0)
PAVED = [(-27.5, -19.0, 19.5, 6.5)]
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=2.4) + [(-36.0, -23.0, -35.0, 26.0), (35.0, -23.0, 36.0, 26.0), (-34.0, 24.0, 34.0, 26.0)]

defmat('ADN_Blue', '#0b4a9e', rough=0.32, spec=0.6)
defmat('ADN_BlueLit', '#0b4a9e', rough=0.3, emit='#1a6cff', es=0.45)
defmat('ADN_BlueLED', '#2a78ff', rough=0.3, emit='#3d8bff', es=4.0)
defmat('ADN_DeepBlue', '#0a2f66', rough=0.35)
defmat('ADN_Red', '#d8232a', rough=0.3, emit='#ff2a2a', es=0.6)
defmat('ADN_SignWhite', '#ffffff', rough=0.3, emit='#ffffff', es=3.0)
defmat('ADN_Clad', '#f1f2f3', rough=0.28, metal=0.1)
defmat('ADN_Price', '#ffffff', rough=0.2, tex='adnoc_price', emit_tex=True, es=1.6)


def tex_adnoc_price(d):
    W, Hh = 512, 640
    img = Image.new('RGB', (W, Hh), '#0b3b84')
    dr = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(R.FONT_SEMI, 40); f2 = ImageFont.truetype(R.FONT_BLACK, 78)
    rows = [('SPECIAL 95', '2.89'), ('SUPER 98', '3.00'), ('E-PLUS 91', '2.78'), ('DIESEL', '3.12')]
    for i, (a, b) in enumerate(rows):
        y0 = 18 + i * 152
        dr.rounded_rectangle([14, y0, W - 14, y0 + 138], 14, fill='#08306c', outline='#6fa8ff', width=3)
        dr.text((34, y0 + 30), a, font=f1, fill='#cfe3ff', anchor='lm')
        dr.text((W - 34, y0 + 84), b, font=f2, fill='white', anchor='rm')
    img.save(f'{d}/adnoc_price_albedo.png', optimize=True)


R.EXTRA_TEXTURES['adnoc_price'] = tex_adnoc_price


def adnoc_logo(acc, L, M, r=0.6, depth=0.07):
    """Simplified emblem: white disc, blue inner disc, white A, red underline (NOT the official artwork)."""
    disc(acc, L, M, r, depth, 'ADN_SignWhite', 'RS_PaintWhite')
    disc(acc, L, M @ Matrix.Translation((0, 0, depth)), r * 0.82, depth * 0.6, 'ADN_BlueLit', 'ADN_Blue')
    txt(acc, L, 'A', M @ Matrix.Translation((0, r * 0.06, depth * 1.6)), r * 1.05, depth * 0.6, 'black', 'ADN_SignWhite', min_size_lod2=0.3)
    acc.add(bm_box(-r * 0.5, -r * 0.5, 0, r * 0.5, -r * 0.4, depth * 0.5), 'ADN_Red', matrix=M @ Matrix.Translation((0, 0, depth * 1.6)))


def wordmark(acc, L, M, size, depth=0.07, spacing=1.08):
    txt(acc, L, 'ADNOC', M, size, depth, 'black', 'ADN_SignWhite', 'RS_PaintWhite', spacing=spacing)


# ------------------------------------------------------------------ ground
def build_ground(A, L):
    holes = [(BX0 - 0.1, BY0 - 0.1, BX1 + 0.1, BY1 + 0.1), (PYLON[0] - 1.6, PYLON[1] - 0.8, PYLON[0] + 1.6, PYLON[1] + 0.8)]
    site_ground(A, L, PLOT, holes, PAVED, BEDS)
    g = A.m(L, 'Ground')
    # concrete pad beneath the store entrance + forecourt kerb
    g.add(bm_box(BX0 - 1.0, 5.0, 0.0, BX1 + 1.0, BY0, 0.15, bevel=0.02 if L == 0 else 0, open_bottom=True), 'RS_Concrete')
    land = A.m(L, 'Landscape')
    palms(A, L, [(-34.8, -23.0), (-34.8, 2.0), (-34.8, 22.0), (34.8, -23.0), (34.8, 2.0), (34.8, 22.0), (-18.0, 24.8), (18.0, 24.8)], 90)
    rng = random.Random(4)
    for i in range(34):
        x = -26.0 + i * 1.55
        if EXIT[0] - 1 < x < EXIT[1] + 1 or ENTRY[0] - 1 < x < ENTRY[1] + 1 or abs(x - PYLON[0]) < 2.2:
            continue
        if i % 3 == 0:
            R.grass_clump(land, L, x, -24.7, 0.8, seed=i)
        else:
            R.shrub(land, L, x, -24.8 + rng.uniform(-0.2, 0.2), 0.8, seed=i, mat='RS_Foliage' if i % 2 else 'RS_Foliage2')
    for i in range(22):
        R.shrub(land, L, -33.5 + i * 3.0, 25.0, 0.8, seed=200 + i, mat='RS_Foliage2')
    entry_exit(A, L, PLOT, -30.5, 30.5, y=-20.5, depth=2.4)
    if L < 2:
        mk = A.m(L, 'Markings')
        R.arrow_mark(mk, -30.5, -9.0, 90, 3.6); R.arrow_mark(mk, 30.5, -9.0, -90, 3.6)
        for x in (-30.5, 30.5):
            mk.add(bm_hquad(x - 0.08, -20.0, x + 0.08, 20.0, 0.006), 'RS_LineWhite')
    # parking east of the store
    cars = {0: ('RS_CarWhite', 'suv'), 2: ('RS_CarBlack', 'sedan'), 5: ('RS_CarSilver', 'hatch')}
    parking_row(A, L, 17.0, 8.0, 13.8, 6, 2.6, cars)
    disabled_bay(A, L, 17.0 + 2.6 * 6 + 1.3, 8.0, 13.8)
    # fuelling lanes: cars at pumps
    v = A.m(L, 'Vehicles')
    car(v, L, -16.0, -17.2, 0, 'RS_CarBlue', 'sedan')
    car(v, L, 8.0, -8.9, 180, 'RS_CarGrey', 'suv')
    car(v, L, -1.0, -17.2, 0, 'RS_CarRed', 'hatch')
    if L < 2:
        # air & water station
        pa = A.m(L, 'Props')
        pa.add(bm_box(24.0, 4.0, 0, 24.7, 4.5, 1.4, bevel=0.02 if L == 0 else 0, open_bottom=True), 'ADN_Blue')
        pa.add(bm_box(24.1, 3.95, 0.9, 24.6, 4.0, 1.25), 'RS_ScreenDark')


# ------------------------------------------------------------------ canopy
def build_canopy(A, L):
    c = A.m(L, 'Canopy')
    bv = 0.03 if L == 0 else 0.0
    n = len(CAN_PTS)
    # top slab (deep-blue soffit edge) and white fascia ring
    cx = sum(p[0] for p in CAN_PTS) / n; cy = sum(p[1] for p in CAN_PTS) / n
    inner = [(cx + (x - cx) * 0.97, cy + (y - cy) * 0.97) for x, y in CAN_PTS]
    slab = [(cx + (x - cx) * 0.965, cy + (y - cy) * 0.965) for x, y in CAN_PTS]
    c.add(bm_prism(slab, Z_CAN0, Z_CAN1 - 0.12), 'ADN_Clad')            # soffit + slab, inset inside the fascia ring
    # fascia: back-lit blue ring around the canopy edge (emissive, so it reads blue even in shade)
    c.add(bm_ring_prism(CAN_PTS, inner, Z_CAN0 - 0.05, Z_CAN1 + 0.35, top=True, bottom=True), 'ADN_BlueLit')
    c.add(bm_prism(slab, Z_CAN1 - 0.12, Z_CAN1 + 0.0), 'RS_PaintWhite')
    if L < 2:
        # LED edge strip around the soffit (emissive blue) and bright white underside
        edge = [(cx + (x - cx) * 0.995, cy + (y - cy) * 0.995) for x, y in CAN_PTS]
        e2 = [(cx + (x - cx) * 0.985, cy + (y - cy) * 0.985) for x, y in CAN_PTS]
        c.add(bm_ring_prism(edge, e2, Z_CAN0 - 0.09, Z_CAN0 - 0.05, top=True, bottom=True), 'ADN_BlueLED')
    # columns: white round with blue base band and a deep-blue cap
    seg = {0: 24, 1: 12, 2: 8}[L]
    for (x, y) in COLS:
        c.add(bm_cyl(x, y, 0.0, Z_CAN0, 0.42, seg, open_bottom=True), 'ADN_Clad')
        c.add(bm_cyl(x, y, 0.0, 1.0, 0.45, seg, open_bottom=True), 'ADN_Blue')
        if L < 2:
            c.add(bm_cyl(x, y, 0.95, 1.05, 0.47, seg), 'RS_MetalBrushed')
            c.add(bm_cyl(x, y, Z_CAN0 - 0.5, Z_CAN0, 0.46, seg, r2=0.7), 'ADN_Clad')
    # under-canopy light panels
    if L < 2:
        cl = A.m(L, 'CanopyLights')
        for i in range(11):
            x = -23.0 + i * 3.7
            for y in (-16.0, -10.0, -4.0):
                cl.add(bm_box(x - 0.6, y - 0.25, Z_CAN0 - 0.04, x + 0.6, y + 0.25, Z_CAN0 - 0.01), 'RS_LightPanel')
    # fascia branding on the long front (-Y) and the two angled ends
    s = A.m(L, 'Signage')
    yf = CAN_PTS[0][1]
    zc = Z_CAN0 + 0.4
    for x in (-12.0, 4.0):
        M = place('-Y', (x, yf - 0.02, zc))
        wordmark(s, L, M @ Matrix.Translation((0.9, 0, 0)), 1.0, 0.07)
        adnoc_logo(s, L, M @ Matrix.Translation((-2.7, 0, 0)), 0.58, 0.06)
    if L == 0:
        register_sign(A, 'ADNOC canopy fascia wordmark', (4.0 + 0.9, yf - 0.1, zc), 0.72, width=3.3)
    for sgn, a in ((1, 0), (-1, 3)):
        p0, p1 = (CAN_PTS[1], CAN_PTS[2]) if sgn > 0 else (CAN_PTS[5], CAN_PTS[0])
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        s_ = A.m(L, 'Signage')
        # face outward: local +Z of the sign frame must point away from the canopy centre
        n_out = Vector((p1[1] - p0[1], -(p1[0] - p0[0]), 0)).normalized()
        if (Vector((mx - cx, my - cy, 0)).dot(n_out)) < 0:
            n_out = -n_out
        # build matrix with local X along edge, local Z = outward normal
        xdir = Vector((p1[0] - p0[0], p1[1] - p0[1], 0)).normalized()
        if xdir.dot(Vector((n_out.y, -n_out.x, 0))) < 0:
            xdir = -xdir
        zdir = n_out; ydir = Vector((0, 0, 1))
        M = Matrix.Translation(Vector((mx, my, zc)) + n_out * 0.02) @ Matrix(((xdir.x, ydir.x, zdir.x), (xdir.y, ydir.y, zdir.y), (xdir.z, ydir.z, zdir.z))).to_4x4()
        wordmark(s_, L, M, 0.5, 0.05)


# ------------------------------------------------------------------ pump islands
def dispenser(acc, L, cx, cy):
    z0 = 0.2
    if L == 2:
        acc.add(bm_box(cx - 0.55, cy - 0.3, z0, cx + 0.55, cy + 0.3, 2.0, open_bottom=True), 'ADN_Clad')
        acc.add(bm_box(cx - 0.58, cy - 0.32, 2.0, cx + 0.58, cy + 0.32, 2.5), 'ADN_Blue')
        return
    bv = 0.03 if L == 0 else 0.0
    acc.add(bm_box(cx - 0.6, cy - 0.32, z0, cx + 0.6, cy + 0.32, z0 + 0.25, bevel=bv, open_bottom=True), 'RS_MetalBrushed')
    acc.add(bm_prism(rounded_rect(cx - 0.55, cy - 0.28, cx + 0.55, cy + 0.28, 0.06 if L == 0 else 0.0, 3 if L == 0 else 1), z0 + 0.25, 2.0, bottom=False), 'ADN_Clad')
    acc.add(bm_box(cx - 0.58, cy - 0.31, 2.0, cx + 0.58, cy + 0.31, 2.28, bevel=bv, open_bottom=True), 'ADN_Blue')
    acc.add(bm_box(cx - 0.6, cy - 0.33, 2.28, cx + 0.6, cy + 0.33, 2.38, open_bottom=True, open_top=True), 'ADN_Red')
    acc.add(bm_box(cx - 0.58, cy - 0.31, 2.38, cx + 0.58, cy + 0.31, 2.5, bevel=bv * 0.5, open_bottom=True), 'RS_PaintWhite')
    for sgn in (-1, 1):
        fy = cy + sgn * 0.28
        facing = '-Y' if sgn < 0 else '+Y'
        M = place(facing, (cx, fy, 1.62))
        acc.add(bm_box(-0.36, -0.2, 0.0, 0.36, 0.2, 0.02), 'RS_ScreenDark', matrix=M, mat_fn=front_back('RS_ScreenDark', 'RS_PlasticBlack'))
        if L == 0:
            txt(acc, L, 'ADNOC', place(facing, (cx, cy + sgn * 0.315, 2.14)), 0.17, 0.01, 'black', 'ADN_SignWhite')
            acc.add(bm_box(-0.12, -0.12, 0.0, 0.12, 0.12, 0.04, bevel=0.01), 'RS_PlasticBlack', matrix=place(facing, (cx + 0.28, fy, 1.22)))
        for nx, hm in ((-0.32, 'ADN_Blue'), (-0.04, 'ADN_Red'), (0.24, 'RS_PlasticBlack')):
            Mn = place(facing, (cx + nx * (-sgn), fy, 1.08))
            acc.add(bm_box(-0.07, -0.1, 0.0, 0.07, 0.1, 0.08, bevel=bv * 0.3), 'RS_PlasticBlack', matrix=Mn)
            acc.add(bm_box(-0.035, -0.12, 0.06, 0.035, 0.08, 0.14, bevel=bv * 0.3), hm, matrix=Mn)
            if L == 0:
                pts = [(0.0, 0.8 * (1 - t) - 0.35 * math.sin(math.pi * t), 0.05 + 0.45 * math.sin(math.pi * t)) for t in [i / 8 for i in range(9)]]
                for i in range(8):
                    acc.add(bm_cyl_between(pts[i], pts[i + 1], 0.018, 6, caps=False), 'RS_Rubber', matrix=Mn)


def build_islands(A, L):
    isl = A.m(L, 'PumpIslands')
    for ix in ISL_X:
        for iy in ISL_Y:
            rr = rounded_rect(ix - 5.0, iy - 0.75, ix + 5.0, iy + 0.75, 0.6 if L < 2 else 0.0, 4 if L == 0 else 2)
            isl.add(bm_prism(rr, 0.0, 0.2, bottom=False), 'RS_Concrete')
            if L == 0:
                isl.add(bm_ring_prism(rr, rounded_rect(ix - 4.9, iy - 0.65, ix + 4.9, iy + 0.65, 0.5, 4), 0.2, 0.23, bottom=False), 'RS_MetalBrushed')
            for dx in (-2.2, 2.2):
                dispenser(isl, L, ix + dx, iy)
            if L < 2:
                for ex in (-4.6, 4.6):
                    for oy in (-0.4, 0.4):
                        isl.add(bm_cyl(ix + ex, iy + oy, 0.2, 1.0, 0.06, 12 if L == 0 else 6, open_bottom=True), 'RS_ReflectorYellow')
                    isl.add(bm_cyl_between((ix + ex, iy - 0.4, 1.0), (ix + ex, iy + 0.4, 1.0), 0.06, 12 if L == 0 else 6), 'RS_ReflectorYellow')


# ------------------------------------------------------------------ store
def build_store(A, L):
    b = A.m(L, 'Store')
    bv = 0.03 if L == 0 else 0.0
    gz1 = 4.0
    holes = [(-11.5, 0.15, 11.5, gz1)]
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'ADN_Clad', t=0.3, holes=holes, roof_mat='ADN_Clad', roof_t=0.35, rooftop=True)
    # blue vertical accent fins at the corners
    for sx in (BX0, BX1 - 1.2):
        b.add(bm_box(sx, BY0 - 0.08, 0.15, sx + 1.2, BY0 + 0.1, H - 0.35, bevel=bv, open_bottom=True), 'ADN_Blue')
    # sloped canopy roof with deep overhang (wedge, profile in YZ)
    prof = [(BY0 - 3.2, 5.05), (BY1 + 0.2, 4.3), (BY1 + 0.2, 4.85), (BY0 - 3.2, 5.6)]
    b.add(bm_prism_local(prof, (BX1 + 1.0) - (BX0 - 1.0)), 'ADN_Clad', matrix=place('+X', (BX0 - 1.0, 0, 0)))
    b.add(bm_box(BX0 - 1.0, BY0 - 3.22, 5.05, BX1 + 1.0, BY0 - 3.1, 5.6, bevel=bv), 'ADN_Blue')
    if L < 2:
        b.add(bm_box(BX0 - 1.0, BY0 - 3.3, 4.98, BX1 + 1.0, BY0 - 3.2, 5.05), 'ADN_BlueLED')
        for x in (-12.0, -4.0, 4.0, 12.0):
            b.add(bm_cyl(x, BY0 - 2.6, 0.15, 5.0, 0.12, 10 if L == 0 else 6, open_bottom=True), 'RS_MetalBrushed')
    s = A.m(L, 'Signage')
    M = place('-Y', (-4.0, BY0 - 3.26, 5.33))
    wordmark(s, L, M, 0.78, 0.06)
    adnoc_logo(s, L, M @ Matrix.Translation((-3.3, 0, 0)), 0.5, 0.05)
    txt(s, L, 'OASIS', place('-Y', (5.8, BY0 - 3.26, 5.33)), 0.5, 0.05, 'xbold_i', 'ADN_SignWhite', 'RS_PaintWhite', spacing=1.1)
    for sx, face in ((BX0 - 0.0, '-X'), (BX1, '+X')):
        wordmark(s, L, place(face, (sx + (-0.02 if face == '-X' else 0.02), BY0 + 4.0, 3.3)), 0.55, 0.05)
    glazing(A, L, -11.5, 11.5, 0.15, gz1, BY0 + 0.1, nx=8, trans=(2.7,), doors=((0.0, 2.4),), frame='RS_MetalBrushed', door_h=2.3)
    # canopy over the glazing: white soffit with light strip
    if L < 2:
        st = A.m(L, 'CanopyLights')
        for x in (-8.0, -3.0, 3.0, 8.0):
            st.add(bm_box(x - 0.9, BY0 - 2.6, 4.97 + 0.0, x + 0.9, BY0 - 2.3, 5.0), 'RS_LightPanel')


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.3, BY0 + 0.3, BX1 - 0.3, BY1 - 0.3
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 3.7, 'RS_TileFloor', 'RS_InteriorWall',
                        lights=light_grid((ix0, iy0, ix1, iy1), 5, 3, (1.8, 0.28)), back_mat='RS_InteriorWall')
    it.add(bm_vquad(ix0, ix1, 2.9, 3.3, iy1 - 0.004), 'ADN_BlueLit')
    # back cooler wall
    it.add(bm_box(ix0 + 0.5, iy1 - 0.95, 0.15, ix1 - 0.5, iy1, 2.5, open_bottom=True), 'RS_PaintCharcoal')
    it.add(bm_vquad(ix0 + 0.6, ix1 - 0.6, 0.4, 2.4, iy1 - 0.955), 'RS_Cooler')
    if L == 0:
        rng = random.Random(21)
        n = 20
        for k in range(n):
            x = ix0 + 0.7 + k * ((ix1 - 0.6) - (ix0 + 0.6)) / n
            for z in (0.55, 1.05, 1.55, 2.0):
                i, j = rng.randrange(8), rng.randrange(8)
                it.add(bm_box(x, iy1 - 0.9, z, x + 1.05, iy1 - 0.6, z + 0.34, open_bottom=True), 'RS_Products', uv='fit', cell=(i / 8, j / 8, (i + 1) / 8, (j + 1) / 8))
    k = 0
    for y in (10.8, 13.8):
        for xa, xb in ((-10.5, -5.5), (-4.0, 1.0), (2.5, 7.5)):
            R.product_shelf(it, L, xa, y - 0.45, xb, y + 0.45, 1.7, 4, seed=300 + k)
            k += 1
    counter(it, L, 7.0, 9.0, 12.0, 10.0, 1.05, 'ADN_Blue', 'RS_PaintWhite')
    it.add(bm_box(7.5, 15.8, 0.15, 12.0, 16.2, 2.4, open_bottom=True), 'RS_PaintCharcoal')
    it.add(bm_vquad(7.6, 11.9, 1.0, 2.3, 15.795), 'RS_Products', uv='fit')


# ------------------------------------------------------------------ pylon
def build_pylon(A, L):
    p = A.m(L, 'Pylon')
    cx, cy = PYLON
    bv = 0.03 if L == 0 else 0.0
    p.add(bm_box(cx - 1.4, cy - 0.7, 0, cx + 1.4, cy + 0.7, 0.5, bevel=bv, open_bottom=True), 'RS_Concrete')
    p.add(bm_box(cx - 1.0, cy - 0.4, 0.5, cx + 1.0, cy + 0.4, 5.0, bevel=bv), 'ADN_Clad')
    p.add(bm_box(cx - 1.0, cy - 0.4, 5.0, cx + 1.0, cy + 0.4, 9.0), 'ADN_Price', uv='fit', mat_fn=lambda f: 'ADN_Price' if abs(f.normal.y) > 0.5 else 'ADN_Blue')
    p.add(bm_box(cx - 1.0, cy - 0.4, 9.0, cx + 1.0, cy + 0.4, 12.4, bevel=bv), 'ADN_BlueLit')
    p.add(bm_box(cx - 1.02, cy - 0.42, 12.4, cx + 1.02, cy + 0.42, 12.6, bevel=bv), 'RS_MetalBrushed')
    p.add(bm_box(cx - 1.02, cy - 0.42, 4.9, cx + 1.02, cy + 0.42, 5.0), 'ADN_Red')
    s = A.m(L, 'Signage')
    for face, yy in (('-Y', cy - 0.4), ('+Y', cy + 0.4)):
        adnoc_logo(s, L, place(face, (cx, yy, 10.8)), 0.72, 0.07)
        wordmark(s, L, place(face, (cx, yy, 9.45)), 0.6, 0.05)
        txt(s, L, 'OASIS', place(face, (cx, yy, 3.2)), 0.42, 0.04, 'xbold_i', 'ADN_Blue', 'ADN_Blue', min_size_lod2=9)
        txt(s, L, '24 HOURS', place(face, (cx, yy, 2.3)), 0.28, 0.03, 'bold', 'ADN_Blue', 'ADN_Blue', min_size_lod2=9)
        if face == '-Y':
            # price board textured quad (uses the box face)
            pass
    if L == 0:
        register_sign(A, 'ADNOC pylon wordmark', (cx, cy - 0.45, 9.45), 0.44, width=2.0)


def build_lamps(A, L):
    lp = A.m(L, 'LampPosts')
    for x in (-8.0, 12.0, 26.0):
        R.lamp_post(lp, L, x, -24.5, 9.0, facing=(0, 1), arm=1.4)
    for x in (-32.0, 32.0):
        for y in (-8.0, 12.0):
            R.lamp_post(lp, L, x, y, 9.0, facing=(-math.copysign(1, x), 0), arm=1.4)
    R.lamp_post(lp, L, 24.0, 22.0, 9.0, facing=(0, -1), arm=1.4)


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Canopy', -27.5, -19.0, Z_CAN0, 19.5, -1.0, Z_CAN1 + 0.35)
    for i, (x, y) in enumerate(COLS):
        A.col_box(f'CanopyColumn{i}', x - 0.45, y - 0.45, 0.0, x + 0.45, y + 0.45, Z_CAN0)
    A.col_box('Store', BX0, BY0, 0.0, BX1, BY1, H)
    A.col_box('StoreRoof', BX0 - 1.0, BY0 - 3.2, 4.9, BX1 + 1.0, BY1, 5.6)
    A.col_box('Pylon', PYLON[0] - 1.1, PYLON[1] - 0.5, 0.0, PYLON[0] + 1.1, PYLON[1] + 0.5, 12.6)
    for i, ix in enumerate(ISL_X):
        for j, iy in enumerate(ISL_Y):
            A.col_box(f'Island{i}{j}', ix - 5.0, iy - 0.75, 0.0, ix + 5.0, iy + 0.75, 0.25)
    for i, (x, y) in enumerate(((-8.0, -24.5), (12.0, -24.5), (26.0, -24.5), (-32.0, -8.0), (-32.0, 12.0), (32.0, -8.0), (32.0, 12.0), (24.0, 22.0))):
        A.col_box(f'LampPost{i}', x - 0.25, y - 0.25, 0.0, x + 0.25, y + 0.25, 9.0)


def build_lights(A):
    for i, (x, y) in enumerate([(x, y) for x in (-20.0, -8.0, 4.0, 12.0) for y in (-14.0, -6.0)]):
        A.light(f'CanopySpot{i}', 'SPOT', (x, y, Z_CAN0 - 0.1), 1300, '#f4f8ff', spot_deg=130, blend=0.8, radius=0.3)
    for i, x in enumerate((-8.0, 0.0, 8.0)):
        A.light(f'Interior{i}', 'POINT', (x, 14.0, 3.3), 900, '#fff3e4', radius=0.5)
        A.light(f'Entrance{i}', 'SPOT', (x, BY0 - 2.6, 4.9), 900, '#fff6ea', spot_deg=110, blend=0.8, radius=0.2)
    A.light('PylonGlow', 'POINT', (PYLON[0], PYLON[1] - 2.0, 8.0), 2400, '#9cc2ff', radius=0.6)
    for i, (x, y, fx, fy) in enumerate(((-8.0, -24.5, 0, 1), (12.0, -24.5, 0, 1), (26.0, -24.5, 0, 1), (-32.0, -8.0, 1, 0), (32.0, -8.0, -1, 0))):
        A.light(f'LampPost{i}', 'SPOT', (x + fx * 1.4, y + fy * 1.4, 8.9), 2600, '#fff2df', spot_deg=125, blend=0.6, radius=0.3)


def main():
    A = Store('01', '01_adnoc', 'adnoc', 'ADNOC', 'ServiceStation', 'ADNOC Service Station')
    A.dims = dict(plot=[PLOT[2] - PLOT[0], PLOT[3] - PLOT[1]], building=[BX1 - BX0, BY1 - BY0, H], canopy_height=Z_CAN1 + 0.35, pylon_height=12.6)
    for L in (0, 1, 2):
        build_ground(A, L); build_canopy(A, L); build_islands(A, L); build_store(A, L)
        build_interior(A, L); build_pylon(A, L); build_lamps(A, L)
    build_collision(A); build_lights(A)
    A.camera('day', (-44.0, -64.0, 5.0), (-4.0, -8.0, 3.4), 30)
    A.camera('road', (31.0, PLOT[1] - 8.6, 1.25), (-6.0, -19.0, 4.8), 32)
    A.camera('detail', (-13.0, -1.6, 1.6), (-3.0, 8.0, 4.0), 24)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
