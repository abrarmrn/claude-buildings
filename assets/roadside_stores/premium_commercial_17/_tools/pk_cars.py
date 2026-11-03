"""Generic placeholder vehicles (no badges, no real-world model copies).

Each car is ONE separate object in the PLACEHOLDER_CARS collection, parented to <P>_PLACEHOLDER_CARS, with its pivot at
ground level in the centre of the car, nose along the object's local +X.  Object transform = placement (scale 1).
"""
import math, json
import bmesh
from mathutils import Vector, Matrix
from pk_core import bm_box, bm_cyl, bm_cyl_between, bm_quad, MeshAcc

# normalized profile keyframes: x (0 = front bumper, 1 = rear), bottom, beltline, roof, body half-width factor
TYPES = {
    'sedan': dict(L=4.95, W=1.88, H=1.45, axles=(0.185, 0.775), r=0.345, wr=0.76,
                  xs=[0.00, 0.02, 0.06, 0.15, 0.27, 0.31, 0.42, 0.50, 0.62, 0.72, 0.80, 0.88, 0.95, 0.99, 1.00],
                  zb=[0.36, 0.26, 0.20, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.18, 0.19, 0.22, 0.28, 0.36, 0.42],
                  zbelt=[0.58, 0.68, 0.74, 0.78, 0.82, 0.85, 0.90, 0.92, 0.94, 0.96, 0.98, 0.99, 0.98, 0.92, 0.80],
                  zroof=[0.58, 0.68, 0.74, 0.78, 0.83, 0.88, 1.36, 1.45, 1.44, 1.36, 1.10, 0.99, 0.98, 0.92, 0.80],
                  wb=[0.80, 0.90, 0.95, 0.98, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.99, 0.97, 0.93, 0.86, 0.80]),
    'suv': dict(L=4.95, W=1.96, H=1.76, axles=(0.18, 0.79), r=0.38, wr=0.78,
                xs=[0.00, 0.02, 0.07, 0.18, 0.28, 0.33, 0.45, 0.60, 0.80, 0.90, 0.95, 0.985, 1.00],
                zb=[0.45, 0.32, 0.26, 0.24, 0.24, 0.24, 0.24, 0.24, 0.25, 0.28, 0.32, 0.40, 0.48],
                zbelt=[0.80, 0.92, 0.98, 1.02, 1.05, 1.07, 1.10, 1.12, 1.14, 1.15, 1.14, 1.10, 1.00],
                zroof=[0.80, 0.92, 0.98, 1.02, 1.06, 1.12, 1.73, 1.76, 1.75, 1.72, 1.62, 1.30, 1.00],
                wb=[0.84, 0.93, 0.97, 0.99, 1.00, 1.00, 1.00, 1.00, 1.00, 0.99, 0.97, 0.93, 0.90]),
    'coupe': dict(L=4.55, W=1.92, H=1.29, axles=(0.20, 0.75), r=0.35, wr=0.68,
                  xs=[0.00, 0.02, 0.08, 0.20, 0.32, 0.36, 0.50, 0.58, 0.70, 0.82, 0.92, 0.98, 1.00],
                  zb=[0.22, 0.14, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.13, 0.15, 0.20, 0.28, 0.34],
                  zbelt=[0.42, 0.52, 0.60, 0.66, 0.72, 0.74, 0.82, 0.86, 0.90, 0.92, 0.92, 0.86, 0.74],
                  zroof=[0.42, 0.52, 0.60, 0.66, 0.73, 0.78, 1.24, 1.29, 1.20, 1.02, 0.93, 0.86, 0.74],
                  wb=[0.78, 0.90, 0.96, 0.99, 1.00, 0.99, 0.96, 0.96, 1.00, 1.00, 0.98, 0.92, 0.86]),
    'pickup': dict(L=5.6, W=2.0, H=1.92, axles=(0.17, 0.78), r=0.40, wr=0.82,
                   xs=[0.00, 0.015, 0.06, 0.16, 0.26, 0.29, 0.36, 0.48, 0.55, 0.565, 0.80, 0.98, 1.00],
                   zb=[0.50, 0.36, 0.30, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.28, 0.30, 0.42, 0.55],
                   zbelt=[0.95, 1.08, 1.16, 1.20, 1.22, 1.23, 1.26, 1.28, 1.28, 1.27, 1.26, 1.24, 1.10],
                   zroof=[0.95, 1.08, 1.16, 1.20, 1.23, 1.30, 1.88, 1.92, 1.90, 1.27, 1.26, 1.24, 1.10],
                   wb=[0.88, 0.96, 0.99, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.98, 0.95]),
    'crossover': dict(L=4.6, W=1.88, H=1.62, axles=(0.19, 0.78), r=0.36, wr=0.76,
                      xs=[0.00, 0.02, 0.07, 0.18, 0.28, 0.32, 0.45, 0.58, 0.76, 0.86, 0.94, 0.985, 1.00],
                      zb=[0.40, 0.30, 0.23, 0.21, 0.21, 0.21, 0.21, 0.21, 0.22, 0.25, 0.30, 0.38, 0.45],
                      zbelt=[0.72, 0.84, 0.90, 0.95, 0.99, 1.01, 1.04, 1.06, 1.08, 1.09, 1.08, 1.02, 0.92],
                      zroof=[0.72, 0.84, 0.90, 0.95, 1.00, 1.06, 1.58, 1.62, 1.58, 1.48, 1.28, 1.06, 0.92],
                      wb=[0.82, 0.92, 0.96, 0.99, 1.00, 1.00, 1.00, 1.00, 1.00, 0.99, 0.96, 0.91, 0.86]),
}


