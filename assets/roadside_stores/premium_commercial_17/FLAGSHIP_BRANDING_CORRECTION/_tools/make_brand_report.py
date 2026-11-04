"""Phase A reports: FLAGSHIP_BRANDING_CORRECTIONS.jpg, FLAGSHIP_BRANDING_CORRECTION_GALLERY.html,
BRAND_CORRECTION_REPORT.md and a "Brand signage correction" section appended to each flagship README.md.
Plain CPython + Pillow (no Blender needed)."""
import os, sys, json, html, datetime, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.normpath(os.path.join(HERE, '..'))
P17 = os.path.normpath(os.path.join(FIX, '..'))
REPO = os.path.normpath(os.path.join(P17, '..', '..', '..'))
VAL = json.load(open(os.path.join(FIX, 'brand_fix_validation.json')))
F_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
F_R = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'

BRANDS = [
    ('01', '01_mercedes_showroom', 'mercedes_showroom', 'Mercedes-Benz',
     'Dimensional three-pointed star in ring on the granite core (4.0 m), official wordmark on the roof plate (11.0 m) and under the star (3.4 m).',
     'Star: simple-icons 5.0.0 (source mercedes-benz.com). Wordmark: official 1792 px image from mercedes-benz.com, potrace-vectorised.'),
    ('02', '02_bmw_showroom', 'bmw_showroom', 'BMW',
     'Dealership roundel (black ring, white letters, blue/white quarters, chrome rims) on the blade (3.8 m) and pylon (2.3 m).',
     'simple-icons bmw (source bmw.com); physical-emblem colours composed from that vector.'),
    ('03', '03_porsche_showroom', 'porsche_showroom', 'Porsche',
     'Official PORSCHE wordmark on the upper box fascia (7.5 m); coloured crest (1.22 m) + wordmark (3.5 m) on the forecourt monolith.',
     'Wordmark: Porsche Design System (official vector). Crest: simple-icons line-art coloured from the official 2023 crest image (recreation).'),
    ('04', '04_ford_showroom', 'ford_showroom', 'Ford',
     'Blue Oval (7.4 x 2.78 m) with raised white script and rim on the portal; supporting SERVICE / PARTS texts re-set in Inter.',
     'ford.com navigation logo SVG (official vector, #00095B).'),
    ('05', '05_samsung_flagship', 'samsung_flagship', 'Samsung',
     'SAMSUNG wordmark (4.9 m, white reversed on the black fascia) as illuminated channel letters; EXPERIENCE STORE line re-set in Inter.',
     'simple-icons samsung (source samsung.com brand identity).'),
    ('06', '06_apple_flagship', 'apple_flagship', 'Apple',
     'Illuminated Apple logo (1.95 m) suspended behind the glass on the existing rod + small flank logo (1.0 m); no store-name text.',
     'apple.com global navigation SVG (official vector).'),
    ('07', '07_xiaomi_flagship', 'xiaomi_flagship', 'Xiaomi',
     'Orange MI symbol (2.2 m) on the portal; lowercase "xiaomi" wordmark (3.6 m) as dark halo-lit letters on the white fascia.',
     'Squircle + #ff6900 from mi.com; MI glyph simple-icons (source mi.com); wordmark typeset in MiSans (recreation).'),
]
VIEWS = [('before', 'Before (original signage)'), ('front_day', 'Corrected - front, day'), ('front_night', 'Corrected - front, night'),
         ('road', 'Corrected - road level')]


def img_path(num, folder, base, v):
    if v == 'before':
        return os.path.join(FIX, 'renders', f'{num}_before_front_day.jpg')
    return os.path.join(P17, folder, 'renders', f'{base}_signage_{v}.jpg')


