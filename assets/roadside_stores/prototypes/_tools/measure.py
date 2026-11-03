"""Measure the three prototypes from the actual .blend and .glb files on disk.

Writes ../MEASUREMENTS.md and ../measurements.json. Every number here is computed, not estimated,
except the clearly-labelled GPU texture memory estimates (formula shown in the report).
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import roadside_lib as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
ASSETS = [('enoc', 'enoc_service_station', 'ENOC'), ('starbucks', 'starbucks_drive_thru', 'SBX'),
          ('zoom', 'zoom_convenience_store', 'ZOOM')]
MIP = 4.0 / 3.0


def mib(b):
    return b / (1024 * 1024)


def measure(folder, base, prefix):
    d = f'{ROOT}/{folder}'
    blend, glb = f'{d}/source/{base}.blend', f'{d}/{base}.glb'
    bpy.ops.wm.open_mainfile(filepath=blend)
    out = dict(asset=base, blend_path=os.path.relpath(blend, ROOT), glb_path=os.path.relpath(glb, ROOT),
               blend_bytes=os.path.getsize(blend), glb_bytes=os.path.getsize(glb), lods={})
    all_mats, images = set(), {}
    for L in (0, 1, 2):
        c = bpy.data.collections[f'{prefix}_LOD{L}']
        objs, mats, tris, verts = {}, set(), 0, 0
        for ob in c.all_objects:
            if ob.type != 'MESH':
                continue
            me = ob.data
            me.calc_loop_triangles()
            t = len(me.loop_triangles)
            objs[ob.name] = t
            tris += t
            verts += len(me.vertices)
            for m in me.materials:
                if m:
                    mats.add(m.name)
        out['lods'][L] = dict(triangles=tris, vertices=verts, mesh_objects=len(objs), materials=len(mats), objects=objs,
                              visibility_range=list(R.LOD_RANGES[L]))
        all_mats |= mats
    for mn in sorted(all_mats):
        m = bpy.data.materials[mn]
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                im = n.image
                w, h = im.size
                normal = im.colorspace_settings.name == 'Non-Color' and 'normal' in im.name
                fpath = bpy.path.abspath(im.filepath)
                images[im.name] = dict(
                    file=os.path.relpath(fpath, d), width=w, height=h, file_bytes=os.path.getsize(fpath),
                    rgba8_mips_mib=round(mib(w * h * 4 * MIP), 2),
                    vram_bc_mips_mib=round(mib(w * h * (1.0 if normal else 0.5) * MIP), 2),
                    used_by=sorted(set(images.get(im.name, {}).get('used_by', [])) | {mn}))
    out['materials_total'] = len(all_mats)
    out['material_names'] = sorted(all_mats)
    out['textures'] = images
    out['texture_rgba8_mib_total'] = round(sum(i['rgba8_mips_mib'] for i in images.values()), 2)
    out['texture_vram_bc_mib_total'] = round(sum(i['vram_bc_mips_mib'] for i in images.values()), 2)
    out['collision_shapes'] = len([o for o in bpy.data.collections[f'{prefix}_Collision'].all_objects if o.type == 'MESH'])
    out['night_lights'] = len([o for o in bpy.data.collections[f'{prefix}_NightLights'].all_objects if o.type == 'LIGHT'])
    out['glb'] = R.gltf_report(glb)
    log = f'{d}/source/build_log.txt'
    warns = []
    if os.path.exists(log):
        for line in open(log, errors='replace'):
            if re.search(r'WARNING|ERROR|Error', line):
                w = re.sub(r'^\d\d:\d\d:\d\d \| ', '', line.strip())
                if w not in warns:
                    warns.append(w)
    out['export_warnings'] = warns
    return out


def md(results):
    L = ['# Roadside store prototypes - measured results', '',
         'All values below were measured by `_tools/measure.py` from the files on disk '
         '(Blender 4.5.15 LTS, `bpy` module). Triangle counts come from Blender loop triangles and are cross-checked '
         'against the index counts inside the exported `.glb`.', '']
    L += ['## Triangle counts per LOD', '',
          '| Asset | LOD0 | LOD1 | LOD2 | LOD1 / LOD0 | LOD2 / LOD0 | GLB check (LOD0 / LOD1 / LOD2) |',
          '|---|---:|---:|---:|---:|---:|---|']
    for r in results:
        t = [r['lods'][k]['triangles'] for k in (0, 1, 2)]
        g = r['glb']['lod_tris']
        gk = lambda k: g.get(k, g.get(str(k), 0))
        L.append(f"| {r['asset']} | {t[0]:,} | {t[1]:,} | {t[2]:,} | {t[1] / t[0]:.0%} | {t[2] / t[0]:.1%} | "
                 f"{gk(0):,} / {gk(1):,} / {gk(2):,} |")
    L += ['', 'Visibility ranges written into the LOD empties (glTF extras): ' +
          ', '.join(f'LOD{k}: {a:.0f}-{b:.0f} m' for k, (a, b) in R.LOD_RANGES.items()) + f', margin {R.LOD_MARGIN:.0f} m.', '']
    L += ['## Files, materials, textures', '',
          '| Asset | .glb size | .blend size | Materials (all LODs) | Textures | Texture memory, RGBA8 + mips | Est. VRAM-compressed + mips | Collision shapes | Night lights |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in results:
        L.append(f"| {r['asset']} | {mib(r['glb_bytes']):.2f} MiB | {mib(r['blend_bytes']):.2f} MiB | {r['materials_total']} | "
                 f"{len(r['textures'])} | {r['texture_rgba8_mib_total']} MiB | {r['texture_vram_bc_mib_total']} MiB | "
                 f"{r['collision_shapes']} | {r['night_lights']} |")
    L += ['', 'Texture memory: "RGBA8 + mips" = width x height x 4 bytes x 4/3. "VRAM-compressed" assumes Godot\'s '
          'default desktop VRAM compression (BC1/DXT1 at 0.5 B/px for colour and ORM maps, BC5/RGTC at 1 B/px for normal maps) '
          'x 4/3 for mipmaps. This is an estimate from the formula, not a measurement inside Godot.', '']
    for r in results:
        L += [f"### {r['asset']}", '',
              f"- Materials per LOD: " + ', '.join(f"LOD{k}: {r['lods'][k]['materials']}" for k in (0, 1, 2)),
              f"- Mesh objects per LOD: " + ', '.join(f"LOD{k}: {r['lods'][k]['mesh_objects']}" for k in (0, 1, 2)),
              f"- GLB: {r['glb']['nodes']} nodes, {r['glb']['meshes']} meshes, {r['glb']['primitives']} primitives (surfaces), "
              f"{r['glb']['materials']} materials, {len(r['glb']['images'])} embedded images, {r['glb']['lights']} punctual lights",
              f"- glTF extensions used: {', '.join(r['glb']['extensions'])}",
              f"- Alpha-blended materials: {', '.join(r['glb']['alpha_blend']) or 'none'}; double-sided: {', '.join(r['glb']['double_sided']) or 'none'}",
              '- Export warnings: ' + ('; '.join(f'`{w}`' for w in r['export_warnings']) if r['export_warnings'] else 'none'),
              '', '| Texture | Size | File | RGBA8+mips | Est. VRAM+mips |', '|---|---|---:|---:|---:|']
        for n, t in sorted(r['textures'].items()):
            L.append(f"| {t['file']} | {t['width']}x{t['height']} | {t['file_bytes'] / 1024:.0f} KiB | {t['rgba8_mips_mib']} MiB | {t['vram_bc_mips_mib']} MiB |")
        L += ['', '<details><summary>Per-object triangle counts</summary>', '']
        for k in (0, 1, 2):
            L.append(f'**LOD{k}**: ' + ', '.join(f'{n.split("_", 2)[-1]} {t:,}' for n, t in sorted(r['lods'][k]['objects'].items())))
            L.append('')
        L += ['</details>', '']
    return '\n'.join(L)


results = [measure(*a) for a in ASSETS]
with open(f'{ROOT}/measurements.json', 'w') as f:
    json.dump(results, f, indent=1, default=str)
with open(f'{ROOT}/MEASUREMENTS.md', 'w') as f:
    f.write(md(results))
for r in results:
    print(r['asset'], {k: v['triangles'] for k, v in r['lods'].items()}, 'glb', r['glb']['lod_tris'],
          f"{mib(r['glb_bytes']):.2f}MiB", 'warnings', len(r['export_warnings']))
