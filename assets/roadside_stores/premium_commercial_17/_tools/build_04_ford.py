"""ASSET 04 - Ford showroom (1 storey, wide horizontal).

Massing: a 64 m wide, low (7.8 m) industrial clear-span hall with an exposed dark-steel portal frame in front of a
36 m display glazing, a SAWTOOTH north-light roof (three teeth rising to 10.3 m) and a projecting blue entrance
portal (10.8 m) carrying the oval sign.  Dark profiled-metal end blocks: parts/service reception on the left,
vehicle delivery bay + two service roller doors on the right (service zone visible through a glass partition).
Site: wide paved forecourt, a direct service apron for the right zone, optional left-side customer parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('04', '04_ford_showroom', 'ford_showroom', 'P04', 'FordShowroom', 'Ford Showroom', 1)
defmat('FD_Blue', '#133a7c', 0.3, 0.3)
defmat('FD_OvalBlue', '#1a3f8f', 0.25, 0.2, emit='#2050b0', es=1.6)
defmat('FD_Letter', '#ffffff', 0.3, emit='#ffffff', es=4.0)

X0, X1, Y0, Y1 = -32.0, 32.0, 10.0, 34.0
ZF = 0.15
ZE = 7.8                                   # eaves
TEETH = [(10.0, 18.0), (18.0, 26.0), (26.0, 34.0)]
ZT = 10.3


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    roof = A.m(L, 'BUILDING_EXTERIOR', 'SawtoothRoof')
    stl = A.m(L, 'FACADE_DETAILS', 'SteelFrame')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], ZF, 0.45, 'PC_FloorEpoxy', 'PC_Concrete', 'PC_Concrete', sub='GroundSlab')
    # sawtooth roof: sloped plates rising towards the rear of each tooth + vertical north-light glazing
    for (ya, yb) in TEETH:
        roof.add(AR.bm_yz_prism([(ya, ZE), (yb, ZT), (yb, ZT + 0.35), (ya - 0.4, ZE + 0.35)], X0 - 0.4, X1 + 0.4), 'PC_Corrugated',
                 mat_fn=lambda f: 'PC_Ceiling' if f.normal.z < -0.3 else 'PC_Corrugated')
        if yb < Y1:
            AR.curtain(A, L, [(X1, yb), (X0, yb)], ZE + 0.35, ZT, 3.2, [], 0.06, 0.15, 'PC_AluDark', 'PC_GlassClear', sub='NorthLight')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, ZT + 0.35, 0.3, 'PC_Corrugated', 'PC_WallWhite', holes=[(44.0, 50.0, 0.0, 4.5)])
    # gable ends follow the sawtooth profile
    for x, s in ((X0, -1), (X1, 1)):
        for (ya, yb) in TEETH:
            ext.add(AR.bm_yz_prism([(ya, 0.0), (yb, 0.0), (yb, ZT), (ya, ZE)], x - 0.3 if s > 0 else x, x if s > 0 else x + 0.3),
                    'PC_Corrugated', mat_fn=lambda f, s=s: 'PC_Corrugated' if f.normal.x * s > 0.5 else 'PC_WallWhite')
    # front: left block (corrugated + clerestory), display glazing, portal, right service zone
    AR.wall(ext, (X0, Y0), (-20.0, Y0), 0.0, ZE + 0.35, 0.3, 'PC_Corrugated', 'PC_WallWhite', holes=[(1.0, 11.0, 5.2, 6.8), (4.0, 6.5, 0.0, 2.6)])
    AR.curtain(A, L, [(X0 + 1.0, Y0 - 0.02), (X0 + 11.0, Y0 - 0.02)], 5.2, 6.8, 2.5, [], 0.06, 0.12, 'PC_AluDark', 'PC_GlassClear', sub='Clerestory')
    AR.curtain(A, L, [(X0 + 4.0, Y0 - 0.02), (X0 + 6.5, Y0 - 0.02)], 0.0, 2.6, 2.5, [], 0.06, 0.12, 'PC_AluDark', 'PC_GlassClear',
               sub='PartsDoor', doors=[dict(seg=0, u0=0.0, u1=2.5, h=2.5, kind='pivot', leaves=1)])
    for (xa, xb) in ((-20.0, -5.0), (5.0, 16.0)):
        AR.curtain(A, L, [(xa, Y0), (xb, Y0)], 0.0, ZE, 3.75 if xa < 0 else 3.67, [4.6], 0.08, 0.25, 'PC_AluBlack', 'PC_Glass', sub=f'Display{int(xa)}')
    AR.box(ext, -20.0, Y0, ZE, 16.0, Y0 + 0.3, ZE + 0.35, 'PC_Corrugated')
    # right zone: delivery bay (glazed sectional door, raised) + 2 service roller doors
    AR.wall(ext, (16.0, Y0), (X1, Y0), 0.0, ZE + 0.35, 0.3, 'PC_Corrugated', 'PC_WallWhite',
            holes=[(1.0, 7.0, 0.0, 4.8), (8.5, 12.0, 0.0, 4.5), (12.5, 15.5, 0.0, 4.5)])
    M, _ = seg_frame((16.0, Y0), (X1, Y0))
    AR.roller_door(ext, L, M, 1.0, 7.0, 4.8, 0.85, 'PC_GlassBlue')
    AR.roller_door(ext, L, M, 8.5, 12.0, 4.5, 1.0)
    AR.roller_door(ext, L, M, 12.5, 15.5, 4.5, 0.45)
    # glass partition between showroom and service zone
    AR.curtain(A, L, [(16.0, Y1 - 0.3), (16.0, Y0 + 0.3)], ZF, 5.5, 2.6, [2.4], 0.06, 0.12, 'PC_AluDark', 'PC_GlassClear', sub='Partition')
    AR.box(ext, 15.9, Y0 + 0.3, 5.5, 16.1, Y1 - 0.3, ZE, 'PC_WallWhite')
    # partition to parts block
    AR.wall(ext, (-20.0, Y0), (-20.0, Y1), ZF, ZE, 0.2, 'PC_WallWhite', 'PC_WallWhite', holes=[(14.0, 16.0, 0.0, 2.6)])
    # exposed steel portal frame in front of the display glazing
    for x in (-20.0, -12.0, 8.5, 16.0):
        AR.box(stl, x - 0.2, Y0 - 1.6, 0.0, x + 0.2, Y0 - 1.2, ZE + 0.6, 'PC_SteelDark')
        AR.box(stl, x - 0.06, Y0 - 1.2, ZE - 0.2, x + 0.06, Y0, ZE + 0.4, 'PC_SteelDark')
    AR.ibeam(stl, (-20.4, Y0 - 1.4, ZE + 1.0), (16.4, Y0 - 1.4, ZE + 1.0), 0.7, 0.4, mat='PC_SteelDark', L=L)
    # blue portal
    pr = (-5.0, Y0 - 3.5, 5.0, Y0 + 0.2)
    AR.wall(ext, (pr[0], pr[1]), (pr[2], pr[1]), 0.0, 10.8, 0.45, 'FD_Blue', 'PC_WallWhite', holes=[(1.6, 8.4, 0.0, 6.4)])
    AR.wall(ext, (pr[2], pr[1]), (pr[2], Y0), 0.0, 10.8, 0.45, 'FD_Blue', 'FD_Blue')
    AR.wall(ext, (pr[0], Y0), (pr[0], pr[1]), 0.0, 10.8, 0.45, 'FD_Blue', 'FD_Blue')
    AR.box(ext, pr[0], pr[1], 10.4, pr[2], Y0, 10.8, 'FD_Blue')
    AR.box(ext, pr[0] + 0.45, pr[1] + 0.45, 6.4, pr[2] - 0.45, Y0, 6.7, 'PC_Ceiling')
    AR.curtain(A, L, [(pr[0] + 1.6, Y0 - 0.5), (pr[2] - 1.6, Y0 - 0.5)], 0.0, 6.4, 2.27, [4.0], 0.07, 0.16, 'PC_AluBlack', 'PC_Glass',
               sub='Entrance', doors=[dict(seg=0, u0=1.9, u1=4.9, h=3.2, kind='slide')])
    if L < 2:
        AR.downlights(ext, L, [(x, y) for x in (-2.5, 0.0, 2.5) for y in (Y0 - 2.4, Y0 - 1.0)], 6.4, 0.12, 'PC_LightPanel')
    # signage
    sg = A.m(L, 'SIGNAGE', 'Brand')
    oval(sg, L, place('-Y', Vector((0.0, pr[1] - 0.02, 8.5))), 3.7, 1.5)
    if L < 2:
        txt(sg, L, 'SERVICE', place('-Y', Vector((24.0, Y0 - 0.05, 6.3))), 0.6, 0.06, 'dsemi', 'FD_Letter', 'PC_AluSilver', spacing=1.1)
        txt(sg, L, 'PARTS & SERVICE RECEPTION', place('-Y', Vector((-26.0, Y0 - 0.05, 3.6))), 0.34, 0.04, 'dsemi', 'FD_Letter', 'PC_AluSilver')
    A.sign('portal_oval', (0.0, pr[1] - 0.1, 8.5), 3.0, width=7.4)
    interior(L)


def oval(acc, L, M, a, b):
    """Generic blue oval badge with white script-style lettering (simplified recreation, not official artwork)."""
    seg = {0: 64, 1: 32, 2: 16}[L]
    outer = [(a * math.cos(2 * math.pi * i / seg), b * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    inner = [(0.94 * x, 0.90 * y) for (x, y) in outer]
    acc.add(R.bm_ring_prism(outer, inner, 0.0, 0.2), 'PC_Chrome', matrix=M)
    poly(acc, inner, 0.16, M, 'FD_OvalBlue')
    txt(acc, L, 'Ford', M @ Matrix.Translation((0, -0.08, 0.16)), 1.75, 0.05, 'serif_bi', 'FD_Letter', 'FD_Letter', min_size_lod2=0.2)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Platforms')
    st = A.m(L, 'BUILDING_INTERIOR', 'Structure')
    # exposed clear-span steel: rafters under each tooth + purlins
    for x in range(-24, 25, 8):
        for (ya, yb) in TEETH:
            AR.box(st, x - 0.15, ya, ZE - 0.5, x + 0.15, yb, ZE, 'PC_SteelDark') if L == 2 else \
                st.add(AR.bm_yz_prism([(ya, ZE - 0.55), (yb, ZT - 0.55), (yb, ZT), (ya, ZE)], x - 0.12, x + 0.12), 'PC_SteelDark')
    if L == 0:
        for (ya, yb) in TEETH:
            for k in (0.25, 0.5, 0.75):
                y = ya + (yb - ya) * k; z = ZE + (ZT - ZE) * k
                AR.box(st, X0 + 0.3, y - 0.08, z - 0.25, X1 - 0.3, y + 0.08, z, 'PC_SteelPaintGrey')
    # high-bay linear lights
    for (ya, yb) in TEETH:
        F.ceiling_strip_lights(fu, L, (-19.0, ya + 1.0, 15.0, yb - 1.0), ZE - 0.8, 2, 'x', 0.2, 'PC_LightCool', 'PC_AluDark', length=30.0)
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_hquad(-19.0, Y0 + 1, 15.0, Y1 - 1, ZE - 0.9, down=True), 'PC_LightCool')
    # back wall graphics + screens
    AR.box(st, -19.5, Y1 - 0.6, ZF, 15.5, Y1 - 0.3, 5.5, 'PC_PanelGraphite')
    if L < 2:
        AR.box(st, -19.5, Y1 - 0.62, 4.2, 15.5, Y1 - 0.6, 4.35, 'FD_OvalBlue')
    F.tv_wall(fu, L, -2.0, Y1 - 0.65, ZF, 0, 4, 1, 2.0, 1.15, 0.15, 1.8, seed=4)
    # display platforms (wide, low)
    for (x0, y0, x1, y1) in ((-18.5, 13.5, -11.5, 20.0), (-9.5, 19.0, -3.0, 25.0), (6.0, 13.5, 13.0, 20.0), (-18.5, 23.5, -11.5, 29.5),
                             (6.0, 23.0, 13.0, 29.0)):
        F.plinth(dp, L, x0, y0, x1, y1, ZF, 0.12, 'PC_FloorEpoxyDark', 'PC_AluDark', 'PC_LightStrip')
    F.reception_desk(fu, L, 0.0, 15.2, ZF, 180, 2.6, 'PC_PanelWhite', 'PC_StoneTop', 'PC_LEDBlue', curved=False)
    for x in (-1.5, 2.0):
        F.desk(fu, L, x, 29.5, ZF, 0, 1.6, 0.8)
    for x in (8.0, 12.0):
        F.desk(fu, L, x, 31.5, ZF, 0, 1.6, 0.8)
    F.lounge_group(fu, L, -7.0, 30.0, ZF, 0, 'PC_FabricNavy', 'PC_LeatherBlack')
    for x in (-15.0, -8.0):
        F.pendant(fu, L, x, 31.0, ZE - 0.5, 1.6, 'cone', 0.4, 'PC_LampGlobe', 'PC_AluBlack')
    # parts block (left): counter + shelving
    F.counter(fu, L, -30.0, 16.0, -24.0, 16.8, ZF, 1.05, 'PC_PanelGraphite', 'PC_StoneTop', 'PC_LEDBlue')
    for y in (21.0, 25.0, 29.0):
        F.wall_shelf(fu, L, -26.0, y, ZF, 0, 9.0, 2.6, 4, 'PC_SteelPaintGrey', 'PC_SteelPaintGrey', seed=int(y))
    # service zone (right): lift, tool cabinets, delivery bay
    F.lift_2post(fu, L, 26.0, 22.0, ZF, 90, 1.5, 3.4)
    F.tool_cabinet(fu, L, 30.8, 18.0, ZF, -90, 1.6)
    F.tool_cabinet(fu, L, 30.8, 26.5, ZF, -90, 1.6, mat='PC_ToolBlack')
    F.workbench(fu, L, 25.0, 32.8, ZF, 180, 3.0)
    F.ceiling_strip_lights(fu, L, (17.0, 12.0, 31.0, 32.0), ZE - 0.8, 3, 'y', 0.2, 'PC_LightCool', 'PC_AluDark', length=18.0)
    F.tyre_rack(fu, L, 20.0, 32.9, ZF, 0, 3.0)


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'pickup', -15.0, 16.75, ZF + 0.12, 160, 'PC_CarPaintBlue', 'display platform')
CARS.add_car(A, 2, 'suv', -6.25, 22.0, ZF + 0.12, 200, 'PC_CarPaintWhite', 'display platform')
CARS.add_car(A, 3, 'coupe', 9.5, 16.75, ZF + 0.12, 200, 'PC_CarPaintOrange', 'display platform')
CARS.add_car(A, 4, 'crossover', -15.0, 26.5, ZF + 0.12, 180, 'PC_CarPaintGraphite', 'display platform')
CARS.add_car(A, 5, 'sedan', 9.5, 26.0, ZF + 0.12, 180, 'PC_CarPaintSilver', 'display platform')
CARS.add_car(A, 6, 'pickup', 20.0, 18.0, ZF, 90, 'PC_CarPaintBlack', 'vehicle delivery bay')
CARS.add_car(A, 7, 'suv', 26.0, 22.0, ZF + 1.5 + 0.05, 90, 'PC_CarPaintRed', 'service lift (raised)')

S.sidewalk(A, -47.0, 36.0, crossings=[(-46.0, -39.0), (17.0, 31.0)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-39.0, 0.0, 17.0, Y0)], 'PC_PaverLight', sub='Plaza')
S.asphalt(A, 'DRIVEWAY', [(17.0, 0.0, 31.0, Y0)])
S.arrow(A, 'DRIVEWAY', 20.0, 5.0, 90); S.arrow(A, 'DRIVEWAY', 27.0, 5.0, 90)
S.asphalt(A, 'OPTIONAL_PARKING', [(-46.0, 0.0, -39.0, 36.0), (-39.0, 12.0, -33.0, 36.0)])
S.bays(A, -38.9, 12.0, 9, 2.6, 5.6, 1, along='y')
for x in (-36.0, -26.0, -16.0, 6.0, 14.0):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 1.0, 0.0)

for i, (x, y, z, e) in enumerate(((-14, 18, 7.0, 2600), (-6, 22, 7.0, 2600), (9, 18, 7.0, 2600), (-12, 28, 7.0, 2000),
                                  (8, 28, 7.0, 2000), (24, 20, 7.0, 1800), (-26, 22, 7.0, 1200))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#f6f8ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'OvalWash', 'SPOT', (0.0, 0.0, 0.2), 900, '#e8f0ff', rot=(-72, 0, 0), spot_deg=24)
A.light('EXTERIOR_LIGHTING', 'ServiceApron', 'SPOT', (24.0, 8.0, 7.6), 1600, '#f0f4ff', rot=(0, 0, 0), spot_deg=100)
A.col_box('Hall', X0, Y0, 0, X1, Y1, ZT + 0.35)
A.col_box('Portal', -5.0, Y0 - 3.5, 0, 5.0, Y0, 10.8)
for i, x in enumerate((-20.0, -12.0, 8.5, 16.0)):
    A.col_box(f'Column{i}', x - 0.2, Y0 - 1.6, 0, x + 0.2, Y0 - 1.2, ZE + 1.0)
A.camera('day', (-30.0, -40.0, 12.0), (0.0, 20.0, 3.0), 26)
A.camera('night', (40.0, -30.0, 6.0), (-4.0, 20.0, 4.0), 26)
A.camera('road', (-20.0, -7.6, 1.1), (-3.0, 18.0, 2.8), 24)
A.camera('interior', (13.5, 31.5, 1.7), (-14.0, 14.0, 3.6), 16)
A.checks['probes'] = [dict(name='Hall_left', p=[-15.0, 20.0, 1.2]), dict(name='Hall_right', p=[9.0, 20.0, 1.2]),
                      dict(name='Reception', p=[0.0, 16.0, 1.2])]
S.finish(A, -47.0, 36.0, width=64.0, depth=24.0, height=10.8, footprint=[X0, Y0 - 3.5, X1, Y1],
         storeys=1, floor_levels=[ZF], roof='sawtooth, eaves 7.8 m, ridges 10.3 m, portal 10.8 m',
         parking='optional left-side customer lot, 9 bays + access aisle (OPTIONAL_PARKING)',
         access='direct service apron from the service road to delivery bay + 2 service doors; separate parking crossing on the left',
         setback_m=10.0, glass='36 m display glazing PC_Glass alpha 0.16 + north lights', concept=__doc__.strip().split('\n')[2])
