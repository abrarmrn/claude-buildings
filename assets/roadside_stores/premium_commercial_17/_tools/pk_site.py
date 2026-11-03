"""Site pieces (exported, separately removable) and the preview street (NOT exported).

Street section used for every asset (all y values relative to the plot frontage line y = 0):
   y  0.0 .. -4.0   public pavement  (SIDEWALK_FRONTAGE, flush with the site at z = 0.0)
   y -4.0           kerb (0.15 m upstand)
   y -4.0 .. -11.5  two-lane service road at z = -0.15            (preview only)
   y -11.5 .. -16   separation strip (plain ground, no planting)  (preview only)
   y -16  .. -28    main carriageway, 3 lanes                     (preview only)
Vehicle access is ALWAYS from the service road (never from the high-speed carriageway).
"""
import math
import bpy
from pk_core import (bm_box, bm_hquad, bm_quad, bm_cyl, rect_subtract, MeshAcc, hex_lin, R)

SW = 4.0                    # pavement depth
ROAD = (-11.5, -4.0)
KERB_H = 0.15


def sidewalk(A, x0, x1, crossings=(), depth=SW, mat='PC_PaverLight'):
    """Public pavement in front of the plot with kerb; crossings = [(xa, xb)] driveway drops (asphalt, ramped)."""
    acc = A.s('SIDEWALK_FRONTAGE')
    rects = [(x0, -depth + 0.25, x1, 0.0)]
    for (a, b) in crossings:
        rects = rect_subtract(rects, (a, -depth - 1, b, 1))
    for r in rects:
        acc.add(bm_box(r[0], r[1], -0.25, r[2], r[3], 0.0), mat, mat_fn=lambda f: mat if f.normal.z > 0.5 else 'PC_Curb')
    # kerb
    kr = [(x0, -depth, x1, -depth + 0.25)]
    for (a, b) in crossings:
        kr = rect_subtract(kr, (a, -depth - 1, b, 1))
    for r in kr:
        acc.add(bm_box(r[0], r[1], -0.3, r[2], r[3], 0.0), 'PC_Curb')
    for (a, b) in crossings:
        d = A.s('DRIVEWAY', 'Crossing')
        # ramp from road level up to site level across the kerb line
        d.add(bm_quad((a, -depth, -KERB_H), (b, -depth, -KERB_H), (b, -depth + 0.9, 0.0), (a, -depth + 0.9, 0.0)), 'PC_Asphalt')
        d.add(bm_hquad(a, -depth + 0.9, b, 0.0, 0.0), 'PC_Asphalt')
        for xx in (a, b):
            d.add(bm_box(xx - 0.15, -depth, -0.3, xx + 0.15, -depth + 0.9, 0.0), 'PC_Curb')


def paved(A, comp, rects, mat='PC_Paver', z=0.0, sub='Main', edge='PC_Curb', thick=0.2):
    acc = A.s(comp, sub)
    for r in rects:
        acc.add(bm_box(r[0], r[1], z - thick, r[2], r[3], z), mat, mat_fn=lambda f: mat if f.normal.z > 0.5 else edge)


def asphalt(A, comp, rects, z=0.0, sub='Asphalt'):
    paved(A, comp, rects, 'PC_Asphalt', z, sub)


def bays(A, x0, y0, n, w=2.6, depth=5.2, dirn=1, along='x', comp='OPTIONAL_PARKING', line='PC_LineWhite', stops=True):
    """Row of parking bays (lines only, on top of an asphalt base supplied separately)."""
    acc = A.s(comp, 'Markings')
    for i in range(n + 1):
        if along == 'x':
            xx = x0 + i * w
            acc.add(bm_hquad(xx - 0.05, min(y0, y0 + dirn * depth), xx + 0.05, max(y0, y0 + dirn * depth), 0.006), line)
        else:
            yy = y0 + i * w
            acc.add(bm_hquad(min(x0, x0 + dirn * depth), yy - 0.05, max(x0, x0 + dirn * depth), yy + 0.05, 0.006), line)
    if stops:
        for i in range(n):
            if along == 'x':
                cx = x0 + (i + 0.5) * w; cy = y0 + dirn * (depth - 0.6)
                acc.add(bm_box(cx - 0.8, cy - 0.08, 0, cx + 0.8, cy + 0.08, 0.12), 'PC_Curb')
            else:
                cy = y0 + (i + 0.5) * w; cx = x0 + dirn * (depth - 0.6)
                acc.add(bm_box(cx - 0.08, cy - 0.8, 0, cx + 0.08, cy + 0.8, 0.12), 'PC_Curb')


