"""Generate per-asset README.md, PREMIUM_ASSET_MANIFEST.json, BUILD_REPORT.md (with checkpoint), contact sheet and the
offline HTML gallery from the files on disk (build_stats.json, validation.json, render_report.json, GLBs, renders).

Usage: python make_reports.py            (works with a partially finished collection: unfinished assets are listed as remaining)
"""
import os, sys, json, glob, datetime, subprocess, html
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
P17 = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from registry import ASSETS, BATCHES, VIEWS
from PIL import Image, ImageDraw, ImageFont

FB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FR = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'


def load(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default


def mb(p):
    return round(os.path.getsize(p) / 1e6, 2) if os.path.exists(p) else None


def collect(a):
    d = f'{P17}/{a["folder"]}'
    st = load(f'{d}/lod/build_stats.json', {})
    va = load(f'{d}/validation.json', {})
    rr = load(f'{d}/renders/render_report.json', {})
    renders = {v: os.path.exists(f'{d}/renders/{a["base"]}_{v}.jpg') for v in VIEWS}
    done = bool(va.get('passed')) and all(renders.values()) and os.path.exists(f'{d}/{a["base"]}.glb')
    return dict(dir=d, stats=st, val=va, rep=rr, renders=renders, done=done)


def vis_summary(rep, key):
    v = rep.get(f'{key}_visibility')
    if not v:
        return None
    cars = v.get('cars', [])
    probes = v.get('probes', [])
    return dict(cars_visible=sum(1 for c in cars if c['visible_fraction'] >= 0.33), cars_total=len(cars),
                car_fractions={c['car'].split('_CAR_')[-1]: c['visible_fraction'] for c in cars},
                probes_reached=sum(1 for p in probes if p['reached'] and p['in_frame']), probes_total=len(probes),
                probes={p['name']: bool(p['reached'] and p['in_frame']) for p in probes})


def concept_of(a):
    import ast
    for f in glob.glob(f'{HERE}/build_{a["num"]}_*.py'):
        doc = ast.get_docstring(ast.parse(open(f).read())) or ''
        return ' '.join(doc.split('\n')[1:]).strip()
    return ''


def asset_record(a, c):
    st, va, rep = c['stats'], c['val'], c['rep']
    chk = va.get('checks', {})
    meta = st.get('meta', {})
    g = chk.get('glb_full', {})
    groups = g.get('groups', {})
    lodx = chk.get('lod_extras', {})
    return dict(
        number=a['num'], name=a['display'], folder=a['folder'], category=a['category'], status='complete' if c['done'] else 'incomplete',
        concept=concept_of(a), storeys=meta.get('storeys'), floor_levels_m=meta.get('floor_levels'), roof=meta.get('roof'),
        frontage_width_m=meta.get('width'), depth_m=meta.get('depth'), height_m=meta.get('height'),
        lod0_bounds_m=chk.get('lod0_bounds_m'), setback_m=meta.get('setback_m'), parking=meta.get('parking'), access=meta.get('access'),
        glass=meta.get('glass'),
        files=dict(blend=f'{a["folder"]}/{a["base"]}.blend', glb=f'{a["folder"]}/{a["base"]}.glb',
                   glb_building_only=f'{a["folder"]}/{a["base"]}_building_only.glb' if os.path.exists(f'{c["dir"]}/{a["base"]}_building_only.glb') else None,
                   lod=[f'{a["folder"]}/lod/{os.path.basename(p)}' for p in sorted(glob.glob(f'{c["dir"]}/lod/*.glb'))],
                   renders=[f'{a["folder"]}/renders/{a["base"]}_{v}.jpg' for v in VIEWS]),
        file_sizes_mb=dict(blend=mb(f'{c["dir"]}/{a["base"]}.blend'), glb=mb(f'{c["dir"]}/{a["base"]}.glb'),
                           glb_building_only=mb(f'{c["dir"]}/{a["base"]}_building_only.glb')),
        triangles_from_glb=dict(LOD0=groups.get('LOD0'), LOD1=groups.get('LOD1'), LOD2=groups.get('LOD2'), placeholder_cars=groups.get('PLACEHOLDER_CARS', 0),
                                site=sum(groups.get(k, 0) for k in ('SIDEWALK_FRONTAGE', 'OPTIONAL_FORECOURT', 'DRIVEWAY', 'OPTIONAL_PARKING')),
                                collision=groups.get('Collision'), total=g.get('total'), lod_files=chk.get('glb_lod_files_tris')),
        lod_ranges_m={k: [v.get('begin'), v.get('end')] for k, v in lodx.items()},
        materials=dict(count_glb=g.get('materials'), alpha_blend=g.get('alpha_blend'), used=chk.get('materials_used')),
        textures=dict(embedded_images=len(g.get('images', [])), sizes=sorted({f'{i["size"][0]}x{i["size"][1]}' for i in g.get('images', []) if i.get('ok')}),
                      files=chk.get('image_textures')),
        lights=chk.get('lights'), collision_boxes=chk.get('collision_boxes'),
        placeholder_cars=st.get('cars', []),
        validation=dict(passed=va.get('passed'), issues=va.get('issues'), warnings=va.get('warnings'),
                        degenerate_faces=chk.get('degenerate_faces'), inverted_closed_faces=chk.get('closed_pieces_with_inverted_normals_faces'),
                        glass=chk.get('glass_materials'), reimport=chk.get('reimport'), vegetation=chk.get('vegetation_objects_or_materials')),
        visibility=dict(road_view=vis_summary(rep, 'road_view'), day=vis_summary(rep, 'day')),
        render_seconds={v: rep.get(f'{v}_seconds') for v in VIEWS},
        brand_note=a['brand_note'])


def readme(a, r):
    t = r['triangles_from_glb']
    L = [f'# {a["num"]} - {a["display"]}', '', f'*{a["category"]}* - status: **{r["status"]}**', '', (r['concept'] or ''), '']
    L += ['## Previews', '']
    for v in VIEWS:
        L.append(f'![{v}](renders/{a["base"]}_{v}.jpg)')
    L += ['', '## Key facts', '', '| Item | Value |', '|---|---|',
          f'| Storeys | {r["storeys"]} (floor levels {r["floor_levels_m"]} m, roof {r["roof"]}) |',
          f'| Frontage x depth x height | {r["frontage_width_m"]} x {r["depth_m"]} x {r["height_m"]} m |',
          f'| LOD0 bounds (Blender) | {r["lod0_bounds_m"]["size"] if r["lod0_bounds_m"] else "-"} m |',
          f'| Setback from plot frontage | {r["setback_m"]} m |',
          f'| Parking | {r["parking"]} |', f'| Vehicle access | {r["access"]} |', f'| Glass | {r["glass"]} |',
          f'| Lights | {r["lights"]} |', f'| Collision boxes | {r["collision_boxes"]} |', '']
    L += ['## Files', '', f'- `{a["base"]}.blend` - full editable Blender 4.5.15 LTS scene (textures referenced relatively from `textures/`).',
          f'- `{a["base"]}.glb` - presentation export: LOD0/1/2 + site pieces + placeholder cars + lights + collision, textures embedded.']
    if r['files']['glb_building_only']:
        L.append(f'- `{a["base"]}_building_only.glb` - identical but WITHOUT the `PLACEHOLDER_CARS` node.')
    else:
        L.append('- (no placeholder cars in this asset, so the main GLB is already building-only)')
    L += ['- `lod/` - geometry-only per-LOD GLBs used for independent triangle read-back (+ placeholder cars GLB where present), `build_stats.json`.',
          '- `textures/` - procedural PBR maps (JPEG albedo/ORM/normal) + PNG brand/screen graphics.', '- `renders/` - four 1600x900 Cycles JPEGs + `render_report.json` (ray-traced visibility checks).',
          '- `validation.json` - fresh-process validation results.', '']
    L += ['## Triangles (read from the exported GLB)', '', '| LOD0 | LOD1 | LOD2 | Placeholder cars | Site pieces | Collision |', '|---|---|---|---|---|---|',
          f'| {t["LOD0"]} | {t["LOD1"]} | {t["LOD2"]} | {t["placeholder_cars"]} | {t["site"]} | {t["collision"]} |', '',
          f'LOD visibility ranges (glTF extras, applied by `../premium_lod_post_import.gd`): {r["lod_ranges_m"]}; placeholder cars 0-340 m.', '']
    L += ['## Hierarchy', '', '```', f'P{a["num"]}_<Title> (root, origin = centre of the plot frontage line, ground; front = -Y Blender / +Z glTF)',
          '  LOD0/1/2 -> BUILDING_EXTERIOR, BUILDING_INTERIOR, GLASS_SYSTEM, FACADE_DETAILS, SIGNAGE, FURNITURE, DISPLAY_OBJECTS',
          '  SIDEWALK_FRONTAGE, OPTIONAL_FORECOURT, DRIVEWAY, OPTIONAL_PARKING   (separate, removable site pieces)',
          '  PLACEHOLDER_CARS (one object per car)   INTERIOR_LIGHTING   EXTERIOR_LIGHTING   COLLISION (*-convcolonly)', '```', '']
    if r['placeholder_cars']:
        L += ['## Placeholder cars', '', 'Generic, badge-free silhouettes for replacement by the game\'s own vehicles. Each car is ONE object '
              '(pivot at ground centre, nose = local +X). Remove them all by deleting the `PLACEHOLDER_CARS` collection in Blender, by using '
              f'`{a["base"]}_building_only.glb`, or in Godot via the `premium_placeholder_cars` group.', '',
              '| Object | Class | L x W x H (m) | Position (m) | Heading | Role | Tris |', '|---|---|---|---|---|---|---|']
        for c in r['placeholder_cars']:
            L.append(f'| `{c["name"]}` | {c["kind"]} | {c["length"]} x {c["width"]} x {c["height"]} | {c["location"]} | {c["heading_deg"]} | {c["role"]} | {c["tris"]} |')
        L.append('')
    v = r['validation']
    L += ['## Validation', '', f'- Result: **{"PASS" if v["passed"] else "FAIL"}**; issues: {v["issues"]}; warnings: {v["warnings"]}',
          f'- Degenerate faces: {v["degenerate_faces"]}; inverted faces in watertight pieces: {v["inverted_closed_faces"]}; vegetation: {v["vegetation"] or "none"}',
          f'- Glass materials: {v["glass"]}', f'- GLB re-import into a clean scene: {v["reimport"]}']
    for k, s in r['visibility'].items():
        if s:
            L.append(f'- Ray-traced visibility from the {k} camera: cars readable {s["cars_visible"]}/{s["cars_total"]} {s["car_fractions"]}; '
                     f'interior probes reached {s["probes_reached"]}/{s["probes_total"]} {s["probes"]}')
    L += ['', f'Brand note: {a["brand_note"]}', '', 'Godot import has NOT been tested from the cloud session. If you copy this folder into a Godot '
          'project, delete or exclude the `.blend` (Godot would try to import it) - `textures/` and `renders/` contain `.gdignore`.', '']
    return '\n'.join(L)


def contact_sheet(done):
    tw, th, lw, pad = 420, 236, 300, 6
    rows = [a for a in ASSETS]
    W = lw + 4 * (tw + pad) + pad
    H = 90 + len(rows) * (th + pad) + pad
    sheet = Image.new('RGB', (W, H), (18, 20, 24))
    d = ImageDraw.Draw(sheet)
    fb, fr, fs = ImageFont.truetype(FB, 30), ImageFont.truetype(FR, 17), ImageFont.truetype(FB, 20)
    d.text((pad + 4, 22), 'PREMIUM COMMERCIAL 17 - Dubai open world - actual Blender 4.5.15 Cycles renders (day / night / road view / interior)', font=fb, fill=(240, 240, 240))
    for k, v in enumerate(['DAY', 'NIGHT', 'ROAD VIEW', 'INTERIOR']):
        d.text((lw + pad + k * (tw + pad) + 6, 64), v, font=fr, fill=(170, 175, 185))
    for i, a in enumerate(rows):
        y = 90 + i * (th + pad)
        d.text((pad + 4, y + 10), f'{a["num"]}', font=fb, fill=(255, 200, 120))
        words, line, yy = a['display'].split(), '', y + 52
        for wd in words:
            if d.textlength(line + ' ' + wd, font=fs) > lw - 20:
                d.text((pad + 4, yy), line.strip(), font=fs, fill=(235, 235, 235)); yy += 26; line = ''
            line += ' ' + wd
        d.text((pad + 4, yy), line.strip(), font=fs, fill=(235, 235, 235))
        d.text((pad + 4, y + th - 30), a['category'].split(' - ')[1], font=fr, fill=(150, 155, 165))
        for k, v in enumerate(VIEWS):
            p = f'{P17}/{a["folder"]}/renders/{a["base"]}_{v}.jpg'
            x = lw + pad + k * (tw + pad)
            if os.path.exists(p):
                sheet.paste(Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS), (x, y))
            else:
                d.rectangle([x, y, x + tw, y + th], outline=(80, 80, 80)); d.text((x + 12, y + th // 2), 'pending', font=fr, fill=(120, 120, 120))
    sheet.save(f'{P17}/PREMIUM_COMMERCIAL_17_CONTACT_SHEET.jpg', quality=88)


def gallery(records):
    cards = []
    for a, r in zip(ASSETS, records):
        t = r['triangles_from_glb']
        imgs = ''.join(f'<figure><a href="{a["folder"]}/renders/{a["base"]}_{v}.jpg" target="_blank"><img loading="lazy" src="{a["folder"]}/renders/{a["base"]}_{v}.jpg" '
                       f'alt="{html.escape(a["display"])} {v}"></a><figcaption>{v.replace("_", " ")}</figcaption></figure>' for v in VIEWS)
        cars = len(r['placeholder_cars'])
        cards.append(f'''<section class="card" id="a{a["num"]}"><header><span class="num">{a["num"]}</span><div><h2>{html.escape(a["display"])}</h2>
<p class="cat">{html.escape(a["category"])} &middot; {r["storeys"]} storey(s) &middot; {r["frontage_width_m"]} &times; {r["depth_m"]} m, {r["height_m"]} m high
&middot; LOD0/1/2 {t["LOD0"]:,} / {t["LOD1"]:,} / {t["LOD2"]:,} tris{f" &middot; {cars} placeholder cars" if cars else ""}
&middot; {"validated" if r["validation"]["passed"] else "NOT validated"}</p></div></header>
<p class="concept">{html.escape(r["concept"] or "")}</p><div class="grid">{imgs}</div>
<p class="meta">Parking: {html.escape(str(r["parking"]))} &middot; Access: {html.escape(str(r["access"]))}</p></section>''' if r['status'] == 'complete' and t['LOD0'] else
                     f'<section class="card"><header><span class="num">{a["num"]}</span><div><h2>{html.escape(a["display"])}</h2><p class="cat">pending</p></div></header></section>')
    nav = ''.join(f'<a href="#a{a["num"]}">{a["num"]} {html.escape(a["display"])}</a>' for a in ASSETS)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Premium Commercial 17 Gallery</title><style>
:root{{--bg:#f4f3f0;--fg:#1c1d20;--muted:#5d6068;--card:#ffffff;--line:#dcdad5;--acc:#9a6b2f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#121316;--fg:#ececec;--muted:#a0a3aa;--card:#1c1e22;--line:#2c2f35;--acc:#e0b070}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:1500px;margin:0 auto;padding:24px 16px 60px}}h1{{margin:0 0 4px;font-size:28px}}.sub{{color:var(--muted);margin:0 0 16px}}
nav{{display:flex;flex-wrap:wrap;gap:6px 14px;margin:0 0 22px;font-size:13px}}nav a{{color:var(--acc);text-decoration:none}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 22px}}
header{{display:flex;gap:14px;align-items:flex-start}}.num{{font-weight:700;font-size:26px;color:var(--acc);min-width:44px}}
h2{{margin:0;font-size:20px}}.cat,.meta{{color:var(--muted);margin:2px 0 0;font-size:13px}}.concept{{margin:10px 0}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:520px){{.grid{{grid-template-columns:1fr}}}}figure{{margin:0}}img{{width:100%;height:auto;display:block;border-radius:6px;background:#888}}
figcaption{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:3px}}</style></head><body><div class="wrap">
<h1>Premium Commercial 17</h1><p class="sub">Dubai open-world premium commercial buildings &middot; actual Blender 4.5.15 LTS Cycles renders (1600&times;900) &middot;
works offline - keep this file next to the asset folders. Click any image for full size.</p><nav>{nav}</nav>{"".join(cards)}</div></body></html>'''
    open(f'{P17}/PREMIUM_COMMERCIAL_17_GALLERY.html', 'w').write(page)


def git_info():
    try:
        br = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=P17, text=True).strip()
        log = subprocess.check_output(['git', 'log', '--oneline', '-8'], cwd=P17, text=True).strip()
        return br, log
    except Exception:
        return '?', ''


def build_report(records, cs):
    done = [r for r in records if r['status'] == 'complete']
    br, log = git_info()
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    L = ['# Premium Commercial 17 - build report', '', f'Generated {now} from the files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU + OpenImageDenoise, headless Linux cloud container).', '',
         '## Checkpoint', '']
    for b, nums in BATCHES.items():
        st = ['complete' if records[int(n) - 1]['status'] == 'complete' else 'remaining' for n in nums]
        L.append(f'- Batch {b}: ' + ', '.join(f'{n} {ASSETS[int(n) - 1]["display"]} ({s})' for n, s in zip(nums, st)))
    rem = [r['name'] for r in records if r['status'] != 'complete']
    L += ['', f'**{len(done)} / 17 assets complete.** ' + ('Remaining: ' + ', '.join(rem) if rem else 'Nothing remaining.'),
          f'Last successful asset: {done[-1]["name"] if done else "-"}', '']
    L += ['## Summary table (triangles read from the exported GLBs)', '',
          '| # | Asset | Storeys | W x D x H (m) | LOD0 | LOD1 | LOD2 | Cars (tris) | GLB MB | Materials | Images | Lights int/ext | Validation |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for a, r in zip(ASSETS, records):
        t = r['triangles_from_glb']
        if not t['LOD0'] or r['status'] != 'complete':
            L.append(f'| {a["num"]} | {a["display"]} | - | - | - | - | - | - | - | - | - | - | pending |'); continue
        li = r['lights'] or {}
        L.append(f'| {a["num"]} | {a["display"]} | {r["storeys"]} | {r["frontage_width_m"]} x {r["depth_m"]} x {r["height_m"]} | {t["LOD0"]:,} | {t["LOD1"]:,} | {t["LOD2"]:,} | '
                 f'{len(r["placeholder_cars"])} ({t["placeholder_cars"]:,}) | {r["file_sizes_mb"]["glb"]} | {r["materials"]["count_glb"]} | {r["textures"]["embedded_images"]} | '
                 f'{li.get("INTERIOR_LIGHTING")}/{li.get("EXTERIOR_LIGHTING")} | {"PASS" if r["validation"]["passed"] else "FAIL"} |')
    tot = lambda k: sum((r['triangles_from_glb'][k] or 0) for r in done)
    L += ['', f'Totals over complete assets: LOD0 {tot("LOD0"):,} tris, LOD1 {tot("LOD1"):,}, LOD2 {tot("LOD2"):,}, placeholder cars {tot("placeholder_cars"):,}; '
          f'{sum(len(r["placeholder_cars"]) for r in done)} placeholder cars; {sum(1 for r in done for f in r["files"]["renders"] if os.path.exists(os.path.join(P17, f)))} renders '
          '+ contact sheet + offline gallery.', '']
    L += ['## Architectural diversity (why these are not one generator with different colours)', '', '| # | Massing / roof | Glass | Site arrangement |', '|---|---|---|---|']
    for a, r in zip(ASSETS, records):
        L.append(f'| {a["num"]} | {r["roof"]} | {r["glass"]} | {r["parking"]}; {r["access"]} |')
    L += ['', 'Every asset has its own build script (`_tools/build_NN_*.py`) that designs its own massing, plan, roof, entrance, interior layout and '
          'site arrangement; only low-level helpers (curtain walls, slabs, stairs, furniture, cars, materials) are shared from `_tools/pk_*.py`.', '']
    L += ['## Method and conventions', '',
          '- Units metres, Z up, front facing Blender -Y (glTF / Godot +Z), origin at the centre of the plot frontage line (back of the 4 m public pavement) at ground level.',
          '- The earlier libraries `prototypes/_tools/roadside_lib.py` and `additional_17/_tools/store_kit.py` are imported READ-ONLY (byte-code writing disabled, '
          'texture cache redirected to `premium_commercial_17/_tools/texcache/`); nothing in `prototypes/` or `additional_17/` was modified.',
          '- Real transparent glass: single double-sided panes with an alpha-blended PBR material (`PC_Glass` alpha 0.16, `PC_GlassClear` 0.11, `PC_GlassRail` 0.14) - '
          'no opaque "fake interior" textures. Interiors are real geometry: slabs, ceilings, stairs, escalators, railings, counters, furniture, products, display cars.',
          '- Lighting: important fixtures are real KHR punctual lights (interior points/spots, exterior washes); small fixtures are emissive materials. '
          'Interior lights are on in all renders (showroom/store lighting); exterior lights only at night.',
          '- LODs: LOD0 full detail; LOD1 keeps the full shell, glass, slabs, stairs and simplified furniture silhouettes (no small products); '
          'LOD2 is the massing with coarse glazing, slabs and emissive interior-glow proxies. Placeholder cars are a separate node with their own 0-340 m range.',
          '- Collision: simple `*-convcolonly` boxes per main volume (same convention as the earlier stores).',
          '- Textures: shared procedural 1024 px PBR sets (limestone, granite, marble, terrazzo, oak, corrugated metal, pavers, + earlier concrete/travertine/asphalt/wood), '
          'one 1024x512 screen-content atlas shared by all displays, PNG logo decals with alpha. JPEG maps keep the GLBs small.', '']
    L += ['## Validation performed (per asset, see each `validation.json`)', '',
          '1. Saved `.blend`, reopened in a fresh Python/Blender process. 2. `Mesh.validate()` on every mesh, degenerate faces counted. 3. Winding of every watertight piece checked. '
          '4. Dimensions / bounds recorded. 5. Material slots checked (no empty slots). 6. Glass materials checked for alpha < 1 + blend mode. 7. UV layer present and finite. '
          '8. Interior geometry triangle count per LOD. 9. Placeholder cars: separate objects, parented only to `<P>_PLACEHOLDER_CARS`, not shared, not inside LOD collections; '
          'building-only GLB verified to contain no car nodes. 10. LOD counts strictly decreasing and LOD extras present. 11-13. GLB exported, parsed (per-group triangles, '
          'embedded images decoded with Pillow) and re-imported into a clean scene (triangle totals compared). 14-16. Four renders + ray-traced visibility: from the road-view '
          'and day cameras, rays to sample points on every placeholder car and to interior probe points may pass glass but not opaque geometry.', '',
          '- Crescent Galleria: probes on the front gallery of each of the 4 levels and on the escalators are traced from the day and road cameras (see its README).', '']
    for a, r in zip(ASSETS, records):
        if r['status'] != 'complete':
            continue
        rv, dv = r['visibility']['road_view'], r['visibility']['day']
        L.append(f'- {a["num"]} {a["display"]}: {"PASS" if r["validation"]["passed"] else "FAIL"}'
                 + (f'; road view: cars readable {rv["cars_visible"]}/{rv["cars_total"]}, probes {rv["probes_reached"]}/{rv["probes_total"]}' if rv else '')
                 + (f'; day view: cars {dv["cars_visible"]}/{dv["cars_total"]}, probes {dv["probes_reached"]}/{dv["probes_total"]}' if dv else '')
                 + (f'; warnings {r["validation"]["warnings"]}' if r['validation']['warnings'] else ''))
    L += ['', '## LOD transition recommendations', '',
          '- Default: LOD0 0-90 m, LOD1 90-260 m, LOD2 260-1600 m, 8 m hysteresis margin (glTF node extras, applied by `premium_lod_post_import.gd`). '
          'Crescent Galleria (large): 0-140 / 140-380 / 380-2000 m.',
          '- Glass stays transparent in every LOD and LOD1 keeps slabs, stairs/escalators and furniture silhouettes, so the interior does not disappear at normal '
          'roadside distances; LOD2 swaps detailed interiors for emissive glow proxies behind the glass.',
          '- Placeholder cars: 0-340 m (they are expected to be replaced by the game\'s own vehicles with their own LODs).',
          '- For Unreal Engine 5, import the LOD0 node (or use Nanite on LOD0) and use LOD1/LOD2 as HLOD inputs; glass materials should be set to Translucent / '
          'Surface Forward Shading.', '']
    L += ['## Known limitations', '',
          '- Godot import has NOT been tested: the cloud session cannot reach the local `Dubai-Game-Godot-PC-Test` project. Neither Godot project was touched.',
          '- Brand marks (Mercedes-Benz, BMW, Porsche, Ford, Samsung, Apple, Xiaomi) are simplified generic recreations made from primitives / procedural images, '
          'not official artwork - replace with licensed assets before release. Restaurant, cafe, garage and mall brands are fictional.',
          '- Placeholder cars are deliberately simple lofted silhouettes (body, glasshouse, wheels, lights) - not production vehicles.',
          '- Glass is alpha-blended (engine friendly) rather than physically refractive; in the renders it reads slightly lighter than real low-iron glass.',
          '- Rear service areas / kitchens / back-of-house spaces that cannot be seen from the street are blocked by partitions and not modelled in detail (intentional).',
          '- Render environment (street, sand ground, sky) is a preview set in `_PREVIEW_NOT_EXPORTED` and is not part of the exported assets.',
          '- No vegetation is modelled anywhere (planters are empty structures) as requested.',
          '- Copying an asset folder into Godot: exclude the `.blend` file (Godot would try to import it); `textures/` and `renders/` contain `.gdignore`.', '']
    L += ['## Git', '', f'- Branch: `{br}` (based on `claude/dubai-17-store-assets`).', '- Recent commits:', '```', log, '```', '']
    open(f'{P17}/BUILD_REPORT.md', 'w').write('\n'.join(L))


def main():
    recs = []
    for a in ASSETS:
        c = collect(a)
        r = asset_record(a, c)
        recs.append(r)
        if c['stats']:
            open(f'{c["dir"]}/README.md', 'w').write(readme(a, r))
    man = dict(collection='Premium Commercial 17', generated=datetime.datetime.utcnow().isoformat() + 'Z', blender='4.5.15 LTS', units='metres',
               axes=dict(blender_front='-Y', gltf_front='+Z', up='Z (Blender) / +Y (glTF)'),
               origin='centre of the plot frontage line (back of pavement), ground level', lod_post_import_script='premium_lod_post_import.gd',
               complete=sum(1 for r in recs if r['status'] == 'complete'), assets=recs)
    json.dump(man, open(f'{P17}/PREMIUM_ASSET_MANIFEST.json', 'w'), indent=1)
    contact_sheet([r['status'] == 'complete' for r in recs])
    gallery(recs)
    build_report(recs, None)
    print('REPORTS', sum(1 for r in recs if r['status'] == 'complete'), 'complete')


if __name__ == '__main__':
    main()
