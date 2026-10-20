"""Rebuild File:室宮山古墳 復原図.png (a reconstruction plan of the Muro Miyayama kofun) by construction: black strokes
15 px wide (measured: 15.0 px of ink across every outline), some dashed (46 on, 14 off), and labels as real <text>.
Geometry: each element is given as rough vertices read off the drawing; every straight run is then fitted by least
squares to the PNG's stroke pixels near it, and vertices are the intersections of
neighbouring runs. Arcs are circles fitted the same way. Run from the repo root; `fit` refits."""
import json, sys
import numpy as np
from PIL import Image
from scipy import optimize

PNG = 'data_lake/downloads/muro-miyayama/muro-miyayama.png'
OUT = 'files/muro-miyayama/Muro Miyayama kofun reconstruction.svg'
PAR = 'files/muro-miyayama/geometry.json'
S = 2376 / 800  # the rough vertices below are in an 800 px wide view
DASH_FROM, DASH_TO = 862, 47  # px along the dyke's right side (from the top) and left side (from the bottom)

src = np.asarray(Image.open(PNG).convert('L'))
H, W = src.shape
dark = src < 160




# rough geometry, 800 px view. 'poly': straight runs; 'arc': circle through the given points, drawn between the ends
ROUGH = {
    'mound_front': ('poly', [(282, 385), (270, 395), (277, 440), (296, 462), (232, 470), (222, 555), (272, 575),
                             (268, 615), (537, 615), (518, 540), (580, 520), (568, 438), (497, 430), (492, 410),
                             (500, 400)]),
    'mound_arc': ('arc', [(282, 385), (405, 197), (500, 400)]),
    'moat_arc': ('arc', [(237, 305), (405, 148), (575, 305)]),
    'moat_sides': ('poly', [(577, 300), (617, 662), (190, 662), (237, 300)]),
    'dyke_arc': ('arc', [(185, 195), (405, 75), (640, 290)]),
    'dyke_right': ('poly', [(640, 290), (688, 735)]),
    'dyke_bottom': ('poly', [(688, 735), (108, 735)]),
    'dyke_left': ('poly', [(108, 735), (150, 320)]),
    'baizuka': ('poly', [(92, 177), (216, 203), (190, 325), (67, 298), (92, 177)]),
}


# labels: text and a rough box (x0, x1, y0, y1) around it in the 800 px view; the ink box inside is measured
LABELS = [('北', (468, 500, 52, 80)), ('陪塚', (48, 128, 315, 348)), ('(ネコ塚)', (18, 142, 350, 385)),
          ('造出', (288, 347, 386, 414)), ('(想定)', (278, 354, 416, 447)), ('墳丘', (358, 442, 372, 418)),
          ('南張出', (453, 532, 456, 484)), ('(想定)', (453, 532, 485, 515)), ('北張出', (272, 348, 502, 530)),
          ('周濠', (530, 602, 622, 658)), ('周堤', (548, 620, 686, 722)), ('国道309号', (176, 300, 762, 788))]
FONT = "'Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', sans-serif"


def fit_labels(family):
    sys.path.insert(0, 'tools')
    from fit_text import fit
    out = []
    for t, (x0, x1, y0, y1) in LABELS:
        sub = dark[int(y0 * S):int(y1 * S), int(x0 * S):int(x1 * S)]
        ys, xs = np.nonzero(sub)
        bx = (int(x0 * S) + xs.min(), int(x0 * S) + xs.max(), int(y0 * S) + ys.min(), int(y0 * S) + ys.max())
        out.append(dict(fit(t, bx, family, 'normal', canvas=(W, H)), text=t))
    return out


def fit_line(M, a, b, band=16):
    """least-squares line through the stroke pixels within `band` of segment a-b, ends excluded"""
    ys, xs = np.nonzero(M)
    P = np.c_[xs, ys].astype(float)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    t = (P - a) @ u; s = (P - a) @ n
    k = (np.abs(s) < band) & (t > 0.12 * L) & (t < 0.88 * L)
    Q = P[k]
    c = Q.mean(0)
    _, _, vt = np.linalg.svd(Q - c)
    return c, vt[0]


def meet(l1, l2):
    (c1, d1), (c2, d2) = l1, l2
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * d1


