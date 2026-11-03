"""ASSET 14 - Pitlane Performance (performance garage & repair centre, 1 storey hangar).

Massing: a 41 m wide racing-hangar with a BARREL-VAULT roof whose arched gable faces the road (eaves 7 m, crown 11.4 m).
The lower front holds four big roller doors (two open, one half-open, one closed) separated by full-height glass
observation panels; the arched lunette above is glazed so the lit workshop reads from the road.  A low glass service
reception box sits on the left beside a tall black/red vertical sign blade.  Red/white chequer band at the doors.
Inside: two 2-post lifts and a 4-post lift with raised cars, a car on the floor with the bonnet zone lit, engine stand,
tyre machine + racks, tool cabinets, workbenches and long high-bay lights following the vault.
Site: wide workshop apron straight off the service road; optional customer parking left of the reception.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('14', '14_pitlane_performance', 'pitlane_performance', 'P14', 'PitlanePerformance', 'Pitlane Performance', 1)
defmat('PL_Red', '#c4121c', 0.35, 0.2)
defmat('PL_RedGlow', '#e01020', 0.3, emit='#ff1a22', es=5.0)
defmat('PL_Letter', '#ffffff', 0.3, emit='#ffffff', es=5.0)

HW = 20.5
Y0, Y1 = 5.0, 31.0
ZE, RISE = 7.0, 4.4
DOORS = [(-17.5, -11.5, 1.0), (-7.5, -1.5, 1.0), (2.0, 8.0, 0.5), (12.0, 18.0, 0.0)]
DH = 5.2


def zvault(x):
    t = max(-1.0, min(1.0, x / HW))
    return ZE + RISE * math.sqrt(max(0.0, 1 - t * t))


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Hangar')
    det = A.m(L, 'FACADE_DETAILS', 'Details')
    AR.slab_r(A, L, (-HW, Y0, HW, Y1), [], 0.15, 0.45, 'PC_FloorEpoxy', 'PC_Concrete', 'PC_PanelBlack', sub='GroundSlab')
    # barrel vault (corrugated outside, white inside)
    nx = {0: 32, 1: 16, 2: 8}[L]
    AR.heightfield_slab(ext, (-HW - 0.3, HW + 0.3), lambda x: Y0 - 1.2, lambda x: Y1 + 0.6, lambda x, y: zvault(x) + 0.35 if abs(x) <= HW else ZE,
                        0.35, nx, 2, 'PC_Corrugated', 'PC_Ceiling', 'PC_PanelBlack')
    # side walls (black) up to the eaves
    for x, s in ((-HW, -1), (HW, 1)):
        p0, p1 = ((x, Y1), (x, Y0)) if s < 0 else ((x, Y0), (x, Y1))
        AR.wall(ext, p0, p1, 0.0, ZE, 0.35, 'PC_PanelBlack', 'PC_WallWhite', holes=[(4.0, 22.0, 4.6, 6.4)] if s > 0 else [(4.0, 14.0, 4.6, 6.4)])
    AR.curtain(A, L, [(HW + 0.01, Y0 + 4.0), (HW + 0.01, Y0 + 22.0)], 4.6, 6.4, 2.0, [], 0.05, 0.12, 'PC_AluBlack', 'PC_Glass', sub='SideClere')
    # front: lower wall with doors + glass panels, arched lunette glazing
    holes = [(a + HW, b + HW, 0.0, DH) for (a, b, _o) in DOORS]
    obs = [(-11.0, -8.0), (-1.0, 1.5), (8.5, 11.5)]
    holes += [(a + HW, b + HW, 0.6, DH) for (a, b) in obs]
    AR.wall(ext, (-HW, Y0), (HW, Y0), 0.0, ZE, 0.4, 'PC_PanelBlack', 'PC_WallWhite', holes=holes)
    M, _ = seg_frame((-HW, Y0), (HW, Y0))
    for (a, b, o) in DOORS:
        AR.roller_door(ext, L, M, a + HW, b + HW, DH, o, 'PC_SteelPaintGrey', 'PC_AluBlack')
    for (a, b) in obs:
        AR.curtain(A, L, [(a, Y0 + 0.1), (b, Y0 + 0.1)], 0.6, DH, 1.5, [2.8], 0.05, 0.12, 'PC_AluBlack', 'PC_GlassClear', sub=f'Obs{int(a)}')
    n = {0: 20, 1: 10, 2: 6}[L]
    arcp = [(-HW + 2 * HW * i / n, zvault(-HW + 2 * HW * i / n)) for i in range(n + 1)]
    Mf = place('-Y', Vector((0, Y0 + 0.2, 0)))
    gl = A.m(L, 'GLASS_SYSTEM', 'Lunette')
    gl.add(bm_poly_flat([(-HW + 0.3, ZE + 0.1)] + [(x * 0.985, z - 0.3) for (x, z) in arcp[1:-1]] + [(HW - 0.3, ZE + 0.1)], 0.0), 'PC_Glass', matrix=Mf)
    ext.add(bm_box(-HW, Y0 - 0.1, ZE - 0.2, HW, Y0 + 0.4, ZE + 0.15), 'PC_PanelBlack')
    if L < 2:
        for i in range(1, 10):
            x = -HW + 2 * HW * i / 10
            gl.add(bm_box(x - 0.05, Y0 + 0.1, ZE, x + 0.05, Y0 + 0.3, zvault(x) - 0.2), 'PC_AluBlack')
        for (a, b) in zip(arcp[:-1], arcp[1:]):
            det.add(AR.quad_world((a[0], Y0 - 1.21, a[1] + 0.05), (b[0], Y0 - 1.21, b[1] + 0.05), (b[0], Y0 - 1.21, b[1] + 0.2),
                                  (a[0], Y0 - 1.21, a[1] + 0.2)), 'PL_RedGlow')
    # rear arch wall (solid)
    ext.add(bm_poly_flat([(x, z) for (x, z) in [(-HW, 0.0), (HW, 0.0)] + list(reversed(arcp))], 0.0), 'PC_PanelBlack',
            matrix=place('+Y', Vector((0, Y1, 0))))
    ext.add(bm_poly_flat([(x, z) for (x, z) in [(-HW, 0.0), (HW, 0.0)] + list(reversed(arcp))], 0.0), 'PC_WallWhite',
            matrix=place('-Y', Vector((0, Y1 - 0.02, 0))) @ Matrix.Scale(-1, 4, (1, 0, 0)))
    # chequer band above the doors
    if L < 2:
        det.add(bm_box(-HW, Y0 - 0.12, DH + 0.15, HW, Y0 - 0.02, DH + 0.75), 'RS_Checker' if L == 0 else 'PL_Red', uv='box', tile=0.6)
    # reception glass box (left)
    rx0, rx1, ry0, ry1 = -28.5, -HW, Y0, Y0 + 12.0
    AR.slab_r(A, L, (rx0, ry0, rx1, ry1), [], 0.15, 0.45, 'PC_FloorDark', 'PC_Concrete', 'PC_PanelBlack', sub='ReceptionSlab')
    AR.curtain(A, L, [(rx0, ry1), (rx0, ry0), (rx1, ry0)], 0.0, 4.2, 2.0, [2.8], 0.06, 0.15, 'PC_AluBlack', 'PC_Glass', sub='Reception',
               doors=[dict(seg=1, u0=3.0, u1=5.0, h=2.6, kind='slide')])
    AR.wall(ext, (rx1, ry1), (rx0, ry1), 0.0, 4.2, 0.3, 'PC_PanelBlack', 'PC_WallWhite')
    ext.add(bm_box(rx0 - 0.6, ry0 - 1.2, 4.2, rx1, ry1 + 0.2, 4.7), 'PC_PanelBlack', mat_fn=mat_by_normal('PC_RoofMembrane', 'PC_Ceiling', 'PC_PanelBlack'))
    if L < 2:
        ext.add(bm_box(rx0 - 0.61, ry0 - 1.21, 4.2, rx1, ry0 - 1.1, 4.3), 'PL_RedGlow')
    # vertical sign blade
    sg = A.m(L, 'SIGNAGE', 'Brand')
    bx = -30.0
    AR.box(sg, bx - 0.7, 1.0, 0.0, bx + 0.7, 1.9, 13.0, 'PC_PanelBlack')
    AR.box(sg, bx - 0.72, 0.98, 0.0, bx - 0.55, 1.92, 13.0, 'PL_RedGlow' if L < 2 else 'PL_Red')
    word = 'PITLANE'
    for i, ch in enumerate(word):
        txt(sg, L, ch, place('-Y', Vector((bx + 0.05, 0.97, 12.1 - i * 1.15))), 0.9, 0.06, 'dblack', 'PL_Letter', 'PC_AluSilver')
    if L < 2:
        txt(sg, L, 'PERFORMANCE', place('-Y', Vector((bx + 0.05, 0.97, 3.4))), 0.2, 0.03, 'dsemi', 'PL_RedGlow', 'PL_RedGlow', spacing=1.1)
    txt(sg, L, 'PITLANE PERFORMANCE', place('-Y', Vector((0.0, Y0 - 1.25, ZE + 0.55))), 0.75, 0.08, 'dblack', 'PL_Letter', 'PC_AluSilver', spacing=1.05)
    A.sign('vertical_blade', (bx, 0.9, 8.0), 0.9, width=1.2)
    A.sign('gable_name', (0.0, Y0 - 1.3, ZE + 0.55), 0.75, width=12.0)
    interior(L)


def interior(L):
    eq = A.m(L, 'DISPLAY_OBJECTS', 'Workshop')
    fu = A.m(L, 'FURNITURE', 'Workstations')
    zf = 0.15
    # bay lines + chequer strip on the floor at the door line
    if L < 2:
        for (a, b, _o) in DOORS:
            for x in (a + 0.1, b - 0.2):
                eq.add(bm_hquad(x, Y0 + 1.0, x + 0.1, Y1 - 5.0, zf + 0.004), 'PL_Red')
    F.lift_2post(eq, L, -14.5, 15.0, zf, 90, 1.8, 3.4, 'PL_Red')
    F.lift_2post(eq, L, -4.5, 15.0, zf, 90, 0.9, 3.4, 'PL_Red')
    F.lift_4post(eq, L, 5.0, 15.5, zf, 90, 1.5, 5.4, 2.8, 'PC_SteelPaintGrey', 'PC_SteelDark')
    # bay 4: engine stand + tyre machine
    eq.add(bm_box(13.0, 12.0, zf, 13.6, 12.6, zf + 0.8), 'PC_SteelDark')
    eq.add(bm_box(12.7, 11.8, zf + 0.8, 13.9, 12.8, zf + 1.4), 'PC_Stainless')
    eq.add(bm_box(17.5, 9.0, zf, 18.4, 9.8, zf + 1.0), 'PL_Red')
    eq.add(bm_cyl(17.95, 9.4, zf + 1.0, zf + 1.1, 0.3, 14 if L == 0 else 6), 'PC_SteelDark')
    for y in (8.0, 12.0, 16.0, 20.0, 24.0):
        F.tool_cabinet(eq, L, -HW + 0.6, y, zf, -90, 1.8, 1.0, 0.55, 'PL_Red' if y % 8 == 0 else 'PC_ToolBlack')
    for y in (12.0, 20.0):
        F.workbench(eq, L, HW - 0.7, y, zf, 90, 3.2)
    F.tyre_rack(eq, L, -8.0, Y1 - 0.6, zf, 0, 6.0)
    F.tyre_rack(eq, L, 0.0, Y1 - 0.6, zf, 0, 6.0)
    F.wall_shelf(eq, L, 10.0, Y1 - 0.45, zf, 0, 8.0, 3.0, 5, 'PC_SteelPaintGrey', 'PC_SteelPaintGrey', seed=9)
    F.compressor(eq, L, 16.0, Y1 - 2.0, zf, 0)
    F.tyre_stack(eq, L, 16.5, 7.5, zf, 5)
    F.tyre_stack(eq, L, 17.3, 7.5, zf, 4)
    # high-bay lights along the vault
    for x in (-15.0, -5.0, 5.0, 15.0):
        z = zvault(x) - 1.2
        F.ceiling_strip_lights(fu, L, (x - 0.5, Y0 + 1.0, x + 0.5, Y1 - 1.0), z, 1, 'y', 0.25, 'PC_LightCool', 'PC_AluDark')
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_hquad(-HW + 1, Y0 + 1, HW - 1, Y1 - 1, ZE - 0.5, down=True), 'PC_LightCool')
    # reception interior
    F.reception_desk(fu, L, -24.5, 12.5, zf, 180, 2.2, 'PC_PanelBlack', 'PC_StoneTop', 'PL_RedGlow', curved=False)
    F.sofa(fu, L, -26.5, 8.0, zf, 90, 2.4, 0.9, 'PC_LeatherBlack')
    F.tv_wall(fu, L, -24.5, Y0 + 11.6, zf, 0, 2, 1, 1.6, 0.9, 0.1, 1.4, seed=51)
    AR.ceiling_panels(A, L, [(-28.0, Y0 + 0.5, -HW - 0.5, Y0 + 11.5)], 4.2, (2.2, 2.2), w=1.4, d=0.15, lod2_glow='PC_LightCool')


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'coupe', -14.5, 15.0, 0.15 + 1.8, 90, 'PC_CarPaintRed', 'bay 1 on 2-post lift (raised)')
CARS.add_car(A, 2, 'sedan', -4.5, 15.0, 0.15 + 0.9, 90, 'PC_CarPaintBlack', 'bay 2 on 2-post lift (half raised)')
CARS.add_car(A, 3, 'suv', 5.0, 15.5, 0.15 + 1.5, 90, 'PC_CarPaintWhite', 'bay 3 on 4-post lift')
CARS.add_car(A, 4, 'coupe', 15.0, 17.0, 0.15, 90, 'PC_CarPaintYellow', 'bay 4 floor service')
CARS.add_car(A, 5, 'crossover', -24.0, 2.0, 0.0, 180, 'PC_CarPaintGraphite', 'customer drop-off at reception')

S.sidewalk(A, -44.0, 26.0, crossings=[(-43.0, -37.0), (-20.0, 20.0)])
S.asphalt(A, 'DRIVEWAY', [(-20.0, 0.0, 20.0, Y0)], sub='WorkshopApron')
for (a, b, _o) in DOORS:
    S.arrow(A, 'DRIVEWAY', (a + b) / 2, 2.4, 90, 2.6)
S.paved(A, 'OPTIONAL_FORECOURT', [(-37.0, 0.0, -20.0, Y0)], 'PC_PaverLight', sub='ReceptionFront')
S.asphalt(A, 'OPTIONAL_PARKING', [(-43.0, 0.0, -37.0, 22.0), (-37.0, 18.0, -20.0, 30.0)])
S.bays(A, -36.5, 19.5, 6, 2.6, 5.2, 1)

for i, (x, y, z, e) in enumerate(((-14, 15, 9.5, 1600), (-4, 15, 10.5, 1600), (5, 15, 10.5, 1600), (15, 15, 9.5, 1600), (-24, 10, 3.8, 700))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#eef4ff', radius=1.0)
A.light('EXTERIOR_LIGHTING', 'ApronFlood', 'SPOT', (0.0, Y0 - 1.0, ZE - 0.3), 2200, '#eef4ff', rot=(30, 0, 0), spot_deg=110)
A.light('EXTERIOR_LIGHTING', 'BladeWash', 'SPOT', (-30.0, -2.5, 0.2), 700, '#ffffff', rot=(-75, 0, 0), spot_deg=25)
A.col_box('Hangar', -HW, Y0, 0, HW, Y1, ZE + RISE + 0.4)
A.col_box('Reception', -28.5, Y0, 0, -HW, Y0 + 12.0, 4.7)
A.col_box('Blade', -30.7, 1.0, 0, -29.3, 1.9, 13.0)
A.camera('day', (32.0, -26.0, 9.0), (-4.0, 15.0, 5.0), 28)
A.camera('night', (-40.0, -26.0, 5.0), (-2.0, 15.0, 5.5), 26)
A.camera('road', (24.0, -7.6, 1.1), (-4.0, 14.0, 4.0), 24)
A.camera('interior', (17.5, 28.0, 2.6), (-12.0, 9.0, 2.6), 16)
A.checks['probes'] = [dict(name='Bay1_lift', p=[-14.5, 13.0, 2.6]), dict(name='Bay2', p=[-4.5, 13.0, 1.6]), dict(name='Bay3', p=[5.0, 13.0, 2.2]),
                      dict(name='Reception', p=[-24.5, 10.0, 1.2])]
S.finish(A, -44.0, 26.0, width=50.5, depth=27.2, height=ZE + RISE + 0.35, footprint=[-30.7, Y0 - 1.2, HW + 0.3, Y1 + 0.6],
         storeys=1, floor_levels=[0.15], roof='barrel vault, eaves 7.0 m, crown 11.75 m', parking='optional left customer parking, 6 bays (OPTIONAL_PARKING)',
         access='40 m wide workshop apron straight off the service road to four roller doors; separate parking crossing',
         setback_m=5.0, glass='glass observation panels + glazed arched lunette + glass reception box', concept=__doc__.strip().split('\n')[2])
