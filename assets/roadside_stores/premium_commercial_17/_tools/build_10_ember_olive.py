"""ASSET 10 - Ember & Olive (contemporary grill & Mediterranean restaurant, 1 tall storey).

Massing: 40 m frontage of FOUR road-facing gables (dark standing-seam roofs, ridges at 9.1 m), each bay a black-steel
portal frame holding a 9 m wide floor-to-eave window with a glazed gable triangle above - strong dark framing on a
dark stone plinth, warm copper eave beam carrying the name, a projecting copper entrance box in bay 2.
Inside: open dining under timber-lined gable ceilings, a central grill feature counter with copper hood and live-fire
glow (display kitchen), wine wall, booths and dome pendants.
Site: frontage paving directly off the pavement, optional ANGLED side parking on the right (separate collection).
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('10', '10_ember_and_olive', 'ember_and_olive', 'P10', 'EmberAndOlive', 'Ember & Olive', 1)
defmat('EO_Copper', '#b06f45', 0.28, 1.0, emit='#ff9a50', es=1.2)
defmat('EO_Olive', '#5b6b2e', 0.5)

X0, X1, Y0, Y1 = -20.0, 20.0, 4.0, 22.0
BAYS = [(-20.0, -10.0), (-10.0, 0.0), (0.0, 10.0), (10.0, 20.0)]
ZE, ZR = 6.5, 9.1


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    roof = A.m(L, 'BUILDING_EXTERIOR', 'GableRoofs')
    frm = A.m(L, 'FACADE_DETAILS', 'SteelFrames')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], 0.15, 0.45, 'PC_FloorTerrazzo', 'PC_Concrete', 'PC_StoneDark', sub='GroundSlab')
    for i, (xa, xb) in enumerate(BAYS):
        xc = (xa + xb) / 2
        # two sloped roof plates (overhang 0.5 front/back) - outside dark metal, underside timber
        for (pa, pb) in (((xa - 0.35, ZE - 0.2), (xc, ZR)), ((xc, ZR), (xb + 0.35, ZE - 0.2))):
            pts = [pa, pb, (pb[0], pb[1] - 0.3), (pa[0], pa[1] - 0.3)]
            roof.add(AR.bm_xz_prism(pts, Y0 - 0.8, Y1 + 0.5), 'PC_SteelDark',
                     mat_fn=lambda f: 'PC_TimberDark' if f.normal.z < -0.3 else 'PC_SteelDark')
        # front: big window + gable glass in a black steel portal
        doors = [dict(seg=0, u0=3.2, u1=6.2, h=3.0, kind='pivot')] if i == 1 else []
        AR.curtain(A, L, [(xa + 0.35, Y0), (xb - 0.35, Y0)], 0.55, ZE - 0.45, 3.1, [3.6], 0.07, 0.2, 'PC_AluBlack', 'PC_Glass',
                   sub=f'Bay{i}', doors=doors)
        if i == 1 and L < 2:
            A.m(L, 'GLASS_SYSTEM', 'Bay1Glass').add(bm_vquad(xa + 0.35 + 3.2, xa + 0.35 + 6.2, 0.15, 0.55, Y0, '-Y'), 'PC_Glass')
        M = place('-Y', Vector((0, Y0, 0)))
        A.m(L, 'GLASS_SYSTEM', 'Gables').add(bm_poly_flat([(xa + 0.6, ZE - 0.3), (xb - 0.6, ZE - 0.3), (xc, ZR - 0.5)], 0.0), 'PC_Glass', matrix=M)
        frm.add(bm_box(xa + 0.35, Y0 - 0.15, ZE - 0.45, xb - 0.35, Y0 + 0.15, ZE - 0.3), 'PC_AluBlack')
        for (pa, pb) in (((xa, ZE - 0.3), (xc, ZR - 0.25)), ((xc, ZR - 0.25), (xb, ZE - 0.3))):
            frm.add(AR.bm_xz_prism([pa, pb, (pb[0], pb[1] - 0.35), (pa[0], pa[1] - 0.35)], Y0 - 0.35, Y0 + 0.1), 'PC_AluBlack')
        # rear gable (stone)
        ext.add(bm_poly_flat([(xb, ZE), (xa, ZE), (xc, ZR - 0.2)], 0.0), 'PC_StoneLime', matrix=place('+Y', Vector((0, Y1, 0))))
        ext.add(bm_poly_flat([(xa, ZE), (xb, ZE), (xc, ZR - 0.2)], 0.0), 'PC_TimberDark', matrix=place('-Y', Vector((0, Y1 - 0.01, 0))))
    # piers between bays (black steel), stone plinth, copper eave beam
    for x in (X0, -10.0, 0.0, 10.0, X1):
        frm.add(bm_box(x - 0.35, Y0 - 0.45, 0.0, x + 0.35, Y0 + 0.35, ZE - 0.2, bevel=0.01 if L == 0 else 0), 'PC_AluBlack')
    ext.add(bm_box(X0, Y0 - 0.25, -0.3, X1, Y0 + 0.4, 0.55), 'PC_StoneDark')
    AR.box(frm, X0 - 0.4, Y0 - 0.55, ZE - 0.75, X1 + 0.4, Y0 - 0.3, ZE - 0.45, 'PC_Copper')
    # side + back walls (stone)
    AR.wall(ext, (X1, Y0), (X1, Y1), 0.0, ZE, 0.4, 'PC_StoneLime', 'PC_WallWarm', holes=[(4.0, 12.0, 1.0, 4.4)])
    AR.curtain(A, L, [(X1 + 0.01, Y0 + 4.0), (X1 + 0.01, Y0 + 12.0)], 1.0, 4.4, 2.7, [], 0.07, 0.15, 'PC_AluBlack', 'PC_Glass', sub='Side')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, ZE, 0.4, 'PC_StoneLime', 'PC_WallWarm', holes=[(2.0, 4.0, 0.0, 2.6)])
    AR.wall(ext, (X0, Y1), (X0, Y0), 0.0, ZE, 0.4, 'PC_StoneLime', 'PC_WallWarm')
    # copper entrance box (bay 2)
    cb = (-7.0, Y0 - 2.6, -3.0, Y0)
    AR.box(frm, cb[0], cb[1], 3.05, cb[2], cb[3], 3.55, 'PC_Copper')
    for x in (cb[0], cb[2] - 0.12):
        AR.box(frm, x, cb[1], 0.0, x + 0.12, cb[1] + 0.12, 3.05, 'PC_Copper')
    if L < 2:
        AR.downlights(frm, L, [(-6.0, Y0 - 1.3), (-4.0, Y0 - 1.3)], 3.05, 0.1, 'PC_LightWarm')
    # signage on the copper eave beam + medallion
    sg = A.m(L, 'SIGNAGE', 'Brand')
    if L == 0:
        txt(sg, L, 'EMBER & OLIVE', place('-Y', Vector((5.0, Y0 - 0.56, ZE - 0.6))), 0.24, 0.03, 'serif_b', 'PC_LEDWhite', 'PC_Copper', spacing=1.4)
    txt(sg, L, 'EMBER & OLIVE', place('-Y', Vector((-5.0, cb[1] - 0.02, 3.3))), 0.36, 0.04, 'serif_b', 'EO_Copper', 'PC_Copper', spacing=1.2)
    M = place('-Y', Vector((-15.0, Y0 - 0.45, 3.4)))
    disc(sg, L, M, 1.25, 0.08, 'PC_AluBlack')
    txt(sg, L, 'E&O', M @ Matrix.Translation((0, 0.1, 0.08)), 0.75, 0.05, 'serif_b', 'EO_Copper', 'PC_Copper')
    if L < 2:
        txt(sg, L, 'GRILL · MEDITERRANEAN', M @ Matrix.Translation((0, -0.45, 0.08)), 0.15, 0.02, 'dsemi', 'EO_Copper', 'EO_Copper', spacing=1.2)
    A.sign('entrance_name', (-5.0, cb[1] - 0.1, 3.3), 0.36, width=4.0)
    A.sign('medallion', (-15.0, Y0 - 0.55, 3.4), 0.75, width=2.5)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Dining')
    kt = A.m(L, 'DISPLAY_OBJECTS', 'DisplayKitchen')
    gz = 0.15
    # grill feature counter + copper hood + fire + kitchen line
    F.counter(kt, L, -7.0, 17.0, 7.0, 18.0, gz, 1.1, 'PC_StoneDark', 'PC_StoneTop', 'EO_Copper')
    kt.add(AR.bm_yz_prism([(17.4, 3.4), (20.6, 3.4), (20.6, 4.9), (18.4, 4.9)], -5.0, 5.0), 'PC_Copper')
    kt.add(bm_box(-4.2, 19.2, gz, 4.2, 20.6, gz + 0.9), 'PC_Stainless')
    kt.add(bm_box(-3.8, 19.4, gz + 0.9, 3.8, 20.4, gz + 1.15), 'PC_Fire')
    if L < 2:
        for k in range(14):
            x = -3.6 + k * 0.55
            kt.add(bm_box(x, 19.35, gz + 1.15, x + 0.05, 20.45, gz + 1.2), 'PC_SteelDark')
        kt.add(bm_box(-4.0, 21.0, gz, 4.0, 21.55, 2.2), 'PC_Stainless')
        kt.add(bm_box(-4.0, 21.0, 2.2, 4.0, 21.55, 2.25), 'PC_LightWarm')
        for x in (-6.0, -4.5, -3.0, 3.0, 4.5, 6.0):
            F.stool(fu, L, x, 16.3, gz, 0.75, 'PC_Copper', 'PC_LeatherBlack')
    # wine wall (left) + booths (right wall)
    F.bottle_shelf(fu, L, X0 + 0.45, 13.0, gz, -90, 12.0, 3, seed=7)
    for y in (8.0, 11.5, 15.0):
        F.booth(fu, L, X1 - 1.4, y, gz, 90, 1.7, 'PC_Leather', 'PC_TimberDark', 'PC_StoneTop')
    # dining field
    for x in (-15.5, -10.5, -5.5, 0.0, 5.5, 10.5):
        F.dining_set(fu, L, x, 7.5, gz, 0, 2, 1.5, 0.85, 'PC_Walnut', 'PC_AluBlack', 'PC_LeatherCream')
    for x in (-14.0, -8.0, 8.0, 13.0):
        F.round_set(fu, L, x, 12.5, gz, 4, 0.55, 'PC_Walnut', 'PC_AluBlack', 'EO_Olive')
    # dome pendants from the ridges + ridge strip lights
    for (xa, xb) in BAYS:
        xc = (xa + xb) / 2
        for y in (7.5, 12.0):
            F.pendant(fu, L, xc, y, ZR - 0.35, 3.3, 'cone', 0.45, 'PC_LampGlobe', 'PC_Copper')
        if L < 2:
            fu.add(bm_box(xc - 0.06, Y0 + 0.5, ZR - 0.42, xc + 0.06, Y1 - 0.5, ZR - 0.36), 'PC_LightStrip')
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_vquad(X0 + 1, X1 - 1, 0.5, ZE - 0.5, Y1 - 0.5, '-Y'), 'PC_LightWarm')


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -24.0, 36.0, crossings=[(22.0, 28.0)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-24.0, 0.0, 22.0, Y0)], 'PC_StoneSand', sub='Frontage')
S.asphalt(A, 'DRIVEWAY', [(22.0, 0.0, 28.0, 4.0)])
S.asphalt(A, 'OPTIONAL_PARKING', [(22.0, 4.0, 34.0, 23.0)])
mk = A.s('OPTIONAL_PARKING', 'AngledMarkings')
for k in range(6):
    y = 6.0 + k * 3.0
    mk.add(bm_quad((28.6, y, 0.006), (28.75, y - 0.1, 0.006), (33.6, y + 2.7, 0.006), (33.45, y + 2.8, 0.006)), 'PC_LineWhite')
S.arrow(A, 'OPTIONAL_PARKING', 25.0, 14.0, 90, 3.0)
tf = A.s('OPTIONAL_FORECOURT', 'TerraceFurniture')
for x in (-17.0, -12.5, 8.0, 12.5, 17.0):
    F.round_set(tf, 0, x, 2.0, 0.0, 2, 0.4, 'PC_StoneTop', 'PC_AluBlack', 'PC_LeatherCream', a0=0)

for i, (x, y) in enumerate(((-15, 10), (-5, 10), (5, 10), (15, 10))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, 6.2), 900, '#ffcf98', radius=1.0)
A.light('INTERIOR_LIGHTING', 'GrillGlow', 'POINT', (0.0, 19.9, 1.8), 350, '#ff7a2a', radius=0.8)
A.light('EXTERIOR_LIGHTING', 'EntranceDown', 'SPOT', (-5.0, Y0 - 1.3, 3.0), 500, '#ffd9a8', spot_deg=90)
for i, x in enumerate((-15.0, 5.0, 15.0)):
    A.light('EXTERIOR_LIGHTING', f'GableUp{i}', 'SPOT', (x, Y0 - 1.5, 0.15), 500, '#ffd9a8', rot=(-82, 0, 0), spot_deg=30)
A.col_box('Main', X0, Y0, 0, X1, Y1, ZE)
A.col_box('Roof', X0 - 0.4, Y0 - 0.8, ZE - 0.3, X1 + 0.4, Y1 + 0.5, ZR)
A.camera('day', (32.0, -24.0, 8.0), (-2.0, 12.0, 4.5), 28)
A.camera('night', (-32.0, -22.0, 4.0), (0.0, 12.0, 4.5), 28)
A.camera('road', (-22.0, -7.6, 1.1), (0.0, 11.0, 3.6), 24)
A.camera('interior', (-16.5, 20.5, 1.7), (6.0, 8.0, 3.4), 17)
A.checks['probes'] = [dict(name='Dining_L', p=[-10.5, 7.5, 1.0]), dict(name='Dining_R', p=[10.5, 7.5, 1.0]), dict(name='Grill', p=[0.0, 19.9, 1.3])]
S.finish(A, -24.0, 36.0, width=40.0, depth=18.0, height=ZR, footprint=[X0, Y0, X1, Y1],
         storeys='1 (tall, gabled)', floor_levels=[0.15], roof='4 gables, eaves 6.5 m, ridges 9.1 m',
         parking='optional angled side parking, 6 bays (OPTIONAL_PARKING)', access='right crossing to angled side parking',
         setback_m=4.0, glass='4 x 9.3 m bay windows + glazed gables (PC_Glass)', concept=__doc__.strip().split('\n')[2])
