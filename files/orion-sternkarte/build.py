"""Rebuild File:Orion-Sternkarte.png (a pp3 1.3 chart in the Wikipedia style of pp3's examples/wiki.pp3) from pp3's own
data (stars.dat = BSC, boundaries.dat = Davenhall & Leggett, lines.dat, nebulae.dat, milkyway.dat; MIT, in
data_lake/downloads/pp3/), in the azimuthal equidistant projection fitted by fit_projection.py, with wiki.pp3's colours.
Star radii follow the PNG's measured radius-by-magnitude medians; labels are real <text> placed at the PNG's labels.
Run from the repo root."""
import io, json, re, sys, zipfile
sys.path.insert(0, 'tools')
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/orion-sternkarte/Orion-Sternkarte.png'
OUT = 'files/orion-sternkarte/Orion-Sternkarte.svg'
PAR = 'files/orion-sternkarte/labels.json'
Z = zipfile.ZipFile('data_lake/downloads/pp3/pp3-1.3.3-win.zip')
dat = lambda f: Z.read('pp3-1.3.3-win/' + f).decode('latin1')
RA0, DEC0, SCALE, ROT, CX, CY = 5.5591, 2.715, 506.6733, -0.0045, 191.334, 229.3006
W, H = 381, 457
GRID, LINES, LABELS_C, BOUND, BOUND_HI, TEXTL, ECL, MW = (
    '#d6ebff', '#00cc00', '#0000ee', '#fff3aa', '#ffdd00', '#b3b3b3', '#cc2200', (0.5, 0.5, 1))
FAINTEST = 5.0
R_MAG = [(-1.5, 7.09), (0.0, 6.10), (0.5, 5.69), (1.5, 5.17), (2.0, 4.60), (2.5, 4.07), (3.0, 3.30), (3.5, 3.48),
         (4.0, 1.70), (4.5, 0.85), (5.0, 0.70)]  # per half-magnitude bin, calibrated so the discs' dark area matches the PNG's

# labels: (text, ink box x0, x1, y0, y1 in the PNG, kind); kind g = Greek letter, n = name, c = constellation (grey, bold)
LABELS = [('β', 192, 199, 6, 18, 'g'), ('ε', 53, 57, 16, 22, 'g'), ('M 35', 107, 129, 21, 29, 'n'),
          ('NGC 1746', 196, 245, 37, 45, 'n'), ('M 1', 168, 182, 45, 53, 'n'), ('μ', 76, 82, 57, 66, 'g'),
          ('η', 110, 116, 57, 66, 'g'), ('ζ', 170, 175, 61, 71, 'g'), ('ε', 335, 339, 70, 76, 'g'),
          ('γ', 355, 362, 98, 107, 'g'), ('γ', 62, 69, 101, 110, 'g'), ('Aldebaran', 254, 305, 100, 108, 'n'),
          ('θ²', 323, 336, 116, 127, 'g'), ('ξ', 24, 31, 121, 131, 'g'), ('λ', 192, 199, 152, 161, 'g'),
          ('γ', 216, 223, 182, 191, 'g'), ('π³', 266, 279, 185, 196, 'g'), ('Beteigeuze', 80, 137, 193, 203, 'n'),
          ('π⁴', 265, 279, 207, 218, 'g'), ('NGC 2238', 41, 89, 215, 223, 'n'), ('M 78', 132, 154, 249, 257, 'n'),
          ('δ', 182, 188, 241, 250, 'g'), ('ζ', 162, 167, 265, 275, 'g'), ('ε', 193, 197, 269, 275, 'g'),
          ('η', 218, 224, 270, 279, 'g'), ('M 42', 195, 217, 292, 302, 'n'), ('τ', 223, 230, 301, 308, 'g'),
          ('β', 254, 261, 303, 315, 'g'), ('ι', 186, 188, 312, 318, 'g'), ('κ', 169, 174, 336, 342, 'g'),
          ('Rigel', 202, 226, 331, 341, 'n'), ('ζ', 167, 172, 369, 379, 'g'), ('Sirius', 44, 72, 387, 395, 'n'),
          ('μ', 243, 250, 392, 401, 'g'), ('β', 94, 101, 407, 419, 'g'), ('α', 179, 187, 416, 422, 'g'),
          ('β', 208, 215, 420, 432, 'g'), ('M 41', 44, 65, 434, 442, 'n'), ('γ', 155, 161, 447, 456, 'g'),
          ('ε', 258, 262, 448, 454, 'g'),
          ('Zwillinge', 69, 130, 6, 20, 'c'), ('Orion', 174, 210, 122, 131, 'c'), ('Stier', 304, 335, 147, 160, 'c'),
          ('Einhorn', 79, 131, 332, 346, 'c'), ('Eridanus', 253, 312, 332, 341, 'c'), ('Hase', 183, 221, 361, 371, 'c'),
          ('Großer', 45, 105, 357, 367, 'c'), ('Hund', 60, 105, 372, 381, 'c')]
