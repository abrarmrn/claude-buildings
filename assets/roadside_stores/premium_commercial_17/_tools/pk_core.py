"""Premium Commercial 17 - core kit (asset container, collections, materials, textures, export).

Re-uses the earlier roadside libraries strictly READ-ONLY:
  prototypes/_tools/roadside_lib.py   (mesh accumulator, primitives, text, world, glTF report)
  additional_17/_tools/store_kit.py   (channel-letter text / sign panels, generic textures)
Nothing is written into those folders: byte-code writing is disabled and the texture cache is redirected here.

Conventions (same as the previous 20 stores, extended):
  * 1 Blender unit = 1 m, Z up.  Road-facing front = Blender -Y  (= glTF / Godot +Z).
  * Origin = centre of the plot frontage line (back edge of the public pavement), ground level.
    The building and its forecourt are at y >= 0, the pavement strip (SIDEWALK_FRONTAGE) at y < 0.
  * Exported node tree:
        <P>_<Title>                      root (extras: asset metadata)
          <P>_LOD0 / _LOD1 / _LOD2       geometry LODs (extras: lod_level + visibility range)
          <P>_SIDEWALK_FRONTAGE, <P>_OPTIONAL_FORECOURT, <P>_DRIVEWAY, <P>_OPTIONAL_PARKING   (site pieces)
          <P>_PLACEHOLDER_CARS           one object per generic car (removable)
          <P>_INTERIOR_LIGHTING / <P>_EXTERIOR_LIGHTING   KHR punctual lights
          <P>_Collision                  *-convcolonly boxes
"""
import os, sys, math, json, random, shutil
sys.dont_write_bytecode = True          # never create __pycache__ inside the protected earlier folders

HERE = os.path.dirname(os.path.abspath(__file__))
P17 = os.path.normpath(os.path.join(HERE, '..'))
STORES = os.path.normpath(os.path.join(P17, '..'))
sys.path.insert(0, os.path.join(STORES, 'prototypes', '_tools'))
sys.path.insert(0, os.path.join(STORES, 'additional_17', '_tools'))

import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import roadside_lib as R
import store_kit as K

K.TEXCACHE = os.path.join(HERE, 'texcache')          # redirect the shared texture cache away from additional_17
from roadside_lib import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_ring_prism, bm_hquad, bm_quad, bm_vquad,
                          bm_poly_flat, bm_sphere, bm_text, rounded_rect, place, front_back, bm_prism_local,
                          rect_subtract, hex_lin, MeshAcc, look_at)
from store_kit import txt, panel, disc, poly, FONT

FONT.update(
    xlight='/usr/share/fonts/opentype/inter/Inter-ExtraLight.otf',
    dlight='/usr/share/fonts/opentype/inter/InterDisplay-Light.otf',
    dmed='/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf',
    dsemi='/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf',
    dxbold='/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf',
    dblack='/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',
    xbold='/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf',
    serif_i='/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
)

COMPONENTS = ['BUILDING_EXTERIOR', 'BUILDING_INTERIOR', 'GLASS_SYSTEM', 'FACADE_DETAILS', 'SIGNAGE',
              'FURNITURE', 'DISPLAY_OBJECTS']
SITE_COMPONENTS = ['SIDEWALK_FRONTAGE', 'OPTIONAL_FORECOURT', 'DRIVEWAY', 'OPTIONAL_PARKING']
DEFAULT_LOD_RANGES = {0: (0.0, 90.0), 1: (90.0, 260.0), 2: (260.0, 1600.0)}
CAR_RANGE = (0.0, 340.0)
LOD_MARGIN = 8.0
TEX_N = 1024

