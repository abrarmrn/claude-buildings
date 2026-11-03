"""ASSET 15 - Crescent Galleria (four-storey urban shopping mall).

Massing: 90 m frontage.  A 66 m CONCAVE (crescent) four-storey glass curtain wall with silver floor spandrels and fins
is held between two taller stone 'bookend' towers that carry their own street-facing shopfronts (separate commercial
frontage sections).  A crescent-shaped canopy crowns the glass with the name; a long glass entrance canopy marks the
central doors; a glazed skylight covers the atrium.
Interior (real 3D): four floors (0.15 / 5.6 / 11.0 / 16.4 m), a stadium-shaped central atrium through all levels with
glass-railed galleries, SIX escalators placed in the glazed front zone (zig-zag GF->L1 at the sides, L1->L2 in the
centre, L2->L3 at the sides) so circulation and floor separation read from the road, 56 shop units (14 per floor) with
glass shopfronts, illuminated sign bands and display fixtures, kiosks, benches, hanging LED screens, atrium pool.
Site: entrance plaza on the frontage; OPTIONAL surface car park on the right (separate collection, own crossing).
"""
import os, sys, math, random
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

LODR = {0: (0.0, 140.0), 1: (140.0, 380.0), 2: (380.0, 2000.0)}
A = PAsset('15', '15_crescent_galleria', 'crescent_galleria', 'P15', 'CrescentGalleria', 'Crescent Galleria', 4, lod_ranges=LODR)
defmat('CG_Gold', '#c9a24a', 0.25, 1.0, emit='#ffd690', es=4.0)
defmat('CG_Letter', '#ffffff', 0.3, emit='#fff6e8', es=5.0)
SIGN_MATS = []
for i, c in enumerate(('#ffffff', '#ffd59a', '#ff9fb8', '#8fe8ff', '#b9a6ff', '#ffe066', '#9dffb0')):
    SIGN_MATS.append(defmat(f'CG_Sign{i}', '#202020', 0.3, emit=c, es=4.0))
WALL_MATS = ['PC_WallWhite', 'PC_WallWarm', 'PC_PanelBlack', 'PC_StoneLime', 'PC_WoodSlat', 'PC_PanelPearl']

XA, XB = -45.0, 45.0
XG = 33.0                                    # crescent glass between -XG..XG
Y1 = 55.0
Z = [0.15, 5.6, 11.0, 16.4]
ZR = 21.8
ATC, ATS, ATR = (0.0, 32.0), 12.0, 8.0       # atrium stadium: centre, half straight length, radius
LANE_A, LANE_B = 18.6, 20.6
NAMES = ['MAISON', 'NOVA', 'LUXE', 'ATELIER', 'VELA', 'AZURE', 'SOLE', 'KAIA', 'LUMA', 'ORBIT', 'TERRA', 'MIRA', 'ZEPHYR', 'ONYX',
         'AURUM', 'SELIN', 'NOOR', 'RAYA', 'IVORY', 'COSTA', 'LYRA', 'OASIS', 'DUNE', 'PALMA', 'CORAL', 'AMBER', 'JADE', 'SAGE']


def yf(x):
    t = max(-1.0, min(1.0, x / XG))
    return 10.0 + 6.0 * (1 - t * t)


def front_pts(n):
    return [(-XG + 2 * XG * i / n, yf(-XG + 2 * XG * i / n)) for i in range(n + 1)]


