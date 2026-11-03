"""Validate one premium asset in a FRESH Blender process: reopen .blend, inspect, re-import the GLB into a clean scene.

Usage: python validate_asset.py <asset_dir> <basename>      -> writes <asset_dir>/validation.json
"""
import os, sys, json, struct, io, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
import numpy as np
from PIL import Image
import pk_core as C
R, K = C.R, C.K

asset_dir, base = sys.argv[1], sys.argv[2]
blend = f'{asset_dir}/{base}.blend'
glb = f'{asset_dir}/{base}.glb'
bonly = f'{asset_dir}/{base}_building_only.glb'
out = dict(asset=base, checks={}, issues=[], warnings=[])
chk = out['checks']

bpy.ops.wm.open_mainfile(filepath=blend)
root = [o for o in bpy.data.objects if 'preview_cameras' in o.keys()][0]
meta = json.loads(root['meta'])
colls = {c.name: c for c in bpy.data.collections}
prefix = root.name.split('_')[0]

# ---------------------------------------------------------------- collections / hierarchy
need = ['LOD0', 'LOD1', 'LOD2', 'PLACEHOLDER_CARS', 'INTERIOR_LIGHTING', 'EXTERIOR_LIGHTING', 'COLLISION', 'SIDEWALK_FRONTAGE',
        'OPTIONAL_FORECOURT', 'DRIVEWAY', 'OPTIONAL_PARKING', 'BUILDING_EXTERIOR', 'BUILDING_INTERIOR', 'GLASS_SYSTEM', 'SIGNAGE']
chk['collections_present'] = {n: n in colls for n in need}
for n, ok in chk['collections_present'].items():
    if not ok and n not in ('OPTIONAL_PARKING', 'OPTIONAL_FORECOURT', 'DRIVEWAY'):
        out['issues'].append(f'missing collection {n}')

lod_objs = {L: [o for o in colls[f'LOD{L}'].all_objects if o.type == 'MESH'] for L in (0, 1, 2)}
car_objs = [o for o in colls['PLACEHOLDER_CARS'].all_objects if o.type == 'MESH']
site_objs = [o for n in ('SIDEWALK_FRONTAGE', 'OPTIONAL_FORECOURT', 'DRIVEWAY', 'OPTIONAL_PARKING') if n in colls
             for o in colls[n].all_objects if o.type == 'MESH']
col_objs = [o for o in colls['COLLISION'].all_objects if o.type == 'MESH']
all_mesh = [o for o in colls[root.users_collection[0].name].all_objects if o.type == 'MESH' and o not in col_objs]


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


# ---------------------------------------------------------------- mesh integrity, normals, transforms, materials, UVs
bad_validate, degenerate, flipped, no_uv, zero_uv, bad_mat, nonunit = [], 0, 0, [], 0, [], []
for o in all_mesh:
    me = o.data
    if me.validate(verbose=False, clean_customdata=False):
        bad_validate.append(o.name)
    bm = bmesh.new(); bm.from_mesh(me)
    degenerate += sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    flipped += K.orient_closed_pieces(bm.copy())
    bm.free()
    if not me.uv_layers:
        no_uv.append(o.name)
    else:
        uv = np.zeros(len(me.loops) * 2); me.uv_layers[0].data.foreach_get('uv', uv)
        if not np.isfinite(uv).all():
            no_uv.append(o.name + ' (nan)')
    if not me.materials or any(m is None for m in me.materials):
        bad_mat.append(o.name)
    if o in car_objs:
        if any(abs(s - 1) > 1e-6 for s in o.scale):
            nonunit.append(o.name)
    elif any(abs(s - 1) > 1e-6 for s in o.scale) or any(abs(r) > 1e-6 for r in o.rotation_euler) or o.location.length > 1e-6:
        nonunit.append(o.name)
chk['mesh_validate_errors'] = bad_validate
chk['degenerate_faces'] = degenerate
chk['closed_pieces_with_inverted_normals_faces'] = flipped
chk['meshes_without_uv'] = no_uv
chk['meshes_with_missing_materials'] = bad_mat
chk['objects_with_unapplied_transforms'] = nonunit
for k in ('mesh_validate_errors', 'meshes_without_uv', 'meshes_with_missing_materials', 'objects_with_unapplied_transforms'):
    if chk[k]:
        out['issues'].append(f'{k}: {chk[k][:5]}')
if flipped:
    out['warnings'].append(f'{flipped} faces in watertight pieces have inverted winding')

# ---------------------------------------------------------------- dimensions
def bbox(objs):
    mn = np.array([1e9] * 3); mx = -mn
    for o in objs:
        for v in o.data.vertices:
            p = o.matrix_world @ v.co
            mn = np.minimum(mn, p); mx = np.maximum(mx, p)
    return mn, mx


