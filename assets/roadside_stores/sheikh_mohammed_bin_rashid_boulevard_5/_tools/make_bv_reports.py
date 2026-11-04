"""Boulevard 5 reports: per-asset README.md, BOULEVARD_ASSET_MANIFEST.json, BOULEVARD_BUILD_REPORT.md,
BOULEVARD_FIVE_CONTACT_SHEET.jpg, BOULEVARD_FIVE_GALLERY.html.  Plain CPython + Pillow; reads the files on disk."""
import os, sys, json, html, datetime, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BV = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(BV, '..', '..', '..'))
sys.path.insert(0, os.path.join(BV, '..', 'premium_commercial_17', 'FLAGSHIP_BRANDING_CORRECTION', '_tools'))
import glb_stats
F_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
F_R = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'

ASSETS = [
    dict(num='01', folder='01_maison_levant', base='maison_levant', name='Maison Levant', type='Premium Levantine fine-dining restaurant',
         identity='Symmetrical limestone frontage: five tall bays between 0.9 m stone piers; four two-storey bronze-framed glass bays '
                  'and a 7 m recessed central entrance under a deep bronze blade canopy; attic band with bronze letters.',
         interior='Double-height dining hall with chandelier rings, reception counter, velvet banquettes and round tables; '
                  'first-floor private dining gallery with a glass balustrade over the void; stone-and-bronze stair; mashrabiya feature wall.',
         terrace='Raised timber dining terrace with parasols (optional collection).'),
    dict(num='02', folder='02_juniper_house', base='juniper_house', name='Juniper House', type='Luxury international restaurant',
         identity='Long, low horizontal frontage: slender travertine mullion-piers on a 3 m grid with 6.2 m continuous glass; '
                  'three recessed entrance bays (6 m central); a 4.6 m deep bronze canopy running the full 30 m; '
                  'stepped crown with a vertical bronze fin screen.',
         interior='Double-height hall with a walnut rib ceiling and light lines, central island bar with lit back bar, '
                  'banquettes and table rows; rear mezzanine dining with glass balustrade and open stair.',
         terrace='Four timber terrace decks under the canopy (optional collection).'),
    dict(num='03', folder='03_lune_and_laurel', base='lune_and_laurel', name='Lune & Laurel Cafe', type='Premium cafe and patisserie (corner unit)',
         identity='Champagne-stone block whose street corner becomes a curved two-storey glass corner (4.2 m radius); '
                  'arched-head recessed entrance under a cantilevered first-floor balcony; tall two-storey finned window; '
                  'stepped parapet; gold script signage + corner blade sign.',
         interior='Marble-and-bronze coffee counter with espresso machines and lit pastry vitrines, cafe tables along the curved '
                  'glass, bronze spiral stair to a first-floor lounge with sofas, armchairs and globe pendants.',
         terrace='Small bistro deck with a parasol (optional collection); side-street paving.'),
    dict(num='04', folder='04_galerie_dor', base='galerie_dor', name="Galerie D'Or", type='High-end fashion and lifestyle retail gallery',
         identity='Beige-stone podium with four different boutique shopfronts (projecting vitrine / horizontal bronze bands / '
                  'vertical bronze fins / framed pane on granite riser), central recessed entrance below a bronze bay window, '
                  'punched upper windows with bronze surrounds, fluted attic.',
         interior='Four boutiques with mannequins, clothes rails, display cases, wall shelving and seating behind glass hall '
                  'partitions; central atrium with a wide stone stair to an open upper gallery with chandelier rings.',
         terrace='None - benches, bollards, empty planters only.'),
    dict(num='05', folder='05_the_promenade_galleria', base='the_promenade_galleria', name='The Promenade Galleria',
         type='Premium shopping and dining gallery (largest)',
         identity='Two limestone towers with bronze slot windows and crowns; 4 m deep stone-column arcade with shopfronts; '
                  'bronze curtain walls with fins on two upper floors; a 12 m wide, 15 m high set-back glazed atrium portal '
                  'with a bronze-and-glass canopy.',
         interior='Three commercial levels around a central atrium: criss-cross escalators, glass-balustraded balcony walkways, '
                  'twelve glazed shop units with fixtures and lit name bands, atrium seating, chandelier rings, glazed skylight.',
         terrace='None - arcade paving, benches, bollards, empty planters.'),
]
VIEWS = [('day', 'Daytime exterior'), ('night', 'Nighttime exterior'), ('road_view', 'Street / driver height'), ('interior', 'Interior')]


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO).stdout.strip()


