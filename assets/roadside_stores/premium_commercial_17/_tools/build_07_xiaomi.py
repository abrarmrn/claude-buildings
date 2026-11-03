"""ASSET 07 - Xiaomi flagship store (2 storeys).

Massing: compact two-storey box with a CHAMFERED right corner holding the entrance inside a big orange rounded-square
portal (echoing the badge shape).  The front is a full-height glass wall overlaid by a staggered grid of proud white
modular panels (~35 % cover) and slim orange fins, so the facade reads as a pixel pattern while most of the glass
stays transparent.  Inside: phone islands, a TV wall, smart-home and wearables zones, e-scooters, an orange stair to
an upper retail floor set back 2.5 m from the glass.
Site: corner plaza at the entrance + optional small side car park on the left (separate collection).
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('07', '07_xiaomi_flagship', 'xiaomi_flagship', 'P07', 'XiaomiFlagship', 'Xiaomi Flagship Store', 2)
defmat('XM_Orange', '#ff6900', 0.35, 0.1)
defmat('XM_OrangeGlow', '#ff6900', 0.3, emit='#ff6a00', es=3.5)
defmat('XM_Letter', '#3a3b3d', 0.35, emit='#ffffff', es=0.0)
defmat('XM_LetterW', '#ffffff', 0.3, emit='#ffffff', es=4.0)
SPECIAL_MATS['XM_Badge'] = lambda: mat_logo('XM_Badge', badge_png('pc_logo_xiaomi.png', (255, 105, 0), 'mi', size=0.52), 3.5)

X0, X1, Y0, Y1 = -13.0, 13.0, 5.0, 25.0
CH = 4.0                                           # chamfer
Z = [0.15, 5.0, 9.6]
ST = (-12.7, 8.8, -10.5, 17.3)
L1Y = Y0 + 2.5
PATTERN = ['P..........', 'P......P...', 'P.P....P..P', 'PPP..PP..PP']    # rows bottom -> top, 11 x 2 m modules
ROWS = [(0.0, 2.4), (2.4, 4.6), (5.0, 7.3), (7.3, 9.6)]


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    pan = A.m(L, 'FACADE_DETAILS', 'ModularPanels')
    foot = [(X0, Y0), (X1 - CH, Y0), (X1, Y0 + CH), (X1, Y1), (X0, Y1)]
    A.m(L, 'BUILDING_INTERIOR', 'GroundSlab').add(bm_prism(foot, -0.3, Z[0]), 'PC_FloorTerrazzo',
                                                   mat_fn=mat_by_normal('PC_FloorTerrazzo', 'PC_Concrete', 'PC_PanelWhite'))
    l1 = [(X0 + 0.3, L1Y), (X1 - CH + 2.5 * 0.41, L1Y), (X1 - 0.3, Y0 + CH + 1.2), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)]
    AR.slab(A, L, l1, Z[1], 0.4, [AR.poly_rect(*ST)], 'PC_FloorTerrazzo', 'PC_Ceiling', 'PC_PanelWhite')
    A.m(L, 'BUILDING_EXTERIOR', 'Roof').add(bm_prism(foot, Z[2] - 0.5, Z[2]), 'PC_RoofGravel',
                                            mat_fn=mat_by_normal('PC_RoofGravel', 'PC_Ceiling', 'PC_PanelWhite'))
    AR.parapet(ext, foot, Z[2], 1.0, 0.3, 'PC_PanelWhite')
    # front glass wall + spandrel at L1
    AR.curtain(A, L, [(X0, Y0), (X1 - CH, Y0)], 0.0, Z[2] - 0.5, 2.0, [2.4, 4.6, 7.3], 0.05, 0.16, 'PC_AluSilver', 'PC_Glass',
               sub='Front', spandrels=[(4.6, 5.0, 'PC_PanelWhite')])
    # chamfer: entrance glass + orange rounded portal + badge
    AR.curtain(A, L, [(X1 - CH, Y0), (X1, Y0 + CH)], 0.0, Z[2] - 0.5, 1.9, [4.6], 0.05, 0.16, 'PC_AluSilver', 'PC_Glass', sub='Corner',
               doors=[dict(seg=0, u0=1.33, u1=4.33, h=3.0, kind='slide')])
    M, Ls = seg_frame((X1 - CH, Y0), (X1, Y0 + CH))
    Mf = M @ Matrix.Translation((Ls / 2, -0.05, 0.0)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    seg = 6 if L == 0 else 2
    outer = rounded_rect(-Ls / 2 - 0.35, 0.0, Ls / 2 + 0.35, 6.4, 1.6, seg)
    inner = rounded_rect(-Ls / 2 + 0.2, 0.0, Ls / 2 - 0.2, 5.85, 1.25, seg)
    ext.add(R.bm_ring_prism(outer, inner, 0.0, 0.9), 'XM_Orange', matrix=Mf)
    if L < 2:
        ext.add(R.bm_ring_prism(inner, [(x * 0.985, y * 0.99) for (x, y) in inner], 0.88, 0.92), 'XM_OrangeGlow', matrix=Mf)
    sg = A.m(L, 'SIGNAGE', 'Brand')
    decal(sg, Mf @ Matrix.Translation((0, 7.8, 0.3)), 2.2, 2.2, 'XM_Badge')
    # staggered white modular panels (proud of the glass) + orange fins
    for r, (za, zb) in enumerate(ROWS):
        for c, ch in enumerate(PATTERN[r]):
            if ch != 'P':
                continue
            xa = X0 + c * 2.0
            pan.add(bm_box(xa + 0.06, Y0 - 0.32, za + 0.06, xa + 1.94, Y0 - 0.12, zb - 0.06, bevel=0.02 if L == 0 else 0), 'PC_PanelWhite')
    for x in (-6.0, -4.0, 4.0):
        pan.add(bm_box(x - 0.05, Y0 - 0.75, 5.0, x + 0.05, Y0 - 0.05, Z[2] - 0.5), 'XM_Orange')
    # other walls
    AR.wall(ext, (X1, Y0 + CH), (X1, Y1), 0.0, Z[2] + 1.0, 0.3, 'PC_PanelWhite', 'PC_WallWhite', holes=[(1.0, 9.0, 1.0, 4.0), (1.0, 9.0, 6.0, 8.6)])
    AR.curtain(A, L, [(X1 + 0.01, Y0 + CH + 1.0), (X1 + 0.01, Y0 + CH + 9.0)], 1.0, 4.0, 2.0, [], 0.05, 0.12, 'PC_AluSilver', 'PC_Glass', sub='SideA')
    AR.curtain(A, L, [(X1 + 0.01, Y0 + CH + 1.0), (X1 + 0.01, Y0 + CH + 9.0)], 6.0, 8.6, 2.0, [], 0.05, 0.12, 'PC_AluSilver', 'PC_Glass', sub='SideB')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2] + 1.0, 0.3, 'PC_PanelWhite', 'PC_WallWhite', holes=[(20.0, 22.5, 0.0, 2.8)])
    AR.wall(ext, (X0, Y1), (X0, Y0), 0.0, Z[2] + 1.0, 0.3, 'PC_PanelWhite', 'PC_WallWhite')
    AR.box(ext, X0 - 0.06, Y0 + 2.0, 0.6, X0, Y0 + 2.6, Z[2] + 0.6, 'XM_Orange')
    # fascia lettering
    txt(sg, L, 'Xiaomi', place('-Y', Vector((-3.5, Y0 - 0.32, Z[2] + 0.12))), 1.3, 0.12, 'bold', 'XM_LetterW', 'PC_AluSilver')
    A.sign('fascia_wordmark', (-3.5, Y0 - 0.4, Z[2] + 0.15), 0.95, width=4.0)
    A.sign('portal_badge', (X1 - CH / 2 + 0.3, Y0 + CH / 2 - 0.3, 7.8), 2.2, normal=(0.707, -0.707, 0), width=2.2)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Products')
    gz = Z[0]
    AR.stair(A, L, -11.6, ST[1] + 0.2, 90, 1.6, gz, Z[1], 'floating', 'PC_WoodLight', 'XM_Orange', sub='Stair', max_flight=6.0,
             rails=(False, True))
    AR.glass_rail(A, L, [(ST[2], ST[3]), (ST[2], L1Y), (X1 - CH + 1.0, L1Y), (X1 - 0.4, Y0 + CH + 1.0)], Z[1])
    AR.ceiling_panels(A, L, [(X0 + 0.5, L1Y + 0.4, X1 - 0.5, Y1 - 0.5)], Z[1] - 0.4, (2.6, 2.4), w=1.8, d=0.2, lod2_glow='PC_LightCool')
    AR.ceiling_panels(A, L, [(X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5)], Z[2] - 0.5, (2.6, 2.4), w=1.8, d=0.2, lod2_glow='PC_LightCool')
    # GF: orange-edged phone tables, TV wall, wearables, smart home, scooters
    for (x, y) in ((-4.0, 10.5), (3.0, 10.5), (-0.5, 15.5)):
        F.product_table(dp, L, x, y, gz, 0, 3.4, 1.1, 0.9, 'PC_WhiteGloss', 'XM_Orange', 'phones', seed=int(x * 5 + y))
    F.tv_wall(dp, L, 2.0, Y1 - 0.45, gz, 0, 4, 2, 1.9, 1.05, 0.12, 0.9, seed=21)
    F.display_case(dp, L, 6.5, 15.0, 10.5, 16.0, gz, 1.2, 'PC_WhiteGloss', 'PC_GlassClear', 'PC_LightCool', 'PC_DeviceBlack')
    F.wall_shelf(dp, L, -7.0, Y1 - 0.45, gz, 0, 5.0, 2.4, 4, 'PC_WhiteGloss', 'PC_WoodLight')
    for i, x in enumerate((-8.5, -6.0)):
        F.plinth(dp, L, x - 1.0, 19.5, x + 1.0, 21.5, gz, 0.15, 'PC_WhiteGloss', 'PC_AluSilver', 'XM_OrangeGlow')
        scooter(dp, L, x, 20.5, gz + 0.15, 30 + i * 20)
    for k in range(4):
        dp.add(bm_cyl(-3.0 + k * 1.2, 21.0, gz + 0.9, gz + 0.99, 0.17, 16 if L == 0 else 8), 'PC_PlasticWhite')
    F.product_table(dp, L, -1.2, 21.0, gz, 0, 5.4, 1.0, 0.9, 'PC_WoodLight', 'PC_WhiteGloss', 'none')
    # L1: upstairs retail
    F.tv_wall(dp, L, 2.0, Y1 - 0.45, Z[1], 0, 3, 2, 2.4, 1.35, 0.12, 0.8, seed=22)
    for (x, y) in ((-5.0, 13.0), (3.5, 13.0)):
        F.product_table(dp, L, x, y, Z[1], 0, 3.4, 1.1, 0.9, 'PC_WoodLight', 'XM_Orange', 'mixed', seed=int(x + 40))
    F.island(dp, L, 8.5, 18.5, Z[1], 1.0, 0.95, 'PC_WhiteGloss', 'PC_WhiteGloss', 'watches', seed=5, led='XM_OrangeGlow')
    F.sofa(fu, L, -5.0, 21.5, Z[1], 180, 2.6, 0.9, 'PC_FabricGrey')
    F.coffee_table(fu, L, -5.0, 20.3, Z[1], 0.45)
    if L < 2:
        for x in (-4.0, 3.0):
            F.linear_pendant(fu, L, x, 10.5, Z[1] - 1.4, 0, 3.0, 'PC_LightStrip')


def scooter(acc, L, x, y, z, ang):
    if L == 2:
        return
    M = AR.T(x, y, z, ang)
    acc.add(bm_box(-0.5, -0.09, 0.1, 0.5, 0.09, 0.16), 'PC_DeviceBlack', matrix=M)
    for u in (-0.5, 0.5):
        acc.add(bm_cyl_between((u, -0.03, 0.11), (u, 0.03, 0.11), 0.11, 10), 'PC_Tyre', matrix=M)
    acc.add(bm_cyl_between((0.5, 0, 0.16), (0.45, 0, 1.05), 0.022, 6), 'PC_DeviceSilver', matrix=M)
    acc.add(bm_cyl_between((0.45, -0.25, 1.05), (0.45, 0.25, 1.05), 0.018, 6), 'PC_DeviceBlack', matrix=M)


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -28.0, 20.0, crossings=[(-27.0, -21.0)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-21.0, 0.0, 20.0, Y0)], 'PC_PaverLight', sub='Plaza')
A.s('OPTIONAL_FORECOURT', 'CornerPlaza').add(bm_prism([(X1 - CH, Y0), (20.0, Y0), (20.0, Y0 + CH + 3.0), (X1, Y0 + CH + 3.0), (X1, Y0 + CH)],
                                                       -0.2, 0.0), 'PC_PaverLight')
S.asphalt(A, 'DRIVEWAY', [(-27.0, 0.0, -21.0, 6.0)])
S.asphalt(A, 'OPTIONAL_PARKING', [(-27.0, 6.0, -14.0, 24.0)])
S.bays(A, -20.6, 7.5, 6, 2.6, 5.4, 1, along='y')
for x in (-16.0, -10.0, -4.0, 2.0, 8.0):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 0.8, 0.0, 0.9, 0.1, 'PC_AluDark', 'XM_OrangeGlow')

for i, (x, y, z, e) in enumerate(((-3, 11, 4.4, 1300), (4, 16, 4.4, 1300), (-7, 20, 4.4, 1000), (-3, 13, 9.0, 1200), (5, 18, 9.0, 1200))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#f6f8ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'PortalWash', 'SPOT', (X1 + 3.0, Y0 - 3.0, 0.2), 900, '#fff1e0', rot=(-65, 0, 45), spot_deg=40)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[2] + 1.0)
A.camera('day', (28.0, -22.0, 7.0), (0.0, 13.0, 4.8), 28)
A.camera('night', (-26.0, -20.0, 4.0), (1.0, 13.0, 5.0), 28)
A.camera('road', (20.0, -7.6, 1.1), (-1.0, 12.0, 4.0), 24)
A.camera('interior', (9.0, 7.6, 1.6), (-10.0, 15.0, 4.6), 16)
A.checks['probes'] = [dict(name='GF_tables', p=[-0.5, 15.5, 1.2]), dict(name='GF_front', p=[-4.0, 10.5, 1.2]),
                      dict(name='L1_tables', p=[-5.0, 13.0, Z[1] + 1.2]), dict(name='L1_tvwall', p=[2.0, Y1 - 0.6, Z[1] + 2.0])]
S.finish(A, -28.0, 20.0, width=26.0, depth=20.0, height=Z[2] + 1.0, footprint=[X0, Y0, X1, Y1],
         storeys=2, floor_levels=Z[:2], roof=Z[2], parking='optional left side car park, 6 bays (OPTIONAL_PARKING)',
         access='left crossing to the small side car park; corner pedestrian plaza', setback_m=5.0,
         glass='full-height PC_Glass behind ~35 % modular panel cover', concept=__doc__.strip().split('\n')[2])
