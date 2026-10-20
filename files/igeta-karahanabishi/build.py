"""Rebuild File:井桁に唐花菱.png (igeta ni karahanabishi, a kamon) by construction, not tracing. In a square (u, v) space
the crest is regular: the frame is a 井 of four bars, its hole a square, and the karahana four petals, each the union of a
tip circle, two side-lobe circles and their hull to the centre, clipped to its quadrant. An affine map (u, v) → image
squashes it into the lozenge. The ring, the midribs and the separators are strokes of constant width in image space,
as in the PNG. The few parameters are fitted to the PNG's white mask; `fit` refits. Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity

PNG = 'data_lake/downloads/igeta-karahanabishi/igeta-karahanabishi.png'
OUT = 'files/igeta-karahanabishi/Igeta ni karahanabishi.svg'
PAR = 'files/igeta-karahanabishi/params.json'
BG, FG = '#00081a', '#f3f3f2'
DS = 4  # fitting resolution: 1/4 of the PNG

src = np.asarray(Image.open(PNG).convert('L'))
N = src.shape[0]
white = src[::DS, ::DS] > 128


def to_img(g, cx, cy, A, B):
    # (u, v) → (cx + A(u + v), cy + B(v - u))
    return affinity.affine_transform(g, [A, A, -B, B, cx, cy])


def frame(c, t, L):
    bars = [box(-L, s * c - t / 2, L, s * c + t / 2) for s in (-1, 1)] + \
           [box(s * c - t / 2, -L, s * c + t / 2, L) for s in (-1, 1)]
    h = c - t / 2
    return unary_union(bars), box(-h, -h, h, h)


def flower(d1, r1, d2, e2, r2, h):
    out = []
    for k in range(4):
        a = np.radians(45 + 90 * k)
        d, n = np.array([np.cos(a), np.sin(a)]), np.array([-np.sin(a), np.cos(a)])
        tip = Point(*(d1 * d)).buffer(r1, 128)
        sides = [Point(*(d2 * d + s * e2 * n)).buffer(r2, 128) for s in (-1, 1)]
        body = unary_union(sides + [Point(0, 0).buffer(1e-3)]).convex_hull
        q = box(0, 0, h, h)
        q = affinity.rotate(q, 90 * k, origin=(0, 0))
        out.append(unary_union([tip, body, *sides]).intersection(q))
    return unary_union(out)


def strokes(P, f):
    cx, cy, A, B = P['aff']
    w, R, Lh, Lv = P['w'], P['R'], P['Lh'], P['Lv']
    h = P['c'] - P['t'] / 2
    seps = [to_img(LineString([(0, 0), (s * h, 0)]), cx, cy, A, B) for s in (-1, 1)] + \
           [to_img(LineString([(0, 0), (0, s * h)]), cx, cy, A, B) for s in (-1, 1)]
    ribs = [LineString([(cx - Lh, cy), (cx + Lh, cy)]), LineString([(cx, cy - Lv), (cx, cy + Lv)])]
    return seps, ribs, Point(cx, cy).buffer(R, 128)


def model(P):
    cx, cy, A, B = P['aff']
    fr, hole = frame(P['c'], P['t'], P['L'])
    fl = flower(*P['fl'], P['c'] - P['t'] / 2)
    seps, ribs, ring = strokes(P, None)
    w = P['w']
    white = to_img(fr.difference(hole), cx, cy, A, B).union(to_img(fl, cx, cy, A, B))
    dark = unary_union([s.buffer(w / 2, cap_style=2) for s in seps] + [r.buffer(w / 2) for r in ribs]
                       + [ring.exterior.buffer(w / 2)]).intersection(to_img(hole, cx, cy, A, B))
    return white.difference(dark).union(ring.buffer(-w / 2))


def raster(g):
    img = Image.new('1', (N // DS, N // DS), 0); d = ImageDraw.Draw(img)
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.geom_type != 'Polygon' or q.is_empty:
            continue
        d.polygon([(x / DS, y / DS) for x, y in q.exterior.coords], fill=1)
        for r in q.interiors:
            d.polygon([(x / DS, y / DS) for x, y in r.coords], fill=0)
    return np.asarray(img)


def iou(g, region=None):
    m = raster(g); t = white
    if region is not None:
        m, t = m & region, t & region
    return (m & t).sum() / (m | t).sum()


def unpack_frame(p):
    return {'aff': list(p[:4]), 'c': p[4], 't': p[5], 'L': p[6]}


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        # frame: the white mask outside the hole
        ys, xs = np.nonzero(white)
        cx0, cy0 = (xs.min() + xs.max()) / 2 * DS, (ys.min() + ys.max()) / 2 * DS
        p0 = [cx0, cy0, (xs.max() - xs.min()) * DS / 2, (ys.max() - ys.min()) * DS / 2, 0.42, 0.18, 0.5]

        def lf(p):
            P = unpack_frame(p)
            fr, hole = frame(P['c'], P['t'], P['L'])
            g = to_img(fr.difference(hole), *P['aff'])
            out = ~raster(to_img(hole, *P['aff']))
            return 1 - iou(g, out)
        best = min((lf(p0[:4] + [c, t, L]), p0[:4] + [c, t, L]) for c in (0.3, 0.38, 0.46) for t in (0.12, 0.2, 0.28)
                   for L in (0.45, 0.55, 0.65))
        r = optimize.minimize(lf, best[1], method='Nelder-Mead', options={'maxiter': 3000, 'xatol': 1e-4, 'fatol': 1e-8})
        P = unpack_frame(r.x)
        print('frame IoU %.4f' % (1 - r.fun), P)
        # strokes measured from the PNG along the centre lines; flower fitted inside the hole
        P.update(w=14.0, R=80.0, Lh=288.0, Lv=290.0)
        hole_m = raster(to_img(frame(P['c'], P['t'], P['L'])[1], *P['aff']))
        h = P['c'] - P['t'] / 2

        def lfl(q):
            P2 = dict(P, fl=list(q[:5]), w=q[5], R=q[6], Lh=q[7], Lv=q[8])
            return 1 - iou(model(P2), hole_m)
        q0 = [0.75 * h * 1.41, 0.17 * h, 0.5 * h * 1.41, 0.25 * h, 0.22 * h, 14, 80, 288, 290]
        r = optimize.minimize(lfl, q0, method='Nelder-Mead', options={'maxiter': 4000, 'xatol': 1e-4, 'fatol': 1e-8})
        q = r.x
        P.update(fl=list(q[:5]), w=q[5], R=q[6], Lh=q[7], Lv=q[8])
        print('flower IoU (in the hole) %.4f' % (1 - r.fun))
        json.dump({k: (list(map(float, v)) if isinstance(v, list) else float(v)) for k, v in P.items()}, open(PAR, 'w'), indent=1)
    P = json.load(open(PAR))
    g = model(P)
    print('whole IoU %.4f' % iou(g))
    cx, cy, A, B = P['aff']
    fr, hole = frame(P['c'], P['t'], P['L'])
    fl = flower(*P['fl'], P['c'] - P['t'] / 2)
    seps, ribs, ring = strokes(P, None)
    pd = lambda g: ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords[:-1]) + 'Z'
                           for q in (g.geoms if hasattr(g, 'geoms') else [g]) for r in [q.exterior, *q.interiors])
    ld = lambda l: 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in l.coords)
    hd = to_img(hole, cx, cy, A, B)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{N}" height="{N}" viewBox="0 0 {N} {N}">',
         f'<rect width="{N}" height="{N}" fill="{BG}"/>',
         f'<path fill="{FG}" fill-rule="evenodd" d="{pd(to_img(fr.difference(hole), cx, cy, A, B))}"/>',
         f'<clipPath id="hole"><path d="{pd(hd)}"/></clipPath>',
         f'<g clip-path="url(#hole)">',
         f'<path fill="{FG}" d="{pd(to_img(fl, cx, cy, A, B))}"/>',
         f'<path fill="none" stroke="{BG}" stroke-width="{P["w"]:.1f}" d="{"".join(ld(s) for s in seps)}"/>',
         f'<path fill="none" stroke="{BG}" stroke-width="{P["w"]:.1f}" stroke-linecap="round" d="{"".join(ld(r) for r in ribs)}"/>',
         f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{P["R"]:.1f}" fill="{FG}" stroke="{BG}" stroke-width="{P["w"]:.1f}"/>',
         '</g>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
