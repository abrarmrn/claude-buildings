"""ASSET 05 - PAUL Bakery & Cafe (French bakery storefront; boulevard podium retail).

Plot 36 m x 28 m, road side faces -Y, origin = plot centre at finished ground.
Massing: two-storey black classical facade with gold trim, arched ground-floor windows and door, sign board,
cornice with dentils, shuttered upper windows with flower boxes, black awnings, railed travertine terrace.
Branding is a simplified recreation (gold serif lettering), not the official artwork.
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store_kit import *

PLOT = (-18.0, -14.0, 18.0, 14.0)
BX0, BY0, BX1, BY1 = -8.0, 1.0, 8.0, 10.0
FLOOR1, SIGN0, SIGN1, H = 4.7, 4.75, 6.0, 8.4
WIN = [(-5.6, 3.2, 0.75, 2.75), (-1.9, 3.2, 0.75, 2.75), (5.6, 3.2, 0.75, 2.75)]
DOOR = (1.9, 2.4, 0.15, 2.4)
TERRACE = (-12.0, -7.0, 12.0, BY0)
ENTRY, EXIT = (-17.0, -12.0), (12.0, 17.0)
BEDS = front_beds(PLOT, [ENTRY, EXIT], depth=1.8) + [(-18.0, -12.0, -17.2, 14.0), (17.2, -12.0, 18.0, 14.0), (-17.0, 12.5, 17.0, 14.0)]

defmat('PA_Black', '#0f1011', rough=0.28, metal=0.1, spec=0.7)
defmat('PA_Gold', '#c6a04e', rough=0.28, metal=1.0)
defmat('PA_GoldLit', '#d9b25c', rough=0.3, metal=0.4, emit='#e6b44e', es=2.6)
defmat('PA_Awning', '#17181a', rough=0.85, double=True)
defmat('PA_Wicker', '#6b4a2b', rough=0.75)
defmat('PA_Marble', '#e9e6e0', rough=0.25)
defmat('PA_Lantern', '#ffffff', rough=0.3, emit='#ffc27a', es=4.0)
defmat('PA_Cream', '#efe6d4', rough=0.6)
defmat('PA_Wood', '#7b5233', rough=0.5)
defmat('PA_Menu', '#17120e', rough=0.3, emit='#ffd9a0', es=0.7)


def paul_wordmark(acc, L, M, size=1.15, depth=0.07):
    txt(acc, L, 'PAUL', M, size, depth, 'serif_b', 'PA_GoldLit', 'PA_Gold', spacing=1.15)


# ------------------------------------------------------------------ ground
def build_ground(A, L):
    holes = [(BX0 - 0.05, BY0 - 0.05, BX1 + 0.05, BY1 + 0.05), (8.5, -13.7, 11.0, -12.4)]
    site_ground(A, L, PLOT, holes, [TERRACE], BEDS, paver_h=0.12, mat_paved='RS_Travertine')
    land = A.m(L, 'Landscape')
    palms(A, L, [(16.5, -11.5), (-16.5, 7.0), (16.5, 7.0)], 170)
    rng = random.Random(14)
    for i in range(16):
        x = -9.5 + i * 1.3
        if EXIT[0] - 1 < x < EXIT[1] + 1 or 8.0 < x < 11.5:
            continue
        R.shrub(land, L, x, -13.0 + rng.uniform(-0.1, 0.1), 0.7, seed=i, mat='RS_Foliage')
    entry_exit(A, L, PLOT, -14.5, 14.5, depth=1.8)
    cars = {1: ('RS_CarBlack', 'sedan'), 5: ('RS_CarWhite', 'suv')}
    parking_row(A, L, -8.0, -12.5, -8.0, 6, 2.6, cars)
    # terrace: black railing around front and sides with a gap at the door path
    fur = A.m(L, 'Furniture')
    pts = [(x, -6.8) for x in [-11.5 + i * 1.5 for i in range(16)] if not (0.0 < x < 4.0)]
    for (x, y) in pts:
        fur.add(bm_cyl(x, y, 0.12, 1.0, 0.025, 6, open_bottom=True), 'PA_Black')
    if L < 2:
        for xa, xb in ((-11.5, -0.2), (3.8, 11.5)):
            fur.add(bm_box(xa, -6.84, 0.96, xb, -6.76, 1.0), 'PA_Black')
            fur.add(bm_box(xa, -6.84, 0.4, xb, -6.76, 0.43), 'PA_Black')
        for x in (-11.5, 11.5):
            fur.add(bm_box(x - 0.04, -6.8, 0.96, x + 0.04, BY0, 1.0), 'PA_Black')
    rng2 = random.Random(3)
    for i, (x, y) in enumerate(((-9.5, -3.4), (-6.2, -4.4), (-2.8, -3.6), (6.0, -4.2), (9.3, -3.2), (9.0, -0.2))):
        cafe_set(fur, L, x, y, 3 if i % 2 else 2, ang=rng2.uniform(0, 90), table_mat='PA_Marble', chair_mat='PA_Wicker', seat_mat='PA_Wicker', r=0.34)
    for x in (0.2, 3.6):
        topiary(fur, L, x, -0.6, 1.7, 0.42, 'PA_Black', 'RS_Foliage')
    for x in (-11.0, 11.0):
        topiary(fur, L, x, -5.9, 1.5, 0.4, 'PA_Black', 'RS_Foliage')
    # terrace lanterns on slim posts (warm light)
    if L < 2:
        for x in (-8.0, -4.4, 5.0, 8.4):
            fur.add(bm_cyl(x, -6.5, 0.12, 2.5, 0.025, 6, open_bottom=True), 'PA_Black')
            fur.add(bm_box(x - 0.1, -6.6, 2.5, x + 0.1, -6.4, 2.85, bevel=0.01 if L == 0 else 0), 'PA_Lantern')
        for k, x in enumerate((-9.0, 9.0)):
            R.bollard(fur, L, x, -7.4, 0.9, 0.08)


# ------------------------------------------------------------------ building
def build_building(A, L):
    b = A.m(L, 'Building')
    bv = 0.02 if L == 0 else 0.0
    t = 0.35
    # slab, side/back walls + roof (front wall handled separately)
    shell(b, L, (BX0, BY0, BX1, BY1), H, 'PA_Black', t=t, holes=[], roof_mat='PA_Black', roof_t=0.4, rooftop=True,
          skip=('front', 'left'), parapet=0.0)
    # west wall with real window openings (ground + upper floor), glass and gold frames
    wy = (3.6, 6.0, 8.4)
    holes_w = [(y - 0.7, 0.95, y + 0.7, 3.45) for y in wy] + [(y - 0.6, 6.3, y + 0.6, 7.75) for y in wy]
    rects = [(BY0 + t, 0.15, BY1 - t, H - 0.4)]
    for hh in holes_w:
        rects = rect_subtract(rects, hh)
    for (y0, z0, y1, z1) in rects:
        b.add(bm_box(BX0, y0, z0, BX0 + t, y1, z1, bevel=bv, open_bottom=z0 <= 0.2), 'PA_Black')
    gl_, fr_ = A.m(L, 'Glass'), A.m(L, 'Frames')
    for (y0, z0, y1, z1) in holes_w:
        gl_.add(bm_quad((BX0 + 0.1, y1, z0), (BX0 + 0.1, y0, z0), (BX0 + 0.1, y0, z1), (BX0 + 0.1, y1, z1)), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
        if L < 2:
            for (a, c, d, e) in ((y0 - 0.06, z0 - 0.06, y1 + 0.06, z0), (y0 - 0.06, z1, y1 + 0.06, z1 + 0.06), (y0 - 0.06, z0, y0, z1), (y1, z0, y1 + 0.06, z1),
                                 ((y0 + y1) / 2 - 0.025, z0, (y0 + y1) / 2 + 0.025, z1)):
                fr_.add(bm_box(BX0 - 0.03, a, c, BX0 + 0.14, d, e), 'PA_Gold')
    # ground-floor front wall with arched openings (windows + door)
    arch_wall(b, L, BX0, BX1, BY0, t, 0.15, FLOOR1, WIN + [DOOR], 'PA_Black', bevel=bv)
    # upper front wall with four rectangular windows
    ups = [(xc - 0.75, 6.35, xc + 0.75, 7.85) for xc in (-5.6, -1.9, 1.9, 5.6)]
    front_wall(b, L, BX0, BX1, BY0, t, FLOOR1, H - 0.4, ups, 'PA_Black', bevel=bv)
    # pilasters + gold trim lines
    for x0, x1 in ((BX0, BX0 + 0.6), (BX1 - 0.6, BX1)):
        b.add(bm_box(x0, BY0 - 0.12, 0.15, x1, BY0, H - 0.4, bevel=bv, open_bottom=True), 'PA_Black')
        b.add(bm_box(x0 - 0.04, BY0 - 0.16, 4.3, x1 + 0.04, BY0, 4.7, bevel=bv), 'PA_Gold')
    for z in (FLOOR1 - 0.02, SIGN1, 7.95):
        b.add(bm_box(BX0, BY0 - 0.1, z, BX1, BY0, z + 0.07), 'PA_Gold')
    # sign board (black, gold-framed) and cornice with dentils
    b.add(bm_box(BX0 + 0.6, BY0 - 0.08, SIGN0, BX1 - 0.6, BY0, SIGN1 - 0.05), 'PA_Black')
    b.add(bm_box(BX0 - 0.15, BY0 - 0.55, H - 0.4, BX1 + 0.15, BY1, H + 0.08, bevel=bv), 'PA_Black')
    b.add(bm_box(BX0 - 0.17, BY0 - 0.58, H - 0.08, BX1 + 0.17, BY0 - 0.45, H + 0.14), 'PA_Gold')
    if L == 0:
        for i in range(int((BX1 - BX0) / 0.45)):
            x = BX0 + 0.1 + i * 0.45
            b.add(bm_box(x, BY0 - 0.5, H - 0.62, x + 0.22, BY0 - 0.1, H - 0.4), 'PA_Gold')
    # awnings over the windows and door
    awn = A.m(L, 'Awnings')
    for xc, w, zb, zs in WIN + [DOOR]:
        awning(awn, L, xc - w / 2 - 0.1, xc + w / 2 + 0.1, BY0 - 0.12, FLOOR1 - 0.35, 0.7, 1.3, ('PA_Awning',), strip=0.8, valance=0.28)
    # flower boxes under the upper windows
    for xc in (-5.6, -1.9, 1.9, 5.6):
        b.add(bm_box(xc - 0.85, BY0 - 0.35, 5.95, xc + 0.85, BY0 - 0.05, 6.35, bevel=bv), 'PA_Gold')
        if L < 2:
            R.shrub(b, L, xc - 0.4, BY0 - 0.2, 0.3, seed=int(xc * 10), mat='RS_Foliage2', z=6.3)
            R.shrub(b, L, xc + 0.4, BY0 - 0.2, 0.3, seed=int(xc * 10) + 1, mat='RS_Foliage', z=6.3)
    # glazing: arched windows, door, upper windows
    for xc, w, zb, zs in WIN:
        arch_window(A, L, xc, w, zb, zs, BY0 + 0.12, 'PA_Gold', 0.07, 2, transom=zs)
    arch_window(A, L, DOOR[0], DOOR[1], DOOR[2], DOOR[3], BY0 + 0.12, 'PA_Gold', 0.08, 1)
    gl, fr = A.m(L, 'Glass'), A.m(L, 'Frames')
    for xc in (-5.6, -1.9, 1.9, 5.6):
        gl.add(bm_vquad(xc - 0.75, xc + 0.75, 6.35, 7.85, BY0 + 0.12), 'RS_Glass' if L < 2 else 'RS_GlassLOD')
        if L < 2:
            fr.add(bm_box(xc - 0.8, BY0 + 0.05, 6.3, xc + 0.8, BY0 + 0.2, 6.35), 'PA_Gold')
            fr.add(bm_box(xc - 0.8, BY0 + 0.05, 7.85, xc + 0.8, BY0 + 0.2, 7.9), 'PA_Gold')
            fr.add(bm_box(xc - 0.03, BY0 + 0.05, 6.35, xc + 0.03, BY0 + 0.2, 7.85), 'PA_Gold')
    # wall lanterns between the arches
    if L < 2:
        for x in (-3.75, 0.2, 3.55):
            b.add(bm_box(x - 0.08, BY0 - 0.26, 2.7, x + 0.08, BY0 - 0.1, 3.1), 'PA_Lantern')
    # signage
    s = A.m(L, 'Signage')
    paul_wordmark(s, L, place('-Y', (0.0, BY0 - 0.1, 5.4)), 1.15)
    txt(s, L, 'BOULANGERIE', place('-Y', (-5.0, BY0 - 0.1, 5.38)), 0.3, 0.03, 'serif', 'PA_GoldLit', 'PA_Gold', spacing=1.25, min_size_lod2=9)
    txt(s, L, 'PÂTISSERIE', place('-Y', (5.0, BY0 - 0.1, 5.38)), 0.3, 0.03, 'serif', 'PA_GoldLit', 'PA_Gold', spacing=1.25, min_size_lod2=9)
    for sx, face in ((BX1, '+X'),):
        paul_wordmark(s, L, place(face, (sx + 0.02, 3.5, 4.2)), 0.6, 0.04)
    if L == 0:
        register_sign(A, 'PAUL sign board', (0.0, BY0 - 0.2, 5.4), 0.8, width=2.8)


def build_interior(A, L):
    if L == 2:
        return
    ix0, iy0, ix1, iy1 = BX0 + 0.35, BY0 + 0.35, BX1 - 0.35, BY1 - 0.35
    it = interior_shell(A, L, (ix0, iy0, ix1, iy1), 4.5, 'RS_TileFloor', 'PA_Cream',
                        lights=light_grid((ix0, iy0, ix1, iy1), 4, 2, (1.2, 0.25), 1.2), back_mat='PA_Cream')
    # back wall wood panelling + bread rack
    it.add(bm_box(ix0, iy1 - 0.12, 0.15, ix1, iy1, 2.6, open_bottom=True), 'PA_Wood')
    rng = random.Random(8)
    for i in range(6):
        x = -6.5 + i * 2.3
        it.add(bm_box(x - 0.9, iy1 - 0.5, 1.0 + (i % 3) * 0.55 - 0.02, x + 0.9, iy1 - 0.12, 1.0 + (i % 3) * 0.55 + 0.02), 'PA_Gold')
        if L == 0:
            for k in range(5):
                a = rng.uniform(-0.2, 0.2)
                it.add(bm_cyl_between((x - 0.7 + k * 0.35, iy1 - 0.4, 1.04 + (i % 3) * 0.55), (x - 0.7 + k * 0.35 + a, iy1 - 0.25, 1.62 + (i % 3) * 0.55), 0.035, 6), 'RS_Bread')
        else:
            it.add(bm_box(x - 0.8, iy1 - 0.45, 1.04 + (i % 3) * 0.55, x + 0.8, iy1 - 0.2, 1.5 + (i % 3) * 0.55), 'RS_Bread')
    # display counters with pastries (visible through the windows)
    for k, (xa, xb) in enumerate(((-7.0, -3.2), (-2.4, 1.4))):
        counter(it, L, xa, 3.4, xb, 4.4, 1.0, 'PA_Black', 'PA_Marble')
        it.add(bm_box(xa + 0.05, 3.5, 1.1, xb - 0.05, 4.3, 1.6), 'RS_Cooler')
        if L == 0:
            for i in range(int((xb - xa) / 0.28)):
                it.add(bm_cyl(xa + 0.2 + i * 0.28, 3.9, 1.1, 1.16, 0.08, 8), rng.choice(['RS_Pastry', 'RS_Pink', 'RS_Choc', 'RS_Cream']))
                it.add(bm_sphere((xa + 0.2 + i * 0.28, 3.9, 1.22), 0.05, 1), 'RS_Bread')
    # tiered cake stands + cash counter + tables
    counter(it, L, 3.6, 5.5, 7.2, 6.5, 1.05, 'PA_Black', 'PA_Marble')
    for i, (x, y) in enumerate(((-6.5, 7.0), (-3.5, 7.2), (-0.5, 7.0))):
        cafe_set(it, L, x, y, 2, ang=90 * i, table_mat='PA_Marble', chair_mat='PA_Black', seat_mat='PA_Wicker', r=0.32)
    # upper floor suggestion: warm lit slab seen through the upper windows
    it.add(bm_hquad(ix0, iy0, ix1, iy1, 4.6 + 0.02), 'PA_Cream')
    it.add(bm_hquad(ix0, iy0, ix1, iy1, 7.95, down=True), 'RS_LightWarm')
    it.add(bm_vquad(ix0, ix1, 4.62, 7.95, iy1 - 0.002), 'PA_Cream')


LAMPS = [(-3.5, -12.5, 0, 1), (10.5, -12.5, 0, 1), (-16.5, 2.0, 1, 0), (16.5, 2.0, -1, 0)]


def build_collision(A):
    A.col_box('GroundPad', PLOT[0], PLOT[1], -0.5, PLOT[2], PLOT[3], 0.0)
    A.col_box('Building', BX0, BY0 - 0.2, 0.0, BX1, BY1, H + 0.1)
    A.col_box('Terrace', *TERRACE[:2], 0.0, *TERRACE[2:], 0.12)
    lamp_collision(A, LAMPS)


def build_lights(A):
    for i, x in enumerate((-5.6, -1.9, 1.9, 5.6)):
        A.light(f'Window{i}', 'POINT', (x, 4.0, 2.4), 650, '#ffd9a0', radius=0.5)
        A.light(f'Upper{i}', 'POINT', (x, 4.0, 6.9), 350, '#ffcf90', radius=0.5)
    glow_lights(A, 'Terrace', [(-8.0, -5.0, 2.7), (-4.4, -5.0, 2.7), (5.0, -5.0, 2.7), (8.4, -5.0, 2.7)], energy=420, color='#ffc27a')
    A.light('SignGlow', 'SPOT', (0.0, -6.0, 5.4), 2600, '#ffe2b0', rot=(-90, 0, 0), spot_deg=110, blend=0.8, radius=0.3)
    A.light('CorniceUp', 'SPOT', (0.0, -3.0, 0.4), 1500, '#ffd9a6', rot=(-60, 0, 0), spot_deg=100, blend=0.9, radius=0.3)
    lamp_lights(A, LAMPS)


def main():
    A = Store('05', '05_paul_bakery', 'paul_bakery', 'PAUL', 'BakeryCafe', 'PAUL Bakery & Cafe')
    A.dims = dict(plot=[36.0, 28.0], building=[BX1 - BX0, BY1 - BY0, H], cornice_height=H + 0.14)
    for L in (0, 1, 2):
        build_ground(A, L); build_building(A, L); build_interior(A, L)
        lamp_set(A, L, LAMPS)
    build_collision(A); build_lights(A)
    A.camera('day', (-17.0, -22.0, 3.6), (0.0, 3.0, 3.6), 32)
    A.camera('road', (-24.0, PLOT[1] - 8.6, 1.25), (0.0, -4.0, 4.0), 32)
    A.camera('detail', (-2.0, -10.5, 1.7), (1.0, 1.0, 3.6), 30)
    finish(A, PLOT)


if __name__ == '__main__':
    main()
