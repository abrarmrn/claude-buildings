"""Boulevard 5 kit - Sheikh Mohammed bin Rashid Boulevard podium retail / restaurant assets.

Builds on the premium_commercial_17 construction kit, imported strictly READ-ONLY (byte-code writing disabled, the
texture cache redirected into this folder).  Nothing in prototypes/, additional_17/ or premium_commercial_17/ is written.

Conventions (same as the earlier assets):
  * metres, Z up, street-facing front = Blender -Y (glTF / Godot +Z, Unreal: import with "Convert Scene" on)
  * origin = centre of the plot frontage line (the building line), ground level; the building is at y >= 0
  * promenade strip in front: y = 0 .. -PROM (separate PROMENADE_FRONTAGE collection, removable)
  * outdoor terraces / street furniture: separate OPTIONAL_TERRACE collection (removable)
  * podium only: each asset ends in a flat podium roof + a REAR TOWER INTERFACE (vertical boundary plane + empty with
    extras) so it can be docked against an existing Downtown tower; no residential tower is modelled.
  * no vegetation anywhere (planters are empty stone structures).
"""
import os, sys, math, json, shutil
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
BV = os.path.normpath(os.path.join(HERE, '..'))
STORES = os.path.normpath(os.path.join(BV, '..'))
P17_TOOLS = os.path.join(STORES, 'premium_commercial_17', '_tools')
sys.path.insert(0, P17_TOOLS)

import pk_core as C
C.SITE_COMPONENTS[:] = C.SITE_COMPONENTS + ['PROMENADE_FRONTAGE', 'OPTIONAL_TERRACE']   # in-memory only
from pk_core import *                                   # noqa: F401,F403  (bpy, bmesh, Vector, Matrix, R, K, txt, ...)
HERE = os.path.dirname(os.path.abspath(__file__))     # (pk_core's star-import shadows HERE - restore it)
import pk_arch as AR
import pk_furn as F
import pk_site as S

K.TEXCACHE = os.path.join(HERE, 'texcache')            # own cache (gitignored), never the earlier folders'
os.makedirs(K.TEXCACHE, exist_ok=True)

FONT.update(
    cinzel=os.path.join(HERE, 'fonts', 'Cinzel-Medium.ttf'),
    cinzel_sb=os.path.join(HERE, 'fonts', 'Cinzel-SemiBold.ttf'),
    garamond=os.path.join(HERE, 'fonts', 'CormorantGaramond-Medium.ttf'),
    garamond_sb=os.path.join(HERE, 'fonts', 'CormorantGaramond-SemiBold.ttf'),
    garamond_i=os.path.join(HERE, 'fonts', 'CormorantGaramond-MediumItalic.ttf'),
)

PROM = 7.0                      # promenade depth in front of the building line
LOD_RANGES = {0: (0.0, 110.0), 1: (110.0, 300.0), 2: (300.0, 1800.0)}


# ---------------------------------------------------------------------------------------------- textures
def _fft(n, beta, seed, aniso=(1.0, 1.0)):
    return R._fft_noise(n, beta, seed, aniso)


def tex_stone(d, key, tone, seed, n=C.TEX_N, pw=1.2, ph=0.6, cols=2, rows=4, joint_mm=6, vein=0.0):
    """Large-format natural stone cladding, one texture tile = cols x rows panels (pw x ph m each)."""
    ys, xs = np.mgrid[0:n, 0:n] / n
    pu, pv = (xs * cols) % 1.0, (ys * rows + 0.5 * (np.floor(xs * cols) % 2)) % 1.0
    jx = np.minimum(pu, 1 - pu) * pw; jy = np.minimum(pv, 1 - pv) * ph
    j = joint_mm / 1000.0
    joint = np.clip((np.minimum(jx, jy) - j * 0.5) / (j * 0.4), 0, 1)
    pid = (np.floor(xs * cols) + cols * np.floor(ys * rows + 0.5 * (np.floor(xs * cols) % 2))).astype(int)
    rng = np.random.default_rng(seed); ptone = rng.normal(0, 0.028, cols * rows * 2 + 4)[pid % (cols * rows * 2 + 4)]
    noise = _fft(n, 1.1, seed + 1); fine = _fft(n, 0.3, seed + 2)
    strata = _fft(n, 1.7, seed + 3, aniso=(0.10, 1.0))
    base = np.array(tone)[None, None] * (1 + ptone[..., None] + 0.04 * noise[..., None] + 0.025 * fine[..., None]
                                         + 0.045 * strata[..., None])
    if vein:
        pores = (_fft(n, 0.2, seed + 4) > 2.3).astype(float)          # travertine pores
        base = base * (1 - vein * pores[..., None] * 0.35)
    col = base * (0.45 + 0.55 * joint[..., None])
    rough = np.clip(0.58 + 0.06 * fine + (1 - joint) * 0.25, 0, 1)
    C._save3(col, rough, joint * 2.0 + 0.06 * fine + 0.03 * strata, key, d, 1.0)


