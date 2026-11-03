"""Shared kit for the 17 additional Dubai roadside stores.

Builds on (and never modifies) the prototype library `prototypes/_tools/roadside_lib.py`:
same units (1 unit = 1 m, Z up), same orientation (road-facing front = Blender -Y -> glTF/Godot +Z),
same LOD node naming/extras (<PREFIX>_LOD0/1/2), same `*-convcolonly` collision boxes, same night-light group.

What this kit adds:
  * the new on-disk layout  <store>/<base>.blend, <base>.glb, lod/, textures/, renders/
  * generic architectural components (glazing, walls with openings, arches, awnings, pergolas, furniture,
    cars, drive-through, interiors) so every store script only describes its own distinctive massing
  * per-LOD geometry-only GLB export (for independent triangle read-back)
  * sign registry used by the render script to check brand-sign readability from the road
"""
import os, sys, math, random, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
A17 = os.path.normpath(os.path.join(HERE, '..'))
PROTO = os.path.normpath(os.path.join(A17, '..', 'prototypes', '_tools'))
TEXCACHE = os.path.join(HERE, 'texcache')
sys.path.insert(0, PROTO)

import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw, ImageFont
import roadside_lib as R
from roadside_lib import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_ring_prism, bm_hquad, bm_quad, bm_vquad,
                          bm_poly_flat, bm_sphere, bm_text, rounded_rect, place, front_back, bm_prism_local,
                          rect_subtract, hex_lin, MeshAcc, arabic)

FONT = dict(
    black=R.FONT_BLACK, bold=R.FONT_BOLD, semi=R.FONT_SEMI, display=R.FONT_DISPLAY_BOLD,
    arabic=R.FONT_ARABIC,
    black_i='/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf',
    bold_i='/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf',
    xbold_i='/usr/share/fonts/opentype/inter/Inter-ExtraBoldItalic.otf',
    light='/usr/share/fonts/opentype/inter/Inter-Light.otf',
    thin='/usr/share/fonts/opentype/inter/Inter-Thin.otf',
    regular='/usr/share/fonts/opentype/inter/Inter-Regular.otf',
    medium='/usr/share/fonts/opentype/inter/Inter-Medium.otf',
    serif_b='/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    serif='/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
    serif_bi='/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf',
    caladea_b='/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf',
)

# ---------------------------------------------------------------------------
# textures: smaller JPEG quality than the prototypes (17 more stores), shared cache across stores
# ---------------------------------------------------------------------------
JPEG_Q = 84


def _save_q(arr, path):
    a = np.clip(arr, 0, 1)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(path.replace('.png', '.jpg'), quality=JPEG_Q, subsampling=0)


R._save = _save_q
_orig_ensure = R.ensure_texture


def _ensure_texture(key, tex_dir):
    os.makedirs(tex_dir, exist_ok=True)
    have = any(os.path.exists(f'{tex_dir}/{key}_albedo{e}') for e in ('.jpg', '.png'))
    if not have:
        _orig_ensure(key, TEXCACHE)                 # generate once into the shared cache
        for f in os.listdir(TEXCACHE):
            if f.startswith(key + '_'):
                shutil.copy(os.path.join(TEXCACHE, f), os.path.join(tex_dir, f))
    return _orig_ensure(key, tex_dir)


R.ensure_texture = _ensure_texture


def tex_brick_factory(seed, hue):
    def gen(d, n=512):
        # 215 x 65 mm bricks + 10 mm mortar, running bond; tile covers 0.9 m x 0.9 m (4 bricks x 12 courses)
        ys, xs = np.mgrid[0:n, 0:n] / n
        rows = ys * 12.0
        r = np.floor(rows).astype(int)
        cols = xs * 4.0 + 0.5 * (r % 2)
        c = np.floor(cols).astype(int) % 4
        fu, fv = cols - np.floor(cols), rows - np.floor(rows)
        mu = np.minimum(fu, 1 - fu) * 0.225
        mv = np.minimum(fv, 1 - fv) * 0.075
        e = np.minimum(mu, mv)
        brick = np.clip((e - 0.0035) / 0.0025, 0, 1)
        rng = np.random.default_rng(seed)
        tone = rng.normal(0, 1, (12, 4))[r % 12, c]
        noise = R._fft_noise(n, 0.9, seed + 1); fine = R._fft_noise(n, 0.2, seed + 2)
        base = np.array(hue)[None, None, :] * (1 + 0.10 * tone[..., None] + 0.04 * noise[..., None] + 0.02 * fine[..., None])
        mortar = np.array([0.62, 0.60, 0.56])[None, None, :]
        col = base * brick[..., None] + mortar * (1 - brick[..., None])
        h = brick * 1.0 + 0.1 * fine
        rough = np.clip(0.78 + 0.05 * fine + (1 - brick) * 0.12, 0.6, 0.95)
        return col, h, rough
    return gen


def _mk_brick(key, seed, hue):
    g = tex_brick_factory(seed, hue)

    def gen(d):
        col, h, rough = g(d)
        R._save(col, f'{d}/{key}_albedo.png'); R._save(R._orm(rough), f'{d}/{key}_orm.png')
        R._save(R._normal_from_height(h * 3.0, 1.1), f'{d}/{key}_normal.png')
    R.EXTRA_TEXTURES[key] = gen


_mk_brick('brick', 301, (0.52, 0.22, 0.15))
_mk_brick('brickgrey', 311, (0.30, 0.29, 0.29))
_mk_brick('brickcream', 321, (0.78, 0.66, 0.50))


def tex_checker(d, n=256):
    # 2 x 2 glossy ceramic tiles, 0.3 m each -> tile covers 0.6 m
    ys, xs = np.mgrid[0:n, 0:n] / n
    cell = (np.floor(xs * 2).astype(int) + np.floor(ys * 2).astype(int)) % 2
    fu, fv = (xs * 2) % 1.0, (ys * 2) % 1.0
    e = np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)) * 0.3
    grout = np.clip((e - 0.002) / 0.002, 0, 1)
    red = np.array([0.78, 0.09, 0.10]); wht = np.array([0.93, 0.92, 0.89])
    col = np.where(cell[..., None] == 1, red, wht) * (0.55 + 0.45 * grout[..., None])
    R._save(col, f'{d}/checker_albedo.png')
    R._save(R._orm(np.clip(0.22 + (1 - grout) * 0.5, 0, 1)), f'{d}/checker_orm.png')
    R._save(R._normal_from_height(grout * 3.0, 1.0), f'{d}/checker_normal.png')


def tex_woodv(d, n=512):
    # vertical slat cladding (the generic wood texture rotated 90 degrees), tile covers 1 m
    R.tex_wood(d, n)
    for ch in ('albedo', 'orm'):
        p = f'{d}/wood_{ch}.jpg'
        Image.open(p).transpose(Image.ROTATE_90).save(f'{d}/woodv_{ch}.jpg', quality=JPEG_Q, subsampling=0)
        os.remove(p)
    for f in ('wood_normal.jpg',):
        if os.path.exists(f'{d}/{f}'):
            os.remove(f'{d}/{f}')


