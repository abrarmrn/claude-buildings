"""Build the corrected brand-logo library for the seven flagship showrooms.

Input : ../source_vectors/original/   (official / officially-sourced artwork, see ../BRAND_ASSET_SOURCES.md)
Output: ../source_vectors/final/*.svg (normalised, layered SVGs with explicit brand colours; read by apply_brand_fix.py)
        ../textures/*.png             (high-resolution RGBA renders of the same vectors, for flat decals / LOD2 cards)
        ../textures/logo_library_preview.jpg

Run with plain CPython 3.11 + cairosvg, svgelements, potracer, fonttools[woff2], scipy, pillow, numpy.
Nothing here invents a logo shape: every outline comes from a vector or raster published by the brand
(or a source-cited vector copy of it); only the colour layering for physical signs is composed here.
"""
import os, re, io, math, json
import numpy as np
from PIL import Image, ImageFilter
import cairosvg
from svgelements import SVG, Path, Shape, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
ORIG = os.path.join(ROOT, 'source_vectors', 'original')
FINAL = os.path.join(ROOT, 'source_vectors', 'final')
TEX = os.path.join(ROOT, 'textures')
os.makedirs(FINAL, exist_ok=True); os.makedirs(TEX, exist_ok=True)

# ---- brand colours (see BRAND_ASSET_SOURCES.md for where each value comes from)
C = dict(
    mb_silver='#E6E8EA',          # illuminated star / wordmark face (physical sign: white acrylic + chrome return)
    bmw_black='#111214', bmw_blue='#0066B1', bmw_white='#FFFFFF', bmw_chrome='#C3C7CB',
    po_gold='#D49E4E', po_red='#8C0A0A', po_black='#121212', po_frame='#E2BD78',
    ford_blue='#00095B', ford_white='#FFFFFF',
    samsung_blue='#1428A0',
    apple_white='#F5F5F7',
    xiaomi_orange='#FF6900', xiaomi_white='#FFFFFF',
)


def src(n):
    return os.path.join(ORIG, n)


def path_items(fn):
    """[(fill, d, [subpath d strings])] for every shape in an SVG (transforms applied)."""
    out = []
    for el in SVG.parse(fn).elements():
        if isinstance(el, Shape) and not isinstance(el, SVG):
            p = Path(el)
            if len(p) == 0:
                continue
            fill = el.fill.hex if el.fill is not None and el.fill.value is not None else '#000000'
            out.append((fill, p.d(relative=False), [Path(sp).d(relative=False) for sp in p.as_subpaths()]))
    return out


def viewbox(fn):
    s = open(fn).read()
    return [float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).replace(',', ' ').split()]


def write_svg(name, vb, layers, note):
    """layers: [(layer_id, fill, d)] painted in order (later on top). fill-rule even-odd."""
    body = '\n'.join(f'  <path id="{lid}" fill="{fill}" fill-rule="evenodd" d="{d}"/>' for lid, fill, d in layers)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:g} {vb[1]:g} {vb[2]:g} {vb[3]:g}">\n'
           f'  <!-- {note} -->\n{body}\n</svg>\n')
    p = os.path.join(FINAL, name)
    open(p, 'w').write(svg)
    return p


def raster(svgp, png, long_side=4096, pad=0.0):
    vb = viewbox(svgp)
    w, h = vb[2], vb[3]
    s = long_side / max(w, h)
    cairosvg.svg2png(url=svgp, write_to=png, output_width=int(round(w * s)), output_height=int(round(h * s)))
    return png


def circle_d(cx, cy, r):
    return (f'M{cx - r:.4f},{cy:.4f} A{r:.4f},{r:.4f} 0 1,0 {cx + r:.4f},{cy:.4f} '
            f'A{r:.4f},{r:.4f} 0 1,0 {cx - r:.4f},{cy:.4f} Z')