def tex_paving(d, key='bv_paving', n=C.TEX_N, seed=91):
    """Promenade: 1.2 x 0.6 m honed limestone slabs in running bond, with a darker 0.3 m granite band every 4.8 m."""
    ys, xs = np.mgrid[0:n, 0:n] / n            # tile = 4.8 x 4.8 m
    rows = ys * 8.0; r = np.floor(rows).astype(int)
    cols = xs * 4.0 + 0.5 * (r % 2); c = np.floor(cols).astype(int)
    fu, fv = cols - c, rows - r
    e = np.minimum(np.minimum(fu, 1 - fu) * 1.2, np.minimum(fv, 1 - fv) * 0.6)
    joint = np.clip((e - 0.003) / 0.002, 0, 1)
    band = (ys * 4.8 < 0.3)
    rng = np.random.default_rng(seed); tone = rng.normal(0, 0.03, (8, 5))[r % 8, c % 5]
    noise = _fft(n, 1.0, seed + 1); fine = _fft(n, 0.3, seed + 2)
    light = np.array([0.80, 0.75, 0.66]); dark = np.array([0.30, 0.29, 0.28])
    base = np.where(band[..., None], dark[None, None], light[None, None])
    col = base * (1 + tone[..., None] + 0.04 * noise[..., None] + 0.02 * fine[..., None]) * (0.6 + 0.4 * joint[..., None])
    rough = np.clip(0.72 + 0.05 * noise - band * 0.2, 0, 1)
    C._save3(col, rough, joint, key, d, 1.0)


def tex_terrace_deck(d, key='bv_deck', n=512, seed=95):
    """Ipe-style terrace deck boards 0.14 m with 6 mm gaps (tile 1.4 m)."""
    ys, xs = np.mgrid[0:n, 0:n] / n
    b = xs * 10.0; bi = np.floor(b).astype(int); fu = b - bi
    gap = np.clip((np.minimum(fu, 1 - fu) * 0.14 - 0.003) / 0.002, 0, 1)
    grain = _fft(n, 1.8, seed, aniso=(1.0, 0.05))
    rng = np.random.default_rng(seed); t = rng.normal(0, 0.07, 32)[bi % 32]
    col = np.array([0.36, 0.22, 0.14])[None, None] * (1 + t[..., None] + 0.1 * grain[..., None]) * (0.35 + 0.65 * gap[..., None])
    rough = np.clip(0.6 + 0.05 * grain + (1 - gap) * 0.3, 0, 1)
    C._save3(col, rough, gap, key, d, 1.0)


for _k, _f in dict(
        bv_limestone=lambda d: tex_stone(d, 'bv_limestone', (0.86, 0.80, 0.70), 101),
        bv_champagne=lambda d: tex_stone(d, 'bv_champagne', (0.84, 0.75, 0.60), 111, pw=0.9, ph=0.9, cols=3, rows=3),
        bv_travertine=lambda d: tex_stone(d, 'bv_travertine', (0.88, 0.83, 0.73), 121, pw=1.2, ph=0.6, vein=1.0),
        bv_beige=lambda d: tex_stone(d, 'bv_beige', (0.80, 0.71, 0.58), 131, pw=1.5, ph=0.75),
        bv_paving=tex_paving, bv_deck=tex_terrace_deck).items():
    R.EXTRA_TEXTURES[_k] = _f

