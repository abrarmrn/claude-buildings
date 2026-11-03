"""ASSET 03 - Porsche flagship showroom (3 storeys).

Massing: narrow (30 m) minimalist stack of deep white-concrete floor bands that project 1.6 m beyond a recessed,
almost frameless glass skin -> strong horizontal lines (LED-washed underneath at night).  The third floor is a
dark graphite box SHIFTED 3 m to the left (cantilevering past the building edge) with a continuous ribbon window,
leaving a glass-railed terrace on the right.  Left half of GF+L1 is a double-height sports-car hall with a white
sculptural spiral stair; L1 right gallery and L2 lounge also show cars.
Site: direct pedestrian frontage (4 m setback, no parking), side driveway on the right to a vehicle door.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('03', '03_porsche_showroom', 'porsche_showroom', 'P03', 'PorscheShowroom', 'Porsche Flagship Showroom', 3)
defmat('PO_Letter', '#f2f2f0', 0.3, emit='#ffffff', es=4.0)
defmat('PO_Red', '#b5121b', 0.3, emit='#d0141e', es=3.0)

X0, X1, YG, Y1 = -15.0, 15.0, 5.6, 32.0          # glass line
YB = 4.0                                          # band outer edge
Z = [0.15, 5.4, 10.0, 14.6]
BOX = (-18.0, 4.8, 12.0, 31.0)                    # L2 graphite box
VOID = (-14.6, YG, -1.0, 18.0)
SPIRAL = (-7.5, 21.6)
WELL = (-9.7, 18.0, -5.3, 23.8)
ST2 = (7.9, 20.0, 9.6, 27.8)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    bands = A.m(L, 'FACADE_DETAILS', 'Bands')
    box = A.m(L, 'BUILDING_EXTERIOR', 'GraphiteBox')
    # slabs
    AR.slab_r(A, L, (X0, YG, X1, Y1), [], Z[0], 0.45, 'PC_FloorDark', 'PC_Concrete', 'PC_ConcreteWhite', sub='GroundSlab')
    AR.slab_r(A, L, (X0, YG, X1, Y1), [VOID, WELL], Z[1], 0.4, 'PC_FloorDark', 'PC_Ceiling', 'PC_ConcreteWhite')
    AR.slab_r(A, L, (X0, YG, X1, Y1), [ST2], Z[2], 0.4, 'PC_FloorOak', 'PC_Ceiling', 'PC_ConcreteWhite')
    # deep projecting white bands (roof band of the lower block = floor of the box)
    for zt, d in ((Z[1] + 0.12, 1.0), (Z[2] + 0.12, 1.0)):
        pts = [(X0 - 0.8, YB), (X1 + 0.8, YB), (X1 + 0.8, Y1 + 0.4), (X0 - 0.8, Y1 + 0.4)]
        hole = [(X0 + 0.2, YG + 0.2), (X1 - 0.2, YG + 0.2), (X1 - 0.2, Y1 - 0.2), (X0 + 0.2, Y1 - 0.2)]
        if zt < Z[2]:
            for (x0, y0, x1, y1) in rect_subtract([(X0 - 0.8, YB, X1 + 0.8, Y1 + 0.4)], (X0 + 0.2, YG + 0.2, X1 - 0.2, Y1 - 0.2)):
                AR.box(bands, x0, y0, zt - d, x1, y1, zt, 'PC_ConcreteWhite')
        else:
            AR.box(bands, X0 - 0.8, YB, zt - d, X1 + 0.8, Y1 + 0.4, zt, 'PC_ConcreteWhite', top='PC_RoofGravel')
        if L < 2:   # LED wash line under the band edge
            bands.add(bm_hquad(X0 - 0.7, YB + 0.05, X1 + 0.7, YB + 0.18, zt - d - 0.004, down=True), 'PC_LightStrip')
    AR.box(bands, X0 - 0.8, YB, -0.3, X1 + 0.8, YG, 0.12, 'PC_StoneDark')           # plinth step
    # recessed glass skin (GF + L1), slim black mullions
    for (za, zb) in ((0.12, Z[1] + 0.12 - 1.0), (Z[1] + 0.12, Z[2] + 0.12 - 1.0)):
        doors = [dict(seg=0, u0=18.0, u1=21.0, h=3.0, kind='slide')] if za < 1 else []
        AR.curtain(A, L, [(X0, YG), (X1, YG)], za, zb, 3.0, [], 0.05, 0.14, 'PC_AluBlack', 'PC_GlassClear', sub=f'Front{int(za)}',
                   doors=doors, head=False, sill=False)
        AR.curtain(A, L, [(X0, 20.0), (X0, YG)], za, zb, 3.0, [], 0.05, 0.14, 'PC_AluBlack', 'PC_GlassClear', sub=f'Left{int(za)}',
                   head=False, sill=False)
        AR.wall(ext, (X0, Y1), (X0, 20.0), za, zb, 0.3, 'PC_ConcreteWhite', 'PC_WallWhite')
        AR.wall(ext, (X1, YG), (X1, Y1), za, zb, 0.3, 'PC_ConcreteWhite', 'PC_WallWhite',
                holes=[(4.0, 10.0, 0.0, 4.2)] if za < 1 else [])
        AR.wall(ext, (X1, Y1), (X0, Y1), za, zb, 0.3, 'PC_ConcreteWhite', 'PC_WallWhite')
    AR.curtain(A, L, [(X1 - 0.02, YG + 4.0), (X1 - 0.02, YG + 10.0)], 0.12, 4.2, 3.0, [], 0.08, 0.14, 'PC_AluBlack', 'PC_GlassClear',
               sub='VehicleDoor', doors=[dict(seg=0, u0=0.0, u1=6.0, h=4.1, kind='slide')])
    # L2 graphite box with ribbon windows (front + left), glass end to the terrace
    bx0, by0, bx1, by1 = BOX
    zb0, zb1 = Z[2] + 0.12, Z[3]
    rib = (zb0 + 0.75, zb1 - 0.95)
    AR.wall(box, (bx0, by0), (bx1, by0), zb0, zb1 + 0.6, 0.3, 'PC_PanelGraphite', 'PC_WallWhite', holes=[(0.6, bx1 - bx0 - 0.6, rib[0], rib[1])])
    AR.wall(box, (bx0, by1), (bx0, by0), zb0, zb1 + 0.6, 0.3, 'PC_PanelGraphite', 'PC_WallWhite', holes=[(1.0, by1 - by0 - 0.6, rib[0], rib[1])])
    AR.wall(box, (bx1, by1), (bx0, by1), zb0, zb1 + 0.6, 0.3, 'PC_PanelGraphite', 'PC_WallWhite')
    AR.wall(box, (bx1, by0), (bx1, 14.0), zb0, zb1 + 0.6, 0.3, 'PC_PanelGraphite', 'PC_WallWhite', holes=[(0.6, 9.2 - 0.6, zb0, zb1 - 0.4)])
    AR.wall(box, (bx1, 14.0), (bx1, by1), zb0, zb1 + 0.6, 0.3, 'PC_PanelGraphite', 'PC_WallWhite')
    AR.curtain(A, L, [(bx0 + 0.6, by0 + 0.1), (bx1 - 0.6, by0 + 0.1)], rib[0], rib[1], 2.4, [], 0.04, 0.12, 'PC_AluBlack', 'PC_GlassClear',
               sub='Ribbon', head=False, sill=False)
    AR.curtain(A, L, [(bx0 + 0.1, by1 - 0.6), (bx0 + 0.1, by0 + 1.0)], rib[0], rib[1], 2.4, [], 0.04, 0.12, 'PC_AluBlack', 'PC_GlassClear',
               sub='RibbonL', head=False, sill=False)
    AR.curtain(A, L, [(bx1 + 0.1, by0 + 0.6), (bx1 + 0.1, 13.4)], zb0, zb1 - 0.4, 2.2, [], 0.05, 0.12, 'PC_AluBlack', 'PC_GlassClear',
               sub='TerraceGlass', doors=[dict(seg=0, u0=5.0, u1=7.6, h=2.6, kind='slide')], head=False)
    AR.box(box, bx0, by0, zb1 + 0.3, bx1, by1, zb1 + 0.6, 'PC_PanelGraphite', top='PC_RoofGravel')
    AR.box(box, bx0, by0, zb0 - 0.02, X0 - 0.8, by1, zb0 + 0.02, 'PC_PanelGraphite')       # soffit of the cantilever
    if L < 2:
        box.add(bm_hquad(bx0 + 0.3, by0 + 0.3, X0 - 1.0, by1 - 0.3, Z[2] + 0.12 - 1.01, down=True), 'PC_PanelGraphite')
        AR.downlights(box, L, [(-16.6, y) for y in range(7, 31, 3)], Z[2] + 0.12 - 1.0, 0.1, 'PC_LightWarm')
    # terrace glass rail on the right
    AR.glass_rail(A, L, [(bx1 + 0.2, by0 + 0.0), (X1 + 0.6, YB + 0.2), (X1 + 0.6, Y1)], Z[2] + 0.12, 1.1, comp='FACADE_DETAILS',
                  sub='TerraceRail')
    # signage
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'P O R S C H E', place('-Y', Vector((-3.0, by0 - 0.02, zb1 - 0.45))), 0.62, 0.06, 'dsemi', 'PO_Letter', 'PC_AluSilver', spacing=1.5)
    AR.box(sg, -26.0, 1.0, 0.0, -21.0, 1.6, 2.6, 'PC_PanelGraphite')
    if L < 2:
        txt(sg, L, 'PORSCHE', place('-Y', Vector((-23.5, 0.98, 1.5))), 0.48, 0.03, 'dsemi', 'PO_Letter', 'PC_AluSilver', spacing=1.3)
        sg.add(bm_box(-25.6, 0.97, 0.5, -21.4, 1.0, 0.56), 'PO_Red')
    A.sign('box_wordmark', (-3.0, by0 - 0.1, zb1 - 0.45), 0.62, width=12.0)
    A.sign('monolith', (-23.5, 0.9, 1.5), 0.48, width=4.0)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Platforms')
    st = A.m(L, 'BUILDING_INTERIOR', 'Partitions')
    AR.spiral_stair(A, L, SPIRAL[0], SPIRAL[1], 0.28, 1.95, Z[0], Z[1], a0=200.0, sweep=320.0)
    AR.stair(A, L, 8.75, ST2[1], 90, 1.5, Z[1], Z[2], 'floating', 'PC_FloorOak', 'PC_SteelDark', sub='UpperStair', max_flight=5.0)
    AR.glass_rail(A, L, [(VOID[0], VOID[3]), (WELL[0], VOID[3]), (WELL[0], WELL[3]), (WELL[2], WELL[3]), (WELL[2], VOID[3]),
                         (VOID[2], VOID[3]), (VOID[2], YG + 0.3)], Z[1])
    AR.glass_rail(A, L, [(ST2[0], ST2[3]), (ST2[0], ST2[1]), (ST2[2], ST2[1]), (ST2[2], ST2[3])], Z[2], sub='Rail2')
    # ceilings
    AR.ceiling_panels(A, L, rect_subtract([(X0 + 0.4, YG + 0.4, X1 - 0.4, Y1 - 0.4)], VOID), Z[1] - 0.4, (2.8, 2.4), w=2.2, d=0.12,
                      lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.4, YG + 0.4, X1 - 0.4, Y1 - 0.4)], Z[2] - 0.4, (2.8, 2.4), w=2.2, d=0.12, lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(BOX[0] + 0.5, BOX[1] + 0.5, BOX[2] - 0.5, BOX[3] - 0.5)], Z[3] + 0.3, (3.0, 2.6), mat='PC_LightWarm',
                      w=2.2, d=0.12, lod2_glow='PC_LightWarm')
    # GF: double-height sports-car hall (dark), red accent wall, reception + lounge
    AR.box(st, X0 + 0.3, Y1 - 0.6, Z[0], 0.0, Y1 - 0.3, Z[2] - 0.4, 'PC_PanelBlack')
    if L < 2:
        AR.box(st, X0 + 1.0, Y1 - 0.62, 3.0, -1.0, Y1 - 0.6, 3.08, 'PO_Red')
        AR.box(st, X0 + 1.0, Y1 - 0.62, 8.0, -1.0, Y1 - 0.6, 8.08, 'PO_Red')
    F.plinth(dp, L, -14.0, 7.6, -8.0, 13.2, Z[0], 0.12, 'PC_BlackGloss', 'PC_AluBlack', 'PC_LightStrip')
    F.plinth(dp, L, -7.2, 10.2, -1.6, 15.6, Z[0], 0.12, 'PC_BlackGloss', 'PC_AluBlack', 'PC_LightStrip')
    F.turntable(dp, L, 7.5, 11.5, Z[0], 2.8, 0.12, 'PC_FloorMarble', 'PC_AluBlack')
    F.reception_desk(fu, L, 6.0, 24.0, Z[0], 180, 2.4, 'PC_PanelBlack', 'PC_StoneTop', 'PC_LightStrip')
    F.lounge_group(fu, L, 10.5, 27.5, Z[0], 0, 'PC_LeatherBlack', 'PC_Leather')
    F.tv_wall(fu, L, 9.0, Y1 - 0.45, Z[0], 0, 3, 2, 1.5, 0.85, seed=3)
    # L1: right gallery
    F.plinth(dp, L, 2.5, 7.6, 8.8, 13.0, Z[1], 0.12, 'PC_FloorMarble', 'PC_AluBlack')
    F.plinth(dp, L, 9.6, 12.0, 14.3, 18.6, Z[1], 0.12, 'PC_FloorMarble', 'PC_AluBlack')
    F.desk(fu, L, 4.0, 25.0, Z[1], 0, 1.6, 0.8)
    F.desk(fu, L, 0.0, 25.0, Z[1], 0, 1.6, 0.8)
    F.wall_shelf(fu, L, -6.0, Y1 - 0.65, Z[1], 0, 6.0, 2.6, 4, 'PC_PanelBlack', 'PC_WoodLight')
    # L2: lounge + display car (seen through the ribbon window)
    F.plinth(dp, L, -16.8, 7.0, -10.2, 12.6, Z[2] + 0.12, 0.1, 'PC_FloorDark', 'PC_AluBlack')
    F.lounge_group(fu, L, -4.5, 11.0, Z[2] + 0.12, 0, 'PC_LeatherCream', 'PC_LeatherBlack')
    F.lounge_group(fu, L, 3.0, 11.0, Z[2] + 0.12, 0, 'PC_FabricGrey', 'PC_Leather')
    F.counter(fu, L, -12.0, 26.0, -4.0, 27.0, Z[2] + 0.12, 1.1, 'PC_PanelBlack', 'PC_StoneTop', 'PO_Red')
    if L < 2:
        for x in (-11.0, -9.5, -8.0, -6.5, -5.0):
            F.stool(fu, L, x, 25.3, Z[2] + 0.12)
        for x in (-4.5, 3.0):
            F.pendant(fu, L, x, 11.0, Z[3] + 0.3, 1.0, 'cone', 0.35, 'PC_LampGlobe', 'PC_AluBlack')
        F.ring_light(fu, L, -8.0, 12.0, Z[1] + 3.6, 3.0, 0.1)


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'coupe', -11.0, 10.4, Z[0] + 0.12, 155, 'PC_CarPaintRed', 'GF double-height hall')
CARS.add_car(A, 2, 'coupe', -4.4, 12.9, Z[0] + 0.12, 205, 'PC_CarPaintSilver', 'GF double-height hall')
CARS.add_car(A, 3, 'coupe', 7.5, 11.5, Z[0] + 0.12, 180, 'PC_CarPaintYellow', 'GF turntable')
CARS.add_car(A, 4, 'crossover', 5.65, 10.3, Z[1] + 0.12, 170, 'PC_CarPaintGraphite', 'L1 gallery')
CARS.add_car(A, 5, 'coupe', 11.95, 15.3, Z[1] + 0.12, 200, 'PC_CarPaintWhite', 'L1 gallery')
CARS.add_car(A, 6, 'coupe', -13.5, 9.8, Z[2] + 0.22, 180, 'PC_CarPaintBlack', 'L2 lounge (ribbon window)')

S.sidewalk(A, -27.0, 24.0, crossings=[(16.5, 22.5)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-27.0, 0.0, 16.5, YB)], 'PC_StoneSand', sub='Frontage')
S.asphalt(A, 'DRIVEWAY', [(16.5, 0.0, 22.5, 20.0)])
S.arrow(A, 'DRIVEWAY', 19.5, 8.0, 90)
for x in (-14.0, -6.0, 2.0, 10.0):
    F.bench(A.s('OPTIONAL_FORECOURT', 'Furniture'), 0, x, 1.6, 0.0, 0, 2.2, 'PC_Walnut', 'PC_ConcreteWhite')

for i, (x, y, z, e) in enumerate(((-8, 11, 9.0, 3000), (7, 12, 4.6, 1600), (6, 25, 4.6, 1200), (6, 12, 9.2, 1600),
                                  (-6, 26, 9.2, 1200), (-12, 10, 13.8, 1400), (0, 12, 13.8, 1400), (-6, 25, 13.8, 1000))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#fff4ea', radius=1.0)
for i, x in enumerate((-11.0, -4.4)):
    A.light('INTERIOR_LIGHTING', f'CarSpot{i}', 'SPOT', (x, 8.0, 8.8), 1500, '#ffffff', rot=(25, 0, 0), spot_deg=45)
A.light('EXTERIOR_LIGHTING', 'MonolithWash', 'SPOT', (-23.5, -2.0, 0.2), 500, '#fff1e0', rot=(-70, 0, 0), spot_deg=40)
A.light('EXTERIOR_LIGHTING', 'BoxUplight', 'SPOT', (-16.6, 2.0, 0.2), 1600, '#fff1e0', rot=(-82, 0, 0), spot_deg=20)
A.col_box('Lower', X0 - 0.8, YB, 0, X1 + 0.8, Y1 + 0.4, Z[2] + 0.12)
A.col_box('Box', BOX[0], BOX[1], Z[2] + 0.12, BOX[2], BOX[3], Z[3] + 0.6)
A.col_box('Monolith', -26.0, 1.0, 0.0, -21.0, 1.6, 2.6)
A.camera('day', (-40.0, -28.0, 9.0), (-2.0, 16.0, 7.0), 28)
A.camera('night', (-34.0, -24.0, 4.0), (-1.0, 16.0, 7.0), 28)
A.camera('road', (-26.0, -7.6, 1.1), (0.0, 14.0, 5.5), 24)
A.camera('interior', (1.5, 27.0, 1.6), (-10.0, 8.0, 6.0), 16)
A.checks['probes'] = [dict(name='GF_hall', p=[-8.0, 14.0, 1.2]), dict(name='GF_right', p=[7.5, 13.5, 1.2]),
                      dict(name='L1_gallery', p=[6.0, 12.5, Z[1] + 1.0]), dict(name='L2_lounge', p=[-6.0, 9.0, Z[2] + 1.3])]
S.finish(A, -27.0, 24.0, width=33.0, depth=28.0, height=15.2, footprint=[BOX[0], YB, X1 + 0.8, Y1 + 0.4],
         storeys=3, floor_levels=Z[:3], roof=Z[3], parking='none (direct pedestrian frontage)',
         access='right side driveway from the service road to a glazed vehicle door; no front parking',
         setback_m=4.0, glass='frameless-look PC_GlassClear alpha 0.11', concept=__doc__.strip().split('\n')[2])