# ---------------------------------------------------------------------------
# materials (PC_ = premium commercial).  All flat-colour or tiled procedural PBR, shared by name.
# ---------------------------------------------------------------------------
MD = R.MATERIAL_DEFS
MD.update({
    # glazing (alpha-blended, double-sided single panes -> Godot / UE friendly)
    'PC_Glass': dict(base='#1d2b31', rough=0.02, alpha=0.16, double=True, spec=1.0),
    'PC_GlassClear': dict(base='#2a383c', rough=0.02, alpha=0.11, double=True, spec=0.9),
    'PC_GlassRail': dict(base='#5f7c80', rough=0.02, alpha=0.14, double=True, spec=0.9),
    'PC_GlassSatin': dict(base='#c9d3d6', rough=0.35, alpha=0.55, double=True),
    'PC_GlassBlue': dict(base='#173040', rough=0.03, alpha=0.30, double=True, spec=1.0),
    # metals / frames
    'PC_AluSilver': dict(base='#b9bdc1', rough=0.30, metal=1.0),
    'PC_AluDark': dict(base='#2b2e31', rough=0.35, metal=0.9),
    'PC_AluBlack': dict(base='#121314', rough=0.32, metal=0.8),
    'PC_AluChampagne': dict(base='#b7a586', rough=0.30, metal=1.0),
    'PC_Bronze': dict(base='#8c6a43', rough=0.32, metal=1.0),
    'PC_Copper': dict(base='#b06f45', rough=0.28, metal=1.0),
    'PC_Brass': dict(base='#c9a65a', rough=0.25, metal=1.0),
    'PC_SteelDark': dict(base='#26292c', rough=0.45, metal=0.7),
    'PC_SteelPaintWhite': dict(base='#e9e9e6', rough=0.35, metal=0.1),
    'PC_SteelPaintGrey': dict(base='#5d6166', rough=0.45, metal=0.3),
    'PC_Chrome': dict(base='#dfe3e6', rough=0.08, metal=1.0),
    'PC_Stainless': dict(base='#a9adb0', rough=0.22, metal=1.0),
    # cladding
    'PC_PanelWhite': dict(base='#f1f1ee', rough=0.22, metal=0.05),
    'PC_PanelPearl': dict(base='#ece7de', rough=0.25, metal=0.15),
    'PC_PanelSilver': dict(base='#a7abae', rough=0.28, metal=0.8),
    'PC_PanelGraphite': dict(base='#3a3d40', rough=0.32, metal=0.6),
    'PC_PanelBlack': dict(base='#151617', rough=0.28, metal=0.5),
    'PC_ConcreteWhite': dict(base='#dcd9d2', rough=0.7),
    'PC_Concrete': dict(base='#ffffff', tex='concrete', tile=3.0),
    'PC_Travertine': dict(base='#ffffff', tex='travertine', tile=2.4),
    'PC_StoneLime': dict(base='#ffffff', tex='pc_stonelime', tile=(3.6, 1.8)),
    'PC_StoneDark': dict(base='#ffffff', tex='pc_granite', tile=2.0),
    'PC_StoneSand': dict(base='#ffffff', tex='pc_stonesand', tile=(2.4, 1.2)),
    'PC_WoodSlat': dict(base='#ffffff', tex='woodv', tile=1.0),
    'PC_TimberDark': dict(base='#3b2a1f', rough=0.55),
    'PC_Corrugated': dict(base='#ffffff', tex='pc_corrugated', tile=1.2),
    'PC_RoofMembrane': dict(base='#9b9893', rough=0.85),
    'PC_RoofGravel': dict(base='#ffffff', tex='gravel', tile=1.0),
    # site
    'PC_Asphalt': dict(base='#ffffff', tex='asphalt', tile=4.0),
    'PC_Paver': dict(base='#ffffff', tex='paver', tile=2.4),
    'PC_PaverLight': dict(base='#ffffff', tex='pc_paverlight', tile=(1.2, 1.2)),
    'PC_Curb': dict(base='#c9c6bf', rough=0.75),
    'PC_LineWhite': dict(base='#e6e6df', rough=0.7),
    'PC_LineYellow': dict(base='#e3b30c', rough=0.65),
    'PC_GroundGreen': dict(base='#4f6a37', rough=0.95),
    'PC_Water': dict(base='#0e2a33', rough=0.04, metal=0.0, spec=1.0),
    # interior finishes
    'PC_FloorDark': dict(base='#ffffff', tex='pc_granite', tile=2.0),
    'PC_FloorMarble': dict(base='#ffffff', tex='pc_marble', tile=2.4),
    'PC_FloorTerrazzo': dict(base='#ffffff', tex='pc_terrazzo', tile=1.6),
    'PC_FloorOak': dict(base='#ffffff', tex='pc_oak', tile=2.0),
    'PC_FloorEpoxy': dict(base='#7d8287', rough=0.32),
    'PC_FloorEpoxyDark': dict(base='#3c4045', rough=0.3),
    'PC_FloorTileWet': dict(base='#ffffff', tex='tilefloor', tile=1.2),
    'PC_Ceiling': dict(base='#f0efec', rough=0.85),
    'PC_CeilingDark': dict(base='#2a2b2d', rough=0.8),
    'PC_WallWhite': dict(base='#ecebe7', rough=0.75),
    'PC_WallWarm': dict(base='#e3d6c3', rough=0.75),
    'PC_WallDark': dict(base='#2e2f31', rough=0.6),
    'PC_SlabEdge': dict(base='#d9d8d3', rough=0.6),
    'PC_Leather': dict(base='#7a4a2c', rough=0.45),
    'PC_LeatherBlack': dict(base='#1b1b1c', rough=0.4),
    'PC_LeatherCream': dict(base='#d8cbb4', rough=0.5),
    'PC_FabricGrey': dict(base='#6d6f72', rough=0.95),
    'PC_FabricCream': dict(base='#d9d0bf', rough=0.95),
    'PC_FabricTeal': dict(base='#2f5b5d', rough=0.95),
    'PC_FabricRust': dict(base='#9a4b2c', rough=0.95),
    'PC_FabricNavy': dict(base='#1f2a44', rough=0.95),
    'PC_Walnut': dict(base='#ffffff', tex='wood', tile=1.0),
    'PC_WoodLight': dict(base='#c8a77e', rough=0.5),
    'PC_StoneTop': dict(base='#e6e1d8', rough=0.25),
    'PC_BlackGloss': dict(base='#0c0c0d', rough=0.12, metal=0.2),
    'PC_WhiteGloss': dict(base='#f4f4f2', rough=0.12),
    'PC_RubberBlack': dict(base='#141414', rough=0.85),
    'PC_PlasticGrey': dict(base='#8a8d90', rough=0.5),
    'PC_PlasticWhite': dict(base='#e8e8e6', rough=0.4),
    'PC_DeviceBlack': dict(base='#0d0e10', rough=0.2, metal=0.4),
    'PC_DeviceSilver': dict(base='#c3c6c9', rough=0.25, metal=1.0),
    # emissive (cheap decorative light; real lamps only for important fixtures)
    'PC_LightPanel': dict(base='#ffffff', rough=0.3, emit='#fff7ee', es=9.0),
    'PC_LightCool': dict(base='#ffffff', rough=0.3, emit='#eef4ff', es=9.0),
    'PC_LightWarm': dict(base='#ffffff', rough=0.3, emit='#ffd8a6', es=8.0),
    'PC_LightStrip': dict(base='#ffffff', rough=0.3, emit='#fff1df', es=14.0),
    'PC_LampGlobe': dict(base='#fff4e6', rough=0.3, emit='#ffd9ad', es=7.0),
    'PC_LEDBlue': dict(base='#2a6cff', rough=0.3, emit='#2f78ff', es=10.0),
    'PC_LEDCyan': dict(base='#29d4ff', rough=0.3, emit='#30d8ff', es=10.0),
    'PC_LEDOrange': dict(base='#ff6a00', rough=0.3, emit='#ff6a00', es=9.0),
    'PC_LEDMagenta': dict(base='#ff2a8a', rough=0.3, emit='#ff2a8a', es=9.0),
    'PC_LEDRed': dict(base='#e01020', rough=0.3, emit='#ff1a22', es=9.0),
    'PC_LEDWhite': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=12.0),
    'PC_Fire': dict(base='#ff7a1a', rough=0.6, emit='#ff6a12', es=18.0),
    # cars (neutral placeholders)
    'PC_CarPaintWhite': dict(base='#e6e7e6', rough=0.18, metal=0.35, spec=0.8),
    'PC_CarPaintSilver': dict(base='#a7acb0', rough=0.22, metal=0.85),
    'PC_CarPaintBlack': dict(base='#0f1012', rough=0.16, metal=0.55),
    'PC_CarPaintGraphite': dict(base='#45494e', rough=0.2, metal=0.75),
    'PC_CarPaintBlue': dict(base='#1d3557', rough=0.2, metal=0.7),
    'PC_CarPaintRed': dict(base='#8f1820', rough=0.2, metal=0.6),
    'PC_CarPaintSand': dict(base='#a8987c', rough=0.22, metal=0.7),
    'PC_CarPaintGreen': dict(base='#2e4639', rough=0.2, metal=0.7),
    'PC_CarPaintYellow': dict(base='#d8a51c', rough=0.2, metal=0.5),
    'PC_CarPaintOrange': dict(base='#d0551c', rough=0.2, metal=0.5),
    'PC_CarWrapMatte': dict(base='#2c6e6a', rough=0.55, metal=0.2),
    'PC_CarGlass': dict(base='#0b1013', rough=0.04, metal=0.3, spec=1.0),
    'PC_CarTrim': dict(base='#0c0c0d', rough=0.25, metal=0.3),
    'PC_Tyre': dict(base='#151515', rough=0.8),
    'PC_Rim': dict(base='#b8bcc0', rough=0.2, metal=1.0),
    'PC_RimDark': dict(base='#2a2c2e', rough=0.25, metal=0.9),
    'PC_HeadLight': dict(base='#e9f1ff', rough=0.1, emit='#eef4ff', es=4.0),
    'PC_TailLight': dict(base='#5a0508', rough=0.15, emit='#ff1010', es=2.5),
    # equipment
    'PC_ToolRed': dict(base='#a3161c', rough=0.3, metal=0.4),
    'PC_ToolBlack': dict(base='#1a1b1d', rough=0.35, metal=0.5),
    'PC_LiftYellow': dict(base='#d9a514', rough=0.4, metal=0.3),
    'PC_LiftBlue': dict(base='#1f4f9a', rough=0.4, metal=0.3),
    'PC_BrushBlue': dict(base='#2a63c9', rough=0.95),
    'PC_BrushRed': dict(base='#c4283a', rough=0.95),
    'PC_Grate': dict(base='#2c2e30', rough=0.5, metal=0.8),
})


