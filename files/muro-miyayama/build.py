"""Rebuild File:室宮山古墳 復原図.png (a reconstruction plan of the Muro Miyayama kofun) by construction: black strokes
15 px wide (measured: 15.0 px of ink across every outline), some dashed (46 on, 14 off), and labels as real <text>.
Geometry: each element is given as rough vertices read off the drawing; every straight run is then fitted by least
squares to the PNG's stroke pixels near it, and vertices are the intersections of
neighbouring runs. Arcs are circles fitted the same way. Run from the repo root; `fit` refits."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

PNG = 'data_lake/downloads/muro-miyayama/muro-miyayama.png'
OUT = 'files/muro-miyayama/Muro Miyayama kofun reconstruction.svg'
PAR = 'files/muro-miyayama/geometry.json'
S = 2376 / 800  # the rough vertices below are in an 800 px wide view
DASH_FROM, DASH_TO = 862, 47  # px along the dyke's right side (from the top) and left side (from the bottom)

src = np.asarray(Image.open(PNG).convert('L'))
H, W = src.shape
dark = src < 160
# thin ink: the road's dashes, the lettering and the small rectangles, without the 15 px outlines
thin = dark & ~ndimage.binary_dilation(ndimage.binary_opening(dark, structure=np.ones((9, 9))), iterations=2)
# national route 309: two dashed lines (6 px, 24 on in a 41.6 px period), each three straight runs with sharp bends
# (near y 880 and y 1950); the east line's middle run lies under the moat's west side, which hides it, so it is that
# side's line. Rough points, full resolution, two per run; the ends are where the dashes start and stop
ROAD = {'west': [((410, 390), (595, 850)), ((598, 1000), (510, 1900)), ((497, 1990), (445, 2400))],
        'east': [((470, 390), (648, 850)), None, ((550, 1975), (492, 2400))]}
ROAD_Y = (382, 2395)
# burial chambers: rectangles 41 x 94 px outside, 5.5 px stroke with round joins, some dashed (18 on, 6 off round the
# outline); centre and long-axis angle measured from their ink (principal axes)
CHAMBERS = [((1161, 980), 90, False), ((1212, 980), 90, False), ((1158, 1471.5), 90, True), ((1226, 1471.5), 90, True),
            ((1611.1, 1430.3), 81.0, True), ((776, 1529.3), 95.5, False), ((420.9, 746.9), 102.1, True)]
CH_W, CH_L, CH_S = 41 - 5.5, 94 - 5.5, 5.5
# north arrow, measured along its axis: tip, direction, total length, shaft width, head length and base width
ARROW = dict(tip=(1508.1, 209.7), angle=-166.99, length=446, shaft=41.7, head=117, base=118)




# rough geometry, 800 px view. 'poly': straight runs; 'arc': circle through the given points, drawn between the ends
ROUGH = {
    'mound_front': ('poly', [(282, 385), (270, 395), (277, 440), (295, 455), (296, 469), (232, 470), (222, 555), (272, 575),
                             (268, 615), (537, 615), (518, 540), (580, 520), (568, 438), (497, 430), (492, 410),
                             (500, 400)]),
    'mound_arc': ('arc', [(282, 385), (405, 197), (500, 400)]),
    'moat_arc': ('arc', [(219, 300), (405, 148), (575, 305)]),
    'moat_sides': ('poly', [(577, 300), (617, 662), (190, 662), (219, 296)]),
    'dyke_arc': ('arc', [(185, 195), (405, 75), (640, 290)]),
    'dyke_right': ('poly', [(640, 290), (688, 735)]),
    'dyke_bottom': ('poly', [(688, 735), (108, 735)]),
    'dyke_left': ('poly', [(108, 735), (150, 320)]),
    'baizuka': ('poly', [(92, 177), (216, 203), (190, 325), (67, 298), (92, 177)]),
}


# labels: text and a rough box (x0, x1, y0, y1) around it in the 800 px view; the ink box inside is measured
LABELS = [('北', (462, 505, 45, 85), 'bold'), ('陪塚', (48, 128, 315, 348)), ('(ネコ塚)', (18, 142, 350, 385)),
          ('造出', (288, 347, 386, 414)), ('(想定)', (278, 354, 416, 447)), ('墳丘', (358, 442, 372, 418)),
          ('南張出', (453, 532, 456, 484)), ('(想定)', (453, 532, 485, 515)), ('北張出', (272, 348, 502, 530)),
          ('周濠', (530, 602, 622, 658)), ('周堤', (548, 620, 686, 722)), ('国道309号', (176, 300, 762, 788))]
FONT = "'Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', sans-serif"


def fit_labels(family):
    sys.path.insert(0, 'tools')
    from fit_text import fit
    out = []
    for t, (x0, x1, y0, y1), *wt in LABELS:
        weight = wt[0] if wt else 'normal'  # bold lettering is thicker than the thin-ink filter keeps
        sub = (dark if weight == 'bold' else thin)[int(y0 * S):int(y1 * S), int(x0 * S):int(x1 * S)]
        ys, xs = np.nonzero(sub)
        bx = (int(x0 * S) + xs.min(), int(x0 * S) + xs.max(), int(y0 * S) + ys.min(), int(y0 * S) + ys.max())
        out.append(dict(fit(t, bx, family, weight, canvas=(W, H)), text=t, weight=weight))
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


def fit_road(G):
    out = {}
    side = np.array(G['moat_sides']['poly'][-2:])  # the moat's west side, bottom to top
    for k, runs in ROAD.items():
        lines = [fit_line(thin, a, b, 12) if r else (side[0], (side[1] - side[0]) / np.hypot(*(side[1] - side[0])))
                 for r in runs for a, b in [r or (None, None)]]
        pts = []
        for (c0, d0), y in ((lines[0], ROAD_Y[0]),):
            pts.append(c0 + (y - c0[1]) / d0[1] * d0)
        pts += [meet(lines[i], lines[i + 1]) for i in range(len(lines) - 1)]
        c0, d0 = lines[-1]; pts.append(c0 + (ROAD_Y[1] - c0[1]) / d0[1] * d0)
        out[k] = {'poly': [p.tolist() for p in pts], 'offset': dash_phase(pts)}
    return out


def dash_phase(poly, on=24, period=41.6):
    """the dash offset that puts the most dash length on the PNG's thin ink"""
    P = np.asarray(poly, float)
    seg = np.diff(P, axis=0); L = np.hypot(*seg.T); cum = np.r_[0, np.cumsum(L)]
    t = np.arange(0, cum[-1], 0.5)
    i = np.clip(np.searchsorted(cum, t, side='right') - 1, 0, len(L) - 1)
    pts = P[i] + seg[i] * ((t - cum[i]) / L[i])[:, None]
    near = ndimage.binary_dilation(thin, iterations=1)
    hit = near[pts[:, 1].round().astype(int).clip(0, H - 1), pts[:, 0].round().astype(int).clip(0, W - 1)]
    best = max(np.arange(0, period, 0.2), key=lambda o: hit[((t + o) % period) < on].sum() - hit[((t + o) % period) >= on].sum())
    return float(best)