MD = R.MATERIAL_DEFS
MD.update({
    'BV_Limestone': dict(base='#ffffff', tex='bv_limestone', tile=(2.4, 2.4)),
    'BV_Champagne': dict(base='#ffffff', tex='bv_champagne', tile=(2.7, 2.7)),
    'BV_Travertine': dict(base='#ffffff', tex='bv_travertine', tile=(2.4, 2.4)),
    'BV_BeigeStone': dict(base='#ffffff', tex='bv_beige', tile=(3.0, 3.0)),
    'BV_Paving': dict(base='#ffffff', tex='bv_paving', tile=(4.8, 4.8)),
    'BV_Deck': dict(base='#ffffff', tex='bv_deck', tile=(1.4, 1.4)),
    'BV_StoneSmooth': dict(base='#d8ccb6', rough=0.5),               # plain stone for small mouldings / LOD2
    'BV_StoneDarkBase': dict(base='#ffffff', tex='pc_granite', tile=2.0),
    'BV_BronzeDark': dict(base='#4a3826', rough=0.34, metal=1.0),
    'BV_Bronze': dict(base='#7a5a38', rough=0.30, metal=1.0),
    'BV_BlackFrame': dict(base='#151515', rough=0.35, metal=0.7),
    'BV_Champ': dict(base='#b29a74', rough=0.30, metal=1.0),
    'BV_Glass': dict(base='#2c3a3d', rough=0.02, alpha=0.11, double=True, spec=0.9),
    'BV_GlassWarm': dict(base='#3a3a33', rough=0.02, alpha=0.12, double=True, spec=0.9),
    'BV_Linen': dict(base='#ece4d4', rough=0.9),
    'BV_Velvet': dict(base='#5c2a2a', rough=0.95),
    'BV_VelvetGreen': dict(base='#2e4a3c', rough=0.95),
    'BV_VelvetBlue': dict(base='#2a3a5a', rough=0.95),
    'BV_Cream': dict(base='#e8dfcf', rough=0.6),
    'BV_PlasterWarm': dict(base='#e9dcc6', rough=0.8),
    'BV_Parasol': dict(base='#e7dfcd', rough=0.85),
    'BV_LetterBronze': dict(base='#a07a48', rough=0.25, metal=1.0, emit='#ffcf8a', es=1.2),
    'BV_LetterGold': dict(base='#c9a65a', rough=0.22, metal=1.0, emit='#ffd58f', es=1.4),
    'BV_LetterWhite': dict(base='#f6f1e7', rough=0.3, emit='#fff3df', es=3.0),
    'BV_LetterDark': dict(base='#2a2a2a', rough=0.35, metal=0.4),
    'BV_Halo': dict(base='#ffffff', rough=0.5, emit='#ffd9a8', es=8.0),
    'BV_Chandelier': dict(base='#fff2dc', rough=0.2, emit='#ffcf94', es=10.0),
    'BV_Interface': dict(base='#9a948a', rough=0.85),
    'PC_Pastry': dict(base='#c78a4e', rough=0.6),
    'BV_Macaron': dict(base='#e3a9b4', rough=0.55),
})


# ---------------------------------------------------------------------------------------------- asset
def new_asset(num, slug, base, title, display, floors):
    """PAsset placed in this folder (pk_core builds paths from premium_commercial_17; we re-point them here)."""
    rel = os.path.relpath(os.path.join(BV, slug), C.P17)
    A = C.PAsset(num, rel, base, f'B{num}', title, display, floors, lod_ranges=LOD_RANGES)
    A.dir = os.path.normpath(A.dir)
    A.tex_dir = os.path.normpath(A.tex_dir)
    R.Ctx.tex_dir = A.tex_dir
    A.root['location_context'] = 'Sheikh Mohammed bin Rashid Boulevard, Downtown Dubai (architectural character only; ' \
                                 'no real-world coordinates or tenant positions are implied)'
    A.root['fictional_business'] = True
    A.root['upper_boundary'] = 'podium roof + rear tower interface - dock under / against an existing tower'
    A.group_root['PROMENADE_FRONTAGE']['optional'] = True
    A.group_root['OPTIONAL_TERRACE']['optional'] = True
    return A