def sector_d(cx, cy, r, a0, a1):
    """Pie sector in SVG (y-down) coordinates, angles in degrees measured clockwise from +x."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    return f'M{cx:.4f},{cy:.4f} L{x0:.4f},{y0:.4f} A{r:.4f},{r:.4f} 0 0,1 {x1:.4f},{y1:.4f} Z'


manifest = {}


# ---------------------------------------------------------------------------------------------- 1 Mercedes-Benz
def mercedes():
    fn = src('mercedes_star_simpleicons5.svg')
    items = path_items(fn)
    p = write_svg('mercedes_star.svg', viewbox(fn), [('star', C['mb_silver'], items[0][1])],
                  'Mercedes-Benz three-pointed star in ring. Outline unchanged from simple-icons 5.0.0 "mercedes" '
                  '(source: https://www.mercedes-benz.com/). Colour = sign face.')
    manifest['mercedes_star'] = dict(svg=p, kind='mono', aspect=1.0)
    # wordmark: official raster (mercedes-benz.com footer, 1792x224 RGBA) -> potrace vector (outline only, no redraw)
    import potrace
    im = Image.open(src('mercedes_wordmark_mbcom.png')).convert('RGBA')
    a = np.array(im)[..., 3].astype(np.float32) / 255.0
    up = 3
    a2 = np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((im.width * up, im.height * up), Image.BICUBIC)) / 255.0
    bm = potrace.Bitmap(a2 <= 0.5)          # potracer: dark (False/0) = ink
    plist = bm.trace(turdsize=6, alphamax=1.0, opticurve=True, opttolerance=0.2)
    parts = []
    for curve in plist:
        st = curve.start_point
        seg = [f'M{st.x / up:.3f},{st.y / up:.3f}']
        for s in curve.segments:
            if s.is_corner:
                seg.append(f'L{s.c.x / up:.3f},{s.c.y / up:.3f} L{s.end_point.x / up:.3f},{s.end_point.y / up:.3f}')
            else:
                seg.append(f'C{s.c1.x / up:.3f},{s.c1.y / up:.3f} {s.c2.x / up:.3f},{s.c2.y / up:.3f} '
                           f'{s.end_point.x / up:.3f},{s.end_point.y / up:.3f}')
        parts.append(' '.join(seg) + ' Z')
    # tight viewBox around the ink
    ys, xs = np.nonzero(a > 0.5)
    vb = [float(xs.min()) - 2, float(ys.min()) - 2, float(xs.max() - xs.min()) + 4, float(ys.max() - ys.min()) + 4]
    p = write_svg('mercedes_wordmark.svg', vb, [('wordmark', C['mb_silver'], ' '.join(parts))],
                  'Mercedes-Benz wordmark, vectorised 1:1 (potrace, 3x supersampled) from the official logo image '
                  'embedded in https://www.mercedes-benz.com/en/ (footer, 1792x224 px). No glyph redrawn.')
    manifest['mercedes_wordmark'] = dict(svg=p, kind='mono', aspect=vb[2] / vb[3])


# ---------------------------------------------------------------------------------------------- 2 BMW
def bmw():
    fn = src('bmw_simpleicons.svg')
    subs = path_items(fn)[0][2]
    # subpath order (measured): 0 outer r=12, 1 r=11.22, 2 M, 3 W, 4 B, 5/7 B counters, 6 r=7.12, 8 quadrant cut r=6.18
    outline = subs[0] + ' ' + subs[1]
    letters = ' '.join(subs[i] for i in (2, 3, 4, 5, 7))
    cx = cy = 12.0
    layers = [
        ('ring', C['bmw_black'], circle_d(cx, cy, 12.0)),
        ('outer_chrome', C['bmw_chrome'], outline),
        ('letters', C['bmw_white'], letters),
        ('inner_chrome', C['bmw_chrome'], circle_d(cx, cy, 7.12)),
        ('white', C['bmw_white'], circle_d(cx, cy, 6.18)),
        # blue quarters top-left + bottom-right (SVG y-down: TL = 180..270 deg, BR = 0..90 deg)
        ('blue', C['bmw_blue'], sector_d(cx, cy, 6.18, 180, 270) + ' ' + sector_d(cx, cy, 6.18, 0, 90)),
    ]
    p = write_svg('bmw_roundel.svg', viewbox(fn), layers,
                  'BMW roundel, physical dealership emblem colouring (black ring, white letters, blue/white quarters, '
                  'chrome rims). Letterforms + ring radii unchanged from simple-icons "bmw" (source: https://bmw.com). '
                  'Quarter radius 6.18 and inner rim 7.12 measured from the same vector.')
    manifest['bmw_roundel'] = dict(svg=p, kind='layered', aspect=1.0)


# ---------------------------------------------------------------------------------------------- 3 Porsche
def porsche():
    fn = src('porsche_wordmark_pds.svg')
    d = path_items(fn)[0][1]
    p = write_svg('porsche_wordmark.svg', viewbox(fn), [('wordmark', '#F2F2F2', d)],
                  'PORSCHE wordmark, path copied unchanged from the official Porsche Design System '
                  '(github.com/porsche-design-system/porsche-design-system, packages/components/src/components/wordmark/wordmark.tsx).')
    manifest['porsche_wordmark'] = dict(svg=p, kind='mono', aspect=4500 / 300)
    # crest: vector line-art (simple-icons "porsche", source porsche.com) coloured from the official PDS crest image
    from scipy import ndimage
    fn = src('porsche_simpleicons.svg')
    vb = viewbox(fn)
    H = 3000
    s = H / vb[3]
    Wd = int(round(vb[2] * s))
    png = cairosvg.svg2png(url=fn, output_width=Wd, output_height=H)
    ink = np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[..., 3] > 127
    # silhouette = everything enclosed by the outer outline
    filled = ndimage.binary_fill_holes(ink)
    ys, xs = np.nonzero(filled)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    ink, filled = ink[y0:y1, x0:x1], filled[y0:y1, x0:x1]
    h, w = ink.shape
    ref = np.array(Image.open(src('porsche_crest_pds@3x.png')).convert('RGBA')).astype(np.float32)
    ra = ref[..., 3] > 127
    ry, rx = np.nonzero(ra)
    ref = ref[ry.min():ry.max() + 1, rx.min():rx.max() + 1, :3]
    ref_big = np.array(Image.fromarray(ref.astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32)
    pal = {'gold': C['po_gold'], 'red': C['po_red'], 'black': C['po_black']}
    pal_rgb = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)], np.float32) for k, v in pal.items()}

    def snap(rgb):
        r, g, b = rgb
        if r > 95 and g > 75 and r - b > 40:
            return 'gold'
        if r > 70 and g < 60:
            return 'red'
        return 'black'
    out = np.zeros((h, w, 4), np.uint8)
    labels = {}
    # non-ink regions inside the silhouette: one colour per region (sampled from the official crest, region median)
    lab, n = ndimage.label(filled & ~ink)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 30:
            col = 'black'
        else:
            core = ndimage.binary_erosion(m, iterations=3)
            core = core if core.sum() > 10 else m
            col = snap(np.median(ref_big[core], axis=0))
        out[m, :3] = pal_rgb[col]; out[m, 3] = 255
        labels[col] = labels.get(col, 0) + 1
    # ink: black linework, except the outer frame band which is the gold metal rim on the real crest
    dist_out = ndimage.distance_transform_edt(filled)
    frame = ink & (dist_out < 0.012 * w)
    inkonly = ink & ~frame
    out[inkonly, :3] = pal_rgb['black']; out[inkonly, 3] = 255
    out[frame, :3] = np.array([int(C['po_frame'][i:i + 2], 16) for i in (1, 3, 5)]); out[frame, 3] = 255
    # centre shield: the line-art draws it inverted (white horse on black) -> real crest = black horse on gold
    cy0, cy1, cx0, cx1 = int(0.36 * h), int(0.80 * h), int(0.33 * w), int(0.67 * w)
    sub_ink = ink[cy0:cy1, cx0:cx1]
    lab2, n2 = ndimage.label(sub_ink)
    if n2:
        big = 1 + int(np.argmax(ndimage.sum(sub_ink, lab2, range(1, n2 + 1))))
        shield = ndimage.binary_fill_holes(lab2 == big)
        rim = shield & ~ndimage.binary_erosion(shield, iterations=int(0.012 * w))
        inner = shield & ~rim
        region = out[cy0:cy1, cx0:cx1]
        inner_ink = inner & sub_ink
        inner_gap = inner & ~sub_ink
        region[inner_ink, :3] = pal_rgb['gold']
        region[inner_gap, :3] = pal_rgb['black']
        region[rim, :3] = pal_rgb['black']
    img = Image.fromarray(out, 'RGBA')
    # soften the 1-px stair steps of the labelling (alpha unchanged)
    rgb = img.convert('RGB').filter(ImageFilter.SMOOTH)
    img = Image.merge('RGBA', (*rgb.split(), img.split()[3]))
    crest_png = os.path.join(TEX, 'porsche_crest_2048.png')
    img.resize((int(round(2048 * w / h)), 2048), Image.LANCZOS).save(crest_png)
    # crest outline (silhouette) as vector for the extruded plaque: outer subpath of the simple-icons crest
    subs = path_items(fn)[0][2]
    outer = max(subs, key=lambda d: Path(d).bbox()[2] - Path(d).bbox()[0])
    bb = Path(outer).bbox()
    p = write_svg('porsche_crest_outline.svg', [bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]], [('outline', C['po_frame'], outer)],
                  'Porsche crest silhouette = outer subpath of simple-icons "porsche" (source https://www.porsche.com). '
                  'Face artwork = textures/porsche_crest_2048.png.')
    manifest['porsche_crest'] = dict(svg=p, png=crest_png, kind='plaque', aspect=w / h, regions=labels)


# ---------------------------------------------------------------------------------------------- 4 Ford
def ford():
    fn = src('ford_oval_fordcom.svg')
    items = path_items(fn)
    layers = [('oval', C['ford_blue'], items[0][1])]
    for i, (fill, d, subs) in enumerate(items[1:]):
        layers.append((f'white{i}', C['ford_white'], d))
    p = write_svg('ford_oval.svg', viewbox(fn), layers,
                  'Ford Blue Oval, paths and colours unchanged from the official ford.com navigation logo symbol '
                  '"navigation-menu-ford-logo" (fill #00095B + white script and rim).')
    manifest['ford_oval'] = dict(svg=p, kind='layered', aspect=80 / 30)


# ---------------------------------------------------------------------------------------------- 5 Samsung
def samsung():
    fn = src('samsung_simpleicons.svg')
    items = path_items(fn)
    d = ' '.join(it[1] for it in items)
    sub = Path(d).bbox()
    vb = [sub[0], sub[1], sub[2] - sub[0], sub[3] - sub[1]]
    p = write_svg('samsung_wordmark.svg', vb, [('wordmark', C['samsung_blue'], d)],
                  'SAMSUNG wordmark, unchanged from simple-icons "samsung" (source/guidelines: '
                  'https://www.samsung.com/us/about-us/brand-identity/logo/). Samsung Blue #1428A0.')
    manifest['samsung_wordmark'] = dict(svg=p, kind='mono', aspect=vb[2] / vb[3])


# ---------------------------------------------------------------------------------------------- 6 Apple
def apple():
    fn = src('apple_logo_applecom.svg')
    items = path_items(fn)
    d = ' '.join(it[1] for it in items)
    bb = Path(d).bbox()
    vb = [bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]]
    p = write_svg('apple_logo.svg', vb, [('apple', C['apple_white'], d)],
                  'Apple logo, path unchanged from the apple.com global navigation (https://www.apple.com/ae/).')
    manifest['apple_logo'] = dict(svg=p, kind='mono', aspect=vb[2] / vb[3])


# ---------------------------------------------------------------------------------------------- 7 Xiaomi
def xiaomi():
    fn = src('xiaomi_simpleicons.svg')
    subs = path_items(fn)[0][2]
    squ = path_items(src('xiaomi_squircle_micom.svg'))[0][1]       # official squircle (mi.com header), viewBox 112
    k = 112.0 / 24.0
    mi = Path(' '.join(subs[1:])) * Matrix(f'scale({k})')
    layers = [('squircle', C['xiaomi_orange'], squ), ('mi', C['xiaomi_white'], mi.d(relative=False))]
    p = write_svg('xiaomi_mi_symbol.svg', [0, 0, 112, 112], layers,
                  'Xiaomi MI symbol: squircle path + #FF6900 copied from the official mi.com header logo; MI letterform '
                  'from simple-icons "xiaomi" (source https://www.mi.com/global) scaled x112/24.')
    manifest['xiaomi_mi_symbol'] = dict(svg=p, kind='layered', aspect=1.0)
    # lowercase wordmark set in Xiaomi's own MiSans typeface (official font, free commercial-use licence)
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    f = TTFont(src('MiSansLatin-Demibold.woff2'))
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
    x = 0.0; ds = []
    hmtx = f['hmtx']
    for ch in 'xiaomi':
        gn = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[gn].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        ds.append(pen.getCommands())
        x += hmtx[gn][0]
    d = ' '.join(ds)
    bb = Path(d).bbox()
    vb = [bb[0] - 10, bb[1] - 10, bb[2] - bb[0] + 20, bb[3] - bb[1] + 20]
    p = write_svg('xiaomi_wordmark.svg', vb, [('wordmark', C['xiaomi_white'], d)],
                  'Lowercase "xiaomi" set in MiSans Latin Demibold (Xiaomi official typeface) - typographic recreation, '
                  'NOT the official wordmark artwork file.')
    manifest['xiaomi_wordmark'] = dict(svg=p, kind='mono', aspect=vb[2] / vb[3], recreation=True)


for fn in (mercedes, bmw, porsche, ford, samsung, apple, xiaomi):
    fn()

# ---- textures (RGBA, long side 4096 for wordmarks / 2048 for emblems) + preview sheet
prev = []
for key, m in manifest.items():
    if m['kind'] == 'plaque':
        prev.append((key, m['png']))
        continue
    long_side = 4096 if m['aspect'] > 2.5 else 2048
    png = os.path.join(TEX, f'{key}_{long_side}.png')
    raster(m['svg'], png, long_side)
    m['png'] = png
    prev.append((key, png))
for m in manifest.values():
    for k in ('svg', 'png'):
        m[k] = os.path.relpath(m[k], ROOT)
json.dump(manifest, open(os.path.join(FINAL, 'logo_manifest.json'), 'w'), indent=1)

W, Hc = 2400, 260 * ((len(prev) + 2) // 3)
sheet = Image.new('RGB', (W, Hc), (58, 60, 64))
for i, (key, png) in enumerate(prev):
    im = Image.open(png).convert('RGBA')
    im.thumbnail((740, 220), Image.LANCZOS)
    cx, cy = (i % 3) * 800 + 400, (i // 3) * 260 + 130
    bg = Image.new('RGBA', (760, 240), (128, 130, 134, 255) if 'apple' in key or 'mercedes' in key or 'xiaomi_word' in key or 'porsche_word' in key else (236, 236, 236, 255))
    bg.alpha_composite(im, ((760 - im.width) // 2, (240 - im.height) // 2))
    sheet.paste(bg.convert('RGB'), (cx - 380, cy - 120))
sheet.save(os.path.join(TEX, 'logo_library_preview.jpg'), quality=90)
print(json.dumps(manifest, indent=1))
