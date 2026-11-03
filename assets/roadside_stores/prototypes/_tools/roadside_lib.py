"""Shared Blender (bpy 4.5 LTS) build library for the Dubai roadside store prototypes.

Conventions (shared by every roadside store asset):
  * 1 Blender unit = 1 metre, Z up.
  * The asset origin is the centre of the plot at finished ground level (z = 0).
  * The road / customer-facing front of the plot faces Blender -Y.
    After glTF export (+Y up) that becomes +Z, which is Godot's MODEL_FRONT.
  * Hierarchy (all names are prefixed with the asset prefix, e.g. ENOC_):
        <PREFIX>_<Name>               root empty
          <PREFIX>_LOD0 / _LOD1 / _LOD2  LOD empties (glTF extras carry lod_level +
                                        visibility ranges for the Godot post-import script)
            <PREFIX>_LODn_<Part>         merged meshes, one per logical part
          <PREFIX>_Collision           simple boxes named *-convcolonly (Godot import hint)
          <PREFIX>_NightLights         optional punctual lights (KHR_lights_punctual)
  * Materials are shared by name across all stores (RS_* = generic, ENOC_/SBX_/ZOOM_ = brand).
  * Textures are generated procedurally (numpy) into <asset>/source/textures and
    embedded into the .glb on export.
"""
import bpy, bmesh, math, os, random, json
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
FONT_SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
FONT_DISPLAY_BOLD = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
FONT_ARABIC = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

LOD_RANGES = {0: (0.0, 60.0), 1: (60.0, 170.0), 2: (170.0, 900.0)}
LOD_MARGIN = 6.0


def arabic(text):
    """Return Arabic text shaped into presentation forms in visual (LTR) order."""
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(text))


# ---------------------------------------------------------------------------
# colour helpers
# ---------------------------------------------------------------------------
def hex_srgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_lin(h):
    return tuple(s2l(c) for c in hex_srgb(h)) + (1.0,)


# ---------------------------------------------------------------------------
# procedural, tileable texture generation
# ---------------------------------------------------------------------------
def _fft_noise(n, beta, seed, aniso=(1.0, 1.0)):
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((n, n))
    f = np.fft.fftfreq(n)
    fx, fy = np.meshgrid(f, f)
    r = np.sqrt((fx * aniso[0]) ** 2 + (fy * aniso[1]) ** 2)
    r[0, 0] = 1.0
    F = np.fft.fft2(w) / (r ** beta)
    F[0, 0] = 0
    out = np.real(np.fft.ifft2(F))
    return (out - out.mean()) / (out.std() + 1e-9)


def _normal_from_height(h, strength):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5
    nx, ny = -dx * strength, dy * strength          # OpenGL (+Y) convention, glTF/Blender/Godot
    l = np.sqrt(nx * nx + ny * ny + 1.0)
    return np.stack([nx / l, ny / l, 1.0 / l], -1) * 0.5 + 0.5


def _save(arr, path):
    """Material maps are stored as high-quality 4:4:4 JPEG (glTF-native, keeps .glb small)."""
    a = np.clip(arr, 0, 1)
    img = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    path = path.replace('.png', '.jpg')
    img.save(path, quality=92, subsampling=0)


def _orm(rough, metal=None):
    n = rough.shape[0]
    metal = np.zeros_like(rough) if metal is None else metal
    return np.stack([np.ones_like(rough), rough, metal], -1)


def _voronoi(n, grid, seed):
    """Periodic jittered-grid voronoi. Returns F1, F2 distances (in cell units) and cell id."""
    rng = np.random.default_rng(seed)
    pts = rng.random((grid, grid, 2))
    ys, xs = np.mgrid[0:n, 0:n] / n * grid
    cx, cy = np.floor(xs).astype(int), np.floor(ys).astype(int)
    f1 = np.full((n, n), 9.0); f2 = np.full((n, n), 9.0); cid = np.zeros((n, n), int)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            gx, gy = cx + ox, cy + oy
            p = pts[gy % grid, gx % grid]
            d = np.sqrt((gx + p[..., 0] - xs) ** 2 + (gy + p[..., 1] - ys) ** 2)
            ids = (gy % grid) * grid + (gx % grid)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, ids, cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def tex_asphalt(d, n=1024):
    big = _fft_noise(n, 1.6, 11); mid = _fft_noise(n, 0.9, 12); fine = _fft_noise(n, 0.15, 13)
    rng = np.random.default_rng(14)
    speck = rng.random((n, n))
    v = 0.205 + 0.018 * big + 0.012 * mid + 0.010 * fine
    v = np.where(speck > 0.988, v + 0.12 * rng.random((n, n)), v)
    v = np.where(speck < 0.010, v - 0.05, v)
    col = np.stack([v * 1.0, v * 0.99, v * 0.965], -1)
    h = 0.6 * fine + 0.4 * mid + np.where(speck > 0.988, 1.5, 0.0)
    rough = np.clip(0.86 + 0.05 * mid - 0.05 * np.clip(big, 0, 2) * 0.5, 0.7, 0.97)
    _save(col, f'{d}/asphalt_albedo.png'); _save(_orm(rough), f'{d}/asphalt_orm.png')
    _save(_normal_from_height(h, 0.9), f'{d}/asphalt_normal.png')


def tex_paver(d, n=1024):
    # 200 x 100 mm concrete pavers, running bond. Texture covers 2.4 m.
    ys, xs = np.mgrid[0:n, 0:n] / n
    rows = ys * 24.0
    r = np.floor(rows).astype(int)
    cols = xs * 12.0 + 0.5 * (r % 2)
    c = np.floor(cols).astype(int) % 12
    fu, fv = cols - np.floor(cols), rows - np.floor(rows)
    edge = np.minimum(np.minimum(fu, 1 - fu) * 0.2, np.minimum(fv, 1 - fv) * 0.1)  # metres to edge
    rng = np.random.default_rng(21)
    tone = rng.normal(0, 1, (24, 12))[r % 24, c]
    noise = _fft_noise(n, 0.8, 22); fine = _fft_noise(n, 0.2, 23)
    joint = np.clip((edge - 0.002) / 0.004, 0, 1)
    base = 0.60 + 0.035 * tone + 0.02 * noise + 0.012 * fine
    base = base * (0.55 + 0.45 * joint)
    col = np.stack([base * 1.0, base * 0.975, base * 0.93], -1)
    h = joint * 1.0 + 0.04 * fine
    rough = np.clip(0.82 - 0.04 * tone * 0.3 + 0.03 * fine + (1 - joint) * 0.1, 0.6, 0.95)
    _save(col, f'{d}/paver_albedo.png'); _save(_orm(rough), f'{d}/paver_orm.png')
    _save(_normal_from_height(h * 3.0, 1.2), f'{d}/paver_normal.png')


