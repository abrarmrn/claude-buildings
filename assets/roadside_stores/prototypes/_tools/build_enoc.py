"""ASSET 01 - ENOC service station (Dubai / E11 roadside).

Run:  python build_enoc.py   (with Blender's bpy module available, e.g. pip install bpy==4.5.15)
Plot: 60 m (X) x 50 m (Y). Road side faces -Y. Origin = plot centre, z = 0 finished ground.
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roadside_lib as R
from roadside_lib import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_ring_prism, bm_hquad, bm_quad,
                          bm_text, bm_poly_flat, rounded_rect, place, front_back, half_disc, bm_prism_local)
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, '..', 'enoc'))

PLOT = (-30.0, -25.0, 30.0, 25.0)
CANOPY = (-15.0, -16.0, 15.0, 0.0)      # outer fascia footprint
CANOPY_R = 1.6
Z_FASCIA0, Z_FASCIA1 = 5.40, 6.90
Z_SOFFIT = 5.55
ISLANDS = [(-7.5, -11.5), (7.5, -11.5), (-7.5, -4.5), (7.5, -4.5)]
STORE = (-13.0, 13.5, 13.0, 22.5)
FLOOR = 0.15

# ------------------------------------------------------------------ brand materials
R.MATERIAL_DEFS.update({
    'ENOC_Green': dict(base='#00984a', rough=0.28, spec=0.6),
    'ENOC_Red': dict(base='#e1251b', rough=0.28, spec=0.6),
    # backlit lightbox versions used on the canopy fascia and the totem head
    'ENOC_GreenLit': dict(base='#00984a', rough=0.3, spec=0.6, emit='#00a651', es=0.45),
    'ENOC_RedLit': dict(base='#e1251b', rough=0.3, spec=0.6, emit='#ff3020', es=0.45),
    'ENOC_Charcoal': dict(base='#3a3e43', rough=0.32, metal=0.25),
    'ENOC_SignWhite': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=3.5),
    'ENOC_LogoGreen': dict(base='#00984a', rough=0.3, emit='#00a651', es=2.2),
    'ENOC_LogoRed': dict(base='#e1251b', rough=0.3, emit='#ff2a1f', es=2.2),
    'ENOC_PriceScreen': dict(base='#ffffff', tex='enoc_price', emit_tex=True, es=1.6, rough=0.18),
    'ZOOM_Red': dict(base='#d71920', rough=0.3, emit='#d71920', es=0.6),
    'ZOOM_SignWhite': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=3.5),
})


def tex_enoc_price(d):
    W, H = 512, 1024
    img = Image.new('RGB', (W, H), '#0a3a8c')
    dr = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        dr.line([(0, y), (W, y)], fill=(int(10 + 6 * t), int(58 - 18 * t), int(150 - 40 * t)))
    dr.rectangle([0, 0, W, 170], fill='#00984a')
    dr.rectangle([0, 150, W, 170], fill='#e1251b')
    f_logo = ImageFont.truetype(R.FONT_BOLD, 110)
    f_lab = ImageFont.truetype(R.FONT_SEMI, 46)
    f_num = ImageFont.truetype(R.FONT_BLACK, 132)
    dr.text((W / 2, 78), 'enoc', font=f_logo, fill='white', anchor='mm')
    rows = [('SUPER 98', '3.08'), ('SPECIAL 95', '2.97'), ('E-PLUS 91', '2.89'), ('DIESEL', '3.12')]
    for i, (lab, num) in enumerate(rows):
        y0 = 190 + i * 208
        dr.rounded_rectangle([18, y0, W - 18, y0 + 192], 18, fill='#06265f')
        dr.text((40, y0 + 34), lab, font=f_lab, fill='#cfe3ff', anchor='lm')
        dr.text((W - 40, y0 + 122), num, font=f_num, fill='#fff3b0', anchor='rm')
    img.save(f'{d}/enoc_price_albedo.png', optimize=True)


R.EXTRA_TEXTURES['enoc_price'] = tex_enoc_price


# ------------------------------------------------------------------ helpers
def enoc_logo(acc, L, M, r=0.55, depth=0.08):
    """ENOC-style roundel: green left half / red right half, built in face-local coords."""
    seg = {0: 20, 1: 12, 2: 8}[L]
    gap = 0.06 * r
    acc.add(bm_prism_local(half_disc(r, gap, -1, seg), depth), 'ENOC_LogoGreen', matrix=M,
            mat_fn=front_back('ENOC_LogoGreen', 'RS_PaintWhite'))
    acc.add(bm_prism_local(half_disc(r, gap, 1, seg), depth), 'ENOC_LogoRed', matrix=M,
            mat_fn=front_back('ENOC_LogoRed', 'RS_PaintWhite'))
    if L < 2:
        # white backing ring behind the roundel
        ring_o = [(math.cos(a) * r * 1.12, math.sin(a) * r * 1.12) for a in
                  [i / (seg * 2) * math.tau for i in range(seg * 2)]]
        acc.add(bm_prism_local(ring_o, depth * 0.5), 'RS_PaintWhite', matrix=M)


def sign_text(acc, L, body, M, size, depth, font=R.FONT_BOLD, front='ENOC_SignWhite', side='RS_PaintWhite',
              align='CENTER', spacing=1.0):
    res = {0: 3, 1: 2, 2: 1}[L]
    bevel = 0.006 if (L == 0 and size >= 0.5) else 0.0
    bm = bm_text(body, font, size, depth if L < 2 else 0.0, bevel, res, align=align,
                 spacing=spacing)
    acc.add(bm, front, matrix=M, mat_fn=front_back(front, side))


# ------------------------------------------------------------------ ground & landscaping
def build_ground(A, L):
    g = A.m(L, 'Ground')
    x0, y0, x1, y1 = PLOT
    paver = (-17.0, -18.5, 17.0, 2.0)
    sidewalk = (-14.5, 11.5, 14.5, 22.5)
    beds = [(-19.0, -25.0, 19.0, -22.5), (-30.0, -25.0, -27.0, -22.5), (27.0, -25.0, 30.0, -22.5),
            (-30.0, -22.5, -28.0, 25.0), (28.0, -22.5, 30.0, 25.0), (-28.0, 23.0, 28.0, 25.0)]
    asphalt = [PLOT]
    for h in [paver, sidewalk] + beds:
        asphalt = R.rect_subtract(asphalt, h)
    R.ground_regions(g, asphalt, 'RS_Asphalt')
    R.ground_regions(g, [paver], 'RS_Paver')
    R.pad_skirt(g, *PLOT)
    # raised sidewalk around the store
    if L < 2:
        sx0, sy0, sx1, sy1 = sidewalk
        g.add(bm_box(sx0, sy0, 0, sx1, STORE[1], FLOOR, bevel=0.02 if L == 0 else 0, open_bottom=True), 'RS_Concrete')
        g.add(bm_box(sx0, STORE[1], 0, STORE[0], sy1, FLOOR, open_bottom=True), 'RS_Concrete')
        g.add(bm_box(STORE[2], STORE[1], 0, sx1, sy1, FLOOR, open_bottom=True), 'RS_Concrete')
    else:
        g.add(bm_box(*sidewalk[:2], 0, *sidewalk[2:], FLOOR, open_bottom=True), 'RS_Concrete')
    for b in beds:
        R.curb_bed(g, L, *b)
    land = A.m(L, 'Landscape')
    rng = random.Random(7)
    # front bed: palms + shrubs + grasses
    for i, x in enumerate([-28.5, 18.0, 28.5]):
        R.palm(land, L, x, -23.75, rng.uniform(6.5, 7.5), seed=10 + i)
    for i in range(30):
        x = -18.0 + i * 1.24
        if abs(x + 15.5) < 1.7:
            continue
        if L == 0 or i % 2 == 0:
            if i % 3 == 0:
                R.grass_clump(land, L, x, -23.2 - (i % 2) * 0.9, 0.8, seed=i)
            else:
                R.shrub(land, L, x, -23.75 + rng.uniform(-0.4, 0.4), rng.uniform(0.7, 1.0), seed=i,
                        mat='RS_Foliage' if i % 2 else 'RS_Foliage2')
    for side in (-1, 1):
        for i in range(12):
            y = -20.0 + i * 3.8
            R.shrub(land, L, side * 29.0, y, 0.9, seed=100 + i + side * 50)
        R.palm(land, L, side * 29.0, 19.0, 7.0, seed=40 + side)
    for i in range(14):
        R.shrub(land, L, -26.0 + i * 4.0, 24.0, 0.8, seed=200 + i, mat='RS_Foliage2')
    # markings
    if L < 2:
        mk = A.m(L, 'Markings')
        R.parking_bays(mk, -13.0, 6.6, 11.4, 4)
        R.parking_bays(mk, 2.6, 6.6, 11.4, 4)
        for i in range(6):
            x = -2.2 + i * 0.85
            mk.add(bm_hquad(x, 2.6, x + 0.45, 11.3, 0.006), 'RS_LineWhite')
        R.arrow_mark(mk, -23.0, -19.5, 90, 4.0)
        R.arrow_mark(mk, 23.0, -16.0, -90, 4.0)
        for y in (-14.6, -8.0, -1.3):
            R.arrow_mark(mk, -12.5, y, 0, 3.0)
            R.arrow_mark(mk, 12.5, y, 0, 3.0)
        R.arrow_mark(mk, 20.0, 4.5, 0, 4.0)
        # lane edge line along the forecourt
        mk.add(bm_hquad(-17.0, 2.0, 17.0, 2.12, 0.006), 'RS_LineYellow')
        if L == 0:
            for i in range(8):
                x = -11.7 + i * 2.6 + (2.6 if i >= 4 else 0)
                mk.add(bm_box(x - 0.8, 7.0, 0, x + 0.8, 7.18, 0.12, bevel=0.02, open_bottom=True), 'RS_Concrete')


# ------------------------------------------------------------------ canopy
def build_canopy(A, L):
    c = A.m(L, 'Canopy')
    x0, y0, x1, y1 = CANOPY
    cseg = {0: 8, 1: 4, 2: 2}[L]
    outer = rounded_rect(x0, y0, x1, y1, CANOPY_R, cseg)
    inner = rounded_rect(x0 + 0.25, y0 + 0.25, x1 - 0.25, y1 - 0.25, CANOPY_R - 0.25, cseg)
    # banded fascia: green body, red band, white cap
    c.add(bm_ring_prism(outer, inner, Z_FASCIA0, 6.30, top=False, bottom=True), 'ENOC_GreenLit')
    c.add(bm_ring_prism(outer, inner, 6.30, 6.72, top=False, bottom=False), 'ENOC_RedLit')
    c.add(bm_ring_prism(outer, inner, 6.72, Z_FASCIA1, top=True, bottom=False), 'RS_PaintWhite')
    # soffit (underside) and roof deck
    c.add(bm_poly_flat(inner, Z_SOFFIT, down=True), 'RS_PaintWhite', tile=2.0)
    c.add(bm_poly_flat(inner, 6.70), 'RS_PaintOffWhite')
    if L == 0:
        # thin shadow-gap reveal line between fascia and soffit
        c.add(bm_ring_prism(rounded_rect(x0 + 0.25, y0 + 0.25, x1 - 0.25, y1 - 0.25, CANOPY_R - 0.25, cseg),
                            rounded_rect(x0 + 0.33, y0 + 0.33, x1 - 0.33, y1 - 0.33, CANOPY_R - 0.33, cseg),
                            Z_SOFFIT - 0.06, Z_SOFFIT, top=False, bottom=True), 'RS_PaintCharcoal')
    # front brand panel (charcoal) with logo + wordmark, and on the back face
    s = A.m(L, 'Signage')
    for facing, yy in (('-Y', y0 - 0.05), ('+Y', y1 + 0.05)):
        sgn = -1 if facing == '-Y' else 1
        s.add(bm_box(-7.0, min(yy, yy - sgn * 0.05), Z_FASCIA0 + 0.06, 7.0, max(yy, yy - sgn * 0.05),
                     Z_FASCIA1 - 0.06, bevel=0.02 if L == 0 else 0), 'ENOC_Charcoal')
        face = yy
        enoc_logo(s, L, place(facing, (3.6 * sgn, face, 6.15)), r=0.55)
        sign_text(s, L, 'enoc', place(facing, (-1.0 * sgn, face, 5.82)), 1.25, 0.07)
        # red underline stripe accent
        if L < 2:
            s.add(bm_box(-6.6, min(face, face + sgn * 0.02), 5.52, 6.6, max(face, face + sgn * 0.02), 5.58),
                  'ENOC_Red')
    # side faces: logo + arabic name
    for facing, xx in (('-X', x0), ('+X', x1)):
        sgn = -1 if facing == '-X' else 1
        enoc_logo(s, L, place(facing, (xx, -10.5 if sgn < 0 else -5.5, 6.15)), r=0.5)
        sign_text(s, L, R.arabic('إينوك'), place(facing, (xx, -7.6 if sgn < 0 else -8.4, 5.78)), 1.0, 0.06,
                  font=R.FONT_ARABIC)
    # LED ceiling panels
    if L < 2:
        cl = A.m(L, 'CanopyLights')
        for ix in range(6):
            for iy in range(3):
                cx = -12.5 + ix * 5.0
                cy = -14.2 + iy * 6.2
                if L == 0:
                    cl.add(bm_box(cx - 0.65, cy - 0.35, Z_SOFFIT - 0.05, cx + 0.65, cy + 0.35, Z_SOFFIT,
                                  open_top=True), 'RS_MetalBrushed')
                    cl.add(bm_hquad(cx - 0.6, cy - 0.3, cx + 0.6, cy + 0.3, Z_SOFFIT - 0.052, down=True),
                           'RS_LightPanel')
                else:
                    cl.add(bm_hquad(cx - 0.6, cy - 0.3, cx + 0.6, cy + 0.3, Z_SOFFIT - 0.01, down=True),
                           'RS_LightPanel')
    # columns with price screens
    col = A.m(L, 'Columns')
    for (cx, cy) in ISLANDS:
        col.add(bm_box(cx - 0.35, cy - 0.35, 0.2, cx + 0.35, cy + 0.35, Z_SOFFIT, bevel=0.04 if L == 0 else 0,
                       open_bottom=True, open_top=True), 'RS_PaintWhite')
        if L == 0:
            col.add(bm_box(cx - 0.4, cy - 0.4, 0.2, cx + 0.4, cy + 0.4, 0.75, bevel=0.03, open_bottom=True),
                    'RS_MetalBrushed')
            col.add(bm_box(cx - 0.37, cy - 0.37, Z_SOFFIT - 0.35, cx + 0.37, cy + 0.37, Z_SOFFIT, open_top=True),
                    'ENOC_Green')
        if L < 2:
            for facing, (ox, oy) in (('-Y', (0, -0.36)), ('+Y', (0, 0.36)), ('-X', (-0.36, 0))):
                M = place(facing, (cx + ox, cy + oy, 2.15))
                bm = bm_box(-0.28, -0.5, 0.0, 0.28, 0.5, 0.025)
                col.add(bm, 'ENOC_PriceScreen', matrix=M, uv='fit',
                        mat_fn=front_back('ENOC_PriceScreen', 'RS_PlasticBlack'))


# ------------------------------------------------------------------ islands and dispensers
def dispenser(acc, L, cx, cy):
    z0 = 0.2
    if L == 2:
        acc.add(bm_box(cx - 0.55, cy - 0.3, z0, cx + 0.55, cy + 0.3, 2.0, open_bottom=True), 'RS_PaintWhite')
        acc.add(bm_box(cx - 0.6, cy - 0.33, 2.0, cx + 0.6, cy + 0.33, 2.55), 'ENOC_Green')
        return
    bev = 0.03 if L == 0 else 0.0
    acc.add(bm_box(cx - 0.6, cy - 0.32, z0, cx + 0.6, cy + 0.32, z0 + 0.22, bevel=bev, open_bottom=True),
            'RS_MetalBrushed')
    body = rounded_rect(cx - 0.55, cy - 0.28, cx + 0.55, cy + 0.28, 0.06 if L == 0 else 0.0, 3 if L == 0 else 1)
    acc.add(bm_prism(body, z0 + 0.22, 2.0, bottom=False), 'RS_PaintWhite')
    # side columns in brushed steel
    for sx in (-1, 1):
        acc.add(bm_box(cx + sx * 0.55 - (0.06 if sx > 0 else 0), cy - 0.3, z0 + 0.22, cx + sx * 0.55 + (0.06 if sx < 0 else 0),
                       cy + 0.3, 2.0, bevel=bev * 0.5, open_bottom=True), 'RS_MetalBrushed')
    # header with brand bands
    acc.add(bm_box(cx - 0.62, cy - 0.33, 2.0, cx + 0.62, cy + 0.33, 2.30, bevel=bev, open_bottom=True), 'ENOC_Green')
    acc.add(bm_box(cx - 0.62, cy - 0.33, 2.30, cx + 0.62, cy + 0.33, 2.44, open_bottom=True, open_top=True), 'ENOC_Red')
    acc.add(bm_box(cx - 0.62, cy - 0.33, 2.44, cx + 0.62, cy + 0.33, 2.52, bevel=bev * 0.5, open_bottom=True),
            'RS_PaintWhite')
    for sgn in (-1, 1):
        fy = cy + sgn * 0.28
        facing = '-Y' if sgn < 0 else '+Y'
        # display + keypad
        acc.add(bm_box(-0.38, -0.2, 0.0, 0.38, 0.2, 0.02), 'RS_ScreenDark',
                matrix=place(facing, (cx, fy, 1.65)), mat_fn=front_back('RS_ScreenDark', 'RS_PlasticBlack'))
        acc.add(bm_box(-0.42, -0.24, 0.0, 0.42, 0.24, 0.012), 'RS_PlasticBlack', matrix=place(facing, (cx, fy, 1.65)))
        if L == 0:
            acc.add(bm_box(-0.12, -0.12, 0.0, 0.12, 0.12, 0.04, bevel=0.01), 'RS_PlasticBlack',
                    matrix=place(facing, (cx + 0.3, fy, 1.25)))
            sign_text(acc, L, 'enoc', place(facing, (cx, cy + sgn * 0.33, 2.15)), 0.2, 0.01)
        # nozzles: holster + coloured handle (+ hose on LOD0)
        for k, (nx, hm) in enumerate(((-0.33, 'ENOC_Green'), (-0.05, 'ENOC_Red'), (0.23, 'RS_PlasticBlack'))):
            M = place(facing, (cx + nx * (-sgn), fy, 1.12))
            acc.add(bm_box(-0.07, -0.1, 0.0, 0.07, 0.1, 0.08, bevel=bev * 0.3), 'RS_PlasticBlack', matrix=M)
            acc.add(bm_box(-0.035, -0.12, 0.06, 0.035, 0.08, 0.14, bevel=bev * 0.3), hm, matrix=M)
            if L == 0:
                acc.add(bm_cyl_between((0, 0.05, 0.12), (0, -0.05, 0.27), 0.012, 6), 'RS_MetalBrushed', matrix=M)
                # hose: sagging loop from header to handle
                pts = []
                for i in range(9):
                    t = i / 8
                    pts.append((0.0, 0.8 * (1 - t) - 0.35 * math.sin(math.pi * t), 0.05 + 0.45 * math.sin(math.pi * t)))
                for i in range(8):
                    acc.add(bm_cyl_between(pts[i], pts[i + 1], 0.018, 6, caps=False), 'RS_Rubber', matrix=M)


def build_islands(A, L):
    isl = A.m(L, 'PumpIslands')
    for (cx, cy) in ISLANDS:
        rr = rounded_rect(cx - 3.4, cy - 0.7, cx + 3.4, cy + 0.7, 0.6 if L < 2 else 0.0, 4 if L == 0 else 2)
        isl.add(bm_prism(rr, 0.0, 0.2, bottom=False), 'RS_Concrete')
        if L == 0:
            isl.add(bm_ring_prism(rr, rounded_rect(cx - 3.3, cy - 0.6, cx + 3.3, cy + 0.6, 0.5, 4), 0.2, 0.23,
                                  bottom=False), 'RS_MetalBrushed')
        for dx in (-2.0, 2.0):
            dispenser(isl, L, cx + dx, cy)
        if L < 2:
            # crash protection hoops at both island ends
            for ex in (-3.1, 3.1):
                for oy in (-0.38, 0.38):
                    isl.add(bm_cyl(cx + ex, cy + oy, 0.2, 1.0, 0.06, 12 if L == 0 else 6, open_bottom=True), 'RS_ReflectorYellow')
                isl.add(bm_cyl_between((cx + ex, cy - 0.38, 1.0), (cx + ex, cy + 0.38, 1.0), 0.06,
                                       12 if L == 0 else 6), 'RS_ReflectorYellow')
            if L == 0:
                # bin + paper towel / water station next to the column
                isl.add(bm_cyl(cx + 0.8, cy, 0.2, 1.0, 0.22, 16, open_bottom=True), 'RS_MetalBrushed')
                isl.add(bm_box(cx - 1.0, cy - 0.2, 0.2, cx - 0.6, cy + 0.2, 1.1, bevel=0.02, open_bottom=True), 'ENOC_Green')


# ------------------------------------------------------------------ store (ZOOM shop)
def build_store(A, L):
    st = A.m(L, 'Store')
    sx0, sy0, sx1, sy1 = STORE
    H = 5.2
    bev = 0.03 if L == 0 else 0.0
    wall = 'RS_PaintWhite'
    # shell
    st.add(bm_box(sx0, sy1 - 0.25, FLOOR, sx1, sy1, H, open_bottom=True), wall)
    st.add(bm_box(sx0, sy0 + 0.25, FLOOR, sx0 + 0.25, sy1 - 0.25, H, open_bottom=True), wall)
    st.add(bm_box(sx1 - 0.25, sy0 + 0.25, FLOOR, sx1, sy1 - 0.25, H, open_bottom=True), wall)
    st.add(bm_box(sx0, sy0, FLOOR, sx0 + 2.0, sy0 + 0.25, 3.4, bevel=bev, open_bottom=True), wall)
    st.add(bm_box(sx1 - 2.0, sy0, FLOOR, sx1, sy0 + 0.25, 3.4, bevel=bev, open_bottom=True), wall)
    st.add(bm_box(sx0, sy0, 3.4, sx1, sy0 + 0.25, H, bevel=bev), wall)
    st.add(bm_hquad(sx0 + 0.25, sy0 + 0.25, sx1 - 0.25, sy1 - 0.25, H - 0.35), 'RS_PaintOffWhite')
    # fascia accent stripes (ENOC green + red)
    st.add(bm_box(sx0 - 0.02, sy0 - 0.04, 3.42, sx1 + 0.02, sy0, 3.56), 'ENOC_Green')
    st.add(bm_box(sx0 - 0.02, sy0 - 0.04, 3.56, sx1 + 0.02, sy0, 3.64), 'ENOC_Red')
    # entrance overhang
    st.add(bm_box(-11.5, sy0 - 1.6, 3.3, 11.5, sy0, 3.42, bevel=bev), 'RS_PaintWhite')
    gl = A.m(L, 'StoreGlass')
    gx0, gx1 = sx0 + 2.0, sx1 - 2.0
    gy = sy0 + 0.12
    if L == 2:
        gl.add(R.bm_vquad(gx0, gx1, FLOOR, 3.4, gy), 'RS_GlassLOD')
    else:
        gl.add(R.bm_vquad(gx0, gx1, FLOOR, 3.4, gy), 'RS_Glass')
        fr = A.m(L, 'StoreFrames')
        n = 10
        for i in range(n + 1):
            x = gx0 + (gx1 - gx0) * i / n
            fr.add(bm_box(x - 0.05, gy - 0.08, FLOOR, x + 0.05, gy + 0.06, 3.4, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(gx0, gy - 0.08, 2.75, gx1, gy + 0.06, 2.85), 'RS_MetalDark')
        fr.add(bm_box(gx0, gy - 0.08, FLOOR, gx1, gy + 0.06, FLOOR + 0.1, open_bottom=True), 'RS_MetalDark')
        # sliding door leaves (offset in front of the glass line)
        for sgn in (-1, 1):
            fr.add(bm_box(min(0.05 * sgn, 1.3 * sgn), gy - 0.22, FLOOR, max(0.05 * sgn, 1.3 * sgn), gy - 0.18, 0.2),
                   'RS_MetalDark')
            fr.add(bm_box(min(0.05 * sgn, 1.3 * sgn), gy - 0.22, 2.6, max(0.05 * sgn, 1.3 * sgn), gy - 0.18, 2.7),
                   'RS_MetalDark')
        fr.add(bm_box(-1.5, gy - 0.3, 2.7, 1.5, gy, 2.95, bevel=bev * 0.5), 'RS_MetalBrushed')
    # ZOOM shop sign on the fascia
    s = A.m(L, 'Signage')
    fy = sy0
    s.add(bm_box(-4.6, fy - 0.22, 3.75, 4.6, fy, 4.95, bevel=0.03 if L == 0 else 0), 'ZOOM_Red')
    sign_text(s, L, 'ZOOM', place('-Y', (-1.6, fy - 0.22, 4.35)), 0.95, 0.06, font=R.FONT_BLACK,
              front='ZOOM_SignWhite')
    sign_text(s, L, R.arabic('زووم'), place('-Y', (2.5, fy - 0.22, 4.32)), 0.85, 0.06, font=R.FONT_ARABIC,
              front='ZOOM_SignWhite')
    enoc_logo(s, L, place('-Y', (-9.5, fy, 4.35)), r=0.45)
    sign_text(s, L, 'enoc', place('-Y', (-7.5, fy, 4.05)), 0.9, 0.05, front='ENOC_Green', side='ENOC_Green')
    if L < 2:
        # overhang downlights
        dl = A.m(L, 'CanopyLights')
        for i in range(8):
            x = -10.0 + i * (20.0 / 7)
            dl.add(R.bm_cyl(x, sy0 - 0.8, 3.29, 3.30, 0.12, 12 if L == 0 else 6, caps=True), 'RS_LightPanel')
        # rooftop HVAC units
        roof = A.m(L, 'Roof')
        for i, x in enumerate((-8.0, -1.0, 6.0)):
            roof.add(bm_box(x - 1.1, 18.0, H - 0.35, x + 1.1, 20.2, H + 0.75, bevel=bev, open_bottom=True),
                     'RS_MetalGalv')
            if L == 0:
                for fx in (-0.5, 0.5):
                    roof.add(bm_cyl(x + fx, 19.1, H + 0.75, H + 0.8, 0.42, 16), 'RS_PlasticBlack')
    # interior visible through the glass
    if L < 2:
        it = A.m(L, 'Interior')
        ix0, iy0, ix1, iy1 = sx0 + 0.25, sy0 + 0.25, sx1 - 0.25, sy1 - 0.25
        it.add(bm_hquad(ix0, iy0, ix1, iy1, FLOOR + 0.005), 'RS_InteriorFloor')
        it.add(bm_hquad(ix0, iy0, ix1, iy1, 3.3, down=True), 'RS_PaintWhite')
        it.add(R.bm_vquad(ix0, ix1, FLOOR, 3.3, iy1 - 0.001, facing='-Y'), 'RS_InteriorWall')
        it.add(bm_quad((ix0 + 0.001, iy1, FLOOR), (ix0 + 0.001, iy0, FLOOR), (ix0 + 0.001, iy0, 3.3), (ix0 + 0.001, iy1, 3.3)),
               'RS_InteriorWall')
        it.add(bm_quad((ix1 - 0.001, iy0, FLOOR), (ix1 - 0.001, iy1, FLOOR), (ix1 - 0.001, iy1, 3.3), (ix1 - 0.001, iy0, 3.3)),
               'RS_InteriorWall')
        # ceiling light strips
        for i in range(4):
            x = -9.0 + i * 6.0
            it.add(bm_hquad(x - 2.0, 15.0, x + 2.0, 15.25, 3.29, down=True), 'RS_LightWarm')
            it.add(bm_hquad(x - 2.0, 18.5, x + 2.0, 18.75, 3.29, down=True), 'RS_LightWarm')
        # coolers along the back wall
        it.add(bm_box(ix0 + 1.0, iy1 - 0.9, FLOOR, ix1 - 7.0, iy1, 2.3, open_bottom=True), 'RS_PaintCharcoal')
        it.add(R.bm_vquad(ix0 + 1.1, ix1 - 7.1, FLOOR + 0.25, 2.2, iy1 - 0.905), 'RS_Cooler')
        if L == 0:
            for k in range(14):
                x = ix0 + 1.1 + k * ((ix1 - 7.1) - (ix0 + 1.1)) / 14
                it.add(bm_box(x - 0.025, iy1 - 0.95, FLOOR + 0.25, x + 0.025, iy1 - 0.9, 2.2), 'RS_PaintCharcoal')
        for k, y in enumerate((16.4, 18.9)):
            for j, (xa, xb) in enumerate(((-9.5, -3.5), (-1.5, 4.5))):
                R.product_shelf(it, L, xa, y - 0.45, xb, y + 0.45, 1.7, 4, seed=k * 10 + j)
        # checkout counter
        it.add(bm_box(6.5, 15.0, FLOOR, 11.0, 16.0, 1.05, bevel=bev, open_bottom=True), 'RS_Wood')
        it.add(bm_box(6.4, 14.95, 1.05, 11.1, 16.05, 1.1), 'RS_PaintCharcoal')
        it.add(R.bm_vquad(7.0, 11.0, 1.5, 2.9, iy1 - 0.002), 'RS_ScreenDark')


def build_totem(A, L):
    t = A.m(L, 'PriceTotem')
    cx, cy = -15.5, -23.75
    bev = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.2, cy - 0.5, 0.0, cx + 1.2, cy + 0.5, 0.5, bevel=bev, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 1.0, cy - 0.3, 0.5, cx + 1.0, cy + 0.3, 2.4, bevel=bev), 'ENOC_Charcoal')
    t.add(bm_box(cx - 1.0, cy - 0.3, 2.4, cx + 1.0, cy + 0.3, 6.3, bevel=bev), 'RS_PaintCharcoal')
    t.add(bm_box(cx - 1.0, cy - 0.3, 6.3, cx + 1.0, cy + 0.3, 8.6, bevel=bev), 'ENOC_GreenLit')
    t.add(bm_box(cx - 1.02, cy - 0.32, 8.2, cx + 1.02, cy + 0.32, 8.45), 'ENOC_RedLit')
    s = A.m(L, 'Signage')
    for facing, fy in (('-Y', cy - 0.3), ('+Y', cy + 0.3)):
        enoc_logo(s, L, place(facing, (cx, fy, 7.55)), r=0.45, depth=0.05)
        sign_text(s, L, 'enoc', place(facing, (cx, fy, 6.75)), 0.62, 0.04)
        sign_text(s, L, R.arabic('إينوك'), place(facing, (cx, fy, 1.45)), 0.6, 0.04, font=R.FONT_ARABIC)
        M = place(facing, (cx, fy, 4.35))
        t.add(bm_box(-0.85, -1.75, 0.0, 0.85, 1.75, 0.03), 'ENOC_PriceScreen', matrix=M, uv='fit',
              mat_fn=front_back('ENOC_PriceScreen', 'RS_PlasticBlack'))


def build_lamps(A, L):
    lp = A.m(L, 'LampPosts')
    for (x, y, fx) in ((-29.0, -6.0, 1), (29.0, -6.0, -1), (-29.0, 8.0, 1), (29.0, 8.0, -1)):
        R.lamp_post(lp, L, x, y, 9.0, facing=(fx, 0), arm=1.4)


def build_collision(A):
    x0, y0, x1, y1 = PLOT
    A.col_box('GroundPad', x0, y0, -0.5, x1, y1, 0.0)
    A.col_box('Canopy', CANOPY[0], CANOPY[1], Z_FASCIA0, CANOPY[2], CANOPY[3], Z_FASCIA1)
    for i, (cx, cy) in enumerate(ISLANDS):
        A.col_box(f'Island{i}', cx - 3.4, cy - 0.7, 0.0, cx + 3.4, cy + 0.7, 2.55)
        A.col_box(f'Column{i}', cx - 0.4, cy - 0.4, 0.0, cx + 0.4, cy + 0.4, Z_SOFFIT)
    A.col_box('Store', STORE[0], STORE[1], 0.0, STORE[2], STORE[3], 5.2)
    A.col_box('Totem', -16.7, -24.25, 0.0, -14.3, -23.25, 8.6)
    for i, (x, y) in enumerate(((-29.0, -6.0), (29.0, -6.0), (-29.0, 8.0), (29.0, 8.0))):
        A.col_box(f'LampPost{i}', x - 0.25, y - 0.25, 0.0, x + 0.25, y + 0.25, 9.0)


def build_lights(A):
    for i, (x, y) in enumerate(((-9.0, -12.0), (0.0, -12.0), (9.0, -12.0), (-9.0, -4.0), (0.0, -4.0), (9.0, -4.0))):
        A.light(f'CanopySpot{i}', 'SPOT', (x, y, Z_SOFFIT - 0.1), 900, '#fff4e6', spot_deg=150, blend=0.8, radius=0.6)
    for i, x in enumerate((-7.0, 0.0, 7.0)):
        A.light(f'StoreInterior{i}', 'POINT', (x, 18.0, 3.0), 350, '#ffd9a8', radius=0.5)
        A.light(f'StoreFront{i}', 'SPOT', (x, STORE[1] - 0.8, 3.25), 250, '#fff0dc', spot_deg=140, blend=0.8, radius=0.2)
    for i, (x, y, fx) in enumerate(((-29.0, -6.0, 1), (29.0, -6.0, -1), (-29.0, 8.0, 1), (29.0, 8.0, -1))):
        A.light(f'LampPost{i}', 'SPOT', (x + fx * 1.4, y, 8.9), 1200, '#fff2df', spot_deg=125, blend=0.6, radius=0.3)


def main():
    A = R.Asset('ENOC', 'ServiceStation', ASSET_DIR, 'enoc_service_station')
    for L in (0, 1, 2):
        build_ground(A, L)
        build_canopy(A, L)
        build_islands(A, L)
        build_store(A, L)
        build_totem(A, L)
        build_lamps(A, L)
    build_collision(A)
    build_lights(A)
    R.build_preview_env(A, PLOT)
    A.camera('day_hero', (-22.0, -60.0, 6.5), (0.5, -5.0, 3.4), 30)
    A.camera('driveby', (-62.0, -35.5, 1.25), (-4.0, -12.0, 3.6), 32)
    A.camera('closeup1', (-14.5, -19.5, 2.1), (-6.5, -10.5, 2.0), 26)
    A.camera('closeup2', (5.0, 3.0, 1.9), (-1.0, 15.0, 2.3), 30)
    A.camera('overview', (48.0, -62.0, 38.0), (0.0, 0.0, 0.0), 32)
    stats = A.finalize()
    blend, glb, res = A.save_and_export()
    print('STATS', json.dumps(stats))
    print('EXPORT', res, blend, glb)


if __name__ == '__main__':
    main()