def mb(p):
    return round(os.path.getsize(p) / 1e6, 2) if os.path.exists(p) else None


def collect():
    rows = []
    for a in ASSETS:
        d = os.path.join(BV, a['folder'])
        v = json.load(open(os.path.join(d, 'validation.json')))
        bs = json.load(open(os.path.join(d, 'lod', 'build_stats.json')))
        rr = json.load(open(os.path.join(d, 'renders', 'render_report.json'))) if os.path.exists(os.path.join(d, 'renders', 'render_report.json')) else {}
        g = glb_stats.stats(os.path.join(d, a['base'] + '.glb'))
        lod = {f'LOD{L}': glb_stats.stats(os.path.join(d, 'lod', f'{a["base"]}_lod{L}.glb'))['total'] for L in (0, 1, 2)}
        m = bs['meta']
        c = v['checks']
        row = dict(a, width_m=m['width'], depth_m=m['depth'], height_m=round(m['height'], 2), storeys=m['storeys'],
                   storey_note=m.get('storey_note'), floor_levels_m=m['floor_levels'], roof_m=m['roof'], frontage_m=m.get('frontage_m'),
                   lod_tris_glb=lod, glb_total_tris=g['total'], glb_groups=c['glb_full']['groups'], images=len(g['images']) if isinstance(g['images'], list) else g['images'],
                   materials=len(c['materials_used']), materials_used=c['materials_used'], lights=c['lights'], collision_boxes=c['collision_boxes'],
                   interior_tris_lod0=c['interior_tris_lod0'], interior_tris_lod1=c['interior_tris_lod1'],
                   tower_interface=m.get('tower_interface'), terrace_note=m.get('terrace'),
                   files=dict(blend_mb=mb(os.path.join(d, a['base'] + '.blend')), glb_mb=mb(os.path.join(d, a['base'] + '.glb')),
                              lod_glb_mb={f'LOD{L}': mb(os.path.join(d, 'lod', f'{a["base"]}_lod{L}.glb')) for L in (0, 1, 2)},
                              fbx_mb={f'LOD{L}': mb(os.path.join(d, 'unreal', f'{a["base"]}_LOD{L}.fbx')) for L in (0, 1, 2)}),
                   validation=dict(passed=v['passed'], issues=v['issues'], warnings=v['warnings'], reimport=c['reimport'],
                                   glass=c['glass_materials'], degenerate_faces=c['degenerate_faces'],
                                   inverted_faces=c['closed_pieces_with_inverted_normals_faces'], vegetation=c['vegetation_objects_or_materials']),
                   renders=[f'renders/{a["base"]}_{k}.jpg' for k, _ in VIEWS if os.path.exists(os.path.join(d, 'renders', f'{a["base"]}_{k}.jpg'))],
                   visibility={k: rr.get(k) for k in ('day_visibility', 'road_view_visibility')},
                   render_seconds={k: rr.get(f'{k}_seconds') for k, _ in VIEWS})
        rows.append(row)
    return rows


