"""Validate the corrected flagship signage in FRESH Blender processes.

Usage: python validate_brand_fix.py <ORIG_GLB_ROOT>
  ORIG_GLB_ROOT = folder holding the pre-correction GLBs at the same relative paths (e.g. extracted with
  `git show <base-commit>:<path>`), used for the node-by-node "nothing but signage changed" diff.
Writes ../brand_fix_validation.json and <flagship>/brand_signage_correction.json.
"""
import os, sys, json, subprocess, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.normpath(os.path.join(HERE, '..'))
P17 = os.path.normpath(os.path.join(FIX, '..'))
sys.path.insert(0, HERE)
import glb_stats

if len(sys.argv) > 2 and sys.argv[1] == '--one':
    # ---------------- child process: inspect one .blend
    import bpy, bmesh
    from mathutils import Vector
    num = sys.argv[2]
    os.environ.setdefault('BR_PYLIB', '')
    from apply_brand_fix import SPECS, MANI, read_layers, flatten
    import numpy as np
    sp = SPECS[num]
    blend = os.path.join(P17, sp['folder'], sp['base'] + '.blend')
    bpy.ops.wm.open_mainfile(filepath=blend)
    P = sp['P']
    out = dict(asset=sp['folder'], issues=[], checks={})
    ch = out['checks']
    colls = {c.name: c for c in bpy.data.collections}
    names = ['BRAND_SIGNAGE_CORRECTED', 'LOD1_BRAND_SIGNAGE_CORRECTED', 'LOD2_BRAND_SIGNAGE_CORRECTED']
    parents = {'BRAND_SIGNAGE_CORRECTED': 'LOD0', 'LOD1_BRAND_SIGNAGE_CORRECTED': 'LOD1', 'LOD2_BRAND_SIGNAGE_CORRECTED': 'LOD2'}
    ch['collections'] = {}
    for n in names:
        c = colls.get(n)
        par = [p.name for p in bpy.data.collections if c and c.name in p.children]
        ch['collections'][n] = dict(present=bool(c), parent=par, objects=sorted(o.name for o in c.objects) if c else [])
        if not c or parents[n] not in par:
            out['issues'].append(f'{n} missing or not inside {parents[n]}')
    dis = colls.get('BRAND_SIGNAGE_ORIGINAL_DISABLED')
    lc = bpy.context.view_layer.layer_collection.children.get('BRAND_SIGNAGE_ORIGINAL_DISABLED')
    root = [o for o in bpy.data.objects if o.parent is None and o.type == 'EMPTY' and o.get('brand_signs')][0]
    asset_objs = set(root.users_collection[0].all_objects)
    ch['original_signage_disabled'] = dict(present=bool(dis), excluded_from_view_layer=bool(lc and lc.exclude),
                                           objects=sorted(o.name for o in dis.objects) if dis else [],
                                           any_in_export_tree=any(o in asset_objs for o in (dis.objects if dis else [])))
    if not dis or ch['original_signage_disabled']['any_in_export_tree']:
        out['issues'].append('original signage not cleanly disabled')
    ch['old_brand_objects_remaining_in_lods'] = [o.name for o in asset_objs if o.name.endswith('_SIGNAGE_Brand')]
    if ch['old_brand_objects_remaining_in_lods']:
        out['issues'].append('old SIGNAGE_Brand objects still exported')
    # mesh integrity + measured proportions
    ch['elements'] = []
    for e in sp['elements']:
        n = Vector(e.get('n', (0, -1, 0))).normalized(); up = Vector((0, 0, 1)); r = up.cross(n).normalized(); o = Vector(e['o'])
        row = dict(element=e['name'], logo=e['logo'], lods={})
        for L in (0, 1, 2):
            ob = bpy.data.objects.get(f'{P}_LOD{L}_BRAND_SIGNAGE_CORRECTED_{e["name"]}')
            if ob is None:
                out['issues'].append(f'{e["name"]} LOD{L} missing'); continue
            me = ob.data
            bad = me.validate(verbose=False, clean_customdata=False)
            tris = sum(len(p.vertices) - 2 for p in me.polygons)
            mats = [m.name if m else None for m in me.materials]
            if None in mats:
                out['issues'].append(f'{ob.name} empty material slot')
            us, ws = [], []
            for p in me.polygons:
                m = me.materials[p.material_index]
                if m and m.name == 'BR_SignBack' and e.get('rail'):
                    continue
                for vi in p.vertices:
                    v = ob.matrix_world @ me.vertices[vi].co - o
                    us.append(v.dot(r)); ws.append(v.dot(up))
            W, H = max(us) - min(us), max(ws) - min(ws)
            row['lods'][f'LOD{L}'] = dict(object=ob.name, tris=tris, validate_changed=bool(bad), width_m=round(W, 3), height_m=round(H, 3),
                                          materials=mats, uv=bool(me.uv_layers))
            if bad:
                out['issues'].append(f'{ob.name} mesh.validate() changed data')
        vb, lays = read_layers(os.path.join(FIX, MANI[e['logo']]['svg']))
        pts = np.vstack([a for (_lid, _f, d) in lays for a in flatten(d, vb[2] / 4000.0)])
        src_aspect = float(np.ptp(pts[:, 0]) / np.ptp(pts[:, 1]))          # ink bounds of the source vector
        l0 = row['lods'].get('LOD0')
        if l0:
            meas = l0['width_m'] / l0['height_m']
            row['source_vector_aspect'] = round(src_aspect, 4)
            row['measured_aspect_LOD0'] = round(meas, 4)
            row['aspect_error_pct'] = round(abs(meas / src_aspect - 1) * 100, 2)
            if row['aspect_error_pct'] > 1.5:
                out['issues'].append(f'{e["name"]} proportion error {row["aspect_error_pct"]}%')
        ch['elements'].append(row)
    imgs = sorted({bpy.path.abspath(i.filepath) for i in bpy.data.images if i.filepath and 'brand_' in i.filepath})
    ch['brand_textures'] = [dict(file=os.path.relpath(p, P17), exists=os.path.exists(p)) for p in imgs]
    if not all(t['exists'] for t in ch['brand_textures']):
        out['issues'].append('missing brand texture')
    ch['brand_signs_extras'] = json.loads(root['brand_signs'])
    print('RESULT ' + json.dumps(out))
    sys.exit(0)