FAMILY = "Arial, 'Liberation Sans', 'DejaVu Sans', sans-serif"
# the seven nebulae the PNG draws (pp3 1.3's filter, not reproducible from 1.3.3's data): NGC numbers
NEBULAE = [1976, 2168, 2238, 1746, 2068, 1952, 2287]


def proj(ra, dec):
    l = np.radians((np.asarray(ra) - RA0) * 15); d = np.radians(np.asarray(dec)); d0 = np.radians(DEC0)
    cosc = np.clip(np.sin(d0) * np.sin(d) + np.cos(d0) * np.cos(d) * np.cos(l), -1, 1)
    c = np.arccos(cosc)
    k = np.where(c > 1e-9, c / np.sin(np.maximum(c, 1e-9)), 1)
    x = -np.cos(d) * np.sin(l) * k
    y = (np.cos(d0) * np.sin(d) - np.sin(d0) * np.cos(d) * np.cos(l)) * k
    r = np.radians(ROT)
    return CX + SCALE * (x * np.cos(r) - y * np.sin(r)), CY - SCALE * (x * np.sin(r) + y * np.cos(r))


def radius(m):
    ms, rs = zip(*R_MAG)
    return float(np.interp(m + 0.25, [q + 0.25 for q in ms], rs))


def inside(x, y, pad=20):
    return -pad < x < W + pad and -pad < y < H + pad


def poly_d(pts):
    return 'M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)


def curve(ras, decs):
    """project a densely sampled line, split where it leaves the view"""
    xs, ys = proj(ras, decs)
    out, cur = [], []
    for x, y in zip(xs, ys):
        if inside(x, y, 40):
            cur.append((x, y))
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return ''.join(poly_d(c) for c in out if len(c) > 1)


def fit_labels():
    """measure each label's tight ink box (its colour, inside the listed box) and fit Arial text to it"""
    from fit_text import fit
    a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
    blue = (a[..., 2] - a[..., 0] > 60) & (a[..., 2] - a[..., 1] > 60) & (a[..., 0] < 180)
    grey = (np.abs(a[..., 0] - a[..., 2]) < 12) & (a[..., 0] > 150) & (a[..., 0] < 215)
    out = []
    for t, x0, x1, y0, y1, kind in LABELS:
        m = (grey if kind == 'c' else blue)[y0:y1 + 1, x0:x1 + 1]
        if kind == 'c':  # the Milky Way's grey speckle: keep rows and columns of the word only
            m = m & (m.sum(1) >= 2)[:, None]
            m = m & (m.sum(0) >= 1)[None, :]
        ys, xs = np.nonzero(m)
        box = (x0 + xs.min(), x0 + xs.max(), y0 + ys.min(), y0 + ys.max())
        weight = 'bold' if kind == 'c' else 'normal'
        try:
            q = fit(t, box, 'Arial', weight, canvas=(W, H))
        except ValueError:  # a hairline glyph (ι) too faint to measure in regular weight
            weight = 'bold'
            q = fit(t, box, 'Arial', weight, canvas=(W, H))
        out.append(dict(text=t, kind=kind, weight=weight, box=[int(v) for v in box], **{k: q[k] for k in ('x', 'y', 'size', 'ls')}))
        print(t, box, out[-1])
    json.dump(out, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)


