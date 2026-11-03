"""ASSET 11 - Pearl Terrace (luxury international dining, 2 storeys).

Massing: a soft, pearl-white two-storey volume with fully rounded corners.  The upper dining room is wrapped by a
deep cantilevered BALCONY TERRACE (rounded, 4 m projection on the front, 6 m over the side terrace) with a solid
pearl parapet and a glass top rail; the ground floor sits back behind a full-height terrace-facing glass wall.
A thin rounded roof canopy with a ring of LED floats above.  Footprint is wider than deep with a side garden
terrace (empty stone planters only) under the balcony overhang.
Inside: grand sweeping curved staircase, premium reception with a chandelier ring, visible upper floor.
Site: terrace directly beside the pavement; no parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('11', '11_pearl_terrace', 'pearl_terrace', 'P11', 'PearlTerrace', 'Pearl Terrace', 2)
defmat('PT_Letter', '#d9c7a0', 0.25, 1.0, emit='#fff0d0', es=3.0)

X0, X1, Y0, Y1 = -17.0, 11.0, 8.0, 26.0
RC = 4.0
Z = [0.15, 5.2, 9.8]
SPIRAL = (-10.0, 20.5)


def rr(x0, y0, x1, y1, r, L):
    return rounded_rect(x0, y0, x1, y1, r, {0: 6, 1: 3, 2: 2}[L])


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    det = A.m(L, 'FACADE_DETAILS', 'Balcony')
    foot = rr(X0, Y0, X1, Y1, RC, L)
    A.m(L, 'BUILDING_INTERIOR', 'GroundSlab').add(bm_prism(foot, -0.3, Z[0]), 'PC_FloorMarble',
                                                   mat_fn=mat_by_normal('PC_FloorMarble', 'PC_Concrete', 'PC_PanelPearl'))
    # balcony slab (= L1 floor, extends beyond the glass) with a stair well
    bal = rr(X0 - 1.0, Y0 - 4.0, X1 + 6.0, Y1, RC + 2.0, L)
    hole = [(SPIRAL[0] + 4.3 * math.cos(2 * math.pi * i / 16), SPIRAL[1] + 4.3 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    AR.slab(A, L, bal, Z[1], 0.45, [hole], 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelPearl', comp='BUILDING_EXTERIOR', sub='BalconySlab')
    # solid pearl parapet with glass top rail along the balcony edge (front + right side)
    edge = [p for p in bal if p[1] < Y1 - 0.5]
    for (p0, p1) in zip(edge[:-1], edge[1:]):
        M, Ls = seg_frame(p0, p1)
        det.add(bm_box(0, 0.0, Z[1], Ls, 0.25, Z[1] + 0.75), 'PC_PanelPearl', matrix=M)
        if L < 2:
            det.add(bm_vquad(0, Ls, Z[1] + 0.75, Z[1] + 1.15, 0.12, '-Y'), 'PC_GlassRail', matrix=M)
            det.add(bm_box(0, 0.0, Z[1] + 1.12, Ls, 0.25, Z[1] + 1.18), 'PC_Brass', matrix=M)
            det.add(bm_hquad(0.0, 0.02, Ls, 0.2, Z[1] - 0.455, down=True), 'PC_LightStrip', matrix=M) if L == 0 else None
    # glass walls (both floors) along the rounded front/sides, solid back
    gl = [p for p in foot if p[1] < Y1 - 1.0]
    gl = sorted(gl, key=lambda p: math.atan2(p[1] - (Y0 + Y1) / 2, p[0] - (X0 + X1) / 2))
    front = [p for p in foot if p[1] < Y1 - RC + 0.01]
    # order: from left-back corner around the front to right-back corner (CCW = outside on the right)
    pts = [(X0, Y1 - RC)] + [p for p in rr(X0, Y0, X1, Y1, RC, L) if p[1] < Y1 - RC - 1e-3]
    pts = R.ccw(pts)
    loop = rr(X0, Y0, X1, Y1, RC, L)
    k0 = min(range(len(loop)), key=lambda i: (loop[i][0] - X0) ** 2 + (loop[i][1] - (Y1 - RC)) ** 2)
    k1 = min(range(len(loop)), key=lambda i: (loop[i][0] - X1) ** 2 + (loop[i][1] - (Y1 - RC)) ** 2)
    seq = loop[k0:] + loop[:k0]
    j = seq.index(loop[k1])
    path = seq[:j + 1]
    if path[1][1] > path[0][1]:
        path = list(reversed(loop[k1:] + loop[:k1]))[:len(loop) - j + 1]
    for (z0, z1, sub) in ((0.0, Z[1] - 0.45, 'GF'), (Z[1], Z[2] - 0.4, 'L1')):
        AR.curtain(A, L, path, z0, z1, 2.4, [], 0.05, 0.16, 'PC_AluChampagne', 'PC_GlassClear', sub=sub,
                   doors=[dict(seg=len(path) // 2, u0=0.0, u1=2.0, h=2.8, kind='slide', leaves=2)] if sub == 'GF' and L < 2 else [])
    AR.wall(ext, (X1, Y1 - RC), (X1, Y1), 0.0, Z[2], 0.3, 'PC_PanelPearl', 'PC_WallWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.3, 'PC_PanelPearl', 'PC_WallWarm', holes=[(3.0, 5.0, 0.0, 2.6)])
    AR.wall(ext, (X0, Y1), (X0, Y1 - RC), 0.0, Z[2], 0.3, 'PC_PanelPearl', 'PC_WallWarm')
    # floating rounded roof canopy with LED ring
    can = rr(X0 - 2.0, Y0 - 2.5, X1 + 3.0, Y1 + 0.8, RC + 1.5, L)
    A.m(L, 'BUILDING_EXTERIOR', 'Roof').add(bm_prism(rr(X0, Y0, X1, Y1, RC, L), Z[2] - 0.4, Z[2]), 'PC_Ceiling',
                                            mat_fn=mat_by_normal('PC_RoofGravel', 'PC_Ceiling', 'PC_PanelPearl'))
    det.add(bm_prism(can, Z[2] + 0.5, Z[2] + 0.85), 'PC_PanelPearl')
    for (x, y) in ((X0 + 1.0, Y0 + 1.0), (X1 - 1.0, Y0 + 1.0), (X0 + 1.0, Y1 - 1.0), (X1 - 1.0, Y1 - 1.0)):
        AR.column(det, L, x, y, Z[2], Z[2] + 0.5, 0.15, 'PC_Brass')
    if L < 2:
        for (p0, p1) in zip(can, can[1:] + can[:1]):
            M, Ls = seg_frame(p0, p1)
            det.add(bm_box(0, 0.0, Z[2] + 0.45, Ls, 0.08, Z[2] + 0.5), 'PC_LightStrip', matrix=M)
    # balcony support columns (slender brass) at the side terrace corner
    for (x, y) in ((X1 + 4.6, Y0 - 1.0), (X1 + 4.6, Y1 - 3.0), (X0 + 1.0, Y0 - 3.4), (-3.0, Y0 - 3.4), (5.0, Y0 - 3.4)):
        AR.column(det, L, x, y, 0.0, Z[1] - 0.45, 0.13, 'PC_Brass')
    # signage on the balcony parapet
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'PEARL TERRACE', place('-Y', Vector((-3.0, Y0 - 4.02, Z[1] + 0.37))), 0.52, 0.05, 'caladea_b', 'PT_Letter', 'PC_Brass', spacing=1.3)
    if L < 2:
        disc(sg, L, place('-Y', Vector((-9.4, Y0 - 4.04, Z[1] + 0.38)) ), 0.28, 0.06, 'PC_LampGlobe')
    A.sign('parapet_name', (-3.0, Y0 - 4.1, Z[1] + 0.37), 0.52, width=8.0)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Dining')
    gz = 0.15
    AR.spiral_stair(A, L, SPIRAL[0], SPIRAL[1], 2.4, 4.0, gz, Z[1], a0=-90.0, sweep=200.0, tread='PC_FloorMarble', struct='PC_PanelPearl',
                    sub='GrandStair')
    AR.ceiling_panels(A, L, [(X0 + 1.5, Y0 + 1.0, X1 - 1.5, Y1 - 1.0)], Z[1] - 0.45, (3.4, 3.0), w=0.6, d=0.6, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 1.5, Y0 + 1.0, X1 - 1.5, Y1 - 1.0)], Z[2] - 0.4, (3.4, 3.0), w=0.6, d=0.6, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    # reception + chandelier
    F.reception_desk(fu, L, 1.0, 11.5, gz, 0, 2.2, 'PC_PanelPearl', 'PC_StoneTop', 'PC_LightWarm')
    if L < 2:
        for k, (r, z) in enumerate(((1.6, 3.6), (1.1, 3.2), (0.6, 2.8))):
            F.ring_light(fu, L, SPIRAL[0], SPIRAL[1], z + 0.8, r, 0.06, 'PC_LampGlobe')
    # GF dining
    for (x, y) in ((-12.5, 11.0), (-6.0, 12.0), (5.5, 13.0), (7.5, 18.5), (-4.0, 17.5), (2.0, 21.5)):
        F.round_set(fu, L, x, y, gz, 4, 0.55, 'PC_StoneTop', 'PC_Brass', 'PC_LeatherCream')
        F.pendant(fu, L, x, y, Z[1] - 0.45, 1.6, 'globe', 0.24)
    # upper dining (visible through the glass) + balcony dining
    for (x, y) in ((-12.0, 12.0), (-6.0, 11.5), (0.0, 11.0), (6.0, 11.5), (1.0, 17.5), (6.5, 20.0)):
        F.dining_set(fu, L, x, y, Z[1], 0, 2, 1.5, 0.85, 'PC_StoneTop', 'PC_Brass', 'PC_FabricTeal')
        F.pendant(fu, L, x, y, Z[2] - 0.4, 1.4, 'globe', 0.24)
    for x in (-13.0, -8.0, -3.0, 2.0, 7.0):
        F.round_set(fu, L, x, Y0 - 2.2, Z[1], 2, 0.4, 'PC_StoneTop', 'PC_Brass', 'PC_FabricCream', a0=0)
    for y in (8.0, 13.0, 18.0):
        F.round_set(fu, L, X1 + 2.8, y, Z[1], 4, 0.45, 'PC_StoneTop', 'PC_Brass', 'PC_FabricCream')
    # side garden terrace under the balcony (GF): seating + EMPTY stone planters
    tf = A.m(L, 'FURNITURE', 'SideTerrace')
    for y in (9.0, 14.0, 19.0):
        F.round_set(tf, L, X1 + 2.6, y, 0.0, 4, 0.45, 'PC_StoneTop', 'PC_Brass', 'PC_FabricCream')
    for y in (6.0, 11.5, 16.5, 21.5):
        F.empty_planter(tf, L, X1 + 4.9, y - 0.6, X1 + 5.7, y + 0.6, 0.0, 0.6, 'PC_StoneTop')


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -22.0, 22.0)
S.paved(A, 'OPTIONAL_FORECOURT', [(-22.0, 0.0, 22.0, Y0 - 0.0)], 'PC_Travertine', sub='FrontTerrace')
S.paved(A, 'OPTIONAL_FORECOURT', [(X1, Y0, 22.0, Y1)], 'PC_Travertine', sub='SideTerrace')
ff = A.s('OPTIONAL_FORECOURT', 'TerraceFurniture')
for x in (-13.5, -7.5, -1.5, 4.5):
    F.round_set(ff, 0, x, 3.0, 0.0, 4, 0.45, 'PC_StoneTop', 'PC_Brass', 'PC_FabricCream')

for i, (x, y, z, e) in enumerate(((-8, 13, 4.4, 900), (4, 15, 4.4, 900), (-8, 14, 9.0, 900), (4, 15, 9.0, 900))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffe2b8', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'TerraceSoffitL', 'SPOT', (-8.0, Y0 - 2.0, Z[1] - 0.5), 700, '#ffe2b8', spot_deg=110)
A.light('EXTERIOR_LIGHTING', 'TerraceSoffitR', 'SPOT', (X1 + 2.5, 14.0, Z[1] - 0.5), 700, '#ffe2b8', spot_deg=110)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[2])
A.col_box('Balcony', X0 - 1.0, Y0 - 4.0, Z[1] - 0.45, X1 + 6.0, Y1, Z[1] + 1.2)
A.col_box('Canopy', X0 - 2.0, Y0 - 2.5, Z[2] + 0.5, X1 + 3.0, Y1 + 0.8, Z[2] + 0.85)
A.camera('day', (30.0, -22.0, 8.0), (-3.0, 13.0, 4.8), 28)
A.camera('night', (-30.0, -20.0, 4.0), (-1.0, 13.0, 5.0), 28)
A.camera('road', (22.0, -7.6, 1.1), (-3.0, 12.0, 4.4), 24)
A.camera('interior', (8.0, 23.5, 1.7), (-12.0, 12.0, 4.0), 17)
A.checks['probes'] = [dict(name='GF_dining', p=[-6.0, 12.0, 1.0]), dict(name='L1_dining', p=[-6.0, 11.5, Z[1] + 1.0]),
                      dict(name='Stair', p=[SPIRAL[0], SPIRAL[1] - 4.0, 2.5])]
S.finish(A, -22.0, 22.0, width=34.0, depth=22.0, height=Z[2] + 0.85, footprint=[X0 - 1.0, Y0 - 4.0, X1 + 6.0, Y1],
         storeys=2, floor_levels=Z[:2], roof=Z[2], parking='none (front + side terraces beside the pavement)',
         access='pedestrian; no vehicle access', setback_m=4.0, glass='rounded champagne-framed PC_GlassClear walls on both floors',
         concept=__doc__.strip().split('\n')[2])
