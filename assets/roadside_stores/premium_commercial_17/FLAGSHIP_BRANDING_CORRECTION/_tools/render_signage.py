"""Targeted signage renders for one corrected flagship (no full-building re-render).

Usage: python render_signage.py <NN> <view> [--blend other.blend --out file.jpg]
views: front_day | front_night | road | detail_day
Lighting / world identical to premium_commercial_17/_tools/render_asset.py (Cycles CPU + OIDN, 1600x900).
"""
import os, sys, json, math, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', '_tools')))
import bpy
from mathutils import Vector
import pk_core as C
from apply_brand_fix import SPECS, P17
R = C.R

args = sys.argv[1:]
num, view = args[0], args[1]
blend = args[args.index('--blend') + 1] if '--blend' in args else None
out = args[args.index('--out') + 1] if '--out' in args else None
scale = float(os.environ.get('PK_SCALE', '1'))
sp = SPECS[num]
adir = os.path.join(P17, sp['folder'])
bpy.ops.wm.open_mainfile(filepath=blend or os.path.join(adir, sp['base'] + '.blend'))
sc = bpy.context.scene
colls = {c.name: c for c in bpy.data.collections}
for n in ('LOD1', 'LOD2', 'COLLISION', 'BRAND_SIGNAGE_ORIGINAL_DISABLED'):
    if n in colls:
        colls[n].hide_render = True
cam = bpy.data.objects.get('PV_Camera') or bpy.data.objects.new('PV_Camera', bpy.data.cameras.new('PV_Camera'))
if cam.name not in sc.collection.objects:
    sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05; cam.data.clip_end = 5000; cam.data.sensor_width = 36

cd = sp['camera']
if view == 'detail_day':
    cd = dict(sp.get('camera2', cd))
T = Vector(cd['target'])
if view == 'road':
    cam.location = Vector(cd['road']); cam.data.lens = cd['road_lens']
else:
    lens = 50.0
    dist = cd['width'] * lens / 36.0
    cam.location = T + Vector((0.0, -dist, -0.06 * dist if T.z > 6 else 0.04 * dist))
    cam.data.lens = lens
C.look_at(cam, T)
bpy.context.view_layer.update()

mode = 'night' if view == 'front_night' else 'day'
R.set_world(sc, mode)
sun = bpy.data.objects['PV_Sun']
if mode == 'night':
    for nd in sc.world.node_tree.nodes:
        if nd.type == 'VALTORGB':
            nd.color_ramp.elements[0].color = (0.020, 0.030, 0.075, 1)
            nd.color_ramp.elements[1].color = (0.004, 0.006, 0.024, 1)
    sun.data.energy = 0.06; sun.data.color = (0.62, 0.72, 1.0)
    sc.view_settings.exposure = 0.35
else:
    sun.data.energy = 4.0
    sc.view_settings.exposure = -0.15
colls['EXTERIOR_LIGHTING'].hide_render = (mode != 'night')
spp = 48 if mode == 'night' else 32
R.setup_render(sc, 1600, 900, spp)
if scale != 1.0:
    sc.render.resolution_x, sc.render.resolution_y = int(1600 * scale), int(900 * scale)
    sc.cycles.samples = max(8, int(spp * scale))
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3
sc.cycles.transmission_bounces = 4; sc.cycles.transparent_max_bounces = 32
sc.cycles.adaptive_threshold = 0.03; sc.cycles.sample_clamp_indirect = 6.0; sc.cycles.light_tree = True
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92
if out is None:
    out = os.path.join(adir, 'renders', f'{sp["base"]}_signage_{view}' + ('_lowres' if scale != 1.0 else '') + '.jpg')
sc.render.filepath = out
t = time.time()
bpy.ops.render.render(write_still=True)
print(f'RENDERED {out} {time.time() - t:.1f}s', flush=True)