def readme(r):
    d = os.path.join(BV, r['folder'])
    t = r['lod_tris_glb']
    s = f"""# {r['name']} - {r['type']}

Boulevard podium asset {r['num']} of 5 for a **Sheikh Mohammed bin Rashid Boulevard (Downtown Dubai)**-inspired street.
This is a fictional business for an internal test game: it is not a real shop, and no real tenant position or geographic
placement is implied. There is no vegetation (planters are empty).

## Architecture
{r['identity']}

## Interior
{r['interior']}

## Dimensions (metres, Z-up, front = -Y in Blender = +Z in glTF)
| Item | Value |
|---|---|
| Frontage x depth | {r['width_m']} x {r['depth_m']} |
| Height (top of podium / crown) | {r['height_m']} |
| Commercial storeys | {r['storeys']}{(' (' + r['storey_note'] + ')') if r.get('storey_note') else ''} |
| Floor levels | {', '.join(str(z) for z in r['floor_levels_m'])} (roof slab {r['roof_m']}) |
| Tower interface | rear plane y = {r['tower_interface']['rear_plane_y']}, podium roof z = {r['tower_interface']['podium_roof_z']}, interface top z = {r['tower_interface']['top_z']} (empty `B{r['num']}_TOWER_INTERFACE`) |
| Origin | centre of the frontage line (building line), ground level; promenade strip at y < 0 |

## Files
| File | Size |
|---|---|
| `{r['base']}.blend` | {r['files']['blend_mb']} MB (editable source; build script `../_tools/build_{r['num']}_*.py`) |
| `{r['base']}.glb` | {r['files']['glb_mb']} MB (Godot: all LODs, promenade + terrace pieces, lights, collision, embedded textures) |
| `lod/{r['base']}_lod0/1/2.glb` | {r['files']['lod_glb_mb']['LOD0']} / {r['files']['lod_glb_mb']['LOD1']} / {r['files']['lod_glb_mb']['LOD2']} MB (geometry only) |
| `unreal/{r['base']}_LOD0/1/2.fbx` | {r['files']['fbx_mb']['LOD0']} / {r['files']['fbx_mb']['LOD1']} / {r['files']['fbx_mb']['LOD2']} MB (Unreal; LOD0 includes `UCX_` collision; textures referenced relatively from `../textures`) |
| `textures/` | PBR maps (albedo / ORM / normal, 1024 px JPEG) |
| `renders/` | four Cycles renders, 1600x900 |
| `validation.json`, `lod/build_stats.json` | validation results / build statistics |

## Triangle counts (read from the exported GLB files)
| LOD | Triangles | Contents |
|---|---|---|
| LOD0 | {t['LOD0']:,} | full facade detail, interiors, furniture, signage ({r['interior_tris_lod0']:,} interior tris) |
| LOD1 | {t['LOD1']:,} | full shell + glass, slabs, stairs/escalators, simplified furniture ({r['interior_tris_lod1']:,} interior tris) |
| LOD2 | {t['LOD2']:,} | massing, coarse glazing, glow proxies, simplified signage |
| Full GLB total | {r['glb_total_tris']:,} | incl. promenade, terrace pieces and collision boxes |

## Materials
{r['materials']} materials. Stone: BV_Limestone / BV_Travertine / BV_Champagne / BV_BeigeStone (procedural large-format panels with
joints, roughness and normal maps); metal: BV_Bronze / BV_BronzeDark / BV_BlackFrame (metallic 1.0, roughness 0.3-0.35);
glass: BV_Glass / BV_GlassWarm (real alpha blend 0.11-0.12, double-sided, low tint, so the interiors stay visible). Lights:
{r['lights']['INTERIOR_LIGHTING']} interior + {r['lights']['EXTERIOR_LIGHTING']} exterior (KHR punctual).

## LOD recommendations
LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m (glTF node extras `visibility_range_*`, applied by
`../../premium_commercial_17/premium_lod_post_import.gd`). The glass facade and main entrance remain in every LOD. For Unreal
Engine 5, import LOD0 (Nanite-friendly) and use LOD1/LOD2 as HLOD inputs, with glass set to Translucent.

## Modular collections
`PROMENADE_FRONTAGE` (stone paving strip, removable), `OPTIONAL_TERRACE` ({r['terrace']}), `SIGNAGE`,
`COLLISION` (`*-convcolonly` boxes, {r['collision_boxes']} pieces). There is no parking or vegetation.

## Validation (Blender only)
Result: **{'PASS' if r['validation']['passed'] else 'FAIL'}**. The `.blend` was reopened in a fresh process, and the checks were:
mesh.validate, degenerate faces, winding, UVs, material slots, glass alpha < 1, LOD order and extras, missing textures, and vegetation. The GLB
was then exported, parsed with every embedded image decoded, and re-imported into a clean scene
({r['validation']['reimport']['triangles']:,} triangles, matching {r['validation']['reimport']['glb_triangles']:,}). Interior visibility was ray-traced from
the day and road cameras (see `renders/render_report.json`). **Godot import has NOT been tested.** Unreal import has not been tested.
"""
    open(os.path.join(d, 'README.md'), 'w').write(s)


