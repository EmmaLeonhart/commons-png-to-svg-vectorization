"""Rebuild File:Agency for Cultural Affairs Organizational chart 20230327.png by construction from
measure.json (boxes, connectors) plus the grey "Tokyo office" area, measured here as a rectilinear
polygon, and every label as real <text>. The PNG's font (Office's Aptos) is not on Commons; the text is
set in Liberation Sans (Arial metrics), each line's size and position fitted to its ink box.
Run from the repo root after measure.py."""
import io, json
import numpy as np, resvg_py
from PIL import Image, ImageFont
from shapely.geometry import box as sbox
from shapely.ops import unary_union

PNG = 'data_lake/downloads/aca-org-chart/Agency for Cultural Affairs Organizational chart 20230327.png'
OUT = 'files/aca-org-chart/Agency for Cultural Affairs Organizational chart 20230327.svg'
ARIAL = r'C:\Windows\Fonts\arial.ttf'
ARIAL_B = r'C:\Windows\Fonts\arialbd.ttf'
FAMILY = "'Liberation Sans', Arial, Helvetica, sans-serif"
M = json.load(open('files/aca-org-chart/measure.json'))
W, H = M['W'], M['H']
TEXT = [
    ['Commissioner for', 'Cultural Affairs'], ['Secretary Strategy', 'Office'],
    ['Food Culture', 'Promotion', 'Headquarters'], ['Cultural Tourism', 'Promotion', 'Headquarters'],
    ['Deputy', 'Commissioner for', 'Cultural Affairs'], ['Deputy', 'Commissioner for', 'Cultural Affairs'],
    ['Director General,', 'Agency for Cultural', 'Affairs'], ['Councillor for', 'Cultural Properties'],
    ['Director General,', 'Agency for Cultural', 'Affairs'], ['Planning and', 'Coordination', 'Division'],
    ['Cultural Economy', 'and International', 'Affairs Division'], ['Policy Division'],
    ['Cultural Resources', 'Utilization Division'], ['Japanese Language', 'Division'], ['Copyright Division'],
    ['First Cultural', 'Properties Division'], ['Second Cultural', 'Properties Division'],
    ['Culture and', 'Creativity Division'], ['Religious Affairs', 'Division'], ['Arts and Culture', 'Division'],
    ['Life Culture', 'Collaboration', 'Division'], ['Cultural Locations', 'Division'],
]

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)

# grey area: grey pixels, closed over the lines and text standing on it, plus the boxes inside it
from scipy import ndimage
g = (a == 166).all(-1)
area = ndimage.binary_closing(g, structure=np.ones((9, 9)))
for b in M['boxes']:
    above = a[max(b['y'] - 4, 0), b['x'] + 10:b['x'] + b['w'] - 10]
    left = a[b['y'] + 10:b['y'] + b['h'] - 10, max(b['x'] - 4, 0)]
    if (above == 166).all(-1).mean() > 0.5 or (left == 166).all(-1).mean() > 0.5:
        area[b['y']:b['y'] + b['h'], b['x']:b['x'] + b['w']] = True
area = ndimage.binary_fill_holes(area)
rects = []
for y in range(H):
    xs = np.nonzero(area[y])[0]
    if len(xs):
        for r in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
            if len(r) > 20:
                rects.append(sbox(r[0], y, r[-1] + 1, y + 1))
poly = unary_union(rects).simplify(0.6)
grey_d = 'M' + ' '.join(f'{x:.0f},{y:.0f}' for x, y in poly.exterior.coords[:-1]) + 'Z'


def fit_line(t, bx, font_path):
    """size from the ink width, then centre x and baseline from the ink box."""
    x0, x1, y0, y1 = bx
    best = None
    for size in np.arange(14, 34, 0.05):
        l, tp, r, bt = ImageFont.truetype(font_path, size).getbbox(t, anchor='ls')
        err = abs((r - l) - (x1 - x0 + 1))
        if best is None or err < best[0]:
            best = (err, size, l, tp, r)
    _, size, l, tp, r = best
    return size, (x0 + x1 + 1) / 2 - (l + r) / 2 + (r - l) / 2 - (r - l) / 2, y0 - tp, l, r


texts, sizes = [], []
for b, lines in zip(M['boxes'], TEXT):
    assert len(b['lines']) == len(lines), (b, lines)
    for bx, t in zip(b['lines'], lines):
        size, cx, base, l, r = fit_line(t, bx, ARIAL)
        sizes.append(size)
        texts.append([t, bx, base])
body = float(np.median(sizes))  # one size for all labels, as in the PNG
out_t = []
f = ImageFont.truetype(ARIAL, body)
for t, (x0, x1, y0, y1), _ in texts:
    l, tp, r, bt = f.getbbox(t, anchor='ms')
    out_t.append(f'<text x="{(x0 + x1 + 1) / 2 - (l + r) / 2:.1f}" y="{y0 - tp:.1f}">{t}</text>')

# "Tokyo office": white bold text on the grey, top right
wt = (a.min(-1) > 240) & area
ys, xs = np.nonzero(wt[235:290, 1290:1510])
tx0, tx1, ty0 = xs.min() + 1290, xs.max() + 1290, ys.min() + 235
size_t, *_ = fit_line('Tokyo office', (tx0, tx1, ty0, ys.max() + 235), ARIAL_B)
fb = ImageFont.truetype(ARIAL_B, size_t)
l, tp, r, bt = fb.getbbox('Tokyo office', anchor='ms')
tokyo = (f'<text x="{(tx0 + tx1 + 1) / 2 - (l + r) / 2:.1f}" y="{ty0 - tp:.1f}" font-size="{size_t:.1f}" '
         f'font-weight="bold" fill="#fff">Tokyo office</text>')

boxes = ''.join(f'<rect x="{b["x"] + 1}" y="{b["y"] + 1}" width="{b["w"] - 2}" height="{b["h"] - 2}"/>' for b in M['boxes'])
segs = ''.join(f'M{s[1]},{s[3]}H{s[2]}' if s[0] == 'h' else f'M{s[1]},{s[2]}V{s[3]}' for s in M['segs'])
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>'
       f'<path id="tokyo-office" d="{grey_d}" fill="#a6a6a6"/>'
       f'<path id="connectors" d="{segs}" stroke="#000" stroke-width="2" fill="none"/>'
       f'<g id="boxes" fill="#fff" stroke="#000" stroke-width="2">{boxes}</g>'
       f'<g id="labels" font-family="{FAMILY}" font-size="{body:.1f}" fill="#000" text-anchor="middle">{"".join(out_t)}</g>'
       f'<g font-family="{FAMILY}" text-anchor="middle">{tokyo}</g></svg>')
open(OUT, 'w', encoding='utf8').write(svg)

r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[ARIAL, ARIAL_B], skip_system_fonts=True)))).convert('RGB')
o = np.asarray(r).astype(int)
diff = np.abs(o - a).max(-1) > 64
print('label size %.2f  Tokyo %.2f  grey vertices %d  pixels differing %.4f' % (body, size_t, len(poly.exterior.coords) - 1, diff.mean()))
c = np.concatenate([a, o], 1).astype(np.uint8)
Image.fromarray(c).save('scratch/arms/aca_cmp.png')
d = np.full_like(a, 255)
d[diff] = (220, 0, 0)
Image.fromarray(d.astype(np.uint8)).save('scratch/arms/aca_diff.png')