def tex_concrete(d, n=1024):
    big = _fft_noise(n, 1.7, 31); mid = _fft_noise(n, 1.0, 32); fine = _fft_noise(n, 0.2, 33)
    rng = np.random.default_rng(34)
    pores = rng.random((n, n)) > 0.996
    v = 0.66 + 0.025 * big + 0.015 * mid + 0.012 * fine - pores * 0.12
    col = np.stack([v, v * 0.99, v * 0.965], -1)
    h = 0.3 * mid + 0.2 * fine - pores * 2.0
    rough = np.clip(0.78 + 0.04 * mid, 0.65, 0.9)
    _save(col, f'{d}/concrete_albedo.png'); _save(_orm(rough), f'{d}/concrete_orm.png')
    _save(_normal_from_height(h, 0.6), f'{d}/concrete_normal.png')


def tex_travertine(d, n=1024):
    # cut travertine cladding, 1.2 x 0.6 m stack-bond panels, texture covers 2.4 m
    streak = _fft_noise(n, 1.3, 41, aniso=(0.12, 1.0))
    streak2 = _fft_noise(n, 0.9, 42, aniso=(0.2, 1.0))
    fine = _fft_noise(n, 0.2, 43)
    rng = np.random.default_rng(44)
    pits = (_fft_noise(n, 0.4, 45, aniso=(0.3, 1.0)) > 2.6)
    ys, xs = np.mgrid[0:n, 0:n] / n
    pu, pv = (xs * 2.0) % 1.0, (ys * 4.0) % 1.0
    pid = (np.floor(xs * 2).astype(int) + 2 * np.floor(ys * 4).astype(int))
    ptone = rng.normal(0, 1, 8)[pid]
    edge = np.minimum(np.minimum(pu, 1 - pu) * 1.2, np.minimum(pv, 1 - pv) * 0.6)
    joint = np.clip((edge - 0.0015) / 0.002, 0, 1)
    t = 0.5 + 0.5 * np.tanh(streak * 0.9)
    r = 0.80 + 0.04 * streak2 + 0.015 * ptone - 0.05 * t
    g = 0.745 + 0.04 * streak2 + 0.012 * ptone - 0.06 * t
    b = 0.645 + 0.035 * streak2 + 0.01 * ptone - 0.07 * t
    col = np.stack([r, g, b], -1) + 0.008 * fine[..., None]
    col = col * (1 - 0.25 * pits[..., None]) * (0.6 + 0.4 * joint[..., None])
    h = 0.15 * streak2 + 0.05 * fine - pits * 1.0 + joint * 1.0
    rough = np.clip(0.58 + 0.06 * streak2 + pits * 0.2, 0.45, 0.85)
    _save(col, f'{d}/travertine_albedo.png'); _save(_orm(rough), f'{d}/travertine_orm.png')
    _save(_normal_from_height(h * 2.0, 1.0), f'{d}/travertine_normal.png')


def tex_gravel(d, n=512):
    f1, f2, cid = _voronoi(n, 14, 51)
    rng = np.random.default_rng(52)
    tones = rng.choice([0.86, 0.78, 0.70, 0.62, 0.9], size=14 * 14)[cid]
    warm = rng.normal(0, 0.03, 14 * 14)[cid]
    edge = np.clip((f2 - f1) * 3.0, 0, 1)
    v = tones * (0.45 + 0.55 * edge)
    col = np.stack([v + warm, v * 0.96 + warm, v * 0.88], -1)
    h = np.sqrt(edge)
    rough = 0.7 + 0.2 * (1 - edge)
    _save(col, f'{d}/gravel_albedo.png'); _save(_orm(rough), f'{d}/gravel_orm.png')
    _save(_normal_from_height(h * 6.0, 1.0), f'{d}/gravel_normal.png')


def tex_wood(d, n=512):
    # horizontal slats 100 mm with 10 mm gaps, texture covers 1 m
    ys, xs = np.mgrid[0:n, 0:n] / n
    warp = _fft_noise(n, 1.2, 61, aniso=(0.1, 1.0))
    grain = np.sin((ys * 220 + warp * 3.0) * 1.0) * 0.5 + 0.5
    slat = (ys * 10.0) % 1.0
    sid = np.floor(ys * 10).astype(int)
    tone = np.random.default_rng(62).normal(0, 1, 10)[sid % 10]
    gap = np.clip((np.minimum(slat, 1 - slat) - 0.05) / 0.02, 0, 1)
    v = (0.56 + 0.04 * tone + 0.06 * grain) * (0.3 + 0.7 * gap)
    col = np.stack([v * 1.0, v * 0.74, v * 0.52], -1)
    h = gap * 1.0 + 0.05 * grain
    rough = 0.55 + 0.1 * grain
    _save(col, f'{d}/wood_albedo.png'); _save(_orm(rough), f'{d}/wood_orm.png')
    _save(_normal_from_height(h * 3.0, 1.0), f'{d}/wood_normal.png')


def tex_products(d, n=512):
    """8x8 atlas of retail packaging faces used for shelf product silhouettes."""
    img = Image.new('RGB', (n, n)); dr = ImageDraw.Draw(img)
    rng = random.Random(71)
    palette = ['#d62828', '#f77f00', '#fcbf49', '#2a9d8f', '#264653', '#e9c46a', '#8ecae6', '#219ebc',
               '#023047', '#ffb703', '#fb8500', '#6a4c93', '#1982c4', '#8ac926', '#ff595e', '#ffffff',
               '#c1121f', '#003049', '#f4a261', '#90be6d']
    cs = n // 8
    for j in range(8):
        for i in range(8):
            x0, y0 = i * cs, j * cs
            bg = rng.choice(palette)
            dr.rectangle([x0, y0, x0 + cs - 1, y0 + cs - 1], fill=bg)
            band = rng.choice(palette)
            by = y0 + int(cs * rng.uniform(0.3, 0.55))
            dr.rectangle([x0, by, x0 + cs - 1, by + int(cs * rng.uniform(0.15, 0.3))], fill=band)
            if rng.random() < 0.6:
                r = int(cs * 0.18)
                cx, cy = x0 + cs // 2, y0 + int(cs * 0.25)
                dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rng.choice(palette))
            dr.rectangle([x0, y0, x0 + cs - 1, y0 + cs - 1], outline='#202020')
    img.save(f'{d}/products_albedo.png', optimize=True)


