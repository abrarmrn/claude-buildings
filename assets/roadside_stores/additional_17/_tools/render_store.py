"""Render the four mandatory preview JPEGs for one store from its saved .blend (Cycles CPU + OIDN denoise).

Usage: python render_store.py <store_dir> <basename> [view ...]      views: day night road_view detail
Env:   RS_PREVIEW_SCALE=0.35  -> quick low-resolution composition check (writes *_lowres.jpg, no report)
Outputs <store_dir>/renders/<basename>_<view>.jpg (1600x900) and renders/render_report.json
The report holds, for the road view, the projected pixel height of the brand sign and an occlusion ray test.
"""
import os, sys, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'prototypes', '_tools'))
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import roadside_lib as R

store_dir, base = sys.argv[1], sys.argv[2]
views = sys.argv[3:] or ['day', 'night', 'road_view', 'detail']
quick = float(os.environ.get('RS_PREVIEW_SCALE', '1')) != 1.0
bpy.ops.wm.open_mainfile(filepath=f'{store_dir}/{base}.blend')
sc = bpy.context.scene
out_dir = f'{store_dir}/renders'
os.makedirs(out_dir, exist_ok=True)
root = [o for o in bpy.data.objects if 'preview_cameras' in o.keys()][0]
prefix = root.name.split('_')[0]
cams = json.loads(root['preview_cameras'])
signs = json.loads(root.get('brand_signs', '[]'))
colls = {c.name: c for c in bpy.data.collections}
for L in (1, 2):
    colls[f'{prefix}_LOD{L}'].hide_render = True
    colls[f'{prefix}_LOD{L}'].hide_viewport = True
colls[f'{prefix}_Collision'].hide_render = True
colls[f'{prefix}_Collision'].hide_viewport = True

cam = bpy.data.objects.get('PV_Camera') or bpy.data.objects.new('PV_Camera', bpy.data.cameras.new('PV_Camera'))
if cam.name not in sc.collection.objects:
    sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 5000
cam.data.sensor_width = 36


def set_cam(key):
    c = cams[key]
    cam.location = Vector(c['loc'])
    R.look_at(cam, Vector(c['target']))
    cam.data.lens = c['lens']
    bpy.context.view_layer.update()


def sign_check(key):
    res = []
    dg = bpy.context.evaluated_depsgraph_get()
    for s in signs:
        ctr = Vector(s['center']); n = Vector(s['normal'])
        top = ctr + Vector((0, 0, s['cap_height'] / 2 * (1 - n.z * n.z) ** 0.5)); bot = ctr - Vector((0, 0, s['cap_height'] / 2 * (1 - n.z * n.z) ** 0.5))
        pt, pb = world_to_camera_view(sc, cam, top), world_to_camera_view(sc, cam, bot)
        pc = world_to_camera_view(sc, cam, ctr)
        px = abs(pt.y - pb.y) * 900.0   # normalised to the real 1600x900 frame
        tdir = Vector((-n.y, n.x, 0)).normalized()
        up = (Vector((0, 0, 1)) - n * n.z).normalized()          # 'up' along the sign surface (matters for signs on sloped roofs)
        w = s.get('width', 2.0)
        vis, total, occ = 0, 0, set()
        for fx in (-0.45, -0.22, 0.0, 0.22, 0.45):
            for fz in (-0.3, 0.3):
                p = ctr + tdir * (fx * w) + up * (fz * s['cap_height']) + n * 0.12
                q = world_to_camera_view(sc, cam, p)
                total += 1
                d = p - cam.location
                hit, loc, nor, idx, ob, mat = sc.ray_cast(dg, cam.location, d.normalized(), distance=d.length - 0.02)
                inside = 0 <= q.x <= 1 and 0 <= q.y <= 1 and q.z > 0
                if inside and not hit:
                    vis += 1
                elif hit and ob:
                    occ.add(ob.name)
        facing = (cam.location - ctr).normalized().dot(n)
        res.append(dict(name=s['name'], cap_height_m=s['cap_height'], pixel_height=round(px, 1), visible_fraction=round(vis / total, 2),
                        in_frame=bool(0 <= pc.x <= 1 and 0 <= pc.y <= 1 and pc.z > 0), occluders=sorted(occ), facing_dot=round(facing, 2),
                        distance_m=round((ctr - cam.location).length, 1), readable=bool(px >= 18 and vis / total >= 0.9 and facing > 0.35)))
    return res


report = {}
for view in views:
    mode = 'night' if view == 'night' else 'day'
    R.set_world(sc, mode)
    if mode == 'night':
        # blue-hour dusk: readable silhouettes + faint moon fill (same for all 17 stores)
        wnt = sc.world.node_tree
        for n in wnt.nodes:
            if n.type == 'VALTORGB':
                n.color_ramp.elements[0].color = (0.018, 0.026, 0.065, 1)
                n.color_ramp.elements[1].color = (0.003, 0.005, 0.02, 1)
        bpy.data.objects['PV_Sun'].data.energy = 0.07
        bpy.data.objects['PV_Sun'].data.color = (0.62, 0.72, 1.0)
    colls[f'{prefix}_NightLights'].hide_render = (mode != 'night')
    key = 'day' if view in ('day', 'night') else view.replace('_view', '')
    set_cam(key)
    R.setup_render(sc, 1600, 900, {'day': 32, 'night': 52, 'road_view': 32, 'detail': 30}[view])
    sc.cycles.max_bounces = 4
    sc.cycles.transparent_max_bounces = 6
    sc.cycles.adaptive_threshold = 0.05
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 93
    name = f'{base}_{view}' + ('_lowres' if quick else '')
    sc.render.filepath = f'{out_dir}/{name}.jpg'
    if view == 'road_view':
        report['road_view_sign'] = sign_check(key)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    report[f'{view}_seconds'] = round(time.time() - t, 1)
    print(f'RENDERED {name}.jpg {sc.render.resolution_x}x{sc.render.resolution_y} {sc.cycles.samples}spp {time.time() - t:.1f}s', flush=True)
if not quick:
    rp = f'{out_dir}/render_report.json'
    old = json.load(open(rp)) if os.path.exists(rp) else {}
    old.update(report)
    json.dump(old, open(rp, 'w'), indent=1)
print('SIGN', json.dumps(report.get('road_view_sign')))
print('DONE')