def tex_tilefloor(d, n=512):
    # 0.6 m large-format porcelain floor tiles, tile covers 1.2 m
    ys, xs = np.mgrid[0:n, 0:n] / n
    fu, fv = (xs * 2) % 1.0, (ys * 2) % 1.0
    e = np.minimum(np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)) * 0.6
    grout = np.clip((e - 0.002) / 0.002, 0, 1)
    tid = (np.floor(xs * 2).astype(int) + 2 * np.floor(ys * 2).astype(int))
    tone = np.random.default_rng(5).normal(0, 1, 4)[tid]
    noise = R._fft_noise(n, 1.0, 6)
    v = (0.80 + 0.015 * tone + 0.015 * noise) * (0.7 + 0.3 * grout)
    R._save(np.stack([v, v * 0.985, v * 0.96], -1), f'{d}/tilefloor_albedo.png')
    R._save(R._orm(np.clip(0.18 + (1 - grout) * 0.5, 0, 1)), f'{d}/tilefloor_orm.png')


R.EXTRA_TEXTURES['checker'] = tex_checker
R.EXTRA_TEXTURES['woodv'] = tex_woodv
R.EXTRA_TEXTURES['tilefloor'] = tex_tilefloor


def defmat(name, base, rough=0.4, metal=0.0, emit=None, es=1.0, **kw):
    d = dict(base=base, rough=rough, metal=metal, **kw)
    if emit:
        d.update(emit=emit, es=es)
    R.MATERIAL_DEFS[name] = d
    return name


# generic additions (shared across the 17 stores, prefix RS_ like the prototypes)
R.MATERIAL_DEFS.update({
    'RS_Brick': dict(base='#ffffff', tex='brick', tile=0.9),
    'RS_BrickGrey': dict(base='#ffffff', tex='brickgrey', tile=0.9),
    'RS_BrickCream': dict(base='#ffffff', tex='brickcream', tile=0.9),
    'RS_Checker': dict(base='#ffffff', tex='checker', tile=0.6),
    'RS_WoodV': dict(base='#ffffff', tex='woodv', tile=1.0),
    'RS_TileFloor': dict(base='#ffffff', tex='tilefloor', tile=1.2),
    'RS_Stucco': dict(base='#d9c7a6', rough=0.82),
    'RS_StuccoWhite': dict(base='#ece8df', rough=0.8),
    'RS_Chrome': dict(base='#d9dde0', rough=0.12, metal=1.0),
    'RS_Gold': dict(base='#c9a24a', rough=0.28, metal=1.0),
    'RS_CarGlass': dict(base='#0e1519', rough=0.05, metal=0.2, spec=0.8),
    'RS_CarWhite': dict(base='#e8e9e8', rough=0.28, metal=0.5),
    'RS_CarBlack': dict(base='#15171a', rough=0.25, metal=0.6),
    'RS_CarSilver': dict(base='#a4a9ad', rough=0.3, metal=0.8),
    'RS_CarRed': dict(base='#9c1620', rough=0.3, metal=0.6),
    'RS_CarBlue': dict(base='#1d3e72', rough=0.3, metal=0.6),
    'RS_CarGrey': dict(base='#51565b', rough=0.3, metal=0.6),
    'RS_CarGold': dict(base='#a98e5d', rough=0.3, metal=0.6),
    'RS_Tail': dict(base='#7a0a0f', rough=0.25, emit='#ff2a1e', es=0.2),
    'RS_Soil': dict(base='#3b2c20', rough=0.95),
    'RS_Planter': dict(base='#bdb6a8', rough=0.7),
    'RS_Terracotta': dict(base='#b5683f', rough=0.7),
    'RS_Fabric': dict(base='#c7c1b4', rough=0.9, double=True),
    'RS_Rattan': dict(base='#6a5036', rough=0.7),
    'RS_Cushion': dict(base='#2c2c2e', rough=0.9),
    'RS_Cardboard': dict(base='#a67c52', rough=0.85),
    'RS_Bread': dict(base='#b9792f', rough=0.75),
    'RS_Pastry': dict(base='#d6a45a', rough=0.7),
    'RS_Pink': dict(base='#f2a3c2', rough=0.5),
    'RS_Cream': dict(base='#f4eddb', rough=0.6),
    'RS_Choc': dict(base='#4a2a18', rough=0.55),
})