def chamber_poly(c, ang):
    u = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))]); v = np.array([-u[1], u[0]])
    c = np.asarray(c, float)
    return [c + su * u * CH_L / 2 + sv * v * CH_W / 2 for su, sv in ((-1, -1), (-1, 1), (1, 1), (1, -1), (-1, -1))]


def fit_chambers():
    return [{'poly': [p.tolist() for p in chamber_poly(c, a)], 'dashed': d,
             'offset': dash_phase(chamber_poly(c, a), 18, 24) if d else 0} for c, a, d in CHAMBERS]


def arrow_d():
    A = ARROW
    u = np.array([np.cos(np.radians(A['angle'])), np.sin(np.radians(A['angle']))]); v = np.array([-u[1], u[0]])
    tip = np.array(A['tip']); hb = tip - u * A['head']; tail = tip - u * A['length']
    pts = [tip, hb + v * A['base'] / 2, hb + v * A['shaft'] / 2, tail + v * A['shaft'] / 2,
           tail - v * A['shaft'] / 2, hb - v * A['shaft'] / 2, hb - v * A['base'] / 2]
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'


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
        G['road'] = fit_road(G)
        G['chambers'] = fit_chambers()
        G['labels'] = fit_labels(sys.argv[2] if len(sys.argv) > 2 else 'Meiryo')
        json.dump(G, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    G = json.load(open(PAR, encoding='utf8'))
    labels = G.pop('labels', [])
    road = G.pop('road', {})
    chambers = G.pop('chambers', [])
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
         *[f'<path stroke="#000000" stroke-width="6" stroke-dasharray="24 17.6" stroke-dashoffset="{r["offset"]:.1f}" d="M'
           + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r['poly']) + '"/>' for r in road.values()],
         f'<path stroke="#000000" stroke-width="15" d="{d}"/>',
         f'<path stroke="#000000" stroke-width="15" stroke-dasharray="46 14" d="{dash}"/>',
         '</g>',
         f'<path fill="#000000" d="{arrow_d()}"/>',
         '<g fill="none" stroke="#000000" stroke-width="5.5" stroke-linejoin="round">',
         *[f'<path' + (f' stroke-dasharray="18 6" stroke-dashoffset="{c["offset"]:.1f}"' if c['dashed'] else '')
           + ' d="M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in c['poly'][:-1]) + 'Z"/>' for c in chambers],
         '</g>']
    for q in labels:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 20 else ''
        fw = ' font-weight="bold"' if q.get('weight') == 'bold' else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls}{fw} font-family="{FONT}">{q["text"]}</text>')
    o.append('</svg>')
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