if len(sys.argv) > 1 and sys.argv[1] == 'fit':
    fit_labels()


# stars
L = dat('stars.dat').split('\n')
stars = []
for k in range(0, len(L) - 3, 4):
    f = L[k].split()
    stars.append(dict(hd=int(f[0]), hr=int(f[1]), ra=float(f[2]), dec=float(f[3]), mag=float(f[4]), fl=int(f[6]),
                      label=L[k + 1], con=L[k + 2]))
by_fl = {(s['con'], s['fl']): s for s in stars if s['fl']}
by_hd = {s['hd']: s for s in stars if s['hd']}
for i, s in enumerate(stars):
    s['i'] = i
    s['x'], s['y'] = (float(v) for v in proj(s['ra'], s['dec']))
shown = [s for s in stars if s['mag'] <= FAINTEST and inside(s['x'], s['y'], 8)]

# constellation lines: star to star, stopping short of each disc
toks = re.sub(r'#[^\n]*', '', dat('lines.dat')).replace(';', ' ; ').split()
paths, cur, i = [], [], 0
while i < len(toks):
    t = toks[i]
    if t == ';':
        paths.append(cur); cur = []; i += 1
    elif t == 'HD':
        cur.append(by_hd.get(int(toks[i + 1]))); i += 2
    else:
        cur.append(by_fl.get((t, int(toks[i + 1])))); i += 2
GAP = 1.6
pairs = {(s['i'], t['i']) for p in paths for s, t in zip(p, p[1:]) if s and t}
# the PNG's author drew a fuller figure than pp3 1.3.3's lines.dat: take every pair of shown stars the PNG joins by a
# green line (green along at least 85% of the stretch between the discs) as a line too
im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
green = (im[..., 1] - im[..., 0] > 50) & (im[..., 1] - im[..., 2] > 50)
gnear = np.zeros_like(green)
gnear[1:-1, 1:-1] = green[1:-1, 1:-1] | green[:-2, 1:-1] | green[2:, 1:-1] | green[1:-1, :-2] | green[1:-1, 2:]
# endpoints: drawn stars, or any star off the canvas (a line seen to stop at an undrawn star would show a gap)
cand = [s for s in stars if inside(s['x'], s['y'], 160) and (s['mag'] <= FAINTEST or (s['mag'] <= 5.5 and not inside(s['x'], s['y'], 0)))]
for ii, s in enumerate(cand):
    for t in cand[ii + 1:]:
        n = np.hypot(t['x'] - s['x'], t['y'] - s['y'])
        a, b = radius(s['mag']) + GAP + 1, radius(t['mag']) + GAP + 1
        if not 8 < n < 400 or n < a + b + 4:
            continue
        u = np.linspace(a / n, 1 - b / n, int(n))
        xs, ys = s['x'] + (t['x'] - s['x']) * u, s['y'] + (t['y'] - s['y']) * u
        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
        if ok.sum() > 6 and gnear[ys[ok].astype(int), xs[ok].astype(int)].mean() > 0.8:
            pairs.add((s['i'], t['i']))
pairs = {tuple(sorted(q)) for q in pairs}


