"""ASSET 02 - BMW flagship showroom (2 storeys).

Massing: a 42 m CONVEX curved glass front (plan arc, 4 m sagitta) held by a continuous white sculptural frame -
two thick end blades plus a sweeping roof that rises from 10.9 m (right) to 14 m (left) and lifts at its front edge,
with a blue LED line along the frame.  Interior: one tall open hall with radial white ceiling lamellas, five display
positions on the ground floor and a rear mezzanine lounge (5.8 m) reached by a floating stair parallel to its edge.
Separate glazed vehicle delivery door in the right blade; customer doors in the middle of the curve.
Site: shallow curved forecourt directly off the pavement, LEFT side driveway to the rear, optional rear parking.
"""
import os, sys, math
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pk_core import *
import pk_arch as AR, pk_furn as F, pk_cars as CARS, pk_site as S

A = PAsset('02', '02_bmw_showroom', 'bmw_showroom', 'P02', 'BMWShowroom', 'BMW Flagship Showroom', 2)
defmat('BMW_Blue', '#1c69d4', 0.3, emit='#1c69d4', es=2.0)
defmat('BMW_White', '#f4f6f8', 0.3, emit='#ffffff', es=2.0)
defmat('BMW_Ring', '#0d0e10', 0.2, 0.4)
defmat('BMW_LetterW', '#ffffff', 0.3, emit='#ffffff', es=3.0)

RAD = 57.125
HW = 21.0
Y1 = 31.0
ZM = 5.8          # mezzanine top
YM = 18.0         # mezzanine front edge


def fy(x):
    return 6.0 + RAD - math.sqrt(RAD * RAD - x * x)


def zroof_top(x, y):
    t = (HW + 2.5 - x) / (2 * HW + 5.0)                     # 0 right .. 1 left
    base = 11.8 + 3.1 * (t * t * (3 - 2 * t))
    d = y - (fy(x) - 2.5)
    lift = 0.7 * max(0.0, 1.0 - d / 7.0) ** 2               # front edge lifts upward
    return base + lift


THK = 0.9


def zunder(x, y):
    return zroof_top(x, y) - THK