def defmat(name, base, rough=0.4, metal=0.0, emit=None, es=1.0, **kw):
    d = dict(base=base, rough=rough, metal=metal, **kw)
    if emit:
        d.update(emit=emit, es=es)
    MD[name] = d
    return name


# ---------------------------------------------------------------------------
# procedural textures (generated once into _tools/texcache, copied into each asset's textures/)
# ---------------------------------------------------------------------------
def _fft(n, beta, seed, aniso=(1.0, 1.0)):
    return R._fft_noise(n, beta, seed, aniso)


def _save3(col, rough, h, key, d, nstr=1.0, metal=None):
    R._save(np.clip(col, 0, 1), f'{d}/{key}_albedo.png')
    R._save(R._orm(rough, metal), f'{d}/{key}_orm.png')
    if h is not None:
        R._save(R._normal_from_height(h, nstr), f'{d}/{key}_normal.png')


def tex_stonelime(d, n=TEX_N, key='pc_stonelime', tone=(0.86, 0.82, 0.74), seed=11):
    # large-format limestone cladding: one tile = 2 x 2 panels of 1.8 x 0.9 m with 8 mm open joints
    ys, xs = np.mgrid[0:n, 0:n] / n
    pu, pv = (xs * 2) % 1.0, (ys * 2) % 1.0
    jx = np.minimum(pu, 1 - pu) * 1.8; jy = np.minimum(pv, 1 - pv) * 0.9
    joint = np.clip((np.minimum(jx, jy) - 0.004) / 0.003, 0, 1)
    pid = (np.floor(xs * 2) + 2 * np.floor(ys * 2)).astype(int)
    rng = np.random.default_rng(seed); ptone = rng.normal(0, 0.035, 4)[pid]
    noise = _fft(n, 1.1, seed + 1); fine = _fft(n, 0.3, seed + 2)
    strata = _fft(n, 1.6, seed + 3, aniso=(0.12, 1.0))
    base = np.array(tone)[None, None] * (1 + ptone[..., None] + 0.05 * noise[..., None] + 0.03 * fine[..., None] + 0.04 * strata[..., None])
    col = base * (0.35 + 0.65 * joint[..., None])
    rough = np.clip(0.62 + 0.06 * fine + (1 - joint) * 0.2, 0, 1)
    _save3(col, rough, joint * 2.0 + 0.05 * fine, key, d, 1.0)


