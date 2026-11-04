"""Correct the brand identity of one existing flagship (signage only) inside its saved .blend, then re-export its GLBs.

Usage:  python apply_brand_fix.py <NN>          (NN = 01..07; Blender 4.5.15 bpy module, svgelements on BR_PYLIB/sys.path)

What it does (nothing else in the scene is touched):
  1. Opens <asset>/<base>.blend.
  2. Splits every old <P>_LODn_SIGNAGE_Brand mesh by material: mounting structures (pylon, monolith, hanger rod) stay in
     place as <P>_LODn_SIGNAGE_Mounting; the old artwork is moved, unparented, into the top-level collection
     BRAND_SIGNAGE_ORIGINAL_DISABLED (excluded from the view layer, hidden, never exported - delete it at will).
  3. Builds the corrected artwork from ../source_vectors/final/*.svg into collections
     BRAND_SIGNAGE_CORRECTED (LOD0), LOD1_BRAND_SIGNAGE_CORRECTED, LOD2_BRAND_SIGNAGE_CORRECTED, parented to the
     existing <P>_LOD0/1/2 nodes (so the glTF LOD visibility ranges still apply):
        LOD0  extruded vector geometry (fine curve tolerance), illuminated faces, metal returns, mounting rails
        LOD1  the same extrusions at a coarser curve tolerance
        LOD2  one alpha-clipped emissive card per sign rendered from the same vector (exact silhouette + colours)
  4. Saves the .blend and re-exports <base>.glb, <base>_building_only.glb (automotive) and lod/<base>_lod0/1/2.glb with
     the same exporter settings as the original build (pk_core.PAsset._export).
"""
import os, sys, re, json, math, shutil
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.normpath(os.path.join(HERE, '..'))
P17 = os.path.normpath(os.path.join(FIX, '..'))
sys.path.insert(0, os.path.join(P17, '_tools'))
if os.environ.get('BR_PYLIB'):
    sys.path.append(os.environ['BR_PYLIB'])          # svgelements (appended: never shadows bpy's numpy)
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image
from svgelements import Path, Move, Close, Line
import pk_core as C                                   # read-only use: txt() / MeshAcc for supporting facade text

FINAL = os.path.join(FIX, 'source_vectors', 'final')
MANI = json.load(open(os.path.join(FINAL, 'logo_manifest.json')))

# ------------------------------------------------------------------------------------------------ materials
MATS = {
    'BR_SignBack': dict(base='#1a1b1d', rough=0.5, metal=0.5),
    'BR_Chrome': dict(base='#d9dde0', rough=0.08, metal=1.0),
    'BR_BrushedAlu': dict(base='#b9bdc1', rough=0.28, metal=1.0),
    'BR_MB_Face': dict(base='#e6e8ea', rough=0.25, metal=0.3, emit='#f2f6ff', es=3.0),
    'BR_MB_FacetA': dict(base='#dadde0', rough=0.18, metal=0.85, emit='#eef3ff', es=1.7),
    'BR_MB_FacetB': dict(base='#c4c8cc', rough=0.18, metal=0.85, emit='#eef3ff', es=0.7),
    'BR_MB_Ring': dict(base='#dfe2e5', rough=0.12, metal=0.9, emit='#eef3ff', es=1.2),
    'BR_BMW_Black': dict(base='#111214', rough=0.15, metal=0.2),
    'BR_BMW_Chrome': dict(base='#c3c7cb', rough=0.12, metal=1.0),
    'BR_BMW_White': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=1.4),
    'BR_BMW_Blue': dict(base='#0066b1', rough=0.3, emit='#0066b1', es=1.4),
    'BR_PO_Letter': dict(base='#f2f2f2', rough=0.25, metal=0.6, emit='#ffffff', es=2.2),
    'BR_PO_Gold': dict(base='#d2a65e', rough=0.25, metal=1.0),
    'BR_FD_Blue': dict(base='#00095b', rough=0.2, emit='#00095b', es=1.6),
    'BR_FD_White': dict(base='#ffffff', rough=0.25, emit='#ffffff', es=2.4),
    'BR_SS_White': dict(base='#ffffff', rough=0.25, emit='#ffffff', es=3.0),
    'BR_AP_White': dict(base='#f5f5f7', rough=0.2, emit='#ffffff', es=4.0),
    'BR_AP_Steel': dict(base='#c9ccce', rough=0.2, metal=1.0),
    'BR_XM_Orange': dict(base='#ff6900', rough=0.3, emit='#ff6900', es=1.6),
    'BR_XM_White': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=2.0),
    'BR_XM_Letter': dict(base='#1d1d1f', rough=0.35, metal=0.2),
    'BR_XM_Halo': dict(base='#ffffff', rough=0.5, emit='#fff6ec', es=9.0),
}