def contact_sheet():
    tw, th, lab = 420, 236, 300
    W = lab + 4 * (tw + 8) + 8
    H = 70 + len(BRANDS) * (th + 12) + 30
    im = Image.new('RGB', (W, H), (24, 25, 28)); d = ImageDraw.Draw(im)
    f1, f2, f3 = ImageFont.truetype(F_SB, 30), ImageFont.truetype(F_SB, 20), ImageFont.truetype(F_R, 14)
    d.text((16, 16), 'Flagship branding corrections - official-vector signage (internal test assets, no endorsement implied)', font=f1,
           fill=(235, 235, 235))
    for j, (_v, t) in enumerate(VIEWS):
        d.text((lab + 8 + j * (tw + 8), 52), t, font=f3, fill=(170, 170, 170))
    for i, (num, folder, base, name, what, src) in enumerate(BRANDS):
        y = 70 + i * (th + 12)
        d.text((16, y + 8), f'{num}  {name}', font=f2, fill=(240, 240, 240))
        words, line, yy = what.split(), '', y + 40
        for w in words:
            if d.textlength(line + ' ' + w, font=f3) > lab - 30:
                d.text((16, yy), line.strip(), font=f3, fill=(180, 180, 180)); yy += 18; line = ''
            line += ' ' + w
        d.text((16, yy), line.strip(), font=f3, fill=(180, 180, 180))
        for j, (v, _t) in enumerate(VIEWS):
            p = img_path(num, folder, base, v)
            x = lab + 8 + j * (tw + 8)
            if os.path.exists(p):
                t = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
                im.paste(t, (x, y))
            else:
                d.rectangle([x, y, x + tw, y + th], outline=(90, 90, 90)); d.text((x + 10, y + 10), 'missing', font=f3, fill=(200, 80, 80))
    d.text((16, H - 24), 'Blender 4.5.15 Cycles renders, ' + datetime.date.today().isoformat() + '. Marks are trademarks of their owners.',
           font=f3, fill=(140, 140, 140))
    im.save(os.path.join(FIX, 'FLAGSHIP_BRANDING_CORRECTIONS.jpg'), quality=88)


def rel(p):
    return os.path.relpath(p, FIX).replace(os.sep, '/')