# a line A-M-B also shows green between A and B, and close pairs of stars give near-parallel duplicates: accept pairs
# shortest first, skipping any whose stretch is already mostly covered by accepted lines
from PIL import ImageDraw
cover = Image.new('1', (W + 400, H + 400), 0)
dr = ImageDraw.Draw(cover)
kept = set()
for i, j in sorted(pairs, key=lambda q: np.hypot(stars[q[0]]['x'] - stars[q[1]]['x'], stars[q[0]]['y'] - stars[q[1]]['y'])):
    s, t = stars[i], stars[j]
    n = np.hypot(t['x'] - s['x'], t['y'] - s['y'])
    a, b = radius(s['mag']) + GAP + 1, radius(t['mag']) + GAP + 1
    u = np.linspace(a / n, 1 - b / n, max(2, int(n))) if n > a + b else np.array([0.5])
    xs, ys = s['x'] + (t['x'] - s['x']) * u + 200, s['y'] + (t['y'] - s['y']) * u + 200
    ok = (xs >= 200) & (xs < W + 200) & (ys >= 200) & (ys < H + 200)  # judge on the visible stretch only
    cv = np.asarray(cover)
    if ok.any() and cv[ys[ok].astype(int), xs[ok].astype(int)].mean() > 0.6:
        continue
    kept.add((i, j))
    dr.line([(s['x'] + 200, s['y'] + 200), (t['x'] + 200, t['y'] + 200)], fill=1, width=4)
pairs = kept
seg = []
for i, j in sorted(pairs):
    s, t = stars[i], stars[j]
    if True:
        if not (inside(s['x'], s['y']) or inside(t['x'], t['y'])):
            continue
        dx, dy = t['x'] - s['x'], t['y'] - s['y']; n = np.hypot(dx, dy)
        a, b = radius(s['mag']) + GAP, radius(t['mag']) + GAP
        if n > a + b:
            seg.append(f'M{s["x"] + dx * a / n:.2f},{s["y"] + dy * a / n:.2f}L{t["x"] - dx * b / n:.2f},{t["y"] - dy * b / n:.2f}')

# boundaries: Orion's own highlighted
bt = dat('boundaries.dat').split()
bnd, bnd_hi, i = [], [], 0
while i < len(bt):
    n = int(bt[i]); pts = np.array(bt[i + 1:i + 1 + 2 * n], float).reshape(-1, 2); i += 1 + 2 * n
    m = int(bt[i]); cons = bt[i + 1:i + 1 + m]; i += 1 + m
    ra = np.concatenate([np.linspace(pts[j, 0], pts[j + 1, 0], 8) for j in range(len(pts) - 1)])
    de = np.concatenate([np.linspace(pts[j, 1], pts[j + 1, 1], 8) for j in range(len(pts) - 1)])
    d = curve(ra, de)
    if d:
        (bnd_hi if 'ORI' in cons else bnd).append(d)

# grid: every hour of rectascension, every 10 degrees of declination
grid = [curve(np.full(400, h), np.linspace(-89, 89, 400)) for h in range(24)]
grid += [curve(np.linspace(0, 24, 2000), np.full(2000, dd)) for dd in range(-80, 90, 10)]
# ecliptic (J2000 obliquity)
lam = np.radians(np.linspace(0, 360, 3000)); eps = np.radians(23.4393)
ecl = curve((np.degrees(np.arctan2(np.sin(lam) * np.cos(eps), np.cos(lam))) % 360) / 15,
            np.degrees(np.arcsin(np.sin(lam) * np.sin(eps))))

# nebulae: circles, of their catalogue size (mean diameter) when larger than the fixed cluster symbol
t = dat('nebulae.dat').split()
neb = []
for i in range(0, len(t) - 10, 11):
    if int(t[i]) in NEBULAE:
        ra, de, d1, d2 = (float(v) for v in (t[i + 4], t[i + 5], t[i + 7], t[i + 8]))
        x, y = (float(v) for v in proj(ra, de))
        px = SCALE * np.pi / 180  # pixels per degree at the centre
        neb.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{max(3.6, (d1 + d2) / 2 * px / 2):.2f}"/>')
P = json.load(open(PAR, encoding='utf8'))
texts = []
for q in P:
    col = TEXTL if q['kind'] == 'c' else LABELS_C
    ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 3 else ''
    wt = ' font-weight="bold"' if q['weight'] == 'bold' else ''
    texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{wt}{ls} fill="{col}">{q["text"]}</text>')

