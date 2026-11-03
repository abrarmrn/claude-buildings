"""Validate one store: reopen the saved .blend (fresh process), then reimport the exported .glb into a clean scene.

Usage: python validate_store.py <store_dir> <basename>
Writes <store_dir>/validation.json ; prints a PASS/FAIL summary line.
Checks: mesh integrity (NaN, zero-area faces, loose verts, bad material indices), UVs, flipped normals
(signed volume of every watertight piece), materials + texture files, LOD objects + triangle budgets,
actual dimensions, collision proxies, then GLB: JSON read-back of triangles per LOD (master + per-LOD files),
embedded texture decode, clean-scene re-import (meshes / triangles / bounds / images / materials), file sizes.
"""
import os, sys, json, math, struct, io
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'prototypes', '_tools'))
import bpy, bmesh
import numpy as np
from mathutils import Vector
from PIL import Image
import roadside_lib as R

store_dir, base = os.path.abspath(sys.argv[1]), sys.argv[2]
rep = dict(store=base, checks={}, warnings=[], errors=[])


def check(name, ok, detail=None):
    rep['checks'][name] = dict(ok=bool(ok), detail=detail)
    if not ok:
        rep['errors'].append(f'{name}: {detail}')


# ------------------------------------------------------------------ 1. saved .blend
bpy.ops.wm.open_mainfile(filepath=f'{store_dir}/{base}.blend')
root = [o for o in bpy.data.objects if 'preview_cameras' in o.keys()][0]
prefix = root.name.split('_')[0]
colls = {c.name: c for c in bpy.data.collections}


def piece_volume(bm, face_ids):
    """Signed volume of a closed piece, summed relative to the piece centroid in double precision (float32 world coords cancel badly)."""
    pts = {l.vert.index: np.array(l.vert.co, dtype=np.float64) for fi in face_ids for l in bm.faces[fi].loops}
    c = np.mean(list(pts.values()), axis=0)
    vol = 0.0
    for fi in face_ids:
        vs = [np.array(l.vert.co, dtype=np.float64) - c for l in bm.faces[fi].loops]
        for k in range(1, len(vs) - 1):
            vol += np.dot(vs[0], np.cross(vs[k], vs[k + 1])) / 6.0
    return vol


def mesh_objs(coll):
    return [o for o in coll.all_objects if o.type == 'MESH']