TEXTURE_GENERATORS = {
    'asphalt': tex_asphalt, 'paver': tex_paver, 'concrete': tex_concrete,
    'travertine': tex_travertine, 'gravel': tex_gravel, 'wood': tex_wood, 'products': tex_products,
}
EXTRA_TEXTURES = {}   # brand textures registered by asset scripts: key -> fn(dir)


def ensure_texture(key, tex_dir):
    os.makedirs(tex_dir, exist_ok=True)
    gen = TEXTURE_GENERATORS.get(key) or EXTRA_TEXTURES[key]
    def find(ch):
        for ext in ('.jpg', '.png'):
            p = f'{tex_dir}/{key}_{ch}{ext}'
            if os.path.exists(p):
                return p
    if not find('albedo'):
        gen(tex_dir)
    out = {}
    for ch in ('albedo', 'orm', 'normal'):
        p = find(ch)
        if p:
            out[ch] = p
    return out


# ---------------------------------------------------------------------------
# materials
# ---------------------------------------------------------------------------
# keys: base (hex sRGB), rough, metal, tex, emit (hex), es (emission strength),
#       emit_tex (bool: albedo texture also drives emission), alpha, double, spec
MATERIAL_DEFS = {
    # generic, textured
    'RS_Asphalt': dict(base='#ffffff', tex='asphalt', tile=4.0),
    'RS_Paver': dict(base='#ffffff', tex='paver', tile=2.4),
    'RS_Concrete': dict(base='#ffffff', tex='concrete', tile=3.0),
    'RS_Travertine': dict(base='#ffffff', tex='travertine', tile=2.4),
    'RS_Gravel': dict(base='#ffffff', tex='gravel', tile=1.0),
    'RS_Wood': dict(base='#ffffff', tex='wood', tile=1.0),
    'RS_Products': dict(base='#ffffff', tex='products', rough=0.42),
    # generic, flat PBR
    'RS_PaintWhite': dict(base='#ecebe7', rough=0.35),
    'RS_PaintOffWhite': dict(base='#d8d4cc', rough=0.5),
    'RS_PaintCharcoal': dict(base='#2c2f33', rough=0.4, metal=0.2),
    'RS_MetalBrushed': dict(base='#c8cbce', rough=0.28, metal=1.0),
    'RS_MetalDark': dict(base='#3a3d41', rough=0.38, metal=0.85),
    'RS_MetalGalv': dict(base='#9a9ea2', rough=0.45, metal=1.0),
    'RS_Glass': dict(base='#22313a', rough=0.03, alpha=0.30, double=True, spec=0.6),
    'RS_GlassLOD': dict(base='#1f2a30', rough=0.08, metal=0.3, emit='#ffcf9a', es=0.35),
    'RS_Rubber': dict(base='#1a1a1a', rough=0.85),
    'RS_PlasticBlack': dict(base='#151617', rough=0.42),
    'RS_LineWhite': dict(base='#e6e6df', rough=0.7),
    'RS_LineYellow': dict(base='#e3b30c', rough=0.65),
    'RS_Foliage': dict(base='#3d6a2a', rough=0.75, spec=0.3),
    'RS_Foliage2': dict(base='#6a8a35', rough=0.75, spec=0.3),
    'RS_PalmFrond': dict(base='#4b6b2c', rough=0.7, spec=0.3, double=True),
    'RS_PalmTrunk': dict(base='#6d5a45', rough=0.92),
    'RS_LightPanel': dict(base='#ffffff', rough=0.3, emit='#fff6ea', es=6.0),
    'RS_LightWarm': dict(base='#ffffff', rough=0.3, emit='#ffd9a8', es=5.0),
    'RS_LampHead': dict(base='#ffffff', rough=0.3, emit='#fff2df', es=8.0),
    'RS_InteriorWall': dict(base='#efe8dc', rough=0.6),
    'RS_InteriorFloor': dict(base='#b9b2a6', rough=0.25),
    'RS_Cooler': dict(base='#dfe9f2', rough=0.1, emit='#e8f2ff', es=2.0),
    'RS_ScreenDark': dict(base='#10161c', rough=0.15, emit='#5aa0ff', es=0.6),
    'RS_ReflectorRed': dict(base='#c4141b', rough=0.25),
    'RS_ReflectorYellow': dict(base='#f2c200', rough=0.3),
}


class Ctx:
    tex_dir = None


def get_mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    d = MATERIAL_DEFS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = hex_lin(d.get('base', '#ffffff'))
    bsdf.inputs['Roughness'].default_value = d.get('rough', 0.5)
    bsdf.inputs['Metallic'].default_value = d.get('metal', 0.0)
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = 1.5
    spec = d.get('spec')
    if spec is not None and 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = spec
    tex = d.get('tex')
    if tex:
        paths = ensure_texture(tex, Ctx.tex_dir)
        x = -700
        img_node = nt.nodes.new('ShaderNodeTexImage'); img_node.location = (x, 300)
        img_node.image = bpy.data.images.load(paths['albedo'], check_existing=True)
        img_node.image.colorspace_settings.name = 'sRGB'
        nt.links.new(img_node.outputs['Color'], bsdf.inputs['Base Color'])
        if d.get('emit_tex'):
            nt.links.new(img_node.outputs['Color'], bsdf.inputs['Emission Color'])
        if 'orm' in paths:
            orm = nt.nodes.new('ShaderNodeTexImage'); orm.location = (x, 0)
            orm.image = bpy.data.images.load(paths['orm'], check_existing=True)
            orm.image.colorspace_settings.name = 'Non-Color'
            sep = nt.nodes.new('ShaderNodeSeparateColor'); sep.location = (x + 300, 0)
            nt.links.new(orm.outputs['Color'], sep.inputs['Color'])
            nt.links.new(sep.outputs['Green'], bsdf.inputs['Roughness'])
            nt.links.new(sep.outputs['Blue'], bsdf.inputs['Metallic'])
        if 'normal' in paths:
            nrm = nt.nodes.new('ShaderNodeTexImage'); nrm.location = (x, -300)
            nrm.image = bpy.data.images.load(paths['normal'], check_existing=True)
            nrm.image.colorspace_settings.name = 'Non-Color'
            nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (x + 300, -300)
            nt.links.new(nrm.outputs['Color'], nm.inputs['Color'])
            nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if d.get('emit'):
        bsdf.inputs['Emission Color'].default_value = hex_lin(d['emit'])
    if d.get('emit') or d.get('emit_tex'):
        bsdf.inputs['Emission Strength'].default_value = d.get('es', 1.0)
    alpha = d.get('alpha', 1.0)
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
        try:
            m.blend_method = 'BLEND'
        except Exception:
            pass
    m.use_backface_culling = not d.get('double', False)
    m.diffuse_color = hex_lin(d.get('base', '#ffffff'))
    return m


