"""ASSET 01 - Mercedes-Benz flagship showroom (3 storeys).

Massing: 42 m glass box + 6 m dark-granite brand core rising to 20.6 m on the right; a floating white roof plate
(rounded corners) hovers over the glass box on four slender portico columns.  Central double-height atrium (GF + L1)
with a sculptural floating stair; L1 side galleries with display cars; L2 full-width lounge band with vertical fins.
Separate entrances: 6 m sliding vehicle door (left) + customer entrance in the granite core under a blade canopy.
Site: narrow 8 m display forecourt (vehicle crossing on the left), side driveway on the right to the rear service yard,
optional side parking (11 bays) as a separate collection.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('01', '01_mercedes_showroom', 'mercedes_showroom', 'P01', 'MercedesShowroom', 'Mercedes-Benz Flagship Showroom', 3)
defmat('MB_Letter', '#f4f6f8', 0.3, emit='#f2f6ff', es=5.0)
defmat('MB_StarGlow', '#e9edf1', 0.15, 0.6, emit='#eef3ff', es=3.5)

X0, X1, Y0, Y1 = -24.0, 18.0, 8.0, 36.0          # glass box
CX0, CX1 = 18.0, 24.0                              # granite core
Z = [0.15, 6.6, 11.6, 16.2]                        # floor tops + roof top
ATR = (-10.0, Y0, 8.0, 22.0)                        # atrium void in L1 slab
STAIR2 = (9.0, 24.0, 11.4, 33.8)                    # stair well in L2 slab


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    core = A.m(L, 'BUILDING_EXTERIOR', 'GraniteCore')
    det = A.m(L, 'FACADE_DETAILS', 'RoofPlate')
    # ---- slabs
    AR.slab_r(A, L, (X0 + 0.1, Y0 + 0.1, X1, Y1 - 0.1), [], Z[0], 0.45, 'PC_FloorDark', 'PC_Concrete', 'PC_StoneDark', sub='GroundSlab')
    AR.slab_r(A, L, (X0 + 0.1, Y0 + 0.1, X1, Y1 - 0.1), [ATR], Z[1], 0.4, 'PC_FloorMarble', 'PC_Ceiling', 'PC_PanelWhite')
    AR.slab_r(A, L, (X0 + 0.1, Y0 + 0.1, X1, Y1 - 0.1), [STAIR2], Z[2], 0.4, 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelWhite')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], Z[3], 0.5, 'PC_RoofGravel', 'PC_Ceiling', 'PC_PanelWhite', comp='BUILDING_EXTERIOR', sub='Roof')
    AR.parapet(ext, AR.poly_rect(X0, Y0, X1, Y1), Z[3], 0.9, 0.3, 'PC_PanelWhite')
    # ---- front curtain wall: left wing / atrium / right wing (atrium has no L1 spandrel -> reads double height)
    fins = dict(depth=0.55, t=0.07, every=1, mat='PC_AluSilver', z0=Z[2] - 0.4, z1=Z[3] - 0.1)
    span = [(Z[1] - 0.45, Z[1] + 0.05, 'PC_AluSilver'), (Z[2] - 0.45, Z[2] + 0.05, 'PC_AluSilver')]
    AR.curtain(A, L, [(X0, Y0), (ATR[0], Y0)], 0.0, Z[3] - 0.5, 2.0, [3.4, Z[1] + 2.4], 0.07, 0.2, 'PC_AluSilver', 'PC_Glass',
               sub='Front', spandrels=span, fins=fins,
               doors=[dict(seg=0, u0=4.0, u1=10.0, h=4.6, kind='slide', leaves=2)])
    AR.curtain(A, L, [(ATR[0], Y0), (ATR[2], Y0)], 0.0, Z[3] - 0.5, 2.25, [6.4], 0.07, 0.22, 'PC_AluSilver', 'PC_Glass',
               sub='Atrium', spandrels=[span[1]], fins=fins)
    AR.curtain(A, L, [(ATR[2], Y0), (X1, Y0)], 0.0, Z[3] - 0.5, 2.0, [3.4, Z[1] + 2.4], 0.07, 0.2, 'PC_AluSilver', 'PC_Glass',
               sub='FrontR', spandrels=span, fins=fins)
    # left side: glass for the front 14 m, granite behind
    AR.curtain(A, L, [(X0, 22.0), (X0, Y0)], 0.0, Z[3] - 0.5, 2.0, [3.4, Z[1] + 2.4], 0.07, 0.2, 'PC_AluSilver', 'PC_Glass',
               sub='Left', spandrels=span)
    AR.wall(ext, (X0, Y1), (X0, 22.0), 0.0, Z[3] + 0.9, 0.35, 'PC_StoneDark', 'PC_WallWhite')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, Z[3] + 0.9, 0.35, 'PC_PanelWhite', 'PC_WallWhite',
            holes=[(26.0, 31.0, 0.0, 4.6)])
    # ---- granite brand core (customer entrance, stair/lift tower), rises to 20.6 m at the front
    AR.wall(core, (CX0, Y0), (CX1, Y0), 0.0, 20.6, 0.4, 'PC_StoneDark', 'PC_WallWarm', holes=[(1.4, 4.6, 0.0, 3.6)])
    AR.wall(core, (CX1, Y0), (CX1, 15.0), 0.0, 20.6, 0.4, 'PC_StoneDark', 'PC_WallWarm')
    AR.wall(core, (CX1, 15.0), (CX1, Y1), 0.0, Z[3] + 0.9, 0.4, 'PC_StoneDark', 'PC_WallWarm')
    AR.wall(core, (CX1, Y1), (CX0, Y1), 0.0, Z[3] + 0.9, 0.4, 'PC_StoneDark', 'PC_WallWarm')
    AR.wall(core, (CX0, 15.0), (CX0, Y0), Z[3], 20.6, 0.4, 'PC_StoneDark', 'PC_StoneDark')
    AR.box(core, CX0, 15.0 - 0.4, Z[3], CX1, 15.0, 20.6, 'PC_StoneDark')
    AR.box(core, CX0 - 0.1, Y0 - 0.1, 20.6, CX1 + 0.1, 15.1, 20.9, 'PC_AluSilver')
    AR.box(core, CX0, 15.0, Z[3] - 0.5, CX1, Y1, Z[3], 'PC_RoofGravel')
    AR.wall(core, (CX0, Y1), (CX0, 15.0), 0.0, Z[3], 0.3, 'PC_WallWarm', 'PC_WallWarm', holes=[(4.0, 6.0, Z[0], Z[0] + 2.4),
            (4.0, 6.0, Z[1], Z[1] + 2.4), (4.0, 6.0, Z[2], Z[2] + 2.4)])
    AR.curtain(A, L, [(CX0 + 1.4, Y0 - 0.02), (CX0 + 4.6, Y0 - 0.02)], 0.0, 3.6, 3.2, [], 0.06, 0.15, 'PC_AluDark', 'PC_Glass',
               sub='CoreEntrance', doors=[dict(seg=0, u0=0.0, u1=3.2, h=3.0, kind='slide', leaves=2)])
    # blade canopy over the customer entrance (tilted cantilever)
    if L < 2:
        pts = [(CX0 - 1.0, Y0), (CX1 + 1.0, Y0), (CX1 + 0.4, Y0 - 5.0), (CX0 - 0.6, Y0 - 5.0)]
        det.add(bm_prism(pts, 4.25, 4.45), 'PC_PanelWhite')
        AR.light_grid(det, L, (CX0 - 0.2, Y0 - 4.5, CX1 + 0.2, Y0 - 0.6), 4.25, 3, 2, 0.6, 0.6, 'PC_LightPanel')
    # ---- floating roof plate + portico columns
    plate = rounded_rect(-26.0, 4.2, 18.0, 30.0, 3.0, 8 if L == 0 else 3)
    det.add(bm_prism(plate, 16.95, 17.55), 'PC_PanelWhite')
    if L < 2:
        AR.downlights(det, L, [(x, y) for x in range(-24, 17, 3) for y in (5.4, 6.6)], 16.95, 0.14, 'PC_LightPanel')
    for x in (-23.0, -9.0, 5.0):
        AR.column(det, L, x, 5.4, 0.0, 16.95, 0.2, 'PC_PanelWhite')
    AR.column(det, L, -25.0, 26.0, 0.0, 16.95, 0.2, 'PC_PanelWhite')
    # ---- signage: rooftop wordmark + star on the core
    sg = A.m(L, 'SIGNAGE', 'Brand')
    txt(sg, L, 'MERCEDES-BENZ', place('-Y', Vector((-4.0, 4.8, 17.55 + 0.75))), 1.35, 0.18, 'dsemi', 'MB_Letter', 'PC_AluSilver', spacing=1.12)
    star(sg, L, place('-Y', Vector((21.0, Y0 - 0.25, 18.1))), 2.0)
    if L < 2:
        txt(sg, L, 'MERCEDES-BENZ', place('-Y', Vector((21.0, Y0 - 0.22, 15.2))), 0.42, 0.06, 'dsemi', 'MB_Letter', 'PC_AluSilver', spacing=1.1)
    A.sign('rooftop_wordmark', (-4.0, 4.6, 18.3), 1.35, width=16.0)
    A.sign('core_star', (21.0, Y0 - 0.4, 18.1), 4.0, width=4.0)
    interior(L)


def star(acc, L, M, r):
    """Simplified three-pointed star in a ring (generic geometric recreation, not official artwork)."""
    seg = {0: 64, 1: 32, 2: 16}[L]
    outer = [(r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    inner = [(0.9 * x, 0.9 * y) for (x, y) in outer]
    bm = R.bm_ring_prism(outer, inner, 0.0, 0.2)
    acc.add(bm, 'MB_StarGlow', matrix=M)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        tip = (0.9 * r * math.cos(a), 0.9 * r * math.sin(a))
        b1 = (0.17 * r * math.cos(a + math.radians(60)), 0.17 * r * math.sin(a + math.radians(60)))
        b2 = (0.17 * r * math.cos(a - math.radians(60)), 0.17 * r * math.sin(a - math.radians(60)))
        poly(acc, [(0, 0), b2, tip, b1], 0.24, M, 'MB_StarGlow')


def interior(L):
    st = A.m(L, 'BUILDING_INTERIOR', 'Partitions')
    fu = A.m(L, 'FURNITURE', 'Lounges')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Platforms')
    # back-of-house partition walls (keep the service zone out of the public view)
    AR.wall(st, (X1, 32.5), (-6.0, 32.5), Z[0], Z[1] - 0.4, 0.2, 'PC_WallWarm')
    AR.box(st, -6.2, 32.5, Z[0], -6.0, Y1, Z[1] - 0.4, 'PC_WallWarm')
    # feature wall with backlit slats behind the reception
    AR.box(st, 9.0, 32.3, Z[0], 17.5, 32.5, Z[1] - 0.4, 'PC_StoneDark')
    if L < 2:
        for i in range(9):
            x = 9.5 + i * 0.95
            AR.box(st, x, 32.22, Z[0] + 0.6, x + 0.06, 32.3, Z[1] - 1.0, 'PC_LightStrip')
    # ceilings + light panels
    full = (X0 + 0.4, Y0 + 0.5, X1 - 0.2, Y1 - 0.5)
    gf_ceiling = [r for r in rect_subtract([full], ATR)]
    AR.ceiling_panels(A, L, gf_ceiling, Z[1] - 0.4, (3.0, 2.6), lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [full], Z[2] - 0.4, (3.0, 2.6), lod2_glow='PC_LightWarm')
    AR.ceiling_panels(A, L, [full], Z[3] - 0.5, (3.0, 2.6), mat='PC_LightWarm', lod2_glow='PC_LightWarm')
    if L < 2:
        F.ring_light(fu, L, -1.0, 15.0, Z[2] - 2.2, 4.2, 0.12)
        F.ring_light(fu, L, -1.0, 15.0, Z[2] - 2.9, 3.0, 0.10)
    # sculptural floating stair in the atrium (GF -> L1) and stair L1 -> L2 by the core
    AR.stair(A, L, -1.0, 22.0 - 11.7, 90, 2.0, Z[0], Z[1], 'floating', 'PC_FloorMarble', 'PC_PanelWhite', sub='AtriumStair')
    AR.stair(A, L, 10.2, STAIR2[1] + 0.1, 90, 1.6, Z[1], Z[2], 'floating', 'PC_FloorOak', 'PC_SteelDark', sub='UpperStair')
    # glass balustrades around the atrium + stair well
    AR.glass_rail(A, L, [(ATR[0], Y0 + 0.4), (ATR[0], ATR[3]), (-2.1, ATR[3])], Z[1])
    AR.glass_rail(A, L, [(0.1, ATR[3]), (ATR[2], ATR[3]), (ATR[2], Y0 + 0.4)], Z[1])
    AR.glass_rail(A, L, [(STAIR2[0], STAIR2[3]), (STAIR2[0], STAIR2[1]), (STAIR2[2], STAIR2[1]), (STAIR2[2], STAIR2[3])], Z[2], sub='RailL2')
    # ---- GF: turntables, reception, lounge
    for (x, y, r) in ((-17.0, 16.0, 3.3), (-6.0, 15.5, 3.2), (4.5, 15.5, 3.2), (12.8, 17.0, 3.0)):
        F.turntable(dp, L, x, y, Z[0], r, 0.16, 'PC_FloorMarble', 'PC_AluSilver')
    F.plinth(dp, L, -20.0, 25.0, -12.0, 30.5, Z[0], 0.2, 'PC_WhiteGloss')
    F.reception_desk(fu, L, 13.0, 27.0, Z[0], 180, 3.0)
    F.lounge_group(fu, L, 2.0, 28.0, Z[0], 0, 'PC_FabricGrey', 'PC_Leather')
    F.lounge_group(fu, L, -4.0, 28.5, Z[0], 0, 'PC_FabricCream', 'PC_LeatherBlack')
    F.stanchion_sign(fu, L, -12.0, 11.0, Z[0], 0)
    F.stanchion_sign(fu, L, 9.0, 11.0, Z[0], 0)
    # ---- L1: side galleries with display cars + configurator desks
    F.plinth(dp, L, -22.5, 11.0, -12.0, 19.5, Z[1], 0.18, 'PC_WhiteGloss')
    F.plinth(dp, L, 9.5, 10.5, 17.0, 19.0, Z[1], 0.18, 'PC_WhiteGloss')
    for i, x in enumerate((-19.0, -14.0)):
        F.desk(fu, L, x, 28.0, Z[1], 0, 1.6, 0.8)
    F.lounge_group(fu, L, -1.0, 28.0, Z[1], 0, 'PC_FabricTeal', 'PC_LeatherCream')
    F.tv_wall(fu, L, -1.0, 32.9, Z[1], 0, 4, 2, 1.6, 0.92, seed=1)
    # ---- L2: premium lounge + display car
    F.turntable(dp, L, -15.5, 15.5, Z[2], 3.0, 0.12, 'PC_FloorDark', 'PC_Brass')
    for x in (-5.0, 1.5):
        F.lounge_group(fu, L, x, 14.5, Z[2], 0, 'PC_LeatherCream', 'PC_Leather')
    F.counter(fu, L, -2.0, 27.0, 6.0, 28.0, Z[2], 1.1, 'PC_TimberDark', 'PC_StoneTop', 'PC_LightStrip')
    if L < 2:
        for x in (-1.0, 0.5, 2.0, 3.5, 5.0):
            F.stool(fu, L, x, 26.3, Z[2])
        F.bottle_shelf(fu, L, 2.0, 30.4, Z[2], 180, 6.0)
        for x in (-14.0, -10.0):
            F.round_set(fu, L, x, 27.0, Z[2], 4, 0.5, 'PC_StoneTop', 'PC_Brass', 'PC_LeatherCream')
        for x in (-4.0, 0.0, 4.0):
            F.pendant(fu, L, x, 14.5, Z[3] - 0.5, 1.4, 'disc', 0.45, 'PC_LampGlobe', 'PC_Brass')


for L in (0, 1, 2):
    build(L)

# ---- placeholder cars (all separate objects)
CARS.add_car(A, 1, 'sedan', -17.0, 16.0, Z[0] + 0.16, 160, 'PC_CarPaintSilver', 'GF turntable')
CARS.add_car(A, 2, 'suv', -6.0, 15.5, Z[0] + 0.16, 200, 'PC_CarPaintBlack', 'GF atrium turntable')
CARS.add_car(A, 3, 'coupe', 4.5, 15.5, Z[0] + 0.16, 160, 'PC_CarPaintWhite', 'GF atrium turntable')
CARS.add_car(A, 4, 'sedan', 12.8, 17.0, Z[0] + 0.16, 200, 'PC_CarPaintGraphite', 'GF turntable')
CARS.add_car(A, 5, 'crossover', -16.0, 27.8, Z[0] + 0.2, 180, 'PC_CarPaintBlue', 'GF rear plinth')
CARS.add_car(A, 6, 'coupe', -17.2, 15.2, Z[1] + 0.18, 170, 'PC_CarPaintRed', 'L1 gallery plinth')
CARS.add_car(A, 7, 'sedan', 13.2, 14.8, Z[1] + 0.18, 190, 'PC_CarPaintSand', 'L1 gallery plinth')
CARS.add_car(A, 8, 'coupe', -15.5, 15.5, Z[2] + 0.12, 165, 'PC_CarPaintBlack', 'L2 lounge turntable')

# ---- site pieces
S.sidewalk(A, -27.0, 46.0, crossings=[(-21.5, -12.5), (25.0, 31.0)])
S.paved(A, 'OPTIONAL_FORECOURT', [(-27.0, 0.0, -21.5, Y0), (-12.5, 0.0, 25.0, Y0)], 'PC_PaverLight', sub='Plaza')
S.paved(A, 'OPTIONAL_FORECOURT', [(-21.5, 0.0, -12.5, Y0)], 'PC_Paver', sub='VehicleApron')
S.asphalt(A, 'DRIVEWAY', [(25.0, 0.0, 31.0, 42.0), (-24.0, Y1, 25.0, 42.0)])
S.arrow(A, 'DRIVEWAY', 28.0, 10.0, 90)
S.asphalt(A, 'OPTIONAL_PARKING', [(31.0, 6.0, 37.0, 36.0)])
S.bays(A, 31.0, 7.0, 11, 2.6, 5.4, 1, along='y')
for x in (-26.5, -13.0, 18.5, 24.6):
    for k in range(3):
        F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x + (k * 1.5 if x < 0 else 0), 0.6 + (0 if x < 0 else k * 1.5), 0.0)

# ---- lights (important fixtures only; small ones are emissive)
for i, (x, y, z, e) in enumerate(((-15, 16, 5.6, 2600), (-1, 16, 10.3, 4200), (11, 18, 5.6, 2400), (0, 28, 5.6, 1800),
                                  (-16, 15, 10.8, 1800), (12, 15, 10.8, 1500), (-15, 16, 15.2, 1700), (0, 16, 15.2, 1700),
                                  (8, 27, 15.2, 1200))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#fff3e6', radius=1.2)
for i, x in enumerate((-17.0, -6.0, 4.5)):
    A.light('INTERIOR_LIGHTING', f'CarSpot{i:02d}', 'SPOT', (x, 13.0, 6.0), 1400, '#ffffff', rot=(30, 0, 0), spot_deg=55, radius=0.3)
A.light('EXTERIOR_LIGHTING', 'StarUplight', 'SPOT', (21.0, 2.0, 0.3), 2500, '#e8f0ff', rot=(-70, 0, 0), spot_deg=30)
A.light('EXTERIOR_LIGHTING', 'CanopyDown', 'SPOT', (21.0, 5.0, 4.2), 900, '#fff1e0', spot_deg=100)
A.light('EXTERIOR_LIGHTING', 'PlateWashL', 'SPOT', (-15.0, 2.0, 0.3), 1800, '#fff1e0', rot=(-80, 0, 0), spot_deg=40)
A.light('EXTERIOR_LIGHTING', 'PlateWashR', 'SPOT', (5.0, 2.0, 0.3), 1800, '#fff1e0', rot=(-80, 0, 0), spot_deg=40)

# ---- collision
A.col_box('GlassBox', X0, Y0, 0, X1, Y1, Z[3] + 0.9)
A.col_box('Core', CX0, Y0, 0, CX1, Y1, 20.9)
A.col_box('RoofPlate', -26, 4.2, 16.95, 18, 30, 17.55)
for i, x in enumerate((-23.0, -9.0, 5.0)):
    A.col_box(f'Column{i}', x - 0.2, 5.2, 0, x + 0.2, 5.6, 16.95)

# ---- cameras + visibility probes
A.camera('day', (-46.0, -34.0, 11.0), (-1.0, 18.0, 7.5), 28)
A.camera('night', (-40.0, -30.0, 6.5), (-1.0, 18.0, 8.5), 28)
A.camera('road', (-30.0, -7.6, 1.1), (2.0, 14.0, 5.5), 24)
A.camera('interior', (9.5, 23.8, 9.2), (-9.0, 12.0, 2.2), 17)
A.checks['probes'] = [dict(name='GF_atrium', p=[-1.0, 18.0, 1.2]), dict(name='L1_gallery_left', p=[-17.0, 18.0, 7.6]),
                      dict(name='L1_gallery_right', p=[13.0, 18.0, 7.6]), dict(name='L2_lounge', p=[-5.0, 15.0, 12.6]),
                      dict(name='L2_lounge_right', p=[1.5, 12.0, 12.6])]
S.finish(A, -27.0, 46.0, width=48.0, depth=28.0, height=20.9, footprint=[X0, Y0, CX1, Y1],
         storeys=3, floor_levels=Z[:3], roof=Z[3], parking='optional side lot, 11 bays (OPTIONAL_PARKING)',
         access='left vehicle crossing to forecourt/showroom door; right side driveway to rear service yard',
         setback_m=8.0, glass='PC_Glass alpha 0.16 curtain wall', concept=__doc__.strip().split('\n')[2])
