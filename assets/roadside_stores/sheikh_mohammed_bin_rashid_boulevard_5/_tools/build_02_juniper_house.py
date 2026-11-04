"""BOULEVARD 02 - JUNIPER HOUSE (luxury international restaurant, one tall floor + mezzanine, 30 m frontage).

Massing: a long, low, horizontal frontage - eleven slender travertine mullion-piers on a 3 m grid carry a continuous
6.2 m glass wall; three recessed entrance bays (a 6 m central one where the middle pier is omitted, two 3 m side
ones); a deep 4.6 m bronze canopy runs the FULL length at 4.1 m over a long promenade terrace.  Above the travertine
lintel band the roof steps back behind a vertical bronze fin crown (screened rooftop pavilion) - a different
silhouette from the flat attic of Maison Levant.
Interior: double-height dining hall behind the glass with a timber-rib feature ceiling, central island bar with a
lit back bar, banquette and table arrangements; rear mezzanine dining (glass balustrade) reached by an open stair.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

A = new_asset('02', '02_juniper_house', 'juniper_house', 'JuniperHouse', 'Juniper House', 2)

X0, X1, Y0, Y1 = -15.0, 15.0, 0.0, 20.0
GL = 0.45
Z = [0.15, 4.4, 7.6]                     # GF floor, mezzanine floor, roof slab top
LINTEL = (6.2, 7.6)
CROWN = (7.6, 9.7)
PIERS = [-15.0, -12.0, -9.0, -6.0, -3.0, 3.0, 6.0, 9.0, 12.0, 15.0]
ENTS = [(-9.0, -6.0), (-3.0, 3.0), (6.0, 9.0)]
MEZ = (X0 + 0.3, 10.0, X1 - 0.3, Y1 - 0.3)
STX = (11.45, 12.95)                   # open stair landing zone at the mezzanine edge


def bays():
    xs = PIERS
    out = []
    for a, b in zip(xs[:-1], xs[1:]):
        out.append((a + 0.25, b - 0.25))
    return out


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    AR.slab_r(A, L, (X0 + 0.3, GL, X1 - 0.3, Y1 - 0.3), [], Z[0], 0.45, 'PC_FloorTerrazzo', 'PC_Concrete', 'BV_StoneDarkBase', sub='GroundSlab')
    AR.slab_r(A, L, MEZ, [], Z[1], 0.35, 'PC_FloorOak', 'BV_PlasterWarm', 'BV_BronzeDark', sub='Mezzanine')
    AR.slab_r(A, L, (X0, 0.0, X1, Y1), [], Z[2], 0.5, 'PC_RoofMembrane', 'BV_PlasterWarm', 'BV_Travertine', comp='BUILDING_EXTERIOR', sub='Roof')
    # ---- slender travertine piers + lintel band
    for x in PIERS:
        w = 0.5 if abs(x) < 15 else 0.7
        xc = x if abs(x) < 15 else x - math.copysign(0.1, x)
        pier(ext, L, xc, w, 0.0, 0.6, 0.0, LINTEL[0], 'BV_Travertine', 0.45, cap=False)
    stone_box(ext, L, X0, 0.0, LINTEL[0], X1, 0.7, LINTEL[1] + 0.1, 'BV_Travertine', reveal_every=0.45)
    det.add(bm_box(X0 - 0.1, -0.12, LINTEL[1] + 0.1, X1 + 0.1, 0.8, LINTEL[1] + 0.26), 'BV_Bronze')
    # ---- continuous glass between the piers (non-entrance bays)
    for i, (a, b) in enumerate(bays()):
        if any(abs((a + b) / 2 - (e0 + e1) / 2) < 0.6 for e0, e1 in ENTS):
            continue
        AR.curtain(A, L, [(a, GL), (b, GL)], 0.0, LINTEL[0], (b - a) / 2, [3.7], 0.05, 0.16, 'BV_BronzeDark', 'BV_Glass', sub=f'Bay{i}')
    # ---- recessed entrance bays (1.8 m deep), central one 6 m wide
    for k, (a, b) in enumerate(ENTS):
        a2, b2 = a + (0.25 if k != 1 else 0.25), b - 0.25
        recessed_portal(A, L, ext, a2, b2, 0.0, 1.8, 5.6, 3.0, 'BV_Travertine', 'BV_BronzeDark', 'BV_Glass', sub=f'Entrance{k}',
                        leaves=2 if k == 1 else 1)
        AR.curtain(A, L, [(a2, GL), (b2, GL)], 5.95, LINTEL[0], (b2 - a2) / (3 if k == 1 else 1), [], 0.05, 0.14, 'BV_BronzeDark',
                   'BV_Glass', sub=f'EntTransom{k}')
        ext.add(bm_box(a2 - 0.35, 0.0, 5.6, b2 + 0.35, 0.6, 5.95), 'BV_Travertine')
    # ---- full-length horizontal canopy (bronze, timber soffit) at 4.1 m
    canopy(det, L, X0 + 0.2, X1 - 0.2, 0.0, 4.6, 4.1, 0.32, 'BV_BronzeDark', 'PC_WoodSlat', every=2.0, fascia='BV_Bronze')
    if L < 2:
        for x in np.arange(X0 + 1.5, X1, 3.0):
            det.add(bm_box(x - 0.03, -4.55, 4.42, x + 0.03, 0.0, 4.48), 'BV_Bronze')       # top ribs
    # ---- stepped crown: travertine band + recessed vertical bronze fin screen + cap
    stone_box(ext, L, X0, 0.0, LINTEL[1] + 0.26, X1, 0.8, 8.2, 'BV_Travertine')
    fz0, fz1 = 8.2, CROWN[1] - 0.12
    ext.add(bm_box(X0 + 1.0, 1.6, Z[2], X1 - 1.0, 2.0, fz1), 'BV_BronzeDark')                     # screen backing
    if L < 2:
        step = 0.42 if L == 0 else 0.84
        for x in np.arange(X0 + 1.2, X1 - 1.0, step):
            det.add(bm_box(x - 0.04, 1.1, fz0, x + 0.04, 1.6, fz1), 'BV_Bronze')
    det.add(bm_box(X0 + 0.9, 1.0, fz1, X1 - 0.9, 2.1, CROWN[1]), 'BV_Bronze')
    # ---- party walls, rear + interface
    AR.wall(ext, (X0, Y1), (X0, 0.7), 0.0, 8.2, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, 0.7), (X1, Y1), 0.0, 8.2, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.3, 'BV_Interface', 'BV_PlasterWarm', holes=[(24.0, 26.0, 0.0, 2.6)])
    rear_interface(A, L, X0, X1, Y1 - 0.4, CROWN[1], 2.0)
    roof_plant(A, L, X0 + 0.5, 2.2, X1 - 0.5, Y1 - 0.5, Z[2])
    # ---- signage: garamond letters on the travertine band above the central entrance + canopy fascia names
    sign_text(A, L, 'JUNIPER HOUSE', 0.0, 0.0, 7.4, 0.7, 'garamond_sb', 'BV_LetterGold', 'BV_BronzeDark', 0.06, spacing=1.12)
    if L < 2:
        for x in (-7.5, 7.5):
            sign_text(A, L, 'JUNIPER', x, -4.62, 4.26, 0.16, 'garamond_sb', 'BV_LetterGold', 'BV_BronzeDark', 0.015, spacing=1.3)
    interior(L)


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Walls')
    fu = A.m(L, 'FURNITURE', 'Dining')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Bar')
    AR.wall(st, (X1 - 0.3, 17.4), (X0 + 0.3, 17.4), Z[0], Z[1] - 0.35, 0.2, 'PC_WoodSlat')       # kitchen screen (GF)
    AR.wall(st, (X1 - 0.3, 18.6), (X0 + 0.3, 18.6), Z[1], Z[2] - 0.5, 0.2, 'BV_PlasterWarm')
    # feature ceiling over the double-height hall: timber ribs + cove light lines
    if L < 2:
        step = 0.6 if L == 0 else 1.2
        for x in np.arange(X0 + 0.6, X1 - 0.4, step):
            st.add(bm_box(x - 0.05, GL + 0.3, Z[2] - 0.95, x + 0.05, 9.9, Z[2] - 0.5), 'PC_Walnut')
        for y in (2.6, 5.4, 8.2):
            st.add(bm_box(X0 + 0.5, y - 0.04, Z[2] - 0.98, X1 - 0.5, y + 0.04, Z[2] - 0.93), 'PC_LightWarm')
    else:
        st.add(bm_hquad(X0 + 0.5, GL + 0.3, X1 - 0.5, 9.9, Z[2] - 0.6, down=True), 'PC_LightWarm')
    st.add(bm_hquad(X0 + 0.3, GL + 0.2, X1 - 0.3, 10.0, Z[2] - 0.5, down=True), 'PC_Walnut')
    AR.ceiling_panels(A, L, [(X0 + 0.5, 10.2, X1 - 0.5, 17.2)], Z[1] - 0.35, (3.0, 2.6), 1.0, 0.16, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.5, 10.2, X1 - 0.5, 18.4)], Z[2] - 0.5, (3.0, 2.8), 1.0, 0.16, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    # central island bar + back bar
    F.counter(dp, L, -4.5, 7.6, 4.5, 9.2, Z[0], 1.1, 'PC_TimberDark', 'PC_StoneTop', 'PC_LightWarm')
    if L < 2:
        for x in np.arange(-4.0, 4.2, 0.8):
            F.stool(dp, L, x, 7.1, Z[0], 0.78, 'BV_BronzeDark', 'PC_LeatherBlack')
        F.bottle_shelf(dp, L, 0.0, 10.15, Z[0], 0, 7.0, seed=21)
        for x in (-3.0, 0.0, 3.0):
            F.pendant(dp, L, x, 8.4, Z[1] - 0.35, 0.8, 'cone', 0.22, 'PC_LampGlobe', 'BV_Bronze')
    # dining arrangements: banquettes on both party walls, tables in rows, round tables near the glass
    if L < 2:
        for y in (2.4, 5.0, 7.6, 10.2, 12.8, 15.4):
            F.booth(fu, L, X0 + 1.2, y, Z[0], 0, 2.0, 'BV_VelvetBlue', 'PC_TimberDark', 'PC_StoneTop')
            F.booth(fu, L, X1 - 1.2, y, Z[0], 180, 2.0, 'BV_VelvetBlue', 'PC_TimberDark', 'PC_StoneTop')
        for x in (-10.5, -7.5, -4.5, 4.5, 7.5, 9.8):
            F.round_set(fu, L, x, 2.6, Z[0], 4, 0.5, 'PC_StoneTop', 'BV_BronzeDark', 'BV_Linen')
        for x in (-9.0, -6.0, 6.0, 8.2):
            F.dining_set(fu, L, x, 5.6, Z[0], 0, 2, 1.8, 0.9, 'PC_Walnut', 'BV_BronzeDark', 'BV_VelvetGreen')
        for x in (-8.0, -3.0, 3.0):
            F.dining_set(fu, L, x, 13.4, Z[0], 0, 3, 2.8, 1.0, 'PC_Walnut', 'BV_BronzeDark', 'BV_Linen')
    else:
        for x in (-7.5, 0.0, 7.5):
            F.table_rect(fu, L, x, 5.0, Z[0], 0, 2.4, 1.0)
    # open stair to the mezzanine + mezzanine dining with glass balustrade
    AR.stair(A, L, 12.2, 3.04, 90, 1.5, Z[0], Z[1], 'floating', 'PC_FloorOak', 'BV_BronzeDark', sub='MezzStair')
    AR.glass_rail(A, L, [(MEZ[0], MEZ[1]), (STX[0], MEZ[1])], Z[1], 1.05, sub='MezzRail', rail='BV_Bronze', shoe='BV_BronzeDark')
    AR.glass_rail(A, L, [(STX[1], MEZ[1]), (MEZ[2], MEZ[1])], Z[1], 1.05, sub='MezzRailR', rail='BV_Bronze', shoe='BV_BronzeDark')
    if L < 2:
        for x in (-12.0, -8.5, -5.0, -1.5, 2.0, 5.5):
            F.round_set(fu, L, x, 11.6, Z[1], 4, 0.5, 'PC_StoneTop', 'BV_BronzeDark', 'BV_VelvetGreen')
        for x in (-10.0, -4.0, 2.0):
            F.lounge_group(fu, L, x, 15.6, Z[1], 0, 'BV_Linen', 'PC_Leather')
        for x in np.arange(-12.0, 8.0, 3.5):
            F.pendant(fu, L, x, 11.6, Z[2] - 0.5, 1.0, 'globe', 0.2, 'PC_LampGlobe', 'BV_Bronze')


for L in (0, 1, 2):
    build(L)

# ---- site: promenade, long terrace deck under the canopy, street furniture
promenade(A, X0 - 1.0, X1 + 1.0, entrances=ENTS)
terrace_deck(A, X0 + 0.6, -4.3, -9.3, -0.3, sub='DeckL')
terrace_deck(A, -5.7, -4.3, -3.3, -0.3, sub='DeckC1')
terrace_deck(A, 3.3, -4.3, 5.7, -0.3, sub='DeckC2')
terrace_deck(A, 9.3, -4.3, X1 - 0.6, -0.3, sub='DeckR')
tacc = A.s('OPTIONAL_FORECOURT', 'TerraceFurniture')
for x in (-13.0, -11.0, 11.0, 13.0, -4.5, 4.5):
    for y in (-1.5, -3.2):
        F.round_set(tacc, 0, x, y, 0.15, 2, 0.38, 'PC_StoneTop', 'BV_BronzeDark', 'BV_Linen')
bollards(A, [-15.5, -10.5, 10.5, 15.5], -6.3)
for x in (-12.0, 0.0, 12.0):
    light_post(A, x, -6.4)
planter(A, -8.6, -6.2, -6.4, -5.2); planter(A, 6.4, -6.2, 8.6, -5.2)

# ---- lights
for i, (x, y, z, e) in enumerate(((-9.0, 4.0, 6.0, 1400), (0.0, 4.0, 6.0, 1600), (9.0, 4.0, 6.0, 1400), (0.0, 8.4, 3.2, 900),
                                  (-8.0, 13.0, 3.4, 900), (6.0, 13.0, 3.4, 900), (-6.0, 13.0, 6.6, 900), (4.0, 13.0, 6.6, 900))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffd6a0', radius=0.8)
for i, x in enumerate(np.arange(-12.0, 13.0, 6.0)):
    A.light('EXTERIOR_LIGHTING', f'CanopyDown{i}', 'SPOT', (float(x), -2.3, 4.05), 700, '#ffd7a0', spot_deg=110)
A.light('EXTERIOR_LIGHTING', 'CrownWash', 'SPOT', (0.0, -3.6, 4.5), 1800, '#ffe0b0', rot=(-62, 0, 0), spot_deg=80)

A.col_box('Podium', X0, 0.0, 0.0, X1, Y1, CROWN[1])
A.col_box('Canopy', X0 + 0.2, -4.6, 4.1, X1 - 0.2, 0.0, 4.42)

A.camera('day', (-22.0, -27.0, 7.0), (0.0, 5.0, 4.2), 24)
A.camera('night', (-19.0, -24.0, 3.6), (0.0, 5.0, 4.0), 24)
A.camera('road', (-26.0, -11.0, 1.15), (0.0, 4.0, 3.6), 24)
A.camera('interior', (-13.6, 2.8, 2.0), (5.0, 12.0, 3.6), 17)
A.checks['probes'] = [dict(name='GF_hall', p=[-6.0, 5.6, 1.2]), dict(name='bar', p=[0.0, 8.4, 1.3]),
                      dict(name='mezzanine', p=[-5.0, 11.6, 5.4]), dict(name='GF_right', p=[9.0, 5.6, 1.2])]
finish(A, X0 - 1.0, X1 + 1.0, width=30.0, depth=20.0, height=CROWN[1], footprint=[X0, 0.0, X1, Y1], storeys=1,
       storey_note='one tall floor (7.6 m) + rear mezzanine', floor_levels=Z[:2], roof=Z[2], parking='none (promenade frontage)',
       access='three recessed pedestrian entrances from the promenade; service via the rear', setback_m=0.0,
       glass='BV_Glass alpha 0.11, bronze frames', concept=__doc__.strip().split('\n')[2], frontage_m=30.0,
       terrace='long timber terrace decks under the 4.6 m canopy (OPTIONAL_FORECOURT)')
