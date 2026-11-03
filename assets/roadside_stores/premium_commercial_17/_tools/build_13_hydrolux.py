"""ASSET 13 - HydroLux Auto Spa (premium car wash + detailing).

Massing: a 28 m drive-through wash TUNNEL running PARALLEL to the road behind a full glass side wall, so the whole
wash sequence (spray arches, brushes, blowers, LED arch) is visible to passing drivers.  Over everything floats a
large WAVE canopy of translucent panels on white portal frames.  Two open detailing bays sit behind the tunnel and a
glass customer lounge overlooks the exit.  Separate ENTRY (left) and EXIT (right) crossings from the service road.
Inside: wash equipment, floor drainage grates, guide rail, detailing carts / vacuum booms, aqua LED lighting.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('13', '13_hydrolux_auto_spa', 'hydrolux_auto_spa', 'P13', 'HydroLuxAutoSpa', 'HydroLux Auto Spa', 1)
defmat('HX_Aqua', '#12b5d6', 0.3, emit='#20d0ff', es=6.0)
defmat('HX_Letter', '#ffffff', 0.3, emit='#e8fbff', es=5.0)
defmat('HX_Deep', '#0d3d66', 0.35, 0.3)

TX0, TX1, TY0, TY1 = -16.0, 12.0, 6.0, 12.0      # tunnel
ZT = 4.6
CY0, CY1 = 2.8, 22.0                              # canopy depth
LGX0, LGX1, LGY0, LGY1 = 18.5, 25.0, 8.0, 20.0     # lounge


def wave(x):
    return 7.2 + 1.1 * math.sin((x + 24.0) / 50.0 * 3 * math.pi)


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Tunnel')
    can = A.m(L, 'BUILDING_EXTERIOR', 'WaveCanopy')
    frm = A.m(L, 'FACADE_DETAILS', 'Frames')
    # floor slabs (wash floor tiles) - tunnel, bays, lounge
    AR.slab_r(A, L, (TX0, TY0, TX1, TY1), [], 0.05, 0.3, 'PC_FloorTileWet', 'PC_Concrete', 'PC_Concrete', sub='TunnelFloor')
    AR.slab_r(A, L, (-16.0, 13.0, 4.0, 21.0), [], 0.05, 0.3, 'PC_FloorEpoxy', 'PC_Concrete', 'PC_Concrete', sub='BayFloor')
    AR.slab_r(A, L, (LGX0, LGY0, LGX1, LGY1), [], 0.2, 0.4, 'PC_FloorTerrazzo', 'PC_Concrete', 'PC_PanelWhite', sub='LoungeFloor')
    # tunnel: glass road side, white back wall with window band to the bays, roof, portals
    AR.curtain(A, L, [(TX0 + 0.6, TY0), (TX1 - 0.6, TY0)], 0.05, ZT, 2.25, [2.6], 0.06, 0.18, 'PC_SteelPaintWhite', 'PC_GlassClear', sub='TunnelSide')
    AR.wall(ext, (TX1, TY1), (TX0, TY1), 0.0, ZT, 0.3, 'PC_PanelWhite', 'PC_PanelWhite', holes=[(3.0, 25.0, 1.4, 3.6)])
    AR.curtain(A, L, [(TX1 - 3.0, TY1 + 0.31), (TX0 + 3.0, TY1 + 0.31)], 1.4, 3.6, 2.75, [], 0.05, 0.1, 'PC_SteelPaintWhite', 'PC_GlassClear', sub='BayWindow')
    ext.add(bm_box(TX0, TY0 - 0.2, ZT, TX1, TY1 + 0.3, ZT + 0.45), 'PC_PanelWhite', mat_fn=mat_by_normal('PC_RoofMembrane', 'PC_Ceiling', 'PC_PanelWhite'))
    for x in (TX0, TX1):
        for (ya, yb) in ((TY0 - 0.4, TY0), (TY1, TY1 + 0.3)):
            ext.add(bm_box(x - 0.3, ya, 0.0, x + 0.3, yb, ZT + 0.6), 'PC_PanelWhite')
        ext.add(bm_box(x - 0.3, TY0 - 0.4, ZT, x + 0.3, TY1 + 0.3, ZT + 0.6), 'PC_PanelWhite')
        if L < 2:
            ext.add(bm_box(x - 0.32, TY0 - 0.05, ZT - 0.08, x + 0.32, TY1 - 0.05, ZT), 'HX_Aqua')
            for y in (TY0 - 0.05, TY1 - 0.05):
                ext.add(bm_box(x - 0.32, y - 0.04, 0.2, x + 0.32, y + 0.04, ZT), 'HX_Aqua')
    # wave canopy (translucent) on white portal frames
    nx, ny = {0: (40, 6), 1: (20, 3), 2: (10, 1)}[L]
    AR.heightfield_slab(can, (-24.0, 26.0), lambda x: CY0, lambda x: CY1, lambda x, y: wave(x) + 0.35 * (y - CY0) / (CY1 - CY0), 0.25, nx, ny,
                        'PC_GlassSatin', 'PC_GlassSatin', 'PC_SteelPaintWhite')
    for x in range(-22, 27, 6):
        z = wave(x) - 0.25
        for y in (CY0 + 0.4, CY1 - 0.4):
            AR.column(frm, L, x, y, 0.0, z + 0.35 * (y - CY0) / (CY1 - CY0), 0.16, 'PC_SteelPaintWhite')
        frm.add(AR.quad_world((x - 0.1, CY0, z), (x + 0.1, CY0, z), (x + 0.1, CY1, z + 0.35), (x - 0.1, CY1, z + 0.35)), 'PC_SteelPaintWhite')
        frm.add(AR.bm_yz_prism([(CY0, z - 0.45), (CY1, z - 0.1), (CY1, z + 0.35), (CY0, z)], x - 0.1, x + 0.1), 'PC_SteelPaintWhite')
    if L < 2:
        n = 50
        for k in range(n):
            xa = -24.0 + 50.0 * k / n; xb = xa + 50.0 / n
            frm.add(AR.quad_world((xa, CY0 - 0.01, wave(xa) - 0.2), (xb, CY0 - 0.01, wave(xb) - 0.2), (xb, CY0 - 0.01, wave(xb) - 0.05),
                                  (xa, CY0 - 0.01, wave(xa) - 0.05)), 'HX_Aqua')
    # lounge glass box
    lp = [(LGX0, LGY0), (LGX1, LGY0), (LGX1, LGY1), (LGX0, LGY1)]
    AR.curtain(A, L, [(LGX0, LGY1), (LGX0, LGY0), (LGX1, LGY0), (LGX1, LGY1 - 4.0)], 0.2, 4.4, 2.0, [], 0.06, 0.15, 'PC_SteelPaintWhite', 'PC_Glass',
               sub='Lounge', doors=[dict(seg=1, u0=0.8, u1=3.2, h=2.6, kind='slide')])
    AR.wall(ext, (LGX1, LGY1 - 4.0), (LGX1, LGY1), 0.0, 4.4, 0.25, 'PC_PanelWhite', 'PC_WallWhite')
    AR.wall(ext, (LGX1, LGY1), (LGX0, LGY1), 0.0, 4.4, 0.25, 'PC_PanelWhite', 'PC_WallWhite')
    ext.add(bm_box(LGX0 - 0.3, LGY0 - 0.6, 4.4, LGX1 + 0.3, LGY1, 4.8), 'PC_PanelWhite', mat_fn=mat_by_normal('PC_RoofMembrane', 'PC_Ceiling', 'HX_Deep'))
    # signage: canopy fascia + pylon with droplet
    sg = A.m(L, 'SIGNAGE', 'Brand')
    xs = -6.0
    txt(sg, L, 'HYDROLUX', place('-Y', Vector((xs, CY0 - 0.06, wave(xs) - 1.2))), 1.0, 0.1, 'dxbold', 'HX_Letter', 'PC_SteelPaintWhite', spacing=1.12)
    sg.add(bm_box(xs - 5.2, CY0 + 0.0, wave(xs) - 1.85, xs + 5.2, CY0 + 0.1, wave(xs) - 0.5), 'HX_Deep')
    if L < 2:
        txt(sg, L, 'AUTO SPA', place('-Y', Vector((xs + 7.2, CY0 - 0.06, wave(xs + 7.2) - 1.1))), 0.55, 0.06, 'dsemi', 'HX_Aqua', 'HX_Aqua', spacing=1.4)
    AR.box(sg, -25.6, 0.6, 0.0, -24.0, 1.4, 7.5, 'HX_Deep')
    Mp = place('-Y', Vector((-24.8, 0.58, 6.0)))
    disc(sg, L, Mp, 0.75, 0.06, 'HX_Aqua')
    poly(sg, [(0, 0.55), (0.32, 0.05), (0.3, -0.18), (0.16, -0.34), (0, -0.4), (-0.16, -0.34), (-0.3, -0.18), (-0.32, 0.05)], 0.1,
         Mp @ Matrix.Translation((0, 0, 0.06)), 'HX_Letter')
    if L < 2:
        for k, w in enumerate(('HYDRO', 'LUX')):
            txt(sg, L, w, place('-Y', Vector((-24.8, 0.58, 4.6 - k * 0.7))), 0.48, 0.04, 'dxbold', 'HX_Letter', 'HX_Letter')
    A.sign('canopy_name', (xs, CY0 - 0.1, wave(xs) - 1.2), 1.0, width=9.0)
    A.sign('pylon', (-24.8, 0.5, 6.0), 1.5, width=1.5)
    interior(L)


def interior(L):
    eq = A.m(L, 'DISPLAY_OBJECTS', 'WashEquipment')
    fu = A.m(L, 'FURNITURE', 'LoungeAndDetailing')
    ym = (TY0 + TY1) / 2
    # wash sequence along the tunnel (car moves +X)
    F.wash_arch(eq, L, -14.5, ym, 0.05, 90, 5.0, 3.8, 'PC_PlasticWhite', 'HX_Aqua')
    F.wash_arch(eq, L, -12.8, ym, 0.05, 90, 5.0, 3.8, 'PC_PlasticWhite', 'PC_LEDMagenta')
    F.wash_gantry(eq, L, -9.0, ym, 0.05, 90, 4.8, 3.6, 'PC_Stainless', 'PC_BrushBlue', 'PC_BrushRed')
    F.wash_gantry(eq, L, -5.6, ym, 0.05, 90, 4.8, 3.6, 'PC_Stainless', 'PC_BrushBlue', 'PC_BrushBlue')
    F.wash_arch(eq, L, -1.0, ym, 0.05, 90, 5.0, 3.8, 'PC_PlasticWhite', 'HX_Aqua')
    F.blower(eq, L, 3.5, ym, 0.05, 90, 4.6, 3.5)
    F.blower(eq, L, 6.0, ym, 0.05, 90, 4.6, 3.5)
    F.wash_arch(eq, L, 10.0, ym, 0.05, 90, 5.0, 3.8, 'PC_PlasticWhite', 'PC_LEDWhite')
    # guide rail + drainage grates
    eq.add(bm_box(TX0, 7.5, 0.05, TX1, 7.75, 0.2), 'PC_Stainless')
    for x in range(-15, 12, 3):
        F.drain_grate(eq, L, x - 0.2, TY0 + 0.3, x + 0.2, TY1 - 0.3, 0.06, along='y')
    for xb in (-12.0, -4.0):
        F.drain_grate(eq, L, xb - 3.0, 16.8, xb + 3.0, 17.2, 0.06, along='x')
    # tunnel ceiling lights (aqua + white)
    if L < 2:
        for y in (TY0 + 0.6, TY1 - 0.6):
            eq.add(bm_hquad(TX0 + 0.5, y - 0.06, TX1 - 0.5, y + 0.06, ZT - 0.02, down=True), 'HX_Aqua')
        AR.light_grid(eq, L, (TX0 + 1.0, TY0 + 1.5, TX1 - 1.0, TY1 - 1.5), ZT - 0.02, 8, 1, 2.0, 0.3, 'PC_LightCool')
    else:
        eq.add(bm_hquad(TX0, TY0, TX1, TY1, ZT - 0.05, down=True), 'HX_Aqua')
    # detailing bays: carts, vacuum booms, tool cabinets, light bars
    for xb in (-12.0, -4.0):
        F.tool_cabinet(fu, L, xb + 3.2, 20.4, 0.05, 0, 1.2, 1.0, 0.5, 'PC_ToolBlack')
        F.workbench(fu, L, xb - 2.6, 20.4, 0.05, 0, 2.0, 0.6, 'PC_Stainless', 'PC_SteelPaintGrey', pegboard=False)
        if L < 2:
            fu.add(bm_cyl(xb + 3.5, 14.0, 0.05, 4.8, 0.08, 8), 'PC_SteelPaintWhite')
            fu.add(bm_cyl_between((xb + 3.5, 14.0, 4.6), (xb + 1.0, 16.0, 4.6), 0.05, 6), 'PC_SteelPaintWhite')
            fu.add(bm_cyl_between((xb + 1.0, 16.0, 4.6), (xb + 1.0, 16.0, 2.4), 0.03, 6), 'PC_RubberBlack')
            for x in (xb - 2.5, xb + 2.5):
                fu.add(bm_box(x - 0.06, 13.4, 3.2, x + 0.06, 20.4, 3.3), 'PC_LEDWhite')
    # lounge: sofas, coffee bar, screens overlooking the exit
    F.sofa(fu, L, 21.5, 9.6, 0.2, 180, 3.2, 0.9, 'PC_LeatherBlack')
    F.lounge_chair(fu, L, 19.8, 12.5, 0.2, 90, 'PC_FabricTeal')
    F.lounge_chair(fu, L, 19.8, 14.0, 0.2, 90, 'PC_FabricTeal')
    F.coffee_table(fu, L, 21.5, 11.0, 0.2, 0.5)
    F.counter(fu, L, 21.0, 17.5, 24.6, 18.3, 0.2, 1.05, 'HX_Deep', 'PC_StoneTop', 'HX_Aqua')
    F.espresso_machine(fu, L, 23.6, 18.6, 1.25, 180)
    F.tv_wall(fu, L, LGX1 - 0.3, 14.0, 0.2, -90, 2, 1, 1.6, 0.9, 0.1, 1.5, seed=41)
    AR.ceiling_panels(A, L, [(LGX0 + 0.4, LGY0 + 0.4, LGX1 - 0.4, LGY1 - 0.4)], 4.4, (2.0, 2.0), w=0.8, d=0.8, lod2_glow='PC_LightWarm')
    F.ceiling_strip_lights(fu, L, (-16.0, 13.5, 4.0, 20.5), 5.2, 3, 'x', 0.2, 'PC_LightCool', 'PC_AluDark', length=18.0)


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'sedan', -21.0, 9.0, 0.0, 0, 'PC_CarPaintSilver', 'queue at the tunnel entry')
CARS.add_car(A, 2, 'suv', -10.5, 9.0, 0.05, 0, 'PC_CarPaintBlue', 'inside wash tunnel (brushes)')
CARS.add_car(A, 3, 'sedan', -1.5, 9.0, 0.05, 0, 'PC_CarPaintWhite', 'inside wash tunnel (spray arch)')
CARS.add_car(A, 4, 'coupe', 6.5, 9.0, 0.05, 0, 'PC_CarPaintBlack', 'inside wash tunnel (blowers)')
CARS.add_car(A, 5, 'crossover', -12.0, 17.0, 0.05, 180, 'PC_CarPaintRed', 'detailing bay 1')
CARS.add_car(A, 6, 'sedan', -4.0, 17.0, 0.05, 180, 'PC_CarPaintGraphite', 'detailing bay 2')
CARS.add_car(A, 7, 'suv', 15.5, 4.2, 0.0, -90, 'PC_CarPaintWhite', 'leaving via the exit lane')

S.sidewalk(A, -30.0, 30.0, crossings=[(-25.0, -19.0), (12.5, 18.5)])
S.asphalt(A, 'DRIVEWAY', [(-25.0, 0.0, -19.0, 6.0), (-25.0, 6.0, TX0, TY1), (TX1, TY0, 18.5, TY1), (12.5, 0.0, 18.5, TY0)], sub='EntryExitLanes')
S.asphalt(A, 'DRIVEWAY', [(-19.0, 13.0, -16.0, 21.0), (4.0, 13.0, 18.0, 21.0)], sub='BayAccess')
S.arrow(A, 'DRIVEWAY', -22.0, 3.0, 90); S.arrow(A, 'DRIVEWAY', -19.0, 9.0, 0)
S.arrow(A, 'DRIVEWAY', 15.0, 9.0, -60, 2.6); S.arrow(A, 'DRIVEWAY', 15.5, 3.0, -90)
S.paved(A, 'OPTIONAL_FORECOURT', [(-19.0, 0.0, 12.5, TY0), (18.5, 0.0, 30.0, LGY0)], 'PC_PaverLight', sub='Frontage')
for x in range(-17, 12, 4):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 5.2, 0.0, 0.9, 0.1, 'PC_SteelPaintWhite', 'HX_Aqua')

for i, (x, y, z, e) in enumerate(((-11, 9, 4.2, 900), (-2, 9, 4.2, 900), (7, 9, 4.2, 900), (-12, 17, 5.0, 900), (-4, 17, 5.0, 900),
                                  (21.5, 13, 4.0, 600))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#eaf8ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'CanopyGlowL', 'POINT', (-12.0, 14.0, 6.6), 1500, '#bfefff', radius=2.0)
A.light('EXTERIOR_LIGHTING', 'CanopyGlowR', 'POINT', (8.0, 14.0, 6.6), 1500, '#bfefff', radius=2.0)
A.light('EXTERIOR_LIGHTING', 'PylonWash', 'SPOT', (-24.8, -2.5, 0.2), 500, '#ffffff', rot=(-70, 0, 0), spot_deg=30)
A.col_box('Tunnel', TX0 - 0.3, TY0 - 0.4, 0, TX1 + 0.3, TY1 + 0.3, ZT + 0.6)
A.col_box('Lounge', LGX0, LGY0, 0, LGX1, LGY1, 4.8)
A.col_box('Canopy', -24.0, CY0, 6.0, 26.0, CY1, 8.9)
A.camera('day', (-38.0, -26.0, 10.0), (0.0, 11.0, 3.2), 28)
A.camera('night', (30.0, -22.0, 4.5), (-3.0, 11.0, 3.6), 26)
A.camera('road', (-22.0, -7.6, 1.1), (-2.0, 9.0, 2.4), 24)
A.camera('interior', (3.0, 20.6, 2.0), (-10.0, 8.0, 1.6), 17)
A.checks['probes'] = [dict(name='Tunnel_brushes', p=[-9.0, 10.5, 1.5]), dict(name='Tunnel_blower', p=[3.5, 10.5, 1.5]),
                      dict(name='Lounge', p=[21.0, 12.0, 1.4])]
S.finish(A, -30.0, 30.0, width=50.0, depth=19.2, height=8.9, footprint=[-24.0, CY0, 26.0, CY1],
         storeys=1, floor_levels=[0.05, 0.2], roof='translucent wave canopy 6.1-8.9 m over a 4.6 m tunnel',
         parking='none (queue lane only)', access='separate ENTRY (left) and EXIT (right) crossings; tunnel runs parallel to the road',
         setback_m=2.8, glass='glass tunnel side wall + glass lounge', concept=__doc__.strip().split('\n')[2])
