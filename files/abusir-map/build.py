"""Rebuild File:Abusir map.png as SVG (run from the repo root after geometry.py and refine.py):
- structures, causeways, river and scale bar: from File:AbusirAndAbuGurabPlan ru.svg (a redrawing of this
  PNG), registered and per-element shifted/stroke-scaled to the PNG (elements.json);
- necropolis area: an ellipse fitted to the PNG's grey loop;
- north arrow: measured from the PNG;
- labels: real <text> in DejaVu Sans, size and position from each line's ink box (PIL metrics of the font);
- leader lines: straight segments fitted (PCA) to the ink left over after everything else.
"""
import io, json, re
import numpy as np, resvg_py
from PIL import Image, ImageFont
from scipy import ndimage

PNG = 'data_lake/downloads/abusir-map/Abusir map.png'
OUT = 'files/abusir-map/Abusir map.svg'
FONT = 'data_lake/downloads/fonts/dejavu/DejaVuSans.ttf'
G = json.load(open('files/abusir-map/geometry.json'))
EL = json.load(open('files/abusir-map/elements.json'))

im = Image.alpha_composite(Image.new('RGBA', (832, 868), 'white'), Image.open(PNG).convert('RGBA')).convert('RGB')
a = np.asarray(im).astype(int)
H, W = a.shape[:2]
ink = a.mean(-1) < 128
grey = (np.abs(a - [138, 132, 132]).max(-1) < 12) & (a[..., 0] - a[..., 1] >= 3)  # the loop's reddish grey

# label lines: text and the approximate centre of its line in the PNG (read off the image)
LINES = [
    ('Abu Gorab', 322, 53), ('Nyuserre Ini', 118, 110), ('Sun', 118, 129), ('Temple', 118, 148),
    ('200 metres', 696, 88), ('Cultivation', 679, 187), ('Userkaf', 304, 216), ('Sun', 307, 235),
    ('Temple', 307, 254), ('Unfinished', 355, 330), ('Pyramid', 355, 349), ('Sahure', 562, 326),
    ('Pyramid', 562, 345), ('Complex', 562, 364), ('Abusir', 771, 345), ('N', 190, 327),
    ('Nyuserre Ini', 401, 443), ('Pyramid', 401, 462), ('Complex', 401, 481), ('Ptahshepse', 715, 462),
    ('Mastaba', 715, 481), ('Neferirkare', 360, 525), ('Pyramid', 360, 544), ('Complex', 360, 563),
    ('Khentkaus II', 651, 574), ('Pyramid', 651, 593), ('Neferefe', 355, 615), ('Unfinished', 355, 634),
    ('Pyramid', 355, 653), ('Necropolis', 613, 634), ('Area', 613, 653), ('Lepsius', 443, 678),
    ('Pyramid 24', 443, 697), ('Lepsius', 562, 706), ('Pyramid 25', 562, 725), ('Shaft Tomb', 464, 795),
]


def render(svg):
    r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[FONT], skip_system_fonts=True)))).convert('RGBA')
    return np.asarray(Image.alpha_composite(Image.new('RGBA', r.size, 'white'), r).convert('RGB')).astype(int)