# ---------------------------------------------------------------------------------------------- architectural pieces
def stone_box(acc, L, x0, y0, z0, x1, y1, z1, mat='BV_Limestone', reveal_every=0.0, reveal_mat='BV_BronzeDark'):
    """Stone mass; optional shadow-gap reveals (thin dark recessed bands) on the -Y face every n metres (LOD0)."""
    acc.add(bm_box(x0, y0, z0, x1, y1, z1), mat if L < 2 else 'BV_StoneSmooth' if mat != 'BV_StoneDarkBase' else mat)
    if L == 0 and reveal_every:
        z = z0 + reveal_every
        while z < z1 - 0.2:
            acc.add(bm_box(x0 - 0.002, y0 - 0.004, z - 0.012, x1 + 0.002, y0 + 0.004, z + 0.012), reveal_mat)
            z += reveal_every


def pier(acc, L, x, w, y0, depth, z0, z1, mat='BV_Limestone', base_h=0.6, cap=True, flute=False):
    """Stone pier / pilaster with a dark granite plinth, optional capital band and vertical flutes."""
    acc.add(bm_box(x - w / 2 - 0.03, y0 - 0.03, z0, x + w / 2 + 0.03, y0 + depth, z0 + base_h), 'BV_StoneDarkBase')
    stone_box(acc, L, x - w / 2, y0, z0 + base_h, x + w / 2, y0 + depth, z1, mat)
    if cap and L < 2:
        acc.add(bm_box(x - w / 2 - 0.06, y0 - 0.06, z1 - 0.28, x + w / 2 + 0.06, y0 + depth, z1 - 0.2), 'BV_Bronze')
    if flute and L == 0:
        n = max(2, int(w / 0.18))
        for k in range(1, n):
            xx = x - w / 2 + k * w / n
            acc.add(bm_box(xx - 0.012, y0 - 0.01, z0 + base_h + 0.3, xx + 0.012, y0 + 0.01, z1 - 0.45), 'BV_StoneSmooth')


def canopy(acc, L, x0, x1, y_wall, depth, z, t=0.35, top='BV_BronzeDark', soffit='BV_BronzeDark', lights='PC_LightWarm', fascia=None,
           every=2.0):
    acc.add(bm_box(x0, y_wall - depth, z, x1, y_wall, z + t), top, mat_fn=mat_by_normal(top, soffit, fascia or top))
    if L < 2 and lights:
        AR.downlights(acc, L, [(x, y_wall - depth * 0.5) for x in np.arange(x0 + every / 2, x1, every)], z, 0.08, lights)


def recessed_portal(A, L, acc, x0, x1, y_face, recess, z_top, door_h, stone='BV_Limestone', frame='BV_BronzeDark',
                    glass='BV_Glass', sub='Portal', leaves=2, transom=True):
    """Deep recessed entrance bay: stone reveals (jambs + soffit), bronze-framed glazed screen at the back with doors."""
    yb = y_face + recess
    acc.add(bm_box(x0 - 0.35, y_face, 0.0, x0, yb, z_top), stone)            # left jamb (thickness into the opening)
    acc.add(bm_box(x1, y_face, 0.0, x1 + 0.35, yb, z_top), stone)            # right jamb
    acc.add(bm_box(x0 - 0.35, y_face, z_top, x1 + 0.35, yb, z_top + 0.4), stone,
            mat_fn=mat_by_normal(stone, 'BV_StoneSmooth', stone))           # soffit beam
    # bronze lining band around the opening (face)
    if L < 2:
        acc.add(bm_box(x0 - 0.06, y_face - 0.04, 0.0, x0, yb, z_top), frame)
        acc.add(bm_box(x1, y_face - 0.04, 0.0, x1 + 0.06, yb, z_top), frame)
        acc.add(bm_box(x0 - 0.06, y_face - 0.04, z_top - 0.06, x1 + 0.06, yb, z_top), frame)
        AR.downlights(acc, L, [((x0 + x1) / 2 + dx, y_face + recess * f) for dx in (-(x1 - x0) / 4, (x1 - x0) / 4) for f in (0.3, 0.7)],
                      z_top - 0.06, 0.07, 'PC_LightWarm')
    w = x1 - x0
    dw = min(w - 0.4, 2.6 if leaves == 2 else 1.4)
    AR.curtain(A, L, [(x0, yb), (x1, yb)], 0.0, z_top, w / max(1, round(w / 1.6)), [door_h] if transom else [], 0.06, 0.16,
               frame, glass, sub=sub, doors=[dict(seg=0, u0=(w - dw) / 2, u1=(w + dw) / 2, h=door_h, kind='pivot', leaves=leaves)])
    return yb


