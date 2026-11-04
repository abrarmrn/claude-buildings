"""BOULEVARD 04 - GALERIE D'OR (high-end fashion and lifestyle retail gallery, 2 storeys, 26 m frontage).

Massing: a warm beige-stone retail podium organised as FOUR visually distinct boutique storefronts around a central
recessed entrance (5 m high, 3 m deep, champagne-bronze lining) crowned by a two-storey-high bronze bay window:
  1  ATELIER NOOR  - projecting glass vitrine box in a bronze frame + side door
  2  MAISON SABLE  - black-steel shopfront with horizontal bronze bands
  3  VELOUR        - glass behind closely spaced vertical bronze fins
  4  OR & ONYX     - one large framed pane on a dark granite stall riser
Upper floor: tall punched windows in the stone with bronze surrounds and a central bronze bay window over the
entrance; fluted stone attic with "GALERIE D'OR" and a bronze cornice.
Interior: four ground-floor boutiques (mannequins, clothes rails, display cases, ottomans) separated by stone-faced
partitions, a central atrium with a wide stone stair up to an open upper retail gallery (glass balustrade, display
plinths, lounge), linear fashion lighting.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

A = new_asset('04', '04_galerie_dor', 'galerie_dor', 'GalerieDor', "Galerie D'Or", 2)

X0, X1, Y0, Y1 = -13.0, 13.0, 0.0, 22.0
GL = 0.5
Z = [0.15, 5.6, 10.2]
ATTIC = 11.6
ZONES = [(-12.4, -7.4), (-6.8, -2.0), (2.0, 6.8), (7.4, 12.4)]
NAMES = ['ATELIER NOOR', 'MAISON SABLE', 'VELOUR', 'OR & ONYX']
ENT = (-1.4, 1.4)
ATR = (-4.2, 4.0, 4.2, 14.4)                 # atrium void in the L1 slab
SF_H = 4.6                                   # shopfront head height


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    AR.slab_r(A, L, (X0 + 0.3, GL, X1 - 0.3, Y1 - 0.3), [], Z[0], 0.45, 'PC_FloorMarble', 'PC_Concrete', 'BV_StoneDarkBase', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.3, GL + 0.05, X1 - 0.3, Y1 - 0.3), [ATR], Z[1], 0.4, 'PC_FloorMarble', 'BV_PlasterWarm', 'BV_Bronze')
    AR.slab_r(A, L, (X0, 0.0, X1, Y1), [], Z[2], 0.5, 'PC_RoofMembrane', 'BV_PlasterWarm', 'BV_BeigeStone', comp='BUILDING_EXTERIOR', sub='Roof')
    roof_plant(A, L, X0 + 0.5, 1.2, X1 - 0.5, Y1 - 0.5, Z[2])
    # ---- stone frame: piers between the zones, GF lintel, upper wall with punched windows, attic
    piers = [(X0, ZONES[0][0]), (ZONES[0][1], ZONES[1][0]), (ZONES[1][1], ENT[0] - 0.6), (ENT[1] + 0.6, ZONES[2][0]),
             (ZONES[2][1], ZONES[3][0]), (ZONES[3][1], X1)]
    for (a, b) in piers:
        pier(ext, L, (a + b) / 2, b - a, 0.0, 0.7, 0.0, Z[1] - 0.6, 'BV_BeigeStone', 0.6, cap=False)
    stone_box(ext, L, X0, 0.0, SF_H, ENT[0] - 0.6, 0.7, Z[1] - 0.6, 'BV_BeigeStone', reveal_every=0.5)
    stone_box(ext, L, ENT[1] + 0.6, 0.0, SF_H, X1, 0.7, Z[1] - 0.6, 'BV_BeigeStone', reveal_every=0.5)
    det.add(bm_box(X0, -0.1, Z[1] - 0.6, X1, 0.7, Z[1] - 0.4), 'BV_Bronze')                       # string course
    # upper wall with punched windows (holes) - one segment per side of the central bay
    upper_holes = []
    wins = [(-12.0, -10.2), (-9.4, -7.6), (-6.4, -4.6), (4.6, 6.4), (7.6, 9.4), (10.2, 12.0)]
    for (a, b) in wins:
        upper_holes.append((a - X0, b - X0, Z[1] + 0.3, Z[1] + 3.6))
    upper_holes.append((-3.6 - X0, 3.6 - X0, Z[1] - 0.4, Z[2] - 0.2))
    AR.wall(ext, (X0, 0.0), (X1, 0.0), Z[1] - 0.4, ATTIC, 0.5, 'BV_BeigeStone', 'BV_PlasterWarm', 'BV_BeigeStone', holes=upper_holes)
    for i, (a, b) in enumerate(wins):
        AR.curtain(A, L, [(a, 0.32), (b, 0.32)], Z[1] + 0.3, Z[1] + 3.6, (b - a) / 2, [Z[1] + 2.7], 0.05, 0.14, 'BV_BronzeDark',
                   'BV_Glass', sub=f'UpWin{i}')
        if L < 2:
            det.add(bm_box(a - 0.12, -0.08, Z[1] + 0.18, b + 0.12, 0.05, Z[1] + 0.3), 'BV_Bronze')          # sill
            for (u0, u1) in ((a - 0.12, a), (b, b + 0.12)):
                det.add(bm_box(u0, -0.06, Z[1] + 0.3, u1, 0.05, Z[1] + 3.75), 'BV_Bronze')            # surround
            det.add(bm_box(a - 0.12, -0.06, Z[1] + 3.6, b + 0.12, 0.05, Z[1] + 3.75), 'BV_Bronze')
    # central bronze bay window above the entrance (projecting 0.6 m)
    bay = A.m(L, 'FACADE_DETAILS', 'BayWindow')
    bay.add(bm_box(-3.7, -0.6, Z[1] - 0.4, 3.7, 0.0, Z[1] - 0.1), 'BV_Bronze')
    bay.add(bm_box(-3.7, -0.6, Z[2] - 0.5, 3.7, 0.0, Z[2] - 0.2), 'BV_Bronze')
    AR.curtain(A, L, [(-3.6, 0.0), (-3.6, -0.55), (3.6, -0.55), (3.6, 0.0)], Z[1] - 0.1, Z[2] - 0.5, 1.2, [Z[1] + 2.9], 0.06, 0.14,
               'BV_BronzeDark', 'BV_Glass', sub='BayWin')
    # fluted attic + cornice + signage
    if L == 0:
        for x in np.arange(X0 + 0.3, X1, 0.32):
            det.add(bm_box(x - 0.02, -0.03, Z[2] + 0.1, x + 0.02, 0.0, ATTIC - 0.15), 'BV_StoneSmooth')
    det.add(bm_box(X0 - 0.2, -0.3, ATTIC, X1 + 0.2, 0.7, ATTIC + 0.25), 'BV_Bronze')
    sign_text(A, L, "GALERIE D'OR", 0.0, -0.02, 10.85, 0.78, 'cinzel_sb', 'BV_LetterGold', 'BV_BronzeDark', 0.06, spacing=1.2,
              backing=(8.6, 1.15, 'BV_BlackFrame'))
    # ---- central recessed entrance, gold lining
    recessed_portal(A, L, ext, ENT[0], ENT[1], 0.0, 3.0, Z[1] - 0.6, 3.3, 'BV_BeigeStone', 'BV_Champ', 'BV_Glass',
                    sub='Entrance')
    ext.add(bm_box(ENT[0] - 0.6, 0.0, Z[1] - 0.6, ENT[1] + 0.6, 0.7, Z[1] - 0.4), 'BV_BeigeStone')
    # ---- the four boutique storefronts
    for k, (a, b) in enumerate(ZONES):
        storefront(L, k, a, b, ext, det)
    # ---- party / rear walls + interface
    AR.wall(ext, (X0, Y1), (X0, 0.7), 0.0, ATTIC, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, 0.7), (X1, Y1), 0.0, ATTIC, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.3, 'BV_Interface', 'BV_PlasterWarm', holes=[(20.0, 22.4, 0.0, 2.8)])
    rear_interface(A, L, X0, X1, Y1 - 0.4, ATTIC + 0.25, 1.4)
    interior(L)


def storefront(L, k, a, b, ext, det):
    w = b - a
    sub = f'Shop{k}'
    if k == 0:      # projecting glass vitrine + side door
        AR.curtain(A, L, [(a, GL), (a + 1.4, GL)], 0.0, SF_H, 1.4, [3.0], 0.06, 0.16, 'BV_BronzeDark', 'BV_Glass', sub=sub + 'Door',
                   doors=[dict(seg=0, u0=0.1, u1=1.3, h=3.0, kind='pivot', leaves=1)])
        AR.curtain(A, L, [(a + 1.4, GL), (a + 1.4, -0.6), (b, -0.6), (b, GL)], 0.7, SF_H - 0.3, 1.2, [], 0.08, 0.12, 'BV_Bronze',
                   'BV_Glass', sub=sub + 'Vitrine')
        det.add(bm_box(a + 1.3, -0.7, 0.0, b + 0.05, GL, 0.7), 'BV_StoneDarkBase')
        det.add(bm_box(a + 1.3, -0.7, SF_H - 0.3, b + 0.05, GL, SF_H), 'BV_Bronze')
        sz = 0.2
    elif k == 1:    # black-steel shopfront with horizontal bronze bands
        AR.curtain(A, L, [(a, GL), (b, GL)], 0.0, SF_H, w / 3, [1.0, 2.0, 3.4], 0.07, 0.16, 'BV_BlackFrame', 'BV_Glass', sub=sub,
                   doors=[dict(seg=0, u0=w / 3, u1=2 * w / 3, h=3.4, kind='pivot', leaves=2)])
        if L < 2:
            for z in (1.0, 2.0, 3.4):
                det.add(bm_box(a, GL - 0.12, z - 0.04, b, GL - 0.05, z + 0.04), 'BV_Bronze')
        sz = 0.2
    elif k == 2:    # glass behind vertical bronze fins
        AR.curtain(A, L, [(a, GL), (b, GL)], 0.0, SF_H, w / 4, [3.4], 0.04, 0.12, 'BV_BronzeDark', 'BV_Glass', sub=sub,
                   doors=[dict(seg=0, u0=0.2, u1=1.4, h=3.0, kind='pivot', leaves=1)])
        if L < 2:
            step = 0.36 if L == 0 else 0.72
            for x in np.arange(a + 1.7, b - 0.1, step):
                det.add(bm_box(x - 0.025, GL - 0.45, 0.3, x + 0.025, GL - 0.12, SF_H - 0.1), 'BV_Bronze')
        sz = 0.22
    else:           # one large framed pane on a granite stall riser
        det.add(bm_box(a, 0.0, 0.0, b, GL + 0.1, 0.65), 'BV_StoneDarkBase')
        AR.curtain(A, L, [(a + 1.3, GL), (b, GL)], 0.65, SF_H - 0.2, w - 1.3, [], 0.05, 0.14, 'BV_BronzeDark', 'BV_Glass', sub=sub + 'Pane')
        AR.curtain(A, L, [(a, GL), (a + 1.3, GL)], 0.0, SF_H - 0.2, 1.3, [], 0.05, 0.14, 'BV_BronzeDark', 'BV_Glass', sub=sub + 'Door',
                   doors=[dict(seg=0, u0=0.1, u1=1.2, h=3.0, kind='pivot', leaves=1)])
        if L < 2:
            for (x0, z0, x1, z1) in ((a - 0.0, SF_H - 0.2, b, SF_H), (a, 0.65, a + 0.06, SF_H), (b - 0.06, 0.65, b, SF_H)):
                det.add(bm_box(x0, -0.12, z0, x1, GL, z1), 'BV_Bronze')
        sz = 0.2
    # fascia band with the boutique name
    det.add(bm_box(a, -0.05, SF_H, b, GL, SF_H + 0.06), 'BV_BronzeDark')
    sign_text(A, L, NAMES[k], (a + b) / 2, 0.0, SF_H + 0.4, sz, 'cinzel', 'BV_LetterGold', 'BV_BronzeDark', 0.02, spacing=1.25)


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Partitions')
    fu = A.m(L, 'FURNITURE', 'Fixtures')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Fashion')
    # boutique partitions (GF) - stone faced, between zones and the atrium hall
    for x in (-7.1, 7.1):
        AR.wall(st, (x, 17.0), (x, GL + 0.1), Z[0], Z[1] - 0.4, 0.2, 'BV_PlasterWarm')
    hg = A.m(L, 'BUILDING_INTERIOR', 'HallGlass')
    for x in (-2.0, 2.0):          # boutiques open onto the central hall through bronze-framed glass
        hg.add(bm_box(x - 0.01, 3.1, Z[0], x + 0.01, 16.9, Z[1] - 0.4), 'BV_GlassWarm')
        if L < 2:
            for y in np.arange(3.1, 17.0, 2.0):
                st.add(bm_box(x - 0.04, y - 0.03, Z[0], x + 0.04, y + 0.03, Z[1] - 0.4), 'BV_BronzeDark')
            st.add(bm_box(x - 0.05, 3.1, Z[0], x + 0.05, 16.9, Z[0] + 0.12), 'BV_BronzeDark')
    AR.wall(st, (X1 - 0.3, 17.0), (X0 + 0.3, 17.0), Z[0], Z[1] - 0.4, 0.2, 'BV_PlasterWarm', holes=[(10.5, 15.5, 0.0, 3.5)])
    AR.ceiling_panels(A, L, rect_subtract([(X0 + 0.4, GL + 0.3, X1 - 0.4, 16.8)], (-2.0, GL, 2.0, 16.8)), Z[1] - 0.4, (2.4, 2.2), 1.4, 0.12,
                      'PC_LightPanel', lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, rect_subtract([(X0 + 0.4, GL + 0.3, X1 - 0.4, Y1 - 0.5)], ATR), Z[2] - 0.5, (2.6, 2.4), 1.4, 0.12,
                      'PC_LightPanel', lod2_glow='PC_LightWarm')
    cloths = ['PC_FabricNavy', 'BV_Velvet', 'PC_FabricCream', 'BV_VelvetGreen', 'PC_LeatherBlack', 'PC_FabricRust']
    zones_in = [(-12.6, -7.3), (-6.9, -2.2), (2.2, 6.9), (7.3, 12.6)]
    for k, (a, b) in enumerate(zones_in):
        cx = (a + b) / 2
        if L < 2:
            for i, (dx, dy) in enumerate(((-1.4, 2.4), (0.2, 2.0), (1.6, 2.6))):
                F.mannequin(dp, L, cx + dx, dy, Z[0] + (0.25 if k == 0 else 0.0), 180, 'PC_WhiteGloss', cloths[(i + k) % 6])
            F.clothes_rail(dp, L, a + 0.7, 9.0, Z[0], 90, 3.0, seed=40 + k)
            F.clothes_rail(dp, L, b - 0.7, 9.0, Z[0], 90, 3.0, seed=50 + k)
            F.display_case(dp, L, cx - 1.0, 6.0, cx + 1.0, 6.8, Z[0], 1.0, 'BV_BronzeDark', 'PC_GlassClear', 'PC_LightWarm', seed=60 + k)
            F.wall_shelf(dp, L, cx, 16.7, Z[0], 180, 3.6, 2.6, 4, 'BV_BronzeDark', 'PC_WoodLight', 'boxes', seed=70 + k)
            F.coffee_table(fu, L, cx, 12.0, Z[0], 0.5, 0.42, 'PC_StoneTop', 'BV_Bronze')
            F.armchair(fu, L, cx - 1.1, 12.0, Z[0], 90, 'BV_Linen')
            F.armchair(fu, L, cx + 1.1, 12.0, Z[0], -90, 'BV_Linen')
            for x in np.arange(a + 1.0, b - 0.5, 1.6):
                F.linear_pendant(fu, L, x, 5.0, Z[1] - 1.2, 90, 3.0, 'PC_LightStrip', 'BV_BronzeDark')
        else:
            F.plinth(dp, L, cx - 1.6, 1.4, cx + 1.6, 3.0, Z[0], 0.2)
    if L == 0:      # vitrine plinth (zone 1)
        F.plinth(dp, L, -10.9, -0.45, -7.5, 0.4, Z[0], 0.12, 'BV_Cream', 'BV_Bronze')
    # central atrium hall: wide stone stair to the upper gallery
    AR.stair(A, L, 0.0, ATR[1], 90, 2.6, Z[0], Z[1], 'solid', 'BV_Travertine', 'BV_BronzeDark', sub='GrandStair')
    AR.glass_rail(A, L, [(ATR[0], ATR[1]), (ATR[0], ATR[3]), (-1.45, ATR[3])], Z[1], 1.1, sub='AtriumRailL', rail='BV_Bronze', shoe='BV_BronzeDark')
    AR.glass_rail(A, L, [(1.45, ATR[3]), (ATR[2], ATR[3]), (ATR[2], ATR[1])], Z[1], 1.1, sub='AtriumRailR', rail='BV_Bronze', shoe='BV_BronzeDark')
    AR.glass_rail(A, L, [(ATR[0], ATR[1]), (ATR[2], ATR[1])], Z[1], 1.1, sub='AtriumRailF', rail='BV_Bronze', shoe='BV_BronzeDark')
    if L < 2:
        F.ring_light(fu, L, 0.0, 8.5, Z[2] - 1.6, 2.2, 0.08, 'BV_Chandelier')
        F.ring_light(fu, L, 0.0, 8.5, Z[2] - 2.1, 1.5, 0.06, 'BV_Chandelier')
        # upper retail gallery
        for (x, y, k) in ((-9.0, 3.0, 0), (-7.0, 3.0, 1), (-11.0, 3.0, 2), (7.0, 3.0, 3), (9.0, 3.0, 4), (11.0, 3.0, 5)):
            F.mannequin(dp, L, x, y, Z[1], 180, 'PC_WhiteGloss', cloths[k])
        for x in (-10.5, -7.0, 7.0, 10.5):
            F.clothes_rail(dp, L, x, 9.0, Z[1], 0, 2.6, seed=int(80 + x))
            F.display_case(dp, L, x - 0.9, 12.5, x + 0.9, 13.3, Z[1], 1.0, 'BV_BronzeDark', 'PC_GlassClear', 'PC_LightWarm', seed=int(90 + x))
        F.lounge_group(fu, L, 0.0, 16.5, Z[1], 0, 'BV_Linen', 'BV_Velvet')
        for x in (-9.0, 9.0):
            F.plinth(dp, L, x - 1.5, 15.0, x + 1.5, 17.5, Z[1], 0.25, 'BV_Cream', 'BV_Bronze')
        st.add(bm_box(-6.0, Y1 - 0.55, Z[1], 6.0, Y1 - 0.35, Z[2] - 0.5), 'PC_WoodSlat')


for L in (0, 1, 2):
    build(L)

promenade(A, X0 - 1.0, X1 + 1.0, entrances=[ENT, (-12.4, -11.0), (-6.0, -4.4), (2.2, 3.4), (7.4, 8.7)])
bollards(A, [-13.5, -9.0, -4.5, 4.5, 9.0, 13.5], -6.3)
for x in (-11.5, 11.5):
    light_post(A, x, -6.4)
for x in (-6.0, 6.0):
    bench(A, x, -4.2, 0.0, 2.4)
planter(A, -3.6, -4.8, -2.2, -3.6); planter(A, 2.2, -4.8, 3.6, -3.6)

for i, (x, y, z, e) in enumerate(((-9.9, 6.0, 4.4, 900), (-4.4, 6.0, 4.4, 900), (4.4, 6.0, 4.4, 900), (9.9, 6.0, 4.4, 900),
                                  (0.0, 8.5, 8.0, 1600), (-9.0, 8.0, 9.2, 900), (9.0, 8.0, 9.2, 900), (0.0, 15.0, 9.2, 700))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#fff0dc', radius=0.7)
for i, (a, b) in enumerate(ZONES):
    A.light('INTERIOR_LIGHTING', f'WindowSpot{i}', 'SPOT', ((a + b) / 2, 1.6, 4.3), 500, '#ffffff', rot=(-30, 0, 0), spot_deg=60)
A.light('EXTERIOR_LIGHTING', 'AtticWash', 'SPOT', (0.0, -4.0, 0.3), 2200, '#ffe0b0', rot=(-74, 0, 0), spot_deg=40)
for i, x in enumerate((-9.9, -4.4, 4.4, 9.9)):
    A.light('EXTERIOR_LIGHTING', f'PierWash{i}', 'SPOT', (x, -1.0, 0.2), 350, '#ffd7a0', rot=(-82, 0, 0), spot_deg=30)

A.col_box('Podium', X0, 0.0, 0.0, X1, Y1, ATTIC + 0.25)
A.col_box('Vitrine', ZONES[0][0] + 1.3, -0.7, 0.0, ZONES[0][1], 0.0, SF_H)
A.col_box('BayWindow', -3.7, -0.6, Z[1] - 0.4, 3.7, 0.0, Z[2] - 0.2)

A.camera('day', (-20.0, -25.0, 7.5), (0.0, 4.0, 5.6), 25)
A.camera('night', (-17.0, -22.0, 4.0), (0.0, 4.0, 5.6), 25)
A.camera('road', (-22.0, -11.0, 1.15), (0.0, 3.0, 4.4), 26)
A.camera('interior', (-10.5, 16.2, 7.5), (1.5, 6.0, 3.6), 16)
A.checks['probes'] = [dict(name='boutique1_mannequins', p=[-9.9, 2.4, 1.2]), dict(name='boutique3', p=[4.4, 2.4, 1.2]),
                      dict(name='upper_gallery', p=[-9.0, 3.0, 6.8]), dict(name='grand_stair', p=[0.0, 6.0, 2.6])]
finish(A, X0 - 1.0, X1 + 1.0, width=26.0, depth=22.0, height=ATTIC + 0.25, footprint=[X0, 0.0, X1, Y1], storeys=2, floor_levels=Z[:2],
       roof=Z[2], parking='none (promenade frontage)', access='central recessed gallery entrance + four boutique doors on the promenade',
       setback_m=0.0, glass='BV_Glass alpha 0.11, bronze / black-steel frames', concept=__doc__.strip().split('\n')[2], frontage_m=26.0,
       boutiques=NAMES, terrace='none (benches, bollards, empty planters only)')