def doc(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>{body}</svg>')


# 1. geometry
# the river: its fitted width (x1.8) covered the PNG's jagged hand-drawn line; the PNG's stroke is 3 px
for e in EL:
    if e['id'] == 'path3227':
        e['xml'] = re.sub(r'stroke-width:[0-9.]+', 'stroke-width:3.0', e['xml'])
geo = ''.join(e['xml'] for e in EL if e['id'] != 'path3370')
geo = (f'<g id="structures" transform="translate({G["tx"]:.3f},{G["ty"]:.3f}) scale({G["scale"]:.5f}) '
       f'translate(0,-68.000038)">{geo}</g>')

# 2. necropolis: algebraic ellipse fit to the grey loop
ys, xs = np.nonzero(grey[560:700, 520:680])
ox, oy = xs.mean() + 520.0, ys.mean() + 560.0
xs, ys = xs + 520.0 - ox, ys + 560.0 - oy  # centred, for a well-conditioned fit
D = np.c_[xs * xs, xs * ys, ys * ys, xs, ys, np.ones_like(xs)]
A, B, C, Dd, E, F = np.linalg.svd(D)[2][-1]
cx = (2 * C * Dd - B * E) / (B * B - 4 * A * C)
cy = (2 * A * E - B * Dd) / (B * B - 4 * A * C)
M = np.array([[A, B / 2], [B / 2, C]])
val = -(A * cx * cx + B * cx * cy + C * cy * cy + Dd * cx + E * cy + F)
w, v = np.linalg.eigh(M / val)
rx, ry = 1 / np.sqrt(w)
ang = np.degrees(np.arctan2(v[1, 0], v[0, 0]))
cx, cy = cx + ox, cy + oy
necro = (f'<ellipse id="necropolis" cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
         f'transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})" fill="none" stroke="#8a8484" stroke-width="3"/>')

# 3. north arrow (measured: head y 337-343, shaft to y=446; crossbar y=368, x 175-207)
cols = np.nonzero(ink[400:440, 180:200].any(0))[0] + 180
sx = (cols.min() + cols.max() + 1) / 2
sw = cols.max() - cols.min() + 1
north = (f'<g id="north" stroke="#000" stroke-width="{sw}"><path d="M {sx},338 V 446 M 175,368.5 H 208" fill="none"/>'
         f'<path d="M {sx},336.5 L {sx + 5.5},343.5 L {sx - 5.5},343.5 Z" fill="#000" stroke="none"/></g>')

base = render(doc(geo + necro + north)).mean(-1) < 128
covered = ndimage.binary_dilation(base, iterations=3)

# 4. labels
font = {}
texts, fits = [], []
for t, cx_, cy_ in LINES:
    half = len(t) * 5 + 12
    x0, x1, y0, y1 = int(cx_ - half), int(cx_ + half), cy_ - 11, cy_ + 11
    win = ink[y0:y1, x0:x1] & ~covered[y0:y1, x0:x1]
    lab, n = ndimage.label(win)
    keep = np.zeros_like(win)
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        n_px = (lab[sl] == i).sum()
        thin_line = w_ > 10 and n_px < 2.6 * max(w_, h_)  # a piece of a leader line, not a glyph
        if h_ <= 16 and w_ <= 22 and not thin_line:
            keep |= lab == i
    # the text band: the run of inked rows through the line's centre (drops the neighbouring lines)
    rows = keep.any(1)
    c = cy_ - y0
    while c < len(rows) - 1 and not rows[c]:
        c += 1
    top, bot = c, c
    while top > 0 and rows[top - 1]:
        top -= 1
    while bot < len(rows) - 1 and rows[bot + 1]:
        bot += 1
    keep[:top] = False
    keep[bot + 1:] = False
    yy, xx = np.nonzero(keep)
    bx0, bx1, by0, by1 = xx.min() + x0, xx.max() + x0, yy.min() + y0, yy.max() + y0
    # font size whose ink width matches the box, then place by the ink's left and top edges
    best = None
    for size in np.arange(8, 24, 0.1):
        f = font.setdefault(round(size, 1), ImageFont.truetype(FONT, size))
        l, tp, r, b = f.getbbox(t, anchor='ls')
        err = abs((r - l) - (bx1 - bx0 + 1))
        if best is None or err < best[0]:
            best = (err, size, l, tp)
    fits.append((t, best[1], (bx0 + bx1 + 1) / 2, by0, by1))

# one size for the body labels (the PNG uses one), the fitted size for the two place names and the small ones
body = float(np.median([f[1] for f in fits if f[0] not in ('Abu Gorab', 'Abusir', '200 metres', 'N')]))
placed = []
for (t, size, mx, by0, by1), (_, cx_, cy_) in zip(fits, LINES):
    if t not in ('Abu Gorab', 'Abusir', '200 metres', 'N'):
        size = body
    f = ImageFont.truetype(FONT, size)
    l, tp, r, b = f.getbbox(t, anchor='ls')
    # centred on the ink box; baseline from the top of the ink (letters with ascenders or capitals)
    placed.append([t, size, mx, by0 - tp, cx_, cy_])
# labels are centred stacks of lines 19 px apart: a leader line touching one line spoils its own box, so
# every line of a stack takes the stack's median centre and median baseline (less its line offset)
stacks, cur = [], [0]
for i in range(1, len(placed)):
    if abs(placed[i][4] - placed[i - 1][4]) <= 6 and 15 <= placed[i][5] - placed[i - 1][5] <= 23:
        cur.append(i)
    else:
        stacks.append(cur)
        cur = [i]
stacks.append(cur)
for st in stacks:
    if len(st) > 1:
        x = float(np.median([placed[i][2] for i in st]))
        b0 = float(np.median([placed[i][3] - k * 19 for k, i in enumerate(st)]))
        for k, i in enumerate(st):
            placed[i][2], placed[i][3] = x, b0 + k * 19
boxes = []
for t, size, x, y, _, _ in placed:
    texts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size:.1f}" text-anchor="middle">{t}</text>')
    l, tp, r, b = ImageFont.truetype(FONT, size).getbbox(t, anchor='ms')
    boxes.append((x + l, y + tp, x + r, y + b))