def hexlin(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    d = MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexlin(d['base'])
    b.inputs['Roughness'].default_value = d.get('rough', 0.4)
    b.inputs['Metallic'].default_value = d.get('metal', 0.0)
    if d.get('emit'):
        b.inputs['Emission Color'].default_value = hexlin(d['emit'])
        b.inputs['Emission Strength'].default_value = d['es']
    return m


def card_mat(name, png_path, strength):
    """Alpha-clipped emissive image card (LOD2 signage / Porsche crest face)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    im = nt.nodes.new('ShaderNodeTexImage')
    im.image = bpy.data.images.load(png_path, check_existing=True)
    nt.links.new(im.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(im.outputs['Color'], b.inputs['Emission Color'])
    nt.links.new(im.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Emission Strength'].default_value = strength
    b.inputs['Roughness'].default_value = 0.3
    try:
        m.blend_method = 'CLIP'; m.alpha_threshold = 0.5
    except Exception:
        pass
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    m.use_backface_culling = False
    return m


# ------------------------------------------------------------------------------------------------ vector reading
def read_layers(svg):
    s = open(svg).read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split()]
    layers = [(m.group(1), m.group(2), m.group(3)) for m in
              re.finditer(r'<path id="([^"]+)" fill="([^"]+)" fill-rule="evenodd" d="([^"]+)"', s)]
    return vb, layers


def adaptive(seg, err):
    """Points (excluding the start) along a curve segment, subdivided until the chord deviates < err (sagitta)."""
    out = []

    def rec(t0, t1, p0, p1, depth):
        tm = 0.5 * (t0 + t1)
        pm = seg.point(tm); pm = (pm.x, pm.y)
        q1 = seg.point(t0 + 0.25 * (t1 - t0)); q3 = seg.point(t0 + 0.75 * (t1 - t0))
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy) or 1e-12
        dev = max(abs((q[0] - p0[0]) * dy - (q[1] - p0[1]) * dx) / ln for q in (pm, (q1.x, q1.y), (q3.x, q3.y)))
        if dev > err and depth < 10:
            rec(t0, tm, p0, pm, depth + 1); rec(tm, t1, pm, p1, depth + 1)
        else:
            out.append(p1)
    a, b = seg.point(0), seg.point(1)
    rec(0.0, 1.0, (a.x, a.y), (b.x, b.y), 0)
    return out


def flatten(d, tol):
    """Path d -> list of closed loops (numpy Nx2, svg coords), curves sampled to chord length <= tol."""
    loops, cur = [], []
    for seg in Path(d):
        if isinstance(seg, Move):
            if len(cur) > 2:
                loops.append(cur)
            cur = [(seg.end.x, seg.end.y)]
        elif isinstance(seg, Close):
            if len(cur) > 2:
                loops.append(cur)
            cur = []
        elif isinstance(seg, Line):
            cur.append((seg.end.x, seg.end.y))
        else:
            cur += [(p[0], p[1]) for p in adaptive(seg, tol)]
    if len(cur) > 2:
        loops.append(cur)
    out = []
    for lp in loops:
        a = np.array(lp, float)
        keep = [0]
        for i in range(1, len(a)):
            if np.linalg.norm(a[i] - a[keep[-1]]) > tol * 0.2:
                keep.append(i)
        a = a[keep]
        if np.linalg.norm(a[0] - a[-1]) < tol * 0.2:
            a = a[:-1]
        if len(a) >= 3:
            a = rdp(a, tol)
            out.append(a)
    return out


def rdp(a, eps):
    """Douglas-Peucker on a closed loop (keeps the first point and the farthest point from it)."""
    def simp(p):
        if len(p) < 3:
            return p
        s, e = p[0], p[-1]
        d = e - s; ln = np.hypot(*d)
        if ln < 1e-12:
            dist = np.hypot(*(p - s).T)
        else:
            dist = np.abs(d[0] * (p[:, 1] - s[1]) - d[1] * (p[:, 0] - s[0])) / ln
        i = int(np.argmax(dist))
        if dist[i] > eps:
            return np.vstack([simp(p[:i + 1])[:-1], simp(p[i:])])
        return np.vstack([s, e])
    k = int(np.argmax(np.hypot(*(a - a[0]).T)))
    ring = np.vstack([a, a[:1]])
    out = np.vstack([simp(ring[:k + 1])[:-1], simp(ring[k:])[:-1]])
    return out if len(out) >= 3 else a


def pip(pt, poly):
    x, y = pt; xs, ys = poly[:, 0], poly[:, 1]
    xj, yj = np.roll(xs, 1), np.roll(ys, 1)
    c = ((ys > y) != (yj > y)) & (x < (xj - xs) * (y - ys) / (yj - ys + 1e-30) + xs)
    return bool(np.count_nonzero(c) % 2)


def groups(loops):
    """Even-odd nesting -> [(outer, [holes])]."""
    depth = []
    for i, a in enumerate(loops):
        probe = a[0]
        depth.append(sum(1 for j, b in enumerate(loops) if j != i and pip(probe, b)))
    res = []
    for i, a in enumerate(loops):
        if depth[i] % 2:
            continue
        holes = [b for j, b in enumerate(loops) if depth[j] == depth[i] + 1 and pip(b[0], a)]
        res.append((a, holes))
    return res


# ------------------------------------------------------------------------------------------------ geometry
class Acc:
    def __init__(self, name):
        self.name, self.co, self.faces, self.fm, self.uv, self.mats = name, [], [], [], [], []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def add(self, verts, faces, mats, uvs):
        base = len(self.co)
        self.co += [tuple(v) for v in verts]
        for f, m, u in zip(faces, mats, uvs):
            self.faces.append([base + i for i in f]); self.fm.append(self.mi(m)); self.uv.append(u)

    def tris(self):
        return sum(len(f) - 2 for f in self.faces)

    def build(self, coll, parent):
        if not self.faces:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.co, [], self.faces)
        for m in self.mats:
            me.materials.append(m)
        me.polygons.foreach_set('material_index', self.fm)
        uvl = me.uv_layers.new(name='UVMap')
        uvl.data.foreach_set('uv', [c for f in self.uv for uv in f for c in uv])
        me.validate(clean_customdata=False)
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        coll.objects.link(ob)
        ob.parent = parent
        return ob


def frame(origin, normal):
    n = Vector(normal).normalized(); up = Vector((0, 0, 1)); r = up.cross(n).normalized()
    M = Matrix.Identity(4)
    for i in range(3):
        M[i][0], M[i][1], M[i][2], M[i][3] = r[i], up[i], n[i], origin[i]
    return M


def tri_fill(outer, holes):
    """Triangulate a 2D polygon with holes; returns (pts Nx2, tris)."""
    bm = bmesh.new()
    allp, edges = [], []
    for lp in [outer] + holes:
        vs = [bm.verts.new((float(x), float(y), 0.0)) for x, y in lp]
        allp += [tuple(p) for p in lp]
        edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bm.verts.index_update()
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return np.array(allp), tris


def extrude_logo(acc, loops2d, z0, z1, M, front, side, back, uvfn):
    """loops2d in local metres (x right, y up). Adds one closed prism per outer+holes group; face roles (front / side /
    back) are assigned from the recalculated outward normals in the local frame, then the piece is placed with M."""
    for outer, holes in groups(loops2d):
        pts, tris = tri_fill(outer, holes)
        n = len(pts)
        bm = bmesh.new()
        vf = [bm.verts.new((float(x), float(y), z1)) for x, y in pts]
        vb = [bm.verts.new((float(x), float(y), z0)) for x, y in pts]
        for a, b, c in tris:
            for vs in ((vf[a], vf[b], vf[c]), (vb[c], vb[b], vb[a])):
                try:
                    bm.faces.new(vs)
                except ValueError:
                    pass
        off = 0
        for lp in [outer] + holes:
            k = len(lp)
            for i in range(k):
                i0, i1 = off + i, off + (i + 1) % k
                try:
                    bm.faces.new((vf[i0], vf[i1], vb[i1], vb[i0]))
                except ValueError:
                    pass
            off += k
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        bm.verts.index_update()
        V = [M @ v.co for v in bm.verts]
        F, Fm, Fu = [], [], []
        for f in bm.faces:
            nz = f.normal.z
            F.append([v.index for v in f.verts])
            Fm.append(front if nz > 0.5 else (back if nz < -0.5 else side))
            Fu.append([uvfn((v.co.x, v.co.y)) for v in f.verts])
        bm.free()
        acc.add(V, F, Fm, Fu)


def logo_loops(key, layer_ids, size, tol_m, by='width'):
    """Return (scale, centre, vb, {layer_id: loops in local metres})."""
    vb, layers = read_layers(os.path.join(FIX, MANI[key]['svg']))
    s = size / (vb[2] if by == 'width' else vb[3])
    cx, cy = vb[0] + vb[2] / 2, vb[1] + vb[3] / 2
    out = {}
    for lid, fill, d in layers:
        if layer_ids is not None and lid not in layer_ids:
            continue
        L = flatten(d, tol_m / s)
        out[lid] = [np.column_stack(((a[:, 0] - cx) * s, -(a[:, 1] - cy) * s)) for a in L]
    return s, (cx, cy), vb, out


def uv_of(vb, s):
    W, H = vb[2] * s, vb[3] * s
    return lambda p: ((p[0] + W / 2) / W, (p[1] + H / 2) / H)


# ------------------------------------------------------------------------------------------------ sign builders
TOL = {0: 0.0015, 1: 0.006}            # max chord deviation in metres (LOD0 / LOD1)


def sign_mono(acc, L, e):
    key = e['logo']
    by = 'height' if 'h' in e else 'width'
    s, c, vb, lay = logo_loops(key, None, e.get('h', e.get('w')), TOL[L], by)
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    loops = [lp for v in lay.values() for lp in v]
    so = e.get('standoff', 0.0)
    extrude_logo(acc, loops, so, so + e['depth'], M, mat(e['face']), mat(e['side']), mat(e.get('back', 'BR_SignBack')), uv_of(vb, s))
    return vb, s


def sign_layered(acc, L, e):
    key = e['logo']
    by = 'height' if 'h' in e else 'width'
    s, c, vb, lay = logo_loops(key, None, e.get('h', e.get('w')), TOL[L], by)
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    z = 0.0
    for i, (lid, loops) in enumerate(lay.items()):
        dz = e['depth'] if i == 0 else e.get('layer_dz', 0.012)
        z0 = 0.0 if i == 0 else z - 0.002
        extrude_logo(acc, loops, z0, z + dz, M, mat(e['mats'][lid]), mat(e.get('side', 'BR_Chrome')) if i == 0 else mat(e['mats'][lid]),
                     mat('BR_SignBack'), uv_of(vb, s))
        z += dz
    return vb, s


def sign_plaque(acc, L, e, tex_dir):
    key = e['logo']
    s, c, vb, lay = logo_loops(key, None, e['h'], TOL[L], 'height')
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    face = card_mat('BR_PO_CrestFace', os.path.join(tex_dir, 'brand_porsche_crest.png'), 0.8)
    extrude_logo(acc, [lp for v in lay.values() for lp in v], 0.0, e['depth'], M, face, mat('BR_PO_Gold'), mat('BR_SignBack'), uv_of(vb, s))
    return vb, s


def sign_mb_star(acc, L, e):
    """Three-pointed star in ring, dimensional: proportions measured from the official star vector
    (ring outer/inner radius, arm tip radius, inner vertex radius/angles); arms built as faceted pyramids."""
    vb, layers = read_layers(os.path.join(FIX, MANI['mercedes_star']['svg']))
    loops = flatten(layers[0][2], 0.01)
    cx, cy = vb[0] + vb[2] / 2, vb[1] + vb[3] / 2
    s = e['d'] / vb[2]
    holes = [a for a in loops if np.max(np.hypot(a[:, 0] - cx, a[:, 1] - cy)) < vb[2] / 2 * 0.99]
    r_out = vb[2] / 2
    r_in = max(np.max(np.hypot(a[:, 0] - cx, a[:, 1] - cy)) for a in holes)
    V = []
    for a in holes:
        dd = np.hypot(a[:, 0] - cx, a[:, 1] - cy); k = int(np.argmin(dd))
        V.append((dd[k], math.atan2(-(a[k, 1] - cy), a[k, 0] - cx)))      # y-up angle
    r_v = float(np.mean([v[0] for v in V]))
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    seg = 96 if L == 0 else 40
    D = e['depth']
    ring_o = [(r_out * s * math.cos(2 * math.pi * i / seg), r_out * s * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    ring_i = [(r_in * s * math.cos(2 * math.pi * i / seg), r_in * s * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    extrude_logo(acc, [np.array(ring_o), np.array(ring_i)], 0.0, D * 0.55, M, mat('BR_MB_Ring'), mat('BR_Chrome'), mat('BR_SignBack'),
                 lambda p: (0, 0))
    # star outline: tips opposite the inner vertices, at the ring inner radius (+ small overlap into the ring)
    pts = []
    for (rv, av) in sorted(V, key=lambda v: v[1]):
        pts.append((av, rv))
        pts.append((av + math.pi, r_in * 1.01))
    pts = sorted(((a % (2 * math.pi), r) for a, r in pts))
    P = [Vector((r * s * math.cos(a), r * s * math.sin(a), 0.0)) for a, r in pts]
    zb, zt = D * 0.35, D * 0.55
    apex = Vector((0, 0, D))
    verts, faces, fm, fu = [], [], [], []
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        tip_first = pts[i][1] > pts[(i + 1) % n][1]
        base = len(verts)
        verts += [M @ apex, M @ Vector((a.x, a.y, zt)), M @ Vector((b.x, b.y, zt))]
        faces.append([base, base + 1, base + 2]); fm.append(mat('BR_MB_FacetA' if tip_first else 'BR_MB_FacetB')); fu.append([(0, 0)] * 3)
        base = len(verts)
        verts += [M @ Vector((a.x, a.y, zt)), M @ Vector((a.x, a.y, zb)), M @ Vector((b.x, b.y, zb)), M @ Vector((b.x, b.y, zt))]
        faces.append([base, base + 1, base + 2, base + 3]); fm.append(mat('BR_Chrome')); fu.append([(0, 0)] * 4)
    base = len(verts)
    verts += [M @ Vector((p.x, p.y, zb)) for p in P]
    faces.append(list(range(base + n - 1, base - 1, -1))); fm.append(mat('BR_SignBack')); fu.append([(0, 0)] * n)
    acc.add(verts, faces, fm, fu)
    return [0, 0, vb[2], vb[3]], s


def sign_card(acc, e, png, mname, strength, vb_wh, z=None):
    """LOD2: one quad card with the vector-rendered texture (2 triangles)."""
    w, h = vb_wh
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    z = e.get('depth', 0.05) if z is None else z
    q = [M @ Vector(p) for p in ((-w / 2, -h / 2, z), (w / 2, -h / 2, z), (w / 2, h / 2, z), (-w / 2, h / 2, z))]
    m = card_mat(mname, png, strength)
    acc.add(q, [[0, 1, 2, 3]], [m], [[(0, 0), (1, 0), (1, 1), (0, 1)]])


def rail(acc, e, w_logo, h_logo, mname='BR_SignBack'):
    """Slim mounting rail under a free-standing rooftop wordmark."""
    M = frame(e['o'], e.get('n', (0, -1, 0)))
    x0, x1 = -w_logo / 2 - 0.25, w_logo / 2 + 0.25
    y0, y1 = -h_logo / 2 - 0.16, -h_logo / 2 + 0.02
    z0, z1 = -0.05, 0.28
    c = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    V = [M @ Vector(p) for p in c]
    F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    acc.add(V, F, [mat(mname)] * 6, [[(0, 0)] * 4] * 6)


# ------------------------------------------------------------------------------------------------ per-brand specs
N = (0, -1, 0)
SPECS = {
    '01': dict(folder='01_mercedes_showroom', base='mercedes_showroom', P='P01', keep=[], elements=[
        dict(name='RooftopWordmark', kind='mono', logo='mercedes_wordmark', o=(-4.0, 4.80, 17.62 + 0.70), w=11.0, depth=0.16,
             face='BR_MB_Face', side='BR_Chrome', rail=True, sign='rooftop_wordmark'),
        dict(name='CoreStar', kind='mb_star', logo='mercedes_star', o=(21.0, 7.80, 18.1), d=4.0, depth=0.34, sign='core_star'),
        dict(name='CoreWordmark', kind='mono', logo='mercedes_wordmark', o=(21.0, 7.80, 15.2), w=3.4, depth=0.04,
             face='BR_MB_Face', side='BR_Chrome', sign='core_wordmark'),
    ], camera=dict(target=(5.5, 6.0, 17.2), width=42.0, road=(-16.0, -9.0, 1.2), road_lens=30)),
    '02': dict(folder='02_bmw_showroom', base='bmw_showroom', P='P02', keep=['PC_PanelWhite'], elements=[
        dict(name='BladeRoundel', kind='layered', logo='bmw_roundel', o=(-21.7, 8.35, 7.6), w=3.8, depth=0.16, layer_dz=0.012,
             mats=dict(ring='BR_BMW_Black', outer_chrome='BR_BMW_Chrome', letters='BR_BMW_White', inner_chrome='BR_BMW_Chrome',
                       white='BR_BMW_White', blue='BR_BMW_Blue'), side='BR_BMW_Chrome', sign='blade_roundel'),
        dict(name='PylonRoundel', kind='layered', logo='bmw_roundel', o=(-24.9, 1.18, 7.0), w=2.3, depth=0.14, layer_dz=0.01,
             mats=dict(ring='BR_BMW_Black', outer_chrome='BR_BMW_Chrome', letters='BR_BMW_White', inner_chrome='BR_BMW_Chrome',
                       white='BR_BMW_White', blue='BR_BMW_Blue'), side='BR_BMW_Chrome', sign='pylon_roundel'),
    ], camera=dict(target=(-23.0, 5.0, 7.2), width=9.5, road=(-38.0, -9.0, 1.2), road_lens=40)),
    '03': dict(folder='03_porsche_showroom', base='porsche_showroom', P='P03', keep=['PC_PanelGraphite'], elements=[
        dict(name='BoxWordmark', kind='mono', logo='porsche_wordmark', o=(-3.0, 4.78, 14.15), h=0.5, depth=0.05,
             face='BR_PO_Letter', side='BR_BrushedAlu', sign='box_wordmark'),
        dict(name='MonolithCrest', kind='plaque', logo='porsche_crest', o=(-23.5, 1.0, 1.66), h=1.22, depth=0.05, sign='monolith_crest'),
        dict(name='MonolithWordmark', kind='mono', logo='porsche_wordmark', o=(-23.5, 1.0, 0.66), w=3.5, depth=0.02,
             face='BR_PO_Letter', side='BR_BrushedAlu', sign='monolith_wordmark'),
    ], camera=dict(target=(-13.5, 2.0, 7.5), width=30.0, road=(-42.0, -9.0, 1.2), road_lens=32),
        camera2=dict(target=(-23.5, 1.0, 1.4), width=7.0)),
    '04': dict(folder='04_ford_showroom', base='ford_showroom', P='P04', keep=[], elements=[
        dict(name='PortalOval', kind='layered', logo='ford_oval', o=(0.0, 6.48, 8.5), w=7.4, depth=0.18, layer_dz=0.025,
             mats=dict(oval='BR_FD_Blue', white0='BR_FD_White', white1='BR_FD_White', white2='BR_FD_White'), side='BR_Chrome',
             sign='portal_oval'),
    ], text=[
        dict(body='SERVICE', o=(24.0, 9.95, 6.3), size=0.6, depth=0.06, font='dsemi', front='FD_Letter', side='PC_AluSilver', spacing=1.1),
        dict(body='PARTS & SERVICE RECEPTION', o=(-26.0, 9.95, 3.6), size=0.34, depth=0.04, font='dsemi', front='FD_Letter', side='PC_AluSilver'),
    ], camera=dict(target=(0.0, 6.0, 8.3), width=14.0, road=(-24.0, -9.0, 1.2), road_lens=40)),
    '05': dict(folder='05_samsung_flagship', base='samsung_flagship', P='P05', keep=[], elements=[
        dict(name='FasciaWordmark', kind='mono', logo='samsung_wordmark', o=(5.5, 6.38, 11.45), h=0.75, depth=0.12,
             face='BR_SS_White', side='BR_BrushedAlu', sign='fascia_wordmark', card_colour='#ffffff'),
    ], text=[
        dict(body='EXPERIENCE STORE', o=(5.5, 6.73, 5.65), size=0.2, depth=0.02, font='dsemi', front='SS_Letter', side='SS_Letter', spacing=1.3),
    ], camera=dict(target=(5.5, 6.0, 9.6), width=13.0, road=(-16.0, -9.0, 1.2), road_lens=38)),
    '06': dict(folder='06_apple_flagship', base='apple_flagship', P='P06', keep=['PC_Stainless'], elements=[
        dict(name='SuspendedLogo', kind='mono', logo='apple_logo', o=(0.0, 6.38, 6.925), h=1.95, depth=0.06,
             face='BR_AP_White', side='BR_AP_Steel', back='BR_AP_White', sign='logo'),
        dict(name='FlankLogo', kind='mono', logo='apple_logo', o=(-14.35, 5.40, 6.0), h=1.0, depth=0.04,
             face='BR_AP_White', side='BR_AP_Steel', back='BR_AP_White', sign='flank_logo'),
    ], camera=dict(target=(-5.0, 5.0, 6.6), width=22.0, road=(-24.0, -9.0, 1.2), road_lens=36)),
    '07': dict(folder='07_xiaomi_flagship', base='xiaomi_flagship', P='P07', keep=[], elements=[
        dict(name='PortalSymbol', kind='layered', logo='xiaomi_mi_symbol', o=(11.25, 6.75, 7.8), n=(0.70710678, -0.70710678, 0.0),
             w=2.2, depth=0.10, layer_dz=0.015, mats=dict(squircle='BR_XM_Orange', mi='BR_XM_White'), side='BR_XM_Orange',
             sign='portal_badge'),
        dict(name='FasciaWordmark', kind='mono', logo='xiaomi_wordmark', o=(-3.52, 4.68, 9.75), h=0.95, depth=0.08, standoff=0.05,
             face='BR_XM_Letter', side='BR_XM_Letter', back='BR_XM_Halo', sign='fascia_wordmark', card_colour='#1d1d1f'),
    ], camera=dict(target=(4.0, 4.0, 8.6), width=22.0, road=(-22.0, -9.0, 1.2), road_lens=34)),
}


def recolour_png(src, dst, hexcol):
    im = Image.open(src).convert('RGBA')
    r, g, b = [int(hexcol[i:i + 2], 16) for i in (1, 3, 5)]
    a = im.split()[3]
    Image.merge('RGBA', (Image.new('L', im.size, r), Image.new('L', im.size, g), Image.new('L', im.size, b), a)).save(dst)


def element_png(e, tex_dir):
    key = e['logo']
    src = os.path.join(FIX, MANI[key]['png'])
    dst = os.path.join(tex_dir, f'brand_{key}' + (f'_{e["card_colour"][1:]}' if e.get('card_colour') else '') + '.png')
    if e.get('card_colour'):
        recolour_png(src, dst, e['card_colour'])
    elif e.get('face') in ('BR_MB_Face', 'BR_PO_Letter', 'BR_AP_White'):
        recolour_png(src, dst, MATS[e['face']]['base'])
    else:
        shutil.copy(src, dst)
    return dst


# ------------------------------------------------------------------------------------------------ main
def export(path, objs, textures=True, lights=True):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs:
        try:
            ob.hide_set(False)
        except RuntimeError:
            pass
        ob.select_set(True)
    return bpy.ops.export_scene.gltf(
        filepath=path, export_format='GLB', use_selection=True, export_extras=True,
        export_lights=lights, export_cameras=False, export_apply=True, export_yup=True,
        export_texcoords=True, export_normals=True, export_tangents=False,
        export_materials='EXPORT', export_image_format='AUTO' if textures else 'NONE',
        export_animations=False, export_import_convert_lighting_mode='SPEC')


def main(num):
    sp = SPECS[num]
    adir = os.path.join(P17, sp['folder'])
    blend = os.path.join(adir, sp['base'] + '.blend')
    bpy.ops.wm.open_mainfile(filepath=blend)
    P = sp['P']
    root = [o for o in bpy.data.objects if o.parent is None and o.type == 'EMPTY' and o.get('brand_signs')][0]
    asset_coll = root.users_collection[0]
    if bpy.data.collections.get('BRAND_SIGNAGE_CORRECTED'):
        raise SystemExit('already corrected - restore the .blend from git before re-running')
    lod_root = {L: bpy.data.objects[f'{P}_LOD{L}'] for L in (0, 1, 2)}
    lod_coll = {L: bpy.data.collections['LOD0' if L == 0 else f'LOD{L}'] for L in (0, 1, 2)}
    tex_dir = os.path.join(adir, 'textures')
    # ---- 1. split old signage
    dis = bpy.data.collections.new('BRAND_SIGNAGE_ORIGINAL_DISABLED')
    bpy.context.scene.collection.children.link(dis)
    report = dict(asset=sp['folder'], removed=[], kept_mounting=[], added=[])
    for L in (0, 1, 2):
        old = bpy.data.objects[f'{P}_LOD{L}_SIGNAGE_Brand']
        keep_idx = [i for i, m in enumerate(old.data.materials) if m and m.name in sp['keep']]
        old_tris = sum(len(p.vertices) - 2 for p in old.data.polygons)
        art = old.copy(); art.data = old.data.copy()
        art.name = f'{P}_LOD{L}_SIGNAGE_Brand_ORIGINAL'
        mw = old.matrix_world.copy()
        dis.objects.link(art); art.parent = None; art.matrix_world = mw
        # artwork copy: drop mounting faces
        bm = bmesh.new(); bm.from_mesh(art.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in keep_idx], context='FACES')
        bm.to_mesh(art.data); bm.free()
        art.hide_render = True; art.hide_viewport = True
        if keep_idx:
            bm = bmesh.new(); bm.from_mesh(old.data)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index not in keep_idx], context='FACES')
            bm.to_mesh(old.data); bm.free()
            old.name = f'{P}_LOD{L}_SIGNAGE_Mounting'; old.data.name = old.name
            report['kept_mounting'].append(dict(lod=L, object=old.name, tris=sum(len(p.vertices) - 2 for p in old.data.polygons),
                                                materials=sp['keep']))
        else:
            bpy.data.objects.remove(old)
        report['removed'].append(dict(lod=L, object=art.name, tris=sum(len(p.vertices) - 2 for p in art.data.polygons),
                                      original_tris=old_tris))
    vl = bpy.context.view_layer.layer_collection.children.get('BRAND_SIGNAGE_ORIGINAL_DISABLED')
    if vl:
        vl.exclude = True
    # ---- 2. corrected signage
    newcoll = {}
    for L in (0, 1, 2):
        c = bpy.data.collections.new('BRAND_SIGNAGE_CORRECTED' if L == 0 else f'LOD{L}_BRAND_SIGNAGE_CORRECTED')
        lod_coll[L].children.link(c); newcoll[L] = c
    signs = []
    for e in sp['elements']:
        png = element_png(e, tex_dir)
        if e['kind'] == 'plaque':
            shutil.copy(os.path.join(FIX, MANI['porsche_crest']['png']), os.path.join(tex_dir, 'brand_porsche_crest.png'))
        for L in (0, 1, 2):
            acc = Acc(f'{P}_LOD{L}_BRAND_SIGNAGE_CORRECTED_{e["name"]}')
            if L < 2:
                if e['kind'] == 'mono':
                    vb, s = sign_mono(acc, L, e)
                elif e['kind'] == 'layered':
                    vb, s = sign_layered(acc, L, e)
                elif e['kind'] == 'plaque':
                    vb, s = sign_plaque(acc, L, e, tex_dir)
                else:
                    vb, s = sign_mb_star(acc, L, e)
                if e.get('rail'):
                    rail(acc, e, vb[2] * s, vb[3] * s)
                wh = (vb[2] * s, vb[3] * s)
            else:
                strength = 1.6 if e['kind'] in ('layered', 'plaque') else 2.5
                if e['kind'] == 'mb_star':
                    star_png = os.path.join(tex_dir, 'brand_mercedes_star.png')
                    recolour_png(os.path.join(FIX, MANI['mercedes_star']['png']), star_png, '#e6e8ea')
                    png_use = star_png
                elif e['kind'] == 'plaque':
                    png_use = os.path.join(tex_dir, 'brand_porsche_crest.png')
                else:
                    png_use = png
                sign_card(acc, e, png_use, f'BR_Card_{e["name"]}_{os.path.splitext(os.path.basename(png_use))[0]}', strength, wh,
                          z=e.get('depth', 0.05) + e.get('standoff', 0.0) + 0.01)
                if e.get('rail'):
                    rail(acc, e, wh[0], wh[1])
            ob = acc.build(newcoll[L], lod_root[L])
            ob['brand_signage'] = e['logo']
            ob['source_vector'] = MANI[e['logo']]['svg']
            report['added'].append(dict(lod=L, object=ob.name, tris=acc.tris(), logo=e['logo'], size_m=[round(wh[0], 3), round(wh[1], 3)]))
        signs.append(dict(name=e['sign'], center=list(e['o']), cap_height=round(wh[1], 3), normal=list(e.get('n', N)),
                          width=round(wh[0], 3), logo=e['logo']))
    # supporting facade text (licensed Inter Display, recreated with the original parameters)
    for t in sp.get('text', []):
        for L in (0, 1):
            acc = C.MeshAcc(f'{P}_LOD{L}_BRAND_SIGNAGE_CORRECTED_Text_{re.sub("[^A-Za-z]", "", t["body"])[:16]}')
            C.txt(acc, L, t['body'], C.place('-Y', Vector(t['o'])), t['size'], t['depth'], t['font'], t['front'], t['side'],
                  spacing=t.get('spacing', 1.0))
            ob = acc.build(newcoll[L], lod_root[L])
            report['added'].append(dict(lod=L, object=ob.name, tris=acc.tris(), text=t['body'], font='Inter Display SemiBold (OFL)'))
    root['brand_signs'] = json.dumps(signs)
    root['brand_signage_correction'] = json.dumps(dict(
        note='Brand signage corrected from official / officially-sourced vectors - see '
             'premium_commercial_17/FLAGSHIP_BRANDING_CORRECTION/BRAND_ASSET_SOURCES.md. Internal test asset; '
             'no brand partnership or endorsement implied.',
        logos=sorted({e['logo'] for e in sp['elements']})))
    # ---- 3. save + export
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
    allobjs = list(asset_coll.all_objects)
    cars = set(bpy.data.collections['PLACEHOLDER_CARS'].all_objects)
    glb = os.path.join(adir, sp['base'] + '.glb')
    export(glb, allobjs)
    bonly = os.path.join(adir, sp['base'] + '_building_only.glb')
    if os.path.exists(bonly):
        export(bonly, [o for o in allobjs if o not in cars])
    for L in (0, 1, 2):
        objs = [root, lod_root[L]] + list(lod_coll[L].all_objects)
        export(os.path.join(adir, 'lod', f'{sp["base"]}_lod{L}.glb'), objs, textures=False, lights=False)
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
    json.dump(report, open(os.path.join(FIX, '_work', f'apply_{num}.json'), 'w'), indent=1)
    print('APPLIED', num, json.dumps(report)[:1500])


if __name__ == '__main__':
    os.makedirs(os.path.join(FIX, '_work'), exist_ok=True)
    main(sys.argv[-1])