def contact_sheet(rows):
    tw, th, lab = 400, 225, 250
    W = lab + 4 * (tw + 8) + 8
    H = 70 + len(rows) * (th + 12) + 30
    im = Image.new('RGB', (W, H), (26, 24, 22)); d = ImageDraw.Draw(im)
    f1, f2, f3 = ImageFont.truetype(F_SB, 28), ImageFont.truetype(F_SB, 19), ImageFont.truetype(F_R, 14)
    d.text((16, 16), 'Sheikh Mohammed bin Rashid Boulevard - five podium retail & restaurant assets (Blender Cycles)', font=f1, fill=(240, 232, 218))
    for j, (_k, t) in enumerate(VIEWS):
        d.text((lab + 8 + j * (tw + 8), 50), t, font=f3, fill=(190, 178, 160))
    for i, r in enumerate(rows):
        y = 70 + i * (th + 12)
        d.text((16, y + 6), f"{r['num']}  {r['name']}", font=f2, fill=(245, 238, 225))
        d.text((16, y + 34), f"{r['width_m']} x {r['depth_m']} x {r['height_m']} m", font=f3, fill=(190, 178, 160))
        d.text((16, y + 54), f"{r['storeys']} storey(s)", font=f3, fill=(190, 178, 160))
        d.text((16, y + 74), f"LOD0 {r['lod_tris_glb']['LOD0']:,} tris", font=f3, fill=(190, 178, 160))
        for j, (k, _t) in enumerate(VIEWS):
            p = os.path.join(BV, r['folder'], 'renders', f"{r['base']}_{k}.jpg")
            if os.path.exists(p):
                im.paste(Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS), (lab + 8 + j * (tw + 8), y))
    d.text((16, H - 24), 'Fictional businesses - architectural character inspired by the Boulevard; no real placement implied.', font=f3, fill=(150, 140, 128))
    im.save(os.path.join(BV, 'BOULEVARD_FIVE_CONTACT_SHEET.jpg'), quality=88)


def gallery(rows, street):
    cards = ''
    for r in rows:
        figs = ''.join(f'<figure><a href="{r["folder"]}/renders/{r["base"]}_{k}.jpg"><img loading="lazy" src="{r["folder"]}/renders/{r["base"]}_{k}.jpg" alt="{html.escape(r["name"])} {t}"></a><figcaption>{t}</figcaption></figure>' for k, t in VIEWS)
        t = r['lod_tris_glb']
        cards += f'''<section class="card" id="a{r['num']}"><header><h2><span>{r['num']}</span> {html.escape(r['name'])}</h2><span class="tag">{html.escape(r['type'])}</span></header>
<div class="grid">{figs}</div>
<div class="cols"><div><h3>Architecture</h3><p>{html.escape(r['identity'])}</p><h3>Interior</h3><p>{html.escape(r['interior'])}</p></div>
<table><tr><th>Frontage x depth x height</th><td>{r['width_m']} x {r['depth_m']} x {r['height_m']} m</td></tr>
<tr><th>Storeys</th><td>{r['storeys']}{(' - ' + html.escape(r['storey_note'])) if r.get('storey_note') else ''}</td></tr>
<tr><th>LOD0 / LOD1 / LOD2 tris</th><td>{t['LOD0']:,} / {t['LOD1']:,} / {t['LOD2']:,}</td></tr>
<tr><th>GLB / .blend</th><td>{r['files']['glb_mb']} MB / {r['files']['blend_mb']} MB</td></tr>
<tr><th>Lights</th><td>{r['lights']['INTERIOR_LIGHTING']} interior, {r['lights']['EXTERIOR_LIGHTING']} exterior</td></tr>
<tr><th>Blender validation</th><td class="{'ok' if r['validation']['passed'] else 'bad'}">{'PASS' if r['validation']['passed'] else 'FAIL'}</td></tr>
<tr><th>Files</th><td><a href="{r['folder']}/README.md">README</a> - <a href="{r['folder']}/{r['base']}.glb">GLB</a></td></tr></table></div></section>'''
    sfigs = ''.join(f'<figure><a href="combined_streetscape/{os.path.basename(p)}"><img loading="lazy" src="combined_streetscape/{os.path.basename(p)}" alt="{t}"></a><figcaption>{t}</figcaption></figure>' for p, t in street)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Boulevard Five Gallery</title><style>