# ---------------------------------------------------------------------------
# geometry primitives (all return bmesh objects in final/local coordinates)
# ---------------------------------------------------------------------------
def bm_box(x0, y0, z0, x1, y1, z1, bevel=0.0, seg=2, open_bottom=False, open_top=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
    if bevel > 0:
        b = min(bevel, 0.45 * min(sx, sy, sz))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, offset_type='OFFSET', segments=seg,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    _strip(bm, open_bottom, open_top, min(z0, z1), max(z0, z1))
    return bm


def _strip(bm, open_bottom, open_top, zmin, zmax):
    bm.normal_update()
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if open_bottom and f.normal.z < -0.99 and abs(c.z - zmin) < 1e-4:
            kill.append(f)
        if open_top and f.normal.z > 0.99 and abs(c.z - zmax) < 1e-4:
            kill.append(f)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context='FACES_ONLY')


def bm_cyl(cx, cy, z0, z1, r, seg=16, r2=None, caps=True, open_bottom=False):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=z1 - z0)
    bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=bm.verts)
    if open_bottom:
        _strip(bm, True, False, z0, z1)
    return bm


def bm_cyl_between(p0, p1, r, seg=8, caps=True, r2=None):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=d.length)
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ rot, verts=bm.verts)
    return bm


def bm_sphere(c, r, subdiv=1, scale=(1, 1, 1), jitter=0.0, seed=0):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
    rng = random.Random(seed)
    for v in bm.verts:
        if jitter:
            v.co *= 1.0 + rng.uniform(-jitter, jitter)
        v.co.x *= scale[0]; v.co.y *= scale[1]; v.co.z *= scale[2]
        v.co += Vector(c)
    return bm


def poly_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2


def ccw(pts):
    return pts if poly_area(pts) > 0 else list(reversed(pts))


def rounded_rect(x0, y0, x1, y1, r, seg=6):
    r = min(r, (x1 - x0) / 2 - 1e-4, (y1 - y0) / 2 - 1e-4)
    pts = []
    corners = [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]
    for cx, cy, a0 in corners:
        if r <= 1e-4:
            pts.append((cx, cy)); continue
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def bm_prism(pts, z0, z1, top=True, bottom=True):
    pts = ccw(pts)
    bm = bmesh.new()
    b = [bm.verts.new((x, y, z0)) for x, y in pts]
    t = [bm.verts.new((x, y, z1)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((b[i], b[j], t[j], t[i]))
    if top:
        bm.faces.new(t)
    if bottom:
        bm.faces.new(list(reversed(b)))
    return bm


def bm_ring_prism(outer, inner, z0, z1, top=True, bottom=True):
    outer, inner = ccw(outer), ccw(inner)
    assert len(outer) == len(inner)
    bm = bmesh.new()
    ob = [bm.verts.new((x, y, z0)) for x, y in outer]; ot = [bm.verts.new((x, y, z1)) for x, y in outer]
    ib = [bm.verts.new((x, y, z0)) for x, y in inner]; it = [bm.verts.new((x, y, z1)) for x, y in inner]
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((it[i], it[j], ib[j], ib[i]))
        if top:
            bm.faces.new((ot[i], ot[j], it[j], it[i]))
        if bottom:
            bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    return bm


def bm_quad(p0, p1, p2, p3):
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
    bm.faces.new(vs)
    return bm


def bm_hquad(x0, y0, x1, y1, z, down=False):
    """Horizontal quad facing +Z (or -Z when down=True)."""
    if down:
        return bm_quad((x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z))
    return bm_quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))


def bm_vquad(x0, x1, z0, z1, y, facing='-Y'):
    """Vertical quad in the XZ plane at y, facing -Y or +Y."""
    if facing == '-Y':
        return bm_quad((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))
    return bm_quad((x1, y, z0), (x0, y, z0), (x0, y, z1), (x1, y, z1))


def bm_poly_flat(pts, z, down=False):
    pts = ccw(pts)
    if down:
        pts = list(reversed(pts))
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((x, y, z)) for x, y in pts])
    return bm


def half_disc(r, gap=0.0, side=1, seg=16):
    """2D half-disc points (local XY), right half when side=1, left when side=-1."""
    pts = []
    for i in range(seg + 1):
        a = -math.pi / 2 + math.pi * i / seg
        pts.append((side * (gap / 2 + r * math.cos(a)), r * math.sin(a)))
    return pts


def bm_prism_local(pts, depth):
    """Extrude 2D local XY polygon from z=0 to z=depth (for use with place())."""
    return bm_prism(pts, 0.0, depth)


_FONTS = {}


def _font(path):
    if path not in _FONTS:
        _FONTS[path] = bpy.data.fonts.load(path, check_existing=True)
    return _FONTS[path]


def bm_text(body, font=FONT_BOLD, size=1.0, depth=0.05, bevel=0.0, res=3, align='CENTER',
            valign='CENTER', spacing=1.0, line_dist=1.0):
    """Text in local XY (reads along +X, up = +Y), back at z=0, front face at z=depth (+Z)."""
    cu = bpy.data.curves.new('tmp_text', 'FONT')
    cu.body = body
    cu.font = _font(font)
    cu.size = size
    cu.extrude = depth / 2 if depth > 0 else 0.0
    cu.bevel_depth = bevel
    cu.bevel_resolution = 0
    cu.resolution_u = res
    cu.align_x = align
    cu.align_y = valign
    cu.space_character = spacing
    cu.space_line = line_dist
    cu.fill_mode = 'BOTH'
    ob = bpy.data.objects.new('tmp_text', cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me)
    ev.to_mesh_clear()
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    if bm.verts:
        zmin = min(v.co.z for v in bm.verts)
        bmesh.ops.translate(bm, vec=(0, 0, -zmin), verts=bm.verts)
    bm.normal_update()
    return bm


def text_width(bm):
    xs = [v.co.x for v in bm.verts]
    return (max(xs) - min(xs)) if xs else 0.0


# local frame -> world frames. Local: X = right, Y = up, Z = out of the face.
FACING = {
    '-Y': Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0))),
    '+Y': Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0))),
    '+X': Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))),
    '-X': Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0))),
    '+Z': Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1))),
}


def place(facing, origin, rot_deg=0.0):
    """Matrix taking face-local coordinates to world. rot_deg rotates in the face plane."""
    m = FACING[facing].to_4x4()
    if rot_deg:
        m = m @ Matrix.Rotation(math.radians(rot_deg), 4, 'Z')
    return Matrix.Translation(origin) @ m


def front_back(front_mat, side_mat, thresh=0.5):
    """Material function: faces pointing local +Z get front_mat, others side_mat."""
    return lambda f: front_mat if f.normal.z > thresh else side_mat