def tex_stonesand(d):
    tex_stonelime(d, key='pc_stonesand', tone=(0.80, 0.68, 0.52), seed=21)


def tex_granite(d, n=TEX_N):
    # polished dark granite / porcelain floor, 1.0 m tiles (2 x 2 per texture tile of 2 m)
    ys, xs = np.mgrid[0:n, 0:n] / n
    pu, pv = (xs * 2) % 1.0, (ys * 2) % 1.0
    e = np.minimum(np.minimum(pu, 1 - pu), np.minimum(pv, 1 - pv))
    joint = np.clip((e - 0.0018) / 0.0015, 0, 1)
    rng = np.random.default_rng(5)
    speck = (rng.random((n, n)) > 0.985).astype(float) * rng.random((n, n))
    speck = np.array(Image.fromarray((speck * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))) / 255.0
    noise = _fft(n, 1.0, 6)
    base = np.array([0.075, 0.075, 0.08])[None, None] * (1 + 0.25 * noise[..., None]) + speck[..., None] * 0.35
    col = base * (0.6 + 0.4 * joint[..., None])
    rough = np.clip(0.12 + 0.04 * noise + (1 - joint) * 0.4, 0, 1)
    _save3(col, rough, joint * 0.6, 'pc_granite', d, 0.6)


def tex_marble(d, n=TEX_N):
    ys, xs = np.mgrid[0:n, 0:n] / n
    pu, pv = (xs * 2) % 1.0, (ys * 2) % 1.0
    e = np.minimum(np.minimum(pu, 1 - pu), np.minimum(pv, 1 - pv))
    joint = np.clip((e - 0.0015) / 0.0015, 0, 1)
    turb = _fft(n, 1.3, 31) * 3.0 + _fft(n, 0.6, 32) * 0.8
    vein = np.abs(np.sin((xs * 3.0 + ys * 1.6) * math.pi * 2 + turb * 2.2))
    vein = np.clip(1 - vein / 0.07, 0, 1) ** 1.5
    fine = _fft(n, 0.3, 33)
    base = np.array([0.90, 0.89, 0.86])[None, None] * (1 + 0.02 * fine[..., None]) - vein[..., None] * np.array([0.32, 0.33, 0.33])
    col = base * (0.75 + 0.25 * joint[..., None])
    rough = np.clip(0.1 + 0.03 * fine + (1 - joint) * 0.3, 0, 1)
    _save3(col, rough, joint * 0.5, 'pc_marble', d, 0.5)


def tex_terrazzo(d, n=TEX_N):
    rng = np.random.default_rng(41)
    img = Image.new('RGB', (n, n), (214, 208, 198)); dr = ImageDraw.Draw(img)
    pal = [(150, 140, 128), (90, 86, 82), (232, 228, 220), (176, 150, 120), (60, 60, 62)]
    for _ in range(int(n * n / 260)):
        x, y = rng.integers(0, n, 2); r = int(rng.integers(1, 6))
        c = pal[int(rng.integers(0, len(pal)))]
        dr.ellipse([x - r, y - r, x + r, y + r], fill=c)
    col = np.array(img) / 255.0
    col = (col ** 2.2)                 # stored as linear-ish -> R._save expects 0-1 sRGB-ish values; keep mid tones
    col = np.array(img) / 255.0
    noise = _fft(n, 1.0, 42)
    rough = np.clip(0.2 + 0.05 * noise, 0, 1)
    _save3(col * (1 + 0.03 * noise[..., None]), rough, None, 'pc_terrazzo', d)


def tex_oak(d, n=TEX_N):
    # 0.2 m wide oak planks, 2 m tile; staggered butt joints
    ys, xs = np.mgrid[0:n, 0:n] / n
    rows = xs * 10.0; r = np.floor(rows).astype(int)
    off = (r * 0.37) % 1.0
    along = (ys + off) % 1.0
    fu = rows - r
    gap = np.clip((np.minimum(fu, 1 - fu) * 0.2 - 0.0012) / 0.001, 0, 1) * np.clip((np.minimum(along, 1 - along) * 2.0 - 0.002) / 0.002, 0, 1)
    grain = _fft(n, 1.8, 51, aniso=(1.0, 0.05)) * 1.2 + _fft(n, 0.5, 52) * 0.3
    rng = np.random.default_rng(53); ptone = rng.normal(0, 0.06, 64)[r % 64]
    base = np.array([0.62, 0.45, 0.30])[None, None] * (1 + ptone[..., None] + 0.08 * grain[..., None])
    col = base * (0.45 + 0.55 * gap[..., None])
    rough = np.clip(0.45 + 0.05 * grain + (1 - gap) * 0.3, 0, 1)
    _save3(col, rough, gap * 0.8 + 0.05 * grain, 'pc_oak', d, 0.6)


def tex_corrugated(d, n=512):
    # dark grey trapezoidal profiled cladding, ribs every 0.2 m (vertical), tile 1.2 m
    ys, xs = np.mgrid[0:n, 0:n] / n
    ph = (xs * 6.0) % 1.0
    prof = np.clip(np.abs(ph - 0.5) * 4 - 0.6, 0, 1)
    noise = _fft(n, 1.2, 61)
    col = np.array([0.24, 0.25, 0.26])[None, None] * (1 + 0.05 * noise[..., None] + 0.12 * prof[..., None])
    rough = np.clip(0.42 + 0.04 * noise, 0, 1)
    metal = np.full_like(rough, 0.6)
    _save3(col, rough, prof * 1.5, 'pc_corrugated', d, 2.0, metal)


