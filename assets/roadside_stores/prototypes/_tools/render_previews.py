"""Render the visual-inspection set for one roadside store prototype.

Usage: python render_previews.py <asset_dir> <blend_basename> [shot ...]
Shots: day_hero night_hero driveby_day driveby_night closeup1_day closeup2_night overview_day
       lod_compare lod_wire lod_distance   (default: all)
Outputs PNGs into <asset_dir>/renders/. Uses Cycles (CPU) with the OIDN denoiser.
"""
import os, sys, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import roadside_lib as R
from PIL import Image, ImageDraw, ImageFont

asset_dir, base = sys.argv[1], sys.argv[2]
shots = sys.argv[3:] or ['day_hero', 'night_hero', 'driveby_day', 'driveby_night', 'closeup1_day',
                         'closeup2_night', 'overview_day', 'lod_compare', 'lod_wire', 'lod_distance']
bpy.ops.wm.open_mainfile(filepath=f'{asset_dir}/source/{base}.blend')
sc = bpy.context.scene
out_dir = f'{asset_dir}/renders'
os.makedirs(out_dir, exist_ok=True)
open(f'{out_dir}/.gdignore', 'w').close()   # keep preview PNGs out of Godot's import
root = [o for o in bpy.data.objects if 'preview_cameras' in o.keys()][0]
prefix = root.name.split('_')[0]
cams = json.loads(root['preview_cameras'])
colls = {c.name: c for c in bpy.data.collections}
lod_colls = {L: colls[f'{prefix}_LOD{L}'] for L in (0, 1, 2)}
colls[f'{prefix}_Collision'].hide_render = True

cam = bpy.data.objects.get('PV_Camera') or bpy.data.objects.new('PV_Camera', bpy.data.cameras.new('PV_Camera'))
if cam.name not in sc.collection.objects:
    sc.collection.objects.link(cam)
sc.camera = cam
cam.data.clip_end = 5000


def tri_count(L):
    t = 0
    for ob in lod_colls[L].all_objects:
        if ob.type == 'MESH':
            ob.data.calc_loop_triangles()
            t += len(ob.data.loop_triangles)
    return t


def show_lod(L):
    for k, c in lod_colls.items():
        c.hide_render = (k != L)


def set_cam(key, dist_scale=None, lens=None):
    c = cams[key]
    loc, tgt = Vector(c['loc']), Vector(c['target'])
    if dist_scale is not None:
        d = (loc - tgt)
        loc = tgt + d.normalized() * dist_scale
    cam.location = loc
    R.look_at(cam, tgt)
    cam.data.lens = lens or c['lens']


def mode(m):
    R.set_world(sc, m)
    colls[f'{prefix}_NightLights'].hide_render = (m != 'night')


def render(path, w, h, samples):
    R.setup_render(sc, w, h, samples)
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f'RENDERED {os.path.basename(path)} {w}x{h} {samples}spp {time.time() - t:.1f}s', flush=True)


def label(img_path, text, sub=None):
    im = Image.open(img_path).convert('RGB')
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(R.FONT_SEMI, max(18, im.width // 45))
    f2 = ImageFont.truetype(R.FONT_SEMI, max(14, im.width // 60))
    dr.rectangle([0, 0, im.width, int(im.height * 0.075) + (f2.size + 6 if sub else 0)], fill=(0, 0, 0))
    dr.text((14, 8), text, font=f, fill='white')
    if sub:
        dr.text((14, 14 + f.size), sub, font=f2, fill=(200, 200, 200))
    return im


def strip(paths, labels, subs, out):
    ims = [label(p, l, s) for p, l, s in zip(paths, labels, subs)]
    W = sum(i.width for i in ims) + 8 * (len(ims) - 1)
    canvas = Image.new('RGB', (W, ims[0].height), (30, 30, 30))
    x = 0
    for i in ims:
        canvas.paste(i, (x, 0)); x += i.width + 8
    canvas.save(out)
    for p in paths:
        os.remove(p)


def wire_override(on):
    vl = sc.view_layers[0]
    if not on:
        vl.material_override = None
        return
    m = bpy.data.materials.get('PV_Wire')
    if not m:
        m = bpy.data.materials.new('PV_Wire'); m.use_nodes = True
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        wf = nt.nodes.new('ShaderNodeWireframe'); wf.use_pixel_size = True; wf.inputs[0].default_value = 1.0
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
        mix.inputs['A'].default_value = (0.75, 0.75, 0.75, 1); mix.inputs['B'].default_value = (0.02, 0.02, 0.05, 1)
        nt.links.new(wf.outputs[0], mix.inputs['Factor'])
        nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
        b.inputs['Roughness'].default_value = 0.9
    vl.material_override = m


tris = {L: tri_count(L) for L in (0, 1, 2)}
print('TRIS', tris)
W, H = 1600, 900
for shot in shots:
    show_lod(0); wire_override(False)
    if shot == 'day_hero':
        mode('day'); set_cam('day_hero'); render(f'{out_dir}/01_day_hero.png', W, H, 64)
    elif shot == 'night_hero':
        mode('night'); set_cam('day_hero'); render(f'{out_dir}/02_night_hero.png', W, H, 128)
    elif shot == 'driveby_day':
        mode('day'); set_cam('driveby'); render(f'{out_dir}/03_driveby_day.png', W, H, 64)
    elif shot == 'driveby_night':
        mode('night'); set_cam('driveby'); render(f'{out_dir}/04_driveby_night.png', W, H, 128)
    elif shot == 'closeup1_day':
        mode('day'); set_cam('closeup1'); render(f'{out_dir}/05_closeup1_day.png', W, H, 64)
    elif shot == 'closeup2_night':
        mode('night'); set_cam('closeup2'); render(f'{out_dir}/06_closeup2_night.png', W, H, 128)
    elif shot == 'overview_day':
        mode('day'); set_cam('overview'); render(f'{out_dir}/07_overview_day.png', W, H, 64)
    elif shot == 'lod_compare':
        mode('day'); set_cam('day_hero'); ps = []
        for L in (0, 1, 2):
            show_lod(L); p = f'{out_dir}/_lod{L}.png'; render(p, 960, 540, 48); ps.append(p)
        strip(ps, [f'LOD{L}  {tris[L]:,} tris' for L in (0, 1, 2)],
              ['same camera, daylight'] * 3, f'{out_dir}/08_lod_compare_same_camera.png')
    elif shot == 'lod_wire':
        mode('day'); set_cam('day_hero'); wire_override(True); ps = []
        for L in (0, 1, 2):
            show_lod(L); p = f'{out_dir}/_wire{L}.png'; render(p, 960, 540, 16); ps.append(p)
        wire_override(False)
        strip(ps, [f'LOD{L} wireframe  {tris[L]:,} tris' for L in (0, 1, 2)],
              ['same camera'] * 3, f'{out_dir}/09_lod_wireframe.png')
    elif shot == 'lod_distance':
        mode('day'); ps = []; subs = []
        for L in (0, 1, 2):
            b, e = R.LOD_RANGES[L]
            d = {0: 45.0, 1: 115.0, 2: 260.0}[L]
            show_lod(L); set_cam('day_hero', dist_scale=d, lens=35)
            p = f'{out_dir}/_dist{L}.png'; render(p, 960, 540, 48); ps.append(p)
            subs.append(f'camera {d:.0f} m from target, 35 mm (LOD range {b:.0f}-{e:.0f} m)')
        strip(ps, [f'LOD{L}  {tris[L]:,} tris' for L in (0, 1, 2)], subs, f'{out_dir}/10_lod_at_switch_distance.png')
print('DONE')