# ---------------------------------------------------------------------------
# mesh accumulator
# ---------------------------------------------------------------------------
class MeshAcc:
    def __init__(self, name):
        self.name = name
        self.co, self.faces, self.fmat, self.uvs, self.mats = [], [], [], [], []

    def _mi(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def add(self, bm, mat, matrix=None, uv='box', tile=None, mat_fn=None, cell=None):
        """Append bmesh geometry.
        uv: 'box'  -> world-space box projection, tile = metres per texture repeat
            'fit'  -> each face's projected bounds fitted into `cell` (u0, v0, u1, v1)
        mat_fn: per-face material chooser evaluated on the *pre-transform* normals."""
        bm.normal_update()
        fm = [mat_fn(f) if mat_fn else mat for f in bm.faces]
        if matrix is not None:
            bmesh.ops.transform(bm, matrix=matrix, verts=bm.verts)
            if matrix.determinant() < 0:
                bmesh.ops.reverse_faces(bm, faces=bm.faces)
            bm.normal_update()
        bm.verts.index_update()
        base = len(self.co)
        self.co.extend(tuple(v.co) for v in bm.verts)
        for f, m in zip(bm.faces, fm):
            self.faces.append([base + v.index for v in f.verts])
            self.fmat.append(self._mi(m))
            t = tile if tile is not None else MATERIAL_DEFS.get(m, {}).get('tile', 1.0)
            self.uvs.append(_face_uv(f, uv, t, cell))
        bm.free()
        return self

    def tris(self):
        return sum(len(f) - 2 for f in self.faces)

    def build(self, collection, parent, sharp_deg=40.0, weighted=True):
        if not self.faces:
            return None
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.co, [], self.faces)
        for m in self.mats:
            me.materials.append(get_mat(m))
        me.polygons.foreach_set('material_index', self.fmat)
        uvl = me.uv_layers.new(name='UVMap')
        flat = [c for f in self.uvs for uv in f for c in uv]
        uvl.data.foreach_set('uv', flat)
        me.validate(clean_customdata=False)
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        collection.objects.link(ob)
        ob.parent = parent
        if weighted:
            mod = ob.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
            mod.mode = 'FACE_AREA'
            mod.keep_sharp = True
            dg = bpy.context.evaluated_depsgraph_get()
            new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True,
                                                  depsgraph=dg)
            ob.modifiers.clear()
            old = ob.data
            ob.data = new
            bpy.data.meshes.remove(old)
            new.name = self.name
        return ob


def _face_uv(f, mode, tile, cell):
    n = f.normal
    ax = max(range(3), key=lambda i: abs(n[i]))
    pts = []
    for l in f.loops:
        p = l.vert.co
        if ax == 2:
            u, v = p.x, (p.y if n.z > 0 else -p.y)
        elif ax == 1:
            u, v = (p.x if n.y < 0 else -p.x), p.z
        else:
            u, v = (p.y if n.x > 0 else -p.y), p.z
        pts.append((u, v))
    if mode == 'fit':
        u0, v0, u1, v1 = cell or (0, 0, 1, 1)
        us = [p[0] for p in pts]; vs = [p[1] for p in pts]
        du = (max(us) - min(us)) or 1.0; dv = (max(vs) - min(vs)) or 1.0
        return [(u0 + (u - min(us)) / du * (u1 - u0), v0 + (v - min(vs)) / dv * (v1 - v0)) for u, v in pts]
    tu, tv = (tile, tile) if not isinstance(tile, (tuple, list)) else tile
    return [(u / tu, v / tv) for u, v in pts]


# ---------------------------------------------------------------------------
# asset container
# ---------------------------------------------------------------------------
class Asset:
    def __init__(self, prefix, title, asset_dir, basename):
        self.prefix, self.title = prefix, title
        self.asset_dir = asset_dir
        self.basename = basename
        self.src_dir = f'{asset_dir}/source'
        self.tex_dir = f'{asset_dir}/source/textures'
        os.makedirs(self.tex_dir, exist_ok=True)
        # Godot must import only the .glb, never the .blend / source textures
        open(f'{self.src_dir}/.gdignore', 'w').close()
        Ctx.tex_dir = self.tex_dir
        reset_scene()
        sc = bpy.context.scene
        self.coll = bpy.data.collections.new(prefix)
        sc.collection.children.link(self.coll)
        self.root = self._empty(f'{prefix}_{title}', self.coll, None, size=3.0)
        self.root['asset_id'] = basename
        self.root['front_axis_blender'] = '-Y'
        self.root['units'] = 'metres'
        self.lod_coll, self.lod_root = {}, {}
        for L in (0, 1, 2):
            c = bpy.data.collections.new(f'{prefix}_LOD{L}')
            self.coll.children.link(c)
            self.lod_coll[L] = c
            e = self._empty(f'{prefix}_LOD{L}', c, self.root)
            b, en = LOD_RANGES[L]
            e['lod_level'] = L
            e['visibility_range_begin'] = b
            e['visibility_range_end'] = en
            e['visibility_range_margin'] = LOD_MARGIN
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
        self.parts = {}
        self.cameras = {}

    def _empty(self, name, coll, parent, size=1.0):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = size
        coll.objects.link(e)
        e.parent = parent
        return e

    def m(self, L, part):
        key = (L, part)
        if key not in self.parts:
            self.parts[key] = MeshAcc(f'{self.prefix}_LOD{L}_{part}')
        return self.parts[key]

    def col_box(self, name, x0, y0, z0, x1, y1, z1):
        bm = bm_box(x0, y0, z0, x1, y1, z1)
        me = bpy.data.meshes.new(f'{self.prefix}_COL_{name}')
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f'{self.prefix}_COL_{name}-convcolonly', me)
        self.col_coll.objects.link(ob)
        ob.parent = self.col_root
        ob.display_type = 'WIRE'
        ob.hide_render = True
        return ob

    def light(self, name, kind, loc, energy, color='#fff2e0', rot=(0, 0, 0), spot_deg=120, blend=0.6,
              radius=0.1, shadow=False):
        ld = bpy.data.lights.new(f'{self.prefix}_{name}', kind)
        ld.energy = energy
        ld.color = hex_lin(color)[:3]
        if kind == 'SPOT':
            ld.spot_size = math.radians(spot_deg)
            ld.spot_blend = blend
        if hasattr(ld, 'shadow_soft_size'):
            ld.shadow_soft_size = radius
        ld.use_shadow = shadow
        ob = bpy.data.objects.new(f'{self.prefix}_{name}', ld)
        ob.location = loc
        ob.rotation_euler = [math.radians(a) for a in rot]
        self.light_coll.objects.link(ob)
        ob.parent = self.light_root
        return ob

    def preview_add(self, name, bm, mat):
        acc = MeshAcc(name)
        acc.add(bm, mat)
        return acc.build(self.preview, None, weighted=False)

    def camera(self, key, loc, target, lens=35):
        self.cameras[key] = dict(loc=list(loc), target=list(target), lens=lens)

    def finalize(self):
        stats = {}
        for (L, part), acc in sorted(self.parts.items()):
            ob = acc.build(self.lod_coll[L], self.lod_root[L])
            if ob:
                stats.setdefault(L, {})[part] = acc.tris()
        self.root['preview_cameras'] = json.dumps(self.cameras)
        return stats

    # -------------------------------------------------------------- export
    def save_and_export(self):
        blend = f'{self.src_dir}/{self.basename}.blend'
        glb = f'{self.asset_dir}/{self.basename}.glb'
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in self.coll.all_objects:
            ob.hide_set(False)
            ob.select_set(True)
        bpy.context.view_layer.objects.active = self.root
        res = bpy.ops.export_scene.gltf(
            filepath=glb, export_format='GLB', use_selection=True, export_extras=True,
            export_lights=True, export_cameras=False, export_apply=True, export_yup=True,
            export_texcoords=True, export_normals=True, export_tangents=False,
            export_materials='EXPORT', export_image_format='AUTO', export_animations=False,
            export_import_convert_lighting_mode='SPEC')
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        return blend, glb, res


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    _FONTS.clear()


