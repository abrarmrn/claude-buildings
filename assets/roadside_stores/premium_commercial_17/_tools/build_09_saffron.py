"""ASSET 09 - Saffron Courtyard (premium contemporary Asian restaurant, 2 levels).

Massing: 38 m frontage whose middle 10 m is carved back 6 m into an entrance COURTYARD with a reflecting pool and
stepping stones.  The ground floor is a long bronze-framed horizontal glass band; the upper dining level is veiled by
dense dark-timber vertical battens (strong vertical rhythm).  The whole is crowned by three stacked, progressively
smaller roof plates with upturned edges and corners (contemporary pagoda silhouette).
Inside: sushi / display counter, private dining rooms behind timber lattice screens, paper-lantern pendants,
straight stair to the upper dining room.
Site: compact drop-off lay-by in front of the courtyard (in/out crossings), no parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('09', '09_saffron_courtyard', 'saffron_courtyard', 'P09', 'SaffronCourtyard', 'Saffron Courtyard', 2)
defmat('SF_Saffron', '#e2a12a', 0.3, 0.6, emit='#ffb43a', es=3.0)
defmat('SF_Paper', '#f4e6cc', 0.6, emit='#ffcf8a', es=5.0)
defmat('SF_Red', '#7c1d18', 0.5)

X0, X1, Y0, Y1 = -19.0, 19.0, 6.0, 28.0
CX, CD = 5.0, 6.0                    # courtyard half width / depth
Z = [0.15, 5.2, 9.4]
ST = (-18.5, 15.5, -16.6, 24.5)


def foot():
    return [(X0, Y0), (-CX, Y0), (-CX, Y0 + CD), (CX, Y0 + CD), (CX, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    det = A.m(L, 'FACADE_DETAILS', 'Timber')
    A.m(L, 'BUILDING_INTERIOR', 'GroundSlab').add(bm_prism(foot(), -0.3, Z[0]), 'PC_FloorOak',
                                                   mat_fn=mat_by_normal('PC_FloorOak', 'PC_Concrete', 'PC_StoneDark'))
    l1 = [(X0 + 0.3, Y0 + 1.6), (-CX - 0.3, Y0 + 1.6), (-CX - 0.3, Y0 + CD + 1.0), (CX + 0.3, Y0 + CD + 1.0), (CX + 0.3, Y0 + 1.6),
          (X1 - 0.3, Y0 + 1.6), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)]
    AR.slab(A, L, l1, Z[1], 0.4, [AR.poly_rect(*ST)], 'PC_FloorOak', 'PC_TimberDark', 'PC_TimberDark')
    A.m(L, 'BUILDING_EXTERIOR', 'Roof').add(bm_prism(foot(), Z[2] - 0.4, Z[2]), 'PC_TimberDark',
                                            mat_fn=mat_by_normal('PC_RoofGravel', 'PC_TimberDark', 'PC_TimberDark'))
    # GF glazing band (bronze, horizontal transom) on all front segments; L1 glazing behind timber battens
    fsegs = foot()[:6]
    for z0, z1, sub, tr in ((0.0, Z[1] - 0.5, 'GF', [2.6]), (Z[1] + 0.1, Z[2] - 0.45, 'L1', [])):
        AR.curtain(A, L, fsegs, z0, z1, 2.4, tr, 0.07, 0.18, 'PC_Bronze', 'PC_Glass', sub=sub,
                   doors=[dict(seg=2, u0=3.5, u1=6.5, h=2.6, kind='slide')] if sub == 'GF' else [])
    # floor band (fascia with sign) and roof band
    for (p0, p1) in zip(fsegs[:-1], fsegs[1:]):
        M, Ls = seg_frame(p0, p1)
        ext.add(bm_box(-0.1, -0.35, Z[1] - 0.5, Ls + 0.1, 0.1, Z[1] + 0.1), 'PC_TimberDark', matrix=M)
        if L < 2:   # dense vertical timber battens over the upper level
            n = int(Ls / 0.32)
            for k in range(n + 1):
                u = k * Ls / max(1, n)
                if L == 1 and k % 2:
                    continue
                det.add(bm_box(u - 0.035, -0.45, Z[1] + 0.1, u + 0.035, -0.25, Z[2] - 0.4), 'PC_TimberDark', matrix=M)
        else:
            det.add(bm_box(0, -0.4, Z[1] + 0.1, Ls, -0.3, Z[2] - 0.4), 'PC_LatticeTimber', matrix=M)
    AR.wall(ext, (X1, Y0), (X1, Y1), 0.0, Z[2], 0.35, 'PC_TimberDark', 'PC_WallWarm', holes=[(3.0, 12.0, 1.0, 4.0)])
    AR.curtain(A, L, [(X1 + 0.01, Y0 + 3.0), (X1 + 0.01, Y0 + 12.0)], 1.0, 4.0, 3.0, [], 0.07, 0.15, 'PC_Bronze', 'PC_Glass', sub='Side')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.35, 'PC_TimberDark', 'PC_WallWarm', holes=[(4.0, 6.0, 0.0, 2.6)])
    AR.wall(ext, (X0, Y1), (X0, Y0), 0.0, Z[2], 0.35, 'PC_TimberDark', 'PC_WallWarm')
    # stacked upturned roof plates
    for k, (inset, zb, th, lift) in enumerate(((-3.0, Z[2] + 0.1, 0.35, 0.9), (2.5, Z[2] + 1.15, 0.3, 0.7), (6.5, Z[2] + 2.05, 0.28, 0.5))):
        x0, x1 = X0 - (3.0 if k == 0 else -inset), X1 + (3.0 if k == 0 else -inset)
        y0, y1 = Y0 - (3.0 if k == 0 else -inset * 0.6), Y1 + (2.0 if k == 0 else -inset * 0.6)
        cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2

        def zt(x, y, zb=zb, th=th, lift=lift, cx=cx, cy=cy, hx=hx, hy=hy):
            u, v = abs(x - cx) / hx, abs(y - cy) / hy
            return zb + th + lift * (u ** 6 + v ** 6) * 0.5 + lift * 0.5 * (u ** 6) * (v ** 6)
        nx, ny = {0: (24, 16), 1: (12, 8), 2: (6, 4)}[L]
        AR.heightfield_slab(A.m(L, 'BUILDING_EXTERIOR', 'RoofPlates'), (x0, x1), lambda x, y0=y0: y0, lambda x, y1=y1: y1, zt, th, nx, ny,
                            'PC_SteelDark', 'PC_TimberDark', 'PC_Bronze')
        if k > 0:
            AR.box(ext, cx - hx * 0.6, cy - hy * 0.6, Z[2], cx + hx * 0.6, cy + hy * 0.6, zb + 0.05, 'PC_TimberDark')
    # courtyard: reflecting pool + stepping stones + timber screen walls
    cy0 = Y0 + 0.05
    ext.add(bm_box(-CX + 0.3, cy0, -0.25, CX - 0.3, Y0 + CD - 1.6, -0.05), 'PC_StoneDark')
    ext.add(bm_hquad(-CX + 0.4, cy0 + 0.1, CX - 0.4, Y0 + CD - 1.7, -0.08), 'PC_Water')
    for k in range(4):
        y = Y0 + 0.6 + k * 1.05
        ext.add(bm_box(-0.7 + (k % 2) * 0.3, y, -0.25, 0.7 + (k % 2) * 0.3, y + 0.7, 0.02), 'PC_StoneTop')
    ext.add(bm_box(-CX + 0.3, Y0 + CD - 1.6, -0.25, CX - 0.3, Y0 + CD, 0.02), 'PC_StoneTop')
    # signage
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'SAFFRON COURTYARD', place('-Y', Vector((-12.0, Y0 - 0.37, Z[1] - 0.2))), 0.5, 0.05, 'caladea_b', 'SF_Saffron', 'PC_Brass', spacing=1.15)
    txt(sg, L, 'SAFFRON', place('-Y', Vector((0.0, Y0 + CD - 0.37, Z[1] - 0.2))), 0.46, 0.05, 'caladea_b', 'SF_Saffron', 'PC_Brass', spacing=1.3)
    if L < 2:
        poly(sg, [(math.cos(a) * 0.45, math.sin(a) * 0.45) for a in [2 * math.pi * i / 16 for i in range(16)]], 0.04,
             place('-Y', Vector((-12.0 + 6.3, Y0 - 0.37, Z[1] - 0.2))), 'SF_Saffron')
    A.sign('fascia_name', (-12.0, Y0 - 0.45, Z[1] - 0.2), 0.5, width=9.0)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Dining')
    st = A.m(L, 'BUILDING_INTERIOR', 'Screens')
    gz = Z[0]
    AR.stair(A, L, -17.55, ST[1], 90, 1.5, gz, Z[1], 'solid', 'PC_FloorOak', 'PC_TimberDark', sub='Stair', max_flight=6.0, rails=(False, True))
    AR.glass_rail(A, L, [(ST[2], ST[3]), (ST[2], ST[1]), (ST[0], ST[1])], Z[1], glass='PC_GlassRail', rail='PC_Bronze')
    AR.ceiling_panels(A, L, [(X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5)], Z[1] - 0.4, (3.6, 3.0), w=0.5, d=0.5, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.5, Y0 + 2.0, X1 - 0.5, Y1 - 0.5)], Z[2] - 0.4, (3.6, 3.0), w=0.5, d=0.5, mat='PC_LightWarm',
                      lod2_glow='PC_LightWarm')
    # display / sushi counter with backlit saffron wall
    F.counter(fu, L, -8.0, 23.5, 8.0, 24.4, gz, 1.1, 'PC_TimberDark', 'PC_StoneTop', 'SF_Saffron')
    if L < 2:
        F.display_case(fu, L, -6.0, 23.6, 6.0, 24.3, gz + 1.1, 0.35, 'PC_TimberDark', 'PC_GlassClear', 'PC_LightWarm', 'PC_CarPaintOrange')
    AR.box(st, -9.0, Y1 - 0.6, gz, 9.0, Y1 - 0.4, Z[1] - 0.4, 'SF_Saffron' if L == 2 else 'PC_TimberDark')
    if L < 2:
        st.add(bm_vquad(-8.6, 8.6, 1.4, 4.4, Y1 - 0.62, '-Y'), 'SF_Paper')
        for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
            F.stool(fu, L, x, 22.7, gz, 0.75, 'PC_Bronze', 'PC_FabricRust')
    # private dining rooms (right) behind timber lattice screens
    for x0 in (9.0, 14.0):
        for (p0, p1) in (((x0, 14.0), (x0 + 4.6, 14.0)), ((x0, 14.0), (x0, 21.0))):
            M, Ls = seg_frame(p0, p1)
            st.add(bm_box(0, -0.04, gz, Ls, 0.04, 3.2), 'PC_LatticeTimber' if L < 2 else 'PC_TimberDark', matrix=M)
            st.add(bm_box(0, -0.06, 3.2, Ls, 0.06, 3.35), 'PC_TimberDark', matrix=M)
        F.dining_set(fu, L, x0 + 2.3, 17.5, gz, 90, 3, None, 1.0, 'PC_TimberDark', 'PC_TimberDark', 'SF_Red', ends=True)
        F.pendant(fu, L, x0 + 2.3, 17.5, Z[1] - 0.4, 1.6, 'cyl', 0.35, 'SF_Paper', 'PC_AluBlack')
    # main dining
    for x in (-15.0, -10.5, -6.0, 6.5, 11.0, 15.5):
        F.dining_set(fu, L, x, 9.0 if abs(x) > 6 else 13.5, gz, 0, 2, 1.4, 0.8, 'PC_TimberDark', 'PC_TimberDark', 'PC_FabricCream')
    for (x, y) in ((-12.5, 15.0), (-8.0, 18.5), (-3.0, 16.5), (2.5, 16.5), (-13.0, 20.5)):
        F.round_set(fu, L, x, y, gz, 4, 0.55, 'PC_TimberDark', 'PC_TimberDark', 'SF_Red')
        F.pendant(fu, L, x, y, Z[1] - 0.4, 1.8, 'cyl', 0.3, 'SF_Paper', 'PC_AluBlack')
    # upper dining level
    for x in (-12.0, -7.0, -2.0, 3.0, 8.0, 13.0):
        F.dining_set(fu, L, x, 10.5, Z[1], 0, 2, 1.4, 0.8, 'PC_TimberDark', 'PC_TimberDark', 'SF_Red')
        F.pendant(fu, L, x, 10.5, Z[2] - 0.4, 1.4, 'cyl', 0.3, 'SF_Paper', 'PC_AluBlack')
    for x in (-10.0, -2.0, 6.0, 14.0):
        F.round_set(fu, L, x, 19.0, Z[1], 6, 0.75, 'PC_TimberDark', 'PC_TimberDark', 'PC_FabricCream')


for L in (0, 1, 2):
    build(L)

S.sidewalk(A, -26.0, 26.0, crossings=[(-14.0, -10.0), (10.0, 14.0)])
S.asphalt(A, 'OPTIONAL_FORECOURT', [(-14.0, 0.0, 14.0, 3.2)], sub='DropOff')
S.paved(A, 'OPTIONAL_FORECOURT', [(-26.0, 0.0, -14.0, Y0), (14.0, 0.0, 26.0, Y0), (-14.0, 3.2, 14.0, Y0)], 'PC_StoneSand', sub='Paving')
S.arrow(A, 'OPTIONAL_FORECOURT', 0.0, 1.6, 0, 4.0, sub='DropOffMarks')
for x in (-9.0, -5.0, 5.0, 9.0):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 3.6, 0.0, 0.9, 0.1, 'PC_TimberDark', 'PC_LightWarm')

for i, (x, y, z, e) in enumerate(((-11, 12, 4.6, 900), (0, 18, 4.6, 900), (11, 12, 4.6, 900), (-10, 14, 8.8, 900), (8, 14, 8.8, 900))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffd6a0', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'CourtyardDown', 'SPOT', (0.0, Y0 + 2.0, Z[2] + 0.05), 900, '#ffd6a0', spot_deg=90)
A.light('EXTERIOR_LIGHTING', 'PoolGlow', 'POINT', (0.0, Y0 + 2.0, 0.3), 120, '#ffc070', radius=1.5)
A.col_box('Main', X0, Y0, 0, X1, Y1, Z[2] + 2.6)
A.camera('day', (-36.0, -24.0, 9.0), (0.0, 14.0, 5.0), 28)
A.camera('night', (30.0, -22.0, 4.5), (0.0, 14.0, 5.0), 28)
A.camera('road', (-24.0, -7.6, 1.1), (0.0, 12.0, 4.0), 24)
A.camera('interior', (7.5, 9.0, 1.7), (-6.0, 24.0, 2.4), 17)
A.checks['probes'] = [dict(name='GF_dining_L', p=[-10.5, 9.0, 1.0]), dict(name='GF_dining_R', p=[11.0, 9.0, 1.0]),
                      dict(name='L1_dining', p=[-7.0, 10.5, Z[1] + 1.0]), dict(name='Courtyard_entrance', p=[0.0, Y0 + CD + 1.0, 1.4])]
S.finish(A, -26.0, 26.0, width=44.0, depth=27.0, height=Z[2] + 2.9, footprint=[X0, Y0, X1, Y1],
         storeys=2, floor_levels=Z[:2], roof='stacked upturned plates, top 12.3 m', parking='none - compact drop-off lay-by (OPTIONAL_FORECOURT)',
         access='in/out crossings to a drop-off lay-by in front of the courtyard', setback_m=6.0,
         glass='GF bronze-framed PC_Glass band + L1 glass behind timber battens', concept=__doc__.strip().split('\n')[2])
