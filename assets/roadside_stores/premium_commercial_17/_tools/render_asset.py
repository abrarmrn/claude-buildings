"""Render the four preview JPEGs of one premium asset from its saved .blend and verify interior visibility.

Usage: python render_asset.py <asset_dir> <basename> [view ...]       views: day night road_view interior
Env:   PK_SCALE=0.4  -> quick low-resolution check (writes *_lowres.jpg, no report update)
Outputs renders/<base>_<view>.jpg (1600x900, Cycles CPU + OpenImageDenoise) and renders/render_report.json with
ray-traced visibility checks: every placeholder car and every registered interior probe point is tested from the
road-view and day cameras; rays may pass through glass (alpha < 1) but not through opaque geometry.
"""
import os, sys, json, math, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import pk_core as C
R = C.R

asset_dir, base = sys.argv[1], sys.argv[2]
views = sys.argv[3:] or ['day', 'night', 'road_view', 'interior']
scale = float(os.environ.get('PK_SCALE', '1'))
quick = scale != 1.0
bpy.ops.wm.open_mainfile(filepath=f'{asset_dir}/{base}.blend')
sc = bpy.context.scene
out_dir = f'{asset_dir}/renders'
os.makedirs(out_dir, exist_ok=True)
root = [o for o in bpy.data.objects if 'preview_cameras' in o.keys()][0]
cams = json.loads(root['preview_cameras'])
checks = json.loads(root.get('checks', '{}'))
colls = {c.name: c for c in bpy.data.collections}
for n in ('LOD1', 'LOD2', 'COLLISION'):
    colls[n].hide_render = True
    colls[n].hide_viewport = True

cam = bpy.data.objects.get('PV_Camera') or bpy.data.objects.new('PV_Camera', bpy.data.cameras.new('PV_Camera'))
if cam.name not in sc.collection.objects:
    sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_start = 0.05
cam.data.clip_end = 5000
cam.data.sensor_width = 36
sc.render.resolution_x, sc.render.resolution_y = 1600, 900


def set_cam(key):
    c = cams.get(key) or cams['day']
    cam.location = Vector(c['loc'])
    C.look_at(cam, Vector(c['target']))
    cam.data.lens = c['lens']
    bpy.context.view_layer.update()


def _is_glass(ob, idx):
    try:
        mi = ob.data.polygons[idx].material_index
        m = ob.material_slots[mi].material
    except Exception:
        return False
    if m is None:
        return False
    d = R.MATERIAL_DEFS.get(m.name, {})
    if d.get('alpha', 1.0) < 1.0 or 'Glass' in m.name and 'Car' not in m.name:
        return True
    return m.blend_method in ('BLEND', 'CLIP') if hasattr(m, 'blend_method') else False


def trace(p_from, p_to, target=None):
    """Return (reached, glass_layers, blocker)."""
    dg = bpy.context.evaluated_depsgraph_get()
    o = Vector(p_from); d = Vector(p_to) - o
    dist = d.length; d.normalize()
    layers = 0
    travelled = 0.0
    for _ in range(40):
        hit, loc, nor, idx, ob, mat = sc.ray_cast(dg, o, d, distance=dist - travelled - 0.02)
        if not hit:
            return True, layers, None
        if target is not None and ob.name == target:
            return True, layers, None
        if _is_glass(ob, idx):
            layers += 1
            step = (loc - o).length + 0.002
            o = loc + d * 0.002
            travelled += step
            continue
        return False, layers, ob.name
    return False, layers, 'too-many-layers'


def visibility(key):
    set_cam(key)
    res = dict(cars=[], probes=[])
    for ob in colls['PLACEHOLDER_CARS'].all_objects:
        if ob.type != 'MESH':
            continue
        L = ob.get('length_m', 4.6); H = ob.get('height_m', 1.4)
        ok, tot, glass, block, inframe = 0, 0, 0, set(), 0
        for fu in (-0.3, 0.0, 0.3):
            for fz in (0.45, 0.75):
                p = ob.matrix_world @ Vector((fu * L, 0, fz * H))
                q = world_to_camera_view(sc, cam, p)
                tot += 1
                fr = 0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0
                inframe += fr
                r, g, b = trace(cam.location, p, ob.name)
                if r and fr:
                    ok += 1; glass = max(glass, g)
                elif b:
                    block.add(b)
        res['cars'].append(dict(car=ob.name, visible_fraction=round(ok / tot, 2), in_frame_fraction=round(inframe / tot, 2),
                                max_glass_layers=glass, blockers=sorted(block)[:4]))
    for pr in checks.get('probes', []):
        p = Vector(pr['p'])
        q = world_to_camera_view(sc, cam, p)
        fr = 0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0
        r, g, b = trace(cam.location, p)
        res['probes'].append(dict(name=pr['name'], reached=bool(r), in_frame=bool(fr), glass_layers=g, blocker=b))
    return res


report = {}
for view in views:
    mode = 'night' if view == 'night' else 'day'
    R.set_world(sc, mode)
    sun = bpy.data.objects['PV_Sun']
    if mode == 'night':
        wnt = sc.world.node_tree
        for n in wnt.nodes:
            if n.type == 'VALTORGB':
                n.color_ramp.elements[0].color = (0.020, 0.030, 0.075, 1)
                n.color_ramp.elements[1].color = (0.004, 0.006, 0.024, 1)
        sun.data.energy = 0.06
        sun.data.color = (0.62, 0.72, 1.0)
        sc.view_settings.exposure = 0.35
    else:
        sun.data.energy = 4.0
        sc.view_settings.exposure = -0.15 if view != 'interior' else -0.7
    colls['EXTERIOR_LIGHTING'].hide_render = (mode != 'night')
    key = {'day': 'day', 'night': 'night', 'road_view': 'road', 'interior': 'interior'}[view]
    set_cam(key)
    spp = {'day': 36, 'night': 52, 'road_view': 36, 'interior': 56}[view]
    R.setup_render(sc, 1600, 900, spp)
    if quick:
        sc.render.resolution_x, sc.render.resolution_y = int(1600 * scale), int(900 * scale)
        sc.cycles.samples = max(10, int(spp * scale))
    sc.cycles.max_bounces = 6
    sc.cycles.diffuse_bounces = 3
    sc.cycles.glossy_bounces = 3
    sc.cycles.transmission_bounces = 4
    sc.cycles.transparent_max_bounces = 32
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.sample_clamp_indirect = 6.0
    sc.cycles.light_tree = True
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 92
    sc.render.threads_mode = 'AUTO'
    name = f'{base}_{view}' + ('_lowres' if quick else '')
    sc.render.filepath = f'{out_dir}/{name}.jpg'
    if view in ('road_view', 'day') and not quick:
        report[f'{view}_visibility'] = visibility(key)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    report[f'{view}_seconds'] = round(time.time() - t, 1)
    print(f'RENDERED {name}.jpg {sc.render.resolution_x}x{sc.render.resolution_y} {sc.cycles.samples}spp {time.time() - t:.1f}s', flush=True)
if not quick:
    rp = f'{out_dir}/render_report.json'
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(report)
    json.dump(old, open(rp, 'w'), indent=1)
    print('VIS', json.dumps({k: v for k, v in report.items() if 'visibility' in k})[:3000])
print('DONE')