def rear_interface(A, L, x0, x1, y_back, z_top, up=1.2):
    """Rear structural connection wall + vertical upper boundary marker for docking against an existing tower."""
    ext = A.m(L, 'BUILDING_EXTERIOR', 'RearInterface')
    ext.add(bm_box(x0, y_back, 0.0, x1, y_back + 0.4, z_top + up), 'BV_Interface')
    if L == 0:
        e = A._empty(f'{A.prefix}_TOWER_INTERFACE', A.coll, A.root, 2.0)
        e.location = ((x0 + x1) / 2, y_back + 0.4, z_top)
        e['interface'] = 'rear vertical boundary plane (back face of the rear wall) + podium roof level'
        e['rear_plane_y_blender'] = round(y_back + 0.4, 3)
        e['podium_roof_z'] = round(z_top, 3)
        e['interface_top_z'] = round(z_top + up, 3)
        e['width_m'] = round(x1 - x0, 3)
        A.meta['tower_interface'] = dict(rear_plane_y=round(y_back + 0.4, 3), podium_roof_z=round(z_top, 3),
                                         top_z=round(z_top + up, 3), x=[x0, x1])


def roof_plant(A, L, x0, y0, x1, y1, z):
    """Podium roof finish: membrane + low screened plant enclosure (keeps the roof reading as a podium terrace)."""
    r = A.m(L, 'BUILDING_EXTERIOR', 'Roof')
    r.add(bm_hquad(x0, y0, x1, y1, z + 0.01), 'PC_RoofGravel')
    if L < 2:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + (y1 - y0) * 0.2
        r.add(bm_box(cx - 3.0, cy - 2.0, z, cx + 3.0, cy + 2.0, z + 1.6), 'PC_Corrugated')


def promenade(A, x0, x1, depth=PROM, entrances=(), steps=None):
    """Promenade paving strip in front of the building (PROMENADE_FRONTAGE, removable), flush with the threshold."""
    acc = A.s('PROMENADE_FRONTAGE', 'Paving')
    acc.add(bm_box(x0, -depth, -0.2, x1, 0.0, 0.0), 'BV_Paving', mat_fn=mat_by_normal('BV_Paving', 'BV_Paving', 'PC_Curb'), uv='box',
            tile=4.8)
    # granite threshold strip along the building line + entrance mats (inlaid bronze strips)
    acc.add(bm_box(x0, -0.6, 0.0, x1, 0.0, 0.012), 'BV_StoneDarkBase')
    for (a, b) in entrances:
        acc.add(bm_box(a, -2.4, 0.0, b, -0.6, 0.008), 'BV_StoneDarkBase')
        acc.add(bm_box(a - 0.05, -2.45, 0.0, b + 0.05, -2.4, 0.01), 'BV_Bronze')
    # kerb edge at the road side
    acc.add(bm_box(x0, -depth - 0.3, -0.35, x1, -depth, 0.0), 'PC_Curb')


def bollards(A, xs, y):
    acc = A.s('OPTIONAL_TERRACE', 'StreetFurniture')
    for x in xs:
        F.bollard(acc, 0, x, y, 0.0, 0.85, 0.09, 'BV_BronzeDark', 'PC_LightWarm')


def light_post(A, x, y, h=4.2):
    acc = A.s('OPTIONAL_TERRACE', 'StreetFurniture')
    acc.add(bm_cyl(x, y, 0.0, h, 0.07, 12), 'BV_BronzeDark')
    acc.add(bm_box(x - 0.18, y - 0.18, h, x + 0.18, y + 0.18, h + 0.12), 'BV_BronzeDark')
    acc.add(bm_box(x - 0.15, y - 0.15, h - 0.02, x + 0.15, y + 0.15, h), 'PC_LightWarm')


def bench(A, x, y, ang=0.0, length=2.2):
    F.bench(A.s('OPTIONAL_TERRACE', 'StreetFurniture'), 0, x, y, 0.0, ang, length, 'PC_Walnut', 'BV_StoneSmooth')