bld = [o for o in lod_objs[0]]
mn, mx = bbox(bld)
chk['lod0_bounds_m'] = dict(min=[round(v, 2) for v in mn], max=[round(v, 2) for v in mx], size=[round(v, 2) for v in (mx - mn)])
fp = meta.get('footprint')
if fp:
    chk['footprint_m'] = dict(width=round(fp[2] - fp[0], 2), depth=round(fp[3] - fp[1], 2))
chk['height_m'] = round(float(mx[2]), 2)
if not (3.0 < mx[2] < 60.0) or (mx - mn)[0] > 200:
    out['issues'].append('implausible dimensions')

# ---------------------------------------------------------------- glass transparency
glass = {}
for m in bpy.data.materials:
    if 'Glass' in m.name and 'Car' not in m.name and m.users:
        b = m.node_tree.nodes.get('Principled BSDF')
        a = b.inputs['Alpha'].default_value if b else 1.0
        glass[m.name] = dict(alpha=round(a, 3), blend=m.blend_method, double_sided=not m.use_backface_culling)
        if a >= 0.95:
            out['issues'].append(f'glass {m.name} is opaque')
chk['glass_materials'] = glass

# ---------------------------------------------------------------- interior / LOD / cars
def comp_tris(L, comps):
    return sum(tris(o) for o in lod_objs[L] if any(f'_{c}_' in o.name for c in comps))


chk['lod_tris_blender'] = {f'LOD{L}': sum(tris(o) for o in lod_objs[L]) for L in (0, 1, 2)}
chk['interior_tris_lod0'] = comp_tris(0, ['BUILDING_INTERIOR', 'FURNITURE', 'DISPLAY_OBJECTS'])
chk['interior_tris_lod1'] = comp_tris(1, ['BUILDING_INTERIOR', 'FURNITURE', 'DISPLAY_OBJECTS'])
chk['interior_objects_lod0'] = sorted(o.name for o in lod_objs[0] if any(f'_{c}_' in o.name for c in ['BUILDING_INTERIOR', 'FURNITURE', 'DISPLAY_OBJECTS']))
if chk['interior_tris_lod0'] < 2000:
    out['issues'].append('interior geometry too sparse')
t = chk['lod_tris_blender']
if not (t['LOD0'] > t['LOD1'] > t['LOD2']):
    out['issues'].append('LOD triangle counts not decreasing')
lod_ex = {}
for L in (0, 1, 2):
    e = bpy.data.objects[f'{prefix}_LOD{L}']
    lod_ex[f'LOD{L}'] = dict(level=e.get('lod_level'), begin=e.get('visibility_range_begin'), end=e.get('visibility_range_end'))
chk['lod_extras'] = lod_ex
car_root = bpy.data.objects.get(f'{prefix}_PLACEHOLDER_CARS')
cars_ok = all(o.parent == car_root for o in car_objs)
shared = [o.name for o in car_objs if o.data.users > 1]
in_lod = [o.name for o in car_objs if any(o.name in colls[f'LOD{L}'].all_objects for L in (0, 1, 2))]
chk['placeholder_cars'] = dict(count=len(car_objs), parented_to_cars_node=cars_ok, shared_mesh=shared, inside_lod_collections=in_lod,
                               names=[o.name for o in car_objs])
if not cars_ok or shared or in_lod:
    out['issues'].append('placeholder cars not cleanly separated')
chk['lights'] = {n: len([o for o in colls[n].all_objects if o.type == 'LIGHT']) for n in ('INTERIOR_LIGHTING', 'EXTERIOR_LIGHTING')}
chk['collision_boxes'] = len([o for o in colls['COLLISION'].all_objects if o.type == 'MESH'])
chk['materials_used'] = sorted({m.name for o in all_mesh for m in o.data.materials if m})
chk['image_textures'] = sorted({i.filepath for i in bpy.data.images if i.users and i.filepath})
missing_img = [i.filepath for i in bpy.data.images if i.users and i.filepath and not os.path.exists(bpy.path.abspath(i.filepath))]
chk['missing_image_files'] = missing_img
if missing_img:
    out['issues'].append(f'missing textures {missing_img[:3]}')
veg = [o.name for o in all_mesh if any(k in o.name.lower() for k in ('palm', 'tree', 'hedge', 'bush', 'shrub', 'foliage'))]
veg += [m for m in chk['materials_used'] if 'Foliage' in m or 'Palm' in m]
chk['vegetation_objects_or_materials'] = veg
if veg:
    out['issues'].append('vegetation found')

# ---------------------------------------------------------------- GLB: parse, decode textures, re-import into a clean scene
def glb_json(path):
    data = open(path, 'rb').read()
    jl = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jl])
    binoff = 20 + jl + 8
    return js, data, binoff


