"""ASSET 03 - ZOOM convenience store (standalone, E11 roadside commercial cluster).

Plot: 42 m (X) x 34 m (Y). Road side faces -Y. Origin = plot centre, z = 0 finished ground.
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roadside_lib as R
from roadside_lib import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_ring_prism, bm_hquad, bm_quad, bm_vquad,
                          bm_text, rounded_rect, place, front_back, bm_prism_local)
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, '..', 'zoom'))

PLOT = (-21.0, -17.0, 21.0, 17.0)
BX0, BY0, BX1, BY1 = -12.0, 1.0, 12.0, 12.0
H = 6.4
FLOOR = 0.15
GX0, GX1 = -8.5, 8.5                      # storefront glazing
CAN = (-12.5, -3.0, 12.5, BY0)             # entrance canopy footprint
Z_CAN0, Z_CAN1 = 3.8, 4.25

R.MATERIAL_DEFS.update({
    'ZOOM_Red': dict(base='#d71920', rough=0.3, spec=0.6),
    'ZOOM_RedLit': dict(base='#cf1820', rough=0.3, spec=0.6, emit='#e0141c', es=0.3),
    'ZOOM_SignWhite': dict(base='#ffffff', rough=0.3, emit='#ffffff', es=3.5),
    'ZOOM_CladWhite': dict(base='#f0f0ee', rough=0.28, metal=0.1),
    'ZOOM_Services': dict(base='#ffffff', tex='zoom_services', emit_tex=True, es=1.0, rough=0.3),
    'ZOOM_AdScreen': dict(base='#ffffff', tex='zoom_ad', emit_tex=True, es=1.8, rough=0.15),
    'ZOOM_Cylinder': dict(base='#c8161d', rough=0.35, metal=0.2),
})


def tex_zoom_services(d):
    W, Hh = 512, 1024
    img = Image.new('RGB', (W, Hh), '#d71920')
    dr = ImageDraw.Draw(img)
    fh = ImageFont.truetype(R.FONT_BOLD, 64)
    fa = ImageFont.truetype(R.FONT_ARABIC, 60)
    dr.text((36, 70), 'services', font=fh, fill='white', anchor='lm')
    dr.text((W - 36, 70), R.arabic('خدمات'), font=fa, fill='white', anchor='rm')
    dr.line([(36, 130), (W - 36, 130)], fill='white', width=4)
    rng = random.Random(4)
    for j in range(5):
        for i in range(3):
            x0, y0 = 50 + i * 145, 170 + j * 165
            dr.rounded_rectangle([x0, y0, x0 + 120, y0 + 120], 22, fill='white')
            c = rng.choice(['#d71920', '#1f3d7a', '#2a9d8f', '#f4a261'])
            k = (i + j) % 4
            if k == 0:
                dr.ellipse([x0 + 30, y0 + 30, x0 + 90, y0 + 90], outline=c, width=10)
            elif k == 1:
                dr.rectangle([x0 + 32, y0 + 26, x0 + 88, y0 + 94], outline=c, width=10)
            elif k == 2:
                dr.polygon([(x0 + 60, y0 + 24), (x0 + 96, y0 + 94), (x0 + 24, y0 + 94)], outline=c, width=10)
            else:
                dr.line([(x0 + 28, y0 + 60), (x0 + 92, y0 + 60)], fill=c, width=12)
                dr.line([(x0 + 60, y0 + 28), (x0 + 60, y0 + 92)], fill=c, width=12)
    img.save(f'{d}/zoom_services_albedo.png', optimize=True)


def tex_zoom_ad(d):
    W, Hh = 512, 640
    img = Image.new('RGB', (W, Hh), '#111433')
    dr = ImageDraw.Draw(img)
    for y in range(Hh):
        t = y / Hh
        dr.line([(0, y), (W, y)], fill=(int(20 + 30 * t), int(18 + 10 * t), int(60 + 50 * t)))
    cx, cy = W / 2, Hh * 0.42
    for k, col in enumerate(('#7b5cff', '#2ec5ff', '#ff4fa3')):
        o = 26 * k
        dr.rounded_rectangle([cx - 120 + o, cy - 120 + o, cx + 60 + o, cy + 60 + o], 26, outline=col, width=16)
    f = ImageFont.truetype(R.FONT_BLACK, 52)
    f2 = ImageFont.truetype(R.FONT_SEMI, 30)
    dr.text((cx, Hh * 0.78), 'IMAGINE YOUR', font=f, fill='white', anchor='mm')
    dr.text((cx, Hh * 0.87), 'AD HERE', font=f, fill='white', anchor='mm')
    dr.text((cx, Hh * 0.95), 'roadside screens', font=f2, fill='#b9c2ff', anchor='mm')
    img.save(f'{d}/zoom_ad_albedo.png', optimize=True)


R.EXTRA_TEXTURES['zoom_services'] = tex_zoom_services
R.EXTRA_TEXTURES['zoom_ad'] = tex_zoom_ad


def sign_text(acc, L, body, M, size, depth, font=R.FONT_BLACK, front='ZOOM_SignWhite', side='RS_PaintWhite', spacing=1.0):
    res = {0: 3, 1: 2, 2: 1}[L]
    bevel = 0.006 if (L == 0 and size >= 0.5) else 0.0
    acc.add(bm_text(body, font, size, depth if L < 2 else 0.0, bevel, res, spacing=spacing), front, matrix=M,
            mat_fn=front_back(front, side))


def swoosh_pts(x0, x1, zb, zt, seg):
    """Front-elevation outline of the red ZOOM fascia band with the sweeping right-hand tail."""
    pts = [(x0, zb), (x1 - 7.0, zb)]
    for i in range(1, seg + 1):
        t = i / seg
        s = t * t * (3 - 2 * t)
        pts.append((x1 - 7.0 + 6.6 * t, zb + (zt - zb - 0.06) * s))
    pts.append((x1, zt))
    pts.append((x0, zt))
    return pts


# ------------------------------------------------------------------ ground
def build_ground(A, L):
    g = A.m(L, 'Ground')
    beds = [(-21.0, -17.0, -19.0, -15.0), (-13.0, -17.0, 13.0, -15.0), (19.0, -17.0, 21.0, -15.0),
            (-21.0, -15.0, -19.0, 17.0), (19.0, -15.0, 21.0, 17.0), (-19.0, 14.5, 19.0, 17.0)]
    walk = (-12.8, -3.3, 12.8, BY0)
    asphalt = [PLOT]
    for h in beds + [walk, (BX0, BY0, BX1, BY1)]:
        asphalt = R.rect_subtract(asphalt, h)
    R.ground_regions(g, asphalt, 'RS_Asphalt')
    R.pad_skirt(g, *PLOT)
    g.add(bm_box(*walk[:2], 0.0, *walk[2:], FLOOR, bevel=0.02 if L == 0 else 0, open_bottom=True), 'RS_Paver')
    for b in beds:
        R.curb_bed(g, L, *b)
    land = A.m(L, 'Landscape')
    rng = random.Random(9)
    for i, (x, y) in enumerate(((-20.0, -16.0), (20.0, -16.0), (-20.0, 8.0), (20.0, 8.0), (-14.0, 15.75), (14.0, 15.75))):
        R.palm(land, L, x, y, rng.uniform(6.2, 7.6), seed=70 + i)
    for i in range(24):
        x = -12.0 + i * 1.04
        if abs(x + 9.0) < 1.4:
            continue
        if i % 3 == 0:
            R.grass_clump(land, L, x, -16.0, 0.75, seed=i)
        else:
            R.shrub(land, L, x, -16.0 + rng.uniform(-0.3, 0.3), 0.8, seed=i, mat='RS_Foliage2' if i % 2 else 'RS_Foliage')
    for side in (-1, 1):
        for i in range(9):
            R.shrub(land, L, side * 20.0, -12.0 + i * 3.2, 0.85, seed=40 + i + side * 20)
    for i in range(12):
        R.shrub(land, L, -16.5 + i * 3.0, 15.75, 0.8, seed=120 + i, mat='RS_Foliage2')
    if L < 2:
        mk = A.m(L, 'Markings')
        R.parking_bays(mk, -11.7, -8.4, -3.4, 9)
        R.arrow_mark(mk, -16.0, -12.5, 90, 3.6)
        R.arrow_mark(mk, 16.0, -12.5, -90, 3.6)
        R.arrow_mark(mk, -5.0, -11.8, 0, 3.6)
        R.arrow_mark(mk, 5.0, -11.8, 0, 3.6)
        # accessible bay hatch
        for i in range(5):
            x = 9.15 + i * 0.42
            mk.add(bm_quad((x, -8.3, 0.006), (x + 0.18, -8.3, 0.006), (x + 0.18 + 0.6, -3.5, 0.006), (x + 0.6, -3.5, 0.006)),
                   'RS_LineWhite')
        if L == 0:
            for i in range(9):
                x = -10.4 + i * 2.6
                mk.add(bm_box(x - 0.8, -4.1, 0, x + 0.8, -3.92, 0.12, bevel=0.02, open_bottom=True), 'RS_Concrete')


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bev = 0.03 if L == 0 else 0.0
    C = 'ZOOM_CladWhite'
    b.add(bm_box(BX0, BY0, 0.0, BX1, BY1, FLOOR, open_bottom=True), 'RS_Concrete')
    b.add(bm_box(BX0, BY1 - 0.25, FLOOR, BX1, BY1, H, bevel=bev, open_bottom=True), C)
    b.add(bm_box(BX0, BY0 + 0.25, FLOOR, BX0 + 0.25, BY1 - 0.25, H, open_bottom=True), C)
    b.add(bm_box(BX1 - 0.25, BY0 + 0.25, FLOOR, BX1, BY1 - 0.25, H, open_bottom=True), C)
    b.add(bm_box(BX0, BY0, FLOOR, GX0, BY0 + 0.25, 3.6, bevel=bev, open_bottom=True), C)
    b.add(bm_box(GX1, BY0, FLOOR, BX1, BY0 + 0.25, 3.6, bevel=bev, open_bottom=True), C)
    b.add(bm_box(BX0, BY0, 3.6, BX1, BY0 + 0.25, H, bevel=bev), C)
    if L < 2:
        b.add(bm_ring_prism([(BX0, BY0), (BX1, BY0), (BX1, BY1), (BX0, BY1)],
                            [(BX0 + 0.25, BY0 + 0.25), (BX1 - 0.25, BY0 + 0.25), (BX1 - 0.25, BY1 - 0.25), (BX0 + 0.25, BY1 - 0.25)],
                            H, H + 0.06, bottom=False), 'RS_MetalBrushed')
        b.add(bm_hquad(BX0 + 0.25, BY0 + 0.25, BX1 - 0.25, BY1 - 0.25, H - 0.4), 'RS_PaintOffWhite')
        for x in (-6.0, 1.0, 7.0):
            b.add(bm_box(x - 1.0, 6.5, H - 0.4, x + 1.0, 8.5, H + 0.6, bevel=bev, open_bottom=True), 'RS_MetalGalv')
    else:
        b.add(bm_hquad(BX0, BY0, BX1, BY1, H), 'RS_PaintOffWhite')
    # red swoosh fascia band (real extruded geometry) + white/red piping above
    fy = BY0
    seg = {0: 16, 1: 8, 2: 4}[L]
    M = place('-Y', (0.0, fy, 0.0))
    b.add(bm_prism_local(swoosh_pts(BX0 - 0.02, BX1 + 0.02, 4.85, 5.95, seg), 0.08), 'ZOOM_RedLit', matrix=M,
          mat_fn=front_back('ZOOM_RedLit', 'ZOOM_Red'))
    b.add(bm_box(BX0 - 0.02, fy - 0.06, 6.05, BX1 + 0.02, fy, 6.13), 'ZOOM_Red')
    # band returns on the side elevations
    for sx, facing in ((BX0, '-X'), (BX1, '+X')):
        x0, x1 = (sx - 0.08, sx) if facing == '-X' else (sx, sx + 0.08)
        b.add(bm_box(x0, BY0, 4.85, x1, BY0 + 3.0, 5.95), 'ZOOM_RedLit')
    s = A.m(L, 'Signage')
    sign_text(s, L, 'ZOOM', place('-Y', (-4.2, fy - 0.08, 5.37)), 1.15, 0.07)
    sign_text(s, L, R.arabic('زووم'), place('-Y', (1.2, fy - 0.08, 5.33)), 1.05, 0.07, font=R.FONT_ARABIC)
    for sx, facing in ((BX0 - 0.08, '-X'), (BX1 + 0.08, '+X')):
        sign_text(s, L, 'ZOOM', place(facing, (sx, BY0 + 1.5, 5.37)), 0.62, 0.05)
    # services panel (left) and digital ad screen (right)
    s.add(bm_box(-1.5, -1.6, 0.0, 1.5, 1.6, 0.03), 'ZOOM_Services', matrix=place('-Y', ((BX0 + GX0) / 2 - 0.05, fy, 1.95)),
          uv='fit', mat_fn=front_back('ZOOM_Services', 'RS_MetalDark'))
    s.add(bm_box(-1.45, -1.15, 0.0, 1.45, 1.15, 0.12, bevel=0.01 if L == 0 else 0), 'ZOOM_AdScreen',
          matrix=place('-Y', ((GX1 + BX1) / 2, fy, 2.15)), uv='fit', mat_fn=front_back('ZOOM_AdScreen', 'RS_PlasticBlack'))
    # storefront
    gl = A.m(L, 'Glass')
    gy = BY0 + 0.12
    gl.add(bm_vquad(GX0, GX1, FLOOR, 3.6, gy), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
    if L < 2:
        fr = A.m(L, 'Frames')
        n = 10
        for i in range(n + 1):
            x = GX0 + (GX1 - GX0) * i / n
            if abs(x) < 1.2 and i not in (0, n):
                continue
            fr.add(bm_box(x - 0.05, gy - 0.08, FLOOR, x + 0.05, gy + 0.06, 3.6, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(GX0, gy - 0.08, 2.9, GX1, gy + 0.06, 2.98), 'RS_MetalDark')
        fr.add(bm_box(GX0, gy - 0.08, FLOOR, GX1, gy + 0.06, FLOOR + 0.12, open_bottom=True), 'RS_MetalDark')
        for x in (-1.2, 1.2):
            fr.add(bm_box(x - 0.06, gy - 0.25, FLOOR, x + 0.06, gy, 2.9, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(-1.3, gy - 0.35, 2.6, 1.3, gy, 2.9, bevel=bev * 0.5), 'RS_MetalBrushed')
        for sgn in (-1, 1):
            fr.add(bm_box(min(0.02 * sgn, 1.15 * sgn), gy - 0.2, FLOOR, max(0.02 * sgn, 1.15 * sgn), gy - 0.16, 0.25),
                   'RS_MetalDark')
        # window promo vinyl strips (red) at low level
        for x0, x1 in ((-8.3, -2.0), (2.0, 8.3)):
            gl.add(bm_vquad(x0, x1, FLOOR + 0.15, 0.75, gy - 0.003), 'ZOOM_Red')


def build_canopy(A, L):
    c = A.m(L, 'Canopy')
    bev = 0.03 if L == 0 else 0.0
    x0, y0, x1, y1 = CAN
    c.add(bm_box(x0, y0, Z_CAN0, x1, y1, Z_CAN1, bevel=bev), 'ZOOM_CladWhite')
    c.add(bm_box(x0 - 0.02, y0 - 0.04, Z_CAN0 + 0.05, x1 + 0.02, y0, Z_CAN0 + 0.15), 'ZOOM_Red')
    for x in (-11.0, -4.0, 4.0, 11.0):
        c.add(bm_box(x - 0.14, y0 + 0.16, FLOOR, x + 0.14, y0 + 0.44, Z_CAN0, bevel=bev * 0.5, open_bottom=True, open_top=True),
              'RS_MetalBrushed')
    if L < 2:
        cl = A.m(L, 'CanopyLights')
        for i in range(10):
            x = -11.25 + i * 2.5
            for y in (-1.9, -0.2):
                cl.add(bm_cyl(x, y, Z_CAN0 - 0.01, Z_CAN0, 0.13, 12 if L == 0 else 6), 'RS_LightPanel')
        # bollards along the walkway edge
        for i in range(10):
            R.bollard(c, L, -11.7 + i * 2.6, -3.05, 1.0, 0.1)
        if L == 0:
            # gas cylinder cage + ice merchandiser + bins
            cx, cy = -10.6, -0.6
            c.add(bm_box(cx - 1.0, cy - 0.45, FLOOR, cx + 1.0, cy + 0.45, FLOOR + 0.05, open_bottom=True), 'RS_MetalGalv')
            for i in range(2):
                for j in range(5):
                    c.add(bm_cyl(cx - 0.8 + j * 0.4, cy - 0.2 + i * 0.4, FLOOR + 0.05, FLOOR + 0.8, 0.15, 12), 'ZOOM_Cylinder')
                    c.add(bm_cyl(cx - 0.8 + j * 0.4, cy - 0.2 + i * 0.4, FLOOR + 0.8, FLOOR + 0.92, 0.04, 8), 'RS_MetalBrushed')
            for px in (-1.0, 1.0):
                for py in (-0.45, 0.45):
                    c.add(bm_cyl_between((cx + px, cy + py, FLOOR), (cx + px, cy + py, FLOOR + 1.3), 0.025, 6), 'RS_MetalGalv')
            for z in (0.7, 1.3):
                for (ax, ay, bx, by) in ((-1, -0.45, 1, -0.45), (-1, 0.45, 1, 0.45), (-1, -0.45, -1, 0.45), (1, -0.45, 1, 0.45)):
                    c.add(bm_cyl_between((cx + ax, cy + ay, FLOOR + z), (cx + bx, cy + by, FLOOR + z), 0.02, 6), 'RS_MetalGalv')
            ix, iy = 10.4, -0.5
            c.add(bm_box(ix - 0.9, iy - 0.4, FLOOR, ix + 0.9, iy + 0.4, FLOOR + 1.35, bevel=0.03, open_bottom=True), 'RS_PaintWhite')
            sign_text(c, 0, 'ICE', place('-Y', (ix, iy - 0.4, FLOOR + 0.9)), 0.35, 0.01, font=R.FONT_BLACK,
                      front='RS_ScreenDark', side='RS_ScreenDark')
            for bx in (-6.5, 6.5):
                c.add(bm_cyl(bx, -0.4, FLOOR, FLOOR + 0.95, 0.24, 16), 'RS_MetalBrushed')


def build_interior(A, L):
    if L == 2:
        return
    it = A.m(L, 'Interior')
    ix0, iy0, ix1, iy1 = BX0 + 0.25, BY0 + 0.25, BX1 - 0.25, BY1 - 0.25
    zc = 3.4
    it.add(bm_hquad(ix0, iy0, ix1, iy1, FLOOR + 0.005), 'RS_InteriorFloor')
    it.add(bm_hquad(ix0, iy0, ix1, iy1, zc, down=True), 'RS_PaintWhite')
    it.add(bm_vquad(ix0, ix1, FLOOR, zc, iy1 - 0.001), 'RS_InteriorWall')
    it.add(bm_quad((ix0 + 0.001, iy1, FLOOR), (ix0 + 0.001, iy0, FLOOR), (ix0 + 0.001, iy0, zc), (ix0 + 0.001, iy1, zc)), 'RS_InteriorWall')
    it.add(bm_quad((ix1 - 0.001, iy0, FLOOR), (ix1 - 0.001, iy1, FLOOR), (ix1 - 0.001, iy1, zc), (ix1 - 0.001, iy0, zc)), 'RS_InteriorWall')
    # red brand band around the interior walls
    it.add(bm_vquad(ix0, ix1, 2.55, 2.95, iy1 - 0.004), 'ZOOM_RedLit')
    # ceiling light rows
    for i in range(5):
        x = -9.0 + i * 4.5
        it.add(bm_hquad(x - 1.6, 2.4, x + 1.6, 2.6, zc - 0.01, down=True), 'RS_LightPanel')
        it.add(bm_hquad(x - 1.6, 6.2, x + 1.6, 6.4, zc - 0.01, down=True), 'RS_LightPanel')
        it.add(bm_hquad(x - 1.6, 9.6, x + 1.6, 9.8, zc - 0.01, down=True), 'RS_LightPanel')
    # back-wall coolers
    it.add(bm_box(ix0 + 0.5, iy1 - 0.95, FLOOR, ix1 - 0.5, iy1, 2.4, open_bottom=True), 'RS_PaintCharcoal')
    it.add(bm_vquad(ix0 + 0.6, ix1 - 0.6, FLOOR + 0.25, 2.3, iy1 - 0.955), 'RS_Cooler')
    if L == 0:
        n = 22
        for k in range(n + 1):
            x = ix0 + 0.6 + k * ((ix1 - 0.6) - (ix0 + 0.6)) / n
            it.add(bm_box(x - 0.025, iy1 - 1.0, FLOOR + 0.25, x + 0.025, iy1 - 0.95, 2.3), 'RS_PaintCharcoal')
        # bottled drinks silhouettes behind the cooler glass
        rng = random.Random(12)
        for k in range(n):
            x = ix0 + 0.7 + k * ((ix1 - 0.6) - (ix0 + 0.6)) / n
            for z in (0.45, 0.95, 1.45, 1.95):
                i, j = rng.randrange(8), rng.randrange(8)
                it.add(bm_box(x, iy1 - 0.9, z, x + 0.85, iy1 - 0.6, z + 0.32, open_bottom=True), 'RS_Products', uv='fit',
                       cell=(i / 8, j / 8, (i + 1) / 8, (j + 1) / 8))
    # gondola shelving rows
    k = 0
    for y in (4.6, 7.4):
        for xa, xb in ((-10.0, -5.6), (-4.2, 0.2), (1.6, 6.0)):
            R.product_shelf(it, L, xa, y - 0.45, xb, y + 0.45, 1.65, 4, seed=50 + k)
            k += 1
    # checkout + tobacco/back counter display
    it.add(bm_box(6.8, 2.0, FLOOR, 11.2, 3.0, 1.05, bevel=0.02 if L == 0 else 0, open_bottom=True), 'ZOOM_Red')
    it.add(bm_box(6.7, 1.95, 1.05, 11.3, 3.05, 1.1), 'RS_PaintCharcoal')
    it.add(bm_box(7.2, 4.2, FLOOR, 11.3, 4.6, 2.4, open_bottom=True), 'RS_PaintCharcoal')
    it.add(bm_vquad(7.3, 11.2, 1.0, 2.3, 4.195), 'RS_Products', uv='fit')
    # hanging promo boards
    for x in (-7.8, -2.0, 3.8):
        it.add(bm_box(x - 0.9, 3.0, 2.6, x + 0.9, 3.04, 3.05), 'ZOOM_RedLit')
        if L == 0:
            it.add(bm_cyl_between((x - 0.7, 3.02, 3.05), (x - 0.7, 3.02, zc), 0.005, 4, caps=False), 'RS_PlasticBlack')
            it.add(bm_cyl_between((x + 0.7, 3.02, 3.05), (x + 0.7, 3.02, zc), 0.005, 4, caps=False), 'RS_PlasticBlack')


def build_totem(A, L):
    t = A.m(L, 'Totem')
    cx, cy = -9.0, -16.0
    bev = 0.03 if L == 0 else 0.0
    t.add(bm_box(cx - 1.1, cy - 0.45, 0.0, cx + 1.1, cy + 0.45, 0.45, bevel=bev, open_bottom=True), 'RS_Concrete')
    t.add(bm_box(cx - 0.9, cy - 0.28, 0.45, cx + 0.9, cy + 0.28, 4.4, bevel=bev), 'ZOOM_CladWhite')
    t.add(bm_box(cx - 0.9, cy - 0.28, 4.4, cx + 0.9, cy + 0.28, 6.4, bevel=bev), 'ZOOM_RedLit')
    s = A.m(L, 'Signage')
    for facing, fy in (('-Y', cy - 0.28), ('+Y', cy + 0.28)):
        sign_text(s, L, 'ZOOM', place(facing, (cx, fy, 5.65)), 0.55, 0.04)
        sign_text(s, L, R.arabic('زووم'), place(facing, (cx, fy, 4.95)), 0.5, 0.04, font=R.FONT_ARABIC)
        sign_text(s, L, '24/7', place(facing, (cx, fy, 3.6)), 0.5, 0.03, front='ZOOM_RedLit', side='ZOOM_Red')
        sign_text(s, L, 'CONVENIENCE', place(facing, (cx, fy, 2.9)), 0.2, 0.02, font=R.FONT_BOLD,
                  front='RS_PaintCharcoal', side='RS_PaintCharcoal')


def build_lamps(A, L):
    lp = A.m(L, 'LampPosts')
    for x in (-3.0, 9.0):
        R.lamp_post(lp, L, x, -16.0, 8.5, facing=(0, 1), arm=1.3)
    for x in (-20.0, 20.0):
        R.lamp_post(lp, L, x, -6.0, 8.5, facing=(-math.copysign(1, x), 0), arm=1.3)


def build_collision(A):
    A.col_box('GroundPad', *PLOT[:2], -0.5, *PLOT[2:], 0.0)
    A.col_box('Building', BX0, BY0, 0.0, BX1, BY1, H)
    A.col_box('Canopy', CAN[0], CAN[1], Z_CAN0, CAN[2], CAN[3], Z_CAN1)
    for i, x in enumerate((-11.0, -4.0, 4.0, 11.0)):
        A.col_box(f'CanopyColumn{i}', x - 0.15, CAN[1] + 0.15, 0.0, x + 0.15, CAN[1] + 0.45, Z_CAN0)
    A.col_box('Walkway', -12.8, -3.3, 0.0, 12.8, BY0, FLOOR)
    A.col_box('Totem', -10.1, -16.45, 0.0, -7.9, -15.55, 6.4)
    for i, (x, y) in enumerate(((-3.0, -16.0), (9.0, -16.0), (-20.0, -6.0), (20.0, -6.0))):
        A.col_box(f'LampPost{i}', x - 0.25, y - 0.25, 0.0, x + 0.25, y + 0.25, 8.5)


def build_lights(A):
    for i, x in enumerate((-9.0, -3.0, 3.0, 9.0)):
        A.light(f'CanopySpot{i}', 'SPOT', (x, -1.0, Z_CAN0 - 0.05), 450, '#fff4e6', spot_deg=140, blend=0.8, radius=0.3)
    for i, x in enumerate((-7.0, 0.0, 7.0)):
        A.light(f'Interior{i}', 'POINT', (x, 6.0, 3.1), 380, '#fff3e4', radius=0.5)
    for i, (x, y, fx, fy) in enumerate(((-3.0, -16.0, 0, 1), (9.0, -16.0, 0, 1), (-20.0, -6.0, 1, 0), (20.0, -6.0, -1, 0))):
        A.light(f'LampPost{i}', 'SPOT', (x + fx * 1.3, y + fy * 1.3, 8.4), 1100, '#fff2df', spot_deg=125, blend=0.6, radius=0.3)


def main():
    A = R.Asset('ZOOM', 'ConvenienceStore', ASSET_DIR, 'zoom_convenience_store')
    for L in (0, 1, 2):
        build_ground(A, L)
        build_building(A, L)
        build_canopy(A, L)
        build_interior(A, L)
        build_totem(A, L)
        build_lamps(A, L)
    build_collision(A)
    build_lights(A)
    R.build_preview_env(A, PLOT)
    A.camera('day_hero', (-19.0, -37.0, 4.4), (0.5, 1.0, 3.0), 30)
    A.camera('driveby', (-50.0, -24.5, 1.25), (-2.0, 0.0, 3.0), 32)
    A.camera('closeup1', (2.5, -9.5, 1.6), (-3.0, 3.0, 2.0), 28)
    A.camera('closeup2', (8.0, -12.5, 1.7), (0.5, 1.0, 3.9), 28)
    A.camera('overview', (36.0, -44.0, 28.0), (0.0, 0.0, 1.0), 32)
    stats = A.finalize()
    blend, glb, res = A.save_and_export()
    print('STATS', json.dumps(stats))
    print('EXPORT', res, blend, glb)


if __name__ == '__main__':
    main()