def planter(A, x0, y0, x1, y1, h=0.6):
    """EMPTY stone planter (no vegetation by design - the user's own planting assets go here)."""
    acc = A.s('OPTIONAL_TERRACE', 'EmptyPlanters')
    t = 0.12
    for (a, b, c, d) in ((x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1)):
        acc.add(bm_box(a, b, 0.0, c, d, h), 'BV_Limestone')
    acc.add(bm_hquad(x0 + t, y0 + t, x1 - t, y1 - t, h - 0.25), 'PC_RoofGravel')


def parasol(acc, L, x, y, z=0.0, r=1.4, h=2.5, mat='BV_Parasol', pole='BV_BronzeDark'):
    acc.add(bm_cyl(x, y, z, z + h, 0.03, 8), pole)
    seg = 8
    pts = [(x + r * math.cos(2 * math.pi * i / seg), y + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    bm = bmesh.new()
    apex = bm.verts.new((x, y, z + h + 0.35))
    rim = [bm.verts.new((px, py, z + h - 0.05)) for px, py in pts]
    for i in range(seg):
        bm.faces.new((apex, rim[i], rim[(i + 1) % seg]))
    apex2 = bm.verts.new((x, y, z + h + 0.33))
    rim2 = [bm.verts.new((px, py, z + h - 0.07)) for px, py in pts]
    for i in range(seg):
        bm.faces.new((apex2, rim2[(i + 1) % seg], rim2[i]))      # underside (separate skin, double sided)
    acc.add(bm, mat)


def terrace_deck(A, x0, y0, x1, y1, h=0.15, edge_rail=True, sub='Deck'):
    acc = A.s('OPTIONAL_TERRACE', sub)
    acc.add(bm_box(x0, y0, 0.0, x1, y1, h), 'BV_Deck', mat_fn=mat_by_normal('BV_Deck', 'BV_Deck', 'BV_BronzeDark'), uv='box', tile=1.4)
    if edge_rail:
        g = A.s('OPTIONAL_TERRACE', sub + 'Screen')
        for (p0, p1) in ((((x0, y0)), (x1, y0)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
            M, Ls = AR.seg_frame(p0, p1)
            g.add(bm_box(0, -0.02, h, Ls, 0.02, h + 0.9), 'BV_GlassWarm', matrix=M)
            g.add(bm_box(0, -0.03, h + 0.9, Ls, 0.03, h + 0.95), 'BV_BronzeDark', matrix=M)
    return acc


def sign_text(A, L, body, x, y, z, size, font='cinzel', front='BV_LetterBronze', side='BV_BronzeDark', depth=0.05, spacing=1.0,
              backing=None):
    """Individual channel letters on the stone fascia (faces softly self-lit so they stay legible at night)."""
    sg = A.m(L, 'SIGNAGE', 'Brand')
    if backing:
        bx, bz, bmat = backing
        sg.add(bm_box(x - bx / 2, y - 0.02, z - bz / 2, x + bx / 2, y + 0.01, z + bz / 2), bmat)
    txt(sg, L, body, place('-Y', Vector((x, y - 0.03, z))), size, depth, font, front, side, spacing=spacing, min_size_lod2=0.25)
    A.sign(body.lower().replace(' ', '_')[:24], (x, y - 0.05, z), size, width=len(body) * size * 0.75 * spacing)


# ---------------------------------------------------------------------------------------------- preview street (not exported)
def boulevard_env(A, x0, x1):
    """Boulevard-like preview: wide tiled promenade continues left/right, kerb, 3-lane boulevard carriageway, median."""
    acc = MeshAcc('PV_Street')
    MD.setdefault('PV_Ground', dict(base='#b49a78', rough=0.95))
    MD.setdefault('PV_Median', dict(base='#b8ab97', rough=0.9))
    acc.add(bm_hquad(-1500, -PROM, x0, 0.0, -0.002), 'BV_Paving', uv='box', tile=4.8)
    acc.add(bm_hquad(x1, -PROM, 1500, 0.0, -0.002), 'BV_Paving', uv='box', tile=4.8)
    acc.add(bm_box(-1500, -PROM - 0.3, -0.35, 1500, -PROM, -0.02), 'PC_Curb')
    acc.add(bm_hquad(-1500, -PROM - 11.0, 1500, -PROM - 0.3, -0.18), 'PC_Asphalt')
    acc.add(bm_box(-1500, -PROM - 14.0, -0.3, 1500, -PROM - 11.0, 0.0), 'PV_Median')
    acc.add(bm_hquad(-1500, -PROM - 25.0, 1500, -PROM - 14.0, -0.18), 'PC_Asphalt')
    acc.add(bm_hquad(-1500, -400, 1500, -PROM - 25.0, -0.2), 'PV_Ground')
    for yy, dash in ((-PROM - 0.6, False), (-PROM - 4.0, True), (-PROM - 7.4, True), (-PROM - 10.6, False),
                     (-PROM - 14.4, False), (-PROM - 17.8, True), (-PROM - 21.2, True), (-PROM - 24.6, False)):
        if dash:
            for k in range(-170, 170):
                acc.add(bm_hquad(k * 9.0, yy - 0.07, k * 9.0 + 3.0, yy + 0.07, -0.177), 'PC_LineWhite')
        else:
            acc.add(bm_hquad(-1500, yy - 0.08, 1500, yy + 0.08, -0.177), 'PC_LineWhite')
    # neighbouring podium frontage stubs (plain stone, low detail) so the asset reads in a continuous street wall
    fp = A.meta.get('footprint') or [x0, 0, x1, 30]
    MD.setdefault('PV_Neighbour', dict(base='#cdbfa6', rough=0.85))
    acc.add(bm_box(fp[0] - 40, 0.6, 0.0, fp[0] - 0.05, 30.0, 11.5), 'PV_Neighbour')
    if A.meta.get('corner') != 'right':
        acc.add(bm_box(fp[2] + 0.05, 0.6, 0.0, fp[2] + 40, 30.0, 11.5), 'PV_Neighbour')
    else:   # side street paving for the corner unit
        acc.add(bm_hquad(fp[2], 0.0, fp[2] + 40, 60.0, -0.002), 'BV_Paving', uv='box', tile=4.8)
    acc.add(bm_hquad(-1500, 0.0, 1500, 1500, -0.03), 'PV_Ground')
    acc.build(A.preview, None, weighted=False)
    R.set_world(bpy.context.scene, 'day')


def finish(A, x0, x1, unreal=True, **meta):
    """Finalize, preview env, save, export GLBs (+ Unreal FBX per LOD), write lod/build_stats.json."""
    A.meta.update(meta)
    A.meta['plot_x'] = [x0, x1]
    A.meta['light_counts'] = dict(A.light_count)
    stats = A.finalize()
    boulevard_env(A, x0, x1)
    blend, glb, bonly = A.save_and_export()
    tot = {k: sum(v.values()) for k, v in stats.items()}
    if unreal:
        export_unreal(A)
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
    json.dump(dict(parts=stats, totals=tot, meta=A.meta), open(f'{A.dir}/lod/build_stats.json', 'w'), indent=1)
    print('BUILD_OK', A.base, json.dumps(tot))
    return stats


def export_unreal(A):
    """FBX per LOD for Unreal Engine 5 (+ UCX_ collision copies in the LOD0 file). Z-up, metres (scale 1 = 1 m)."""
    d = os.path.join(A.dir, 'unreal')
    os.makedirs(d, exist_ok=True)
    cols = [o for o in A.group_coll['COLLISION'].all_objects if o.type == 'MESH']
    for L in (0, 1, 2):
        objs = [o for o in A.lod_coll[L].all_objects if o.type == 'MESH']
        ucx = []
        if L == 0:
            for i, c in enumerate(cols):
                u = c.copy(); u.data = c.data.copy()
                u.name = f'UCX_{A.prefix}_LOD0_{i:02d}'
                A.group_coll['COLLISION'].objects.link(u)
                u.parent = None; u.matrix_world = c.matrix_world.copy()
                ucx.append(u)
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs + ucx:
            o.hide_set(False); o.select_set(True)
        bpy.ops.export_scene.fbx(filepath=os.path.join(d, f'{A.base}_LOD{L}.fbx'), use_selection=True, apply_unit_scale=True,
                                 apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Y', axis_up='Z', use_mesh_modifiers=True,
                                 mesh_smooth_type='FACE', path_mode='RELATIVE', embed_textures=False, bake_space_transform=False,
                                 object_types={'MESH'}, add_leaf_bones=False)
        for u in ucx:
            bpy.data.objects.remove(u)
