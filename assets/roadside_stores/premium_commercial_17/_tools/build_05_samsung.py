"""ASSET 05 - Samsung flagship experience store (2 storeys).

Massing: a black-metal framed box whose LEFT corner is wrapped by a curved 11 m tall LED media wall (rounded corner,
radius 4 m); the right two thirds are a two-storey glass exhibition front split by a slim black floor band, with a
grand recessed full-height entrance portal in brushed silver.  Upper floor is set back 3 m from the glass so both
levels read through the facade; an escalator links the floors.
Site: shallow pedestrian forecourt with a short drop-off lay-by (service-road side), no dedicated parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('05', '05_samsung_flagship', 'samsung_flagship', 'P05', 'SamsungFlagship', 'Samsung Flagship Experience Store', 2)
defmat('SS_Letter', '#ffffff', 0.3, emit='#ffffff', es=4.5)
defmat('SS_Blue', '#1428a0', 0.3, emit='#1d3fd0', es=3.0)
SPECIAL_MATS['SS_Media'] = lambda: mat_image_emissive('SS_Media', media_png('pc_media_samsung.png', [(4, 8, 40), (20, 60, 220), (90, 40, 200),
                                                                                                    (0, 170, 255), (240, 240, 255), (60, 0, 140)]), 3.0)

X0, X1, Y0, Y1 = -17.0, 17.0, 7.0, 29.0
Z = [0.15, 6.0, 12.0]
RC = 4.0                                            # media wall corner radius
XG = -5.5                                           # end of the media wall on the front
ESC = (11.9, 9.6, 14.3, 22.4)                       # escalator well in L1
L1Y = Y0 + 3.0                                      # L1 slab front edge (set back)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    med = A.m(L, 'FACADE_DETAILS', 'MediaWall')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], Z[0], 0.45, 'PC_FloorTerrazzo', 'PC_Concrete', 'PC_PanelBlack', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.3, L1Y, X1 - 0.3, Y1 - 0.3), [ESC], Z[1], 0.4, 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelBlack')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], Z[2], 0.5, 'PC_RoofGravel', 'PC_Ceiling', 'PC_PanelBlack', comp='BUILDING_EXTERIOR', sub='Roof')
    # media wall: front segment + rounded corner + left side, 0.6 m proud LED surface on a black frame
    n = {0: 12, 1: 6, 2: 3}[L]
    corner = arc_pts(X0 + RC, Y0 + RC, RC, 270, 180, n)               # from front to left side
    path = [(XG, Y0), (X0 + RC, Y0)] + corner[1:] + [(X0, Y0 + 14.0)]
    path = list(reversed(path))     # CCW (outside on the right)
    for (p0, p1) in zip(path[:-1], path[1:]):
        M, Ls = seg_frame(p0, p1)
        med.add(bm_box(0, -0.05, 0.6, Ls, 0.6, Z[2] + 0.4), 'PC_PanelBlack', matrix=M)
    total = sum(math.dist(a, b) for a, b in zip(path[:-1], path[1:]))
    u = 0.0
    for (p0, p1) in zip(path[:-1], path[1:]):
        M, Ls = seg_frame(p0, p1)
        q = bm_vquad(0, Ls, 1.0, Z[2], -0.08, '-Y')
        u0, u1 = u / total, (u + Ls) / total
        med.add(q, 'SS_Media', matrix=M, uv='fit', cell=(u0, 0, u1, 1))
        u += Ls
    # black metal frame: roof fascia band, right end pier, floor band
    AR.box(ext, XG - 0.3, Y0 - 0.6, Z[2] - 1.6, X1 + 0.6, Y0 + 0.3, Z[2] + 0.6, 'PC_PanelBlack')
    AR.box(ext, X1 - 0.6, Y0 - 0.6, 0.0, X1 + 0.6, Y0 + 0.3, Z[2] - 1.6, 'PC_PanelBlack')
    AR.box(ext, XG - 0.3, Y0 - 0.25, Z[1] - 0.5, X1 - 0.6, Y0 + 0.0, Z[1] - 0.2, 'PC_PanelBlack')
    # glass front (x XG..X1) with grand entrance portal
    PX0, PX1 = 2.5, 9.5
    for (xa, xb) in ((XG, PX0), (PX1, X1 - 0.6)):
        AR.curtain(A, L, [(xa, Y0), (xb, Y0)], 0.0, Z[2] - 1.6, 2.6, [Z[1] - 0.5, Z[1] - 0.2], 0.06, 0.2, 'PC_AluBlack', 'PC_Glass',
                   sub=f'Front{int(xa)}', spandrels=[(Z[1] - 0.5, Z[1] - 0.2, 'PC_PanelBlack')])
    # portal: recessed 2.2 m, silver surround, full-height glass with doors
    AR.box(ext, PX0 - 0.6, Y0 - 0.7, 0.0, PX0, Y0 + 2.2, Z[2] - 1.6, 'PC_PanelSilver')
    AR.box(ext, PX1, Y0 - 0.7, 0.0, PX1 + 0.6, Y0 + 2.2, Z[2] - 1.6, 'PC_PanelSilver')
    AR.box(ext, PX0 - 0.6, Y0 - 0.7, Z[2] - 2.4, PX1 + 0.6, Y0 + 2.2, Z[2] - 1.6, 'PC_PanelSilver')
    AR.curtain(A, L, [(PX0, Y0 + 2.2), (PX1, Y0 + 2.2)], 0.0, Z[2] - 2.4, 1.75, [4.2], 0.06, 0.15, 'PC_AluSilver', 'PC_Glass', sub='Portal',
               doors=[dict(seg=0, u0=1.75, u1=5.25, h=3.4, kind='slide')])
    if L < 2:
        AR.downlights(ext, L, [(x, Y0 + 0.8) for x in (3.5, 6.0, 8.5)], Z[2] - 2.4, 0.15, 'PC_LightPanel')
        ext.add(bm_hquad(PX0, Y0 - 0.7, PX1, Y0 + 2.2, 0.01), 'PC_StoneDark')
    # sides + back
    AR.wall(ext, (X1, Y0 + 0.3), (X1, Y1), 0.0, Z[2] + 0.6, 0.35, 'PC_PanelBlack', 'PC_WallWhite')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2] + 0.6, 0.35, 'PC_PanelBlack', 'PC_WallWhite', holes=[(26.0, 29.0, 0.0, 3.0)])
    AR.wall(ext, (X0, Y1), (X0, Y0 + 14.0), 0.0, Z[2] + 0.6, 0.35, 'PC_PanelBlack', 'PC_WallWhite')
    # behind the media wall: inner wall (the wall is opaque, display interior lies to its right)
    AR.wall(ext, (X0 + 0.6, Y0 + 14.0), (X0 + 0.6, Y0 + RC), 0.0, Z[2], 0.2, 'PC_WallWhite', 'PC_WallWhite')
    AR.wall(ext, (X0 + RC, Y0 + 0.6), (XG, Y0 + 0.6), 0.0, Z[2], 0.2, 'PC_WallWhite', 'PC_WallWhite')
    # signage on the fascia
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'SAMSUNG', place('-Y', Vector((5.5, Y0 - 0.62, Z[2] - 0.55))), 1.05, 0.12, 'xbold', 'SS_Letter', 'PC_AluSilver', spacing=1.25)
    if L < 2:
        txt(sg, L, 'EXPERIENCE STORE', place('-Y', Vector((5.5, Y0 - 0.27, Z[1] - 0.35))), 0.2, 0.02, 'dsemi', 'SS_Letter', 'SS_Letter', spacing=1.3)
    A.sign('fascia_wordmark', (5.5, Y0 - 0.7, Z[2] - 0.55), 1.05, width=11.0)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Products')
    gz = 0.15
    AR.escalator(A, L, 13.1, ESC[1] - 2.2, 90, Z[0], Z[1], 1.0)
    AR.glass_rail(A, L, [(X0 + 0.6 + 4.0, L1Y), (ESC[0], L1Y), (ESC[0], ESC[3])], Z[1])
    AR.glass_rail(A, L, [(ESC[2], ESC[3] - 2.2), (ESC[2], L1Y), (X1 - 0.4, L1Y)], Z[1], sub='Rail2')
    AR.ceiling_panels(A, L, [(XG + 0.5, L1Y + 0.4, X1 - 0.5, Y1 - 0.5)], Z[1] - 0.4, (2.4, 2.2), w=1.2, d=1.2, lod2_glow='PC_LightCool',
                      mat='PC_LightCool')
    AR.ceiling_panels(A, L, [(X0 + 1.0, Y0 + 1.0, X1 - 0.5, Y1 - 0.5)], Z[2] - 0.5, (2.4, 2.2), w=1.2, d=1.2, lod2_glow='PC_LightCool',
                      mat='PC_LightCool')
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_vquad(XG, X1 - 1, 0.5, 11.0, Y1 - 0.5, '-Y'), 'PC_Screen', uv='fit', cell=(0, 0, 1, 1))
    # GF: TV wall (back), phone islands, laptop counters, demo surface
    F.tv_wall(dp, L, 0.0, Y1 - 0.45, gz, 0, 5, 2, 2.2, 1.25, 0.12, 1.0, seed=11)
    for (x, y) in ((-3.0, 13.0), (4.0, 14.0), (-1.0, 19.5)):
        F.island(dp, L, x, y, gz, 1.3, 0.95, 'PC_WhiteGloss', 'PC_WhiteGloss', 'phones', seed=int(x * 7 + y))
    F.product_table(dp, L, 8.5, 20.5, gz, 0, 3.6, 1.0, 0.9, 'PC_WhiteGloss', 'PC_WhiteGloss', 'laptops', seed=5)
    F.product_table(dp, L, -8.5, 20.5, gz, 0, 3.6, 1.0, 0.9, 'PC_WhiteGloss', 'PC_WhiteGloss', 'tablets', seed=6)
    F.tv_wall(dp, L, X1 - 0.5, 19.0, gz, -90, 3, 2, 2.0, 1.15, 0.12, 1.1, seed=13)
    F.tv_wall(dp, L, X0 + 0.85, 19.0, gz, 90, 4, 2, 1.6, 0.9, 0.1, 1.2, seed=14)
    F.tv_wall(dp, L, X0 + 0.85, 19.0, Z[1], 90, 1, 1, 9.0, 4.0, 0.1, 0.8, seed=15)
    for (x, y) in ((9.0, 12.5), (-9.0, 13.0)):
        F.product_table(dp, L, x, y, gz, 90, 3.0, 1.1, 0.9, 'PC_WoodLight', 'PC_WhiteGloss', 'phones', seed=int(x * 3))
    F.island(dp, L, 9.0, 16.5, Z[1], 1.1, 0.95, 'PC_WhiteGloss', 'PC_WhiteGloss', 'phones', seed=9)
    F.product_table(dp, L, -9.0, 15.0, Z[1], 90, 3.2, 1.0, 0.9, 'PC_WhiteGloss', 'PC_WhiteGloss', 'laptops', seed=31)
    F.counter(fu, L, -12.0, 24.5, -6.0, 25.3, gz, 1.05, 'PC_WhiteGloss', 'PC_StoneTop', 'SS_Blue')
    # L1: exhibition + large digital demonstration surface + wearables
    F.tv_wall(dp, L, 0.0, Y1 - 0.45, Z[1], 0, 6, 2, 2.0, 1.15, 0.08, 1.0, seed=12)
    F.island(dp, L, -6.0, 16.0, Z[1], 1.1, 0.95, 'PC_WhiteGloss', 'PC_WhiteGloss', 'watches', seed=7)
    for x in (-1.0, 5.0):
        F.product_table(dp, L, x, 16.0, Z[1], 0, 3.2, 1.0, 0.9, 'PC_WoodLight', 'PC_WhiteGloss', 'mixed', seed=int(x + 20))
    for x in (-10.5, -6.0, -1.5):
        F.lounge_chair(fu, L, x, 23.5, Z[1], 180, 'PC_FabricGrey')
    F.sofa(fu, L, 8.5, 25.0, Z[1], 0, 3.0, 0.9, 'PC_FabricNavy')
    if L < 2:
        F.ring_light(fu, L, 2.0, 13.0, Z[2] - 1.2, 3.2, 0.08)
        F.ring_light(fu, L, -4.0, 18.0, Z[1] - 1.0, 2.2, 0.06)
    for x in (-10.0, 10.0):
        F.stanchion_sign(fu, L, x, 9.0, gz, 0)


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -24.0, 22.0, crossings=[(-23.0, -19.0), (17.5, 21.5)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-19.0, 0.0, 17.5, Y0)], 'PC_StoneDark', sub='Plaza')
S.asphalt(A, 'DRIVEWAY', [(-23.0, 0.0, -19.0, 2.8), (17.5, 0.0, 21.5, 2.8)])
S.asphalt(A, 'OPTIONAL_FORECOURT', [(-19.0, 0.0, 17.5, 2.8)], sub='DropOffLayBy')
for k in range(4):
    S.arrow(A, 'OPTIONAL_FORECOURT', -12.0 + k * 9.0, 1.4, 0, 2.6, sub='LayByMarks')
for x in range(-18, 18, 3):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x + 0.5, 3.1, 0.0)

for i, (x, y, z, e) in enumerate(((-2, 14, 5.0, 1800), (6, 18, 5.0, 1600), (-8, 22, 5.0, 1400), (0, 16, 10.6, 1600),
                                  (-8, 20, 10.6, 1400), (8, 20, 10.6, 1400))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#f4f8ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'PortalDown', 'SPOT', (6.0, Y0 + 0.6, Z[2] - 2.5), 800, '#ffffff', spot_deg=90)
A.light('EXTERIOR_LIGHTING', 'MediaGlow', 'POINT', (-12.0, 2.0, 5.0), 600, '#5070ff', radius=2.0)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[2] + 0.6)
A.col_box('Fascia', XG - 0.3, Y0 - 0.6, Z[2] - 1.6, X1 + 0.6, Y0, Z[2] + 0.6)
A.camera('day', (32.0, -26.0, 8.0), (-2.0, 15.0, 6.0), 28)
A.camera('night', (-34.0, -24.0, 5.0), (0.0, 16.0, 6.0), 28)
A.camera('road', (24.0, -7.6, 1.1), (-2.0, 14.0, 4.5), 24)
A.camera('interior', (-12.5, 25.5, 1.75), (6.0, 10.0, 4.2), 17)
A.checks['probes'] = [dict(name='GF_islands', p=[-3.0, 13.0, 1.3]), dict(name='GF_tvwall', p=[2.0, Y1 - 0.6, 2.0]),
                      dict(name='L1_tables', p=[1.0, 16.0, Z[1] + 1.2]), dict(name='L1_tvwall', p=[2.0, Y1 - 0.6, Z[1] + 2.0])]
S.finish(A, -24.0, 22.0, width=35.2, depth=22.6, height=12.6, footprint=[X0, Y0 - 0.7, X1 + 0.6, Y1],
         storeys=2, floor_levels=Z[:2], roof=Z[2], parking='none - short drop-off lay-by in OPTIONAL_FORECOURT',
         access='in/out crossings to a 2.8 m drop-off lay-by along the frontage (service road side)',
         setback_m=7.0, glass='two-storey PC_Glass front + recessed entrance portal', concept=__doc__.strip().split('\n')[2])