# ---------------------------------------------------------------------------
# reusable roadside elements
# ---------------------------------------------------------------------------
def rect_subtract(rects, hole):
    """Axis-aligned rectangle difference. rects: list of (x0,y0,x1,y1)."""
    hx0, hy0, hx1, hy1 = hole
    out = []
    for (x0, y0, x1, y1) in rects:
        if hx0 >= x1 or hx1 <= x0 or hy0 >= y1 or hy1 <= y0:
            out.append((x0, y0, x1, y1)); continue
        if hy0 > y0: out.append((x0, y0, x1, hy0))
        if hy1 < y1: out.append((x0, hy1, x1, y1))
        mx0, mx1 = max(x0, hx0), min(x1, hx1)
        my0, my1 = max(y0, hy0), min(y1, hy1)
        if hx0 > x0: out.append((x0, my0, hx0, my1))
        if hx1 < x1: out.append((hx1, my0, x1, my1))
    return [r for r in out if r[2] - r[0] > 1e-4 and r[3] - r[1] > 1e-4]


def ground_regions(acc, rects, mat, z=0.0):
    for (x0, y0, x1, y1) in rects:
        acc.add(bm_hquad(x0, y0, x1, y1, z), mat)


def pad_skirt(acc, x0, y0, x1, y1, depth=0.3, mat='RS_Concrete'):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    acc.add(bm_prism(pts, -depth, 0.0, top=False, bottom=False), mat)


def curb_bed(acc, L, x0, y0, x1, y1, h=0.15, w=0.15, fill='RS_Gravel', curb='RS_Concrete', top=True):
    """Raised landscape bed: concrete curb ring + gravel/soil fill."""
    if L <= 1:
        outer = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        inner = [(x0 + w, y0 + w), (x1 - w, y0 + w), (x1 - w, y1 - w), (x0 + w, y1 - w)]
        acc.add(bm_ring_prism(outer, inner, 0.0, h, bottom=False), curb)
        acc.add(bm_hquad(x0 + w, y0 + w, x1 - w, y1 - w, h - 0.03), fill)
    else:
        acc.add(bm_box(x0, y0, 0, x1, y1, h, open_bottom=True), fill)


def shrub(acc, L, x, y, s=1.0, seed=0, mat='RS_Foliage'):
    if L == 0:
        acc.add(bm_sphere((x, y, 0.35 * s), 0.55 * s, 2, (1.0, 1.0, 0.75), 0.18, seed), mat)
    elif L == 1:
        acc.add(bm_sphere((x, y, 0.35 * s), 0.55 * s, 1, (1.0, 1.0, 0.75), 0.12, seed), mat)


def grass_clump(acc, L, x, y, h=0.7, seed=0, mat='RS_Foliage2'):
    if L > 0:
        if L == 1:
            acc.add(bm_cyl(x, y, 0.0, h * 0.8, 0.28, 6, r2=0.4, caps=True, open_bottom=True), mat)
        return
    rng = random.Random(seed)
    bm = bmesh.new()
    for i in range(9):
        a = rng.uniform(0, math.tau)
        lean = rng.uniform(0.15, 0.45)
        hh = h * rng.uniform(0.7, 1.1)
        w = 0.035
        base = Vector((x + 0.08 * math.cos(a), y + 0.08 * math.sin(a), 0.0))
        tipd = Vector((math.cos(a) * lean, math.sin(a) * lean, hh))
        side = Vector((-math.sin(a), math.cos(a), 0)) * w
        v0 = bm.verts.new(base - side); v1 = bm.verts.new(base + side)
        v2 = bm.verts.new(base + tipd * 0.55 + side * 0.6); v3 = bm.verts.new(base + tipd * 0.55 - side * 0.6)
        v4 = bm.verts.new(base + tipd)
        bm.faces.new((v0, v1, v2, v3)); bm.faces.new((v3, v2, v4))
    acc.add(bm, 'RS_PalmFrond')


def palm(acc, L, x, y, h=7.0, seed=0):
    rng = random.Random(seed)
    seg = {0: 10, 1: 6, 2: 5}[L]
    rings = {0: 6, 1: 2, 2: 1}[L]
    # trunk: tapered, slightly bent, with ring bulges on LOD0
    pts = []
    lean = Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0))
    for i in range(rings + 1):
        t = i / rings
        pts.append(Vector((x, y, 0)) + lean * (t * t) + Vector((0, 0, h * t)))
    for i in range(rings):
        r0 = 0.30 - 0.08 * (i / rings); r1 = 0.30 - 0.08 * ((i + 1) / rings)
        bm = bm_cyl_between(pts[i], pts[i + 1], r0, seg, caps=False, r2=r1 * (0.92 if L == 0 else 1.0))
        acc.add(bm, 'RS_PalmTrunk', tile=1.0)
    top = pts[-1]
    acc.add(bm_sphere(tuple(top + Vector((0, 0, 0.1))), 0.42, 1 if L < 2 else 0, (1, 1, 0.9), 0.1, seed),
            'RS_PalmTrunk')
    nf = {0: 16, 1: 10, 2: 6}[L]
    ns = {0: 7, 1: 4, 2: 2}[L]
    bm = bmesh.new()
    for k in range(nf):
        a = k / nf * math.tau + rng.uniform(-0.15, 0.15)
        up = rng.uniform(0.25, 0.9) if k % 2 == 0 else rng.uniform(-0.1, 0.5)
        length = rng.uniform(2.6, 3.4)
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-math.sin(a), math.cos(a), 0))
        prev = None
        for s in range(ns + 1):
            t = s / ns
            # parabolic droop
            p = top + d * (length * t) + Vector((0, 0, length * (up * t - 0.75 * t * t)))
            w = 0.55 * math.sin(math.pi * min(1.0, t * 1.15 + 0.05)) + 0.04
            fold = Vector((0, 0, 0.12 * w)) if L == 0 else Vector((0, 0, 0))
            row = [bm.verts.new(p - side * w - fold), bm.verts.new(p), bm.verts.new(p + side * w - fold)]
            if prev:
                bm.faces.new((prev[0], prev[1], row[1], row[0]))
                bm.faces.new((prev[1], prev[2], row[2], row[1]))
            prev = row
    acc.add(bm, 'RS_PalmFrond')