def stadium(L, grow=0.0):
    n = {0: 14, 1: 8, 2: 4}[L]
    cx, cy = ATC
    r = ATR + grow
    pts = []
    for i in range(n + 1):
        a = -90 + 180 * i / n
        pts.append((cx + ATS + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    for i in range(n + 1):
        a = 90 + 180 * i / n
        pts.append((cx - ATS + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    return pts


def esc_len(h):
    return 4.4 + h / math.tan(math.radians(30))


def wells(level):
    """Escalator wells (rect holes) cut in the slab of floor `level` (1..3)."""
    H = 5.45
    Lt = esc_len(H)
    if level in (1, 3):
        return [(-21.0, LANE_A - 0.8, -21.0 + Lt - 2.2, LANE_A + 0.8), (21.0 - Lt + 2.2, LANE_A - 0.8, 21.0, LANE_A + 0.8)]
    return [(-6.9, LANE_A - 0.8, -6.9 + Lt - 2.2, LANE_A + 0.8), (6.9 - Lt + 2.2, LANE_B - 0.8, 6.9, LANE_B + 0.8)]


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Bookends')
    det = A.m(L, 'FACADE_DETAILS', 'Crescent')
    nfront = {0: 24, 1: 16, 2: 8}[L]
    fp = front_pts(nfront)
    outline = fp + [(XG, Y1), (-XG, Y1)]
    # ---- floor slabs (GF solid, L1-L3 with atrium + escalator wells), roof with skylight opening
    A.m(L, 'BUILDING_INTERIOR', 'Slabs').add(bm_prism(outline, -0.4, Z[0]), 'PC_FloorMarble',
                                             mat_fn=mat_by_normal('PC_FloorMarble', 'PC_Concrete', 'PC_AluSilver'))
    for k in (1, 2, 3):
        holes = [stadium(L)] + [AR.poly_rect(*w) for w in wells(k)]
        AR.slab(A, L, outline, Z[k], 0.5, holes, 'PC_FloorMarble' if k % 2 else 'PC_FloorTerrazzo', 'PC_Ceiling', 'PC_AluSilver')
    AR.slab(A, L, outline, ZR, 0.5, [stadium(L, -0.5)], 'PC_RoofGravel', 'PC_Ceiling', 'PC_AluSilver', comp='BUILDING_EXTERIOR', sub='Roof')
    # skylight (glass + frame ribs) over the atrium
    sk = stadium(L, 0.2)
    A.m(L, 'GLASS_SYSTEM', 'Skylight').add(bm_poly_flat(sk, ZR + 0.9), 'PC_GlassClear')
    if L < 2:
        for x in range(-18, 19, 3):
            A.m(L, 'GLASS_SYSTEM', 'SkylightFrame').add(bm_box(x - 0.06, ATC[1] - ATR, ZR + 0.5, x + 0.06, ATC[1] + ATR, ZR + 0.9), 'PC_AluSilver')
        for (p0, p1) in zip(sk, sk[1:] + sk[:1]):
            M, Ls = seg_frame(p0, p1)
            A.m(L, 'GLASS_SYSTEM', 'SkylightFrame').add(bm_box(0, -0.1, ZR - 0.05, Ls, 0.1, ZR + 0.95), 'PC_AluSilver', matrix=M)
    # ---- crescent curtain wall with silver floor spandrels + fins
    span = [(Z[k] - 0.55, Z[k] + 0.05, 'PC_AluSilver') for k in (1, 2, 3)] + [(ZR - 0.55, ZR, 'PC_AluSilver')]
    mid = nfront // 2
    AR.curtain(A, L, fp, 0.0, ZR, 2.2, [3.6], 0.06, 0.2, 'PC_AluSilver', 'PC_Glass', sub='Crescent',
               spandrels=span, fins=dict(depth=0.45, t=0.08, every=3, mat='PC_AluSilver', z0=Z[1], z1=ZR) if L == 0 else None,
               doors=[dict(seg=mid - 1, u0=0.2, u1=2.6, h=3.4, kind='slide'), dict(seg=mid, u0=0.15, u1=2.55, h=3.4, kind='slide')])
    # entrance canopy (glass on steel)
    ec = (-7.0, yf(0) - 6.5, 7.0, yf(0) + 0.1)
    det.add(bm_box(ec[0], ec[1], 6.0, ec[2], ec[3], 6.12), 'PC_GlassClear')
    for x in (ec[0], -3.5, 0.0, 3.5, ec[2]):
        det.add(bm_box(x - 0.08, ec[1], 5.86, x + 0.08, ec[3], 6.0), 'PC_AluSilver')
        if L < 2:
            det.add(bm_cyl_between((x, ec[1] + 0.1, 6.06), (x, ec[3] - 0.2, 9.5), 0.03, 6), 'PC_Stainless')
    det.add(bm_box(ec[0], ec[1], 5.7, ec[2], ec[1] + 0.25, 6.12), 'PC_AluSilver')
    # crescent crown canopy following the arc
    nc = {0: 30, 1: 16, 2: 8}[L]
    crown = [(-XG - 3.0 + (2 * XG + 6.0) * i / nc) for i in range(nc + 1)]
    outer = [(x, yf(x) - 4.0) for x in crown]
    inner = [(x, yf(x) + 5.0) for x in reversed(crown)]
    det.add(bm_prism(outer + inner, ZR + 1.3, ZR + 2.1), 'PC_PanelWhite', mat_fn=mat_by_normal('PC_PanelWhite', 'PC_PanelWhite', 'PC_AluSilver'))
    for x in (-24.0, -12.0, 12.0, 24.0):
        AR.column(det, L, x, yf(x) + 1.5, ZR, ZR + 1.3, 0.18, 'PC_AluSilver')
    if L < 2:
        for (a, b) in zip(outer[:-1], outer[1:]):
            det.add(AR.quad_world((a[0], a[1] - 0.01, ZR + 1.25), (b[0], b[1] - 0.01, ZR + 1.25), (b[0], b[1] - 0.01, ZR + 1.35),
                                  (a[0], a[1] - 0.01, ZR + 1.35)), 'PC_LightStrip')
    # ---- bookend towers (stone) with street-facing shopfronts
    for s in (-1, 1):
        xo, xi = s * XB, s * XG
        x0, x1 = min(xo, xi), max(xo, xi)
        bt = 25.5
        AR.wall(ext, (x0, 10.0), (x1, 10.0), 0.0, bt, 0.5, 'PC_StoneLime', 'PC_WallWarm',
                holes=[(1.0, 11.0, 0.0, 4.8)] + [(1.5 + 2.4 * k, 2.3 + 2.4 * k, 6.5, 20.5) for k in range(5)])
        AR.curtain(A, L, [(x0 + 1.0, 10.0 + 0.02), (x0 + 11.0, 10.0 + 0.02)], 0.0, 4.8, 2.5, [], 0.07, 0.18, 'PC_Bronze', 'PC_Glass',
                   sub=f'BookShop{s}', doors=[dict(seg=0, u0=4.0, u1=6.0, h=2.8, kind='pivot')])
        for k in range(5):
            AR.curtain(A, L, [(x0 + 1.5 + 2.4 * k, 10.3), (x0 + 2.3 + 2.4 * k, 10.3)], 6.5, 20.5, 1.0, [], 0.04, 0.1, 'PC_Bronze', 'PC_Glass',
                       sub=f'Slot{s}{k}')
        p_out = ((xo, 10.0), (xo, Y1)) if s > 0 else ((xo, Y1), (xo, 10.0))
        AR.wall(ext, p_out[0], p_out[1], 0.0, bt, 0.5, 'PC_StoneLime', 'PC_WallWarm')
        AR.wall(ext, (x1, Y1), (x0, Y1), 0.0, bt, 0.5, 'PC_StoneLime', 'PC_WallWarm')
        if s < 0:
            AR.wall(ext, (xi, 10.0), (xi, Y1), 0.0, bt, 0.5, 'PC_StoneLime', 'PC_WallWarm')
        else:
            AR.wall(ext, (xi, Y1), (xi, 10.0), 0.0, bt, 0.5, 'PC_StoneLime', 'PC_WallWarm')
        AR.box(ext, x0, 10.0, bt - 0.4, x1, Y1, bt, 'PC_StoneLime', top='PC_RoofGravel')
        AR.box(ext, x0 - 0.2, 9.6, 5.0, x1 + 0.2, 10.1, 5.6, 'PC_Bronze')
        for k in range(4):
            AR.slab_r(A, L, (x0 + 0.5, 10.5, x1 - 0.5, Y1 - 0.5), [], Z[k] if k else 0.15, 0.4, 'PC_FloorOak', 'PC_Ceiling', 'PC_WallWarm',
                      sub='BookendFloors')
    AR.wall(ext, (XG, Y1), (-XG, Y1), 0.0, ZR + 0.6, 0.5, 'PC_PanelSilver', 'PC_WallWhite', holes=[(30.0, 36.0, 0.0, 5.0)])
    # ---- signage: crown letters along the crescent + crescent emblems on the bookends + bookend shop names
    sg = A.m(L, 'SIGNAGE', 'Brand')
    word = 'CRESCENT  GALLERIA'
    w = 1.95
    xs = -len(word) * w * 0.5 + w * 0.5
    for i, ch in enumerate(word):
        x = xs + i * w
        if ch == ' ':
            continue
        y = yf(x) - 4.05
        ang = math.degrees(math.atan2(-12.0 * x / (XG * XG), 1.0))
        Mt = Matrix.Translation((x, y + 0.4, ZR + 2.1 + 0.85)) @ Matrix.Rotation(math.radians(ang), 4, 'Z') @ R.FACING['-Y'].to_4x4()
        txt(sg, L, ch, Mt, 1.7, 0.18, 'dsemi', 'CG_Letter', 'PC_AluSilver')
    for s in (-1, 1):
        M = place('-Y', Vector((s * 39.0, 9.98, 19.5)))
        crescent(sg, L, M, 2.6)
        if L < 2:
            txt(sg, L, 'GALLERIA', M @ Matrix.Translation((0, -3.6, 0)), 0.6, 0.05, 'dsemi', 'CG_Gold', 'PC_Bronze', spacing=1.4)
    txt(sg, L, 'ATRIA CAFE', place('-Y', Vector((-39.0, 9.55, 5.3))), 0.5, 0.05, 'dsemi', 'CG_Letter', 'PC_Bronze', spacing=1.2)
    txt(sg, L, 'MAISON OR', place('-Y', Vector((39.0, 9.55, 5.3))), 0.5, 0.05, 'caladea_b', 'CG_Gold', 'PC_Bronze', spacing=1.2)
    A.sign('crown_name', (0.0, yf(0) - 3.8, ZR + 2.95), 1.7, width=34.0)
    A.sign('bookend_emblem_L', (-39.0, 9.9, 19.5), 5.2, width=5.2)
    interior(L)


def crescent_png():
    p = os.path.join(K.TEXCACHE, 'pc_logo_crescent.png')
    if not os.path.exists(p):
        n = 512
        im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
        d.ellipse([16, 16, n - 16, n - 16], fill=255)
        d.ellipse([150, 0, n + 120, n - 40], fill=0)
        im = im.filter(ImageFilter.GaussianBlur(1.2))
        Image.merge('RGBA', (Image.new('L', (n, n), 255), Image.new('L', (n, n), 214), Image.new('L', (n, n), 150), im)).save(p)
    return p


SPECIAL_MATS['CG_Crescent'] = lambda: mat_logo('CG_Crescent', crescent_png(), 4.0)


def crescent(acc, L, M, r):
    decal(acc, M @ Matrix.Translation((0, 0, 0.02)), 2 * r, 2 * r, 'CG_Crescent')


def shop(L, z, p0, p1, depth, idx):
    rng = random.Random(idx * 7 + 3)
    M, W = seg_frame(p0, p1, z)
    sf = A.m(L, 'GLASS_SYSTEM', 'Shopfronts')
    sw = A.m(L, 'BUILDING_INTERIOR', 'ShopShells')
    sd = A.m(L, 'DISPLAY_OBJECTS', 'ShopDisplays')
    sg = A.m(L, 'SIGNAGE', 'ShopSigns')
    sm = SIGN_MATS[idx % len(SIGN_MATS)]
    wm = WALL_MATS[idx % len(WALL_MATS)]
    H = 4.9
    sw.add(bm_box(0.0, 0.0, 0.0, 0.25, depth, H), 'PC_WallWhite', matrix=M)                 # party wall
    sw.add(bm_box(0.25, depth - 0.25, 0.0, W, depth, H), wm, matrix=M)                     # back wall
    sw.add(bm_box(0.0, -0.3, H - 0.95, W, 0.05, H), 'PC_PanelBlack', matrix=M)              # sign band
    if L == 2:
        sw.add(bm_vquad(0.3, W - 0.3, 0.2, H - 1.0, depth - 0.3, '-Y'), 'PC_LightWarm', matrix=M)
        return
    dw = 2.6
    for (a, b) in ((0.4, W / 2 - dw / 2), (W / 2 + dw / 2, W - 0.2)):
        sf.add(bm_vquad(a, b, 0.0, H - 0.95, 0.0, '-Y'), 'PC_GlassClear', matrix=M)
        sf.add(bm_box(a - 0.04, -0.05, 0.0, a + 0.04, 0.05, H - 0.95), 'PC_AluDark', matrix=M)
        sf.add(bm_box(b - 0.04, -0.05, 0.0, b + 0.04, 0.05, H - 0.95), 'PC_AluDark', matrix=M)
    sw.add(bm_hquad(1.0, 1.0, W - 1.0, depth - 1.0, H - 0.02, down=True), 'PC_LightPanel', matrix=M)
    name = NAMES[idx % len(NAMES)]
    if L == 0:
        txt(sg, L, name, M @ Matrix.Translation((W / 2, -0.31, H - 0.48)) @ R.FACING['-Y'].to_4x4(), 0.45, 0.04,
            rng.choice(['dsemi', 'caladea_b', 'dlight']), sm, sm, spacing=1.2)
    else:
        sg.add(bm_box(W / 2 - 1.5, -0.32, H - 0.65, W / 2 + 1.5, -0.3, H - 0.3), sm, matrix=M)
    kind = idx % 5
    zl = z
    for k in range(3 if L == 0 else 2):
        u = 1.6 + k * (W - 3.2) / 2
        p = M @ Vector((u, depth * 0.45, 0))
        q = M @ Vector((u, depth - 0.6, 0))
        ang = math.degrees(math.atan2(M[1][0], M[0][0]))
        if kind == 0:
            F.clothes_rail(sd, L, p.x, p.y, zl, ang, 1.6, seed=idx + k)
            F.mannequin(sd, L, (M @ Vector((u, 1.2, 0))).x, (M @ Vector((u, 1.2, 0))).y, zl, 0, 'PC_WhiteGloss',
                        rng.choice(['PC_FabricNavy', 'PC_FabricRust', 'PC_FabricCream', 'PC_LeatherBlack']))
        elif kind == 1:
            F.product_table(sd, L, p.x, p.y, zl, ang, 2.2, 0.9, 0.9, 'PC_WhiteGloss', 'PC_WhiteGloss', 'mixed', seed=idx + k)
        elif kind == 2:
            dx = M @ Vector((u - 0.8, depth * 0.45, 0)); dy = M @ Vector((u + 0.8, depth * 0.45 + 0.6, 0))
            F.display_case(sd, L, min(dx.x, dy.x), min(dx.y, dy.y), max(dx.x, dy.x), max(dx.y, dy.y), zl, 1.2, 'PC_BlackGloss', 'PC_GlassClear',
                           'PC_LightWarm', 'CG_Gold')
        elif kind == 3:
            F.sofa(sd, L, p.x, p.y, zl, ang + 180, 2.0, 0.9, rng.choice(['PC_FabricTeal', 'PC_FabricCream', 'PC_FabricGrey']))
        else:
            F.plinth(sd, L, min(p.x, p.x + 0.01) - 0.6, p.y - 0.6, p.x + 0.6, p.y + 0.6, zl, 0.6, 'PC_WhiteGloss', 'PC_AluSilver', None)
    if kind in (0, 4) and L == 0:
        F.wall_shelf(sd, L, q.x, q.y + 0.0, zl, ang, W - 1.2, 2.6, 4, 'PC_WhiteGloss', wm, seed=idx)


def interior(L):
    gal = A.m(L, 'FURNITURE', 'Galleries')
    cl = A.m(L, 'BUILDING_INTERIOR', 'Ceilings')
    # shops: back row + side rows, every floor
    idx = 0
    for k, z in enumerate(Z):
        for i in range(8):
            shop(L, z, (-32.0 + 8 * i, 44.0), (-24.0 + 8 * i, 44.0), 10.5, idx); idx += 1
        for i in range(3):
            y0 = 21.5 + i * 7.5
            shop(L, z, (-22.0, y0), (-22.0, y0 + 7.5), 10.5, idx); idx += 1
            shop(L, z, (22.0, y0 + 7.5), (22.0, y0), 10.5, idx); idx += 1
        # gallery ceilings with linear lights (front zone + corridor ring)
        zc = (Z[k + 1] if k < 3 else ZR) - 0.5
        ring = [(-22.0, 21.0, 22.0, 24.0), (-22.0, 40.0, 22.0, 44.0), (-22.0, 24.0, -20.5, 40.0), (20.5, 24.0, 22.0, 40.0)]
        AR.ceiling_panels(A, L, ring + [(-28.0, 14.0, 28.0, 21.0)], zc, (4.0, 2.0), w=2.5, d=0.15, mat='PC_LightPanel', lod2_glow='PC_LightWarm',
                          sub='GalleryLights')
        # balustrades around the atrium (L1-L3)
        if k >= 1:
            st = stadium(L)
            AR.glass_rail(A, L, st + [st[0]], z, 1.1, sub=f'AtriumRail{k}')
            for w in wells(k):
                AR.glass_rail(A, L, [(w[0], w[1]), (w[2], w[1]), (w[2], w[3]), (w[0], w[3]), (w[0], w[1])], z, 1.1, sub=f'WellRail{k}')
            # LED screens hung on the balustrade + benches
            if L < 2:
                for x in (-8.0, 8.0):
                    F.tv_wall(gal, L, x, 23.75, z + 1.2, 180, 1, 1, 3.2, 1.6, 0.0, 0.0, seed=k * 10 + int(x))
        for x in (-16.0, 0.0, 16.0):
            F.bench(gal, L, x, 42.6, z, 0, 2.4, 'PC_Walnut', 'PC_StoneTop')
        if k == 0:
            for x in (-15.0, 15.0):
                F.kiosk(gal, L, x, 30.0, z, 90, 3.0, 1.4)
            # atrium pool + benches (architectural water, no planting)
            gal.add(bm_cyl(0.0, 32.0, z, z + 0.45, 4.5, {0: 40, 1: 16, 2: 8}[L]), 'PC_StoneTop')
            gal.add(bm_cyl(0.0, 32.0, z + 0.45, z + 0.46, 4.2, {0: 40, 1: 16, 2: 8}[L]), 'PC_Water')
    # escalators: GF->L1 sides, L1->L2 centre (two lanes), L2->L3 sides
    H = 5.45
    Lt = esc_len(H)
    for (zb, zt) in ((Z[0], Z[1]), (Z[2], Z[3])):
        AR.escalator(A, L, -21.0, LANE_A, 0, zb, zt, 1.0, sub=f'EscL{int(zb)}')
        AR.escalator(A, L, 21.0, LANE_A, 180, zb, zt, 1.0, sub=f'EscR{int(zb)}')
    AR.escalator(A, L, -6.9, LANE_A, 0, Z[1], Z[2], 1.0, sub='EscCA')
    AR.escalator(A, L, 6.9, LANE_B, 180, Z[1], Z[2], 1.0, sub='EscCB')
    # atrium features: hanging LED screens + ring chandeliers
    if L < 2:
        for k in (1, 2, 3):
            F.ring_light(gal, L, 0.0, 32.0, Z[k] + 3.6, 5.0 - k * 0.8, 0.12)
        for x in (-6.0, 6.0):
            gal.add(bm_box(x - 3.0, 32.0 - 0.1, 12.5, x + 3.0, 32.0 + 0.1, 16.0), 'PC_DeviceBlack')
            F.screen_quad(gal, Matrix.Translation((x, 31.88, 0)), -2.9, 2.9, 12.6, 15.9, 0.0, 'PC_Screen', 2 if x < 0 else 6)
            gal.add(bm_cyl(x, 32.0, 16.0, ZR - 0.5, 0.02, 4), 'PC_Stainless')
    # bookend ground-floor shops (street frontage): cafe (left) + boutique (right)
    bf = A.m(L, 'FURNITURE', 'BookendShops')
    for x in (-42.0, -39.0, -36.0):
        F.round_set(bf, L, x, 13.5, 0.15, 3, 0.45, 'PC_StoneTop', 'PC_Brass', 'PC_FabricCream')
        F.pendant(bf, L, x, 13.5, 5.2, 1.6, 'globe', 0.2)
    F.counter(bf, L, -43.5, 17.0, -35.0, 17.8, 0.15, 1.05, 'PC_TimberDark', 'PC_StoneTop', 'PC_LightWarm')
    for x in (36.0, 39.0, 42.0):
        F.mannequin(bf, L, x, 12.0, 0.15, 0, 'PC_WhiteGloss', 'PC_FabricRust')
        F.display_case(bf, L, x - 0.8, 14.5, x + 0.8, 15.2, 0.15, 1.2, 'PC_BlackGloss', 'PC_GlassClear', 'PC_LightWarm', 'CG_Gold')
    AR.ceiling_panels(A, L, [(-44.0, 10.6, -34.0, 20.0), (34.0, 10.6, 44.0, 20.0)], 5.2, (2.5, 2.5), w=0.8, d=0.8, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm', sub='BookendLights')


for L in (0, 1, 2):
    build(L)

# ---- site
S.sidewalk(A, -50.0, 80.0, crossings=[(48.0, 56.0)])
pl = [(XA - 4.0, 0.0), (XB + 2.0, 0.0), (XB + 2.0, 10.0), (XG, 10.0)] + [(x, yf(x)) for x in [XG - 2 * XG * i / 24 for i in range(1, 24)]] + \
     [(-XG, 10.0), (XA - 4.0, 10.0)]
A.s('OPTIONAL_FORECOURT', 'EntrancePlaza').add(bm_prism(pl, -0.25, 0.0), 'PC_PaverLight',
                                                mat_fn=mat_by_normal('PC_PaverLight', 'PC_Curb', 'PC_Curb'))
for x in (-20.0, -12.0, 12.0, 20.0):
    F.bench(A.s('OPTIONAL_FORECOURT', 'Furniture'), 0, x, 6.0, 0.0, 0, 3.0, 'PC_Walnut', 'PC_StoneTop')
for x in range(-40, 44, 6):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 0.8, 0.0, 0.9, 0.12, 'PC_AluSilver', 'PC_LightStrip')
S.asphalt(A, 'DRIVEWAY', [(48.0, 0.0, 56.0, 8.0)])
S.asphalt(A, 'OPTIONAL_PARKING', [(47.0, 8.0, 78.0, 56.0)])
for r, (y0, d) in enumerate(((9.0, 1), (26.0, -1), (26.0, 1), (43.0, -1))):
    S.bays(A, 57.0, y0 if d > 0 else y0 + 0.0, 8, 2.6, 5.4, d)
S.arrow(A, 'DRIVEWAY', 52.0, 4.0, 90)

# ---- lights (one per floor zone + atrium; small fixtures emissive)
for k, z in enumerate(Z):
    zc = (Z[k + 1] if k < 3 else ZR) - 1.0
    for i, x in enumerate((-16.0, 0.0, 16.0)):
        A.light('INTERIOR_LIGHTING', f'Floor{k}_{i}', 'POINT', (x, 19.0 if x == 0 else 22.0, zc), 2200, '#fff2e2', radius=1.5)
A.light('INTERIOR_LIGHTING', 'AtriumTop', 'POINT', (0.0, 32.0, ZR - 1.5), 5000, '#fff2e2', radius=2.5)
A.light('EXTERIOR_LIGHTING', 'CanopyDown', 'SPOT', (0.0, yf(0) - 3.0, 5.8), 1500, '#fff1e0', spot_deg=110)
for s in (-1, 1):
    A.light('EXTERIOR_LIGHTING', f'BookendWash{s}', 'SPOT', (s * 39.0, 3.0, 0.2), 2500, '#ffe8c8', rot=(-80, 0, 0), spot_deg=35)
A.col_box('Mall', -XG, 10.0, 0, XG, Y1, ZR + 0.9)
A.col_box('BookendL', XA, 10.0, 0, -XG, Y1, 25.5)
A.col_box('BookendR', XG, 10.0, 0, XB, Y1, 25.5)
A.col_box('Crown', -XG - 3.0, 6.0, ZR + 1.3, XG + 3.0, 21.0, ZR + 2.1)
A.col_box('EntranceCanopy', -7.0, yf(0) - 6.5, 5.7, 7.0, yf(0), 6.12)
A.camera('day', (-78.0, -52.0, 24.0), (0.0, 24.0, 10.0), 26)
A.camera('night', (62.0, -50.0, 10.0), (0.0, 24.0, 11.0), 26)
A.camera('road', (-48.0, -7.6, 1.1), (-4.0, 22.0, 9.0), 22)
A.camera('interior', (17.5, 21.6, Z[2] + 1.7), (-14.0, 40.0, 7.0), 15)
A.checks['probes'] = [dict(name=f'Level{k}_front_gallery', p=[0.0, 22.5, Z[k] + 1.3]) for k in range(4)] + \
                     [dict(name=f'Level{k}_escalator', p=[-14.0 if k != 1 else 0.0, LANE_A, Z[k] + 1.5]) for k in range(3)] + \
                     [dict(name='Atrium_pool', p=[0.0, 28.0, 0.8])]
A.meta['visible_levels'] = 4
S.finish(A, -50.0, 80.0, width=90.0, depth=45.0, height=25.5, footprint=[XA, 10.0, XB, Y1],
         storeys=4, floor_levels=Z, roof=ZR, parking='optional right-side surface car park, 32 bays (OPTIONAL_PARKING)',
         access='pedestrian entrance plaza on the frontage; separate right crossing to the optional car park',
         setback_m=10.0, glass='66 m concave crescent curtain wall PC_Glass alpha 0.16 + skylight', concept=__doc__.strip().split('\n')[2])