lod_stats, bad = {}, dict(nan=0, zero_area=0, loose=0, bad_matidx=0, no_uv=0, uv_nan=0, flipped=0, watertight=0, pieces=0)
mats_used, images_used = set(), set()
bounds = {}
for L in (0, 1, 2):
    obs = mesh_objs(colls[f'{prefix}_LOD{L}'])
    tris, verts = 0, 0
    mn = np.array([1e9] * 3); mx = np.array([-1e9] * 3)
    for ob in obs:
        me = ob.data
        # transforms applied (identity) - geometry is authored in final plot coordinates
        if (ob.location.length > 1e-6 or any(abs(a) > 1e-6 for a in ob.rotation_euler) or any(abs(s - 1) > 1e-6 for s in ob.scale)):
            rep['errors'].append(f'transform not applied: {ob.name}')
        n = len(me.vertices)
        co = np.empty(n * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        if not np.isfinite(co).all():
            bad['nan'] += 1
        if n:
            mn = np.minimum(mn, co.min(0)); mx = np.maximum(mx, co.max(0))
        me.calc_loop_triangles()
        tris += len(me.loop_triangles); verts += n
        if len(me.uv_layers) == 0:
            bad['no_uv'] += 1
        else:
            uv = np.empty(len(me.loops) * 2); me.uv_layers[0].data.foreach_get('uv', uv)
            if not np.isfinite(uv).all():
                bad['uv_nan'] += 1
        mi = np.empty(len(me.polygons), dtype=np.int32); me.polygons.foreach_get('material_index', mi)
        if len(mi) and (mi.max() >= len(me.materials) or any(m is None for m in me.materials)):
            bad['bad_matidx'] += 1
        for m in me.materials:
            if m:
                mats_used.add(m.name)
        if L == 0:
            bm = bmesh.new(); bm.from_mesh(me)
            bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.edges.ensure_lookup_table()
            bad['zero_area'] += sum(1 for f in bm.faces if f.calc_area() < 1e-10)
            bad['loose'] += sum(1 for v in bm.verts if not v.link_faces)
            # flipped normals: every watertight piece must have positive signed volume
            seen = set()
            for v0 in bm.verts:
                if v0.index in seen or not v0.link_faces:
                    continue
                stack, comp_faces, comp_edges = [v0], set(), set()
                seen.add(v0.index)
                while stack:
                    v = stack.pop()
                    for e in v.link_edges:
                        comp_edges.add(e.index)
                        for f in e.link_faces:
                            comp_faces.add(f.index)
                        o = e.other_vert(v)
                        if o.index not in seen:
                            seen.add(o.index); stack.append(o)
                bad['pieces'] += 1
                if all(len(bm.edges[ei].link_faces) == 2 for ei in comp_edges):
                    bad['watertight'] += 1
                    vol = piece_volume(bm, comp_faces)
                    if vol < 0:
                        bad['flipped'] += 1
            bm.free()
    lod_stats[L] = dict(triangles=tris, vertices=verts, objects=len(obs))
    bounds[L] = dict(min=mn.round(3).tolist(), max=mx.round(3).tolist(), size=(mx - mn).round(3).tolist())

check('lod_objects_exist', all(lod_stats[L]['objects'] > 0 for L in (0, 1, 2)), {L: lod_stats[L]['objects'] for L in lod_stats})
check('lod_budgets_decreasing', lod_stats[0]['triangles'] > lod_stats[1]['triangles'] > lod_stats[2]['triangles'],
      {L: lod_stats[L]['triangles'] for L in lod_stats})
check('lod_ratio', lod_stats[1]['triangles'] < 0.45 * lod_stats[0]['triangles'] and lod_stats[2]['triangles'] < 0.45 * lod_stats[1]['triangles'],
      dict(l1_over_l0=round(lod_stats[1]['triangles'] / lod_stats[0]['triangles'], 3), l2_over_l1=round(lod_stats[2]['triangles'] / lod_stats[1]['triangles'], 3)))
check('no_nan_geometry', bad['nan'] == 0 and bad['uv_nan'] == 0, bad)
check('uvs_present', bad['no_uv'] == 0, bad['no_uv'])
check('material_indices_valid', bad['bad_matidx'] == 0, bad['bad_matidx'])
check('no_loose_vertices', bad['loose'] == 0, bad['loose'])
check('normals_not_flipped', bad['flipped'] == 0, dict(flipped_pieces=bad['flipped'], watertight_pieces=bad['watertight'], pieces=bad['pieces']))
if bad['zero_area']:
    rep['warnings'].append(f"{bad['zero_area']} zero-area faces in LOD0 (font triangulation slivers)")
rep['mesh_integrity'] = bad

# dimensions + ground
b0 = bounds[0]
dims = json.loads(root.get('store_dims', '{}'))
check('dimensions_sane', 3.0 < b0['size'][2] < 40.0 and 8.0 < b0['size'][0] < 120.0 and 8.0 < b0['size'][1] < 120.0, b0['size'])
check('ground_at_z0', -0.5 <= b0['min'][2] <= 0.0, b0['min'])
for L in (1, 2):
    d = [abs(bounds[L]['size'][i] - b0['size'][i]) for i in range(3)]
    check(f'lod{L}_bounds_match_lod0', max(d) < 0.15 * max(b0['size']), dict(lod0=b0['size'], lod=bounds[L]['size']))
cols = [o for o in colls[f'{prefix}_Collision'].all_objects if o.type == 'MESH']
check('collision_proxies', len(cols) >= 3 and all(o.name.endswith('-convcolonly') for o in cols), len(cols))
check('night_lights', len(list(colls[f'{prefix}_NightLights'].all_objects)) >= 4, len(list(colls[f'{prefix}_NightLights'].all_objects)))
lod_extras = {o.name: dict(o.items()) for o in bpy.data.objects if o.name.endswith(('_LOD0', '_LOD1', '_LOD2'))}
check('lod_extras', all('lod_level' in dict(v) and 'visibility_range_end' in dict(v) for v in lod_extras.values()) and len(lod_extras) == 3,
      list(lod_extras))
# materials / textures
img_ok, img_list = True, []
for m in bpy.data.materials:
    if m.name not in mats_used or not m.use_nodes:
        continue
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            im = n.image
            p = bpy.path.abspath(im.filepath)
            ok = os.path.exists(p) and os.path.getsize(p) > 100
            im.reload() if ok else None
            ok = ok and im.size[0] > 0
            img_list.append(dict(image=os.path.basename(p), size=list(im.size), ok=ok))
            img_ok &= ok
            images_used.add(os.path.basename(p))
img_list = [json.loads(x) for x in sorted({json.dumps(d, sort_keys=True) for d in img_list})]
check('texture_files_ok', img_ok and len(img_list) > 0, f'{len(img_list)} distinct texture refs')
check('materials', len(mats_used) >= 12, len(mats_used))
rep['blend'] = dict(lod=lod_stats, bounds=bounds, materials=sorted(mats_used), material_count=len(mats_used), textures=img_list,
                    collision_proxies=len(cols), declared_dimensions=dims)

# ------------------------------------------------------------------ 2. GLB read-back
glb = f'{store_dir}/{base}.glb'
gr = R.gltf_report(glb)
with open(glb, 'rb') as f:
    data = f.read()
jlen = struct.unpack('<I', data[12:16])[0]
js = json.loads(data[20:20 + jlen])
binoff = 20 + jlen + 8
dec_ok, dec = True, []
for i, im in enumerate(js.get('images', [])):
    bv = js['bufferViews'][im['bufferView']]
    raw = data[binoff + bv.get('byteOffset', 0): binoff + bv.get('byteOffset', 0) + bv['byteLength']]
    try:
        pi = Image.open(io.BytesIO(raw)); pi.load()
        dec.append(dict(name=im.get('name'), size=list(pi.size), mime=im.get('mimeType'), bytes=len(raw)))
    except Exception as ex:
        dec_ok = False; dec.append(dict(name=im.get('name'), error=str(ex)))
check('glb_textures_decode', dec_ok and len(dec) > 0, f'{len(dec)} embedded images decoded')
lt = {int(k): v for k, v in gr['lod_tris'].items()}
check('glb_tris_match_blend', all(lt.get(L) == lod_stats[L]['triangles'] for L in (0, 1, 2)), dict(glb=lt, blend={L: lod_stats[L]['triangles'] for L in lod_stats}))
check('glb_collision_nodes', len(gr['collision_nodes']) == len(cols), len(gr['collision_nodes']))
per_lod = {}
for L in (0, 1, 2):
    p = f'{store_dir}/lod/{base}_lod{L}.glb'
    g2 = R.gltf_report(p)
    per_lod[L] = dict(triangles=g2['lod_tris'].get(L, g2['lod_tris'].get(str(L))), bytes=os.path.getsize(p))
check('lod_glb_tris', all(per_lod[L]['triangles'] == lod_stats[L]['triangles'] for L in (0, 1, 2)), per_lod)

# clean-scene re-import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
ri_tris, ri_meshes = {}, 0
mn = np.array([1e9] * 3); mx = np.array([-1e9] * 3)
for ob in bpy.data.objects:
    if ob.type != 'MESH' or ob.name.endswith('-convcolonly') or 'COL_' in ob.name:
        continue
    ri_meshes += 1
    me = ob.data; me.calc_loop_triangles()
    lod = next((L for L in (0, 1, 2) if f'_LOD{L}_' in ob.name), None)
    ri_tris[lod] = ri_tris.get(lod, 0) + len(me.loop_triangles)
    if lod == 0:
        for v in me.vertices:
            w = ob.matrix_world @ v.co
            mn = np.minimum(mn, np.array(w)); mx = np.maximum(mx, np.array(w))
ri_ok_img = all(im.size[0] > 0 for im in bpy.data.images if im.name not in ('Render Result', 'Viewer Node'))
ri_size = (mx - mn).round(3).tolist()
check('reimport_meshes', ri_meshes > 20, ri_meshes)
check('reimport_tris', all(ri_tris.get(L) == lod_stats[L]['triangles'] for L in (0, 1, 2)), ri_tris)
check('reimport_bounds', max(abs(ri_size[i] - b0['size'][i]) for i in range(3)) < 0.05, dict(reimport=ri_size, blend=b0['size']))
check('reimport_textures', ri_ok_img and len(bpy.data.images) > 0, f'{len(bpy.data.images)} images')
rep['glb'] = dict(bytes=os.path.getsize(glb), lod_triangles=lt, lod_files=per_lod, materials=gr['materials'], alpha_blend=gr['alpha_blend'],
                  images=dec, extensions=gr['extensions'], lights=gr['lights'], nodes=gr['nodes'], meshes=gr['meshes'],
                  primitives=gr['primitives'], collision_nodes=len(gr['collision_nodes']), reimport=dict(meshes=ri_meshes, tris=ri_tris, size=ri_size))
rep['files'] = dict(blend_bytes=os.path.getsize(f'{store_dir}/{base}.blend'), glb_bytes=os.path.getsize(glb))
rep['passed'] = len(rep['errors']) == 0
with open(f'{store_dir}/validation.json', 'w') as f:
    json.dump(rep, f, indent=1)
print('VALIDATION', 'PASS' if rep['passed'] else 'FAIL', base, 'LOD tris', lt, 'errors:', rep['errors'], 'warnings:', rep['warnings'])