# ---------------------------------------------------------------------------
# text, signs
# ---------------------------------------------------------------------------
def _shear(s):
    return Matrix(((1, s, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))


def orient_closed_pieces(bm):
    """Flip every watertight connected piece whose signed volume is negative (font extrusion occasionally winds a thin glyph inward)."""
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    seen, flip = set(), []
    for v0 in bm.verts:
        if v0.index in seen or not v0.link_faces:
            continue
        stack, faces, edges = [v0], set(), set()
        seen.add(v0.index)
        while stack:
            v = stack.pop()
            for e in v.link_edges:
                edges.add(e.index)
                faces.update(f.index for f in e.link_faces)
                o = e.other_vert(v)
                if o.index not in seen:
                    seen.add(o.index); stack.append(o)
        if all(len(bm.edges[i].link_faces) == 2 for i in edges):
            pts = {l.vert.index: np.array(l.vert.co, dtype=np.float64) for fi in faces for l in bm.faces[fi].loops}
            c = np.mean(list(pts.values()), axis=0)
            vol = 0.0
            for fi in faces:
                vs = [np.array(l.vert.co, dtype=np.float64) - c for l in bm.faces[fi].loops]
                for j in range(1, len(vs) - 1):
                    vol += np.dot(vs[0], np.cross(vs[j], vs[j + 1])) / 6.0
            if vol < 0:
                flip.extend(bm.faces[i] for i in faces)
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    return len(flip)


def txt(acc, L, body, M, size, depth=0.06, font='bold', front='RS_PaintWhite', side=None, spacing=1.0, shear=0.0,
        align='CENTER', valign='CENTER', min_size_lod2=0.3):
    """Channel-letter style text in the face frame M (see roadside_lib.place). LOD2 keeps flat text for large signs."""
    if L == 2 and size < min_size_lod2:
        return
    res = {0: 3, 1: 2, 2: 1}[L]
    bevel = 0.006 if (L == 0 and size >= 0.5) else 0.0
    f = FONT.get(font, font)
    bm = bm_text(body, f, size, depth if L < 2 else 0.0, bevel, res, align=align, valign=valign, spacing=spacing)
    if L < 2 and depth > 0:
        orient_closed_pieces(bm)
    mat = M if not shear else M @ _shear(shear)
    acc.add(bm, front, matrix=mat, mat_fn=front_back(front, side or front))


def panel(acc, L, M, w, h, depth, face, edge=None, r=0.0, bevel=0.012):
    """Flat sign face (optionally rounded) in face frame M, front at +local Z."""
    edge = edge or face
    if r > 0:
        pts = rounded_rect(-w / 2, -h / 2, w / 2, h / 2, r, 4 if L == 0 else 2 if L == 1 else 1)
        bm = bm_prism(pts, 0.0, depth)
    else:
        bm = bm_box(-w / 2, -h / 2, 0.0, w / 2, h / 2, depth, bevel=bevel if L == 0 else 0.0)
    acc.add(bm, face, matrix=M, mat_fn=front_back(face, edge))


def disc(acc, L, M, r, depth, face, edge=None):
    seg = {0: 40, 1: 20, 2: 10}[L]
    edge = edge or face
    acc.add(bm_cyl(0, 0, 0, depth, r, seg), face, matrix=M, mat_fn=front_back(face, edge))


def poly(acc, pts, depth, M, face, edge=None):
    acc.add(bm_prism_local(pts, depth), face, matrix=M, mat_fn=front_back(face, edge or face))


def register_sign(A, name, center, cap_h, normal=(0, -1, 0), width=2.0):
    A.signs.append(dict(name=name, center=list(center), cap_height=cap_h, normal=list(normal), width=width))


# ---------------------------------------------------------------------------
# Asset container with the new layout
# ---------------------------------------------------------------------------
class Store(R.Asset):
    def __init__(self, num, folder, base, prefix, title, display):
        self.num, self.folder, self.display = num, folder, display
        self.prefix, self.title = prefix, title
        self.asset_dir = f'{A17}/{folder}'
        self.basename = base
        self.tex_dir = f'{self.asset_dir}/textures'
        self.src_dir = self.asset_dir
        for sub in ('textures', 'lod', 'renders'):
            os.makedirs(f'{self.asset_dir}/{sub}', exist_ok=True)
        for sub in ('textures',):
            open(f'{self.asset_dir}/{sub}/.gdignore', 'w').close()   # embedded in the .glb already
        R.Ctx.tex_dir = self.tex_dir
        R.reset_scene()
        sc = bpy.context.scene
        self.coll = bpy.data.collections.new(prefix)
        sc.collection.children.link(self.coll)
        self.root = self._empty(f'{prefix}_{title}', self.coll, None, size=3.0)
        self.root['asset_id'] = base
        self.root['display_name'] = display
        self.root['front_axis_blender'] = '-Y'
        self.root['units'] = 'metres'
        self.lod_coll, self.lod_root = {}, {}
        for L in (0, 1, 2):
            c = bpy.data.collections.new(f'{prefix}_LOD{L}')
            self.coll.children.link(c)
            self.lod_coll[L] = c
            e = self._empty(f'{prefix}_LOD{L}', c, self.root)
            b, en = R.LOD_RANGES[L]
            e['lod_level'] = L
            e['visibility_range_begin'] = b
            e['visibility_range_end'] = en
            e['visibility_range_margin'] = R.LOD_MARGIN
            self.lod_root[L] = e
        self.col_coll = bpy.data.collections.new(f'{prefix}_Collision')
        self.coll.children.link(self.col_coll)
        self.col_root = self._empty(f'{prefix}_Collision', self.col_coll, self.root)
        self.light_coll = bpy.data.collections.new(f'{prefix}_NightLights')
        self.coll.children.link(self.light_coll)
        self.light_root = self._empty(f'{prefix}_NightLights', self.light_coll, self.root)
        self.light_root['godot_group'] = 'roadside_store_night_lights'
        self.preview = bpy.data.collections.new('_Preview_NotExported')
        sc.collection.children.link(self.preview)
        self.parts, self.cameras, self.signs = {}, {}, []
        self.dims = {}

    def finalize(self):
        stats = super().finalize()
        self.root['brand_signs'] = json.dumps(self.signs)
        self.root['store_dims'] = json.dumps(self.dims)
        return stats

    def _export(self, path, objs, textures=True):
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objs:
            ob.hide_set(False)
            ob.select_set(True)
        bpy.context.view_layer.objects.active = self.root
        return bpy.ops.export_scene.gltf(
            filepath=path, export_format='GLB', use_selection=True, export_extras=True,
            export_lights=True, export_cameras=False, export_apply=True, export_yup=True,
            export_texcoords=True, export_normals=True, export_tangents=False,
            export_materials='EXPORT', export_image_format='AUTO' if textures else 'NONE',
            export_animations=False, export_import_convert_lighting_mode='SPEC')

    def save_and_export(self):
        blend = f'{self.asset_dir}/{self.basename}.blend'
        glb = f'{self.asset_dir}/{self.basename}.glb'
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        res = self._export(glb, list(self.coll.all_objects))
        lod_res = {}
        for L in (0, 1, 2):
            objs = [self.root, self.lod_root[L], self.col_root] + list(self.lod_coll[L].all_objects) + \
                   [o for o in self.col_coll.all_objects]
            lod_res[L] = self._export(f'{self.asset_dir}/lod/{self.basename}_lod{L}.glb', objs, textures=False)
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        return blend, glb, (res, lod_res)


# ---------------------------------------------------------------------------
# ground / site helpers
# ---------------------------------------------------------------------------
def site_ground(A, L, plot, holes, paved=(), beds=(), paver_h=0.12, mat_paved='RS_Paver'):
    """Asphalt over the plot minus every hole/paved/bed rectangle; skirt; raised paved areas; curb beds."""
    g = A.m(L, 'Ground')
    rects = [plot]
    for h in list(holes) + list(paved) + list(beds):
        rects = rect_subtract(rects, h)
    R.ground_regions(g, rects, 'RS_Asphalt')
    R.pad_skirt(g, *plot)
    for p in paved:
        g.add(bm_box(p[0], p[1], 0.0, p[2], p[3], paver_h, bevel=0.015 if L == 0 else 0, open_bottom=True), mat_paved)
    for b in beds:
        R.curb_bed(g, L, *b)
    return g


def front_beds(plot, gaps, depth=2.0, y_off=0.0):
    """Landscape beds along the road edge of the plot, leaving curb cuts (entrance / exit) at `gaps` (x0,x1)."""
    x0, y0, x1, _ = plot
    xs = [x0]
    out = []
    cur = x0
    for g0, g1 in sorted(gaps):
        if g0 - cur > 1.0:
            out.append((cur, y0 + y_off, g0, y0 + y_off + depth))
        cur = g1
    if x1 - cur > 1.0:
        out.append((cur, y0 + y_off, x1, y0 + y_off + depth))
    return out


def entry_exit(A, L, plot, x_in, x_out, y=None, depth=2.0):
    """Entrance/exit arrows on the apron plus small ENTRANCE / EXIT post signs (LOD0/1)."""
    if L == 2:
        return
    mk = A.m(L, 'Markings')
    y = (plot[1] + depth + 3.0) if y is None else y
    R.arrow_mark(mk, x_in, y, 90, 3.4)       # entering: pointing +Y (into the plot)
    R.arrow_mark(mk, x_out, y, -90, 3.4)     # leaving: pointing -Y (to the road)
    s = A.m(L, 'Signage')
    for x, word, bg, facing in ((x_in + 3.3, 'ENTRANCE', 'RS_PaintCharcoal', '-Y'), (x_out - 3.3, 'EXIT', 'RS_PaintCharcoal', '-Y')):
        yy = plot[1] + 0.5
        s.add(bm_cyl(x, yy, 0, 2.3, 0.04, 8, open_bottom=True), 'RS_MetalGalv')
        panel(s, L, place('-Y', (x, yy, 2.3)), 1.5 if word == 'ENTRANCE' else 1.0, 0.4, 0.04, 'RS_ReflectorYellow', 'RS_MetalGalv')
        txt(s, L, word, place('-Y', (x, yy - 0.04, 2.3)), 0.2, 0.012, 'bold', 'RS_PlasticBlack', min_size_lod2=9)


def parking_row(A, L, x0, y_front, y_back, n, w=2.6, cars=(), wheel_stops=True, line_mat='RS_LineWhite'):
    """Perpendicular bays along X starting at x0 spanning y_front..y_back (sorted). cars: {bay_index: (colour, kind)}."""
    if L < 2:
        mk = A.m(L, 'Markings')
        R.parking_bays(mk, x0, y_front, y_back, n, w, mat=line_mat)
        if wheel_stops and L == 0:
            for i in range(n):
                x = x0 + (i + 0.5) * w
                mk.add(bm_box(x - 0.7, y_back - 0.5, 0, x + 0.7, y_back - 0.32, 0.1, bevel=0.015, open_bottom=True), 'RS_Concrete')
    for i, (colr, kind) in cars.items():
        car(A.m(L, 'Vehicles'), L, x0 + (i + 0.5) * w, (y_front + y_back) / 2 + 0.2, 90, colr, kind)


def disabled_bay(A, L, x, y_front, y_back, w=2.6):
    if L == 2:
        return
    mk = A.m(L, 'Markings')
    for i in range(4):
        xx = x - w / 2 + 0.35 + i * 0.5
        mk.add(bm_quad((xx, y_front, 0.006), (xx + 0.16, y_front, 0.006), (xx + 0.16 + 0.5, y_back, 0.006), (xx + 0.5, y_back, 0.006)),
               'RS_LineWhite')


# ---------------------------------------------------------------------------
# facade components
# ---------------------------------------------------------------------------
def arch_pts(cx, zs, r, seg=12, a0=180.0, a1=0.0):
    """Points of a semicircular arch (x, z) from angle a0 to a1 (degrees), spring line at zs."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / seg)), zs + r * math.sin(math.radians(a0 + (a1 - a0) * i / seg)))
            for i in range(seg + 1)]


def front_wall(b, L, x0, x1, y, t, z0, z1, holes, mat, bevel=0.0, mat_fn=None):
    """Front wall (outer face at y, facing -Y, thickness t toward +Y) with rectangular openings (x0,z0,x1,z1)."""
    rects = [(x0, z0, x1, z1)]
    for h in holes:
        rects = rect_subtract(rects, h)
    for (a, c, d, e) in rects:
        b.add(bm_box(a, y, c, d, y + t, e, bevel=bevel if L == 0 else 0.0, open_bottom=(c <= z0 + 1e-6 and z0 <= 0.2)), mat)


def wall_x(b, L, x, y0, y1, z0, z1, t, mat, side=1, bevel=0.0):
    """Side wall at x (side=+1 -> wall occupies x-t..x, side=-1 -> x..x+t)."""
    xa, xb = (x - t, x) if side > 0 else (x, x + t)
    b.add(bm_box(xa, y0, z0, xb, y1, z1, bevel=bevel if L == 0 else 0.0, open_bottom=z0 <= 0.2), mat)


def shell(b, L, rect, H, wall, t=0.25, holes=(), front_mat=None, floor_h=0.15, floor_mat='RS_Concrete',
          roof_mat='RS_PaintOffWhite', roof_t=0.3, parapet=0.0, parapet_mat=None, bevel=0.025, rooftop=True,
          skip=()):
    """Four walls + floor slab + flat roof slab. Front (-Y) wall has `holes`. skip: subset of {'front','back','left','right','roof'}."""
    x0, y0, x1, y1 = rect
    bv = bevel if L == 0 else 0.0
    b.add(bm_box(x0, y0, 0.0, x1, y1, floor_h, open_bottom=True), floor_mat)
    if 'front' not in skip:
        front_wall(b, L, x0, x1, y0, t, floor_h, H - roof_t, holes, front_mat or wall, bevel=bevel)
    if 'back' not in skip:
        b.add(bm_box(x0, y1 - t, floor_h, x1, y1, H - roof_t, bevel=bv, open_bottom=True), wall)
    if 'left' not in skip:
        b.add(bm_box(x0, y0 + t, floor_h, x0 + t, y1 - t, H - roof_t, open_bottom=True), wall)
    if 'right' not in skip:
        b.add(bm_box(x1 - t, y0 + t, floor_h, x1, y1 - t, H - roof_t, open_bottom=True), wall)
    if 'roof' not in skip:
        b.add(bm_box(x0, y0, H - roof_t, x1, y1, H, bevel=bv), roof_mat)
        if parapet > 0 and L < 2:
            outer = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            inner = [(x0 + 0.2, y0 + 0.2), (x1 - 0.2, y0 + 0.2), (x1 - 0.2, y1 - 0.2), (x0 + 0.2, y1 - 0.2)]
            b.add(bm_ring_prism(outer, inner, H, H + parapet, bottom=False), parapet_mat or wall)
        if rooftop and L < 2:
            n = max(1, int((x1 - x0) / 7))
            for i in range(n):
                cx = x0 + (i + 0.5) * (x1 - x0) / n
                b.add(bm_box(cx - 0.9, y1 - 3.5, H, cx + 0.9, y1 - 2.2, H + 0.9, bevel=bv, open_bottom=True), 'RS_MetalGalv')
                if L == 0:
                    b.add(bm_cyl(cx, y1 - 2.85, H + 0.9, H + 0.97, 0.5, 14), 'RS_MetalDark')


def glazing(A, L, x0, x1, z0, z1, y, nx=4, trans=(), doors=(), frame='RS_MetalDark', glass=None, fd=0.12,
            door_h=2.25, bottom_rail=0.0, frameless=False, glass_z0=None):
    """Glazed storefront in the plane y (facing -Y). doors: list of (xc, width) pairs of doors (double leaf)."""
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    gm = glass or ('RS_Glass' if L < 2 else 'RS_GlassLOD')
    gl.add(bm_vquad(x0, x1, z0, z1, y), gm)
    if L == 2:
        return
    gaps = [(xc - w / 2, xc + w / 2) for xc, w in doors]
    mw = 0.035 if frameless else 0.05
    xs = [x0 + (x1 - x0) * i / nx for i in range(nx + 1)]
    for i, x in enumerate(xs):
        if 0 < i < nx and any(g0 - 0.01 < x < g1 + 0.01 for g0, g1 in gaps):
            continue
        fr.add(bm_box(x - mw, y - fd * 0.6, z0, x + mw, y + fd * 0.4, z1, open_bottom=z0 <= 0.2), frame)
    for z in (z0, z1 - 0.07):
        if z == z0 and bottom_rail <= 0:
            continue
        fr.add(bm_box(x0, y - fd * 0.6, z, x1, y + fd * 0.4, z + (max(bottom_rail, 0.07) if z == z0 else 0.07)), frame)
    fr.add(bm_box(x0, y - fd * 0.6, z1 - 0.07, x1, y + fd * 0.4, z1), frame)
    for tz in trans:
        fr.add(bm_box(x0, y - fd * 0.5, tz - 0.03, x1, y + fd * 0.3, tz + 0.03), frame)
    for xc, w in doors:
        a, c = xc - w / 2, xc + w / 2
        for sx in (a, c):
            fr.add(bm_box(sx - 0.05, y - fd * 0.7, z0, sx + 0.05, y + fd * 0.45, z0 + door_h, open_bottom=True), frame)
        fr.add(bm_box(a - 0.05, y - fd * 0.7, z0 + door_h, c + 0.05, y + fd * 0.45, z0 + door_h + 0.07), frame)
        if L == 0:
            fr.add(bm_box(xc - 0.03, y - fd * 0.7, z0, xc + 0.03, y + fd * 0.45, z0 + door_h, open_bottom=True), frame)
            for sgn in (-1, 1):
                fr.add(bm_cyl_between((xc + sgn * 0.14, y - fd * 0.9, z0 + 0.95), (xc + sgn * 0.14, y - fd * 0.9, z0 + 1.45), 0.014, 6),
                       'RS_MetalBrushed')
                la, lb = (a + 0.05, xc - 0.03) if sgn < 0 else (xc + 0.03, c - 0.05)
                fr.add(bm_box(la, y - fd * 0.65, z0, lb, y + fd * 0.4, z0 + 0.25, open_bottom=True), frame)
        fr.add(bm_box(a, y - 0.05, z0, c, y + 0.1, z0 + 0.03, open_bottom=True), 'RS_MetalBrushed')


def awning(acc, L, x0, x1, y_wall, z_top, drop, proj, mats, strip=0.45, valance=0.25, frame_mat='RS_MetalDark'):
    """Sloped fabric awning projecting toward -Y from the wall at y_wall. mats=(a,b) alternate strips."""
    n = max(1, int(round((x1 - x0) / strip)))
    if L == 2:
        n = max(2, n // 4)
    w = (x1 - x0) / n
    for i in range(n):
        xa, xb = x0 + i * w, x0 + (i + 1) * w
        m = mats[i % len(mats)]
        acc.add(bm_quad((xa, y_wall, z_top), (xb, y_wall, z_top), (xb, y_wall - proj, z_top - drop), (xa, y_wall - proj, z_top - drop)), m)
        acc.add(bm_quad((xa, y_wall, z_top), (xa, y_wall - proj, z_top - drop), (xb, y_wall - proj, z_top - drop), (xb, y_wall, z_top)), m)
        if L < 2 and valance > 0:
            yv = y_wall - proj
            acc.add(bm_quad((xa, yv, z_top - drop - valance), (xb, yv, z_top - drop - valance), (xb, yv, z_top - drop), (xa, yv, z_top - drop)), m)
            acc.add(bm_quad((xa, yv, z_top - drop), (xb, yv, z_top - drop), (xb, yv, z_top - drop - valance), (xa, yv, z_top - drop - valance)), m)
    if L == 0:
        for x in (x0, x1):
            acc.add(bm_cyl_between((x, y_wall, z_top), (x, y_wall - proj, z_top - drop), 0.02, 6), frame_mat)


def pergola(acc, L, x0, y0, x1, y1, z, post=0.14, beam=0.1, n_slats=None, mat='RS_WoodV', post_mat=None, posts=None):
    post_mat = post_mat or mat
    pts = posts or [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    for (px, py) in pts:
        acc.add(bm_box(px - post / 2, py - post / 2, 0, px + post / 2, py + post / 2, z, open_bottom=True), post_mat)
    if L == 2:
        acc.add(bm_box(x0 - 0.1, y0 - 0.1, z, x1 + 0.1, y1 + 0.1, z + 0.12), mat)
        return
    acc.add(bm_box(x0 - 0.15, y0 - 0.05, z, x1 + 0.15, y0 + beam, z + 0.2, bevel=0.01 if L == 0 else 0), mat)
    acc.add(bm_box(x0 - 0.15, y1 - beam, z, x1 + 0.15, y1 + 0.05, z + 0.2, bevel=0.01 if L == 0 else 0), mat)
    ns = n_slats or max(3, int((x1 - x0) / (0.45 if L == 0 else 1.2)))
    for i in range(ns + 1):
        x = x0 + (x1 - x0) * i / ns
        acc.add(bm_box(x - 0.04, y0 - 0.05, z + 0.2, x + 0.04, y1 + 0.05, z + 0.28), mat)


# ---------------------------------------------------------------------------
# furniture & landscape
# ---------------------------------------------------------------------------
def chair(acc, L, x, y, ang, mat='RS_MetalDark', seat_mat=None, h=0.45):
    if L == 2:
        return
    seat_mat = seat_mat or mat
    M = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(ang), 4, 'Z')
    acc.add(bm_box(-0.21, -0.21, h - 0.04, 0.21, 0.21, h, bevel=0.01 if L == 0 else 0), seat_mat, matrix=M)
    acc.add(bm_box(-0.21, 0.18, h, 0.21, 0.22, h + 0.4, bevel=0.01 if L == 0 else 0), seat_mat, matrix=M)
    if L == 0:
        for sx in (-0.18, 0.18):
            for sy in (-0.18, 0.18):
                acc.add(bm_cyl_between((sx, sy, 0), (sx, sy, h - 0.04), 0.012, 5), mat, matrix=M)
    else:
        acc.add(bm_box(-0.2, -0.2, 0, 0.2, 0.2, h - 0.04, open_bottom=True), mat, matrix=M)


def table(acc, L, x, y, r=0.38, h=0.74, mat='RS_MetalDark', top='RS_PaintWhite'):
    seg = {0: 20, 1: 10, 2: 6}[L]
    acc.add(bm_cyl(x, y, h - 0.035, h, r, seg), top)
    acc.add(bm_cyl(x, y, 0, h - 0.035, 0.03, 8 if L == 0 else 5, open_bottom=True), mat)
    if L == 0:
        acc.add(bm_cyl(x, y, 0, 0.02, 0.22, 14), mat)


def umbrella(acc, L, x, y, r=1.45, z=2.45, mat='RS_Fabric', mat2=None):
    seg = {0: 16, 1: 8, 2: 6}[L]
    acc.add(bm_cyl(x, y, 0, z, 0.03, 6, open_bottom=True), 'RS_MetalDark')
    if mat2 and L < 2:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=seg, radius1=r, radius2=0.04, depth=0.45)
        bmesh.ops.translate(bm, vec=(x, y, z + 0.225), verts=bm.verts)
        acc.add(bm, mat, mat_fn=lambda f: mat if int(((math.atan2(f.calc_center_median().y - y, f.calc_center_median().x - x) + math.pi) / (2 * math.pi) * seg)) % 2 == 0 else mat2)
    else:
        acc.add(bm_cyl(x, y, z, z + 0.45, r, seg, r2=0.04, caps=False), mat)


def cafe_set(acc, L, x, y, n_chairs=4, ang=0, table_mat='RS_PaintWhite', chair_mat='RS_MetalDark', seat_mat=None,
             umb=None, umb2=None, r=0.38):
    table(acc, L, x, y, r, top=table_mat)
    d = r + 0.32
    for k in range(n_chairs):
        a = math.radians(ang + 360.0 * k / n_chairs)
        chair(acc, L, x + d * math.cos(a), y + d * math.sin(a), math.degrees(a) + 90 + 180 - 180, chair_mat, seat_mat)
    if umb:
        umbrella(acc, L, x, y, 1.45, 2.45, umb, umb2)


def planter(acc, L, x0, y0, x1, y1, h=0.6, mat='RS_Planter', plant='RS_Foliage', seed=0, bush=True):
    acc.add(bm_box(x0, y0, 0, x1, y1, h, bevel=0.02 if L == 0 else 0, open_bottom=True), mat)
    if L < 2:
        acc.add(bm_box(x0 + 0.05, y0 + 0.05, h - 0.02, x1 - 0.05, y1 - 0.05, h + 0.005), 'RS_Soil')
    if bush and L < 2:
        n = max(1, int(max(x1 - x0, y1 - y0) / 0.9))
        for i in range(n):
            cx = x0 + (x1 - x0) * (i + 0.5) / n if (x1 - x0) >= (y1 - y0) else (x0 + x1) / 2
            cy = y0 + (y1 - y0) * (i + 0.5) / n if (y1 - y0) > (x1 - x0) else (y0 + y1) / 2
            R.shrub(acc, L, cx, cy, 0.62, seed=seed + i, mat=plant, z=h - 0.1)
    elif bush and L == 2:
        acc.add(bm_box(x0 + 0.1, y0 + 0.1, h, x1 - 0.1, y1 - 0.1, h + 0.4, open_bottom=True), plant)


def topiary(acc, L, x, y, h=1.5, r=0.4, pot='RS_Terracotta', plant='RS_Foliage'):
    acc.add(bm_cyl(x, y, 0, 0.45, 0.28, 12 if L == 0 else 6, r2=0.22, open_bottom=True), pot)
    if L < 2:
        acc.add(bm_cyl(x, y, 0.45, h - r, 0.03, 5), 'RS_PalmTrunk')
    acc.add(bm_sphere((x, y, h), r, 2 if L == 0 else 1, jitter=0.03), plant)


def bench(acc, L, x, y, length=1.8, ang=0, mat='RS_WoodV'):
    if L == 2:
        return
    M = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(math.radians(ang), 4, 'Z')
    acc.add(bm_box(-length / 2, -0.22, 0.42, length / 2, 0.22, 0.47), mat, matrix=M)
    acc.add(bm_box(-length / 2, 0.2, 0.47, length / 2, 0.24, 0.9), mat, matrix=M)
    for sx in (-length / 2 + 0.15, length / 2 - 0.15):
        acc.add(bm_box(sx - 0.03, -0.2, 0, sx + 0.03, 0.22, 0.42, open_bottom=True), 'RS_MetalDark', matrix=M)


def bin_(acc, L, x, y, mat='RS_MetalDark'):
    acc.add(bm_cyl(x, y, 0, 0.9, 0.25, 12 if L == 0 else 6, open_bottom=True), mat)
    if L == 0:
        acc.add(bm_cyl(x, y, 0.9, 0.95, 0.27, 12), 'RS_MetalBrushed')


def palms(A, L, spots, seed=70):
    land = A.m(L, 'Landscape')
    rng = random.Random(seed)
    for i, (x, y) in enumerate(spots):
        R.palm(land, L, x, y, rng.uniform(6.2, 7.6), seed=seed + i)


def hedge_row(A, L, xs, y, mat='RS_Foliage', s=0.8, seed=0):
    land = A.m(L, 'Landscape')
    for i, x in enumerate(xs):
        R.shrub(land, L, x, y, s, seed=seed + i, mat=mat if i % 2 == 0 else 'RS_Foliage2')


# ---------------------------------------------------------------------------
# cars
# ---------------------------------------------------------------------------
CAR_PROFILES = {
    'sedan': dict(length=4.65, width=1.82, lower=[(-2.32, 0.32), (2.32, 0.32), (2.32, 0.72), (1.75, 0.84), (-1.95, 0.86), (-2.32, 0.74)],
                  cabin=[(-1.15, 0.86), (-0.65, 1.42), (0.85, 1.42), (1.45, 0.86)], wheel_r=0.33, wheel_x=1.4),
    'suv': dict(length=4.85, width=1.95, lower=[(-2.42, 0.38), (2.42, 0.38), (2.42, 0.95), (1.9, 1.05), (-2.1, 1.07), (-2.42, 0.98)],
                cabin=[(-2.05, 1.07), (-1.95, 1.78), (0.7, 1.78), (1.5, 1.07)], wheel_r=0.38, wheel_x=1.5),
    'hatch': dict(length=4.0, width=1.74, lower=[(-2.0, 0.3), (2.0, 0.3), (2.0, 0.68), (1.5, 0.8), (-1.7, 0.82), (-2.0, 0.7)],
                  cabin=[(-1.8, 0.82), (-1.45, 1.42), (0.55, 1.42), (1.2, 0.82)], wheel_r=0.3, wheel_x=1.2),
    'van': dict(length=5.2, width=2.0, lower=[(-2.6, 0.4), (2.6, 0.4), (2.6, 1.0), (2.1, 1.1), (-2.5, 1.12), (-2.6, 1.05)],
                cabin=[(-2.5, 1.12), (-2.5, 2.2), (1.0, 2.2), (1.9, 1.12)], wheel_r=0.38, wheel_x=1.7),
}


def car(acc, L, x, y, ang_deg, colour='RS_CarSilver', kind='sedan', z=0.0):
    """Simple parked car, nose toward local +X rotated by ang_deg about Z (90 = nose toward +Y)."""
    p = CAR_PROFILES[kind]
    cm = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(ang_deg), 4, 'Z')
    # profile (x=length, y=height) extruded across the width -> world (X=length, Y=width, Z=height)
    prof = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    W = p['width']
    for pts, mat in ((p['lower'], colour), (p['cabin'], colour)):
        bm = bm_prism(pts, 0.0, W)
        bmesh.ops.translate(bm, vec=(0, 0, -W / 2), verts=bm.verts)
        acc.add(bm, mat, matrix=cm @ prof)
    if L == 2:
        return
    # windows (dark glass quads slightly proud of the cabin sides / windscreen)
    c = p['cabin']
    for sgn in (-1, 1):
        yy = sgn * (W / 2 * 0.985)
        acc.add(bm_quad((c[0][0] + 0.2, yy, c[0][1] + 0.05), (c[3][0] - 0.2, yy, c[3][1] + 0.05), (c[2][0] - 0.12, yy, c[2][1] - 0.08),
                        (c[1][0] + 0.12, yy, c[1][1] - 0.08)) if sgn > 0 else
                bm_quad((c[3][0] - 0.2, yy, c[3][1] + 0.05), (c[0][0] + 0.2, yy, c[0][1] + 0.05), (c[1][0] + 0.12, yy, c[1][1] - 0.08),
                        (c[2][0] - 0.12, yy, c[2][1] - 0.08)), 'RS_CarGlass', matrix=cm)
    hw = W / 2 * 0.86
    acc.add(bm_quad((c[3][0] + 0.005, -hw, c[3][1] + 0.03), (c[3][0] + 0.005, hw, c[3][1] + 0.03),
                    (c[2][0] + 0.01, hw * 0.95, c[2][1] - 0.05), (c[2][0] + 0.01, -hw * 0.95, c[2][1] - 0.05)), 'RS_CarGlass', matrix=cm)
    acc.add(bm_quad((c[0][0] - 0.005, hw, c[0][1] + 0.03), (c[0][0] - 0.005, -hw, c[0][1] + 0.03),
                    (c[1][0] - 0.01, -hw * 0.95, c[1][1] - 0.05), (c[1][0] - 0.01, hw * 0.95, c[1][1] - 0.05)), 'RS_CarGlass', matrix=cm)
    seg = 14 if L == 0 else 7
    r, wx = p['wheel_r'], p['wheel_x']
    for sx in (-wx, wx):
        for sy in (-1, 1):
            bm = bm_cyl(0, 0, -0.1, 0.1, r, seg)
            bm.verts.ensure_lookup_table()
            M = cm @ Matrix.Translation((sx, sy * (W / 2 - 0.12), r)) @ Matrix.Rotation(math.radians(90), 4, 'X')
            acc.add(bm, 'RS_Rubber', matrix=M)
    if L == 0:
        L0 = p['length'] / 2
        acc.add(bm_box(L0 - 0.01, -W / 2 + 0.15, 0.62, L0 + 0.03, -W / 2 + 0.55, 0.75), 'RS_PaintWhite', matrix=cm)
        acc.add(bm_box(L0 - 0.01, W / 2 - 0.55, 0.62, L0 + 0.03, W / 2 - 0.15, 0.75), 'RS_PaintWhite', matrix=cm)
        acc.add(bm_box(-L0 - 0.03, -W / 2 + 0.1, 0.66, -L0 + 0.01, -W / 2 + 0.5, 0.78), 'RS_Tail', matrix=cm)
        acc.add(bm_box(-L0 - 0.03, W / 2 - 0.5, 0.66, -L0 + 0.01, W / 2 - 0.1, 0.78), 'RS_Tail', matrix=cm)


# ---------------------------------------------------------------------------
# drive-through
# ---------------------------------------------------------------------------
def menu_board(A, L, x, y, face='-Y', screen='RS_ScreenDark', body='RS_PaintCharcoal', w=1.2, h=2.2, trim='RS_MetalDark'):
    """Drive-through order board; `face` is the direction the screen faces (-Y, +Y, +X, -X)."""
    s = A.m(L, 'DriveThru')
    ax = face in ('+X', '-X')
    dx, dy = (0.12, w / 2) if ax else (w / 2, 0.12)
    s.add(bm_box(x - dx, y - dy, 0, x + dx, y + dy, h, bevel=0.015 if L == 0 else 0, open_bottom=True), body)
    if L < 2:
        off = {'-Y': (0, -dy), '+Y': (0, dy), '+X': (dx, 0), '-X': (-dx, 0)}[face]
        s.add(bm_box(-w / 2 + 0.08, -0.6, 0.0, w / 2 - 0.08, 0.6, 0.02), screen, matrix=place(face, (x + off[0], y + off[1], 0.9)),
              mat_fn=front_back(screen, trim))
        s.add(bm_box(-0.2, -0.12, 0.0, 0.2, 0.12, 0.05), 'RS_PlasticBlack', matrix=place(face, (x + off[0], y + off[1], 1.95)))


def height_bar(acc, L, x, y, span, h=2.3, mat='RS_ReflectorYellow'):
    if L == 2:
        return
    for sx in (x - span / 2, x + span / 2):
        acc.add(bm_cyl(sx, y, 0, h, 0.07, 10 if L == 0 else 5, open_bottom=True), 'RS_MetalDark')
    acc.add(bm_cyl_between((x - span / 2, y, h), (x + span / 2, y, h), 0.06, 8 if L == 0 else 4), mat)


# ---------------------------------------------------------------------------
# interiors
# ---------------------------------------------------------------------------
def interior_shell(A, L, rect, zc, floor_mat='RS_TileFloor', wall_mat='RS_InteriorWall', ceil_mat='RS_PaintWhite',
                   floor_h=0.15, lights=None, light_mat='RS_LightPanel', back_mat=None):
    """Floor, ceiling and three inside wall planes (front is the glazing). lights: list of (x0,y0,x1,y1)."""
    if L == 2:
        return A.m(L, 'Interior')
    it = A.m(L, 'Interior')
    ix0, iy0, ix1, iy1 = rect
    it.add(bm_hquad(ix0, iy0, ix1, iy1, floor_h + 0.005), floor_mat)
    it.add(bm_hquad(ix0, iy0, ix1, iy1, zc, down=True), ceil_mat)
    it.add(bm_vquad(ix0, ix1, floor_h, zc, iy1 - 0.001), back_mat or wall_mat)
    it.add(bm_quad((ix0 + 0.001, iy1, floor_h), (ix0 + 0.001, iy0, floor_h), (ix0 + 0.001, iy0, zc), (ix0 + 0.001, iy1, zc)), wall_mat)
    it.add(bm_quad((ix1 - 0.001, iy0, floor_h), (ix1 - 0.001, iy1, floor_h), (ix1 - 0.001, iy1, zc), (ix1 - 0.001, iy0, zc)), wall_mat)
    for (a, b_, c, d) in (lights or []):
        it.add(bm_hquad(a, b_, c, d, zc - 0.012, down=True), light_mat)
    return it


def light_grid(rect, nx, ny, size=(1.2, 0.3), margin=1.0):
    x0, y0, x1, y1 = rect
    out = []
    for i in range(nx):
        for j in range(ny):
            cx = x0 + margin + (x1 - x0 - 2 * margin) * (i + 0.5) / nx
            cy = y0 + margin + (y1 - y0 - 2 * margin) * (j + 0.5) / ny
            out.append((cx - size[0] / 2, cy - size[1] / 2, cx + size[0] / 2, cy + size[1] / 2))
    return out


def counter(acc, L, x0, y0, x1, y1, h=1.05, body='RS_PaintCharcoal', top='RS_PaintWhite', front=None, floor=0.15):
    bv = 0.02 if L == 0 else 0.0
    acc.add(bm_box(x0, y0, floor, x1, y1, floor + h - 0.05, bevel=bv, open_bottom=True), body)
    acc.add(bm_box(x0 - 0.04, y0 - 0.04, floor + h - 0.05, x1 + 0.04, y1 + 0.04, floor + h, bevel=bv), top)


def stool(acc, L, x, y, h=0.65, mat='RS_MetalDark', seat='RS_Cushion'):
    if L == 2:
        return
    acc.add(bm_cyl(x, y, 0.15, 0.15 + h - 0.05, 0.025, 5), mat)
    acc.add(bm_cyl(x, y, 0.15 + h - 0.05, 0.15 + h, 0.17, 12 if L == 0 else 6), seat)


# ---------------------------------------------------------------------------
# cameras & finishing
# ---------------------------------------------------------------------------
def std_cameras(A, plot, bx0, by0, bx1, by1, H, road_dx=-44.0, sign_z=None, day_dist=None, lens=30, detail_target=None,
                detail_off=(-1.0, -9.5, 1.7), day_side=-1, cx=None):
    """Standard presentation: 3/4 hero (day & night), driver-height road view, facade/entrance detail."""
    W = bx1 - bx0
    cx = (bx0 + bx1) / 2 if cx is None else cx
    tz = min(H, 6.0) * 0.5
    dist = day_dist or max(W * 1.35, 30.0)
    tgt = (cx, by0 + 1.5, tz)
    A.camera('day', (cx + day_side * dist * 0.55, by0 - dist * 0.88, 4.6), tgt, lens)
    sz = sign_z if sign_z is not None else min(H, 5.0)
    A.camera('road', (cx + road_dx, plot[1] - 8.6, 1.25), (cx, by0, sz * 0.7), 35)
    dt = detail_target or (cx, by0, min(H, 6.0) * 0.45)
    A.camera('detail', (dt[0] + detail_off[0], by0 + detail_off[1], detail_off[2]), dt, 36)


def finish(A, plot, report=True):
    R.build_preview_env(A, plot)
    stats = A.finalize()
    blend, glb, res = A.save_and_export()
    tot = {L: sum(v.values()) for L, v in stats.items()}
    print('STATS', json.dumps(tot))
    print('EXPORT', res[0], blend, glb, res[1])
    with open(f'{A.asset_dir}/lod/build_stats.json', 'w') as f:
        json.dump(dict(blender_loop_triangles=tot, parts={str(k): v for k, v in stats.items()}), f, indent=1)
    return stats


# ---------------------------------------------------------------------------
# small shared builders: lamp posts (+collision +night lights), generic night lights
# ---------------------------------------------------------------------------
def lamp_set(A, L, spots, h=8.5, arm=1.3):
    lp = A.m(L, 'LampPosts')
    for (x, y, fx, fy) in spots:
        R.lamp_post(lp, L, x, y, h, facing=(fx, fy), arm=arm)


def lamp_collision(A, spots, h=8.5):
    for i, (x, y, fx, fy) in enumerate(spots):
        A.col_box(f'LampPost{i}', x - 0.25, y - 0.25, 0.0, x + 0.25, y + 0.25, h)


def lamp_lights(A, spots, h=8.4, arm=1.3, energy=2600):
    for i, (x, y, fx, fy) in enumerate(spots):
        A.light(f'LampPost{i}', 'SPOT', (x + fx * arm, y + fy * arm, h), energy, '#fff2df', spot_deg=125, blend=0.6, radius=0.3)


def glow_lights(A, name, pts, kind='POINT', energy=800, color='#fff3e4', radius=0.5, **kw):
    for i, p in enumerate(pts):
        A.light(f'{name}{i}', kind, p, energy, color, radius=radius, **kw)


def sign_light(A, name, loc, energy=2200, color='#ffffff'):
    """Soft point light placed in front of a lit sign so it spills onto the facade / ground."""
    A.light(name, 'POINT', loc, energy, color, radius=0.6)


# ---------------------------------------------------------------------------
# arched openings (PAUL, Operation Falafel, ...)
# ---------------------------------------------------------------------------
def arch_poly(xc, w, zb, zs, seg=10, grow=0.0):
    """Outline (x, z) of a window: flat bottom at zb, straight sides up to the spring line zs, semicircular top."""
    r = w / 2 + grow
    pts = [(xc - r, zb - grow), (xc + r, zb - grow)]
    pts += [(xc + r * math.cos(math.radians(a)), zs + r * math.sin(math.radians(a))) for a in [180.0 * i / seg for i in range(seg + 1)]]
    return pts


def arch_wall(b, L, x0, x1, y, t, z0, z1, openings, mat, seg=10, bevel=0.0):
    """Front wall (outer face at y, thickness t toward +Y) with arched openings. openings: (xc, w, zb, zs)."""
    seg = {0: seg, 1: max(4, seg // 2), 2: 3}[L]
    rects = [(x0, z0, x1, z1)]
    for xc, w, zb, zs in openings:
        rects = rect_subtract(rects, (xc - w / 2, zb, xc + w / 2, zs + w / 2))
    for (a, c, d, e) in rects:
        b.add(bm_box(a, y, c, d, y + t, e, bevel=bevel if L == 0 else 0.0, open_bottom=c <= z0 + 1e-6 and z0 <= 0.2), mat)
    M = place('-Y', (0.0, y + t, 0.0))
    for xc, w, zb, zs in openings:
        r = w / 2
        for sgn in (-1, 1):
            side_x = xc + sgn * r
            pts = [(side_x, zs)] + [(xc + sgn * r * math.cos(math.radians(a)), zs + r * math.sin(math.radians(a))) for a in [90.0 * i / seg for i in range(1, seg + 1)]]
            pts += [(side_x, zs + r)]
            b.add(bm_prism_local(pts, t), mat, matrix=M)


def arch_window(A, L, xc, w, zb, zs, y, frame='RS_MetalDark', f=0.07, mullions=1, glass=None, seg=10, depth=0.1, transom=None):
    """Arched glazing + frame ring + vertical mullions + optional transom height."""
    seg = {0: seg, 1: max(4, seg // 2), 2: 3}[L]
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    gm = glass or ('RS_Glass' if L < 2 else 'RS_GlassLOD')
    M = place('-Y', (0.0, y, 0.0))
    gl.add(bm_poly_flat(arch_poly(xc, w, zb, zs, seg), 0.0), gm, matrix=M)
    if L == 2:
        return
    inner = arch_poly(xc, w, zb, zs, seg)
    outer = arch_poly(xc, w, zb, zs, seg, grow=f)
    fr.add(bm_ring_prism(outer, inner, -depth * 0.6, depth * 0.4, top=True, bottom=True), frame, matrix=M)
    for i in range(1, mullions + 1):
        x = xc - w / 2 + w * i / (mullions + 1)
        fr.add(bm_box(x - 0.025, y - 0.05, zb, x + 0.025, y + 0.05, zs + math.sqrt(max(0.0, (w / 2) ** 2 - (x - xc) ** 2))), frame)
    if transom:
        fr.add(bm_box(xc - w / 2, y - 0.05, transom - 0.025, xc + w / 2, y + 0.05, transom + 0.025), frame)


# ---------------------------------------------------------------------------
# torus / donut
# ---------------------------------------------------------------------------
def bm_torus(c, Rr, r, seg=24, rings=10, minor=(0.0, 2 * math.pi), axis='Z'):
    """Torus about local Z (hole axis); `minor` limits the tube angle (0..pi = the +Z half). axis 'Y' makes the hole axis point to -Y."""
    bm = bmesh.new()
    full = abs((minor[1] - minor[0]) - 2 * math.pi) < 1e-6
    nr = rings if full else rings + 1
    grid = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(nr):
            b = minor[0] + (minor[1] - minor[0]) * j / rings
            row.append(bm.verts.new(((Rr + r * math.cos(b)) * math.cos(a), (Rr + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        grid.append(row)
    for i in range(seg):
        i2 = (i + 1) % seg
        for j in range(rings):
            j2 = (j + 1) % nr
            bm.faces.new((grid[i][j], grid[i2][j], grid[i2][j2], grid[i][j2]))
    m = Matrix.Identity(4)
    if axis == 'Y':
        m = Matrix.Rotation(math.radians(90), 4, 'X')
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ m, verts=bm.verts)
    return bm


def donut(acc, L, c, Rr=0.5, r=0.2, axis='Z', icing='RS_Pink', dough='RS_Pastry', sprinkles=False):
    seg = {0: 20, 1: 12, 2: 8}[L]
    rings = {0: 8, 1: 6, 2: 4}[L]
    acc.add(bm_torus(c, Rr, r, seg, rings, axis=axis), dough)
    if L < 2:
        acc.add(bm_torus(c, Rr, r * 1.08, seg, rings // 2 + 1, (0.0, math.pi), axis=axis), icing)