:root{{--bg:#f3efe8;--fg:#211d18;--mut:#6b6257;--card:#fffdf9;--line:#e1d9cc;--acc:#8c6a43;--ok:#1d7a46;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16140f;--fg:#efe8dc;--mut:#b0a493;--card:#201d17;--line:#38322a;--acc:#c9a65a;--ok:#5cc98a;--bad:#ff7a70}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:26px 16px 60px}}h1{{font-size:30px;margin:0 0 6px;letter-spacing:.01em}}.lede{{color:var(--mut);max-width:980px}}
nav a{{display:inline-block;margin:4px 12px 4px 0;color:var(--acc)}}.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:24px 0}}
.card header{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}}h2{{margin:0;font-size:23px}}h2 span{{color:var(--acc);margin-right:6px}}
h3{{font-size:15px;margin:12px 0 2px;color:var(--acc)}}.tag{{color:var(--mut);font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:10px;margin-top:12px}}figure{{margin:0}}
img{{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--line)}}figcaption{{font-size:13px;color:var(--mut);margin-top:4px}}
.cols{{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:20px}}@media (max-width:800px){{.cols{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;font-size:13px;width:100%;margin-top:12px}}th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--mut);font-weight:500}}
.ok{{color:var(--ok);font-weight:600}}.bad{{color:var(--bad);font-weight:600}}a{{color:var(--acc)}}.note{{border-left:3px solid var(--acc);padding:8px 12px;background:var(--card);border-radius:6px}}
</style></head><body><main>
<h1>Sheikh Mohammed bin Rashid Boulevard - five podium assets</h1>
<p class="lede">Five premium retail and restaurant podium buildings with the Downtown Dubai Boulevard character: warm limestone, travertine and
champagne stone, dark bronze frames, tall clear glass, recessed entrances, canopies and terraces. Each ends in a podium roof with a rear
tower interface for docking against existing towers. All images are genuine Blender 4.5.15 Cycles renders. Nothing has been tested in Godot.</p>
<p class="note">The businesses are fictional, and the combined streetscape is a presentation layout only: it does not represent real
geographic placement or real tenants.</p>
<nav>{''.join(f'<a href="#a{r["num"]}">{r["num"]} {html.escape(r["name"])}</a>' for r in rows)}<a href="#street">Combined streetscape</a>
<a href="BOULEVARD_BUILD_REPORT.md">Build report</a></nav>
{cards}
<section class="card" id="street"><header><h2>Combined streetscape</h2><span class="tag">presentation layout - not geographic placement</span></header><div class="grid">{sfigs}</div></section>
<p class="tag">Generated {datetime.date.today().isoformat()}. Works offline when opened from this folder.</p></main></body></html>'''
    open(os.path.join(BV, 'BOULEVARD_FIVE_GALLERY.html'), 'w').write(page)


def report(rows, street):
    ok = all(r['validation']['passed'] for r in rows)
    nr = sum(len(r['renders']) for r in rows)
    L = [f'# Boulevard 5 - build report', '',
         f'Generated {datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")} from the files on disk (Blender 4.5.15 LTS via the `bpy` module, Cycles CPU + OIDN, headless Linux cloud container).', '',
         '## Checkpoint', '',
         '- Phase B: 01 Maison Levant, 02 Juniper House: complete',
         '- Phase C: 03 Lune & Laurel Cafe: complete',
         '- Phase D: 04 Galerie D\'Or, 05 The Promenade Galleria: complete',
         f'- Phase E: combined streetscape: {"complete" if len(street) == 4 else "INCOMPLETE"} ({len(street)} renders)',
         f'- Phase F: validation + reports: {"complete" if ok else "see issues"}', '',
         f'**5 / 5 assets built, {nr} / 20 asset renders + {len(street)} streetscape renders. Blender validation: {"PASS" if ok else "FAIL"} for all.**', '',
         '## Summary (triangles read from the exported GLB files)', '',
         '| # | Asset | Storeys | W x D x H (m) | LOD0 | LOD1 | LOD2 | GLB MB | .blend MB | Materials | Lights int/ext | Validation |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        t = r['lod_tris_glb']
        L.append(f"| {r['num']} | {r['name']} | {r['storeys']}{' (+mezz.)' if r.get('storey_note') else ''} | {r['width_m']} x {r['depth_m']} x {r['height_m']} | "
                 f"{t['LOD0']:,} | {t['LOD1']:,} | {t['LOD2']:,} | {r['files']['glb_mb']} | {r['files']['blend_mb']} | {r['materials']} | "
                 f"{r['lights']['INTERIOR_LIGHTING']}/{r['lights']['EXTERIOR_LIGHTING']} | {'PASS' if r['validation']['passed'] else 'FAIL'} |")
    L += ['', '## Architectural diversity', '', '| # | Frontage | Storeys / height | Glass : stone (approx. design intent) | Rhythm | Entrance | Canopy | Upper floor / roof | Terrace |',
          '|---|---|---|---|---|---|---|---|---|',
          '| 01 | 22 m | 2 / 11.2 m | ~60:40 | 5 tall bays, 0.9 m deep piers, symmetric | central, 7 m tall, 3 m recess | 3.4 m deep blade over the entrance only | two-storey glass bays, solid attic with letters | raised deck (left) |',
          '| 02 | 30 m | 1 tall + mezzanine / 9.7 m | ~80:20 | 3 m grid of slender travertine mullions, horizontal | three recessed bays (6 m centre) | 4.6 m deep, full length | stepped crown with bronze fin screen | four decks under the canopy |',
          '| 03 | 16 m | 2 / 10.9 m | ~50:50 | vertical composition + curved glass corner | arched, recessed, left | balcony doubles as canopy | balcony, stepped parapet | small bistro deck |',
          '| 04 | 26 m | 2 / 11.9 m | ~45:55 | four different boutique shopfronts | central recess under a bay window | none (fascias) | punched windows, bay window, fluted attic | none |',
          '| 05 | 34 m | 3 / 18.6 m (towers) | ~70:30 | towers + arcade colonnade + curtain wall | 12 m x 15 m atrium portal | glass + bronze, 5 m deep | curtain wall with fins, tower crowns, skylight | none (arcade) |', '',
          'Only low-level construction helpers are shared (`bv_core.py` on top of the read-only premium kit). Each building has its own script that defines its massing, plan, facade rhythm, entrance, interior and site.', '',
          '## Validation (per asset, `NN_*/validation.json`)', '',
          'Each asset went through these steps: the build was saved, reopened in a fresh Blender process, run through mesh.validate, degenerate-face, winding, UV and material-slot checks, and checked that glass alpha is below 1 with blend mode set. LOD counts were checked to decrease and their extras to be present. Dimensions were recorded. The GLB was exported, parsed with embedded images decoded, and re-imported into a clean scene with triangle totals compared. Four renders were made, and interior probe points were ray-traced from the day and road cameras (glass may be crossed, opaque geometry may not).', '']
    for r in rows:
        vis = r['visibility'].get('road_view_visibility') or {}
        pr = vis.get('probes', [])
        vd = r['visibility'].get('day_visibility') or {}
        prd = vd.get('probes', [])
        L.append(f"- {r['num']} {r['name']}: {'PASS' if r['validation']['passed'] else 'FAIL'}; re-import {r['validation']['reimport']['triangles']:,} = GLB {r['validation']['reimport']['glb_triangles']:,} tris; "
                 f"{r['validation']['reimport']['images_loaded']} textures loaded; interior probes visible: road view {sum(p['reached'] and p['in_frame'] for p in pr)}/{len(pr)}, "
                 f"day view {sum(p['reached'] and p['in_frame'] for p in prd)}/{len(prd)}; warnings: {r['validation']['warnings'] or 'none'}")
    L += ['', '## LOD recommendations', '', '- LOD0 0-110 m, LOD1 110-300 m, LOD2 300-1800 m, 8 m hysteresis (glTF node extras; Godot: `../premium_commercial_17/premium_lod_post_import.gd`).',
          '- The glass facade and main entrance remain in every LOD. LOD2 replaces interiors with emissive glow proxies behind the glass.',
          '- Unreal Engine 5: use the `unreal/*_LOD0/1/2.fbx` files (or the GLB through the Interchange glTF importer). Glass should be Translucent with Surface Forward Shading. Use LOD0 with Nanite, or set up LOD1/2 as LOD groups.', '',
          '## Combined streetscape', '', f'`combined_streetscape/boulevard_five_streetscape.blend`: the five assets were appended side by side (128 m of continuous frontage) on one promenade, with {len(street)} renders. '
          'This is a presentation demonstration only. The order and adjacency are not real geographic placement.', '',
          '## Known limitations', '',
          '- **Godot import has NOT been tested**, and neither has Unreal import. The cloud session cannot reach the local `Dubai-Game-Godot` / `Dubai-Game-Godot-PC-Test` projects, which were not touched, and nothing was copied to the user\'s computer.',
          '- Glass is alpha-blended (engine-friendly), not refractive.',
          '- Kitchens and back-of-house areas are closed off by partitions and are not modelled.',
          '- The tower slot windows on The Promenade Galleria are glazed panels on the stone cores, which are service and stair cores with no public interior behind them.',
          '- People, vehicles and vegetation are not modelled (vegetation is excluded by request; planters are empty).',
          '- The preview street, neighbouring stub buildings and sky are render-only (`_PREVIEW_NOT_EXPORTED`).',
          '- Fictional business names and signage use the OFL fonts Cinzel and Cormorant Garamond (`_tools/fonts/FONTS_LICENSE.md`).', '',
          '## Git', '', f'- Branch: `{sh("git rev-parse --abbrev-ref HEAD")}`. The final commit hash is given in the final report message.']
    open(os.path.join(BV, 'BOULEVARD_BUILD_REPORT.md'), 'w').write('\n'.join(L) + '\n')


rows = collect()
for r in rows:
    readme(r)
street = [(os.path.join(BV, 'combined_streetscape', f'streetscape_{k}.jpg'), t) for k, t in
          (('overview_day', 'Overview - day'), ('overview_night', 'Overview - night'), ('promenade_day', 'Promenade - pedestrian level, day'),
           ('driver_night', 'Boulevard - driver height, night'))]
street = [s for s in street if os.path.exists(s[0])]
contact_sheet(rows)
gallery(rows, street)
report(rows, street)
man = dict(collection='Sheikh Mohammed bin Rashid Boulevard - 5 podium assets', generated=datetime.datetime.utcnow().isoformat() + 'Z',
           units='metres', up='Z (Blender) / Y (glTF)', front='-Y (Blender) / +Z (glTF)', fictional_businesses=True,
           placement_note='No real-world coordinates or tenant positions; streetscape is a presentation layout only.',
           godot_tested=False, unreal_tested=False, lod_ranges_m={'LOD0': [0, 110], 'LOD1': [110, 300], 'LOD2': [300, 1800]},
           streetscape=dict(blend='combined_streetscape/boulevard_five_streetscape.blend', renders=[os.path.relpath(p, BV) for p, _ in street]),
           assets=[{k: v for k, v in r.items() if k not in ('materials_used',)} | dict(materials_used=r['materials_used']) for r in rows])
json.dump(man, open(os.path.join(BV, 'BOULEVARD_ASSET_MANIFEST.json'), 'w'), indent=1)
print('BV_REPORTS_OK', [r['validation']['passed'] for r in rows])
