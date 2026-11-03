"""ASSET 16 - Serein Cafe (luxury two-storey glass-and-steel cafe).

Massing: a slender 16 x 14 m glass pavilion in a fine black-steel frame (exposed corner + mid columns, thin floor
edge), a razor-thin flat roof plane with a 1.6 m white soffit overhang, and an upper TERRACE BALCONY cantilevered 3 m
over the pavement on the right half (wrapping the right corner) with frameless glass railing.  Entrance through a
deep black-steel pivot-door portal on the left, opening into a double-height void with globe pendants.
Inside: coffee counter with espresso machines + pastry case, tables, upstairs lounge seating with glass balustrade,
black steel stair.
Site: small pavement terrace with bistro tables directly at the frontage; no parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('16', '16_serein_cafe', 'serein_cafe', 'P16', 'SereinCafe', 'Serein Cafe', 2)
defmat('SR_Letter', '#ffffff', 0.3, emit='#ffffff', es=4.0)

X0, X1, Y0, Y1 = -8.0, 8.0, 4.0, 18.0
Z = [0.15, 4.6, 8.7]
VOID = (-7.6, Y0 + 0.4, -2.0, 9.0)
ST = (6.3, 9.5, 7.7, 16.6)
BAL = (-1.0, Y0 - 3.0, X1 + 2.0, Y0)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Frame')
    det = A.m(L, 'FACADE_DETAILS', 'Balcony')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], Z[0], 0.45, 'PC_FloorTerrazzo', 'PC_Concrete', 'PC_AluBlack', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.1, Y0 + 0.1, X1 - 0.1, Y1 - 0.1), [VOID, ST], Z[1], 0.3, 'PC_FloorOak', 'PC_Ceiling', 'PC_AluBlack')
    # cantilevered balcony (front-right, wrapping the right corner)
    AR.box(det, BAL[0], BAL[1], Z[1] - 0.3, BAL[2], BAL[3], Z[1], 'PC_FloorOak', top='PC_FloorOak')
    AR.box(det, X1, Y0, Z[1] - 0.3, X1 + 2.0, 12.0, Z[1], 'PC_FloorOak', top='PC_FloorOak')
    det.add(bm_box(BAL[0], BAL[1], Z[1] - 0.32, BAL[2], BAL[3], Z[1] - 0.3), 'PC_AluBlack')
    AR.glass_rail(A, L, [(BAL[0], Y0), (BAL[0], BAL[1]), (BAL[2], BAL[1]), (BAL[2], 12.0), (X1, 12.0)], Z[1], 1.1, comp='FACADE_DETAILS',
                  sub='BalconyRail', glass='PC_GlassRail', rail='PC_AluBlack')
    if L < 2:
        AR.downlights(det, L, [(x, Y0 - 1.5) for x in (0.5, 3.0, 5.5, 8.5)], Z[1] - 0.32, 0.08, 'PC_LightWarm')
    # thin roof plane with overhang (white soffit)
    A.m(L, 'BUILDING_EXTERIOR', 'Roof').add(bm_box(X0 - 1.6, Y0 - 1.6, Z[2], X1 + 1.6, Y1 + 0.8, Z[2] + 0.28), 'PC_PanelBlack',
                                            mat_fn=mat_by_normal('PC_RoofMembrane', 'PC_PanelWhite', 'PC_AluBlack'))
    if L < 2:
        AR.downlights(A.m(L, 'BUILDING_EXTERIOR', 'Roof'), L, [(x, Y0 - 0.8) for x in range(-8, 9, 2)], Z[2], 0.07, 'PC_LightWarm')
    # black steel frame: columns + floor edge beam
    for x in (X0, -2.6, 2.6, X1):
        ext.add(bm_box(x - 0.12, Y0 - 0.12, 0.0, x + 0.12, Y0 + 0.12, Z[2]), 'PC_AluBlack')
    for y in (11.0, Y1):
        for x in (X0, X1):
            ext.add(bm_box(x - 0.12, y - 0.12, 0.0, x + 0.12, y + 0.12, Z[2]), 'PC_AluBlack')
    ext.add(bm_box(X0 - 0.12, Y0 - 0.14, Z[1] - 0.32, X1 + 0.12, Y0 + 0.1, Z[1]), 'PC_AluBlack')
    # glazing both floors: front + sides, back wall solid (service)
    for (z0, z1, sub) in ((0.0, Z[1] - 0.32, 'GF'), (Z[1], Z[2], 'L1')):
        doors = [dict(seg=0, u0=1.2, u1=3.6, h=3.0, kind='open')] if sub == 'GF' else [dict(seg=0, u0=9.5, u1=11.5, h=2.6, kind='slide')]
        AR.curtain(A, L, [(X0, Y0), (X1, Y0)], z0, z1, 2.65, [], 0.05, 0.12, 'PC_AluBlack', 'PC_GlassClear', sub=sub, doors=doors,
                   head=(sub == 'L1'), sill=False)
        AR.curtain(A, L, [(X0, Y1 - 2.0), (X0, Y0)], z0, z1, 2.4, [], 0.05, 0.12, 'PC_AluBlack', 'PC_GlassClear', sub=sub + 'L', head=False, sill=False)
        AR.curtain(A, L, [(X1, Y0), (X1, Y1 - 2.0)], z0, z1, 2.4, [], 0.05, 0.12, 'PC_AluBlack', 'PC_GlassClear', sub=sub + 'R', head=False, sill=False,
                   doors=[dict(seg=0, u0=2.0, u1=4.0, h=2.6, kind='slide')] if sub == 'L1' else [])
    AR.wall(ext, (X1, Y1 - 2.0), (X1, Y1), 0.0, Z[2], 0.25, 'PC_PanelBlack', 'PC_WallWhite')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.25, 'PC_PanelBlack', 'PC_WallWhite', holes=[(12.0, 13.6, 0.0, 2.5)])
    AR.wall(ext, (X0, Y1), (X0, Y1 - 2.0), 0.0, Z[2], 0.25, 'PC_PanelBlack', 'PC_WallWhite')
    # pivot-door portal (deep black steel frame, projecting) on the left
    px0, px1 = X0 + 1.0, X0 + 3.8
    for (a, b, c, d, e, f) in ((px0 - 0.25, Y0 - 1.2, 0.0, px0, Y0, 3.4), (px1, Y0 - 1.2, 0.0, px1 + 0.25, Y0, 3.4),
                               (px0 - 0.25, Y0 - 1.2, 3.15, px1 + 0.25, Y0, 3.4)):
        ext.add(bm_box(a, b, c, d, e, f), 'PC_AluBlack')
    if L < 2:
        A.m(L, 'GLASS_SYSTEM', 'PivotDoor').add(AR.quad_world((px0 + 1.15, Y0 - 0.1, 0.05), (px0 + 2.45, Y0 - 1.0, 0.05),
                                                              (px0 + 2.45, Y0 - 1.0, 3.1), (px0 + 1.15, Y0 - 0.1, 3.1)), 'PC_GlassClear')
        A.m(L, 'GLASS_SYSTEM', 'PivotDoor').add(bm_box(px0 + 0.2, Y0 - 0.02, 0.0, px0 + 1.15, Y0 + 0.02, 3.1), 'PC_GlassClear')
        ext.add(bm_hquad(px0, Y0 - 1.2, px1, Y0, 3.149, down=True), 'PC_LightWarm')
    # signage: fine letters on the roof fascia + projecting blade
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'SEREIN', place('-Y', Vector((-4.6, Y0 - 1.25, 3.95))), 0.52, 0.04, 'xlight', 'SR_Letter', 'PC_AluBlack', spacing=1.5)
    sg.add(bm_box(-7.4, Y0 - 1.3, 3.55, -1.8, Y0 - 1.15, 4.35), 'PC_AluBlack')
    sg.add(bm_box(X0 - 1.6, Y0 - 1.0, 5.5, X0 - 1.5, Y0 + 0.2, 7.6), 'PC_AluBlack')
    if L < 2:
        for k, ch in enumerate('SEREIN'):
            txt(sg, L, ch, Matrix.Translation((X0 - 1.62, Y0 - 0.4, 7.3 - k * 0.32)) @ R.FACING['-X'].to_4x4(), 0.25, 0.01, 'dsemi',
                'SR_Letter', 'SR_Letter')
        txt(sg, L, 'COFFEE ROASTERS', place('-Y', Vector((-4.6, Y0 - 1.32, 3.66))), 0.13, 0.01, 'dsemi', 'SR_Letter', 'SR_Letter', spacing=1.6)
    A.sign('portal_name', (-4.6, Y0 - 1.35, 3.95), 0.52, width=4.5)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Cafe')
    gz = Z[0]
    AR.stair(A, L, 7.0, ST[1], 90, 1.2, gz, Z[1], 'floating', 'PC_FloorOak', 'PC_AluBlack', sub='Stair', max_flight=5.0, rails=(True, False),
             rail_mat='PC_AluBlack')
    AR.glass_rail(A, L, [(VOID[2], Y0 + 0.4), (VOID[2], VOID[3]), (VOID[0], VOID[3])], Z[1], rail='PC_AluBlack')
    AR.glass_rail(A, L, [(ST[0], ST[3]), (ST[0], ST[1]), (ST[2], ST[1])], Z[1], sub='StairRail', rail='PC_AluBlack')
    AR.ceiling_panels(A, L, rect_subtract([(X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5)], VOID), Z[1] - 0.3, (3.0, 2.6), w=0.4, d=0.4,
                      mat='PC_LightWarm', lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5)], Z[2] - 0.02, (3.0, 2.6), w=0.4, d=0.4, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    # coffee bar along the back
    F.counter(fu, L, -4.5, 14.2, 4.5, 15.0, gz, 1.05, 'PC_PanelBlack', 'PC_StoneTop', 'PC_LightWarm')
    F.display_case(fu, L, -4.4, 13.4, -1.6, 14.2, gz, 1.25, 'PC_PanelBlack', 'PC_GlassClear', 'PC_LightWarm', 'PC_WoodLight')
    F.espresso_machine(fu, L, 0.8, 14.6, gz + 1.05, 180)
    F.espresso_machine(fu, L, 3.2, 14.6, gz + 1.05, 180)
    F.bottle_shelf(fu, L, 0.0, Y1 - 0.35, gz, 0, 8.0, 2, seed=3, back='PC_WoodLight')
    for x in (-0.5, 1.0, 2.5):
        F.stool(fu, L, x, 13.4, gz, 0.75, 'PC_AluBlack', 'PC_LeatherCream')
    for (x, y) in ((1.0, 7.0), (4.5, 7.0), (1.0, 10.5), (4.5, 10.5), (-5.5, 11.5)):
        F.round_set(fu, L, x, y, gz, 2, 0.4, 'PC_StoneTop', 'PC_AluBlack', 'PC_FabricGrey', a0=0)
    # void pendants (globes at different drops)
    if L < 2:
        for i, (x, y) in enumerate(((-6.5, 5.5), (-5.0, 6.5), (-3.5, 5.2), (-6.0, 7.8), (-4.0, 8.2))):
            F.pendant(fu, L, x, y, Z[2] - 0.05, 2.2 + (i % 3) * 1.2, 'globe', 0.22)
    # upstairs lounge
    F.sofa(fu, L, -4.5, 16.5, Z[1], 0, 2.6, 0.9, 'PC_FabricCream')
    F.coffee_table(fu, L, -4.5, 15.3, Z[1], 0.5)
    for (x, y) in ((1.0, 6.5), (4.5, 6.5), (1.0, 10.0), (4.5, 10.0)):
        F.round_set(fu, L, x, y, Z[1], 2, 0.4, 'PC_StoneTop', 'PC_AluBlack', 'PC_LeatherCream', a0=0)
    for x in (-6.5, -2.0):
        F.lounge_chair(fu, L, x, 11.5, Z[1], 180, 'PC_FabricTeal')
    for x in (1.0, 4.5):
        F.round_set(fu, L, x, Y0 - 1.5, Z[1], 2, 0.35, 'PC_StoneTop', 'PC_AluBlack', 'PC_FabricCream', a0=0)


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -14.0, 14.0)
S.paved(A, 'OPTIONAL_FORECOURT', [(-14.0, 0.0, 14.0, Y0)], 'PC_PaverLight', sub='PavementTerrace')
tf = A.s('OPTIONAL_FORECOURT', 'BistroTables')
for x in (0.5, 3.5, 6.5, 10.5):
    F.round_set(tf, 0, x, 2.0, 0.0, 2, 0.35, 'PC_StoneTop', 'PC_AluBlack', 'PC_FabricCream', a0=0)

for i, (x, y, z, e) in enumerate(((0, 10, 4.0, 500), (-5, 6, 7.8, 500), (2, 10, 8.1, 500))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffdcb0', radius=0.8)
A.light('EXTERIOR_LIGHTING', 'PortalDown', 'SPOT', (-4.6, Y0 - 0.6, 3.1), 300, '#ffdcb0', spot_deg=100)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[2] + 0.28)
A.col_box('Balcony', BAL[0], BAL[1], Z[1] - 0.3, BAL[2], 12.0, Z[1] + 1.1)
A.col_box('Roof', X0 - 1.6, Y0 - 1.6, Z[2], X1 + 1.6, Y1 + 0.8, Z[2] + 0.28)
A.camera('day', (22.0, -16.0, 6.0), (0.0, 9.0, 4.0), 28)
A.camera('night', (-20.0, -15.0, 3.5), (0.0, 9.0, 4.2), 28)
A.camera('road', (16.0, -7.6, 1.1), (-1.0, 8.0, 3.6), 24)
A.camera('interior', (5.6, 16.6, 1.6), (-5.0, 6.5, 6.4), 16)
A.checks['probes'] = [dict(name='GF_tables', p=[1.0, 7.0, 1.0]), dict(name='Coffee_bar', p=[0.0, 14.0, 1.3]),
                      dict(name='L1_lounge', p=[1.0, 6.5, Z[1] + 1.0]), dict(name='Void_pendants', p=[-5.0, 6.5, 5.0])]
S.finish(A, -14.0, 14.0, width=16.0, depth=14.0, height=Z[2] + 0.28, footprint=[X0 - 1.6, Y0 - 3.0, X1 + 2.0, Y1 + 0.8],
         storeys=2, floor_levels=Z[:2], roof=Z[2], parking='none (pavement terrace)', access='pedestrian only', setback_m=4.0,
         glass='full-height PC_GlassClear on both floors in a black steel frame', concept=__doc__.strip().split('\n')[2])