def fit_circle(M, pts, band=16):
    pts = np.asarray(pts, float)
    # circle through three rough points, then least squares on the stroke pixels near it
    (x1, y1), (x2, y2), (x3, y3) = pts
    A = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]]) * 2
    bb = np.array([x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2, x3 ** 2 - x1 ** 2 + y3 ** 2 - y1 ** 2])
    c = np.linalg.solve(A, bb); r = np.hypot(*(pts[0] - c))
    ys, xs = np.nonzero(M)
    P = np.c_[xs, ys].astype(float)
    k = (np.abs(np.hypot(*(P - c).T) - r) < band) & (P[:, 1] < max(y1, y3) - 20)
    sol = optimize.least_squares(lambda p: np.hypot(*(P[k] - p[:2]).T) - p[2], [*c, r])
    return sol.x


def refine():
    M = dark
    G = {}
    for name, (kind, pts) in ROUGH.items():
        pts = [(x * S, y * S) for x, y in pts]
        if kind == 'arc':
            G[name] = {'arc': list(map(float, fit_circle(M, pts))), 'ends': [list(pts[0]), list(pts[-1])], 'mid': list(pts[1])}
            continue
        closed = pts[0] == pts[-1]
        lines = [fit_line(M, pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        if closed:
            v = [meet(lines[i - 1], lines[i]) for i in range(len(lines))]
        else:
            v = [np.asarray(pts[0])] + [meet(lines[i], lines[i + 1]) for i in range(len(lines) - 1)] + [np.asarray(pts[-1])]
            # open ends: project the rough end onto its fitted line
            for j, li in ((0, lines[0]), (-1, lines[-1])):
                c, d = li
                v[j] = c + ((v[j] - c) @ d) * d
        G[name] = {'poly': [list(map(float, p)) for p in v], 'closed': closed}
    return G


def arc_d(g):
    cx, cy, r = g['arc']
    ends = []
    for x, y in g['ends']:  # project the rough ends onto the circle
        a = np.arctan2(y - cy, x - cx); ends.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    (x0, y0), (x1, y1) = ends
    # flags from the arc's middle point: SVG angles grow clockwise (y down)
    ang = lambda x, y: np.arctan2(y - cy, x - cx)
    a0, a1, am = ang(x0, y0), ang(x1, y1), ang(*g['mid'])
    delta, dm = (a1 - a0) % (2 * np.pi), (am - a0) % (2 * np.pi)
    sweep = 1 if dm < delta else 0
    large = int((delta if sweep else 2 * np.pi - delta) > np.pi)
    return f'M{x0:.1f},{y0:.1f}A{r:.1f},{r:.1f} 0 {large} {sweep} {x1:.1f},{y1:.1f}'


def poly_d(g):
    p = g['poly']
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in p) + ('Z' if g['closed'] else '')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        G = refine()
        G['labels'] = fit_labels(sys.argv[2] if len(sys.argv) > 2 else 'Meiryo')
        json.dump(G, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    G = json.load(open(PAR, encoding='utf8'))
    labels = G.pop('labels', [])
    # the dyke's lower right side, bottom and lower-left corner are dashed (46 on, 14 off, continuous round the
    # corners): split them off the solid runs
    R, B, L = (np.array(G.pop(k)['poly']) for k in ('dyke_right', 'dyke_bottom', 'dyke_left'))
    at = lambda P, dist: P[0] + (P[1] - P[0]) / np.hypot(*(P[1] - P[0])) * dist
    r_split, l_split = at(R, DASH_FROM), at(L, DASH_TO)
    corner_r, corner_l = meet((R[0], R[1] - R[0]), (B[0], B[1] - B[0])), meet((B[0], B[1] - B[0]), (L[0], L[1] - L[0]))
    G['dyke_right'] = {'poly': [R[0].tolist(), r_split.tolist()], 'closed': False}
    G['dyke_left'] = {'poly': [l_split.tolist(), L[1].tolist()], 'closed': False}
    dash = 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in (r_split, corner_r, corner_l, l_split))
    d = ''.join(arc_d(g) if 'arc' in g else poly_d(g) for g in G.values())
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         '<g fill="none" stroke-linejoin="miter">',
         f'<path stroke="#000000" stroke-width="15" d="{d}"/>',
         f'<path stroke="#000000" stroke-width="15" stroke-dasharray="46 14" d="{dash}"/>',
         '</g>']
    for q in labels:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 20 else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} font-family="{FONT}">{q["text"]}</text>')
    o.append('</svg>')
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
