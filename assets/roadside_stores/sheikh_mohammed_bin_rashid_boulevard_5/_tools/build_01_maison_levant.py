"""BOULEVARD 01 - MAISON LEVANT (premium Levantine fine dining, 2 storeys, 22 m frontage).

Massing: symmetrical beige-limestone podium frontage of five tall vertical bays between deep stone piers; the four side
bays are two-storey bronze-framed glass (bronze spandrel at the first-floor slab), the central bay is a 7 m tall
recessed entrance (3 m deep stone reveals) under a deep cantilevered bronze canopy.  Stone lintel + attic band with
bronze channel-letter signage, bronze cornice.  Rear tower interface at the back.
Interior: double-height dining hall behind the central glass with chandelier rings, reception counter, banquettes and
round tables; first-floor private dining gallery with glass balustrade over the void; architectural stone/bronze stair.
Site: promenade paving + an optional raised timber dining terrace (left), bollards, empty planters, lighting posts.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

A = new_asset('01', '01_maison_levant', 'maison_levant', 'MaisonLevant', 'Maison Levant', 2)

X0, X1, Y0, Y1 = -11.0, 11.0, 0.0, 18.0
GL = 0.65                                   # glass line (behind the 0.9 m deep stone piers)
Z = [0.15, 5.0, 9.2]                        # GF floor, L1 floor, roof slab top
ATTIC = 11.0
PIERS = [(-11.0, -9.8), (-6.7, -5.8), (-2.7, -1.8), (1.8, 2.7), (5.8, 6.7), (9.8, 11.0)]
BAYS = [(-9.8, -6.7), (-5.8, -2.7), (2.7, 5.8), (6.7, 9.8)]
ENT = (-1.8, 1.8)
VOID = (-5.8, GL + 0.1, 5.8, 5.2)           # double-height zone behind the central bays
STW = (-10.6, 6.5, -8.6, 16.4)              # stair well in the L1 slab


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Stone')
    det = A.m(L, 'FACADE_DETAILS', 'Bronze')
    # ---- slabs + roof
    AR.slab_r(A, L, (X0 + 0.3, GL, X1 - 0.3, Y1 - 0.3), [], Z[0], 0.45, 'PC_FloorMarble', 'PC_Concrete', 'BV_StoneDarkBase', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.3, GL + 0.05, X1 - 0.3, Y1 - 0.3), [VOID, STW], Z[1], 0.4, 'PC_FloorOak', 'BV_PlasterWarm', 'BV_BronzeDark')
    AR.slab_r(A, L, (X0, 0.0, X1, Y1), [], Z[2], 0.5, 'PC_RoofMembrane', 'BV_PlasterWarm', 'BV_Limestone', comp='BUILDING_EXTERIOR', sub='Roof')
    roof_plant(A, L, X0 + 0.5, 1.0, X1 - 0.5, Y1 - 0.5, Z[2])
    # ---- stone frontage: piers, lintel, attic, cornice
    for i, (a, b) in enumerate(PIERS):
        pier(ext, L, (a + b) / 2, b - a, 0.0, 0.9, 0.0, 8.8, 'BV_Limestone', 0.7, cap=False, flute=(i in (2, 3)))
    stone_box(ext, L, X0, 0.0, 8.8, X1, 0.9, ATTIC, 'BV_Limestone', reveal_every=0.6)
    det.add(bm_box(X0 - 0.15, -0.18, ATTIC, X1 + 0.15, 0.9, ATTIC + 0.22), 'BV_Bronze')            # cornice
    det.add(bm_box(X0, -0.08, 8.78, X1, 0.0, 8.86), 'BV_BronzeDark')                                # lintel shadow line
    # ---- two-storey glazed side bays (bronze frames, bronze spandrel at the L1 slab)
    for i, (a, b) in enumerate(BAYS):
        AR.curtain(A, L, [(a, GL), (b, GL)], 0.0, 8.8, (b - a) / 2, [3.6, 7.2], 0.07, 0.2, 'BV_BronzeDark', 'BV_Glass',
                   sub=f'Bay{i}', spandrels=[(4.55, 5.2, 'BV_BronzeDark')])
        if L < 2:     # slim bronze sill + stone threshold
            det.add(bm_box(a, GL - 0.25, 0.0, b, GL, 0.12), 'BV_StoneDarkBase')
    # ---- central recessed entrance (7 m tall, 3 m deep) + transom glazing above
    yb = recessed_portal(A, L, ext, ENT[0], ENT[1], 0.0, 3.0, 7.0, 3.3, 'BV_Limestone', 'BV_BronzeDark', 'BV_Glass', sub='Entrance')
    AR.curtain(A, L, [(ENT[0], GL), (ENT[1], GL)], 7.4, 8.8, 1.2, [], 0.06, 0.16, 'BV_BronzeDark', 'BV_Glass', sub='EntTransom')
    ext.add(bm_box(ENT[0] - 0.35, 0.0, 7.0, ENT[1] + 0.35, 0.9, 7.4), 'BV_Limestone')
    # entrance canopy: deep bronze blade cantilever with tie rods
    canopy(det, L, ENT[0] - 1.6, ENT[1] + 1.6, 0.0, 3.4, 7.05, 0.28, every=1.2)
    if L == 0:
        for x in (ENT[0] - 1.3, ENT[1] + 1.3):
            det.add(bm_cyl_between((x, -3.2, 7.33), (x, 0.0, 8.6), 0.025, 8), 'BV_BronzeDark')
    # ---- party walls, rear wall + tower interface
    AR.wall(ext, (X0, Y1), (X0, 0.9), 0.0, ATTIC, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, 0.9), (X1, Y1), 0.0, ATTIC, 0.3, 'BV_Interface', 'BV_PlasterWarm')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[2], 0.3, 'BV_Interface', 'BV_PlasterWarm', holes=[(17.0, 19.0, 0.0, 2.6)])
    rear_interface(A, L, X0, X1, Y1 - 0.4, ATTIC + 0.22, 1.3)
    # ---- signage on the attic band + monogram plaque at the canopy fascia
    sign_text(A, L, 'MAISON LEVANT', 0.0, 0.0, 9.95, 0.82, 'cinzel', 'BV_LetterBronze', 'BV_BronzeDark', 0.06, spacing=1.18)
    if L < 2:
        sign_text(A, L, 'FINE LEVANTINE DINING', 0.0, -3.42, 7.19, 0.13, 'cinzel', 'BV_LetterGold', 'BV_BronzeDark', 0.015, spacing=1.3)
    interior(L)


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Walls')
    fu = A.m(L, 'FURNITURE', 'Dining')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Decor')
    # back-of-house partition (kitchen beyond, not modelled) with a bronze-lattice feature wall
    AR.wall(st, (X1 - 0.3, 14.6), (-7.6, 14.6), Z[0], Z[1] - 0.4, 0.2, 'BV_PlasterWarm')
    AR.wall(st, (X1 - 0.3, 14.6), (-7.6, 14.6), Z[1], Z[2] - 0.5, 0.2, 'BV_PlasterWarm')
    if L < 2:
        dp.add(bm_box(-4.0, 14.45, Z[0] + 0.4, 4.0, 14.6, Z[1] - 0.8), 'PC_Mashrabiya')
        dp.add(bm_box(-4.2, 14.5, Z[0] + 0.3, 4.2, 14.6, Z[1] - 0.7), 'BV_Halo')
    # ceilings: coffered plaster with warm cove lights
    gf_ceiling = rect_subtract([(X0 + 0.4, GL + 0.2, X1 - 0.4, 14.5)], VOID)
    AR.ceiling_panels(A, L, gf_ceiling, Z[1] - 0.4, (3.2, 2.8), 1.2, 0.18, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [(X0 + 0.4, GL + 0.2, X1 - 0.4, 14.5)], Z[2] - 0.5, (3.4, 3.0), 1.2, 0.18, 'PC_LightWarm', lod2_glow='PC_LightWarm')
    if L < 2:
        for x in (-3.0, 3.0):
            F.ring_light(fu, L, x, 3.0, Z[2] - 2.6, 1.3, 0.07, 'BV_Chandelier')
            F.ring_light(fu, L, x, 3.0, Z[2] - 3.1, 0.9, 0.06, 'BV_Chandelier')
            fu.add(bm_cyl_between((x, 3.0, Z[2] - 0.5), (x, 3.0, Z[2] - 2.6), 0.012, 6), 'BV_BronzeDark')
    # reception counter behind the entrance + host lectern
    F.counter(fu, L, -1.6, 4.4, 1.6, 5.1, Z[0], 1.1, 'BV_BronzeDark', 'PC_StoneTop', 'PC_LightWarm')
    # GF dining: banquettes along the party walls, round + rectangular tables in the hall
    if L < 2:
        for y in (3.0, 6.0, 9.0, 12.0):
            F.booth(fu, L, X1 - 1.2, y, Z[0], 180, 2.2, 'BV_Velvet', 'PC_TimberDark', 'PC_StoneTop')
        for (x, y) in ((-4.2, 3.4), (4.2, 3.4), (-4.2, 7.2), (0.0, 8.0), (4.2, 7.2), (-2.2, 11.4), (2.2, 11.4), (6.6, 10.6)):
            F.round_set(fu, L, x, y, Z[0], 4, 0.55, 'BV_Linen', 'BV_BronzeDark', 'BV_VelvetGreen')
        for y in (9.0, 12.4):
            F.dining_set(fu, L, -6.8, y, Z[0], 90, 2, None, 0.9, 'BV_Linen', 'BV_BronzeDark', 'BV_Velvet')
    else:
        for (x, y) in ((-4.2, 3.4), (4.2, 3.4), (0.0, 8.0)):
            F.table_round(fu, L, x, y, Z[0], 0.6)
    # architectural stair (stone treads, bronze stringers) along the left party wall, mid landing
    AR.stair(A, L, -9.6, 6.6, 90, 1.7, Z[0], Z[1], 'solid', 'BV_Travertine', 'BV_BronzeDark', sub='GrandStair', rails=(False, True))
    # first floor: private dining gallery around the void, glass balustrade, salon
    AR.glass_rail(A, L, [(VOID[0], GL + 0.3), (VOID[0], VOID[3]), (VOID[2], VOID[3]), (VOID[2], GL + 0.3)], Z[1], 1.1,
                  sub='VoidRail', rail='BV_Bronze', shoe='BV_BronzeDark')
    AR.glass_rail(A, L, [(STW[2], STW[1]), (STW[2], STW[3])], Z[1], 1.1, sub='StairRail', rail='BV_Bronze', shoe='BV_BronzeDark')
    if L < 2:
        for (x, y) in ((-7.6, 2.6), (7.6, 2.6)):
            F.round_set(fu, L, x, y, Z[1], 4, 0.55, 'BV_Linen', 'BV_BronzeDark', 'BV_Velvet')
        F.dining_set(fu, L, 0.0, 9.6, Z[1], 0, 4, 5.0, 1.1, 'PC_Walnut', 'BV_BronzeDark', 'BV_VelvetGreen')
        F.dining_set(fu, L, 6.2, 9.6, Z[1], 0, 2, 2.4, 1.0, 'PC_Walnut', 'BV_BronzeDark', 'BV_Velvet')
        F.lounge_group(fu, L, -3.0, 12.6, Z[1], 0, 'BV_VelvetGreen', 'PC_Leather')
        for x in (-2.0, 0.0, 2.0):
            F.pendant(fu, L, x, 9.6, Z[2] - 0.5, 1.2, 'globe', 0.24, 'PC_LampGlobe', 'BV_Bronze')
        F.bottle_shelf(fu, L, 6.0, 14.35, Z[1], 180, 4.0, seed=12)
    # glass partition of the private dining room (L1 right)
    if L < 2:
        A.m(L, 'BUILDING_INTERIOR', 'PartitionGlass').add(bm_box(4.0, 6.0, Z[1], 4.04, 14.4, Z[2] - 0.5), 'BV_GlassWarm')


for L in (0, 1, 2):
    build(L)

# ---- site: promenade + optional terrace (raised deck in front of the two left bays)
promenade(A, X0 - 1.0, X1 + 1.0, entrances=[ENT])
terrace_deck(A, -10.6, -5.6, -3.2, -0.4)
tacc = A.s('OPTIONAL_FORECOURT', 'TerraceFurniture')
for (x, y) in ((-8.6, -2.0), (-5.4, -2.0), (-8.6, -4.4), (-5.4, -4.4)):
    F.round_set(tacc, 0, x, y, 0.15, 2, 0.4, 'BV_Linen', 'BV_BronzeDark', 'BV_VelvetGreen')
for x in (-8.6, -5.4):
    parasol(tacc, 0, x, -3.2, 0.15, 1.6, 2.4)
bollards(A, [-2.6, 2.6, 4.6, 6.6, 8.6], -6.2)
for x in (-12.0, 10.4):
    planter(A, x - 0.6, -2.6, x + 0.6, -1.0)
light_post(A, 0.0, -6.4); light_post(A, -11.6, -6.4); light_post(A, 11.6, -6.4)
bench(A, 6.0, -3.6, 0.0); bench(A, 8.6, -3.6, 0.0)

# ---- lights
for i, (x, y, z, e) in enumerate(((-3.0, 3.0, 7.0, 1600), (3.0, 3.0, 7.0, 1600), (0.0, 9.0, 4.0, 1500), (-6.0, 9.0, 4.0, 1100),
                                  (6.0, 9.0, 4.0, 1100), (-7.6, 2.6, 8.4, 700), (7.6, 2.6, 8.4, 700), (0.0, 10.0, 8.4, 1300),
                                  (0.0, 5.5, 3.6, 700))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#ffd9a8', radius=0.8)
for i, x in enumerate((-8.25, -4.25, 4.25, 8.25)):
    A.light('EXTERIOR_LIGHTING', f'PierWash{i}', 'SPOT', (x, -1.2, 0.2), 450, '#ffd7a0', rot=(-80, 0, 0), spot_deg=38)
A.light('EXTERIOR_LIGHTING', 'SignWash', 'SPOT', (0.0, -3.0, 7.0), 1500, '#ffe0b0', rot=(-55, 0, 0), spot_deg=60)
A.light('EXTERIOR_LIGHTING', 'CanopyDown', 'SPOT', (0.0, -1.8, 6.95), 900, '#ffd9a8', spot_deg=100)

# ---- collision
A.col_box('Podium', X0, 0.0, 0.0, X1, Y1, ATTIC + 0.2)
A.col_box('Canopy', ENT[0] - 1.6, -3.4, 7.05, ENT[1] + 1.6, 0.0, 7.33)

# ---- cameras + interior probes
A.camera('day', (-17.0, -24.0, 7.5), (0.5, 4.0, 5.2), 26)
A.camera('night', (-15.0, -21.0, 4.2), (0.5, 4.0, 5.4), 26)
A.camera('road', (-22.0, -11.5, 1.15), (0.0, 4.0, 4.6), 26)
A.camera('interior', (8.2, 13.2, 2.3), (-3.0, 2.0, 4.6), 17)
A.checks['probes'] = [dict(name='GF_hall', p=[0.0, 7.0, 1.3]), dict(name='GF_banquettes', p=[9.6, 6.0, 1.0]),
                      dict(name='L1_gallery', p=[-7.6, 2.6, 6.2]), dict(name='chandelier', p=[3.0, 3.0, 6.6])]
finish(A, X0 - 1.0, X1 + 1.0, width=22.0, depth=18.0, height=ATTIC + 0.22, footprint=[X0, 0.0, X1, Y1], storeys=2,
       floor_levels=Z[:2], roof=Z[2], parking='none (promenade frontage)', access='pedestrian from the promenade; service via the rear',
       setback_m=0.0, glass='BV_Glass alpha 0.11, bronze frames', concept=__doc__.strip().split('\n')[2],
       frontage_m=22.0, terrace='optional raised timber deck 7.4 x 5.2 m (OPTIONAL_FORECOURT)')