def _interp(xs, ys, x):
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i] or 1)
            t = t * t * (3 - 2 * t) * 0.35 + t * 0.65          # gentle easing between keys
            return ys[i] + (ys[i + 1] - ys[i]) * t
    return ys[-1]


def _ring(p, xn):
    W2 = p['W'] / 2
    zb, zbl, zr = (_interp(p['xs'], p[k], xn) for k in ('zb', 'zbelt', 'zroof'))
    wb = _interp(p['xs'], p['wb'], xn) * W2
    wr = p['wr'] * W2 * min(1.0, wb / W2 + 0.05)
    t = max(0.0, min(1.0, (zr - zbl) / 0.25))
    hood5 = (wb - 0.2, zbl + 0.012); hood6 = (wb * 0.5, zbl + 0.03)
    cab5 = (wr, zr - 0.06); cab6 = (wr - 0.12, zr)
    r5 = (hood5[0] + (cab5[0] - hood5[0]) * t, hood5[1] + (cab5[1] - hood5[1]) * t)
    r6 = (hood6[0] + (cab6[0] - hood6[0]) * t, hood6[1] + (cab6[1] - hood6[1]) * t)
    right = [(wb - 0.12, zb), (wb - 0.02, zb + 0.06), (wb, zb + 0.42 * (zbl - zb)), (wb - 0.015, zbl - 0.05),
             (wb - 0.05, zbl), r5, r6]
    left = [(-y, z) for (y, z) in reversed(right)]
    return right + left, dict(zb=zb, zbelt=zbl, zroof=zr, t=t, wb=wb)


