"""Combined presentation streetscape: the five Boulevard assets appended side by side along one promenade.

Presentation only - the order and spacing are a layout DEMONSTRATION and do NOT represent real geographic positions or
real tenants on Sheikh Mohammed bin Rashid Boulevard.
Usage: python build_streetscape.py [render]     -> combined_streetscape/boulevard_five_streetscape.blend (+ 4 renders)
"""
import os, sys, json, math, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bv_core import *

OUT = os.path.join(BV, 'combined_streetscape')
os.makedirs(OUT, exist_ok=True)
# left -> right; widths from the asset footprints; party walls touch
ORDER = [('04_galerie_dor', 'galerie_dor', 26.0), ('01_maison_levant', 'maison_levant', 22.0),
         ('05_the_promenade_galleria', 'the_promenade_galleria', 34.0), ('02_juniper_house', 'juniper_house', 30.0),
         ('03_lune_and_laurel', 'lune_and_laurel', 16.0)]

R.reset_scene()
R.Ctx.tex_dir = os.path.join(OUT, 'textures')
os.makedirs(R.Ctx.tex_dir, exist_ok=True)
open(os.path.join(R.Ctx.tex_dir, '.gdignore'), 'w').close()
sc = bpy.context.scene
total = sum(w for _f, _b, w in ORDER)
x = -total / 2
placed = []
for folder, base, w in ORDER:
    blend = os.path.join(BV, folder, base + '.blend')
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c.startswith('B0') and '_' in c]
    for c in dst.collections:
        sc.collection.children.link(c)
        root = [o for o in c.objects if o.parent is None and o.type == 'EMPTY'][0]
        cx = x + w / 2
        root.location.x = cx
        placed.append(dict(asset=folder, x_centre=round(cx, 2), width=w))
        for ch in c.children:
            if ch.name.startswith(('LOD1', 'LOD2', 'COLLISION')) or ch.name in ('LOD1', 'LOD2', 'COLLISION'):
                ch.hide_render = True; ch.hide_viewport = True
    x += w
# shared promenade / boulevard (preview) - reuse the per-asset environment builder with a dummy asset-like object
class _Env:
    pass
E = _Env(); E.meta = dict(footprint=[-total / 2, 0, total / 2, 30], corner='right')
E.preview = bpy.data.collections.new('_STREET_PREVIEW'); sc.collection.children.link(E.preview)
boulevard_env(E, -total / 2, total / 2)
sun = bpy.data.objects.get('PV_Sun')
cam = bpy.data.objects.new('PV_Camera', bpy.data.cameras.new('PV_Camera')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.sensor_width = 36; cam.data.clip_start = 0.05; cam.data.clip_end = 5000
VIEWS = dict(
    overview_day=dict(loc=(-70.0, -78.0, 26.0), target=(-6.0, 6.0, 6.0), lens=30, mode='day'),
    overview_night=dict(loc=(-62.0, -70.0, 16.0), target=(-6.0, 6.0, 6.0), lens=30, mode='night'),
    promenade_day=dict(loc=(-60.0, -6.2, 1.7), target=(8.0, 3.0, 6.0), lens=26, mode='day'),
    driver_night=dict(loc=(-58.0, -12.5, 1.15), target=(8.0, 2.0, 6.0), lens=26, mode='night'),
)
meta = dict(note='Presentation layout only - not real geographic placement or real tenant positions.', order=placed,
            total_frontage_m=total, views=VIEWS)
root = bpy.data.objects.new('STREETSCAPE_PRESENTATION', None); sc.collection.objects.link(root)
root['note'] = meta['note']
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'boulevard_five_streetscape.blend'), compress=True, relative_remap=True)
json.dump(meta, open(os.path.join(OUT, 'streetscape_layout.json'), 'w'), indent=1)
print('STREETSCAPE_SAVED', total)

if 'render' in sys.argv:
    scale = float(os.environ.get('PK_SCALE', '1'))
    ext_colls = [c for c in bpy.data.collections if c.name.startswith('EXTERIOR_LIGHTING')]
    for key, v in VIEWS.items():
        R.set_world(sc, v['mode'])
        sun = bpy.data.objects.get('PV_Sun')
        if v['mode'] == 'night':
            for nd in sc.world.node_tree.nodes:
                if nd.type == 'VALTORGB':
                    nd.color_ramp.elements[0].color = (0.020, 0.030, 0.075, 1)
                    nd.color_ramp.elements[1].color = (0.004, 0.006, 0.024, 1)
            sun.data.energy = 0.06; sun.data.color = (0.62, 0.72, 1.0); sc.view_settings.exposure = 0.35
        else:
            sun.data.energy = 4.0; sc.view_settings.exposure = -0.15
        for c in ext_colls:
            c.hide_render = v['mode'] != 'night'
        cam.location = Vector(v['loc']); look_at(cam, Vector(v['target'])); cam.data.lens = v['lens']
        spp = 48 if v['mode'] == 'night' else 32
        R.setup_render(sc, 1600, 900, spp)
        if scale != 1.0:
            sc.render.resolution_x, sc.render.resolution_y = int(1600 * scale), int(900 * scale)
            sc.cycles.samples = max(8, int(spp * scale))
        sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 32; sc.cycles.adaptive_threshold = 0.03
        sc.cycles.sample_clamp_indirect = 6.0
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
        sc.render.filepath = os.path.join(OUT, f'streetscape_{key}' + ('_lowres' if scale != 1.0 else '') + '.jpg')
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print('RENDERED', key, round(time.time() - t, 1), flush=True)