# Milky Way: milkyway.dat's sky pixels (discs of the header radius, grey 1-255) splatted onto the pixel grid, lightly
# smoothed, and cut into bands of 8 grey levels; each band filled with white blended toward wiki.pp3's milky_way colour
# by 0.9 * grey / 255 (the PNG's tints, measured; grey below 6 is lost in the PNG's palette and left out)
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
mt = dat('milkyway.dat').split()
mrad = float(mt[0]) * SCALE * np.pi / 180
mv = np.array(mt[1:], float).reshape(-1, 3)
mx, my = proj(mv[:, 0], mv[:, 1])
keep = (mx > -10) & (mx < W + 10) & (my > -10) & (my < H + 10)
F = np.zeros((H + 20, W + 20))  # 10 px margin so bands run off the edge cleanly
gy, gx = np.mgrid[0:H + 20, 0:W + 20] + 0.5 - 10
for xi, yi, val in zip(mx[keep], my[keep], mv[keep, 2]):
    x0, x1 = int(max(0, xi + 10 - mrad - 1)), int(min(W + 20, xi + 10 + mrad + 2))
    y0, y1 = int(max(0, yi + 10 - mrad - 1)), int(min(H + 20, yi + 10 + mrad + 2))
    d = (gx[y0:y1, x0:x1] - xi) ** 2 + (gy[y0:y1, x0:x1] - yi) ** 2 <= mrad * mrad
    sub = F[y0:y1, x0:x1]; sub[d] = np.maximum(sub[d], val)
F = ndimage.gaussian_filter(F, 1.0)
levels = list(range(6, int(F.max()) + 8, 8))
cs = plt.contourf(gx[0], gy[:, 0], F, levels=levels + [999])
mw_paths = []


def ring_d(ring):
    from shapely.geometry import LineString
    pts = list(LineString(ring + [ring[0]]).simplify(0.4).coords)[:-1] if len(ring) > 3 else ring
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'


for lv, path in zip(levels, cs.get_paths()):
    if not len(path.vertices):
        continue
    d, ring = [], []
    for (vx, vy), c in zip(path.vertices, path.codes):  # rings, each simplified to 0.4 px
        if c == 1 and ring:
            d.append(ring_d(ring)); ring = []
        if c != 79:
            ring.append((vx, vy))
    if ring:
        d.append(ring_d(ring))
    tnt = 0.9 * (lv + 4) / 255
    col = '#%02x%02x%02x' % tuple(int(round(255 - tnt * (255 - 255 * c))) for c in MW)
    mw_paths.append(f'<path fill="{col}" fill-rule="evenodd" d="{"".join(d)}"/>')
plt.close('all')

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     *mw_paths,
     f'<path fill="none" stroke="{GRID}" stroke-width="1.2" d="{"".join(grid)}"/>',
     f'<path fill="none" stroke="{BOUND}" stroke-width="1.6" stroke-dasharray="6,3" d="{"".join(bnd)}"/>',
     f'<path fill="none" stroke="{BOUND_HI}" stroke-width="1.6" stroke-dasharray="6,3" d="{"".join(bnd_hi)}"/>',
     f'<path fill="none" stroke="{ECL}" stroke-width="1.5" stroke-dasharray="7,3" d="{ecl}"/>',
     f'<path fill="none" stroke="{LINES}" stroke-width="1.2" d="{"".join(seg)}"/>',
     '<g fill="#ffffff" stroke="#000000" stroke-width="1.3">' + ''.join(neb) + '</g>',
     '<g fill="#000000" stroke="#ffffff" stroke-width="1.6" paint-order="stroke">' +
     ''.join(f'<circle cx="{s["x"]:.2f}" cy="{s["y"]:.2f}" r="{radius(s["mag"]):.2f}"/>' for s in shown) + '</g>',
     f'<g font-family="{FAMILY}">', *texts, '</g>',
     '</svg>']
open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
print('wrote', OUT, len(shown), 'stars,', len(seg), 'line segments')
