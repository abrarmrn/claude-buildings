"""ASSET 12 - Apex Auto Lab (premium car customisation & wrapping centre, 1 storey + office mezzanine).

Massing: compact black industrial box only 3 m from the pavement.  Three tall glass sectional doors (raised) open the
workshop bays straight to the road; a diagonal cyan/magenta neon stripe slices across the black cladding and over the
glass-box customer lounge on the right (double-height glazing with an office mezzanine).  Illuminated chevron + name.
Inside: bay 1 car on a 2-post lift, bay 2 car being wrapped (vinyl racks, plotter), bay 3 detailing car inside an LED
light-tunnel frame; tool cabinets, workbench, industrial strip lights; lounge with coffee bar.
Site: direct road-facing apron to the bays (wide crossing), no parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('12', '12_apex_auto_lab', 'apex_auto_lab', 'P12', 'ApexAutoLab', 'Apex Auto Lab', 1)
defmat('AX_Letter', '#ffffff', 0.3, emit='#e8fbff', es=5.0)

X0, X1, Y0, Y1 = -16.0, 16.0, 3.0, 25.0
ZF, ZH = 0.15, 8.6
BAYS = [(-15.2, -10.8), (-10.2, -5.8), (-5.2, -0.8)]
DH = 5.2
LX = 1.0                       # lounge glass box from LX to X1
ZM = 4.0


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Shell')
    det = A.m(L, 'FACADE_DETAILS', 'Neon')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], ZF, 0.45, 'PC_FloorEpoxyDark', 'PC_Concrete', 'PC_PanelBlack', sub='GroundSlab')
    AR.slab_r(A, L, (X0, Y0, X1, Y1), [], ZH, 0.5, 'PC_RoofGravel', 'PC_CeilingDark', 'PC_PanelBlack', comp='BUILDING_EXTERIOR', sub='Roof')
    AR.slab_r(A, L, (LX + 0.3, Y0 + 7.0, X1 - 0.3, Y1 - 0.3), [], ZM, 0.3, 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelBlack', sub='Mezzanine')
    # front: black wall with 3 door openings (workshop) + lounge glass box
    AR.wall(ext, (X0, Y0), (LX, Y0), 0.0, ZH + 0.8, 0.35, 'PC_PanelBlack', 'PC_WallDark',
            holes=[(a - X0, b - X0, 0.0, DH) for (a, b) in BAYS])
    M, _ = seg_frame((X0, Y0), (LX, Y0))
    for (a, b) in BAYS:
        AR.roller_door(ext, L, M, a - X0, b - X0, DH, 0.92, 'PC_GlassBlue', 'PC_AluDark')
    # glass strip above doors (clerestory) for interior visibility
    AR.wall(ext, (LX, Y0), (X1, Y0), ZH - 0.6, ZH + 0.8, 0.35, 'PC_PanelBlack', 'PC_WallDark')
    AR.curtain(A, L, [(LX, Y0), (X1, Y0)], 0.0, ZH - 0.6, 2.5, [3.0, ZM - 0.2], 0.06, 0.18, 'PC_AluBlack', 'PC_Glass', sub='Lounge',
               doors=[dict(seg=0, u0=2.5, u1=5.0, h=3.0, kind='slide')], spandrels=[(ZM - 0.3, ZM, 'PC_PanelBlack')])
    AR.curtain(A, L, [(X1, Y0), (X1, Y0 + 9.0)], 0.0, ZH - 0.6, 3.0, [3.0], 0.06, 0.18, 'PC_AluBlack', 'PC_Glass', sub='LoungeSide')
    AR.wall(ext, (X1, Y0 + 9.0), (X1, Y1), 0.0, ZH + 0.8, 0.35, 'PC_PanelBlack', 'PC_WallDark')
    AR.wall(ext, (X1, Y1), (X0, Y1), 0.0, ZH + 0.8, 0.35, 'PC_PanelBlack', 'PC_WallDark', holes=[(20.0, 25.0, 0.0, 4.6)])
    AR.wall(ext, (X0, Y1), (X0, Y0), 0.0, ZH + 0.8, 0.35, 'PC_PanelBlack', 'PC_WallDark', holes=[(5.0, 17.0, 5.6, 7.6)])
    AR.curtain(A, L, [(X0 - 0.01, Y0 + 17.0), (X0 - 0.01, Y0 + 5.0)], 5.6, 7.6, 2.0, [], 0.05, 0.12, 'PC_AluBlack', 'PC_Glass', sub='Clerestory')
    # interior partition lounge | workshop (glass)
    AR.curtain(A, L, [(LX - 0.2, Y1 - 0.4), (LX - 0.2, Y0 + 0.4)], ZF, ZH - 0.5, 2.6, [3.0], 0.05, 0.12, 'PC_AluDark', 'PC_GlassClear', sub='Partition')
    # diagonal neon stripe (cyan + magenta) across the facade
    for (dz, mat) in ((0.0, 'PC_LEDCyan'), (-0.45, 'PC_LEDMagenta')):
        p0, p1 = (X0 - 0.3, 6.6 + dz), (X1 + 0.3, ZH + 0.2 + dz)
        if L < 2:
            for xa, xb in ((X0 - 0.2, -0.6), (-0.6, LX), (LX, X1 + 0.2)):
                ya = p0[1] + (p1[1] - p0[1]) * (xa - p0[0]) / (p1[0] - p0[0])
                yb = p0[1] + (p1[1] - p0[1]) * (xb - p0[0]) / (p1[0] - p0[0])
                if xa >= LX:
                    continue
                det.add(AR.quad_world((xa, Y0 - 0.36, max(ya, DH + 0.1)), (xb, Y0 - 0.36, max(yb, DH + 0.1)), (xb, Y0 - 0.36, max(yb, DH + 0.1) + 0.18),
                                      (xa, Y0 - 0.36, max(ya, DH + 0.1) + 0.18)), mat)
    # signage: chevron + name above the bays, vertical name on the lounge corner
    sg = A.m(L, 'SIGNAGE', 'Brand')
    Ms = place('-Y', Vector((-8.0, Y0 - 0.4, 7.2)))
    for k, mat in ((0, 'PC_LEDCyan'), (1, 'PC_LEDMagenta')):
        dx = -6.4 + k * 0.7
        poly(sg, [(dx, -0.5), (dx + 0.35, -0.5), (dx + 0.95, 0.4), (dx + 0.6, 0.4)], 0.08, Ms, mat)
        poly(sg, [(dx + 0.6, 0.4), (dx + 0.95, 0.4), (dx + 1.55, -0.5), (dx + 1.2, -0.5)], 0.08, Ms, mat)
    txt(sg, L, 'APEX AUTO LAB', Ms @ Matrix.Translation((1.0, 0.0, 0.0)), 0.95, 0.1, 'dxbold', 'AX_Letter', 'PC_AluDark', spacing=1.08)
    if L < 2:
        txt(sg, L, 'WRAP · TINT · DETAIL · CUSTOM', Ms @ Matrix.Translation((1.0, -0.95, 0.0)), 0.3, 0.03, 'dsemi', 'PC_LEDCyan', 'PC_LEDCyan', spacing=1.3)
    A.sign('fascia_name', (-7.0, Y0 - 0.45, 7.2), 0.95, width=10.0)
    interior(L)


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Workshop')
    eq = A.m(L, 'DISPLAY_OBJECTS', 'Equipment')
    lg = A.m(L, 'FURNITURE', 'Lounge')
    # bay floor markings (yellow) + strip lights
    if L < 2:
        for (a, b) in BAYS:
            for x in (a + 0.1, b - 0.2):
                eq.add(bm_hquad(x, Y0 + 0.5, x + 0.1, Y1 - 3.0, ZF + 0.004), 'PC_LineYellow')
    F.ceiling_strip_lights(fu, L, (X0 + 0.5, Y0 + 1.0, LX - 0.5, Y1 - 1.0), ZH - 1.2, 6, 'y', 0.18, 'PC_LightCool', 'PC_AluDark', length=18.0)
    # bay 1: 2-post lift with raised car
    F.lift_2post(eq, L, -13.0, 13.0, ZF, 90, 1.7, 3.3, 'PC_LiftBlue')
    # bay 2: wrap station (car on floor) - vinyl racks + plotter + work lights
    F.vinyl_rack(eq, L, -8.0, Y1 - 0.5, ZF, 0, 3.6, seed=3)
    F.plotter(eq, L, -4.2, Y1 - 1.4, ZF, 0, 2.2)
    for x in (-9.6, -6.4):
        F.linear_pendant(fu, L, x, 12.5, ZH - 2.0, 90, 5.0, 'PC_LightStrip')
    # bay 3: detailing LED light tunnel (rectangular frame of light around the car)
    if L < 2:
        for y in (9.0, 11.5, 14.0, 16.5):
            for (x0, z0, x1, z1) in ((-5.0, ZF, -4.85, 2.8), (-1.15, ZF, -1.0, 2.8), (-5.0, 2.65, -1.0, 2.8)):
                eq.add(bm_box(x0, y - 0.05, z0, x1, y + 0.05, z1), 'PC_LEDWhite')
    # tool cabinets + workbench along the left wall, compressor
    for i, y in enumerate((7.0, 9.0, 11.0)):
        F.tool_cabinet(eq, L, X0 + 0.6, y, ZF, -90, 1.6, 1.0, 0.5, 'PC_ToolRed' if i % 2 == 0 else 'PC_ToolBlack')
    F.workbench(eq, L, X0 + 0.7, 16.5, ZF, -90, 3.0)
    F.compressor(eq, L, X0 + 1.0, 21.5, ZF, 90)
    F.tyre_stack(eq, L, -1.6, Y1 - 1.0, ZF)
    # lounge: reception, sofas, coffee bar, display wall with wrap samples; mezzanine office
    F.reception_desk(lg, L, 5.0, 7.0, ZF, 0, 2.4, 'PC_PanelBlack', 'PC_StoneTop', 'PC_LEDCyan', curved=False)
    F.lounge_group(lg, L, 10.5, 9.5, ZF, 0, 'PC_LeatherBlack', 'PC_LeatherBlack')
    F.counter(lg, L, 12.0, 15.0, 15.4, 15.8, ZF, 1.05, 'PC_PanelBlack', 'PC_StoneTop', 'PC_LEDMagenta')
    F.espresso_machine(lg, L, 14.4, 15.4, ZF + 1.05, 180)
    F.tv_wall(lg, L, 7.0, Y1 - 0.45, ZF, 0, 2, 1, 2.2, 1.25, 0.1, 1.1, seed=31)
    F.desk(lg, L, 6.0, 15.5, ZM, 0, 1.8, 0.8)
    F.desk(lg, L, 11.0, 15.5, ZM, 0, 1.8, 0.8)
    AR.glass_rail(A, L, [(LX + 0.3, Y0 + 7.0), (X1 - 0.3, Y0 + 7.0)], ZM)
    AR.stair(A, L, 2.0, Y0 + 7.8, 90, 1.2, ZF, ZM, 'floating', 'PC_SteelDark', 'PC_SteelDark', sub='MezzStair', max_flight=5.0)
    AR.ceiling_panels(A, L, [(LX + 0.4, Y0 + 0.4, X1 - 0.4, Y0 + 6.8)], ZH - 0.5, (2.4, 2.2), w=1.6, d=0.15, lod2_glow='PC_LightCool')
    AR.ceiling_panels(A, L, [(LX + 0.4, Y0 + 7.2, X1 - 0.4, Y1 - 0.4)], ZM - 0.3, (2.4, 2.2), w=1.6, d=0.15, lod2_glow='PC_LightCool')
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_hquad(X0 + 0.5, Y0 + 0.5, LX, Y1 - 0.5, ZH - 1.2, down=True), 'PC_LightCool')


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'coupe', -13.0, 13.0, ZF + 1.7, 90, 'PC_CarPaintGraphite', 'bay 1 on 2-post lift (raised)')
CARS.add_car(A, 2, 'sedan', -8.0, 12.5, ZF, 90, 'PC_CarWrapMatte', 'bay 2 wrap station')
CARS.add_car(A, 3, 'suv', -3.0, 12.8, ZF, 90, 'PC_CarPaintBlack', 'bay 3 detailing light tunnel')
CARS.add_car(A, 4, 'coupe', 6.0, 1.4, 0.0, 180, 'PC_CarPaintRed', 'waiting on the apron (optional)')

S.sidewalk(A, -20.0, 20.0, crossings=[(-16.0, 0.0)])
S.asphalt(A, 'DRIVEWAY', [(-16.0, 0.0, 0.0, Y0)])
for (a, b) in BAYS:
    S.arrow(A, 'DRIVEWAY', (a + b) / 2, 1.5, 90, 2.4)
S.paved(A, 'OPTIONAL_FORECOURT', [(0.0, 0.0, 20.0, Y0)], 'PC_StoneDark', sub='LoungeApron')

for i, (x, y, z, e) in enumerate(((-13, 12, 7.0, 1400), (-8, 12, 7.0, 1400), (-3, 12, 7.0, 1400), (8, 6, 7.0, 900), (10, 16, 3.4, 700))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#eef4ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'ApronFlood', 'SPOT', (-8.0, Y0 - 0.6, DH + 0.5), 1500, '#eef4ff', rot=(25, 0, 0), spot_deg=100)
A.col_box('Main', X0, Y0, 0, X1, Y1, ZH + 0.8)
A.camera('day', (-30.0, -20.0, 7.0), (-2.0, 12.0, 3.8), 28)
A.camera('night', (24.0, -20.0, 3.5), (-3.0, 12.0, 4.0), 28)
A.camera('road', (-20.0, -7.6, 1.1), (-4.0, 11.0, 3.0), 24)
A.camera('interior', (-0.2, 23.2, 2.4), (-12.0, 6.0, 1.5), 16)
A.checks['probes'] = [dict(name='Bay1_lift', p=[-13.0, 11.0, 2.4]), dict(name='Bay2_wrap', p=[-8.0, 11.0, 1.0]),
                      dict(name='Bay3_tunnel', p=[-3.0, 11.0, 1.0]), dict(name='Lounge', p=[8.0, 8.0, 1.2])]
S.finish(A, -20.0, 20.0, width=32.0, depth=22.0, height=ZH + 0.8, footprint=[X0, Y0, X1, Y1],
         storeys='1 (+ lounge office mezzanine)', floor_levels=[ZF, ZM], roof=ZH, parking='none',
         access='16 m wide road-facing crossing straight to three raised glass bay doors', setback_m=3.0,
         glass='glass sectional bay doors (PC_GlassBlue) + lounge PC_Glass box', concept=__doc__.strip().split('\n')[2])