def build(L):
    ext = A.m(L, 'BUILDING_EXTERIOR', 'Frame')
    det = A.m(L, 'FACADE_DETAILS', 'Lamellas')
    n = {0: 18, 1: 12, 2: 6}[L]
    arc = [(-HW + 2 * HW * i / n, fy(-HW + 2 * HW * i / n)) for i in range(n + 1)]
    # ---- slabs
    floor_poly = arc + [(HW, Y1), (-HW, Y1)]
    A.m(L, 'BUILDING_INTERIOR', 'GroundSlab').add(bm_prism(floor_poly, -0.3, 0.15), 'PC_FloorDark',
                                                   mat_fn=mat_by_normal('PC_FloorDark', 'PC_Concrete', 'PC_StoneDark'))
    tongue = (0.4, YM - 1.45, 3.1, YM)
    AR.slab_r(A, L, (-HW + 0.2, YM, HW - 0.2, Y1 - 0.3), [], ZM, 0.35, 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelWhite', sub='Mezzanine')
    AR.slab_r(A, L, tongue, [], ZM, 0.35, 'PC_FloorOak', 'PC_Ceiling', 'PC_PanelWhite', sub='Mezzanine')
    # ---- curved curtain wall, per segment up to the sweeping roof underside
    for i, (p0, p1) in enumerate(zip(arc[:-1], arc[1:])):
        xm = (p0[0] + p1[0]) / 2
        z1 = zunder(xm, fy(xm)) - 0.05
        doors = [dict(seg=0, u0=0.0, u1=math.dist(p0, p1), h=3.2, kind='slide')] if (L < 2 and i in (n // 2 - 1, n // 2)) else []
        AR.curtain(A, L, [p0, p1], 0.0, z1, 2.5, [3.3, 7.6], 0.06, 0.22, 'PC_AluDark', 'PC_Glass', sub='Curve', doors=doors,
                   fins=dict(depth=0.35, t=0.06, mat='PC_AluSilver') if L == 0 else None)
    # ---- sweeping roof (heightfield) + frame blades
    nx, ny = {0: (24, 8), 1: (12, 4), 2: (6, 2)}[L]
    AR.heightfield_slab(ext, (-HW - 2.6, HW + 2.6), lambda x: fy(max(-HW, min(HW, x))) - 2.5, lambda x: Y1 + 0.6, zroof_top, THK,
                        nx, ny, 'PC_PanelWhite', 'PC_PanelWhite', 'PC_PanelWhite')
    for s in (-1, 1):
        xa, xb = (s * HW, s * (HW + 1.4)) if s > 0 else (s * (HW + 1.4), s * HW)
        yfb = fy(HW) - 1.6
        zt = min(zunder(xa, yfb), zunder(xb, yfb))
        pts = [(xa, yfb), (xb, yfb), (xb, Y1 + 0.6), (xa, Y1 + 0.6)]
        holes = []
        if s > 0:
            ext.add(bm_prism([(xa, yfb), (xb, yfb), (xb, 12.5), (xa, 12.5)], 0.0, zt + 0.2), 'PC_PanelWhite')
            ext.add(bm_prism([(xa, 18.5), (xb, 18.5), (xb, Y1 + 0.6), (xa, Y1 + 0.6)], 0.0, zt + 0.2), 'PC_PanelWhite')
            ext.add(bm_prism([(xa, 12.5), (xb, 12.5), (xb, 18.5), (xa, 18.5)], 5.0, zt + 0.2), 'PC_PanelWhite')
            AR.curtain(A, L, [(xb + 0.01, 12.5), (xb + 0.01, 18.5)], 0.0, 5.0, 3.0, [], 0.08, 0.2, 'PC_AluDark', 'PC_Glass',
                       sub='DeliveryDoor', doors=[dict(seg=0, u0=0.0, u1=6.0, h=4.6, kind='slide', leaves=2)])
        else:
            ext.add(bm_prism(pts, 0.0, zt + 0.2), 'PC_PanelWhite')
        if L < 2:
            xe = xb if s > 0 else xa
            ext.add(bm_box(xe - 0.03 if s > 0 else xe - 0.05, yfb - 0.05, 0.3, xe + 0.05 if s > 0 else xe + 0.03, yfb + 0.08, zt), 'BMW_Blue')
    # back wall
    AR.wall(ext, (HW, Y1), (-HW, Y1), 0.0, 11.4, 0.35, 'PC_PanelWhite', 'PC_WallWhite', holes=[(30.0, 35.0, 0.0, 4.2)])
    for s in (-1, 1):
        x = s * HW
        AR.box(ext, x - 0.2 if s > 0 else x, Y1 - 0.4, 11.4, x if s > 0 else x + 0.2, Y1, 13.0, 'PC_PanelWhite')
    # LED line under the roof front edge
    if L < 2:
        for i, (p0, p1) in enumerate(zip(arc[:-1], arc[1:])):
            z0_ = zunder(p0[0], p0[1] - 2.4); z1_ = zunder(p1[0], p1[1] - 2.4)
            det.add(AR.quad_world((p1[0], p1[1] - 2.3, z1_ - 0.01), (p0[0], p0[1] - 2.3, z0_ - 0.01), (p0[0], p0[1] - 2.1, z0_ - 0.01),
                                  (p1[0], p1[1] - 2.1, z1_ - 0.01)), 'BMW_Blue')
    # ---- radial ceiling lamellas (white fins following the roof underside)
    if L < 2:
        step = 1.4 if L == 0 else 2.8
        x = -HW + 0.7
        while x < HW - 0.5:
            ys = [fy(x) + 0.4 + (Y1 - 0.4 - fy(x) - 0.4) * k / 5 for k in range(6)]
            for ya, yb in zip(ys[:-1], ys[1:]):
                za, zb = zunder(x, ya), zunder(x, yb)
                for dx in (-0.03, 0.03):
                    q = (AR.quad_world((x + dx, ya, za - 0.75), (x + dx, yb, zb - 0.75), (x + dx, yb, zb), (x + dx, ya, za)) if dx > 0 else
                         AR.quad_world((x + dx, yb, zb - 0.75), (x + dx, ya, za - 0.75), (x + dx, ya, za), (x + dx, yb, zb)))
                    det.add(q, 'PC_PanelWhite')
                det.add(AR.quad_world((x - 0.03, ya, za - 0.75), (x + 0.03, ya, za - 0.75), (x + 0.03, yb, zb - 0.75), (x - 0.03, yb, zb - 0.75)),
                        'PC_LightStrip' if int((x + HW) / step) % 3 == 0 else 'PC_PanelWhite')
            x += step
    # ---- signage: roundel on the left blade + forecourt pylon
    sg = A.m(L, 'SIGNAGE', 'Brand')
    roundel(sg, L, place('-Y', Vector((-HW - 0.7, fy(HW) - 1.65, 7.6))), 1.9)
    AR.box(sg, -HW - 4.3, 1.2, 0.0, -HW - 3.5, 2.0, 8.2, 'PC_PanelWhite')
    roundel(sg, L, place('-Y', Vector((-HW - 3.9, 1.18, 7.0))), 1.15)
    if L < 2:
        txt(sg, L, 'BMW', place('-Y', Vector((-HW - 3.9, 1.17, 4.4))), 0.5, 0.05, 'dsemi', 'BMW_LetterW', 'PC_AluSilver')
        txt(sg, L, 'BMW  FLAGSHIP', place('-Y', Vector((6.0, fy(6.0) - 2.6, zunder(6.0, fy(6.0) - 2.5) + 0.42))), 0.5, 0.05, 'dsemi',
            'BMW_LetterW', 'PC_AluSilver', spacing=1.2)
    A.sign('blade_roundel', (-HW - 0.7, fy(HW) - 1.8, 7.6), 3.8, width=3.8)
    A.sign('pylon_roundel', (-HW - 3.9, 1.0, 7.0), 2.3, width=2.3)
    interior(L)


def roundel(acc, L, M, r):
    """Simplified roundel: black ring with white letters, blue/white quartered centre (generic recreation)."""
    seg = {0: 64, 1: 32, 2: 16}[L]
    circ = lambda rr, a0=0.0, a1=360.0, n=seg: [(rr * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                                                 rr * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n)]
    acc.add(R.bm_ring_prism(circ(r), circ(r * 0.64), 0.0, 0.16), 'BMW_Ring', matrix=M)
    acc.add(R.bm_ring_prism(circ(r * 0.66), circ(r * 0.62), 0.0, 0.18), 'PC_Chrome', matrix=M)
    q = max(4, seg // 4)
    for k in range(4):
        pts = [(0, 0)] + [(r * 0.62 * math.cos(math.radians(90 * k + 90 * i / q)), r * 0.62 * math.sin(math.radians(90 * k + 90 * i / q)))
                          for i in range(q + 1)]
        poly(acc, pts, 0.12, M, 'BMW_Blue' if k % 2 == 0 else 'BMW_White')
    if L < 2:
        for ch, a in (('B', 140), ('M', 90), ('W', 40)):
            rr = r * 0.82
            Mt = M @ Matrix.Translation((rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)), 0.16)) @ \
                Matrix.Rotation(math.radians(a - 90), 4, 'Z')
            txt(acc, L, ch, Mt, r * 0.26, 0.03, 'dsemi', 'BMW_LetterW', 'BMW_LetterW')


def interior(L):
    fu = A.m(L, 'FURNITURE', 'Main')
    dp = A.m(L, 'DISPLAY_OBJECTS', 'Platforms')
    st = A.m(L, 'BUILDING_INTERIOR', 'Partitions')
    AR.stair(A, L, 12.4, YM - 0.72, 180, 1.4, 0.15, ZM, 'floating', 'PC_FloorOak', 'PC_PanelWhite', sub='Stair', max_flight=7.0,
             rails=(True, False))
    AR.glass_rail(A, L, [(-HW + 0.3, YM), (0.4, YM), (0.4, YM - 1.45), (3.1, YM - 1.45)], ZM)
    AR.glass_rail(A, L, [(3.1, YM), (HW - 0.3, YM)], ZM, sub='Rail2')
    AR.ceiling_panels(A, L, [(-HW + 0.5, YM + 0.4, HW - 0.5, Y1 - 0.5)], ZM - 0.35, (3.2, 3.0), lod2_glow='PC_LightWarm')
    if L == 2:
        A.m(2, 'BUILDING_INTERIOR', 'GlowProxy').add(bm_vquad(-HW + 1, HW - 1, 0.5, 11.0, Y1 - 0.5, '-Y'), 'PC_LightWarm')
    # back wall feature: illuminated slats + screen wall behind the mezzanine lounge
    AR.box(st, -HW + 0.4, Y1 - 0.75, 0.15, HW - 0.4, Y1 - 0.4, ZM - 0.35, 'PC_PanelBlack')
    if L < 2:
        for i in range(28):
            x = -HW + 1.2 + i * 1.45
            AR.box(st, x, Y1 - 0.8, 0.6, x + 0.05, Y1 - 0.75, ZM - 0.9, 'BMW_Blue' if i % 7 == 3 else 'PC_LightStrip')
    F.tv_wall(fu, L, 0.0, Y1 - 0.45, ZM, 0, 6, 2, 1.7, 0.95, 0.1, 1.2, seed=2)
    # display positions (GF)
    F.turntable(dp, L, -4.0, 12.5, 0.15, 3.3, 0.18, 'PC_PanelWhite', 'PC_AluSilver', 'BMW_Blue')
    for (x0, y0, x1, y1) in ((-19.0, 11.0, -12.0, 15.5), (5.5, 9.8, 12.5, 14.3), (14.0, 12.6, 19.8, 17.6)):
        F.plinth(dp, L, x0, y0, x1, y1, 0.15, 0.2, 'PC_FloorDark', 'PC_AluSilver', 'BMW_Blue')
    F.plinth(dp, L, -16.5, 21.5, -9.5, 26.0, 0.15, 0.15, 'PC_WhiteGloss', 'PC_AluSilver')
    # under the mezzanine: reception + lounge + configurator
    F.reception_desk(fu, L, 4.5, 24.0, 0.15, 180, 2.6, 'PC_PanelWhite', 'PC_StoneTop', 'BMW_Blue')
    F.lounge_group(fu, L, 12.5, 25.0, 0.15, 0, 'PC_FabricGrey', 'PC_LeatherBlack')
    for x in (-5.5, -2.0):
        F.desk(fu, L, x, 26.0, 0.15, 0, 1.5, 0.8, 'PC_WhiteGloss')
    # mezzanine: two cars + lounge
    F.plinth(dp, L, -18.5, 22.0, -11.0, 27.5, ZM, 0.15, 'PC_FloorDark', 'PC_AluSilver', 'BMW_Blue')
    F.plinth(dp, L, 11.0, 20.5, 18.5, 26.0, ZM, 0.15, 'PC_FloorDark', 'PC_AluSilver', 'BMW_Blue')
    F.lounge_group(fu, L, -4.0, 23.5, ZM, 0, 'PC_LeatherCream', 'PC_Leather')
    F.lounge_group(fu, L, 4.0, 23.5, ZM, 0, 'PC_FabricGrey', 'PC_LeatherBlack')
    for x in (-8.0, 0.0, 8.0):
        F.pendant(fu, L, x, 12.5, zunder(x, 12.5) - 0.75, 2.6, 'cyl', 0.35, 'PC_LightStrip', 'PC_AluDark')


for L in (0, 1, 2):
    build(L)

CARS.add_car(A, 1, 'coupe', -4.0, 12.5, 0.33, 200, 'PC_CarPaintBlue', 'GF central turntable')
CARS.add_car(A, 2, 'sedan', -15.5, 13.25, 0.35, 165, 'PC_CarPaintWhite', 'GF plinth left')
CARS.add_car(A, 3, 'suv', 9.0, 12.05, 0.35, 195, 'PC_CarPaintGraphite', 'GF plinth')
CARS.add_car(A, 4, 'crossover', 16.9, 15.1, 0.35, 150, 'PC_CarPaintSilver', 'GF by delivery door')
CARS.add_car(A, 5, 'sedan', -13.0, 23.75, 0.3, 180, 'PC_CarPaintBlack', 'GF under mezzanine')
CARS.add_car(A, 6, 'coupe', -14.75, 24.75, ZM + 0.15, 170, 'PC_CarPaintRed', 'mezzanine plinth')
CARS.add_car(A, 7, 'sedan', 14.75, 23.25, ZM + 0.15, 190, 'PC_CarPaintSilver', 'mezzanine plinth')

# ---- site
S.sidewalk(A, -34.0, 26.0, crossings=[(-33.0, -27.0)])
fpts = [(-HW - 2.0, 0.0), (HW + 3.0, 0.0)] + [(HW + 3.0, fy(HW) - 2.0)] + \
       [(x, fy(x) - 0.05) for x in [HW - 2 * HW * i / 16 for i in range(17)]] + [(-HW - 2.0, fy(HW) - 2.0)]
A.s('OPTIONAL_FORECOURT', 'Plaza').add(bm_prism(fpts, -0.2, 0.0), 'PC_PaverLight', mat_fn=mat_by_normal('PC_PaverLight', 'PC_Curb', 'PC_Curb'))
S.asphalt(A, 'DRIVEWAY', [(-33.0, 0.0, -27.0, 46.0)])
S.arrow(A, 'DRIVEWAY', -30.0, 8.0, 90)
S.asphalt(A, 'OPTIONAL_PARKING', [(-27.0, 33.0, 22.0, 46.0)])
S.bays(A, -26.0, 33.0, 17, 2.6, 5.2, 1)
S.bays(A, -26.0, 46.0, 17, 2.6, 5.2, -1)
for x in (-HW - 1.5, HW + 2.5):
    F.bollard(A.s('OPTIONAL_FORECOURT', 'Bollards'), 0, x, 0.8, 0.0)

for i, (x, y, z, e) in enumerate(((-12, 13, 9.5, 3200), (0, 12, 10.0, 3600), (12, 14, 9.0, 3000), (-10, 24, 4.6, 1400),
                                  (8, 24, 4.6, 1400), (-12, 25, 9.0, 1600), (12, 24, 8.6, 1600))):
    A.light('INTERIOR_LIGHTING', f'IntPoint{i:02d}', 'POINT', (x, y, z), e, '#f4f6ff', radius=1.2)
A.light('EXTERIOR_LIGHTING', 'PylonWash', 'SPOT', (-HW - 3.9, -2.0, 0.2), 900, '#e8f0ff', rot=(-75, 0, 0), spot_deg=25)
A.light('EXTERIOR_LIGHTING', 'BladeWash', 'SPOT', (-HW - 0.7, 3.0, 0.2), 1500, '#e8f0ff', rot=(-78, 0, 0), spot_deg=30)
A.col_box('Hall', -HW, fy(HW) - 1.0, 0, HW, Y1, 12.0)
A.col_box('HallFront', -12.0, 6.0, 0, 12.0, 10.0, 12.0)
A.col_box('BladeL', -HW - 1.4, 8.4, 0, -HW, Y1 + 0.6, 14.0)
A.col_box('BladeR', HW, 8.4, 0, HW + 1.4, Y1 + 0.6, 12.0)
A.col_box('Pylon', -HW - 4.3, 1.2, 0, -HW - 3.5, 2.0, 8.2)
A.camera('day', (44.0, -30.0, 9.5), (0.0, 16.0, 6.0), 28)
A.camera('night', (36.0, -26.0, 5.0), (-1.0, 16.0, 6.5), 28)
A.camera('road', (30.0, -7.6, 1.1), (-2.0, 14.0, 4.5), 24)
A.camera('interior', (9.5, 9.0, 1.7), (-9.0, 25.0, 5.6), 17)
A.checks['probes'] = [dict(name='GF_hall', p=[-4.0, 15.0, 1.2]), dict(name='GF_right', p=[9.0, 14.0, 1.2]),
                      dict(name='Mezzanine_left', p=[-14.0, 22.0, ZM + 1.0]), dict(name='Mezzanine_right', p=[14.0, 21.5, ZM + 1.0])]
S.finish(A, -34.0, 26.0, width=44.8, depth=25.0, height=14.6, footprint=[-HW - 1.4, 6.0, HW + 1.4, Y1],
         storeys=2, floor_levels=[0.15, ZM], roof='sweeping 11.8-14.6 m', parking='optional rear lot, 34 bays (OPTIONAL_PARKING)',
         access='left side driveway from the service road to the rear yard; vehicle delivery door in the right blade',
         setback_m=6.0, glass='curved faceted curtain wall, PC_Glass alpha 0.16', concept=__doc__.strip().split('\n')[2])
