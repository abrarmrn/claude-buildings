"""Assemble gallery, catalog (JPG + offline HTML), manifest, per-store READMEs and the build report.

Usage: python make_reports.py            (pure Python + Pillow; run after build/validate/render)
Everything is computed from files on disk: validation.json, lod/build_stats.json, renders/render_report.json, the images.
"""
import os, sys, json, shutil, html, datetime
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A17 = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from registry import STORES

GALLERY = f'{A17}/PREVIEW_GALLERY'
VIEWS = [('day', 'Day, three-quarter'), ('night', 'Night, illuminated'), ('road_view', 'Road level (driver height)'), ('detail', 'Facade / entrance / signage detail')]
BATCHES = {'A': ['01', '02', '03', '04'], 'B': ['05', '06', '07', '08', '09'], 'C': ['10', '11', '12', '13'], 'D': ['14', '15', '16', '17']}
FONT = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
FONTB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONTR = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'


def jload(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else default


def mib(b):
    return round(b / 1048576, 2)


def collect():
    out = []
    for s in STORES:
        d = f"{A17}/{s['folder']}"
        v = jload(f'{d}/validation.json', {})
        bs = jload(f'{d}/lod/build_stats.json', {})
        rr = jload(f'{d}/renders/render_report.json', {})
        imgs = {}
        for k, _ in VIEWS:
            p = f"{d}/renders/{s['base']}_{k}.jpg"
            ok = os.path.exists(p)
            size = None
            if ok:
                try:
                    with Image.open(p) as im:
                        size = list(im.size)
                except Exception:
                    ok = False
            imgs[k] = dict(path=f"{s['folder']}/renders/{s['base']}_{k}.jpg", exists=ok, size=size, bytes=os.path.getsize(p) if ok else 0)
        files = {}
        for name, rel in (('blend', f"{s['base']}.blend"), ('glb', f"{s['base']}.glb"), ('lod0_glb', f"lod/{s['base']}_lod0.glb"),
                          ('lod1_glb', f"lod/{s['base']}_lod1.glb"), ('lod2_glb', f"lod/{s['base']}_lod2.glb")):
            p = f'{d}/{rel}'
            files[name] = dict(path=f"{s['folder']}/{rel}", bytes=os.path.getsize(p) if os.path.exists(p) else 0, exists=os.path.exists(p))
        tex_dir = f'{d}/textures'
        tex = sorted(os.listdir(tex_dir)) if os.path.isdir(tex_dir) else []
        tex = [t for t in tex if not t.startswith('.')]
        signs = rr.get('road_view_sign', [])
        sign_ok = any(x.get('readable') for x in signs)
        complete = bool(v.get('passed')) and all(i['exists'] and i['size'] == [1600, 900] for i in imgs.values()) and all(f['exists'] for f in files.values()) and sign_ok
        out.append(dict(reg=s, dir=d, val=v, stats=bs, render=rr, imgs=imgs, files=files, textures=tex, signs=signs, sign_ok=sign_ok, complete=complete))
    return out


def font(p, n):
    return ImageFont.truetype(p, n)


def gallery(data):
    os.makedirs(f'{GALLERY}/thumbs', exist_ok=True)
    n = 0
    for e in data:
        s = e['reg']
        for k, _ in VIEWS:
            if not e['imgs'][k]['exists']:
                continue
            src = f"{A17}/{e['imgs'][k]['path']}"
            dst = f"{GALLERY}/{s['num']}_{s['base']}_{k}.jpg"
            shutil.copyfile(src, dst)
            with Image.open(src) as im:
                im.convert('RGB').resize((640, 360), Image.LANCZOS).save(f"{GALLERY}/thumbs/{s['num']}_{s['base']}_{k}.jpg", quality=86)
            n += 1
    return n


def contact_sheet(data):
    cols, rows = 5, 4
    cw, ch, gap, lab, top = 384, 216, 14, 46, 92
    W = cols * cw + (cols + 1) * gap
    Hh = top + rows * (ch + lab) + (rows + 1) * gap + 40
    cv = Image.new('RGB', (W, Hh), (24, 26, 30))
    dr = ImageDraw.Draw(cv)
    dr.text((gap + 6, 20), 'Dubai Open World - 17 additional roadside store assets', font=font(FONTB, 34), fill=(255, 255, 255))
    done = sum(1 for e in data if e['complete'])
    dr.text((gap + 6, 62), f'Blender 4.5 LTS renders (Cycles) - day view shown - {done}/17 complete - full set: STORE_CATALOG_17.html', font=font(FONTR, 17), fill=(170, 176, 186))
    for i, e in enumerate(data):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = top + gap + r * (ch + lab + gap)
        p = f"{A17}/{e['imgs']['day']['path']}"
        if e['imgs']['day']['exists']:
            with Image.open(p) as im:
                t = im.convert('RGB').resize((cw, ch), Image.LANCZOS)
            cv.paste(t, (x, y))
            if e['imgs']['night']['exists']:
                with Image.open(f"{A17}/{e['imgs']['night']['path']}") as im:
                    nt = im.convert('RGB').resize((cw // 3, ch // 3), Image.LANCZOS)
                cv.paste(nt, (x + cw - cw // 3 - 6, y + ch - ch // 3 - 6))
                dr.rectangle([x + cw - cw // 3 - 6, y + ch - ch // 3 - 6, x + cw - 6, y + ch - 6], outline=(255, 255, 255), width=2)
        else:
            dr.rectangle([x, y, x + cw, y + ch], fill=(60, 30, 30))
            dr.text((x + 20, y + ch // 2 - 10), 'NOT RENDERED', font=font(FONTB, 26), fill=(255, 140, 140))
        s = e['reg']
        dr.rectangle([x, y + ch, x + cw, y + ch + lab], fill=(38, 41, 47))
        dr.text((x + 10, y + ch + 5), f"{s['num']}  {s['display']}", font=font(FONTB, 19), fill=(255, 255, 255))
        t0 = e['val'].get('glb', {}).get('lod_triangles', {})
        sub = f"{s['placement']}  |  LOD0 {int(t0.get('0', 0)):,} tris" if t0 else s['placement']
        dr.text((x + 10, y + ch + 27), sub, font=font(FONTR, 14), fill=(160, 168, 180))
        if not e['complete']:
            dr.rectangle([x, y, x + 150, y + 22], fill=(150, 40, 40))
            dr.text((x + 6, y + 2), 'INCOMPLETE', font=font(FONTB, 14), fill=(255, 255, 255))
    dr.text((gap + 6, Hh - 30), 'Previews are Blender renders of the actual models. Brand marks are simplified recreations, not official logo artwork.', font=font(FONTR, 14), fill=(130, 136, 146))
    cv.save(f'{A17}/STORE_CATALOG_17.jpg', quality=92)


def tri(e, L):
    return e['val'].get('glb', {}).get('lod_triangles', {}).get(str(L))


def html_gallery(data):
    cards = []
    for e in data:
        s = e['reg']
        imgs = ''
        for k, label in VIEWS:
            fn = f"{s['num']}_{s['base']}_{k}.jpg"
            if e['imgs'][k]['exists']:
                imgs += f'<figure><a href="PREVIEW_GALLERY/{fn}" target="_blank"><img loading="lazy" src="PREVIEW_GALLERY/thumbs/{fn}" alt="{html.escape(s["display"])} {label}"></a><figcaption>{label}</figcaption></figure>'
            else:
                imgs += f'<figure><div class="missing">not rendered</div><figcaption>{label}</figcaption></figure>'
        g = e['val'].get('glb', {})
        bb = e['val'].get('blend', {}).get('bounds', {}).get('0', {}).get('size')
        meta = (f"LOD0 {tri(e, 0):,} / LOD1 {tri(e, 1):,} / LOD2 {tri(e, 2):,} tris &middot; GLB {mib(e['files']['glb']['bytes'])} MiB &middot; "
                f".blend {mib(e['files']['blend']['bytes'])} MiB &middot; footprint {bb[0]:.0f} x {bb[1]:.0f} x {bb[2]:.1f} m") if tri(e, 0) else 'not measured'
        status = '<span class="ok">complete</span>' if e['complete'] else '<span class="bad">INCOMPLETE</span>'
        cards.append(f'''<section id="s{s['num']}"><h2><span class="n">{s['num']}</span> {html.escape(s['display'])} {status}</h2>
<p class="meta">{html.escape(s['placement'])} &middot; {meta}</p>
<p class="meta">Files: <a href="{s['folder']}/{s['base']}.glb">{s['base']}.glb</a> &middot; <a href="{s['folder']}/{s['base']}.blend">{s['base']}.blend</a> &middot; <a href="{s['folder']}/README.md">README</a></p>
<div class="grid">{imgs}</div><p class="note">{html.escape(s['brand_note'])}</p></section>''')
    nav = ' '.join(f'<a href="#s{e["reg"]["num"]}">{e["reg"]["num"]} {html.escape(e["reg"]["display"])}</a>' for e in data)
    done = sum(1 for e in data if e['complete'])
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dubai Open World - 17 roadside store assets</title>
<style>
:root{{color-scheme:dark}}body{{margin:0;background:#16181c;color:#e8eaee;font:15px/1.45 system-ui,Segoe UI,Arial,sans-serif}}
header{{padding:22px 28px;background:#1f2228;border-bottom:1px solid #333}}h1{{margin:0 0 4px;font-size:26px}}header p{{margin:4px 0;color:#9aa3b2}}
nav{{padding:12px 28px;display:flex;flex-wrap:wrap;gap:8px;background:#1a1d22;border-bottom:1px solid #2a2d33;position:sticky;top:0;z-index:5}}
nav a{{color:#9ecbff;text-decoration:none;font-size:13px;background:#242830;padding:4px 9px;border-radius:12px}}nav a:hover{{background:#2f3540}}
section{{padding:18px 28px 6px;border-bottom:1px solid #2a2d33}}h2{{margin:0 0 4px;font-size:21px}}.n{{display:inline-block;background:#2d6cdf;color:#fff;border-radius:6px;padding:0 8px;margin-right:6px;font-size:16px}}
.meta{{margin:2px 0;color:#9aa3b2;font-size:13px}}.meta a{{color:#9ecbff}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:12px;margin:12px 0}}
figure{{margin:0;background:#1f2228;border-radius:8px;overflow:hidden}}figure img{{display:block;width:100%;height:auto}}figcaption{{padding:6px 10px;font-size:12px;color:#aab3c2}}
.missing{{height:200px;display:flex;align-items:center;justify-content:center;color:#ff9a9a;background:#3a2020}}.note{{font-size:12px;color:#7f8897;margin:0 0 14px}}
.ok{{color:#6fe39a;font-size:12px;margin-left:8px}}.bad{{color:#ff8a8a;font-size:12px;margin-left:8px}}footer{{padding:20px 28px;color:#7f8897;font-size:12px}}
</style></head><body><header><h1>Dubai Open World - 17 additional roadside store assets</h1>
<p>{done}/17 complete &middot; Blender 4.5.15 LTS (Cycles) previews, 1600x900 &middot; click a thumbnail for the full-size JPEG &middot; works fully offline (relative paths only).</p>
<p>Master contact sheet: <a style="color:#9ecbff" href="STORE_CATALOG_17.jpg">STORE_CATALOG_17.jpg</a> &middot; Manifest: <a style="color:#9ecbff" href="STORE_ASSET_MANIFEST.json">STORE_ASSET_MANIFEST.json</a> &middot; Report: <a style="color:#9ecbff" href="BUILD_REPORT.md">BUILD_REPORT.md</a></p></header>
<nav>{nav}</nav>{''.join(cards)}
<footer>Renders are produced from the actual Blender models (no stock photography). Brand marks are simplified procedural recreations, not official logo artwork. Godot import has not been tested.</footer></body></html>'''
    open(f'{A17}/STORE_CATALOG_17.html', 'w', encoding='utf-8').write(page)


def manifest(data):
    items = []
    last = None
    for e in data:
        s = e['reg']
        v = e['val']
        b0 = v.get('blend', {}).get('bounds', {}).get('0', {})
        dims = v.get('blend', {}).get('declared_dimensions', {})
        g = v.get('glb', {})
        items.append(dict(
            id=s['num'], name=s['display'], brand=s['brand'], folder=f"assets/roadside_stores/additional_17/{s['folder']}", status='complete' if e['complete'] else 'incomplete',
            recommended_placement=dict(primary=s['placement'], alternatives=s['alt'],
                                       note='Reusable asset: not a geographic placement; real-world positions are handled separately from Dubai road/building data.'),
            dimensions_m=dict(lod0_bounding_box_xyz=b0.get('size'), lod0_min=b0.get('min'), lod0_max=b0.get('max'), declared=dims),
            triangles=dict(lod0=tri(e, 0), lod1=tri(e, 1), lod2=tri(e, 2), source='read back from exported GLB JSON (accessor index counts), cross-checked against Blender and re-import'),
            lod_ranges_m=dict(lod0=[0, 60], lod1=[60, 170], lod2=[170, 900]),
            files={k: dict(path=f['path'], bytes=f['bytes'], mib=mib(f['bytes'])) for k, f in e['files'].items()},
            materials=v.get('blend', {}).get('material_count'), texture_files=e['textures'], collision_proxies=v.get('blend', {}).get('collision_proxies'),
            glb=dict(materials=g.get('materials'), alpha_blend_materials=g.get('alpha_blend'), lights=g.get('lights'), nodes=g.get('nodes'), meshes=g.get('meshes'),
                     primitives=g.get('primitives'), extensions=g.get('extensions'), embedded_images=[dict(name=i.get('name'), size=i.get('size'), bytes=i.get('bytes')) for i in g.get('images', [])]),
            validation=dict(passed=v.get('passed'), failed_checks=v.get('errors'), warnings=v.get('warnings'), checks={k: c['ok'] for k, c in v.get('checks', {}).items()}),
            renders={k: dict(path=i['path'], size=i['size'], bytes=i['bytes']) for k, i in e['imgs'].items()},
            road_view_sign_check=e['signs'],
            brand_note=s['brand_note'], render_seconds={k: e['render'].get(f'{k}_seconds') for k, _ in VIEWS}))
        if e['complete']:
            last = s['num'] + ' ' + s['display']
    done = [i for i in items if i['status'] == 'complete']
    man = dict(
        project='Dubai Open World PC game - 17 additional roadside store assets', generated_utc=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        blender='4.5.15 LTS (bpy module)', conventions='1 unit = 1 m, Z up in Blender (Y up in glTF), road-facing front = Blender -Y = glTF/Godot +Z, origin = plot centre at finished ground; '
        'LOD nodes <PREFIX>_LOD0/1/2 with visibility-range extras (compatible with prototypes/roadside_lod_post_import.gd), collision *-convcolonly boxes, KHR_lights_punctual night lights (shadows off).',
        godot_import_tested=False,
        checkpoint=dict(last_completed_asset=last, completed=len(done), total=len(items), remaining=[i['id'] + ' ' + i['name'] for i in items if i['status'] != 'complete'],
                        batches={b: [i['id'] for i in items if i['id'] in ids and i['status'] == 'complete'] for b, ids in BATCHES.items()}),
        totals=dict(stores=len(items), complete=len(done), jpeg_renders=sum(1 for i in items for r in i['renders'].values() if r['size'] == [1600, 900]),
                    glb_files=sum(1 for i in items if i['files']['glb']['bytes']), blend_files=sum(1 for i in items if i['files']['blend']['bytes'])),
        assets=items)
    json.dump(man, open(f'{A17}/STORE_ASSET_MANIFEST.json', 'w'), indent=1)
    return man


def store_readme(e):
    s = e['reg']
    v = e['val']
    b = v.get('blend', {})
    b0 = b.get('bounds', {}).get('0', {}).get('size', [0, 0, 0])
    g = v.get('glb', {})
    lt = g.get('lod_triangles', {})
    lf = g.get('lod_files', {})
    mats = b.get('materials', [])
    brand = [m for m in mats if not m.startswith('RS_')]
    sign = e['signs']
    sg = '\n'.join(f"- {x['name']}: {x['pixel_height']} px letter height at 1600x900, {int(x['visible_fraction'] * 100)} % visible, {'readable' if x['readable'] else 'not primary'}" for x in sign) or '- not measured'
    txt = f'''# {s['num']} - {s['display']}

**Status:** {'complete (all validation checks passed, 4 renders produced)' if e['complete'] else 'INCOMPLETE - see BUILD_REPORT.md'}
**Recommended commercial placement:** {s['placement']} (alternatives: {', '.join(s['alt'])}). This is a reusable asset, not a geographic location.

## Files
| File | Purpose | Size |
|---|---|---:|
| `{s['base']}.glb` | Godot import file: all three LODs, collision proxies, night lights, embedded textures | {mib(e['files']['glb']['bytes'])} MiB |
| `{s['base']}.blend` | Editable Blender 4.5 LTS source (textures referenced from `textures/`) | {mib(e['files']['blend']['bytes'])} MiB |
| `lod/{s['base']}_lod0.glb` / `_lod1.glb` / `_lod2.glb` | Geometry-only exports of each LOD (no embedded textures), used to read back triangle counts | {mib(e['files']['lod0_glb']['bytes'])} / {mib(e['files']['lod1_glb']['bytes'])} / {mib(e['files']['lod2_glb']['bytes'])} MiB |
| `textures/` | Procedural PBR textures actually used ({len(e['textures'])} files, JPEG/PNG) | - |
| `renders/` | `{s['base']}_day.jpg`, `_night.jpg`, `_road_view.jpg`, `_detail.jpg` (1600x900 Blender/Cycles renders) | - |
| `validation.json` | Machine-readable results of every check listed below | - |

## Measured geometry (read back from the exported GLB)
| LOD | Triangles | Visibility range (Godot, via post-import script) |
|---|---:|---|
| LOD0 | {int(lt.get('0', 0)):,} | 0 - 60 m |
| LOD1 | {int(lt.get('1', 0)):,} | 60 - 170 m |
| LOD2 | {int(lt.get('2', 0)):,} | 170 - 900 m |

LOD0 bounding box (plot incl. forecourt/parking, metres): **{b0[0]:.1f} x {b0[1]:.1f} x {b0[2]:.1f}** (X x Y x Z in Blender; width x depth x height).
Materials: {b.get('material_count')} ({len(brand)} brand-specific: {', '.join(brand[:8])}{' ...' if len(brand) > 8 else ''}). Collision proxies: {b.get('collision_proxies')} convex boxes (`*-convcolonly`). Night lights: {g.get('lights')} glTF punctual lights (shadows off).

## Conventions (same as the three prototypes)
1 unit = 1 m - road-facing front is Blender -Y (glTF/Godot +Z) - origin at the plot centre at finished ground (z = 0) - transforms applied (geometry authored in final coordinates) -
hierarchy `root > <PREFIX>_LOD0/1/2 > merged part meshes`, plus `<PREFIX>_Collision` and `<PREFIX>_NightLights`.
To enable LOD switching in Godot assign `prototypes/roadside_lod_post_import.gd` (a verbatim copy is in `additional_17/`) as the import script. **Godot import has not been tested** from this cloud session.

## Day / night
Day: sun + sky, emissive sign faces stay readable. Night: emissive sign/glass/interior materials plus the `NightLights` collection (hidden in the day renders). Nothing is duplicated for night.

## Road-level sign readability (automatic check on the road-view camera)
{sg}

## Branding
{s['brand_note']}

## Validation performed
Reopened the saved `.blend` in a fresh Blender process; mesh integrity (NaN, loose vertices, material indices, UVs), flipped-normal test (signed volume of every watertight piece), LOD objects and decreasing budgets, bounds, collision, materials and texture files; exported GLB parsed (triangles per LOD, embedded images decoded) and re-imported into a clean scene (meshes, triangles, bounds, textures). Results: `validation.json`.
Rebuild: `python _tools/{s['script']}` then `render_store.py` / `validate_store.py` (see BUILD_REPORT.md).
'''
    open(f"{e['dir']}/README.md", 'w', encoding='utf-8').write(txt)


def report(data, man):
    L = []
    L.append('# BUILD REPORT - 17 additional roadside store assets\n')
    L.append(f"Generated {man['generated_utc']} from files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU renders, headless Linux cloud container).\n")
    cp = man['checkpoint']
    L.append(f"**Result: {cp['completed']}/{cp['total']} stores complete; {man['totals']['jpeg_renders']} of 68 required 1600x900 JPEG renders exist.** Last completed asset: {cp['last_completed_asset']}.")
    L.append(f"Remaining / incomplete: {', '.join(cp['remaining']) if cp['remaining'] else 'none'}.\n")
    L.append('## Batches (processed sequentially as requested)\n')
    L.append('| Batch | Assets | Complete |\n|---|---|---|')
    for bname, ids in BATCHES.items():
        L.append(f"| {bname} | {', '.join(ids)} | {', '.join(cp['batches'][bname]) or 'none'} |")
    L.append('\n## Per-store measured results (triangles read back from the exported GLB)\n')
    L.append('| # | Store | Placement | LOD0 tris | LOD1 tris | LOD2 tris | GLB MiB | .blend MiB | Materials | Bounding box (m) | Sign px (road view) | Validation | Status |')
    L.append('|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---|')
    for e in data:
        s = e['reg']
        b0 = e['val'].get('blend', {}).get('bounds', {}).get('0', {}).get('size', [0, 0, 0])
        best = max([x['pixel_height'] for x in e['signs'] if x.get('readable')] or [0])
        L.append(f"| {s['num']} | {s['display']} | {s['placement']} | {int(tri(e, 0) or 0):,} | {int(tri(e, 1) or 0):,} | {int(tri(e, 2) or 0):,} | {mib(e['files']['glb']['bytes'])} | {mib(e['files']['blend']['bytes'])} | "
                 f"{e['val'].get('blend', {}).get('material_count', '-')} | {b0[0]:.0f} x {b0[1]:.0f} x {b0[2]:.1f} | {best:.0f} | {'PASS' if e['val'].get('passed') else 'FAIL'} | {'complete' if e['complete'] else 'INCOMPLETE'} |")
    tot = lambda f: sum(e['files'][f]['bytes'] for e in data)
    L.append(f"\nTotals: GLB {mib(tot('glb'))} MiB, .blend {mib(tot('blend'))} MiB, per-LOD GLBs {mib(tot('lod0_glb') + tot('lod1_glb') + tot('lod2_glb'))} MiB.\n")
    L.append('## What was verified for every asset\n')
    L.append('- Saved `.blend`, reopened in a fresh background Blender process and inspected (integrity, UVs, materials, LOD objects, dimensions, collision, lights, extras).')
    L.append('- Flipped-normal test: every watertight mesh piece has positive signed volume (computed relative to the piece centroid in double precision after a float32 false-positive was found and fixed).')
    L.append('- GLB exported (master + three per-LOD geometry files); triangle counts parsed from the GLB JSON and matched to Blender; embedded textures decoded with Pillow; GLB re-imported into a clean scene and bounds/triangles/textures compared.')
    L.append('- Four 1600x900 JPEG renders per store (day, night, road view, detail) produced from the saved `.blend`.')
    L.append('- Road-view brand-sign check: the camera projects each registered sign (pixel height at 1600x900), ray-casts 10 points across the lettering for occlusion and checks the viewing angle. The check found and drove fixes to real problems (signs hidden by lamps/palms/porches, a lettering plane buried inside its sign box, an overhang covering a fascia).')
    L.append('- Visual inspection of every store (day/night/road/detail contact sheets) during production; fixes were applied before marking complete.\n')
    L.append('## Not verified / limitations (stated plainly)\n')
    L.append('- **Godot import was NOT tested.** The cloud session cannot reach the local project; conventions are copied from the three prototypes and the existing post-import script (see `roadside_lod_post_import.gd`, copied verbatim).')
    L.append('- Brand marks are **simplified procedural recreations**, not official logo artwork (see each README). Logos use Inter / Liberation / DejaVu fonts, extruded polygons and simple primitives. The KFC Colonel portrait and official script lettering (Tim Hortons, Krispy Kreme) are not reproduced.')
    L.append('- Interiors are shallow set dressing (shelves, counters, furniture silhouettes) intended to read through glass, not walkable interiors.')
    L.append('- Textures are procedural and tileable (1024 px JPEG q84 for generic materials); less rich than scanned PBR sets. Glass is alpha-blended (alpha 0.30), as in the prototypes.')
    L.append('- Lights in the GLB are tuned for the Cycles previews and will need re-tuning in Godot (shadows off).')
    L.append('- No exact real-world branch coordinates are used or implied; placement categories in the manifest are recommendations only.')
    L.append('- `lod/*.glb` are geometry-only (no embedded textures) to keep the repository small; the master `.glb` carries the textures.')
    L.append('- The `.blend` files sit next to the `.glb` (requested layout): if you copy whole store folders into a Godot project, either delete the `.blend` files or configure the Blender path, otherwise Godot will try to import them. `textures/` and `renders/` contain `.gdignore`; `PREVIEW_GALLERY/` deliberately has none.\n')
    L.append('## Render settings\n')
    L.append('Cycles (CPU, OpenImageDenoise), 1600x900, adaptive sampling, AgX view transform, 32-52 samples (denoised), Nishita sky + sun for day; blue-hour dusk world with moonlight and the `NightLights` collection for night. Cameras: 3/4 hero, driver height (1.25 m) road view, close facade/entrance/signage detail. Per-view render times are recorded in `STORE_ASSET_MANIFEST.json`.\n')
    L.append('## Reproducing\n')
    L.append('```bash\npython3.11 -m venv venv && venv/bin/pip install bpy==4.5.15 pillow numpy arabic-reshaper python-bidi\n'
             'cd assets/roadside_stores/additional_17/_tools\n../../../../venv/bin/python build_01_adnoc.py          # one script per store (build_NN_*.py), writes .blend/.glb/lod/textures\n'
             '../../../../venv/bin/python validate_store.py ../01_adnoc adnoc\n../../../../venv/bin/python render_store.py ../01_adnoc adnoc   # 4 JPEGs in renders/\n'
             '../../../../venv/bin/python make_reports.py                # gallery, catalog, manifest, READMEs, this report\n```\n')
    L.append('The kit (`store_kit.py`) imports the prototypes\' `roadside_lib.py` unchanged; the three original prototypes were not modified.\n')
    open(f'{A17}/BUILD_REPORT.md', 'w', encoding='utf-8').write('\n'.join(L))


def main():
    data = collect()
    n = gallery(data)
    contact_sheet(data)
    html_gallery(data)
    for e in data:
        store_readme(e)
    man = manifest(data)
    report(data, man)
    # verbatim copy of the existing Godot post-import script (not modified)
    src = os.path.normpath(f'{A17}/../prototypes/roadside_lod_post_import.gd')
    if os.path.exists(src):
        shutil.copyfile(src, f'{A17}/roadside_lod_post_import.gd')
    print(f"gallery images: {n}; complete: {man['totals']['complete']}/17; renders: {man['totals']['jpeg_renders']}/68")


if __name__ == '__main__':
    main()