def car_mesh(kind, paint, name, detail=0):
    p = TYPES[kind]
    Lc = p['L']
    xs = sorted(set([round(v, 4) for v in p['xs']] + [round(i / 34.0, 4) for i in range(35)]))
    rings, info = [], []
    for xn in xs:
        r, inf = _ring(p, xn)
        rings.append(r); info.append(inf)
    bm = bmesh.new()
    vr = []
    for xn, r in zip(xs, rings):
        X = Lc / 2 - xn * Lc
        vr.append([bm.verts.new((X, y, z)) for (y, z) in r])
    nseg = len(rings[0])
    # cabin extent for pillar logic
    zmax = max(i['zroof'] for i in info)
    cab = [k for k, i in enumerate(info) if i['zroof'] > zmax - 0.12]
    bpil = (cab[0] + cab[-1]) // 2 if cab else -1
    face_mat = []
    for i in range(len(xs) - 1):
        a, b = info[i], info[i + 1]
        slope = abs((b['zroof'] - a['zroof']) / ((xs[i + 1] - xs[i]) * Lc))
        for j in range(nseg):
            k = (j + 1) % nseg
            f = bm.faces.new((vr[i][j], vr[i + 1][j], vr[i + 1][k], vr[i][k]))
            m = paint
            side_glass = j in (4, nseg - 6) and a['t'] > 0.8 and b['t'] > 0.8 and slope < 0.45
            if j == nseg - 1:
                m = 'PC_CarTrim'
            elif side_glass:
                m = 'PC_CarTrim' if i == bpil else 'PC_CarGlass'
            elif j in (4, nseg - 6) and slope >= 0.45 and a['t'] > 0.3:
                m = 'PC_CarTrim'                                  # A / C pillars
            elif j in (5, 6, 7) and slope >= 0.45 and min(a['t'], b['t']) > 0.25:
                m = 'PC_CarGlass'                                 # windscreen / rear window
            face_mat.append((f, m))
    fcap = bm.faces.new(list(reversed(vr[0])))
    rcap = bm.faces.new(vr[-1])
    face_mat += [(fcap, paint), (rcap, paint)]
    bm.faces.index_update()
    mats = {f.index: m for f, m in face_mat}
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    acc = MeshAcc(name)
    acc.add(bm, paint, mat_fn=lambda f: mats.get(f.index, paint))
    # wheels
    seg = 20 if detail == 0 else 10
    r = p['r']
    yw = p['W'] / 2 - 0.13
    for ax in p['axles']:
        X = Lc / 2 - ax * Lc
        for s in (-1, 1):
            Mw = Matrix.Translation((X, s * yw, r)) @ Matrix.Rotation(math.radians(90), 4, 'X')
            acc.add(bm_cyl(0, 0, -0.125, 0.125, r, seg), 'PC_Tyre', matrix=Mw)
            zo = 0.127 if s < 0 else -0.127          # outer face (local z) points away from the car
            rim_z0, rim_z1 = (zo - 0.006, zo + 0.004) if s < 0 else (zo - 0.004, zo + 0.006)
            acc.add(bm_cyl(0, 0, rim_z0, rim_z1, r * 0.68, seg), 'PC_Rim', matrix=Mw)
            if detail == 0:
                for k in range(5):
                    a = 2 * math.pi * k / 5
                    rot = Matrix.Rotation(a, 4, 'Z')
                    zz = (zo + 0.005, zo + 0.012) if s < 0 else (zo - 0.012, zo - 0.005)
                    acc.add(bm_box(0.05, -0.025, zz[0], r * 0.64, 0.025, zz[1]), 'PC_RimDark', matrix=Mw @ rot)
    # lights, grille, mirrors
    fr, rr = info[0], info[-1]
    xf = Lc / 2; xr = -Lc / 2
    zf = info[2]['zbelt'] - 0.08
    w0 = info[2]['wb']
    acc.add(bm_box(xf - 0.16, -w0 + 0.06, zf - 0.07, xf - 0.06, -w0 + 0.42, zf), 'PC_HeadLight')
    acc.add(bm_box(xf - 0.16, w0 - 0.42, zf - 0.07, xf - 0.06, w0 - 0.06, zf), 'PC_HeadLight')
    acc.add(bm_box(xf + 0.0, -0.42, info[0]['zb'] + 0.05, xf + 0.012, 0.42, info[0]['zbelt'] - 0.08), 'PC_CarTrim')
    zt = info[-3]['zbelt'] - 0.1
    wt = info[-3]['wb']
    acc.add(bm_box(xr - 0.01, -wt + 0.08, zt - 0.08, xr + 0.12, wt - 0.08, zt), 'PC_TailLight')
    cabf = [k for k, i in enumerate(info) if i['t'] > 0.5]
    if cabf:
        k = cabf[0]
        X = Lc / 2 - xs[k] * Lc
        zz = info[k]['zbelt'] + 0.05
        for s in (-1, 1):
            y0 = s * info[k]['wb']
            acc.add(bm_box(X - 0.12, min(y0, y0 + s * 0.2), zz, X + 0.02, max(y0, y0 + s * 0.2), zz + 0.12), 'PC_CarTrim')
    return acc


def add_car(A, idx, kind, x, y, z, heading, paint='PC_CarPaintSilver', role='display', note=''):
    """Create one placeholder car object. heading = nose direction in degrees (0 = +X, 90 = +Y)."""
    import bpy
    p = TYPES[kind]
    name = f'{A.prefix}_CAR_{idx:02d}_{kind.capitalize()}_{paint.split("_")[-1]}'
    acc = car_mesh(kind, paint, name)
    ob = acc.build(A.group_coll['PLACEHOLDER_CARS'], A.group_root['PLACEHOLDER_CARS'], sharp_deg=50.0)
    ob.location = (x, y, z)
    ob.rotation_euler = (0, 0, math.radians(heading))
    ob['placeholder_vehicle'] = True
    ob['vehicle_class'] = kind
    ob['length_m'] = p['L']; ob['width_m'] = p['W']; ob['height_m'] = p['H']
    ob['role'] = role
    A.cars.append(dict(name=name, kind=kind, length=p['L'], width=p['W'], height=p['H'], location=[round(x, 3), round(y, 3), round(z, 3)],
                       heading_deg=heading, paint=paint, role=role, note=note, tris=acc.tris()))
    return ob
