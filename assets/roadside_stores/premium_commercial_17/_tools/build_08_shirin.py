"""ASSET 08 - Shirin Restaurant (premium Middle Eastern dining, 1 storey + 2-storey entrance tower).

Massing: a long (46 m) but SHALLOW (14 m) sand-limestone frontage with ten tall arched windows and a bronze cornice,
broken in the middle by an 11 m entrance tower carrying a tall pointed-arch portal and a back-lit bronze mashrabiya
screen.  A 4.6 m deep terrace runs along the pavement: shaded on the left by a bronze pergola with lattice screens,
open with a low stone balustrade on the right.  Inside: one tall (5.7 m) dining hall with lanterns, banquettes and a
back-lit screen wall hiding the kitchen.
Site: terrace directly on the pavement; optional side parking on the right (separate collection).
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('08', '08_shirin_restaurant', 'shirin_restaurant', 'P08', 'ShirinRestaurant', 'Shirin Restaurant', 1)
defmat('SH_Gold', '#c9a24a', 0.3, 1.0, emit='#ffcf7a', es=2.5)
defmat('SH_ScreenGlow', '#ffb060', 0.5, emit='#ffb060', es=4.0)

X0, X1, Y0, Y1 = -23.0, 23.0, 5.0, 19.0
TW = (-4.0, 4.0)
ZR, ZT = 7.2, 11.0
WIN = [-20.6, -17.2, -13.8, -10.4, -7.0, 7.0, 10.4, 13.8, 17.2, 20.6]
WW, WZB, WZS = 2.6, 0.6, 4.4


def arch_glass(A, L, xc, w, zb, zs, y, frame='PC_Bronze', comp='GLASS_SYSTEM', sub='Arches'):
    seg = {0: 12, 1: 6, 2: 3}[L]
    M = place('-Y', Vector((0.0, y, 0.0)))
    A.m(L, comp, sub + 'Glass').add(bm_poly_flat(K.arch_poly(xc, w, zb, zs, seg), 0.0), 'PC_Glass', matrix=M)
    if L == 2:
        return
    inner = K.arch_poly(xc, w, zb, zs, seg)
    outer = K.arch_poly(xc, w, zb, zs, seg, grow=0.08)
    A.m(L, comp, sub + 'Frame').add(R.bm_ring_prism(outer, inner, -0.06, 0.08), frame, matrix=M)
    if L == 0:
        A.m(L, comp, sub + 'Frame').add(bm_box(xc - 0.025, y - 0.04, zb, xc + 0.025, y + 0.04, zs + w / 2), frame)
        A.m(L, comp, sub + 'Frame').add(bm_box(xc - w / 2, y - 0.04, zs - 0.025, xc + w / 2, y + 0.04, zs + 0.025), frame)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], 0.15, 0.45, 'PC_FloorMarble', 'PC_Concrete', 'PC_StoneSand', sub='GroundSlab')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], ZR, 0.5, 'PC_RoofGravel', 'PC_Ceiling', 'PC_StoneSand', comp='BUILDING_EXTERIOR', sub='Roof')
    # front: arched wall (outer face y = Y0), split by the tower
    K.arch_wall(ext, L, X0, TW[0], Y0, 0.5, 0.0, ZR + 0.8, [(x, WW, WZB, WZS) for x in WIN if x < 0], 'PC_StoneSand')
    K.arch_wall(ext, L, TW[1], X1, Y0, 0.5, 0.0, ZR + 0.8, [(x, WW, WZB, WZS) for x in WIN if x > 0], 'PC_StoneSand')
    for x in WIN:
        arch_glass(A, L, x, WW, WZB, WZS, Y0 + 0.25)
    # cornice + base
    AR.box(det, X0 - 0.2, Y0 - 0.3, ZR + 0.15, X1 + 0.2, Y0 + 0.5, ZR + 0.35, 'PC_Bronze')
    AR.box(ext, X0 - 0.1, Y0 - 0.15, 0.0, X1 + 0.1, Y0 + 0.5, 0.45, 'PC_StoneDark')
    # tower: projecting 2 m, pointed arch portal, back-lit mashrabiya panel, sign
    ty0 = Y0 - 2.0
    K.arch_wall(ext, L, TW[0], TW[1], ty0, 0.6, 0.0, ZT, [(0.0, 3.6, 0.0, 5.0)], 'PC_StoneSand')
    tyb = Y0 + 4.0
    AR.wall(ext, (TW[0], tyb), (TW[0], ty0), 0.0, ZT, 0.5, 'PC_StoneSand', 'PC_StoneSand')
    AR.wall(ext, (TW[1], ty0), (TW[1], tyb), 0.0, ZT, 0.5, 'PC_StoneSand', 'PC_StoneSand')
    AR.wall(ext, (TW[1], tyb), (TW[0], tyb), ZR, ZT, 0.5, 'PC_StoneSand', 'PC_StoneSand')
    AR.box(ext, TW[0], ty0, ZT - 0.3, TW[1], tyb, ZT, 'PC_StoneSand', top='PC_RoofGravel')
    AR.box(det, TW[0] - 0.25, ty0 - 0.3, ZT - 0.05, TW[1] + 0.25, Y0 + 0.6, ZT + 0.2, 'PC_Bronze')
    arch_glass(A, L, 0.0, 3.6, 0.0, 5.0, ty0 + 0.6 + 1.2, sub='Portal')
    if L < 2:
        A.m(L, 'GLASS_SYSTEM', 'PortalDoor').add(bm_box(-0.04, ty0 + 1.75, 0.0, 0.04, ty0 + 1.85, 3.0), 'PC_Bronze')
        A.m(L, 'FACADE_DETAILS', 'Screen').add(bm_vquad(-3.2, 3.2, 7.6, 10.4, ty0 - 0.05, '-Y'), 'PC_Mashrabiya', uv='box', tile=0.6)
        det.add(bm_box(-3.35, ty0 - 0.1, 7.45, 3.35, ty0 + 0.0, 7.6), 'PC_Bronze')
        det.add(bm_vquad(-3.2, 3.2, 7.6, 10.4, ty0 + 0.12, '-Y'), 'SH_ScreenGlow')
    else:
        det.add(bm_vquad(-3.2, 3.2, 7.6, 10.4, ty0 - 0.05, '-Y'), 'SH_ScreenGlow')
    # sides/back
    AR.wall(ext, (X1, Y0), (X1, Y1), 0.0, ZR + 0.8, 0.5, 'PC_StoneSand', 'PC_WallWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, ZR + 0.8, 0.5, 'PC_StoneSand', 'PC_WallWarm', holes=[(4.0, 6.0, 0.0, 2.6)])
    AR.wall(ext, (X0, Y1), (X0, Y0), 0.0, ZR + 0.8, 0.5, 'PC_StoneSand', 'PC_WallWarm')
    # signage
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'SHIRIN', place('-Y', Vector((0.0, ty0 - 0.08, 6.65))), 0.95, 0.1, 'caladea_b', 'SH_Gold', 'PC_Bronze', spacing=1.25)
    if L < 2:
        txt(sg, L, R.arabic('شيرين'), place('-Y', Vector((0.0, ty0 - 0.08, 5.75))), 0.55, 0.06, 'arabic', 'SH_Gold', 'PC_Bronze')
        txt(sg, L, 'FINE MIDDLE EASTERN DINING', place('-Y', Vector((-13.8, Y0 - 0.32, ZR + 0.25))), 0.3, 0.02, 'caladea_b',
            'SH_Gold', 'SH_Gold', spacing=1.2)
    A.sign('tower_wordmark', (0.0, ty0 - 0.2, 6.65), 0.95, width=5.0)
    # terrace: pergola (left) + balustrade (right)
    tr = A.m(L, 'FACADE_DETAILS', 'Terrace')
    for x in (-22.5, -17.8, -13.1, -8.4, -4.6):
        AR.column(tr, L, x, 0.9, 0.0, 3.5, 0.11, 'PC_Bronze', square=True)
    AR.box(tr, -22.7, 0.7, 3.5, -4.4, 1.1, 3.75, 'PC_Bronze')
    AR.box(tr, -22.7, 0.7, 3.5, -22.3, Y0, 3.75, 'PC_Bronze')
    if L < 2:
        tr.add(bm_hquad(-22.6, 0.8, -4.5, Y0, 3.62), 'PC_Mashrabiya', uv='box', tile=0.6)
        tr.add(bm_hquad(-22.6, 0.8, -4.5, Y0, 3.62, down=True), 'PC_Mashrabiya', uv='box', tile=0.6)
        for x in range(-21, -5, 3):
            AR.downlights(tr, L, [(x + 0.5, 2.9)], 3.5, 0.1, 'PC_LightWarm')
    AR.box(tr, 4.6, 0.6, 0.0, 22.6, 0.9, 0.9, 'PC_StoneSand')
    AR.box(tr, 22.3, 0.6, 0.0, 22.6, Y0, 0.9, 'PC_StoneSand')
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Dining')
    st = A.m(L, 'BUILDING_INTERIOR', 'Walls')
    gz = 0.15
    # back-lit screen wall hiding the kitchen (kitchen zone y > 15.8 is not modelled in detail)
    AR.box(st, X0 + 0.5, 15.8, gz, X1 - 0.5, 16.0, ZR - 0.5, 'PC_WallWarm')
    if L < 2:
        for xc in (-14.0, 0.0, 14.0):
            st.add(bm_vquad(xc - 3.0, xc + 3.0, 1.0, 5.0, 15.78, '-Y'), 'PC_Mashrabiya', uv='box', tile=0.6)
            st.add(bm_vquad(xc - 3.0, xc + 3.0, 1.0, 5.0, 15.84, '-Y'), 'SH_ScreenGlow')
    AR.ceiling_panels(A, L, [(X0 + 1.0, Y0 + 1.0, X1 - 1.0, 15.5)], ZR - 0.5, (4.0, 3.0), w=1.0, d=1.0, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    # reception (inside the tower)
    F.counter(fu, L, -1.6, 7.0, 1.6, 7.7, gz, 1.1, 'PC_TimberDark', 'PC_StoneTop', 'SH_Gold')
    # dining: 4-seat tables in front of the arches, round tables, banquettes along the back wall
    for x in WIN:
        F.dining_set(fu, L, x, 7.6, gz, 0, 2, 1.2, 0.8, 'PC_Walnut', 'PC_TimberDark', 'PC_FabricRust')
    for x in (-18.5, -11.0, 11.0, 18.5):
        F.round_set(fu, L, x, 11.3, gz, 5, 0.6, 'PC_StoneTop', 'PC_TimberDark', 'PC_FabricCream')
    for x in (-19.0, -14.0, -9.0, 9.0, 14.0, 19.0):
        sofa_bench(fu, L, x, 15.2, gz)
        F.table_rect(fu, L, x, 14.2, gz, 0, 1.6, 0.8, top='PC_Walnut')
        F.chair(fu, L, x - 0.45, 13.3, gz, 180, 'PC_TimberDark', 'PC_FabricRust')
        F.chair(fu, L, x + 0.45, 13.3, gz, 180, 'PC_TimberDark', 'PC_FabricRust')
    # lanterns
    for x in WIN + [-3.0, 3.0]:
        for y in (9.5, 13.0):
            F.pendant(fu, L, x, y, ZR - 0.5, 2.0 if y < 10 else 1.6, 'lantern', 0.18, 'PC_LampGlobe', 'PC_Brass')
    # terrace dining (outside, part of the restaurant furniture)
    tf = A.m(L, 'FURNITURE', 'Terrace')
    for x in (-20.0, -15.4, -10.8, -6.6):
        F.round_set(tf, L, x, 2.9, 0.0, 4, 0.45, 'PC_StoneTop', 'PC_Bronze', 'PC_FabricCream')
    for x in (7.0, 11.5, 16.0, 20.5):
        F.round_set(tf, L, x, 2.9, 0.0, 4, 0.45, 'PC_StoneTop', 'PC_Bronze', 'PC_FabricCream')


def sofa_bench(acc, L, x, y, z):
    if L == 2:
        return
    acc.add(bm_box(x - 0.9, y - 0.3, z, x + 0.9, y + 0.3, z + 0.45), 'PC_FabricRust')
    acc.add(bm_box(x - 0.9, y + 0.25, z + 0.45, x + 0.9, y + 0.45, z + 1.1, bevel=0.02 if L == 0 else 0), 'PC_FabricRust')


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -26.0, 36.0, crossings=[(26.0, 32.0)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-26.0, 0.0, 26.0, Y0)], 'PC_StoneSand', sub='Terrace')
S.asphalt(A, 'DRIVEWAY', [(26.0, 0.0, 32.0, 6.0)])
S.asphalt(A, 'OPTIONAL_PARKING', [(26.0, 6.0, 38.0, 20.0)])
S.bays(A, 32.0, 6.5, 5, 2.6, 6.0, 1, along='y')

for i, (x, y) in enumerate(((-15, 10), (-6, 10), (6, 10), (15, 10))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, 5.6), 900, '#ffd9a8', radius=1.0)
A.light('INTERIOR_LIGHTING', 'Reception', 'POINT', (0.0, 6.0, 6.0), 500, '#ffd9a8', radius=0.6)
A.light('EXTERIOR_LIGHTING', 'TowerWashL', 'SPOT', (-3.0, -2.0, 0.2), 900, '#ffd9a8', rot=(-80, 0, 0), spot_deg=35)
A.light('EXTERIOR_LIGHTING', 'TowerWashR', 'SPOT', (3.0, -2.0, 0.2), 900, '#ffd9a8', rot=(-80, 0, 0), spot_deg=35)
A.light('EXTERIOR_LIGHTING', 'TerraceR', 'POINT', (14.0, 2.8, 3.0), 300, '#ffd9a8', radius=0.5)
A.col_box('Main', X0, Y0, 0, X1, Y1, ZR + 0.8)
A.col_box('Tower', TW[0], Y0 - 2.0, 0, TW[1], Y1, ZT + 0.2)
A.col_box('Pergola', -22.7, 0.7, 3.5, -4.4, Y0, 3.75)
A.camera('day', (-38.0, -24.0, 7.5), (-2.0, 9.0, 3.5), 28)
A.camera('night', (30.0, -22.0, 4.0), (-2.0, 9.0, 4.0), 26)
A.camera('road', (-26.0, -7.6, 1.1), (2.0, 9.0, 3.2), 24)
A.camera('interior', (20.5, 14.5, 1.65), (-8.0, 8.0, 2.6), 17)
A.checks['probes'] = [dict(name='Dining_front_L', p=[-13.8, 7.6, 1.0]), dict(name='Dining_front_R', p=[10.4, 7.6, 1.0]),
                      dict(name='Dining_round', p=[-11.0, 11.3, 1.0])]
S.finish(A, -26.0, 38.0, width=46.0, depth=16.0, height=ZT + 0.2, footprint=[X0, Y0 - 2.0, X1, Y1],
         storeys='1 (+ 2-storey-high entrance tower)', floor_levels=[0.15], roof=ZR, parking='optional right side, 5 bays (OPTIONAL_PARKING)',
         access='terrace opens directly onto the pavement; separate right-hand crossing to optional parking', setback_m=0.0,
         glass='10 arched PC_Glass windows + portal', concept=__doc__.strip().split('\n')[2])