def tex_paverlight(d, n=512):
    # light grey 0.6 x 0.3 m sidewalk pavers
    ys, xs = np.mgrid[0:n, 0:n] / n
    rows = ys * 4.0; r = np.floor(rows).astype(int)
    cols = xs * 2.0 + 0.5 * (r % 2); c = np.floor(cols).astype(int)
    fu, fv = cols - c, rows - r
    e = np.minimum(np.minimum(fu, 1 - fu) * 0.6, np.minimum(fv, 1 - fv) * 0.3)
    joint = np.clip((e - 0.003) / 0.002, 0, 1)
    rng = np.random.default_rng(71); tone = rng.normal(0, 0.03, (4, 3))[r % 4, c % 3]
    noise = _fft(n, 1.0, 72)
    col = np.array([0.70, 0.69, 0.66])[None, None] * (1 + tone[..., None] + 0.04 * noise[..., None]) * (0.6 + 0.4 * joint[..., None])
    rough = np.clip(0.8 + 0.05 * noise, 0, 1)
    _save3(col, rough, joint, 'pc_paverlight', d, 1.0)


for _k, _f in dict(pc_stonelime=tex_stonelime, pc_stonesand=tex_stonesand, pc_granite=tex_granite, pc_marble=tex_marble,
                   pc_terrazzo=tex_terrazzo, pc_oak=tex_oak, pc_corrugated=tex_corrugated,
                   pc_paverlight=tex_paverlight).items():
    R.EXTRA_TEXTURES[_k] = _f


# --- special image materials (alpha screens, emissive content, logos) ------------------------------------------------
def _img_path(name):
    os.makedirs(K.TEXCACHE, exist_ok=True)
    return os.path.join(K.TEXCACHE, name)


