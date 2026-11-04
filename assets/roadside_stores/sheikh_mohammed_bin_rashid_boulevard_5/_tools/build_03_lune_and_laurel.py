"""BOULEVARD 03 - LUNE & LAUREL CAFE (luxury cafe + patisserie, 2 storeys, 16 m frontage, corner unit).

Massing: a compact champagne-stone block whose right-hand street corner dissolves into a CURVED two-storey glass corner
(4 m radius, bronze mullions, slim bronze slab band).  The stone part is a deliberate vertical composition: a tall
two-storey bronze-framed window with fins in the middle, a recessed arched-head entrance on the left under a small
bronze marquise, and above it a cantilevered first-floor balcony with a bronze railing.  Stepped stone parapet with a
bronze coping; gold script signage on the stone.
Interior: ground-floor coffee counter with espresso machines and lit pastry vitrines, cafe tables along the curved
glass, a bronze spiral stair to the first-floor lounge (sofas, armchairs, globe pendants) that opens onto the balcony.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

A = new_asset('03', '03_lune_and_laurel', 'lune_and_laurel', 'LuneLaurel', 'Lune & Laurel Cafe', 2)

X0, X1, Y0, Y1 = -8.0, 8.0, 0.0, 15.0
RC = 4.2                              # corner radius (centre at X1 - RC, Y0 + RC)
CX, CY = X1 - RC, Y0 + RC
Z = [0.15, 4.8, 9.0]
PAR = 10.1
GL = 0.35                             # glass line of the stone part
ENT = (-7.0, -4.4)
WIN = (-2.9, 1.3)                     # tall two-storey window
SP = (-5.2, 11.2)                     # spiral stair centre
BAL = (-7.6, -1.5, -3.6, 0.0)         # balcony slab (x0, y0, x1, y1)


def corner_pts(n):
    return arc_pts(CX, CY, RC, -90, 0, n)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    n = {0: 12, 1: 6, 2: 4}[L]
    # floor plates follow the rounded corner
    plan = [(X0, Y0 + GL), (CX, Y0 + 0.02)] + corner_pts(n)[1:] + [(X1 - 0.02, Y1), (X0, Y1)]
    AR.slab(A, L, plan, Z[0], 0.45, top='PC_FloorTerrazzo', bottom='PC_Concrete', edge='BV_StoneDarkBase', sub='GroundSlab')
    sp_hole = [(SP[0] + 1.3 * math.cos(2 * math.pi * i / 12), SP[1] + 1.3 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
    AR.slab(A, L, plan, Z[1], 0.35, holes=[sp_hole], top='PC_FloorOak', bottom='BV_PlasterWarm', edge='BV_Bronze', sub='FirstSlab')
    AR.slab(A, L, plan, Z[2], 0.45, top='PC_RoofMembrane', bottom='BV_PlasterWarm', edge='BV_Champagne', comp='BUILDING_EXTERIOR', sub='Roof')
    # ---- stone front (x0 .. CX): solid with openings for entrance + tall window, upper windows
    front = [(X0, 0.0), (CX, 0.0)]
    Lf = CX - X0
    cxe = (ENT[0] + ENT[1]) / 2; we = (ENT[1] - ENT[0]) / 2
    holes = [(ENT[0] - X0, ENT[1] - X0, 0.0, 3.4 + we * 0.5 + 0.2), (WIN[0] - X0, WIN[1] - X0, 0.6, 8.3),
             (ENT[0] - X0 + 0.2, ENT[1] - X0 - 0.2, Z[1] + 0.05, Z[1] + 2.9)]
    AR.wall(ext, front[0], front[1], 0.0, PAR, GL, 'BV_Champagne', 'BV_PlasterWarm', 'BV_Champagne', holes=holes)
    # arched head of the entrance (segmental, built from stone voussoir boxes) + recessed doors
    if L < 2:
        for k in range(9):
            a0 = math.pi * k / 9; a1 = math.pi * (k + 1) / 9
            xa, xb = cxe - we * math.cos(a0), cxe - we * math.cos(a1)
            za, zb = 3.4 - 0.0 + we * 0.45 * math.sin(a0), 3.4 + we * 0.45 * math.sin(a1)
            ext.add(bm_box(min(xa, xb), -0.02, min(za, zb) - 0.0, max(xa, xb), GL, 3.4 + we * 0.5 + 0.2), 'BV_Champagne')
            ext.add(bm_box(min(xa, xb), -0.05, min(za, zb) - 0.06, max(xa, xb), -0.02, min(za, zb)), 'BV_Bronze')
    yb = recessed_portal(A, L, ext, ENT[0] + 0.35, ENT[1] - 0.35, GL, 1.0, 3.4 + we * 0.45 + 0.05, 2.7, 'BV_Champagne', 'BV_BronzeDark', 'BV_Glass',
                         sub='Entrance', leaves=1)
    if L < 2:     # downlights under the balcony, which doubles as the entrance canopy
        AR.downlights(det, L, [(x, -0.75) for x in (-6.6, -5.6, -4.6)], Z[1] - 0.25, 0.07, 'PC_LightWarm')
    # tall two-storey window with bronze fins
    AR.curtain(A, L, [(WIN[0], GL), (WIN[1], GL)], 0.6, 8.3, (WIN[1] - WIN[0]) / 3, [2.9, Z[1] - 0.3, Z[1] + 0.15, 6.6], 0.06, 0.18,
               'BV_BronzeDark', 'BV_GlassWarm', sub='TallWindow', spandrels=[(Z[1] - 0.3, Z[1] + 0.15, 'BV_Bronze')],
               fins=dict(depth=0.45, t=0.05, every=1, mat='BV_Bronze', z0=0.6, z1=8.3))
    det.add(bm_box(WIN[0] - 0.15, -0.2, 0.45, WIN[1] + 0.15, GL, 0.6), 'BV_StoneDarkBase')
    det.add(bm_box(WIN[0] - 0.15, -0.12, 8.3, WIN[1] + 0.15, GL, 8.45), 'BV_Bronze')
    # balcony above the entrance + upper glazed door
    AR.box(det, BAL[0], BAL[1], Z[1] - 0.25, BAL[2], BAL[3], Z[1], 'BV_Champagne', top='PC_FloorOak')
    if L < 2:
        rail = A.m(L, 'FACADE_DETAILS', 'BalconyRail')
        for (p0, p1) in (((BAL[0], 0.0), (BAL[0], BAL[1])), ((BAL[0], BAL[1]), (BAL[2], BAL[1])), ((BAL[2], BAL[1]), (BAL[2], 0.0))):
            M, Ls = AR.seg_frame(p0, p1)
            rail.add(bm_box(0, -0.025, Z[1] + 1.0, Ls, 0.025, Z[1] + 1.06), 'BV_Bronze', matrix=M)
            rail.add(bm_box(0, -0.02, Z[1] + 0.1, Ls, 0.02, Z[1] + 0.14), 'BV_Bronze', matrix=M)
            step = 0.12 if L == 0 else 0.3
            for u in np.arange(0.06, Ls, step):
                rail.add(bm_box(u - 0.012, -0.012, Z[1], u + 0.012, 0.012, Z[1] + 1.0), 'BV_BronzeDark', matrix=M)
    AR.curtain(A, L, [(ENT[0] + 0.2, GL), (ENT[1] - 0.2, GL)], Z[1] + 0.05, Z[1] + 2.9, 1.1, [], 0.05, 0.14, 'BV_BronzeDark', 'BV_Glass',
               sub='BalconyDoor', doors=[dict(seg=0, u0=0.4, u1=1.8, h=2.5, kind='pivot', leaves=1)])
    # ---- curved glass corner (both floors) + continuing side glass, bronze slab band + cornice
    pts = [(CX - 0.01, Y0 + 0.0)] + corner_pts(n)[1:] + [(X1, 9.0)]
    AR.curtain(A, L, pts, 0.0, Z[2] - 0.2, 1.45, [3.5, Z[1] - 0.25, Z[1] + 0.15, 7.8], 0.05, 0.16, 'BV_BronzeDark', 'BV_Glass', sub='Corner',
               spandrels=[(Z[1] - 0.25, Z[1] + 0.15, 'BV_Bronze')],
               doors=[dict(seg=len(pts) - 2, u0=1.6, u1=3.2, h=2.6, kind='slide', leaves=2)])
    band = A.m(L, 'FACADE_DETAILS', 'CornerBands')
    for (za, zb, m) in ((Z[2] - 0.2, PAR - 0.6, 'BV_Champagne'), (PAR - 0.6, PAR - 0.45, 'BV_Bronze')):
        for (p0, p1) in AR.path_segments(pts, False):
            M, Ls = AR.seg_frame(p0, p1)
            band.add(bm_box(-0.02, -0.05, za, Ls + 0.02, 0.35, zb), m, matrix=M)
    # stepped parapet on the stone part + bronze coping
    det.add(bm_box(X0 - 0.05, -0.08, PAR, CX, GL + 0.05, PAR + 0.14), 'BV_Bronze')
    ext.add(bm_box(WIN[0] - 0.4, 0.0, PAR, WIN[1] + 0.4, GL, PAR + 0.7), 'BV_Champagne')
    det.add(bm_box(WIN[0] - 0.45, -0.06, PAR + 0.7, WIN[1] + 0.45, GL + 0.05, PAR + 0.82), 'BV_Bronze')
    # ---- side / party / rear walls + interface
    AR.wall(ext, (X1, 9.0), (X1, Y1), 0.0, PAR, 0.3, 'BV_Champagne', 'BV_PlasterWarm', holes=[(1.5, 3.0, 0.0, 2.6)])
    AR.wall(ext, (X0, Y1), (X0, 0.0), 0.0, PAR, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.3, 'BV_Interface', 'BV_PlasterWarm')
    rear_interface(A, L, X0, X1, Y1 - 0.4, PAR + 0.82, 1.2)
    roof_plant(A, L, X0 + 0.5, 1.5, X1 - 1.2, Y1 - 0.5, Z[2])
    # ---- signage (gold script on stone, small caps line under it, blade sign at the corner)
    sign_text(A, L, 'Lune & Laurel', -1.2 + 0.4, 0.0, 9.35, 0.74, 'garamond_i', 'BV_LetterGold', 'BV_BronzeDark', 0.05, spacing=1.02)
    if L < 2:
        sign_text(A, L, 'CAFÉ · PÂTISSERIE', (BAL[0] + BAL[2]) / 2, BAL[1] + 0.02, Z[1] - 0.13, 0.14, 'cinzel', 'BV_LetterGold', 'BV_BronzeDark', 0.012, spacing=1.25)
        bl = A.m(L, 'SIGNAGE', 'Blade')
        bx, by = X1 - RC * (1 - math.cos(math.radians(45))) + 0.2, Y0 + RC * (1 - math.sin(math.radians(45))) - 0.2
        bl.add(bm_cyl(bx + 0.35, by - 0.35, 5.6, 7.2, 0.45, 24 if L == 0 else 12), 'BV_BronzeDark')
        txt(bl, L, 'L&L', Matrix.Translation((bx + 0.35, by - 0.35, 6.25)) @ Matrix.Rotation(math.radians(-45), 4, 'Z') @
            R.FACING['-Y'].to_4x4() @ Matrix.Translation((0, 0, 0.45)), 0.42, 0.02, 'garamond_i', 'BV_LetterGold', 'BV_BronzeDark')
    interior(L)


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Walls')
    fu = A.m(L, 'FURNITURE', 'Cafe')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Pastry')
    AR.wall(st, (X1 - 0.3, 12.6), (-3.4, 12.6), Z[0], Z[1] - 0.35, 0.2, 'PC_WoodSlat')         # back-of-house screen
    AR.ceiling_panels(A, L, [(X0 + 0.4, GL + 0.3, X1 - 0.6, 12.4)], Z[1] - 0.35, (3.0, 2.6), 0.9, 0.14, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.4, GL + 0.3, X1 - 0.6, 14.6)], Z[2] - 0.45, (3.2, 2.8), 0.9, 0.14, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    # coffee counter (marble top, fluted bronze front) along the back + espresso machines + lit pastry vitrines
    F.counter(dp, L, -1.8, 10.6, 6.4, 11.6, Z[0], 1.05, 'BV_Bronze', 'PC_StoneTop', 'PC_LightWarm')
    F.display_case(dp, L, -1.8, 9.6, 2.8, 10.6, Z[0], 1.25, 'BV_Cream', 'BV_GlassWarm', 'PC_LightWarm', goods=None, seed=31)
    if L < 2:
        for x in (4.0, 5.6):
            F.espresso_machine(dp, L, x, 11.25, Z[0] + 1.05, 180)
        F.bottle_shelf(dp, L, 2.6, 12.45, Z[0], 180, 6.0, seed=33)
        F.display_case(dp, L, -6.6, 6.0, -4.4, 7.0, Z[0], 1.1, 'BV_Cream', 'BV_GlassWarm', 'PC_LightWarm', goods=None, seed=34)
        # cafe tables along the glass + in the middle
        for (x, y) in ((4.6, 2.0), (6.6, 4.6), (6.4, 7.6), (2.2, 3.4), (-0.4, 6.0), (2.6, 6.8), (-3.0, 3.0)):
            F.round_set(fu, L, x, y, Z[0], 2, 0.36, 'PC_StoneTop', 'BV_BronzeDark', 'BV_VelvetGreen', a0=0)
        for x in (-1.0, 0.6):
            F.pendant(fu, L, x, 10.1, Z[1] - 0.35, 1.0, 'globe', 0.18, 'PC_LampGlobe', 'BV_Bronze')
    # bronze spiral stair to the lounge
    AR.spiral_stair(A, L, SP[0], SP[1], 0.12, 1.2, Z[0], Z[1], a0=-90.0, sweep=320.0, tread='PC_FloorOak', struct='BV_BronzeDark')
    # first-floor lounge
    AR.glass_rail(A, L, [(SP[0] - 1.35, SP[1] - 1.35), (SP[0] + 1.35, SP[1] - 1.35), (SP[0] + 1.35, SP[1] + 1.35)], Z[1], 1.05,
                  sub='StairRail', rail='BV_Bronze', shoe='BV_BronzeDark')
    if L < 2:
        F.lounge_group(fu, L, 1.6, 4.0, Z[1], 0, 'BV_Linen', 'BV_Velvet')
        F.lounge_group(fu, L, 5.4, 9.0, Z[1], 90, 'BV_VelvetGreen', 'PC_LeatherCream')
        F.sofa(fu, L, -5.0, 3.0, Z[1], 0, 2.4, 0.9, 'BV_Linen')
        for (x, y) in ((-1.6, 8.0), (1.6, 8.0), (-1.6, 11.0)):
            F.round_set(fu, L, x, y, Z[1], 2, 0.4, 'PC_StoneTop', 'BV_BronzeDark', 'BV_Velvet', a0=0)
        for (x, y) in ((1.6, 4.0), (5.4, 9.0), (-5.0, 3.6)):
            F.pendant(fu, L, x, y, Z[2] - 0.45, 1.3, 'globe', 0.26, 'PC_LampGlobe', 'BV_Bronze')
        st.add(bm_box(-3.4, 14.4, Z[1], 3.4, 14.65, Z[2] - 0.45), 'PC_WoodSlat')


for L in (0, 1, 2):
    build(L)

# ---- site: promenade (front + around the corner), small terrace with bistro sets, street furniture
promenade(A, X0 - 1.0, X1 + 1.0, entrances=[ENT])
side = A.s('SIDEWALK_FRONTAGE', 'SidePaving')
side.add(bm_box(X1, 0.0, -0.2, X1 + 4.0, 10.0, 0.0), 'BV_Paving', mat_fn=mat_by_normal('BV_Paving', 'BV_Paving', 'PC_Curb'), uv='box', tile=4.8)
terrace_deck(A, -3.2, -3.2, 3.6, -0.3, edge_rail=False)
tacc = A.s('OPTIONAL_FORECOURT', 'BistroSets')
for x in (-2.2, 0.2, 2.6):
    F.round_set(tacc, 0, x, -1.6, 0.15, 2, 0.32, 'PC_StoneTop', 'BV_BronzeDark', 'BV_Linen', a0=0)
parasol(tacc, 0, 0.2, -1.8, 0.15, 1.5, 2.4)
planter(A, -3.9, -3.1, -3.4, -0.5, 0.55); planter(A, 3.8, -3.1, 4.3, -0.5, 0.55)
bollards(A, [5.5, 7.0, 8.5], -6.3)
light_post(A, -6.0, -6.4)

for i, (x, y, z, e) in enumerate(((2.0, 6.0, 3.6, 900), (-4.0, 6.0, 3.6, 700), (2.0, 11.0, 3.4, 600), (1.6, 5.0, 7.8, 700),
                                  (-3.0, 9.0, 7.8, 600), (5.0, 9.0, 7.8, 600))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffd6a0', radius=0.7)
A.light('EXTERIOR_LIGHTING', 'SignWash', 'SPOT', (-0.8, -2.2, 5.0), 900, '#ffe0b0', rot=(-50, 0, 0), spot_deg=55)
A.light('EXTERIOR_LIGHTING', 'MarquiseDown', 'SPOT', ((ENT[0] + ENT[1]) / 2, -0.7, 3.9), 450, '#ffd7a0', spot_deg=100)
A.light('EXTERIOR_LIGHTING', 'CornerUp', 'SPOT', (X1 + 1.0, -1.0, 0.2), 600, '#ffd7a0', rot=(-75, 0, -45), spot_deg=45)

A.col_box('Block', X0, 0.0, 0.0, CX, Y1, PAR + 0.8)
A.col_box('Corner', CX, 0.0, 0.0, X1, Y1, PAR)

A.camera('day', (17.0, -19.0, 6.5), (0.5, 5.0, 4.6), 26)
A.camera('night', (15.0, -16.0, 3.6), (0.5, 5.0, 4.6), 26)
A.camera('road', (-14.0, -10.5, 1.15), (1.0, 3.0, 4.2), 26)
A.camera('interior', (6.4, 2.6, 1.9), (-4.6, 10.6, 3.2), 16)
A.checks['probes'] = [dict(name='counter', p=[1.0, 10.2, 1.3]), dict(name='corner_tables', p=[6.4, 4.6, 1.0]),
                      dict(name='L1_lounge', p=[1.6, 4.0, 5.6])]
finish(A, X0 - 1.0, X1 + 1.0, width=16.0, depth=15.0, height=PAR + 0.82, footprint=[X0, 0.0, X1, Y1], storeys=2, floor_levels=Z[:2],
       roof=Z[2], parking='none (promenade frontage)', access='pedestrian: arched entrance (front) + corner door (side)', setback_m=0.0,
       glass='BV_Glass / BV_GlassWarm alpha 0.11-0.12, bronze frames', concept=__doc__.strip().split('\n')[2], frontage_m=16.0,
       terrace='small timber bistro terrace 6.8 x 2.9 m (OPTIONAL_FORECOURT)', corner='right')
