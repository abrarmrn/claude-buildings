"""ASSET 06 - Apple flagship store (2 storeys).

Massing: pure minimalist pavilion - five 5.6 m x 9.4 m frameless glass panes stabilised by internal glass fins, held
between two thick travertine flank walls and capped by a razor-thin white roof plate cantilevering 2.5 m on all sides.
Inside: a 9.4 m double-height hall under a luminous backlit ceiling, rows of light-oak product tables (iPhone, Mac,
iPad zones), twin stone stairs with glass balustrades rising to a rear mezzanine with more tables and a video wall.
Site: open stone plaza directly off the pavement (pedestrian only, no parking, no vehicle access).
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('06', '06_apple_flagship', 'apple_flagship', 'P06', 'AppleFlagship', 'Apple Flagship Store', 2)
defmat('AP_Lumi', '#ffffff', 0.4, emit='#fff6ea', es=2.6)
SPECIAL_MATS['AP_Logo'] = lambda: mat_logo('AP_Logo', apple_logo_png(), 5.0)

X0, X1, Y0, Y1 = -14.0, 14.0, 6.0, 32.0
ZG, ZM, ZC = 0.15, 5.0, 9.6
YM = 18.0


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'RoofPlate')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], ZG, 0.45, 'PC_Travertine', 'PC_Concrete', 'PC_Travertine', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.6, YM, X1 - 0.6, Y1 - 0.6), [], ZM, 0.4, 'PC_Travertine', 'PC_WoodLight', 'PC_Travertine', sub='Mezzanine')
    # travertine flanks (proud of the glass) + back wall
    for s in (-1, 1):
        x = s * X1
        AR.box(ext, min(x, x + s * 0.7), Y0 - 0.6, 0.0, max(x, x + s * 0.7), Y1, ZC, 'PC_Travertine')
    AR.box(ext, X0, Y1 - 0.6, 0.0, X1, Y1, ZC, 'PC_Travertine')
    AR.box(ext, X0, Y0, ZC - 0.05, X1, Y1, ZC + 0.3, 'PC_Ceiling', top='PC_RoofGravel')
    # roof plate
    det.add(bm_prism(rounded_rect(X0 - 2.5, Y0 - 2.5, X1 + 2.5, Y1 + 2.0, 0.6, 4 if L == 0 else 1), ZC + 0.3, ZC + 0.85), 'PC_PanelWhite')
    if L < 2:
        AR.downlights(det, L, [(x, Y0 - 1.3) for x in range(-15, 16, 2)], ZC + 0.3, 0.08, 'PC_LightWarm')
    # frameless glass: 5 panes, glass fins inside, slim head/sill channels
    n = 5
    w = (X1 - X0) / n
    g = A.m(L, 'GLASS_SYSTEM', 'Panes')
    fr = A.m(L, 'GLASS_SYSTEM', 'Fins')
    for i in range(n):
        xa, xb = X0 + i * w + 0.01, X0 + (i + 1) * w - 0.01
        if i == n // 2 and L < 2:
            g.add(bm_vquad(xa, xb, 3.4, ZC - 0.05, Y0, '-Y'), 'PC_GlassClear')
            AR.door(A, L, Matrix.Translation((0, Y0, 0)), dict(u0=xa + 1.0, u1=xb - 1.0, h=3.4, kind='pivot', leaves=2), 'PC_Stainless',
                    'PC_GlassClear', 'GLASS_SYSTEM', 'Door')
            g.add(bm_vquad(xa, xa + 1.0, 0.0, 3.4, Y0, '-Y'), 'PC_GlassClear')
            g.add(bm_vquad(xb - 1.0, xb, 0.0, 3.4, Y0, '-Y'), 'PC_GlassClear')
        else:
            g.add(bm_vquad(xa, xb, 0.0, ZC - 0.05, Y0, '-Y'), 'PC_GlassClear')
        if i > 0:
            x = X0 + i * w
            fr.add(bm_box(x - 0.02, Y0, 0.0, x + 0.02, Y0 + 0.75, ZC - 0.05), 'PC_GlassRail')
    if L < 2:
        fr.add(bm_box(X0, Y0 - 0.03, ZC - 0.12, X1, Y0 + 0.08, ZC), 'PC_Stainless')
        fr.add(bm_box(X0, Y0 - 0.03, 0.0, X1, Y0 + 0.08, 0.06), 'PC_Stainless')
    # signage: illuminated logo suspended just inside the glass + a small one on the left flank
    sg = A.m(L, 'SIGNAGE', 'Brand')
    decal(sg, place('-Y', Vector((0.0, Y0 + 0.35, 6.9))), 1.9, 1.9, 'AP_Logo')
    if L < 2:
        sg.add(bm_box(-0.01, Y0 + 0.36, 7.9, 0.01, Y0 + 0.38, ZC), 'PC_Stainless')
    decal(sg, place('-Y', Vector((X0 - 0.35, Y0 - 0.62, 6.0))), 1.0, 1.0, 'AP_Logo')
    A.sign('logo', (0.0, Y0 + 0.2, 6.9), 1.9, width=1.9)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Products')
    lum = A.m(L, 'BUILDING_INTERIOR', 'LuminousCeiling')
    # luminous ceilings (backlit panels) over the hall and under the mezzanine
    if L < 2:
        AR.light_grid(lum, L, (X0 + 0.8, Y0 + 0.4, X1 - 0.8, Y1 - 0.8), ZC - 0.05, 9 if L == 0 else 3, 8 if L == 0 else 3,
                      2.75 if L == 0 else 8.0, 2.85 if L == 0 else 8.0, 'AP_Lumi')
        AR.light_grid(lum, L, (X0 + 0.8, YM + 0.4, X1 - 0.8, Y1 - 0.8), ZM - 0.4, 9 if L == 0 else 3, 4 if L == 0 else 2,
                      2.75 if L == 0 else 8.0, 2.85 if L == 0 else 5.6, 'AP_Lumi')
    else:
        lum.add(bm_hquad(X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5, ZC - 0.1, down=True), 'AP_Lumi')
    # twin stone stairs with glass balustrades + mezzanine balustrade
    for x in (-10.6, 10.6):
        AR.stair(A, L, x, YM - 8.4, 90, 1.8, ZG, ZM, 'solid', 'PC_Travertine', 'PC_Travertine', sub=f'Stair{int(x)}', max_flight=6.0,
                 rails=(True, True))
    AR.glass_rail(A, L, [(X0 + 0.7, YM), (-11.5, YM)], ZM, sub='RailA')
    AR.glass_rail(A, L, [(-9.7, YM), (9.7, YM)], ZM, sub='RailB')
    AR.glass_rail(A, L, [(11.5, YM), (X1 - 0.7, YM)], ZM, sub='RailC')
    # product tables (hall): front row iPhone, then iPad, Mac, accessories
    rows = [(9.8, 'phones'), (13.6, 'tablets')]
    for (y, items) in rows:
        for x in (-5.4, 0.0, 5.4):
            F.product_table(dp, L, x, y, ZG, 0, 4.4, 1.15, 0.86, 'PC_WoodLight', 'PC_WoodLight', items, seed=int(x * 10 + y))
    for x in (-5.4, 0.0, 5.4):
        F.product_table(dp, L, x, 16.6, ZG, 0, 4.4, 1.15, 0.86, 'PC_WoodLight', 'PC_WoodLight', 'laptops', seed=int(x + 50))
    # under the mezzanine: accessory avenues + support bar
    for s in (-1, 1):
        F.wall_shelf(dp, L, s * (X1 - 0.75), 25.0, ZG, s * -90, 11.0, 3.6, 5, 'PC_WoodLight', 'PC_Travertine', seed=40 + s)
    F.product_table(fu, L, 0.0, 26.0, ZG, 0, 6.0, 1.2, 1.0, 'PC_WoodLight', 'PC_WoodLight', 'none')
    for x in (-2.4, -1.2, 0.0, 1.2, 2.4):
        F.stool(fu, L, x, 27.0, ZG, 0.72, 'PC_WoodLight', 'PC_WoodLight')
    # mezzanine: tables + video wall
    for x in (-6.0, 6.0):
        F.product_table(dp, L, x, 22.4, ZM, 0, 4.4, 1.15, 0.86, 'PC_WoodLight', 'PC_WoodLight', 'mixed', seed=int(x + 70))
    F.tv_wall(dp, L, 0.0, Y1 - 0.65, ZM, 0, 1, 1, 7.0, 3.2, 0.1, 0.6, seed=16)
    for x in (-3.0, -1.5, 0.0, 1.5, 3.0):
        for y in (26.5, 28.0):
            F.stool(fu, L, x, y, ZM, 0.45, 'PC_WoodLight', 'PC_WoodLight')


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -22.0, 22.0)
S.paved(A, 'OPTIONAL_FORECOURT', [(-22.0, 0.0, 22.0, Y0 - 0.6)], 'PC_Travertine', sub='StonePlaza')
for x in (-12.0, 12.0):
    F.bench(A.s('OPTIONAL_FORECOURT', 'Benches'), 0, x, 2.6, 0.0, 0, 3.0, 'PC_Travertine', 'PC_Travertine')
for x in (-18.0, -7.0, 7.0, 18.0):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 0.6, 0.0, 0.9, 0.12, 'PC_Stainless', None)

for i, (x, y, z, e) in enumerate(((-7, 11, 8.6, 1600), (7, 11, 8.6, 1600), (0, 15, 8.6, 1600), (-7, 25, 4.0, 900), (7, 25, 4.0, 900),
                                  (-6, 24, 8.6, 1000), (6, 24, 8.6, 1000))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#fff3e4', radius=1.5)
A.light('EXTERIOR_LIGHTING', 'PlazaDown', 'SPOT', (0.0, 4.0, ZC + 0.25), 1200, '#fff1e0', spot_deg=110)
A.col_box('Pavilion', X0 - 0.7, Y0 - 0.6, 0, X1 + 0.7, Y1, ZC + 0.3)
A.col_box('Roof', X0 - 2.5, Y0 - 2.5, ZC + 0.3, X1 + 2.5, Y1 + 2.0, ZC + 0.85)
A.camera('day', (-30.0, -24.0, 7.5), (0.0, 16.0, 5.0), 28)
A.camera('night', (26.0, -22.0, 4.0), (0.0, 16.0, 5.0), 28)
A.camera('road', (-22.0, -7.6, 1.1), (0.0, 15.0, 4.2), 24)
A.camera('interior', (12.4, 7.2, 2.0), (-5.0, 24.0, 4.6), 17)
A.checks['probes'] = [dict(name='Hall_tables', p=[0.0, 10.0, 1.2]), dict(name='Hall_tables_2', p=[-5.4, 13.6, 1.2]),
                      dict(name='Mezzanine', p=[-6.0, 22.4, ZM + 1.2]), dict(name='Mezzanine_r', p=[6.0, 22.4, ZM + 1.2])]
S.finish(A, -22.0, 22.0, width=33.0, depth=31.0, height=ZC + 0.85, footprint=[X0 - 2.5, Y0 - 2.5, X1 + 2.5, Y1 + 2.0],
         storeys=2, floor_levels=[ZG, ZM], roof=ZC + 0.85, parking='none (pedestrian plaza only)',
         access='pedestrian only - no vehicle access', setback_m=5.4, glass='frameless PC_GlassClear alpha 0.11 with glass fins',
         concept=__doc__.strip().split('\n')[2])