def screen_atlas():
    """4 x 2 atlas of abstract display content (TV walls, phones, laptops, signage screens). sRGB PNG 1024x512."""
    p = _img_path('pc_screen_atlas.png')
    if os.path.exists(p):
        return p
    W, H = 1024, 512; img = Image.new('RGB', (W, H)); dr = ImageDraw.Draw(img)
    rng = np.random.default_rng(3)
    pals = [((10, 40, 120), (60, 170, 255)), ((90, 20, 110), (255, 120, 60)), ((5, 70, 70), (90, 240, 200)),
            ((20, 20, 30), (250, 250, 255)), ((120, 30, 20), (255, 200, 80)), ((10, 30, 60), (120, 90, 255)),
            ((30, 80, 30), (200, 255, 140)), ((60, 60, 70), (255, 255, 255))]
    for i in range(8):
        cx, cy = (i % 4) * 256, (i // 4) * 256
        a, b = pals[i]
        ys, xs = np.mgrid[0:256, 0:256] / 256.0
        t = np.clip(0.5 + 0.5 * np.sin(xs * (2 + i) + ys * 3 + i) * np.cos(ys * 2.5 - i), 0, 1)
        arr = (np.array(a)[None, None] * (1 - t[..., None]) + np.array(b)[None, None] * t[..., None]).astype(np.uint8)
        tile = Image.fromarray(arr); td = ImageDraw.Draw(tile)
        for k in range(5):
            r = int(rng.integers(20, 90)); x, y = rng.integers(0, 256, 2)
            td.ellipse([x - r, y - r, x + r, y + r], outline=tuple(int(v) for v in b), width=3)
        td.rectangle([18, 200, 140, 214], fill=(255, 255, 255)); td.rectangle([18, 222, 96, 230], fill=(220, 220, 230))
        img.paste(tile.filter(ImageFilter.GaussianBlur(0.8)), (cx, cy))
    img.save(p)
    return p


def mashrabiya_png(name='pc_mashrabiya.png', n=512, motif='star'):
    """Geometric lattice screen with real alpha (alpha-clip in glTF). One tile = 0.6 m."""
    p = _img_path(name)
    if os.path.exists(p):
        return p
    ys, xs = np.mgrid[0:n, 0:n] / n * 2.0     # 2 x 2 motifs per tile
    u, v = (xs % 1.0) - 0.5, (ys % 1.0) - 0.5
    rr = np.sqrt(u * u + v * v); a = np.arctan2(v, u)
    if motif == 'star':
        star = 0.30 + 0.07 * np.cos(8 * a)
        hole = (rr < star) & (rr > 0.07)
        diag = (np.abs(np.abs(u) - np.abs(v)) < 0.035)
        edge = (np.abs(u) > 0.47) | (np.abs(v) > 0.47)
        solid = ~hole | diag | edge
    else:   # 'lattice' - Asian vertical/horizontal lattice
        solid = (np.abs(u) < 0.05) | (np.abs(v) < 0.05) | (np.abs(np.abs(u) - 0.25) < 0.03) & (np.abs(v) < 0.25)
    rgba = np.zeros((n, n, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = np.where(solid, 255, 0)
    Image.fromarray(rgba, 'RGBA').save(p)
    return p


def _new_mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m, None
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree


def _copy_into_asset(path):
    """Copy a cached image into the current asset's textures/ folder and load it from there (relative paths in .blend)."""
    dst = os.path.join(R.Ctx.tex_dir, os.path.basename(path))
    if not os.path.exists(dst):
        shutil.copy(path, dst)
    return bpy.data.images.load(dst, check_existing=True)


def mat_alpha_screen(name, png, colour, rough=0.4, metal=0.8, tile=0.6):
    m, nt = _new_mat(name)
    if nt is None:
        return name
    b = nt.nodes['Principled BSDF']
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = _copy_into_asset(png)
    b.inputs['Base Color'].default_value = hex_lin(colour)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    nt.links.new(im.outputs['Alpha'], b.inputs['Alpha'])
    try:
        m.blend_method = 'CLIP'; m.alpha_threshold = 0.5
    except Exception:
        pass
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    m.use_backface_culling = False
    MD[name] = dict(base=colour, tile=tile)
    return name


def mat_image_emissive(name, png, strength=3.0, rough=0.2, tile=1.0):
    m, nt = _new_mat(name)
    if nt is None:
        return name
    b = nt.nodes['Principled BSDF']
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = _copy_into_asset(png)
    nt.links.new(im.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(im.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = strength
    b.inputs['Roughness'].default_value = rough
    MD[name] = dict(base='#808080', tile=tile)
    return name


def mat_logo(name, png, strength=4.0, colour=None):
    """Emissive logo decal with alpha clip (illuminated sign graphics)."""
    m, nt = _new_mat(name)
    if nt is None:
        return name
    b = nt.nodes['Principled BSDF']
    im = nt.nodes.new('ShaderNodeTexImage'); im.image = _copy_into_asset(png)
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
    MD[name] = dict(base='#ffffff', tile=1.0)
    return name


SPECIAL_MATS = {
    'PC_Screen': lambda: mat_image_emissive('PC_Screen', screen_atlas(), 2.2, tile=1.0),
    'PC_Mashrabiya': lambda: mat_alpha_screen('PC_Mashrabiya', mashrabiya_png(), '#8c6a43', 0.35, 1.0, 1.2),
    'PC_MashrabiyaWhite': lambda: mat_alpha_screen('PC_MashrabiyaWhite', mashrabiya_png(), '#ece7de', 0.4, 0.1, 1.2),
    'PC_LatticeTimber': lambda: mat_alpha_screen('PC_LatticeTimber', mashrabiya_png('pc_lattice.png', motif='lattice'), '#3b2a1f', 0.55, 0.0, 1.0),
}


# ---------------------------------------------------------------------------
# asset container
# ---------------------------------------------------------------------------
class PAsset:
    def __init__(self, num, folder, base, prefix, title, display, floors, lod_ranges=None):
        self.num, self.folder, self.base, self.prefix, self.title, self.display = num, folder, base, prefix, title, display
        self.floors = floors
        self.lod_ranges = lod_ranges or DEFAULT_LOD_RANGES
        self.dir = f'{P17}/{folder}'
        self.tex_dir = f'{self.dir}/textures'
        for sub in ('textures', 'lod', 'renders'):
            os.makedirs(f'{self.dir}/{sub}', exist_ok=True)
        open(f'{self.tex_dir}/.gdignore', 'w').close()
        open(f'{self.dir}/renders/.gdignore', 'w').close()
        R.Ctx.tex_dir = self.tex_dir
        R.reset_scene()
        sc = bpy.context.scene
        self.sc = sc
        self.coll = bpy.data.collections.new(f'{prefix}_{title}')
        sc.collection.children.link(self.coll)
        self.root = self._empty(f'{prefix}_{title}', self.coll, None, 4.0)
        self.root['asset_id'] = base
        self.root['display_name'] = display
        self.root['front_axis_blender'] = '-Y'
        self.root['front_axis_gltf'] = '+Z'
        self.root['units'] = 'metres'
        self.root['origin'] = 'centre of plot frontage line (back of pavement), ground level'
        self.root['floors'] = floors
        # LOD collections + nodes
        self.lod_coll, self.lod_root, self.comp_coll = {}, {}, {}
        for L in (0, 1, 2):
            c = bpy.data.collections.new(f'LOD{L}')
            self.coll.children.link(c)
            self.lod_coll[L] = c
            e = self._empty(f'{prefix}_LOD{L}', c, self.root)
            b, en = self.lod_ranges[L]
            e['lod_level'] = L
            e['visibility_range_begin'] = b
            e['visibility_range_end'] = en
            e['visibility_range_margin'] = LOD_MARGIN
            self.lod_root[L] = e
        # site / cars / lights / collision
        self.group_coll, self.group_root = {}, {}
        for g in SITE_COMPONENTS + ['PLACEHOLDER_CARS', 'INTERIOR_LIGHTING', 'EXTERIOR_LIGHTING', 'COLLISION']:
            c = bpy.data.collections.new(g)
            self.coll.children.link(c)
            self.group_coll[g] = c
            nm = f'{prefix}_Collision' if g == 'COLLISION' else f'{prefix}_{g}'
            self.group_root[g] = self._empty(nm, c, self.root)
        cr = self.group_root['PLACEHOLDER_CARS']
        cr['placeholder'] = True
        cr['note'] = 'Generic placeholder vehicles - delete this node (or the PLACEHOLDER_CARS collection) to remove all cars.'
        cr['lod_level'] = 0
        cr['visibility_range_begin'] = CAR_RANGE[0]
        cr['visibility_range_end'] = CAR_RANGE[1]
        cr['visibility_range_margin'] = LOD_MARGIN
        self.group_root['INTERIOR_LIGHTING']['godot_group'] = 'premium_interior_lights'
        self.group_root['EXTERIOR_LIGHTING']['godot_group'] = 'premium_exterior_night_lights'
        for g in SITE_COMPONENTS:
            self.group_root[g]['optional'] = g.startswith('OPTIONAL')
        self.preview = bpy.data.collections.new('_PREVIEW_NOT_EXPORTED')
        sc.collection.children.link(self.preview)
        self.parts, self.site_parts = {}, {}
        self.cameras, self.signs, self.cars, self.checks = {}, [], [], {}
        self.meta = dict(floors=floors)
        self.light_count = {'INTERIOR_LIGHTING': 0, 'EXTERIOR_LIGHTING': 0}

    def _empty(self, name, coll, parent, size=1.0):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = size
        coll.objects.link(e)
        e.parent = parent
        return e

    # geometry accumulators -----------------------------------------------------------
    def m(self, L, comp, sub='Main'):
        """Mesh accumulator for LOD L, component comp (one of COMPONENTS), sub-part name."""
        assert comp in COMPONENTS, comp
        key = (L, comp, sub)
        if key not in self.parts:
            self.parts[key] = MeshAcc(f'{self.prefix}_LOD{L}_{comp}_{sub}')
        return self.parts[key]

    def s(self, comp, sub='Main'):
        assert comp in SITE_COMPONENTS, comp
        key = (comp, sub)
        if key not in self.site_parts:
            self.site_parts[key] = MeshAcc(f'{self.prefix}_{comp}_{sub}')
        return self.site_parts[key]

    def col_box(self, name, x0, y0, z0, x1, y1, z1):
        bm = bm_box(x0, y0, z0, x1, y1, z1)
        me = bpy.data.meshes.new(f'{self.prefix}_COL_{name}')
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f'{self.prefix}_COL_{name}-convcolonly', me)
        self.group_coll['COLLISION'].objects.link(ob)
        ob.parent = self.group_root['COLLISION']
        ob.display_type = 'WIRE'
        ob.hide_render = True
        return ob

    def light(self, group, name, kind, loc, energy, color='#fff2e0', rot=(0, 0, 0), spot_deg=110, blend=0.6,
              radius=0.25, shadow=False, size=None):
        assert group in ('INTERIOR_LIGHTING', 'EXTERIOR_LIGHTING')
        ld = bpy.data.lights.new(f'{self.prefix}_{name}', kind)
        ld.energy = energy
        ld.color = hex_lin(color)[:3]
        if kind == 'SPOT':
            ld.spot_size = math.radians(spot_deg); ld.spot_blend = blend
        if kind == 'AREA':
            ld.size = size or 1.0
        ld.shadow_soft_size = radius
        ld.use_shadow = shadow
        try:
            ld.cycles.cast_shadow = shadow
        except Exception:
            pass
        ob = bpy.data.objects.new(f'{self.prefix}_{name}', ld)
        ob.location = loc
        ob.rotation_euler = [math.radians(a) for a in rot]
        self.group_coll[group].objects.link(ob)
        ob.parent = self.group_root[group]
        self.light_count[group] += 1
        return ob

    def camera(self, key, loc, target, lens=30):
        self.cameras[key] = dict(loc=list(loc), target=list(target), lens=lens)

    def sign(self, name, center, cap_h, normal=(0, -1, 0), width=2.0):
        self.signs.append(dict(name=name, center=list(center), cap_height=cap_h, normal=list(normal), width=width))

    # ---------------------------------------------------------------------------------
    def finalize(self):
        stats = {}
        used = set(m for acc in list(self.parts.values()) + list(self.site_parts.values()) for m in acc.mats)
        for name, fn in SPECIAL_MATS.items():
            if name in used and bpy.data.materials.get(name) is None:
                fn()
        for (L, comp, sub), acc in sorted(self.parts.items()):
            cname = comp if L == 0 else f'LOD{L}_{comp}'
            c = self.comp_coll.get(cname)
            if c is None:
                c = bpy.data.collections.new(cname)
                self.lod_coll[L].children.link(c)
                self.comp_coll[cname] = c
            ob = acc.build(c, self.lod_root[L])
            if ob:
                stats.setdefault(f'LOD{L}', {})[f'{comp}/{sub}'] = acc.tris()
        for (comp, sub), acc in sorted(self.site_parts.items()):
            ob = acc.build(self.group_coll[comp], self.group_root[comp], weighted=False)
            if ob:
                stats.setdefault('SITE', {})[f'{comp}/{sub}'] = acc.tris()
        # drop empty site groups from the export tree
        for g in SITE_COMPONENTS:
            if not self.group_root[g].children:
                self.group_root[g]['empty'] = True
        self.root['preview_cameras'] = json.dumps(self.cameras)
        self.root['brand_signs'] = json.dumps(self.signs)
        self.root['meta'] = json.dumps(self.meta)
        self.root['placeholder_cars'] = json.dumps(self.cars)
        self.root['checks'] = json.dumps(self.checks)
        self.stats = stats
        return stats

    def _export(self, path, objs, textures=True, lights=True):
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objs:
            ob.hide_set(False)
            ob.select_set(True)
        bpy.context.view_layer.objects.active = self.root
        return bpy.ops.export_scene.gltf(
            filepath=path, export_format='GLB', use_selection=True, export_extras=True,
            export_lights=lights, export_cameras=False, export_apply=True, export_yup=True,
            export_texcoords=True, export_normals=True, export_tangents=False,
            export_materials='EXPORT', export_image_format='AUTO' if textures else 'NONE',
            export_animations=False, export_import_convert_lighting_mode='SPEC')

    def save_and_export(self):
        blend = f'{self.dir}/{self.base}.blend'
        glb = f'{self.dir}/{self.base}.glb'
        bonly = f'{self.dir}/{self.base}_building_only.glb'
        # remove empty site groups before export (kept as collections for editing)
        for g in SITE_COMPONENTS:
            e = self.group_root[g]
            if e.get('empty'):
                bpy.data.objects.remove(e)
                self.group_root[g] = None
        has_cars = bool([o for o in self.group_coll['PLACEHOLDER_CARS'].all_objects if o.type == 'MESH'])
        if not has_cars:
            bpy.data.objects.remove(self.group_root['PLACEHOLDER_CARS'])
            for p in (bonly, f'{self.dir}/lod/{self.base}_placeholder_cars.glb'):
                if os.path.exists(p):
                    os.remove(p)
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        allobjs = list(self.coll.all_objects)
        cars = set(self.group_coll['PLACEHOLDER_CARS'].all_objects)
        self._export(glb, allobjs)
        if has_cars:
            self._export(bonly, [o for o in allobjs if o not in cars])
        for L in (0, 1, 2):
            objs = [self.root, self.lod_root[L]] + list(self.lod_coll[L].all_objects)
            self._export(f'{self.dir}/lod/{self.base}_lod{L}.glb', objs, textures=False, lights=False)
        if has_cars:
            self._export(f'{self.dir}/lod/{self.base}_placeholder_cars.glb',
                         [self.root, self.group_root['PLACEHOLDER_CARS']] + list(cars), textures=False, lights=False)
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True, relative_remap=True)
        return blend, glb, bonly


# ---------------------------------------------------------------------------
# small geometry utilities
# ---------------------------------------------------------------------------
def rotz(ang_deg, origin=(0, 0, 0)):
    return Matrix.Translation(Vector(origin)) @ Matrix.Rotation(math.radians(ang_deg), 4, 'Z')


def seg_frame(p0, p1, z=0.0):
    """Matrix for a local frame on segment p0->p1: local X along the segment, local Y = left normal (inside for CCW
    outlines), Z up. Returns (matrix, length)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    return Matrix.Translation((p0[0], p0[1], z)) @ Matrix.Rotation(a, 4, 'Z'), L


def arc_pts(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def bm_slab(outer, holes, z0, z1):
    """Polygon slab with optional polygon holes (atria). Faces: top (+Z), bottom (-Z), outer/inner edges."""
    bm = bmesh.new()
    edges, loops = [], []
    for pts in [R.ccw(outer)] + [list(reversed(R.ccw(h))) for h in holes]:
        vs = [bm.verts.new((x, y, z1)) for x, y in pts]
        loops.append(vs)
        edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges)
    for f in bm.faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    top = list(bm.faces)
    ext = bmesh.ops.extrude_face_region(bm, geom=top)
    vs = [g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z0 - z1), verts=vs)
    # extruded copy moved down -> it is the bottom; the originals stay as top. Fix orientation.
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def poly_rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def mat_by_normal(top, bottom, side):
    return lambda f: top if f.normal.z > 0.5 else (bottom if f.normal.z < -0.5 else side)


# ---------------------------------------------------------------------------
# brand graphics (simplified generic recreations drawn procedurally - not official artwork)
# ---------------------------------------------------------------------------
def media_png(name, cols, w=2048, h=512, seed=1):
    """Abstract flowing-wave content for LED media facades (sRGB PNG)."""
    p = _img_path(name)
    if os.path.exists(p):
        return p
    ys, xs = np.mgrid[0:h, 0:w] / float(h)
    acc = np.zeros((h, w, 3))
    rng = np.random.default_rng(seed)
    base = np.array(cols[0]) / 255.0
    acc += base[None, None]
    for k in range(6):
        c = np.array(cols[1 + k % (len(cols) - 1)]) / 255.0
        ph = rng.uniform(0, 6.28); fr = rng.uniform(0.6, 1.6); amp = rng.uniform(0.08, 0.22); off = rng.uniform(0.2, 0.8)
        yc = off + amp * np.sin(xs * fr * 2 + ph) + 0.05 * np.sin(xs * 7 + ph * 2)
        band = np.exp(-((ys - yc) / rng.uniform(0.03, 0.12)) ** 2)
        acc += band[..., None] * c[None, None] * rng.uniform(0.6, 1.0)
    acc = np.clip(acc, 0, 1)
    Image.fromarray((acc * 255).astype(np.uint8)).save(p)
    return p


def apple_logo_png(name='pc_logo_apple.png', n=1024):
    p = _img_path(name)
    if os.path.exists(p):
        return p
    im = Image.new('L', (n, n), 0); d = ImageDraw.Draw(im)
    d.ellipse([150, 260, 560, 900], fill=255); d.ellipse([464, 260, 874, 900], fill=255)
    d.ellipse([230, 520, 794, 960], fill=255)
    d.ellipse([440, 200, 584, 330], fill=0)                      # top notch
    d.ellipse([800, 390, 1080, 690], fill=0)                     # bite
    d.ellipse([360, 860, 664, 1010], fill=0)                     # bottom notch
    leaf = Image.new('L', (n, n), 0); ld = ImageDraw.Draw(leaf)
    ld.ellipse([440, 40, 620, 300], fill=255)
    leaf = leaf.rotate(-38, center=(530, 170))
    im = Image.fromarray(np.maximum(np.array(im), np.array(leaf)))
    im = im.filter(ImageFilter.GaussianBlur(2))
    rgba = Image.merge('RGBA', (Image.new('L', (n, n), 255),) * 3 + (im,))
    rgba.save(p)
    return p


def badge_png(name, bg, text, fg=(255, 255, 255), n=512, radius=0.28, font='/usr/share/fonts/opentype/inter/Inter-Bold.otf', size=0.5):
    p = _img_path(name)
    if os.path.exists(p):
        return p
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, n - 4, n - 4], radius=int(n * radius), fill=tuple(bg) + (255,))
    f = ImageFont.truetype(font, int(n * size))
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((n - (bb[2] - bb[0])) / 2 - bb[0], (n - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=tuple(fg) + (255,))
    im.save(p)
    return p


def decal(acc, M, w, h, mat, z=0.0):
    """Flat quad decal (logo) in face frame M, size w x h, UV 0..1."""
    acc.add(bm_quad((-w / 2, -h / 2, z), (w / 2, -h / 2, z), (w / 2, h / 2, z), (-w / 2, h / 2, z)), mat, matrix=M, uv='fit',
            cell=(0, 0, 1, 1))