def arrow(A, comp, x, y, ang, length=3.0, sub='Markings', mat='PC_LineWhite'):
    acc = A.s(comp, sub)
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    def P(u, v):
        return (x + u * ca - v * sa, y + u * sa + v * ca, 0.007)
    acc.add(bm_quad(P(-length / 2, -0.12), P(length / 2 - 0.8, -0.12), P(length / 2 - 0.8, 0.12), P(-length / 2, 0.12)), mat)
    acc.add(bm_quad(P(length / 2 - 0.8, -0.45), P(length / 2, 0.0), P(length / 2, 0.0), P(length / 2 - 0.8, 0.45)), mat)


# ---------------------------------------------------------------------------- preview street (not exported)
def preview_env(A, x0, x1, back=60.0):
    acc = MeshAcc('PV_Street')
    R.MATERIAL_DEFS.setdefault('PV_Ground', dict(base='#b49a78', rough=0.95))
    R.MATERIAL_DEFS.setdefault('PV_GroundPaved', dict(base='#a7a29a', rough=0.9))
    # service road + main road + strips
    acc.add(bm_hquad(-1500, ROAD[0], 1500, ROAD[1], -KERB_H), 'PC_Asphalt')
    acc.add(bm_hquad(-1500, -16.0, 1500, ROAD[0], -KERB_H + 0.02), 'PV_Ground')
    acc.add(bm_hquad(-1500, -28.0, 1500, -16.0, -KERB_H), 'PC_Asphalt')
    acc.add(bm_hquad(-1500, -400, 1500, -28.0, -KERB_H - 0.02), 'PV_Ground')
    for yy, mat, dash in ((ROAD[1] - 0.25, 'PC_LineWhite', False), ((ROAD[0] + ROAD[1]) / 2, 'PC_LineWhite', True),
                          (-16.4, 'PC_LineYellow', False), (-20.3, 'PC_LineWhite', True), (-24.1, 'PC_LineWhite', True),
                          (-27.6, 'PC_LineWhite', False)):
        if dash:
            for k in range(-170, 170):
                acc.add(bm_hquad(k * 9.0, yy - 0.07, k * 9.0 + 3.0, yy + 0.07, -KERB_H + 0.003), mat)
        else:
            acc.add(bm_hquad(-1500, yy - 0.08, 1500, yy + 0.08, -KERB_H + 0.003), mat)
    # kerbs along the separation strip
    acc.add(bm_box(-1500, ROAD[0] - 0.2, -0.3, 1500, ROAD[0], 0.0), 'PC_Curb')
    acc.add(bm_box(-1500, -16.0, -0.3, 1500, -15.8, 0.0), 'PC_Curb')
    # pavement continues left/right of the plot (neutral), ground around + behind the plot
    acc.add(bm_hquad(-1500, -SW, x0, 0.0, -0.002), 'PV_GroundPaved')
    acc.add(bm_hquad(x1, -SW, 1500, 0.0, -0.002), 'PV_GroundPaved')
    acc.add(bm_box(-1500, -SW, -0.3, x0, -SW + 0.25, 0.0), 'PC_Curb')
    acc.add(bm_box(x1, -SW, -0.3, 1500, -SW + 0.25, 0.0), 'PC_Curb')
    acc.add(bm_hquad(-1500, 0.0, 1500, 1500, -0.03), 'PV_Ground')
    acc.build(A.preview, None, weighted=False)
    # sun / world defaults
    R.set_world(bpy.context.scene, 'day')


def finish(A, x0, x1, **meta):
    """Finalize geometry, add preview street, save .blend, export GLBs, write lod/build_stats.json."""
    import json, os
    A.meta.update(meta)
    A.meta['plot_x'] = [x0, x1]
    A.meta['light_counts'] = dict(A.light_count)
    stats = A.finalize()
    preview_env(A, x0, x1)
    blend, glb, bonly = A.save_and_export()
    tot = {k: sum(v.values()) for k, v in stats.items()}
    tot['PLACEHOLDER_CARS'] = sum(c['tris'] for c in A.cars)
    json.dump(dict(parts=stats, totals=tot, cars=A.cars, meta=A.meta), open(f'{A.dir}/lod/build_stats.json', 'w'), indent=1)
    print('BUILD_OK', A.base, json.dumps(tot))
    return stats