def gallery():
    cards = []
    for num, folder, base, name, what, src in BRANDS:
        a = VAL['assets'][num]
        els = a['checks']['elements']
        rows = ''.join(f'<tr><td>{html.escape(e["element"])}</td><td><code>{e["logo"]}</code></td>'
                       f'<td>{e["lods"]["LOD0"]["width_m"]} x {e["lods"]["LOD0"]["height_m"]}</td>'
                       f'<td>{e["lods"]["LOD0"]["tris"]:,} / {e["lods"]["LOD1"]["tris"]:,} / {e["lods"]["LOD2"]["tris"]:,}</td>'
                       f'<td>{e["aspect_error_pct"]}%</td></tr>' for e in els)
        figs = ''.join(f'<figure><a href="{rel(img_path(num, folder, base, v))}"><img loading="lazy" src="{rel(img_path(num, folder, base, v))}" '
                       f'alt="{html.escape(name)} {t}"></a><figcaption>{t}</figcaption></figure>' for v, t in VIEWS)
        extra = ''
        if num == '03':
            p = os.path.join(P17, folder, 'renders', f'{base}_signage_detail_day.jpg')
            extra = f'<figure class="wide"><img loading="lazy" src="{rel(p)}" alt="Porsche monolith crest detail"><figcaption>Detail - crest + wordmark on the forecourt monolith</figcaption></figure>'
        cards.append(f'''<section class="card" id="b{num}"><header><h2><span>{num}</span> {html.escape(name)}</h2>
<span class="pill {'ok' if a['passed'] else 'bad'}">{'Blender validation PASS' if a['passed'] else 'FAIL'}</span></header>
<p>{html.escape(what)}</p><p class="src"><b>Artwork source:</b> {html.escape(src)}</p>
<div class="grid">{figs}{extra}</div>
<table><thead><tr><th>Sign element</th><th>Logo</th><th>Size LOD0 (m)</th><th>Tris LOD0 / 1 / 2</th><th>Proportion error</th></tr></thead><tbody>{rows}</tbody></table>
</section>''')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flagship Branding Corrections</title>
<style>
:root{{--bg:#f4f2ee;--fg:#1d1d1f;--mut:#5e5e63;--card:#fff;--line:#dedad3;--ok:#1d7a46;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151517;--fg:#ececee;--mut:#a3a3a8;--card:#1f1f22;--line:#333338;--ok:#5cc98a;--bad:#ff7a70}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:24px 16px 60px}}h1{{font-size:28px;margin:0 0 6px}}.lede{{color:var(--mut);max-width:980px}}
nav a{{display:inline-block;margin:4px 10px 4px 0;color:inherit}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:22px 0}}
.card header{{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}}.card h2{{margin:0;font-size:22px}}
.card h2 span{{color:var(--mut);font-weight:500;margin-right:6px}}.pill{{font-size:12px;padding:3px 10px;border-radius:99px;border:1px solid}}
.ok{{color:var(--ok)}}.bad{{color:var(--bad)}}.src{{color:var(--mut);font-size:14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px}}figure{{margin:0}}figure.wide{{grid-column:1/-1}}
img{{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--line)}}figcaption{{font-size:13px;color:var(--mut);margin-top:4px}}
table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px}}th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}}
.scroll{{overflow-x:auto}}code{{font-size:12px}}.note{{border-left:3px solid #c9a65a;padding:8px 12px;background:var(--card);border-radius:6px}}
</style></head><body><main>
<h1>Flagship branding corrections</h1>
<p class="lede">Seven premium flagships with only their brand identity corrected: official or officially-sourced vector logos,
built as extruded sign geometry (LOD0/LOD1) and exact vector-rendered cards (LOD2). Building geometry, interiors, cars, glass,
lighting and collision are unchanged. Every non-signage glTF node is verified identical to the originals. These are Blender
renders; nothing here has been tested in Godot.</p>
<p class="note">Internal test-game assets. No brand partnership, dealership authorisation or endorsement is implied. See
<a href="BRAND_ASSET_SOURCES.md">BRAND_ASSET_SOURCES.md</a> for provenance and the permissions needed before any public release.</p>
<nav>{''.join(f'<a href="#b{n}">{n} {html.escape(nm)}</a>' for n, _f, _b, nm, _w, _s in BRANDS)}</nav>
<figure><img src="textures/logo_library_preview.jpg" alt="Corrected logo library"><figcaption>Corrected logo library (vector renders)</figcaption></figure>
{''.join(cards)}
<p class="src">Generated {datetime.date.today().isoformat()} - all images are relative links and work offline when this folder is kept next to the flagship folders.</p>
</main></body></html>'''
    open(os.path.join(FIX, 'FLAGSHIP_BRANDING_CORRECTION_GALLERY.html'), 'w').write(page)


def readmes_and_report():
    lines = ['# Flagship brand signage correction - report', '',
             f'Generated {datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ")} from the files on disk. Blender 4.5.15 LTS (bpy), Cycles CPU.', '',
             '**Scope:** only signage was changed in `01`-`07`. Building geometry, interiors, placeholder cars, glass, lighting, '
             'materials not related to signage, LOD structure and collision are untouched. Every re-exported GLB was diffed node-by-node '
             'against the original commit: **all non-signage nodes have identical triangle counts and the lights are unchanged** '
             '(`brand_fix_validation.json`).', '',
             f'Overall Blender validation: **{"PASS" if VAL["all_passed"] else "FAIL"}**. Godot import has NOT been tested (the cloud session '
             'cannot reach the local Godot projects, which were not touched).', '',
             '| # | Brand | Corrected marks | Artwork source | LOD0 / LOD1 / LOD2 sign tris | GLB tris before -> after | Validation |',
             '|---|---|---|---|---|---|---|']
    for num, folder, base, name, what, src in BRANDS:
        a = VAL['assets'][num]
        t = [sum(e['lods'][f'LOD{L}']['tris'] for e in a['checks']['elements']) for L in (0, 1, 2)]
        g = a['checks']['glb_diff_vs_original'][base + '.glb']
        lines.append(f'| {num} | {name} | {what} | {src} | {t[0]:,} / {t[1]:,} / {t[2]:,} | {g["tris_before"]:,} -> {g["tris_after"]:,} '
                     f'| {"PASS" if a["passed"] else "FAIL"} |')
    lines += ['', '## Files changed in each flagship folder', '',
              '- `<base>.blend`: old brand objects moved to the excluded `BRAND_SIGNAGE_ORIGINAL_DISABLED` collection (mounting structures '
              'kept as `<P>_LODn_SIGNAGE_Mounting`), plus the new `BRAND_SIGNAGE_CORRECTED` / `LOD1_` / `LOD2_` collections',
              '- `<base>.glb`, `<base>_building_only.glb` (automotive), `lod/<base>_lod0/1/2.glb`: re-exported with the original exporter settings',
              '- `textures/brand_*.png`: vector-rendered sign textures (LOD2 cards, Porsche crest face)',
              '- `renders/<base>_signage_front_day.jpg`, `_front_night.jpg`, `_road.jpg` (+ Porsche `_detail_day.jpg`): new targeted renders',
              '- `brand_signage_correction.json`: per-asset validation, measured sign sizes, GLB diff',
              '- `README.md`: a "Brand signage correction" section appended',
              '', 'Not changed: `validation.json`, `lod/build_stats.json`, the original four renders, `../PREMIUM_ASSET_MANIFEST.json` and '
              '`../BUILD_REPORT.md`. These still describe the original build, and their signage triangle counts are superseded by the '
              'numbers here. The old procedural logo PNGs stay in `textures/` (no longer referenced).', '',
              '## Validation performed', '',
              '1. Each `.blend` reopened in a fresh Blender process: corrected collections are present and nested in LOD0/1/2, the original signage '
              'is excluded from the view layer and is outside the export tree, and no old `_SIGNAGE_Brand` object is still exported.',
              '2. `Mesh.validate()` was run on every corrected sign object, with no empty material slots and UVs present.',
              '3. Logo proportions: the width/height of every LOD0 sign was measured in the sign plane and compared with the ink bounds of '
              'its source vector. The maximum error is 0.14 %.',
              '4. Spelling: all wordmarks are the brand vectors themselves (no typed text). The supporting texts are "SERVICE", '
              '"PARTS & SERVICE RECEPTION" and "EXPERIENCE STORE".',
              '5. GLB diff against the original commit (main, building-only and the per-LOD files).',
              '6. Targeted Cycles renders: front day, front night and road level, plus a before view rendered from the original `.blend`.', '',
              'See `BRAND_ASSET_SOURCES.md` for provenance, known gaps and permissions.']
    open(os.path.join(FIX, 'BRAND_CORRECTION_REPORT.md'), 'w').write('\n'.join(lines) + '\n')
    marker = '## Brand signage correction'
    for num, folder, base, name, what, src in BRANDS:
        p = os.path.join(P17, folder, 'README.md')
        s = open(p).read()
        if marker in s:
            s = s[:s.index(marker)].rstrip() + '\n'
        a = VAL['assets'][num]
        s += (f'\n{marker}\n\nThe brand identity was corrected on branch `claude/flagship-brand-fixes-boulevard-5`, and only the signage changed. '
              f'{what} Artwork: {src} Old signage: `BRAND_SIGNAGE_ORIGINAL_DISABLED` collection in the .blend (not exported). '
              f'New signage: `BRAND_SIGNAGE_CORRECTED` (+ `LOD1_` / `LOD2_`). Renders: `renders/{base}_signage_*.jpg`. '
              f'Validation: `brand_signage_correction.json` ({"PASS" if a["passed"] else "FAIL"}). Provenance and permissions: '
              f'`../FLAGSHIP_BRANDING_CORRECTION/BRAND_ASSET_SOURCES.md`. Internal test asset; no endorsement implied.\n')
        open(p, 'w').write(s)


contact_sheet(); gallery(); readmes_and_report()
print('BRAND_REPORTS_OK')