def glb_tris(path):
    rep = R.gltf_report(path)
    js, data, binoff = glb_json(path)
    acc = js['accessors']; meshes = js.get('meshes', []); nodes = js['nodes']

    def mt(mi):
        return sum(acc[p['indices']]['count'] // 3 if 'indices' in p else acc[p['attributes']['POSITION']]['count'] // 3
                   for p in meshes[mi]['primitives'])
    groups = {}

    def walk(ni, g):
        n = nodes[ni]; nm = n.get('name', '')
        for key in ('_LOD0', '_LOD1', '_LOD2', '_PLACEHOLDER_CARS', '_SIDEWALK_FRONTAGE', '_OPTIONAL_FORECOURT', '_DRIVEWAY', '_OPTIONAL_PARKING', '_Collision'):
            if nm.endswith(key):
                g = key[1:]
        if 'mesh' in n and g:
            groups[g] = groups.get(g, 0) + mt(n['mesh'])
        for c in n.get('children', []):
            walk(c, g)
    for s in js['scenes']:
        for ni in s['nodes']:
            walk(ni, None)
    imgs = []
    for im in js.get('images', []):
        bv = js['bufferViews'][im['bufferView']]
        raw = data[binoff + bv.get('byteOffset', 0): binoff + bv.get('byteOffset', 0) + bv['byteLength']]
        try:
            pi = Image.open(io.BytesIO(raw)); pi.load()
            imgs.append(dict(name=im.get('name'), mime=im.get('mimeType'), size=list(pi.size), ok=True))
        except Exception as e:
            imgs.append(dict(name=im.get('name'), ok=False, err=str(e)))
    return dict(groups=groups, total=sum(groups.values()), images=imgs, materials=rep['materials'], alpha_blend=rep['alpha_blend'],
                lights=rep['lights'], collision_nodes=len(rep['collision_nodes']), nodes=rep['nodes'], meshes=rep['meshes'],
                primitives=rep['primitives'], lod_extras=rep['lod_extras'], car_nodes=len([n for n in js['nodes'] if '_CAR_' in n.get('name', '')]),
                size_mb=round(os.path.getsize(path) / 1e6, 2))


g_full = glb_tris(glb)
g_bonly = glb_tris(bonly) if os.path.exists(bonly) else dict(total=None, car_nodes=0, size_mb=None, note='no cars in this asset - main GLB is building-only')
lodfiles = {}
for L in (0, 1, 2):
    p = f'{asset_dir}/lod/{base}_lod{L}.glb'
    lodfiles[f'LOD{L}'] = glb_tris(p)['total'] if os.path.exists(p) else None
chk['glb_full'] = g_full
chk['glb_building_only'] = dict(total=g_bonly['total'], car_nodes=g_bonly['car_nodes'], size_mb=g_bonly['size_mb'], note=g_bonly.get('note'))
chk['glb_lod_files_tris'] = lodfiles
if g_bonly['car_nodes']:
    out['issues'].append('building-only GLB contains cars')
if not all(i['ok'] for i in g_full['images']):
    out['issues'].append('undecodable texture in GLB')
for L in (0, 1, 2):
    if g_full['groups'].get(f'LOD{L}') != chk['lod_tris_blender'][f'LOD{L}']:
        out['warnings'].append(f'LOD{L} tris GLB {g_full["groups"].get(f"LOD{L}")} != Blender {chk["lod_tris_blender"][f"LOD{L}"]}')

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
imp = [o for o in bpy.data.objects if o.type == 'MESH']
dg = bpy.context.evaluated_depsgraph_get()
imp_tris = 0
for o in imp:
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    imp_tris += len(me.loop_triangles)
    o.evaluated_get(dg).to_mesh_clear()
imgs_loaded = [i for i in bpy.data.images if i.size[0] > 0]
mn2 = np.array([1e9] * 3); mx2 = -mn2
for o in imp:
    if '_LOD0' in o.name or (o.parent and o.parent.name.endswith('_LOD0')):
        for c in o.bound_box:
            p = o.matrix_world @ __import__('mathutils').Vector(c)
            mn2 = np.minimum(mn2, p); mx2 = np.maximum(mx2, p)
chk['reimport'] = dict(mesh_objects=len(imp), triangles=imp_tris, glb_triangles=g_full['total'], images_loaded=len(imgs_loaded),
                       lights=len([o for o in bpy.data.objects if o.type == 'LIGHT']),
                       lod0_size_yup_converted=[round(float(v), 2) for v in (mx2 - mn2)] if imp else None)
if imp_tris != g_full['total']:
    out['warnings'].append(f'reimport triangles {imp_tris} != glb {g_full["total"]}')
out['passed'] = not out['issues']
json.dump(out, open(f'{asset_dir}/validation.json', 'w'), indent=1)
print('VALIDATION', base, 'PASS' if out['passed'] else 'FAIL', json.dumps(out['issues']), json.dumps(out['warnings'])[:400])
