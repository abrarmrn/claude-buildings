"""BOULEVARD 05 - THE PROMENADE GALLERIA (premium shopping + dining gallery, 3 commercial floors, 34 m frontage).

Massing: two 4 m wide limestone towers (stair / service cores) rise to 18.6 m at both ends with vertical bronze slot
windows and bronze crowns.  Between them: a recessed ground-floor ARCADE (stone columns, 4 m deep) with shopfronts
behind it; two upper retail floors in a bronze curtain wall with slab spandrels and fins; and in the middle a
12 m wide, 15 m high glazed ATRIUM PORTAL set back behind a stone frame, fronted by a bronze-and-glass canopy.
Interior: three real commercial levels around a central atrium - criss-cross escalators (GF->L1 rising inward,
L1->L2 rising outward), glass-balustraded balcony walkways, glass shopfronts with fixtures and display lighting on
every level, seating in the atrium and a glazed skylight.  At night the atrium, escalators and lit shopfronts read
through the portal glass.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

A = new_asset('05', '05_the_promenade_galleria', 'the_promenade_galleria', 'PromenadeGalleria', 'The Promenade Galleria', 3)

X0, X1, Y0, Y1 = -17.0, 17.0, 0.0, 30.0
TW = 4.0                                    # tower width
TX0, TX1 = X0 + TW, X1 - TW                 # -13 .. 13 between the towers
Z = [0.15, 5.6, 10.4, 15.2]                 # GF, L1, L2 floors, roof slab top
PAR = 16.2
TOWER_H = 18.6
ARC = 4.0                                   # arcade depth
PORT = (-6.0, 6.0)                          # atrium portal
PGL = 1.2                                   # portal glass line
VOID1 = (-6.0, 1.6, 6.0, 15.4)              # L1 atrium hole
VOID2 = (-6.0, 1.6, 6.0, 13.0)              # L2 atrium hole
ESC2 = (1.0, 18.4, 3.8, 27.0)               # L2 opening over the L1->L2 escalator
SKY = (-6.0, 1.6, 6.0, 13.0)
WALK = 2.0                                  # balcony walkway width beside the void
SHOPX = 6.0 + WALK                          # atrium-side shopfront line (+/-)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    # ---- slabs
    AR.slab_r(A, L, (X0 + 0.3, 0.0, X1 - 0.3, Y1 - 0.3), [], Z[0], 0.45, 'PC_FloorMarble', 'PC_Concrete', 'BV_StoneDarkBase', sub='GroundSlab')
    AR.slab_r(A, L, (TX0, 0.0, TX1, Y1 - 0.3), [VOID1], Z[1], 0.45, 'PC_FloorTerrazzo', 'BV_PlasterWarm', 'BV_Bronze', sub='L1Slab')
    AR.slab_r(A, L, (TX0, 0.0, TX1, Y1 - 0.3), [VOID2, ESC2], Z[2], 0.45, 'PC_FloorTerrazzo', 'BV_PlasterWarm', 'BV_Bronze', sub='L2Slab')
    AR.slab_r(A, L, (X0, 0.0, X1, Y1), [SKY], Z[3], 0.6, 'PC_RoofMembrane', 'BV_PlasterWarm', 'BV_Limestone', comp='BUILDING_EXTERIOR', sub='Roof')
    # skylight over the atrium (glass + bronze grid)
    sk = A.m(L, 'GLASS_SYSTEM', 'Skylight')
    sk.add(bm_hquad(SKY[0], SKY[1], SKY[2], SKY[3], Z[3] + 0.6), 'BV_Glass')
    if L < 2:
        for x in np.arange(SKY[0], SKY[2] + 0.01, 2.0):
            sk.add(bm_box(x - 0.05, SKY[1], Z[3] + 0.45, x + 0.05, SKY[3], Z[3] + 0.6), 'BV_BronzeDark')
        for y in np.arange(SKY[1], SKY[3] + 0.01, 2.85):
            sk.add(bm_box(SKY[0], y - 0.05, Z[3] + 0.45, SKY[2], y + 0.05, Z[3] + 0.6), 'BV_BronzeDark')
    # ---- limestone towers with slot windows + crowns
    for (a, b) in ((X0, TX0), (TX1, X1)):
        ext.add(bm_box(a, 0.0, 0.0, b, 1.4, 0.8), 'BV_StoneDarkBase')
        stone_box(ext, L, a, 0.0, 0.8, b, 1.4, TOWER_H - 0.8, 'BV_Limestone', reveal_every=0.9)
        AR.wall(ext, (a, Y1), (a, 1.4), 0.0, TOWER_H - 0.8, 0.3, 'BV_Interface', 'BV_PlasterWarm') if a == X0 else \
            AR.wall(ext, (b, 1.4), (b, Y1), 0.0, TOWER_H - 0.8, 0.3, 'BV_Interface', 'BV_PlasterWarm')
        cx = (a + b) / 2
        for dx in (-0.85, 0.85):
            sl = A.m(L, 'GLASS_SYSTEM', 'TowerSlots')
            sl.add(bm_box(cx + dx - 0.32, -0.06, 6.0, cx + dx + 0.32, -0.02, 16.8), 'BV_BronzeDark')
            sl.add(bm_box(cx + dx - 0.24, -0.08, 6.1, cx + dx + 0.24, -0.06, 16.7), 'BV_GlassWarm')
            if L == 0:
                for z in np.arange(6.6, 16.7, 1.2):
                    sl.add(bm_box(cx + dx - 0.24, -0.1, z, cx + dx + 0.24, -0.06, z + 0.04), 'BV_Bronze')
        det.add(bm_box(a - 0.1, -0.15, TOWER_H - 0.8, b + 0.1, 1.5, TOWER_H - 0.1), 'BV_Bronze')
        det.add(bm_box(a + 0.2, 0.05, TOWER_H - 0.1, b - 0.2, 1.3, TOWER_H), 'BV_BronzeDark')
        if L < 2:
            for x in np.arange(a + 0.3, b - 0.2, 0.3):
                det.add(bm_box(x - 0.02, -0.2, TOWER_H - 0.75, x + 0.02, -0.15, TOWER_H - 0.15), 'BV_BronzeDark')
    # ---- arcade: stone columns on the frontage line carrying the L1 floor, shopfronts set back 4 m
    cols = [x for x in np.arange(TX0 + 1.6, PORT[0] - 0.5, 3.4)] + [x for x in np.arange(PORT[1] + 1.4, TX1 - 0.5, 3.4)]
    for x in cols:
        pier(ext, L, x, 0.75, 0.0, 0.75, 0.0, Z[1] - 0.45, 'BV_Limestone', 0.6, cap=True)
    ext.add(bm_box(TX0, 0.0, Z[1] - 0.45, TX1, 0.8, Z[1] + 0.25), 'BV_Limestone')                  # arcade lintel / L1 edge
    det.add(bm_box(TX0, -0.06, Z[1] + 0.25, TX1, 0.8, Z[1] + 0.35), 'BV_Bronze')
    arc = A.m(L, 'FACADE_DETAILS', 'ArcadeCeiling')
    for (a, b) in ((TX0, PORT[0] - 0.6), (PORT[1] + 0.6, TX1)):
        arc.add(bm_hquad(a, 0.0, b, ARC, Z[1] - 0.46, down=True), 'BV_PlasterWarm')
        if L < 2:
            AR.downlights(arc, L, [(x, ARC / 2) for x in np.arange(a + 1.6, b, 3.4)], Z[1] - 0.47, 0.09, 'PC_LightWarm')
        AR.curtain(A, L, [(a, ARC), (b, ARC)], 0.0, Z[1] - 0.46, (b - a) / 4, [3.6], 0.06, 0.16, 'BV_BronzeDark', 'BV_Glass',
                   sub=f'ArcadeShops{int(a)}', doors=[dict(seg=0, u0=1.0, u1=2.6, h=3.0, kind='pivot', leaves=2),
                                                     dict(seg=0, u0=(b - a) - 2.6, u1=(b - a) - 1.0, h=3.0, kind='pivot', leaves=2)])
    # ---- upper floors curtain wall (L1 + L2) either side of the portal
    for (a, b) in ((TX0, PORT[0] - 0.6), (PORT[1] + 0.6, TX1)):
        AR.curtain(A, L, [(a, 0.4), (b, 0.4)], Z[1] + 0.35, Z[3] - 0.1, (b - a) / 4, [Z[1] + 3.2, Z[2] + 3.0], 0.06, 0.2, 'BV_BronzeDark',
                   'BV_Glass', sub=f'Upper{int(a)}', spandrels=[(Z[2] - 0.55, Z[2] + 0.15, 'BV_Bronze')],
                   fins=dict(depth=0.5, t=0.06, every=1, mat='BV_Bronze', z0=Z[1] + 0.35, z1=Z[3] - 0.1))
    # ---- atrium portal: stone frame + set-back full-height glazing + glass canopy
    for (a, b) in ((PORT[0] - 0.6, PORT[0]), (PORT[1], PORT[1] + 0.6)):
        pier(ext, L, (a + b) / 2, 0.6, 0.0, PGL + 0.1, 0.0, Z[3] + 0.2, 'BV_Limestone', 0.8, cap=False, flute=True)
    ext.add(bm_box(PORT[0] - 0.6, 0.0, Z[3] + 0.2, PORT[1] + 0.6, PGL + 0.1, PAR), 'BV_Limestone')
    w = PORT[1] - PORT[0]
    AR.curtain(A, L, [(PORT[0], PGL), (PORT[1], PGL)], 0.0, Z[3] + 0.2, w / 6, [3.8, 7.6, 11.4], 0.07, 0.24, 'BV_BronzeDark', 'BV_Glass',
               sub='Portal', doors=[dict(seg=0, u0=w / 2 - 2.0, u1=w / 2, h=3.4, kind='slide', leaves=2),
                                    dict(seg=0, u0=w / 2, u1=w / 2 + 2.0, h=3.4, kind='slide', leaves=2)])
    can = A.m(L, 'FACADE_DETAILS', 'Canopy')
    can.add(bm_box(PORT[0] - 1.0, -5.0, 5.0, PORT[1] + 1.0, PGL, 5.04), 'BV_Glass')
    can.add(bm_box(PORT[0] - 1.0, -5.1, 4.82, PORT[1] + 1.0, -4.9, 5.12), 'BV_Bronze')
    if L < 2:
        for x in np.arange(PORT[0] - 1.0, PORT[1] + 1.01, 1.4):
            can.add(bm_box(x - 0.05, -5.0, 4.86, x + 0.05, PGL, 4.98), 'BV_BronzeDark')
        if L == 0:
            for x in (PORT[0] - 0.5, 0.0, PORT[1] + 0.5):
                can.add(bm_cyl_between((x, -4.9, 5.12), (x, 0.0, 8.2), 0.03, 8), 'BV_BronzeDark')
        AR.downlights(can, L, [(x, -2.5) for x in np.arange(PORT[0], PORT[1] + 0.1, 2.0)], 4.82, 0.08, 'PC_LightWarm')
    # ---- parapet band + signage + rear / interface
    stone_box(ext, L, TX0, 0.0, Z[3] - 0.1, TX1, 0.9, PAR, 'BV_Limestone', reveal_every=0.5)
    det.add(bm_box(TX0, -0.12, PAR, TX1, 0.9, PAR + 0.18), 'BV_Bronze')
    sign_text(A, L, 'THE PROMENADE GALLERIA', 0.0, 0.0, 15.62, 0.62, 'cinzel_sb', 'BV_LetterGold', 'BV_BronzeDark', 0.06, spacing=1.15)
    if L < 2:
        sign_text(A, L, 'SHOPPING · DINING · LIFESTYLE', 0.0, -5.12, 4.97, 0.16, 'cinzel', 'BV_LetterGold', 'BV_BronzeDark', 0.012,
                  spacing=1.3)
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[3], 0.3, 'BV_Interface', 'BV_PlasterWarm', holes=[(15.0, 19.0, 0.0, 3.2)])
    rear_interface(A, L, X0, X1, Y1 - 0.4, PAR + 0.18, 2.4)
    roof_plant(A, L, X0 + 0.5, SKY[3] + 1.0, X1 - 0.5, Y1 - 0.5, Z[3])
    interior(L)


def shop_fitout(L, x0, x1, y0, y1, z, seed, kind):
    """One shop unit: back wall shelving, display case / product tables, mannequins or counters, display lighting."""
    fu = A.m(L, 'FURNITURE', 'Shops')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Merch')
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if L == 2:
        F.plinth(dp, L, cx - 1.2, cy - 0.8, cx + 1.2, cy + 0.8, z, 0.9)
        return
    side = 1 if x0 > 0 else -1
    wall_x = x1 - 0.3 if side > 0 else x0 + 0.3
    F.wall_shelf(dp, L, wall_x, cy, z, -90 * side, min(5.0, y1 - y0 - 1.5), 2.6, 4, 'BV_BronzeDark', 'PC_WoodLight',
                 'boxes' if kind != 'fashion' else 'clothes', seed=seed)
    if kind == 'fashion':
        for k, dy in enumerate((-1.5, 0.0, 1.5)):
            F.mannequin(dp, L, cx - side * 0.8, cy + dy, z, 90 * side, 'PC_WhiteGloss', ['PC_FabricNavy', 'BV_Velvet', 'PC_FabricCream'][k])
        F.clothes_rail(dp, L, cx + side * 0.6, cy, z, 90, 2.4, seed=seed)
    elif kind == 'tech':
        F.product_table(dp, L, cx, cy, z, 90, 2.8, 1.1, 0.9, 'PC_WoodLight', 'PC_WoodLight', 'phones', seed=seed)
    elif kind == 'jewel':
        F.display_case(dp, L, cx - 0.7, cy - 1.6, cx + 0.7, cy - 0.4, z, 1.1, 'BV_BronzeDark', 'PC_GlassClear', 'PC_LightWarm', seed=seed)
        F.display_case(dp, L, cx - 0.7, cy + 0.4, cx + 0.7, cy + 1.6, z, 1.1, 'BV_BronzeDark', 'PC_GlassClear', 'PC_LightWarm', seed=seed + 1)
    else:   # cafe / dining unit
        F.counter(fu, L, wall_x - side * 1.0, y0 + 0.8, wall_x - side * 0.2, y1 - 0.8, z, 1.05, 'PC_TimberDark', 'PC_StoneTop', 'PC_LightWarm')
        for dy in (-1.6, 1.6):
            F.round_set(fu, L, cx - side * 0.8, cy + dy, z, 2, 0.35, 'PC_StoneTop', 'BV_BronzeDark', 'BV_VelvetGreen', a0=0)
    F.linear_pendant(fu, L, cx, cy, z + 3.6, 0, min(3.2, y1 - y0 - 1.0), 'PC_LightStrip', 'BV_BronzeDark')


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Shopfronts')
    fu = A.m(L, 'FURNITURE', 'Atrium')
    kinds = ['fashion', 'tech', 'jewel', 'cafe', 'fashion', 'jewel', 'tech', 'fashion', 'cafe', 'fashion', 'jewel', 'tech']
    ki = 0
    for li, z in enumerate(Z[:3]):
        zc = Z[li + 1] - 0.45                        # ceiling under the next slab
        # shop units either side of the atrium, divided at y = 10 / 20; atrium-facing glass shopfronts at x = +/-SHOPX
        y_front = ARC if li == 0 else 0.6
        for s in (-1, 1):
            xs = s * SHOPX
            xo = s * (TX1 - 0.3)
            for (ya, yb) in ((y_front, 10.0), (10.0, 20.0)):
                gl = A.m(L, 'BUILDING_INTERIOR', 'ShopGlass')
                p0, p1 = ((xs, ya), (xs, yb)) if s > 0 else ((xs, yb), (xs, ya))
                AR.curtain(A, L, [p0, p1], z, zc - 0.6, (yb - ya) / 3, [z + 2.8], 0.05, 0.12, 'BV_BronzeDark', 'BV_Glass',
                           comp='BUILDING_INTERIOR', sub=f'ShopFront{li}{s}{int(ya)}',
                           doors=[dict(seg=0, u0=(yb - ya) / 2 - 0.9, u1=(yb - ya) / 2 + 0.9, h=2.8, kind='open')])
                st.add(bm_box(min(xs, xs + s * 0.1), ya, zc - 0.6, max(xs, xs + s * 0.1), yb, zc), 'BV_BronzeDark')    # fascia
                if L < 2:
                    st.add(bm_box(min(xs, xs + s * 0.1) - s * 0.02, ya + 0.6, zc - 0.48, max(xs, xs + s * 0.1) - s * 0.02, yb - 0.6,
                                  zc - 0.12), 'PC_LightWarm')                                            # lit name band
                shop_fitout(L, min(xs, xo), max(xs, xo), ya, yb, z, 100 + ki, kinds[ki % len(kinds)])
                ki += 1
            # party walls between units and back-of-house wall
            for y in (10.0, 20.0):
                AR.wall(st, (xo, y), (xs, y), z, zc, 0.2, 'BV_PlasterWarm')
            st.add(bm_hquad(min(xs, xo), y_front, max(xs, xo), 20.0, zc, down=True), 'BV_PlasterWarm')
            AR.ceiling_panels(A, L, [(min(xs, xo) + 0.3, y_front + 0.3, max(xs, xo) - 0.3, 19.8)], zc, (2.6, 2.6), 1.2, 0.12,
                              'PC_LightPanel', lod2_glow='PC_LightWarm')
        # back-of-house wall behind the rear concourse
        AR.wall(st, (TX1 - 0.3, 26.0), (TX0 + 0.3, 26.0), z, zc, 0.2, 'BV_PlasterWarm', holes=[(8.0, 16.0, 0.0, 3.0)] if li else [])
        # walkway balustrades around the voids
        if li >= 1:
            v = VOID1 if li == 1 else VOID2
            AR.glass_rail(A, L, [(v[0], v[1]), (v[0], v[3]), (v[2], v[3]), (v[2], v[1])], z, 1.1, sub=f'VoidRail{li}', rail='BV_Bronze',
                          shoe='BV_BronzeDark')
            AR.ceiling_panels(A, L, [(v[2] + 0.2, 0.8, SHOPX - 0.2, 20.0), (-SHOPX + 0.2, 0.8, v[0] - 0.2, 20.0)], zc, (1.8, 3.0), 1.0,
                              0.12, 'PC_LightWarm', sub=f'WalkLights{li}')
        if li == 2:
            AR.glass_rail(A, L, [(ESC2[0], ESC2[3]), (ESC2[0], ESC2[1])], z, 1.1, sub='Esc2RailL', rail='BV_Bronze', shoe='BV_BronzeDark')
            AR.glass_rail(A, L, [(ESC2[2], ESC2[1]), (ESC2[2], ESC2[3])], z, 1.1, sub='Esc2RailR', rail='BV_Bronze', shoe='BV_BronzeDark')
    # escalators: GF -> L1 rising inward (x = -2.4), L1 -> L2 rising outward (x = +2.4)
    AR.escalator(A, L, -2.4, 3.8, 90, Z[0], Z[1], 1.0, 'BV_Bronze', 'PC_SteelDark', sub='EscalatorUp1')
    AR.escalator(A, L, 2.4, 29.0, -90, Z[1], Z[2], 1.0, 'BV_Bronze', 'PC_SteelDark', sub='EscalatorUp2')
    # atrium seating, feature pendants, centre plinth display
    if L < 2:
        for (x, y) in ((3.4, 6.0), (3.4, 10.5)):
            F.lounge_group(fu, L, x, y, Z[0], 90, 'BV_Linen', 'BV_Velvet')
        F.bench(fu, L, -4.6, 18.0, Z[0], 90, 2.4, 'PC_Walnut', 'BV_StoneSmooth')
        F.bench(fu, L, 4.6, 18.0, Z[0], 90, 2.4, 'PC_Walnut', 'BV_StoneSmooth')
        F.plinth(A.m(L, 'DISPLAY_OBJECTS', 'Atrium'), L, -1.0, 17.5, 1.0, 20.5, Z[0], 0.3, 'BV_Cream', 'BV_Bronze')
        for (x, y) in ((0.0, 5.0), (0.0, 9.5)):
            F.ring_light(fu, L, x, y, Z[3] - 2.2, 2.4, 0.08, 'BV_Chandelier')
            fu.add(bm_cyl_between((x, y, Z[3]), (x, y, Z[3] - 2.2), 0.012, 6), 'BV_BronzeDark')
        for y in np.arange(5.0, 13.0, 3.0):
            F.linear_pendant(fu, L, 0.0, y, Z[2] - 1.4, 0, 6.0, 'PC_LightStrip', 'BV_BronzeDark')


for L in (0, 1, 2):
    build(L)

promenade(A, X0 - 1.0, X1 + 1.0, entrances=[(-2.0, 2.0)])
arcp = A.s('PROMENADE_FRONTAGE', 'ArcadePaving')
arcp.add(bm_box(TX0, 0.0, 0.0, TX1, ARC, 0.15), 'BV_Paving', mat_fn=mat_by_normal('BV_Paving', 'BV_Paving', 'BV_StoneDarkBase'), uv='box', tile=4.8)
bollards(A, [-9.0, -7.5, 7.5, 9.0, -15.0, 15.0], -6.3)
for x in (-14.0, 14.0):
    light_post(A, x, -6.4)
for x in (-10.5, 10.5):
    bench(A, x, -4.4, 0.0, 2.6)
for x in (-12.5, 12.5):
    planter(A, x - 0.9, -3.2, x + 0.9, -2.0)

for li, z in enumerate(Z[:3]):
    for i, (x, y) in enumerate(((-10.5, 7.0), (10.5, 7.0), (-10.5, 15.0), (10.5, 15.0))):
        A.light('INTERIOR_LIGHTING', f'Shop{li}{i}', 'POINT', (x, y, z + 3.2), 650, '#fff1dc', radius=0.6)
for i, (x, y, z) in enumerate(((0.0, 5.0, 12.6), (0.0, 9.5, 12.6), (0.0, 7.0, 4.0), (0.0, 18.0, 4.0), (0.0, 14.0, 8.4))):
    A.light('INTERIOR_LIGHTING', f'Atrium{i}', 'POINT', (x, y, z), 1800, '#ffe2bd', radius=1.0)
for i, x in enumerate((-15.0, 15.0)):
    A.light('EXTERIOR_LIGHTING', f'TowerWash{i}', 'SPOT', (x, -1.5, 0.2), 1600, '#ffd9a8', rot=(-84, 0, 0), spot_deg=26)
A.light('EXTERIOR_LIGHTING', 'SignWash', 'SPOT', (0.0, -6.0, 0.3), 2600, '#ffe0b0', rot=(-70, 0, 0), spot_deg=32)
A.light('EXTERIOR_LIGHTING', 'CanopyGlow', 'SPOT', (0.0, -2.5, 4.8), 900, '#ffd7a0', spot_deg=110)

A.col_box('Centre', TX0, 0.0, 0.0, TX1, Y1, PAR + 0.2)
for i, (a, b) in enumerate(((X0, TX0), (TX1, X1))):
    A.col_box(f'Tower{i}', a, 0.0, 0.0, b, Y1, TOWER_H)
A.col_box('Canopy', PORT[0] - 1.0, -5.1, 4.82, PORT[1] + 1.0, 0.0, 5.12)

A.camera('day', (-24.0, -33.0, 9.5), (0.0, 6.0, 8.0), 26)
A.camera('night', (-21.0, -29.0, 4.5), (0.0, 6.0, 8.0), 26)
A.camera('road', (-26.0, -11.5, 1.15), (0.0, 4.0, 6.8), 24)
A.camera('interior', (4.6, 2.4, 1.8), (-2.0, 17.0, 8.2), 15)
A.checks['probes'] = [dict(name='escalator_GF_L1', p=[-2.4, 9.0, 3.0]), dict(name='L1_walkway', p=[7.0, 6.0, 6.8]),
                      dict(name='L2_walkway', p=[-7.0, 6.0, 11.6]), dict(name='L1_shop', p=[10.5, 5.0, 6.8]),
                      dict(name='L2_shop', p=[-10.5, 5.0, 11.6]), dict(name='atrium_GF', p=[0.0, 8.0, 1.4])]
finish(A, X0 - 1.0, X1 + 1.0, width=34.0, depth=30.0, height=TOWER_H, footprint=[X0, 0.0, X1, Y1], storeys=3, floor_levels=Z[:3],
       roof=Z[3], parking='none (promenade frontage)', access='atrium portal + arcade shop doors from the promenade; service via the rear',
       setback_m=0.0, glass='BV_Glass alpha 0.11, bronze curtain walls + skylight', concept=__doc__.strip().split('\n')[2],
       frontage_m=34.0, terrace='none (arcade + promenade furniture)')
