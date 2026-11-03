"""ASSET 02 - Starbucks standalone drive-thru cafe (Dubai roadside commercial cluster).

Plot: 46 m (X) x 42 m (Y). Road side faces -Y. Origin = plot centre, z = 0 finished ground.
Drive-thru runs clockwise (UAE: driver sits on the left): enter east lane northbound, rear lane
westbound past the menu board, west lane southbound past the pickup window, exit to the front aisle.
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roadside_lib as R
from roadside_lib import (bm_box, bm_cyl, bm_cyl_between, bm_prism, bm_ring_prism, bm_hquad, bm_quad, bm_vquad,
                          bm_text, bm_poly_flat, rounded_rect, place, front_back, bm_prism_local, bm_sphere)
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.normpath(os.path.join(HERE, '..', 'starbucks'))

PLOT = (-23.0, -22.0, 23.0, 20.0)
BX0, BY0, BX1, BY1 = -10.0, -1.0, 10.0, 10.0      # building footprint (upper volume front at BY0)
GLASS_Y = -0.4                                      # recessed ground-floor storefront line
H_TOP = 6.8
H_GF = 3.4
FLOOR = 0.15
TERRACE = (-9.5, -9.0, 9.0, -1.0)

R.MATERIAL_DEFS.update({
    'SBX_Green': dict(base='#00704a', rough=0.35),
    'SBX_HouseGreen': dict(base='#1e3932', rough=0.4),
    'SBX_SignWhite': dict(base='#ffffff', rough=0.3, emit='#fffaf0', es=3.5),
    'SBX_Emblem': dict(base='#ffffff', tex='sbx_emblem', emit_tex=True, es=1.8, rough=0.3),
    'SBX_Menu': dict(base='#ffffff', tex='sbx_menu', emit_tex=True, es=1.6, rough=0.2),
    'SBX_Frame': dict(base='#c8bda9', rough=0.35, metal=0.6),
    'SBX_Umbrella': dict(base='#1e3932', rough=0.85, double=True),
    'SBX_Leather': dict(base='#5a3b28', rough=0.55),
})


def _catmull(pts, n=8):
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def tex_sbx_emblem(d, n=1024):
    """Simplified flat green siren roundel (stylised graphic for the prototype)."""
    G, W = '#00704a', '#ffffff'
    S = n * 2
    img = Image.new('RGB', (S, S), G)
    dr = ImageDraw.Draw(img)
    P = lambda pts: [(x * S, y * S) for x, y in pts]
    # twin tails: thick curved bands rising to finned tips
    for sgn in (-1, 1):
        cl = [(0.5 + sgn * (0.13 + 0.17 * math.sin(math.pi * t * 0.95)), 0.90 - 0.66 * t) for t in [i / 24 for i in range(25)]]
        left, right = [], []
        for i in range(len(cl)):
            x0, y0 = cl[max(0, i - 1)]; x1, y1 = cl[min(len(cl) - 1, i + 1)]
            dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy) or 1
            w = 0.045 - 0.015 * i / 24
            left.append((cl[i][0] - dy / l * w, cl[i][1] + dx / l * w)); right.append((cl[i][0] + dy / l * w, cl[i][1] - dx / l * w))
        dr.polygon(P(left + right[::-1]), fill=W)
        tx, ty = cl[-1]
        dr.polygon(P([(tx - 0.07, ty - 0.06), (tx, ty + 0.03), (tx + 0.07, ty - 0.06), (tx, ty - 0.01)]), fill=W)
    # hair + face silhouette
    side = [(0.385, 0.31), (0.33, 0.37), (0.305, 0.47), (0.325, 0.58), (0.29, 0.70), (0.31, 0.82), (0.36, 0.93)]
    lft = _catmull(side, 6)
    rgt = [(1 - x, y) for x, y in lft][::-1]
    sil = lft + [(0.5, 0.95)] + rgt
    dr.polygon(P(sil), fill=W, outline=G)
    dr.line(P(sil + [sil[0]]), fill=G, width=int(S * 0.018))
    # hair strands
    for sgn in (-1, 1):
        for k, (x0, x1) in enumerate(((0.43, 0.37), (0.405, 0.335), (0.455, 0.42))):
            pts = _catmull([(0.5 + sgn * (0.5 - x0), 0.36 + 0.02 * k), (0.5 + sgn * (0.5 - x0 - 0.04), 0.5),
                            (0.5 + sgn * (0.5 - x1), 0.66), (0.5 + sgn * (0.5 - x1 + 0.03), 0.8), (0.5 + sgn * (0.5 - x1 - 0.01), 0.9)], 6)
            if k == 2:
                pts = pts[len(pts) // 2:]
            dr.line(P(pts), fill=G, width=int(S * 0.012))
    # face
    fc = (0.5, 0.47)
    dr.ellipse(P([(fc[0] - 0.095, fc[1] - 0.115), (fc[0] + 0.095, fc[1] + 0.12)]), fill=W, outline=G, width=int(S * 0.012))
    for sgn in (-1, 1):
        ex = 0.5 + sgn * 0.04
        dr.arc(P([(ex - 0.022, 0.445), (ex + 0.022, 0.475)]), start=200, end=340, fill=G, width=int(S * 0.008))
    dr.line(P([(0.5, 0.46), (0.492, 0.51), (0.505, 0.515)]), fill=G, width=int(S * 0.007))
    dr.arc(P([(0.47, 0.515), (0.53, 0.55)]), start=20, end=160, fill=G, width=int(S * 0.008))
    # crown with star
    dr.polygon(P([(0.385, 0.33), (0.615, 0.33), (0.6, 0.25), (0.56, 0.285), (0.5, 0.18), (0.44, 0.285), (0.4, 0.25)]), fill=W)
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 0.038 if i % 2 == 0 else 0.016
        star.append((0.5 + r * math.cos(a), 0.285 + r * math.sin(a)))
    dr.polygon(P(star), fill=G)
    img = img.resize((n, n), Image.LANCZOS)
    img.save(f'{d}/sbx_emblem_albedo.png', optimize=True)


def tex_sbx_menu(d):
    W, H = 512, 1024
    img = Image.new('RGB', (W, H), '#1b1d1e')
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 120], fill='#00704a')
    fh = ImageFont.truetype(R.FONT_BOLD, 54)
    fs = ImageFont.truetype(R.FONT_SEMI, 30)
    fi = ImageFont.truetype(R.FONT_SEMI, 27)
    dr.text((W / 2, 60), 'DRIVE THRU', font=fh, fill='white', anchor='mm')
    items = [('Caffè Latte', '19'), ('Cappuccino', '19'), ('Caramel Macchiato', '22'), ('Flat White', '21'),
             ('Iced Americano', '17'), ('Cold Brew', '20'), ('Frappuccino', '24'), ('Chai Tea Latte', '21'),
             ('Matcha Latte', '23'), ('Croissant', '12'), ('Banana Bread', '14')]
    y = 150
    dr.text((30, y), 'HANDCRAFTED', font=fs, fill='#d4e9e2'); y += 50
    rng = random.Random(3)
    for name, price in items:
        dr.ellipse([30, y + 2, 62, y + 34], fill=rng.choice(['#c8a27a', '#e8dcc8', '#6f4e37', '#a3c9a8']))
        dr.text((78, y + 18), name, font=fi, fill='white', anchor='lm')
        dr.text((W - 30, y + 18), price, font=fi, fill='#d4e9e2', anchor='rm')
        y += 62
    dr.rectangle([20, y + 20, W - 20, H - 30], fill='#00704a')
    dr.text((W / 2, (y + H) / 2), 'ORDER HERE', font=fh, fill='white', anchor='mm')
    img.save(f'{d}/sbx_menu_albedo.png', optimize=True)


R.EXTRA_TEXTURES['sbx_emblem'] = tex_sbx_emblem
R.EXTRA_TEXTURES['sbx_menu'] = tex_sbx_menu


def sign_text(acc, L, body, M, size, depth, font=R.FONT_BOLD, front='SBX_SignWhite', side='RS_MetalDark', spacing=1.0):
    res = {0: 3, 1: 2, 2: 1}[L]
    bevel = 0.006 if (L == 0 and size >= 0.5) else 0.0
    acc.add(bm_text(body, font, size, depth if L < 2 else 0.0, bevel, res, spacing=spacing), front, matrix=M,
            mat_fn=front_back(front, side))


def emblem(acc, L, M, r, depth=0.08):
    seg = {0: 40, 1: 20, 2: 12}[L]
    pts = [(r * math.cos(a), r * math.sin(a)) for a in [i / seg * math.tau for i in range(seg)]]
    acc.add(bm_prism_local(pts, depth), 'SBX_Emblem', matrix=M, uv='fit', mat_fn=front_back('SBX_Emblem', 'SBX_Green'))


# ------------------------------------------------------------------ ground & landscape
def build_ground(A, L):
    g = A.m(L, 'Ground')
    beds = [(-23.0, -22.0, -21.0, -19.5), (-15.0, -22.0, 15.0, -19.5), (21.0, -22.0, 23.0, -19.5),
            (-23.0, -8.5, -14.6, 20.0), (-14.6, 14.7, 23.0, 20.0), (17.4, -12.5, 23.0, 14.7),
            (10.3, -8.0, 13.0, 10.3)]
    curb = (BX0 - 0.3, GLASS_Y, BX1 + 0.3, BY1 + 0.3)
    asphalt = [PLOT]
    for h in beds + [curb, TERRACE]:
        asphalt = R.rect_subtract(asphalt, h)
    R.ground_regions(g, asphalt, 'RS_Asphalt')
    R.pad_skirt(g, *PLOT)
    bev = 0.02 if L == 0 else 0.0
    # terrace (pavers, raised) + walkway ring around the building
    g.add(bm_box(*TERRACE[:2], 0.0, *TERRACE[2:], FLOOR, bevel=bev, open_bottom=True), 'RS_Paver')
    for r in R.rect_subtract([curb], (BX0, GLASS_Y, BX1, BY1)):
        g.add(bm_box(r[0], r[1], 0.0, r[2], r[3], FLOOR, open_bottom=True), 'RS_Concrete')
    for b in beds:
        R.curb_bed(g, L, *b)
    land = A.m(L, 'Landscape')
    rng = random.Random(5)
    for i, (x, y) in enumerate(((-19.0, -4.0), (-19.5, 5.0), (-18.5, 13.0), (-6.0, 17.5), (6.0, 17.5),
                                (20.0, 10.0), (20.5, -6.0), (-22.0, -20.75), (22.0, -20.75))):
        R.palm(land, L, x, y, rng.uniform(6.0, 7.8), seed=30 + i)
    for i in range(26):
        x = -14.0 + i * 1.1
        if abs(x) < 0.4:
            continue
        (R.grass_clump if i % 3 == 0 else R.shrub)(land, L, x, -20.75 + rng.uniform(-0.3, 0.3), *( (0.8,) if i % 3 == 0 else (0.85,)), seed=i)
    for i in range(10):
        R.shrub(land, L, -16.0 - (i % 2) * 2.5, -6.0 + i * 2.0, 1.0, seed=60 + i, mat='RS_Foliage2')
        R.grass_clump(land, L, 11.6, -6.5 + i * 1.7, 0.9, seed=80 + i)
    for i in range(12):
        R.shrub(land, L, -12.0 + i * 3.0, 16.2, 0.9, seed=90 + i)
    if L < 2:
        mk = A.m(L, 'Markings')
        R.parking_bays(mk, -11.7, -19.2, -14.2, 9)
        # drive-thru lane edge lines and arrows
        mk.add(bm_hquad(13.2, -14.0, 13.32, 14.7, 0.006), 'RS_LineYellow')
        mk.add(bm_hquad(-14.1, 10.3, 13.2, 10.42, 0.006), 'RS_LineYellow')
        for y in (-11.5, -2.0, 7.0):
            R.arrow_mark(mk, 15.3, y, 90, 3.2)
        for x in (8.0, -2.0, -11.0):
            R.arrow_mark(mk, x, 12.5, 180, 3.2)
        for y in (8.0, -3.0):
            R.arrow_mark(mk, -12.2, y, -90, 3.2)
        R.arrow_mark(mk, -18.0, -11.5, 180, 3.5)
        R.arrow_mark(mk, 18.0, -16.5, 90, 3.5)
        sign_lane = place('+Z', (15.3, 4.0, 0.006), rot_deg=90)
        mk.add(bm_text('DRIVE THRU', R.FONT_BOLD, 0.7, 0.0, 0.0, 2), 'RS_LineWhite', matrix=sign_lane)


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bev = 0.03 if L == 0 else 0.0
    T = 'RS_Travertine'
    # upper volume: left part recessed behind the fin screen, right part flush
    b.add(bm_box(BX0, BY0 + 0.4, H_GF, -1.0, BY1, H_TOP, bevel=bev), T)
    b.add(bm_box(-1.0, BY0, H_GF, BX1, BY1, H_TOP, bevel=bev), T)
    # coping + roof
    if L < 2:
        b.add(bm_ring_prism([(BX0, BY0 + 0.4), (BX1, BY0 + 0.4), (BX1, BY1), (BX0, BY1)],
                            [(BX0 + 0.3, BY0 + 0.7), (BX1 - 0.3, BY0 + 0.7), (BX1 - 0.3, BY1 - 0.3), (BX0 + 0.3, BY1 - 0.3)],
                            H_TOP, H_TOP + 0.08, bottom=False), 'RS_MetalDark')
    # ground floor: side + back walls, corner piers
    b.add(bm_box(BX1 - 0.3, GLASS_Y + 0.3, FLOOR, BX1, BY1, H_GF, open_bottom=True, open_top=True), T)
    b.add(bm_box(BX0 + 0.3, BY1 - 0.3, FLOOR, BX1 - 0.3, BY1, H_GF, open_bottom=True, open_top=True), T)
    b.add(bm_box(BX0, GLASS_Y, FLOOR, BX0 + 0.6, GLASS_Y + 0.3, H_GF, open_bottom=True, open_top=True), T)
    b.add(bm_box(BX1 - 0.6, GLASS_Y, FLOOR, BX1, GLASS_Y + 0.3, H_GF, open_bottom=True, open_top=True), T)
    b.add(bm_box(BX0, GLASS_Y, 0.0, BX1, BY1, FLOOR, open_bottom=True), 'RS_Concrete')
    # soffit under the overhang (with downlights on LOD0/1)
    b.add(bm_hquad(-1.0, BY0, BX1, GLASS_Y, H_GF, down=True), 'RS_Wood')
    b.add(bm_hquad(BX0, BY0 + 0.4, -1.0, GLASS_Y, H_GF, down=True), 'RS_Wood')
    # west-side glazing return near the front + pickup window
    gl = A.m(L, 'Glass')
    gm = 'RS_Glass' if L < 2 else 'RS_GlassLOD'
    gl.add(bm_vquad(BX0 + 0.6, BX1 - 0.6, FLOOR, H_GF, GLASS_Y + 0.15), gm)
    gl.add(bm_quad((BX0 + 0.15, 1.2, FLOOR), (BX0 + 0.15, GLASS_Y + 0.3, FLOOR),
                   (BX0 + 0.15, GLASS_Y + 0.3, H_GF), (BX0 + 0.15, 1.2, H_GF)), gm)
    fr = A.m(L, 'Frames')
    if L < 2:
        n = 9
        for i in range(n + 1):
            x = BX0 + 0.6 + (BX1 - BX0 - 1.2) * i / n
            fr.add(bm_box(x - 0.04, GLASS_Y + 0.08, FLOOR, x + 0.04, GLASS_Y + 0.22, H_GF, open_bottom=True, open_top=True),
                   'RS_MetalDark')
        fr.add(bm_box(BX0 + 0.6, GLASS_Y + 0.08, FLOOR, BX1 - 0.6, GLASS_Y + 0.22, FLOOR + 0.12, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(BX0 + 0.6, GLASS_Y + 0.08, 2.75, BX1 - 0.6, GLASS_Y + 0.22, 2.83), 'RS_MetalDark')
        # main entrance: framed door pair with push bars
        dx0, dx1 = 2.2, 4.4
        fr.add(bm_box(dx0 - 0.08, GLASS_Y - 0.05, FLOOR, dx0, GLASS_Y + 0.25, 2.75, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(dx1, GLASS_Y - 0.05, FLOOR, dx1 + 0.08, GLASS_Y + 0.25, 2.75, open_bottom=True), 'RS_MetalDark')
        fr.add(bm_box(dx0 - 0.08, GLASS_Y - 0.05, 2.6, dx1 + 0.08, GLASS_Y + 0.25, 2.75), 'RS_MetalDark')
        fr.add(bm_box((dx0 + dx1) / 2 - 0.03, GLASS_Y + 0.0, FLOOR, (dx0 + dx1) / 2 + 0.03, GLASS_Y + 0.2, 2.6,
                      open_bottom=True), 'RS_MetalDark')
        if L == 0:
            for hx in ((dx0 + dx1) / 2 - 0.15, (dx0 + dx1) / 2 + 0.15):
                fr.add(bm_cyl_between((hx, GLASS_Y - 0.05, 0.9), (hx, GLASS_Y - 0.05, 1.9), 0.02, 8), 'RS_MetalBrushed')
        for y in (GLASS_Y + 0.34, 1.16):
            fr.add(bm_box(BX0 + 0.05, y - 0.04, FLOOR, BX0 + 0.25, y + 0.04, H_GF, open_bottom=True, open_top=True),
                   'RS_MetalDark')
    # fin screen (left upper facade) - real geometry fins
    fins = A.m(L, 'Fins')
    step = {0: 0.42, 1: 0.84, 2: 1.68}[L]
    x = BX0 + 0.2
    while x < -1.1:
        fins.add(bm_box(x - 0.06, BY0 - 0.12, H_GF - 0.15 if L < 2 else H_GF, x + 0.06, BY0 + 0.38, H_TOP,
                        bevel=0.015 if L == 0 else 0.0), T, tile=1.2)
        x += step
    if L < 2:
        fins.add(bm_box(BX0, BY0 - 0.12, H_GF - 0.3, -1.0, BY0 + 0.38, H_GF - 0.15, bevel=bev), 'RS_MetalDark')
    # pickup window on the west wall
    pw = A.m(L, 'PickupWindow')
    wy0, wy1 = 2.0, 4.2
    pw.add(bm_box(BX0, wy0 - 0.3, 0.0, BX0 + 0.3, wy1 + 0.3, 0.95, open_bottom=True), 'RS_Travertine')
    pw.add(bm_box(BX0, wy0 - 0.3, 2.15, BX0 + 0.3, wy1 + 0.3, H_GF, open_top=True), 'RS_Travertine')
    pw.add(bm_box(BX0, 4.5, FLOOR, BX0 + 0.3, BY1, H_GF, open_bottom=True, open_top=True), 'RS_Travertine')
    pw.add(bm_box(BX0, 1.2, FLOOR, BX0 + 0.3, wy0 - 0.3, H_GF, open_bottom=True, open_top=True), 'RS_Travertine')
    pw.add(bm_box(BX0 - 0.5, wy0 - 0.4, 2.35, BX0 + 0.02, wy1 + 0.4, 2.55, bevel=bev), 'SBX_HouseGreen')
    if L < 2:
        pw.add(bm_box(BX0 - 0.35, wy0 - 0.1, 0.92, BX0 + 0.05, wy1 + 0.1, 0.98, bevel=bev * 0.5), 'RS_MetalBrushed')
        pw.add(bm_quad((BX0 + 0.15, wy1, 0.98), (BX0 + 0.15, wy0, 0.98), (BX0 + 0.15, wy0, 2.12), (BX0 + 0.15, wy1, 2.12)),
               'RS_Glass')
        pw.add(bm_box(BX0 - 0.02, wy0 - 0.06, 0.95, BX0 + 0.3, wy0, 2.15), 'RS_MetalDark')
        pw.add(bm_box(BX0 - 0.02, wy1, 0.95, BX0 + 0.3, wy1 + 0.06, 2.15), 'RS_MetalDark')
        pw.add(bm_box(BX0 - 0.02, (wy0 + wy1) / 2 - 0.03, 0.95, BX0 + 0.3, (wy0 + wy1) / 2 + 0.03, 2.15), 'RS_MetalDark')
        # lit back-of-house wall seen through the window
        pw.add(bm_quad((BX0 + 2.0, wy1 + 0.5, FLOOR), (BX0 + 2.0, wy0 - 0.5, FLOOR), (BX0 + 2.0, wy0 - 0.5, H_GF - 0.3),
                       (BX0 + 2.0, wy1 + 0.5, H_GF - 0.3)), 'RS_InteriorWall')
        pw.add(bm_box(BX0 + 0.3, wy0 - 0.5, FLOOR, BX0 + 1.0, wy1 + 0.5, 0.95, open_bottom=True), 'RS_Wood')
        pw.add(bm_hquad(BX0 + 0.3, wy0 - 0.5, BX0 + 2.0, wy1 + 0.5, H_GF - 0.3, down=True), 'RS_LightWarm')
    s = A.m(L, 'Signage')
    s.add(bm_box(-0.7, -0.22, 0.0, 0.7, 0.22, 0.04), 'SBX_Green', matrix=place('-X', (BX0 - 0.5, 3.1, 2.75)))
    sign_text(s, L, 'PICK-UP', place('-X', (BX0 - 0.545, 3.1, 2.68)), 0.24, 0.03)
    # rooftop plant
    if L < 2:
        rf = A.m(L, 'Roof')
        rf.add(bm_hquad(BX0 + 0.3, BY0 + 0.7, BX1 - 0.3, BY1 - 0.3, H_TOP - 0.25), 'RS_PaintOffWhite')
        for x in (-4.0, 3.0):
            rf.add(bm_box(x - 1.0, 5.0, H_TOP - 0.25, x + 1.0, 7.0, H_TOP + 0.55, bevel=bev, open_bottom=True), 'RS_MetalGalv')
    else:
        b.add(bm_hquad(BX0, BY0 + 0.4, BX1, BY1, H_TOP), 'RS_PaintOffWhite')


def build_interior(A, L):
    if L == 2:
        return
    it = A.m(L, 'Interior')
    ix0, iy0, ix1, iy1 = BX0 + 0.3, GLASS_Y + 0.3, BX1 - 0.3, BY1 - 0.3
    it.add(bm_hquad(ix0, iy0, ix1, iy1, FLOOR + 0.005), 'RS_InteriorFloor')
    it.add(bm_hquad(ix0, iy0, ix1, iy1, 3.2, down=True), 'RS_Wood')
    it.add(bm_vquad(ix0, ix1, FLOOR, 3.2, iy1 - 0.002), 'SBX_HouseGreen')
    it.add(bm_quad((ix1 - 0.002, iy0, FLOOR), (ix1 - 0.002, iy1, FLOOR), (ix1 - 0.002, iy1, 3.2), (ix1 - 0.002, iy0, 3.2)),
           'RS_InteriorWall')
    it.add(bm_quad((ix0 + 0.002, iy1, FLOOR), (ix0 + 0.002, iy0, FLOOR), (ix0 + 0.002, iy0, 3.2), (ix0 + 0.002, iy1, 3.2)),
           'RS_InteriorWall')
    # bar counter + pastry case + menu boards on the back wall
    it.add(bm_box(-6.5, 6.4, FLOOR, 5.0, 7.3, 1.05, bevel=0.02 if L == 0 else 0, open_bottom=True), 'RS_Wood')
    it.add(bm_box(-6.6, 6.35, 1.05, 5.1, 7.35, 1.1), 'RS_PaintCharcoal')
    it.add(bm_box(-5.5, 6.4, 1.1, -2.5, 6.9, 1.6, open_bottom=True), 'RS_Cooler')
    for i in range(3):
        x = -4.5 + i * 3.4
        it.add(bm_box(-1.1, -0.6, 0.0, 1.1, 0.6, 0.04), 'SBX_Menu', matrix=place('-Y', (x, iy1 - 0.01, 2.35)) @
               R.Matrix.Rotation(math.radians(90), 4, 'Z'), uv='fit', mat_fn=front_back('SBX_Menu', 'RS_PlasticBlack'))
    # pendant lights over the counter and seating
    for i in range(7):
        x = -6.0 + i * 2.0
        for y in (5.2, 2.0):
            if L == 0:
                it.add(bm_cyl_between((x, y, 3.2), (x, y, 2.55), 0.006, 4, caps=False), 'RS_PlasticBlack')
                it.add(bm_cyl(x, y, 2.35, 2.55, 0.17, 12, r2=0.05), 'RS_LightWarm')
            else:
                it.add(bm_cyl(x, y, 2.35, 2.55, 0.17, 6, r2=0.05), 'RS_LightWarm')
    # indoor tables
    for i, x in enumerate((-7.5, -4.5, -1.5, 6.5)):
        table(it, L, x, 1.4, indoor=True)


def table(acc, L, x, y, indoor=False, chairs=2):
    seg = {0: 16, 1: 8}[L] if L < 2 else 6
    acc.add(bm_cyl(x, y, 0.72, 0.75, 0.4, seg), 'RS_Wood' if indoor else 'RS_MetalDark')
    acc.add(bm_cyl(x, y, FLOOR, 0.72, 0.035, max(6, seg // 2), open_bottom=True), 'RS_MetalDark')
    if L == 0:
        acc.add(bm_cyl(x, y, FLOOR, FLOOR + 0.03, 0.22, 12, open_bottom=True), 'RS_MetalDark')
    for k in range(chairs):
        a = k / chairs * math.tau + 0.4
        cx, cy = x + 0.72 * math.cos(a), y + 0.72 * math.sin(a)
        chair(acc, L, cx, cy, a + math.pi)


def chair(acc, L, x, y, face_ang):
    M = R.Matrix.Translation((x, y, 0)) @ R.Matrix.Rotation(face_ang - math.pi / 2, 4, 'Z')
    mat = 'SBX_Leather'
    if L == 0:
        acc.add(bm_box(-0.22, -0.22, 0.44, 0.22, 0.22, 0.48, bevel=0.015), mat, matrix=M)
        acc.add(bm_box(-0.22, -0.24, 0.48, 0.22, -0.2, 0.86, bevel=0.012), mat, matrix=M)
        for lx in (-0.19, 0.19):
            for ly in (-0.19, 0.19):
                acc.add(bm_cyl_between((lx, ly, FLOOR), (lx, ly, 0.44), 0.012, 6, caps=False), 'RS_MetalDark', matrix=M)
    else:
        acc.add(bm_box(-0.22, -0.22, FLOOR, 0.22, 0.22, 0.48, open_bottom=True), mat, matrix=M)
        acc.add(bm_box(-0.22, -0.24, 0.48, 0.22, -0.2, 0.86), mat, matrix=M)


def build_terrace(A, L):
    tr = A.m(L, 'Terrace')
    bev = 0.02 if L == 0 else 0.0
    # pergola frame (posts, edge beams, slats perpendicular to the facade)
    py = -6.2
    px = [-9.2, -4.6, 0.0, 4.6, 8.7]
    ztop = 3.62
    for x in px:
        tr.add(bm_box(x - 0.09, py - 0.09, FLOOR, x + 0.09, py + 0.09, ztop, bevel=bev * 0.5, open_bottom=True), 'SBX_Frame')
    tr.add(bm_box(px[0] - 0.09, py - 0.1, ztop - 0.3, px[-1] + 0.09, py + 0.1, ztop, bevel=bev * 0.5), 'SBX_Frame')
    for x in (px[0], px[-1]):
        tr.add(bm_box(x - 0.09, py + 0.1, ztop - 0.3, x + 0.09, BY0 - 0.12, ztop, bevel=bev * 0.5), 'SBX_Frame')
    if L < 2:
        tr.add(bm_box(px[0], BY0 - 0.3, ztop - 0.25, px[-1], BY0 - 0.12, ztop - 0.05), 'SBX_Frame')
    step = {0: 0.32, 1: 0.64, 2: 1.6}[L]
    x = px[0] + step
    while x < px[-1] - 0.05:
        tr.add(bm_box(x - 0.025, py + 0.1, ztop - 0.18, x + 0.025, BY0 - 0.3, ztop - 0.02), 'SBX_Frame')
        x += step
    # seating
    if L < 2:
        for i, x in enumerate((-7.0, -3.4, 0.2)):
            table(tr, L, x, -3.4, chairs=3 if i != 1 else 2)
        for i, x in enumerate((-7.0, -2.5, 2.0)):
            table(tr, L, x, -7.6, chairs=4)
    for i, x in enumerate((-7.0, -2.5, 2.0)):
        umbrella(tr, L, x, -7.6)
    # planters on the terrace edge
    for i, x in enumerate((-8.4, -4.6, 5.7)):
        planter(tr, L, x - 1.2, -8.9, x + 1.2, -8.35, seed=i)
    planter(tr, L, 6.6, -8.3, 8.9, -1.4, seed=9)
    if L < 2:
        planter(tr, L, 4.9, -1.25, 5.8, -0.55, seed=11)


def umbrella(acc, L, x, y):
    seg = {0: 12, 1: 8, 2: 4}[L]
    acc.add(bm_cyl(x, y, FLOOR, 2.55, 0.025, max(4, seg // 2), caps=False), 'RS_MetalBrushed')
    acc.add(bm_cyl(x, y, 2.05, 2.55, 1.45, seg, r2=0.05, caps=False), 'SBX_Umbrella')
    if L == 0:
        acc.add(bm_cyl(x, y, 2.0, 2.05, 1.45, seg, caps=False), 'SBX_Umbrella')
        acc.add(bm_cyl(x, y, FLOOR, FLOOR + 0.08, 0.3, 12, open_bottom=True), 'RS_PaintCharcoal')


def planter(acc, L, x0, y0, x1, y1, seed=0):
    acc.add(bm_box(x0, y0, FLOOR, x1, y1, FLOOR + 0.6, bevel=0.02 if L == 0 else 0, open_bottom=True, open_top=(L < 2)),
            'RS_PaintCharcoal')
    if L == 2:
        return
    acc.add(bm_hquad(x0 + 0.04, y0 + 0.04, x1 - 0.04, y1 - 0.04, FLOOR + 0.52), 'RS_Gravel')
    n = max(2, int(max(x1 - x0, y1 - y0) / 0.55))
    zs = FLOOR + 0.52
    for i in range(n):
        t = (i + 0.5) / n
        px = x0 + (x1 - x0) * (t if x1 - x0 > y1 - y0 else 0.5)
        py = y0 + (y1 - y0) * (t if y1 - y0 >= x1 - x0 else 0.5)
        if i % 2 == 0:
            R.grass_clump(acc, L, px, py, 0.8, seed=seed * 10 + i, z=zs)
        else:
            R.shrub(acc, L, px, py, 0.6, seed=seed * 10 + i, mat='RS_Foliage', z=zs - 0.1)


def build_signage(A, L):
    s = A.m(L, 'Signage')
    fy = BY0 - 0.12
    # emblem + wordmark on the fin screen (mounted proud of the fins)
    emblem(s, L, place('-Y', (-5.5, fy, 5.55)), 0.85)
    sign_text(s, L, 'STARBUCKS', place('-Y', (-5.5, fy, 4.25)), 0.58, 0.06, spacing=1.12)
    # DRIVE THRU on the flush travertine face
    sign_text(s, L, 'DRIVE', place('-Y', (4.5, BY0, 5.55)), 0.95, 0.07, font=R.FONT_SEMI)
    sign_text(s, L, 'THRU', place('-Y', (4.5, BY0, 4.4)), 0.95, 0.07, font=R.FONT_SEMI)
    # emblem on the east wall (seen by drive-thru traffic) and the west wall
    emblem(s, L, place('+X', (BX1, 4.5, 5.2)), 0.9)
    emblem(s, L, place('-X', (BX0, 6.5, 5.2)), 0.9)
    sign_text(s, L, 'STARBUCKS', place('-X', (BX0, 6.5, 3.95)), 0.5, 0.05, spacing=1.12)
    # drive-thru gantry with clearance bar and vertical brand column
    gx0, gx1, gy = 12.9, 17.7, -8.0
    g = A.m(L, 'Gantry')
    bev = 0.02 if L == 0 else 0.0
    g.add(bm_box(gx0 - 0.25, gy - 0.25, 0.0, gx0 + 0.25, gy + 0.25, 3.6, bevel=bev, open_bottom=True), 'RS_PaintCharcoal')
    g.add(bm_box(gx1 - 0.35, gy - 0.35, 0.0, gx1 + 0.35, gy + 0.35, 6.0, bevel=bev, open_bottom=True), 'RS_PaintCharcoal')
    g.add(bm_box(gx0 - 0.25, gy - 0.22, 3.0, gx1, gy + 0.22, 3.6, bevel=bev), 'RS_PaintCharcoal')
    sign_text(s, L, '2.70 CLEARANCE', place('-Y', ((gx0 + gx1) / 2 - 0.2, gy - 0.22, 3.3)), 0.24, 0.02 if L < 2 else 0)
    sign_text(s, L, 'STARBUCKS', place('-Y', (gx1, gy - 0.35, 3.0), rot_deg=90), 0.5, 0.05, spacing=1.1)
    emblem(s, L, place('-Y', (gx1, gy - 0.35, 5.45)), 0.3, 0.04)
    # menu board + order point on the rear lane (facing the westbound driver)
    mx, my = 3.0, BY1 + 0.6
    g.add(bm_box(mx - 1.0, my - 0.15, 0.0, mx + 1.0, my + 0.15, 0.35, bevel=bev, open_bottom=True), 'RS_Concrete')
    g.add(bm_box(mx - 0.9, my - 0.1, 0.35, mx + 0.9, my + 0.1, 2.6, bevel=bev), 'RS_PaintCharcoal')
    g.add(bm_box(-0.8, -1.05, 0.0, 0.8, 1.05, 0.02), 'SBX_Menu', matrix=place('+Y', (mx, my + 0.1, 1.5)), uv='fit',
          mat_fn=front_back('SBX_Menu', 'RS_PlasticBlack'))
    g.add(bm_box(mx + 2.0, my - 0.15, 0.0, mx + 2.4, my + 0.15, 1.4, bevel=bev, open_bottom=True), 'SBX_Green')
    if L < 2:
        g.add(bm_box(mx + 1.95, my - 0.18, 1.0, mx + 2.45, my + 0.18, 1.6, bevel=bev), 'RS_PaintCharcoal')
    # drive-thru fin screen along the west lane (outer edge)
    fs = A.m(L, 'LaneScreen')
    step = {0: 0.5, 1: 1.0, 2: 2.0}[L]
    y = 0.0
    while y <= 10.0:
        fs.add(bm_box(-14.55, y - 0.04, 0.0, -14.35, y + 0.04, 3.6, open_bottom=True), 'RS_PaintWhite')
        y += step
    fs.add(bm_box(-14.6, -0.1, 3.6, -14.3, 10.1, 3.75), 'RS_PaintWhite')


def build_lamps(A, L):
    lp = A.m(L, 'LampPosts')
    for x in (-12.0, 0.0, 12.0):
        R.lamp_post(lp, L, x, -20.75, 8.5, facing=(0, 1), arm=1.3)
    if L < 2:
        # ground uplights grazing the facade
        up = A.m(L, 'Uplights')
        for x in (-8.5, -6.5, -4.5, -2.5, 1.0, 4.5, 8.0):
            up.add(bm_cyl(x, -1.45, FLOOR, FLOOR + 0.08, 0.09, 8 if L == 0 else 6, open_bottom=True), 'RS_MetalDark')
            up.add(bm_cyl(x, -1.45, FLOOR + 0.08, FLOOR + 0.085, 0.07, 8 if L == 0 else 6, caps=True), 'RS_LampHead')


def build_collision(A):
    A.col_box('GroundPad', *PLOT[:2], -0.5, *PLOT[2:], 0.0)
    A.col_box('Building', BX0, GLASS_Y, 0.0, BX1, BY1, H_TOP)
    A.col_box('UpperFront', BX0, BY0 - 0.12, H_GF - 0.3, BX1, GLASS_Y, H_TOP)
    A.col_box('Terrace', *TERRACE[:2], 0.0, *TERRACE[2:], FLOOR)
    A.col_box('GantryPost', 12.65, -8.25, 0.0, 13.15, -7.75, 3.6)
    A.col_box('GantryColumn', 17.35, -8.35, 0.0, 18.05, -7.65, 6.0)
    A.col_box('GantryBeam', 12.65, -8.22, 3.0, 17.7, -7.78, 3.6)
    A.col_box('MenuBoard', 2.0, 10.45, 0.0, 4.0, 10.75, 2.6)
    A.col_box('LaneScreen', -14.6, -0.1, 0.0, -14.3, 10.1, 3.75)
    for i, x in enumerate((-12.0, 0.0, 12.0)):
        A.col_box(f'LampPost{i}', x - 0.25, -21.0, 0.0, x + 0.25, -20.5, 8.5)


def build_lights(A):
    for i, x in enumerate((-6.0, -1.0, 4.0)):
        A.light(f'Interior{i}', 'POINT', (x, 3.5, 2.8), 300, '#ffcf96', radius=0.4)
    for i, x in enumerate((-6.5, -1.0, 4.5)):
        A.light(f'Pergola{i}', 'SPOT', (x, -4.0, 3.3), 220, '#ffd8a8', spot_deg=130, blend=0.8, radius=0.2)
    for i, x in enumerate((-8.5, -4.5, 1.0, 4.5, 8.0)):
        A.light(f'Uplight{i}', 'SPOT', (x, -1.45, FLOOR + 0.12), 450, '#ffdcae', rot=(170, 0, 0), spot_deg=55, blend=0.6, radius=0.05)
    A.light('PickupWindow', 'SPOT', (BX0 - 0.3, 3.1, 2.3), 150, '#ffe0b8', spot_deg=120, blend=0.7)
    A.light('Gantry', 'SPOT', (15.3, -8.0, 2.95), 300, '#fff1de', spot_deg=120, blend=0.7)
    for i, x in enumerate((-12.0, 0.0, 12.0)):
        A.light(f'LampPost{i}', 'SPOT', (x, -19.45, 8.4), 1100, '#fff2df', spot_deg=125, blend=0.6, radius=0.3)


def main():
    A = R.Asset('SBX', 'DriveThru', ASSET_DIR, 'starbucks_drive_thru')
    for L in (0, 1, 2):
        build_ground(A, L)
        build_building(A, L)
        build_interior(A, L)
        build_terrace(A, L)
        build_signage(A, L)
        build_lamps(A, L)
    build_collision(A)
    build_lights(A)
    R.build_preview_env(A, PLOT)
    A.camera('day_hero', (-17.0, -40.0, 4.6), (-0.5, -2.0, 3.3), 30)
    A.camera('driveby', (-55.0, -29.5, 1.25), (-3.0, -3.0, 3.6), 32)
    A.camera('closeup1', (-12.6, -7.5, 1.55), (-9.8, 3.2, 1.7), 26)
    A.camera('closeup2', (5.5, -13.5, 1.7), (-1.5, -1.5, 2.6), 28)
    A.camera('overview', (38.0, -48.0, 30.0), (0.0, 0.0, 1.0), 32)
    stats = A.finalize()
    blend, glb, res = A.save_and_export()
    print('STATS', json.dumps(stats))
    print('EXPORT', res, blend, glb)


if __name__ == '__main__':
    main()