def bollard(acc, L, x, y, h=1.0, r=0.1):
    if L == 0:
        acc.add(bm_cyl(x, y, 0, h, r, 16, open_bottom=True), 'RS_MetalGalv')
        acc.add(bm_sphere((x, y, h), r, 1, (1, 1, 0.5)), 'RS_MetalGalv')
        acc.add(bm_cyl(x, y, h - 0.25, h - 0.17, r + 0.005, 16, caps=False), 'RS_ReflectorRed')
    elif L == 1:
        acc.add(bm_cyl(x, y, 0, h, r, 8, open_bottom=True), 'RS_MetalGalv')


def lamp_post(acc, L, x, y, h=8.0, facing=(0, 1), arm=1.2, double=False):
    seg = {0: 16, 1: 8, 2: 6}[L]
    if L == 0:
        acc.add(bm_box(x - 0.25, y - 0.25, 0, x + 0.25, y + 0.25, 0.5, bevel=0.03, open_bottom=True), 'RS_Concrete')
    z0 = 0.5 if L == 0 else 0.0
    acc.add(bm_cyl(x, y, z0, h, 0.11, seg, r2=0.07, open_bottom=True), 'RS_MetalDark')
    dirs = [facing] + ([(-facing[0], -facing[1])] if double else [])
    for fx, fy in dirs:
        if L <= 1:
            acc.add(bm_cyl_between((x, y, h - 0.15), (x + fx * arm, y + fy * arm, h), 0.045, 6), 'RS_MetalDark')
        hx, hy = x + fx * arm, y + fy * arm
        w, l = 0.35, 0.75
        ax, ay = (l / 2 if fx else w / 2), (w / 2 if fx else l / 2)
        acc.add(bm_box(hx - ax, hy - ay, h - 0.02, hx + ax, hy + ay, h + 0.12,
                       bevel=0.03 if L == 0 else 0, open_bottom=True), 'RS_MetalDark')
        acc.add(bm_quad((hx - ax + 0.04, hy - ay + 0.04, h - 0.025), (hx - ax + 0.04, hy + ay - 0.04, h - 0.025),
                        (hx + ax - 0.04, hy + ay - 0.04, h - 0.025), (hx + ax - 0.04, hy - ay + 0.04, h - 0.025)),
                'RS_LampHead')


def parking_bays(acc, x0, y_line0, y_line1, n, w=2.6, line=0.1, z=0.006, mat='RS_LineWhite'):
    """Perpendicular parking bay lines along +X starting at x0; bays span y_line0..y_line1."""
    for i in range(n + 1):
        x = x0 + i * w
        acc.add(bm_hquad(x - line / 2, y_line0, x + line / 2, y_line1, z), mat)


def arrow_mark(acc, x, y, ang_deg, length=4.0, z=0.006, mat='RS_LineWhite'):
    s = length
    pts = [(-0.5 * s, -0.08 * s), (0.15 * s, -0.08 * s), (0.15 * s, -0.2 * s), (0.5 * s, 0.0),
           (0.15 * s, 0.2 * s), (0.15 * s, 0.08 * s), (-0.5 * s, 0.08 * s)]
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    acc.add(bm_poly_flat(pts, z), mat)


def product_shelf(acc, L, x0, y0, x1, y1, h=1.8, levels=5, seed=0, two_sided=True):
    """Gondola shelf aligned along X (x0..x1), depth y0..y1, product boxes on each level."""
    rng = random.Random(seed)
    if L == 2:
        return
    acc.add(bm_box(x0, y0, 0.0, x1, y1, 0.12, open_bottom=True), 'RS_PaintCharcoal')
    yc = (y0 + y1) / 2
    acc.add(bm_box(x0, yc - 0.03, 0.12, x1, yc + 0.03, h, open_bottom=True), 'RS_PaintWhite')
    acc.add(bm_box(x0 - 0.02, y0, 0.0, x0, y1, h, open_bottom=True), 'RS_PaintWhite')
    acc.add(bm_box(x1, y0, 0.0, x1 + 0.02, y1, h, open_bottom=True), 'RS_PaintWhite')
    sides = [(y0, yc - 0.03, -1), (yc + 0.03, y1, 1)] if two_sided else [(y0, yc - 0.03, -1)]
    for lvl in range(levels):
        z = 0.12 + lvl * (h - 0.25) / levels
        for sy0, sy1, sgn in sides:
            acc.add(bm_box(x0, sy0, z, x1, sy1, z + 0.025, open_bottom=(L == 1)), 'RS_PaintWhite')
            if L == 1:
                # one textured block per shelf level reads as products from distance
                ztop = z + 0.025 + (h - 0.25) / levels * 0.72
                acc.add(bm_box(x0 + 0.02, sy0 + 0.02, z + 0.025, x1 - 0.02, sy1 - 0.02, ztop, open_bottom=True),
                        'RS_Products', uv='fit', cell=(0, 0, 1, 0.25))
                continue
            x = x0 + 0.02
            while x < x1 - 0.1:
                pw = rng.uniform(0.07, 0.18)
                ph = rng.uniform(0.12, (h - 0.25) / levels * 0.8)
                pd = (sy1 - sy0) * rng.uniform(0.6, 0.92)
                i, j = rng.randrange(8), rng.randrange(8)
                cell = (i / 8, j / 8, (i + 1) / 8, (j + 1) / 8)
                if sgn < 0:
                    yy0, yy1 = sy0 + 0.01, sy0 + 0.01 + pd
                else:
                    yy0, yy1 = sy1 - 0.01 - pd, sy1 - 0.01
                xe = min(x + pw, x1 - 0.02)
                acc.add(bm_box(x, yy0, z + 0.025, xe, yy1, z + 0.025 + ph, open_bottom=True),
                        'RS_Products', uv='fit', cell=cell)
                x = xe + 0.005