# ---------------- parent: run each asset in its own process, add GLB diffs
from apply_brand_fix import SPECS
orig_root = sys.argv[1]
report = dict(assets={}, all_passed=True)
for num, sp in SPECS.items():
    r = subprocess.run([sys.executable, os.path.abspath(__file__), '--one', num], capture_output=True, text=True,
                       env=dict(os.environ))
    line = [l for l in r.stdout.splitlines() if l.startswith('RESULT ')]
    res = json.loads(line[0][7:]) if line else dict(issues=['child failed: ' + r.stderr[-400:]], checks={})
    adir = os.path.join(P17, sp['folder'])
    diffs = {}
    for rel in [sp['base'] + '.glb', sp['base'] + '_building_only.glb'] + [f'lod/{sp["base"]}_lod{L}.glb' for L in (0, 1, 2)]:
        new = os.path.join(adir, rel)
        old = os.path.join(orig_root, 'assets/roadside_stores/premium_commercial_17', sp['folder'], rel)
        if not os.path.exists(new):
            continue
        a, b = glb_stats.stats(old), glb_stats.stats(new)
        changed = {k for k in set(a['nodes']) | set(b['nodes']) if a['nodes'].get(k) != b['nodes'].get(k)}
        non_sig = sorted(k for k in changed if 'SIGNAGE' not in k)
        diffs[rel] = dict(tris_before=a['total'], tris_after=b['total'], non_signage_nodes_changed=non_sig,
                          signage_nodes_before=sorted(k for k in a['nodes'] if 'SIGNAGE' in k),
                          signage_nodes_after=sorted(k for k in b['nodes'] if 'SIGNAGE' in k),
                          lights=(a['lights'], b['lights']), images=(a['images'], b['images']),
                          size_mb=round(os.path.getsize(new) / 1e6, 2))
        if non_sig or a['lights'] != b['lights']:
            res['issues'].append(f'{rel}: non-signage nodes changed {non_sig[:5]}')
    res['checks']['glb_diff_vs_original'] = diffs
    res['passed'] = not res['issues']
    report['all_passed'] &= res['passed']
    report['assets'][num] = res
    json.dump(res, open(os.path.join(adir, 'brand_signage_correction.json'), 'w'), indent=1)
    print('VALIDATED', num, 'PASS' if res['passed'] else 'FAIL', res['issues'][:4])
json.dump(report, open(os.path.join(FIX, 'brand_fix_validation.json'), 'w'), indent=1)
