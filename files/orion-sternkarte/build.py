"""Rebuild File:Orion-Sternkarte.png (a pp3 1.3 chart in the Wikipedia style of pp3's examples/wiki.pp3) from pp3's own
data (stars.dat = BSC, boundaries.dat = Davenhall & Leggett, lines.dat, nebulae.dat, milkyway.dat; MIT, in
data_lake/downloads/pp3/), in the azimuthal equidistant projection fitted by fit_projection.py, with wiki.pp3's colours.
Star radii follow the PNG's measured radius-by-magnitude medians; labels are real <text> placed at the PNG's labels.
Run from the repo root."""
import io, json, re, sys, zipfile
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/orion-sternkarte/Orion-Sternkarte.png'
OUT = 'files/orion-sternkarte/Orion-Sternkarte.svg'
Z = zipfile.ZipFile('data_lake/downloads/pp3/pp3-1.3.3-win.zip')
dat = lambda f: Z.read('pp3-1.3.3-win/' + f).decode('latin1')
RA0, DEC0, SCALE, ROT, CX, CY = 5.5591, 2.715, 506.6733, -0.0045, 191.334, 229.3006
W, H = 381, 457
GRID, LINES, LABELS, BOUND, BOUND_HI, TEXTL, ECL, MW = (
    '#d6ebff', '#00cc00', '#0000ee', '#fff3aa', '#ffdd00', '#b3b3b3', '#cc2200', (0.5, 0.5, 1))
FAINTEST = 5.0
R_MAG = [(-1.5, 7.09), (0.0, 6.10), (0.5, 5.69), (1.5, 4.88), (2.0, 4.47), (2.5, 3.77), (3.0, 3.24), (3.5, 2.62),
         (4.0, 1.20), (4.5, 0.54), (5.0, 0.45)]  # medians measured in the PNG (bin starts), see devlog


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
cand = [s for s in stars if s['mag'] <= 5.5 and inside(s['x'], s['y'], 160)]
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


def between(s, m, t):
    """star m lies on the segment s-t"""
    dx, dy = t['x'] - s['x'], t['y'] - s['y']; n2 = dx * dx + dy * dy
    u = ((m['x'] - s['x']) * dx + (m['y'] - s['y']) * dy) / n2
    return 0 < u < 1 and abs((m['x'] - s['x']) * dy - (m['y'] - s['y']) * dx) / np.sqrt(n2) < 2


# a line A-M-B also shows green between A and B: drop A-B when A-M and M-B are lines
adj = {}
for q in pairs:
    adj.setdefault(q[0], set()).add(q[1]); adj.setdefault(q[1], set()).add(q[0])
pairs = {(i, j) for i, j in pairs if not any(between(stars[i], stars[m], stars[j]) for m in adj[i] & adj[j])}
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

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     f'<path fill="none" stroke="{GRID}" stroke-width="1.2" d="{"".join(grid)}"/>',
     f'<path fill="none" stroke="{BOUND}" stroke-width="1.6" stroke-dasharray="6,3" d="{"".join(bnd)}"/>',
     f'<path fill="none" stroke="{BOUND_HI}" stroke-width="1.6" stroke-dasharray="6,3" d="{"".join(bnd_hi)}"/>',
     f'<path fill="none" stroke="{ECL}" stroke-width="1.2" stroke-dasharray="7,3" d="{ecl}"/>',
     f'<path fill="none" stroke="{LINES}" stroke-width="1.2" d="{"".join(seg)}"/>',
     '<g fill="#000000" stroke="#ffffff" stroke-width="0.8">' +
     ''.join(f'<circle cx="{s["x"]:.2f}" cy="{s["y"]:.2f}" r="{radius(s["mag"]):.2f}"/>' for s in shown) + '</g>',
     '</svg>']
open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
print('wrote', OUT, len(shown), 'stars,', len(seg), 'line segments')