# ---------------------------------------------------------------------------
# preview environment, lighting, rendering helpers
# ---------------------------------------------------------------------------
def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def preview_sand_material():
    m = bpy.data.materials.get('PV_Sand')
    if m:
        return m
    m = bpy.data.materials.new('PV_Sand'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 0.4
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = hex_lin('#b89a74'); ramp.color_ramp.elements[1].color = hex_lin('#d6bd98')
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.95
    return m


def build_preview_env(asset, plot, road_y=None):
    """Sand ground + an E11-style road in front of the plot. Not exported."""
    x0, y0, x1, y1 = plot
    sand = preview_sand_material()
    MATERIAL_DEFS.setdefault('PV_Sand', dict(base='#c8ab86'))
    acc = MeshAcc('PV_Sand')
    for r in rect_subtract([(-3000, -3000, 3000, 3000)], (x0, y0 - 16.0, x1, y1)):
        acc.add(bm_hquad(*r, -0.02), 'PV_Sand')
    ob = acc.build(asset.preview, None, weighted=False)
    ob.data.materials[0] = sand
    # road: 3 lanes + shoulder in front of the plot (along X), plus long extension
    road = MeshAcc('PV_Road')
    ry0, ry1 = y0 - 15.0, y0 - 1.0
    road.add(bm_hquad(-1500, ry0, 1500, ry1, -0.01), 'RS_Asphalt')
    road.add(bm_hquad(x0, ry1, x1, y0, -0.005), 'RS_Concrete')
    for i, yy in enumerate([ry0 + 1.0, ry0 + 4.6, ry0 + 8.2, ry1 - 1.0]):
        if i in (0, 3):
            road.add(bm_hquad(-1500, yy - 0.08, 1500, yy + 0.08, 0.0), 'RS_LineWhite' if i == 3 else 'RS_LineYellow')
        else:
            for k in range(-160, 160):
                xx = k * 9.0
                road.add(bm_hquad(xx, yy - 0.07, xx + 3.0, yy + 0.07, 0.0), 'RS_LineWhite')
    road.build(asset.preview, None, weighted=False)


def setup_render(scene, w=1600, h=900, samples=96):
    q = float(os.environ.get('RS_PREVIEW_SCALE', '1'))
    w, h, samples = int(w * q), int(h * q), max(8, int(samples * q))
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 16
    scene.cycles.sample_clamp_indirect = 8.0
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass


def set_world(scene, mode):
    w = bpy.data.worlds.get('PV_World') or bpy.data.worlds.new('PV_World')
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        if n.type not in ('OUTPUT_WORLD',):
            nt.nodes.remove(n)
    out = nt.nodes['World Output']
    bg = nt.nodes.new('ShaderNodeBackground')
    nt.links.new(bg.outputs[0], out.inputs[0])
    sun = bpy.data.objects.get('PV_Sun')
    if sun is None:
        sun = bpy.data.objects.new('PV_Sun', bpy.data.lights.new('PV_Sun', 'SUN'))
        scene.collection.objects.link(sun)
    if mode == 'day':
        sky = nt.nodes.new('ShaderNodeTexSky')
        sky.sky_type = 'NISHITA'
        sky.sun_disc = False
        sky.sun_elevation = math.radians(40)
        sky.sun_rotation = math.radians(215)
        sky.air_density = 1.2
        sky.dust_density = 1.6
        nt.links.new(sky.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 0.22
        sun.data.energy = 4.2
        sun.data.color = (1.0, 0.95, 0.86)
        sun.data.angle = math.radians(0.8)
        sun.rotation_euler = (math.radians(50), 0, math.radians(215 - 180 + 20))
        scene.view_settings.exposure = 0.0
    else:
        grad = nt.nodes.new('ShaderNodeTexGradient')
        coord = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        nt.links.new(coord.outputs['Generated'], sep.inputs[0])
        nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
        ramp.color_ramp.elements[0].position = 0.48
        ramp.color_ramp.elements[0].color = (0.020, 0.018, 0.030, 1)
        ramp.color_ramp.elements[1].position = 0.62
        ramp.color_ramp.elements[1].color = (0.004, 0.006, 0.020, 1)
        nt.links.new(ramp.outputs['Color'], bg.inputs[0])
        bg.inputs[1].default_value = 1.0
        sun.data.energy = 0.03
        sun.data.color = (0.6, 0.7, 1.0)
        sun.rotation_euler = (math.radians(40), 0, math.radians(120))
        scene.view_settings.exposure = 0.6
    return sun


def gltf_report(glb_path):
    """Parse a .glb and report what Godot will actually receive."""
    import struct
    with open(glb_path, 'rb') as f:
        data = f.read()
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    acc = js.get('accessors', [])
    meshes = js.get('meshes', [])
    nodes = js.get('nodes', [])

    def mesh_tris(mi):
        t = 0
        for p in meshes[mi]['primitives']:
            if 'indices' in p:
                t += acc[p['indices']]['count'] // 3
            else:
                t += acc[p['attributes']['POSITION']]['count'] // 3
        return t
    lod_tris = {}

    def walk(ni, lod):
        n = nodes[ni]
        name = n.get('name', '')
        for L in (0, 1, 2):
            if name.endswith(f'_LOD{L}'):
                lod = L
        if 'mesh' in n and lod is not None:
            lod_tris[lod] = lod_tris.get(lod, 0) + mesh_tris(n['mesh'])
        for c in n.get('children', []):
            walk(c, lod)
    for s in js['scenes']:
        for ni in s['nodes']:
            walk(ni, None)
    mats = js.get('materials', [])
    return dict(
        lod_tris=lod_tris,
        materials=len(mats),
        alpha_blend=[m['name'] for m in mats if m.get('alphaMode') == 'BLEND'],
        double_sided=[m['name'] for m in mats if m.get('doubleSided')],
        images=[(im.get('name'), im.get('mimeType')) for im in js.get('images', [])],
        extensions=js.get('extensionsUsed', []),
        lights=len(js.get('extensions', {}).get('KHR_lights_punctual', {}).get('lights', [])),
        collision_nodes=[n['name'] for n in nodes if n.get('name', '').endswith('-convcolonly')],
        lod_extras={n['name']: n.get('extras') for n in nodes if n.get('name', '').endswith(('_LOD0', '_LOD1', '_LOD2'))},
        nodes=len(nodes), meshes=len(meshes),
        primitives=sum(len(m['primitives']) for m in meshes),
    )