def near_label(p, pad=12):
    return any(x0 - pad <= p[0] <= x1 + pad and y0 - pad <= p[1] <= y1 + pad for x0, y0, x1, y1 in boxes)
labels = ('<g id="labels" font-family="DejaVu Sans" fill="#000">' + ''.join(texts) + '</g>')

# 5. leader lines from what is left
done = render(doc(geo + necro + north + labels)).mean(-1) < 128
left = ink & ~ndimage.binary_dilation(done, iterations=2)
lab, n = ndimage.label(ndimage.binary_dilation(left, iterations=2))
segs = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    yy, xx = np.nonzero((lab == i) & ink)
    if len(xx) < 22:
        continue
    P = np.c_[xx, yy].astype(float)
    m = P.mean(0)
    u = np.linalg.svd(P - m)[2][0]
    proj = (P - m) @ u
    p0, p1 = m + u * proj.min(), m + u * proj.max()
    width = len(xx) / max(np.hypot(*(p1 - p0)), 1)
    if np.hypot(*(p1 - p0)) < 13 or width > 5:  # a straight thin run, not a leftover blob
        continue
    if not (near_label(p0) or near_label(p1)):  # leftovers of the geometry, not a leader
        continue
    if near_label((p0 + p1) / 2, pad=0):  # leftover glyph edges inside a label
        continue
    segs.append((p0, p1, width))
# the Sahure leader runs into its pyramid, so only 11 px of it is left over: measured by hand
segs.append((np.array([557.5, 375.0]), np.array([550.0, 389.0]), 3.4))
sw_lead = float(np.median([w_ for _, _, w_ in segs]))
leaders = (f'<path id="leaders" stroke="#000" stroke-width="{sw_lead:.1f}" fill="none" d="'
           + ' '.join(f'M {p0[0]:.1f},{p0[1]:.1f} L {p1[0]:.1f},{p1[1]:.1f}' for p0, p1, _ in segs) + '"/>')

svg = doc(geo + necro + north + leaders + labels)
open(OUT, 'w', encoding='utf8').write(svg)
out = render(svg).mean(-1) < 128
print('body size %.1f' % body, 'leader width %.1f' % sw_lead, 'labels', len(texts), 'leaders', len(segs), 'ink IoU %.4f' % ((out & ink).sum() / (out | ink).sum()),
      'pixels differing %.4f' % (out != ink).mean())
rgb = np.full((H, W, 3), 255, np.uint8)
rgb[ink & ~out] = (0, 0, 255)
rgb[out & ~ink] = (220, 0, 0)
rgb[out & ink] = (120, 120, 120)
Image.fromarray(rgb).save('scratch/arms/abusir_diff.png')
