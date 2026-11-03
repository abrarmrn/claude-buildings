"""ASSET 17 - Aurelia Coffee House (luxury two-storey cafe, contrasting Serein).

Massing: warm travertine-clad volume whose front-LEFT corner is a 6 m radius CURVED glass wall (ground floor) under a
curved bronze canopy that follows it.  The upper floor is SET BACK 4 m, leaving a roof terrace with a bronze pergola
over the curve; its front is a raked (angled) glazed lounge window framed by bronze fins, and a stepped stone cornice
completes a stepped roof composition.  Premium roadside stone terrace with benches and EMPTY stone planters.
Inside: marble + brass coffee counter, armchairs, a curved stair to an upstairs lounge with chesterfield-style sofas,
brass ring chandeliers.
Site: terrace directly on the pavement; no parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('17', '17_aurelia_coffee_house', 'aurelia_coffee_house', 'P17', 'AureliaCoffeeHouse', 'Aurelia Coffee House', 2)
defmat('AU_Gold', '#c9a24a', 0.25, 1.0, emit='#ffd690', es=3.5)

X0, X1, Y0, Y1 = -10.0, 10.0, 5.0, 20.0
RC = 6.0
Z = [0.15, 4.8, 9.2]
YU = Y0 + 4.0                    # upper floor front (set back)
SP = (6.4, 15.8)                 # curved stair centre


def gf_outline(L):
    n = {0: 12, 1: 6, 2: 3}[L]
    arc = arc_pts(X0 + RC, Y0 + RC, RC, 180, 270, n)       # from left side down to the front
    return arc + [(X1, Y0), (X1, Y1), (X0, Y1)]


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    out = gf_outline(L)
    A.m(L, 'BUILDING_INTERIOR', 'GroundSlab').add(bm_prism(out, -0.3, Z[0]), 'PC_FloorMarble',
                                                   mat_fn=mat_by_normal('PC_FloorMarble', 'PC_Concrete', 'PC_Travertine'))
    # GF roof = terrace floor (follows the curve) with stair well
    AR.slab(A, L, out, Z[1], 0.45, [AR.poly_rect(SP[0] - 2.4, SP[1] - 2.4, SP[0] + 2.4, SP[1] + 2.4)], 'PC_Travertine', 'PC_Ceiling', 'PC_Travertine')
    # curved bronze canopy following the corner + front (1.6 m projection)
    n = {0: 16, 1: 8, 2: 4}[L]
    ca = arc_pts(X0 + RC, Y0 + RC, RC + 1.6, 180, 270, n) + [(X1 - 3.0, Y0 - 1.6)]
    ci = list(reversed(arc_pts(X0 + RC, Y0 + RC, RC, 180, 270, n) + [(X1 - 3.0, Y0)]))
    det.add(bm_prism(ca + ci, Z[1] - 0.75, Z[1] - 0.5), 'PC_Bronze')
    if L < 2:
        AR.downlights(det, L, [(X0 + RC + (RC + 0.8) * math.cos(math.radians(a)), Y0 + RC + (RC + 0.8) * math.sin(math.radians(a)))
                               for a in range(185, 270, 14)], Z[1] - 0.75, 0.08, 'PC_LightWarm')
    # GF curved glass (with entrance) + stone front pier to the right + stone sides/back
    arc = arc_pts(X0 + RC, Y0 + RC, RC, 180, 270, n)
    AR.curtain(A, L, arc, 0.0, Z[1] - 0.75, 1.6, [3.2], 0.05, 0.15, 'PC_Bronze', 'PC_GlassClear', sub='Curve')
    AR.curtain(A, L, [(X0 + RC, Y0), (X1 - 3.0, Y0)], 0.0, Z[1] - 0.75, 1.5, [3.2], 0.05, 0.15, 'PC_Bronze', 'PC_GlassClear', sub='FrontGF',
               doors=[dict(seg=0, u0=0.4, u1=2.6, h=2.9, kind='pivot', leaves=2)])
    AR.wall(ext, (X1 - 3.0, Y0), (X1, Y0), 0.0, Z[1] + 0.3, 0.45, 'PC_Travertine', 'PC_WallWarm')
    AR.wall(ext, (X1, Y0), (X1, Y1), 0.0, Z[2] + 0.5, 0.45, 'PC_Travertine', 'PC_WallWarm', holes=[(5.0, 11.0, 1.0, 3.6), (6.0, 12.0, Z[1] + 0.8, Z[2] - 0.8)])
    AR.curtain(A, L, [(X1 + 0.01, Y0 + 5.0), (X1 + 0.01, Y0 + 11.0)], 1.0, 3.6, 2.0, [], 0.05, 0.12, 'PC_Bronze', 'PC_GlassClear', sub='SideGF')
    AR.curtain(A, L, [(X1 + 0.01, Y0 + 6.0), (X1 + 0.01, Y0 + 12.0)], Z[1] + 0.8, Z[2] - 0.8, 2.0, [], 0.05, 0.12, 'PC_Bronze', 'PC_GlassClear', sub='SideL1')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2] + 0.5, 0.45, 'PC_Travertine', 'PC_WallWarm', holes=[(3.0, 4.6, 0.0, 2.5)])
    AR.wall(ext, (X0, Y1), (X0, Y0 + RC), 0.0, Z[1] + 0.3, 0.45, 'PC_Travertine', 'PC_WallWarm')
    AR.wall(ext, (X0, Y1), (X0, YU), Z[1], Z[2] + 0.5, 0.45, 'PC_Travertine', 'PC_WallWarm')
    # upper floor: set-back front with raked glass + bronze fins, stepped cornice
    rk = 0.7                                             # rake (top leans forward)
    g = A.m(L, 'GLASS_SYSTEM', 'RakedGlass')
    nfin = 8
    for i in range(nfin):
        xa = X0 + (X1 - X0) * i / nfin; xb = X0 + (X1 - X0) * (i + 1) / nfin
        g.add(AR.quad_world((xa, YU, Z[1]), (xb, YU, Z[1]), (xb, YU - rk, Z[2] - 0.2), (xa, YU - rk, Z[2] - 0.2)), 'PC_GlassClear')
        if L < 2:
            det.add(AR.bm_yz_prism([(YU - 0.05, Z[1]), (YU + 0.1, Z[1]), (YU - rk + 0.1, Z[2] - 0.2), (YU - rk - 0.45, Z[2] - 0.2), (YU - 0.45, Z[1] + 0.3)],
                                   xa - 0.05, xa + 0.05), 'PC_Bronze')
    ext.add(bm_box(X0, YU - rk - 0.5, Z[2] - 0.2, X1, Y1, Z[2] + 0.35), 'PC_Travertine', mat_fn=mat_by_normal('PC_RoofGravel', 'PC_Ceiling', 'PC_Travertine'))
    ext.add(bm_box(X0 - 0.2, YU - rk - 0.7, Z[2] + 0.35, X1 + 0.2, Y1, Z[2] + 0.6), 'PC_Travertine')
    ext.add(bm_box(X0 + 1.5, YU + 1.0, Z[2] + 0.6, X1 - 1.5, Y1 - 1.0, Z[2] + 1.3), 'PC_Travertine')
    det.add(bm_box(X0 - 0.22, YU - rk - 0.72, Z[2] + 0.3, X1 + 0.22, YU - rk - 0.62, Z[2] + 0.38), 'PC_Bronze')
    # roof terrace: stone parapet along the curve + bronze pergola (no planting)
    for (p0, p1) in zip(arc[:-1] + [(X0 + RC, Y0)], arc[1:] + [(X1 - 3.0, Y0)]):
        M, Ls = seg_frame(p0, p1)
        det.add(bm_box(0, 0.0, Z[1], Ls, 0.3, Z[1] + 1.05), 'PC_Travertine', matrix=M)
    for x in (X0 + 1.0, -4.0, 1.0, 6.0):
        AR.column(det, L, x, Y0 + 1.2 if x > X0 + 3 else Y0 + 3.0, Z[1], Z[1] + 3.0, 0.08, 'PC_Bronze', square=True)
    AR.box(det, X0 + 0.8, Y0 + 1.0, Z[1] + 3.0, X1 - 3.0, Y0 + 1.25, Z[1] + 3.15, 'PC_Bronze')
    if L < 2:
        for k in range(14):
            x = X0 + 1.0 + k * 1.0
            det.add(bm_box(x - 0.04, Y0 + 1.0, Z[1] + 3.15, x + 0.04, YU - 0.3, Z[1] + 3.3), 'PC_Bronze')
    # signage
    sg = A.m(L, 'SIGNAGE', 'Brand')
    Ms = place('-Y', Vector((1.0, YU - rk - 0.73, Z[2] + 0.02)))
    txt(sg, L, 'AURELIA', Ms, 0.5, 0.05, 'caladea_b', 'AU_Gold', 'PC_Bronze', spacing=1.4)
    Mp = place('-Y', Vector((X1 - 1.5, Y0 - 0.47, 2.6)))
    sg.add(bm_box(X1 - 2.8, Y0 - 0.46, 1.2, X1 - 0.2, Y0 - 0.45, 4.2), 'PC_Bronze')
    txt(sg, L, 'A', Mp @ Matrix.Translation((0, 0.6, 0.0)), 1.1, 0.06, 'caladea_b', 'AU_Gold', 'PC_Bronze')
    if L < 2:
        txt(sg, L, 'COFFEE HOUSE', Mp @ Matrix.Translation((0, -0.5, 0.0)), 0.17, 0.02, 'caladea_b', 'AU_Gold', 'AU_Gold', spacing=1.3)
    A.sign('cornice_name', (1.0, YU - rk - 0.8, Z[2] + 0.02), 0.5, width=5.0)
    A.sign('stone_plaque', (X1 - 1.5, Y0 - 0.55, 3.2), 1.1, width=2.6)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Cafe')
    gz = Z[0]
    AR.spiral_stair(A, L, SP[0], SP[1], 0.9, 2.3, gz, Z[1], a0=180.0, sweep=250.0, tread='PC_Travertine', struct='PC_Bronze', sub='CurvedStair')
    AR.glass_rail(A, L, [(SP[0] - 2.4, SP[1] - 2.4), (SP[0] + 2.4, SP[1] - 2.4)], Z[1], rail='PC_Bronze')
    AR.ceiling_panels(A, L, [(X0 + 1.0, Y0 + 1.0, X1 - 1.0, Y1 - 1.0)], Z[1] - 0.45, (3.0, 3.0), w=0.35, d=0.35, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 1.0, YU + 0.5, X1 - 1.0, Y1 - 1.0)], Z[2] - 0.2, (3.0, 3.0), w=0.35, d=0.35, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    # counter (marble + brass) along the back, pastry case, bottle/coffee shelves
    F.counter(fu, L, -7.5, 16.5, 2.5, 17.4, gz, 1.05, 'PC_FloorMarble', 'PC_StoneTop', 'AU_Gold')
    F.display_case(fu, L, -7.4, 15.7, -4.4, 16.5, gz, 1.25, 'PC_Brass', 'PC_GlassClear', 'PC_LightWarm', 'PC_WoodLight')
    F.espresso_machine(fu, L, -1.5, 17.0, gz + 1.05, 180, 'PC_Brass', 'PC_BlackGloss')
    F.bottle_shelf(fu, L, -2.5, Y1 - 0.5, gz, 0, 9.0, 2, seed=4, back='PC_TimberDark', light='PC_LightWarm')
    # armchair groups + round tables along the curved glass
    for (x, y) in ((-6.5, 9.5), (-3.0, 7.5), (0.5, 7.5), (4.0, 8.0)):
        F.round_set(fu, L, x, y, gz, 3, 0.45, 'PC_StoneTop', 'PC_Brass', 'PC_LeatherCream')
    F.lounge_group(fu, L, -5.5, 13.0, gz, 0, 'PC_Leather', 'PC_FabricRust')
    # chandeliers
    if L < 2:
        for (x, y) in ((-4.0, 9.0), (1.5, 9.5)):
            for r, dz in ((1.0, 1.4), (0.65, 1.1)):
                F.ring_light(fu, L, x, y, Z[1] - 0.45 - dz, r, 0.05, 'PC_LampGlobe')
                fu.add(bm_cyl(x, y, Z[1] - 0.45 - dz, Z[1] - 0.45, 0.01, 4), 'PC_Brass')
    # upstairs lounge
    for x in (-6.0, -1.5):
        F.sofa(fu, L, x, 17.6, Z[1], 0, 2.6, 0.95, 'PC_Leather')
        F.coffee_table(fu, L, x, 16.3, Z[1], 0.5)
    for (x, y) in ((-7.0, 11.0), (-3.5, 11.0), (0.0, 11.0)):
        F.armchair(fu, L, x, y, Z[1], 180, 'PC_LeatherCream')
    # roof terrace seating under the pergola
    for (x, y) in ((-6.0, 6.8), (-2.5, 6.6), (1.5, 6.6)):
        F.round_set(fu, L, x, y, Z[1], 2, 0.4, 'PC_StoneTop', 'PC_Bronze', 'PC_FabricCream', a0=0)


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -16.0, 16.0)
S.paved(A, 'OPTIONAL_FORECOURT', [(-16.0, 0.0, 16.0, Y0)], 'PC_Travertine', sub='StoneTerrace')
A.s('OPTIONAL_FORECOURT', 'CornerTerrace').add(bm_prism([(X0, Y0)] + arc_pts(X0 + RC, Y0 + RC, RC, 270, 180, 12), -0.2, 0.0), 'PC_Travertine')
tf = A.s('OPTIONAL_FORECOURT', 'TerraceFurniture')
for x in (-12.5, -8.5, -4.0, 0.0):
    F.round_set(tf, 0, x, 2.6, 0.0, 2, 0.4, 'PC_StoneTop', 'PC_Bronze', 'PC_FabricCream', a0=0)
F.bench(tf, 0, 4.5, 1.2, 0.0, 0, 2.6, 'PC_Walnut', 'PC_Travertine')
for x in (-14.5, 8.0, 14.0):
    F.empty_planter(tf, 0, x - 0.6, 3.6, x + 0.6, 4.6, 0.0, 0.6, 'PC_Travertine')

for i, (x, y, z, e) in enumerate(((-3, 10, 4.0, 600), (3, 14, 4.0, 500), (-3, 15, 8.4, 500))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffd6a0', radius=0.8)
A.light('EXTERIOR_LIGHTING', 'PlaqueWash', 'SPOT', (X1 - 1.5, Y0 - 3.0, 0.2), 300, '#ffd6a0', rot=(-70, 0, 0), spot_deg=30)
A.light('EXTERIOR_LIGHTING', 'PergolaGlow', 'POINT', (-3.0, Y0 + 2.5, Z[1] + 2.6), 200, '#ffd6a0', radius=0.6)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[1] + 0.3)
A.col_box('Upper', X0, YU - 0.7, Z[1], X1, Y1, Z[2] + 1.3)
A.camera('day', (-24.0, -16.0, 7.0), (0.0, 10.0, 4.0), 28)
A.camera('night', (20.0, -16.0, 3.8), (-1.0, 10.0, 4.4), 28)
A.camera('road', (-18.0, -7.6, 1.1), (0.0, 9.0, 3.6), 24)
A.camera('interior', (-8.6, 18.4, 1.7), (4.0, 8.0, 3.6), 16)
A.checks['probes'] = [dict(name='GF_curve_tables', p=[-3.0, 7.5, 1.0]), dict(name='Counter', p=[-3.0, 16.0, 1.3]),
                      dict(name='L1_lounge', p=[-3.5, 11.0, Z[1] + 1.0])]
S.finish(A, -16.0, 16.0, width=20.0, depth=15.0, height=Z[2] + 1.3, footprint=[X0, Y0 - 1.6, X1, Y1],
         storeys=2, floor_levels=Z[:2], roof='stepped: terrace 4.8 m, upper roof 9.8 m, crown 10.5 m', parking='none (roadside stone terrace)',
         access='pedestrian only', setback_m=5.0, glass='curved GF PC_GlassClear corner + raked upper lounge glass',
         concept=__doc__.strip().split('\n')[2])
