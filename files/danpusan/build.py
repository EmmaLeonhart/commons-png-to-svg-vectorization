"""Rebuild File:断夫山古墳 周濠復原図.png (Danpusan kofun, a reconstruction of its moat) by construction, as for
files/muro-miyayama: the mound outline and the estimated moat line are 15 px strokes (measured: 15.0 px of ink), the
present moat and the roads 4 px, the leader lines 10 px. Every straight run is a least-squares line through the PNG's stroke
pixels near rough vertices read off the drawing, vertices are the intersections of neighbouring runs, and the round
parts are fitted circles. Dash patterns and phases are measured; the labels are real <text>. Run from the repo root;
`fit` refits."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

PNG = 'data_lake/downloads/danpusan/danpusan.png'
OUT = 'files/danpusan/Danpusan kofun moat reconstruction.svg'
PAR = 'files/danpusan/geometry.json'
S = 2365 / 1000  # rough vertices below are in a 1000 px wide view

src = np.asarray(Image.open(PNG).convert('L'))
H, W = src.shape
dark = src < 128
thick = ndimage.binary_opening(dark, structure=np.ones((9, 9)))  # the 15 px strokes (and bold lettering)
thin = dark & ~ndimage.binary_dilation(thick, iterations=2)

# 'poly': straight runs (closed if the first point repeats); 'arc': circle through three points, drawn end to end
THICK = {
    'mound_arc': ('arc', [(410, 312), (499, 92), (596, 305)]),
    'mound_front': ('poly', [(410, 312), (373, 305), (348, 368), (378, 382), (303, 602), (352, 621), (605, 621),
                             (697, 577), (596, 305)]),
}
THIN = {
    'moat_now': ('poly', [(278, 640), (340, 215), (355, 170), (400, 110), (465, 50), (495, 50), (560, 75), (620, 130),
                          (655, 200), (665, 350), (695, 470), (720, 625), (278, 640)]),
}
# the estimated moat line: dashed 15 px; rough arc points, and the lower sides and the bottom as straight runs
EST_ARC = [(300, 205), (480, 27), (703, 215)]
EST_DASH = (46, 60)  # on, period (px)
# roads, thin dashed (16 on, 12 off): rough runs in the view, and where the dashes start and stop (full resolution,
# y for the north-south 伏見通, x for the east-west 市道). 市道 crosses the west side of 伏見通, which stops at its
# north edge and resumes below its south edge (that short run is fitted on its own)
ROADS = {'fushimi_w': ((808, 70), (775, 740)), 'fushimi_e': ((980, 80), (950, 740)),
         'shido_n': ((130, 656), (775, 633)), 'shido_s': ((135, 685), (770, 663))}
ROAD_ENDS = {'fushimi_w': (154, 1762), 'fushimi_e': (149, 1760), 'shido_n': (299, None), 'shido_s': (303, None)}
ROAD_DASH = (16, 28)
# north arrow, measured along its axis: tip, direction, total length, shaft width, head length and base width
ARROW = dict(tip=(2182.4, 152.3), angle=-55.19, length=302.8, shaft=41.8, head=124.8, base=125)
# leader lines (10 px, measured), rough runs in the view
LEADERS = [((225, 123), (318, 165)), ((217, 240), (330, 290))]
# labels: text, rough box (x0, x1, y0, y1) in the view, options; 'rot' = set rotated -90 degrees
LABELS = [('北', (900, 945, 18, 52), 'bold'), ('周濠', (130, 215, 92, 132), ''), ('推定線', (110, 235, 140, 180), ''),
          ('周濠', (130, 215, 210, 250), ''), ('(現在)', (110, 235, 257, 300), ''), ('造出', (362, 436, 327, 365), ''),
          ('墳丘', (442, 555, 367, 421), ''), ('市道', (133, 200, 657, 690), ''), ('伏見通', (858, 900, 305, 400), 'rot')]
FONT = "'Meiryo', 'Yu Gothic', 'Noto Sans CJK JP', sans-serif"
EST_SIDES = [((200, 690), (240, 500)), ((770, 500), (812, 690)), ((230, 718), (790, 718))]


def fit_line(M, a, b, band=12):
    ys, xs = np.nonzero(M)
    P = np.c_[xs, ys].astype(float)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    t = (P - a) @ u; s = (P - a) @ n
    Q = P[(np.abs(s) < band) & (t > 0.12 * L) & (t < 0.88 * L)]
    c = Q.mean(0)
    _, _, vt = np.linalg.svd(Q - c, full_matrices=False)
    return c, vt[0]


def meet(l1, l2):
    (c1, d1), (c2, d2) = l1, l2
    t = np.linalg.solve(np.array([d1, -d2]).T, c2 - c1)
    return c1 + t[0] * d1


def fit_circle(M, pts, band=14, below=20):
    pts = np.asarray(pts, float)
    (x1, y1), (x2, y2), (x3, y3) = pts
    A = np.array([[x2 - x1, y2 - y1], [x3 - x1, y3 - y1]]) * 2
    bb = np.array([x2 ** 2 - x1 ** 2 + y2 ** 2 - y1 ** 2, x3 ** 2 - x1 ** 2 + y3 ** 2 - y1 ** 2])
    c = np.linalg.solve(A, bb); r = np.hypot(*(pts[0] - c))
    ys, xs = np.nonzero(M)
    P = np.c_[xs, ys].astype(float)
    k = (np.abs(np.hypot(*(P - c).T) - r) < band) & (P[:, 1] < max(y1, y3) - below)
    return optimize.least_squares(lambda p: np.hypot(*(P[k] - p[:2]).T) - p[2], [*c, r]).x


def polyfit(M, pts, band):
    pts = [(x * S, y * S) for x, y in pts]
    closed = pts[0] == pts[-1]
    lines = [fit_line(M, pts[i], pts[i + 1], band) for i in range(len(pts) - 1)]
    if closed:
        v = [meet(lines[i - 1], lines[i]) for i in range(len(lines))]
    else:
        v = [np.asarray(pts[0])] + [meet(lines[i], lines[i + 1]) for i in range(len(lines) - 1)] + [np.asarray(pts[-1])]
        for j, (c, d) in ((0, lines[0]), (-1, lines[-1])):
            v[j] = c + ((v[j] - c) @ d) * d
    return {'poly': [list(map(float, p)) for p in v], 'closed': closed}


def refine():
    G = {}
    for group, M, band in ((THICK, thick, 14), (THIN, thin, 8)):
        for name, (kind, pts) in group.items():
            if kind == 'arc':
                p = [(x * S, y * S) for x, y in pts]
                G[name] = {'arc': list(map(float, fit_circle(M, p))), 'ends': [list(p[0]), list(p[-1])], 'mid': list(p[1])}
            else:
                G[name] = polyfit(M, pts, band)
    # estimated moat line, made regular: straight bottom; straight sides from the bottom corners, each tangent to a
    # circle over the top (fitted to the dashes: median distance 5 px, within the 15 px stroke's own spread)
    sides = [fit_line(thick, np.multiply(a, S), np.multiply(b, S), 16) for a, b in EST_SIDES]
    BL, BR = meet(sides[0], sides[2]), meet(sides[1], sides[2])
    ys, xs = np.nonzero(thick & ~near_drawn(G))
    P = np.c_[xs, ys].astype(float)
    P = P[(P[:, 0] < 840 * S) & (P[:, 1] < 700 * S) & ~((P[:, 0] < 260 * S) & (P[:, 1] < 300 * S))
          & ~((P[:, 0] > 420 * S) & (P[:, 0] < 560 * S) & (P[:, 1] > 350 * S))]
    c0 = fit_circle(thick, [(x * S, y * S) for x, y in EST_ARC], band=16, below=60)
    sol = optimize.least_squares(lambda p: est_dist(p, BL, BR, P), c0, loss='soft_l1', f_scale=5,
                                 bounds=([c0[0] - 300, c0[1] - 300, 0.6 * c0[2]], [c0[0] + 300, c0[1] + 300, 1.4 * c0[2]]))
    G['estimated'] = {'circle': list(map(float, sol.x)), 'bottom_left': BL.tolist(), 'bottom_right': BR.tolist(),
                      'tangents': [(Pt + u * L).tolist() for Pt, u, L in tangents(sol.x, BL, BR)]}
    G['roads'] = fit_roads()
    G['leaders'] = []
    for a_, b_ in LEADERS:
        c, d = fit_line(dark, np.multiply(a_, S), np.multiply(b_, S), 10)
        ys, xs = np.nonzero(dark); P = np.c_[xs, ys].astype(float)
        t = (P - c) @ d; sd = np.abs((P - c) @ np.array([-d[1], d[0]]))
        lo, hi = sorted([(np.multiply(a_, S) - c) @ d, (np.multiply(b_, S) - c) @ d])
        k = (sd < 5) & (t > lo - 40) & (t < hi + 40)
        G['leaders'].append([(c + t[k].min() * d).tolist(), (c + t[k].max() * d).tolist()])
    G['labels'] = fit_labels(sys.argv[2] if len(sys.argv) > 2 else 'Meiryo', G['roads'])
    G['estimated']['dash'] = EST_DASH
    # each piece: the period (scaled near 60 px, the dash keeping its share) and phase that best match the PNG's dashes;
    # the arc needs its own scale, being a regular stand-in for a slightly different drawn curve
    G['estimated']['pieces'] = []
    for _, P in est_pieces(G['estimated']):
        best = max(((dash_score(P, thick, EST_DASH[0] * k, EST_DASH[1] * k), k) for k in np.arange(0.94, 1.065, 0.005)))
        k = best[1]
        G['estimated']['pieces'].append({'scale': float(k), 'offset': dash_phase(P, thick, EST_DASH[0] * k, EST_DASH[1] * k)})
    return G


def near_drawn(G):
    """pixels near the mound outline as fitted, so the estimated line's dashes can be told apart"""
    from PIL import ImageDraw
    img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
    for k in THICK:
        g = G[k]
        if 'arc' in g:
            cx, cy, r = g['arc']; d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], outline=1, width=28)
        else:
            d.line([tuple(p) for p in g['poly']], fill=1, width=30)
    return np.asarray(img)


def tangents(p, BL, BR):
    cx, cy, r = p; c = np.array([cx, cy]); T = []
    for Pt, side in ((BL, -1), (BR, 1)):
        v = c - Pt; dl = np.hypot(*v); ang = np.arcsin(min(r / dl, 1)); base = np.arctan2(v[1], v[0])
        th = base + side * ang; u = np.array([np.cos(th), np.sin(th)])
        T.append((Pt, u, np.sqrt(max(dl ** 2 - r ** 2, 0))))
    return T


def est_dist(p, BL, BR, P):
    cx, cy, r = p
    T = tangents(p, BL, BR); tops = [Pt + u * L for Pt, u, L in T]
    out = np.where(P[:, 1] < max(tops[0][1], tops[1][1]) + 5, np.abs(np.hypot(P[:, 0] - cx, P[:, 1] - cy) - r), np.inf)
    for Pt, u, L in T:
        t = np.clip((P - Pt) @ u, 0, L); Q = Pt + t[:, None] * u
        out = np.minimum(out, np.hypot(*(P - Q).T))
    return out


def est_points(e, step=0.5):
    """points every `step` px along the estimated line, in drawing order (bottom-left, up, over, down, back)"""
    cx, cy, r = e['circle']
    BL, BR = np.array(e['bottom_left']), np.array(e['bottom_right']); TL, TR = map(np.array, e['tangents'])
    a0, a1 = np.arctan2(TL[1] - cy, TL[0] - cx), np.arctan2(TR[1] - cy, TR[0] - cx)
    if a1 < a0:
        a1 += 2 * np.pi
    arc = [np.array([cx + r * np.cos(t), cy + r * np.sin(t)]) for t in np.linspace(a0, a1, 600)]
    pts, out = [BL, *arc, BR, BL], []
    for p, q in zip(pts[:-1], pts[1:]):
        n = max(int(np.hypot(*(q - p)) / step), 1); out += [p + (q - p) * t for t in np.arange(n) / n]
    return np.array(out)


def est_pieces(e, step=0.5):
    """the estimated line as four pieces (west side, arc, east side, bottom): (svg path, sampled points)"""
    cx, cy, r = e['circle']
    BL, BR = np.array(e['bottom_left']), np.array(e['bottom_right']); TL, TR = map(np.array, e['tangents'])
    a0, a1 = np.arctan2(TL[1] - cy, TL[0] - cx), np.arctan2(TR[1] - cy, TR[0] - cx)
    if a1 < a0:
        a1 += 2 * np.pi
    seg = lambda p, q: np.array([p + (q - p) * t for t in np.arange(int(np.hypot(*(q - p)) / step)) / int(np.hypot(*(q - p)) / step)])
    n = int(r * (a1 - a0) / step)
    arc = np.array([[cx + r * np.cos(t), cy + r * np.sin(t)] for t in np.linspace(a0, a1, n)])
    f = lambda p: f'{p[0]:.1f},{p[1]:.1f}'
    return [(f'M{f(BL)}L{f(TL)}', seg(BL, TL)), (f'M{f(TL)}A{r:.1f},{r:.1f} 0 0 1 {f(TR)}', arc),
            (f'M{f(TR)}L{f(BR)}', seg(TR, BR)), (f'M{f(BR)}L{f(BL)}', seg(BR, BL))]


def dash_score(P, M, on, period, step=0.5):
    t = np.arange(len(P)) * step
    hit = M[P[:, 1].round().astype(int).clip(0, H - 1), P[:, 0].round().astype(int).clip(0, W - 1)]
    return max(hit[((t + o) % period) < on].sum() - hit[((t + o) % period) >= on].sum() for o in np.arange(0, period, 0.5))


def dash_phase(P, M, on, period, step=0.5):
    t = np.arange(len(P)) * step
    hit = M[P[:, 1].round().astype(int).clip(0, H - 1), P[:, 0].round().astype(int).clip(0, W - 1)]
    return float(max(np.arange(0, period, 0.25), key=lambda o: hit[((t + o) % period) < on].sum() - hit[((t + o) % period) >= on].sum()))


def fit_roads():
    L = {k: fit_line(thin, np.multiply(a, S), np.multiply(b, S), 8) for k, (a, b) in ROADS.items()}
    at_y = lambda l, y: l[0] + (y - l[0][1]) / l[1][1] * l[1]
    at_x = lambda l, x: l[0] + (x - l[0][0]) / l[1][0] * l[1]
    w, e, n, s_ = L['fushimi_w'], L['fushimi_e'], L['shido_n'], L['shido_s']
    w2 = fit_line(thin, np.multiply((777, 668), S), np.multiply((775, 742), S), 6)  # its own short run below 市道
    runs = [[at_y(w, ROAD_ENDS['fushimi_w'][0]), meet(w, n)], [meet(w2, s_), at_y(w2, ROAD_ENDS['fushimi_w'][1])],
            [at_y(e, ROAD_ENDS['fushimi_e'][0]), at_y(e, ROAD_ENDS['fushimi_e'][1])],
            [at_x(n, ROAD_ENDS['shido_n'][0]), meet(n, w)], [at_x(s_, ROAD_ENDS['shido_s'][0]), meet(s_, w)]]
    out = []
    for a, b in runs:
        n_ = int(np.hypot(*(b - a)) / 0.5); P = np.array([a + (b - a) * t for t in np.arange(n_) / n_])
        out.append({'line': [a.tolist(), b.tolist()], 'offset': dash_phase(P, ndimage.binary_dilation(thin), *ROAD_DASH)})
    return out


def arrow_d():
    A = ARROW
    u = np.array([np.cos(np.radians(A['angle'])), np.sin(np.radians(A['angle']))]); v = np.array([-u[1], u[0]])
    tip = np.array(A['tip']); hb = tip - u * A['head']; tail = tip - u * A['length']
    pts = [tip, hb + v * A['base'] / 2, hb + v * A['shaft'] / 2, tail + v * A['shaft'] / 2,
           tail - v * A['shaft'] / 2, hb - v * A['shaft'] / 2, hb - v * A['base'] / 2]
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'


def fit_labels(family, roads):
    sys.path.insert(0, 'tools')
    from fit_text import fit
    from PIL import ImageDraw
    img = Image.new('1', (W, H), 0); dr = ImageDraw.Draw(img)
    for r in roads:  # the road dashes run close to 市道: keep them out of the lettering's ink
        dr.line([tuple(r['line'][0]), tuple(r['line'][1])], fill=1, width=14)
    letters = thin & ~np.asarray(img)
    out = []
    for t, (x0, x1, y0, y1), opt in LABELS:
        sub = (dark if opt == 'bold' else letters)[int(y0 * S):int(y1 * S), int(x0 * S):int(x1 * S)]
        ys, xs = np.nonzero(sub)
        bx0, bx1, by0, by1 = int(x0 * S) + xs.min(), int(x0 * S) + xs.max(), int(y0 * S) + ys.min(), int(y0 * S) + ys.max()
        if opt == 'rot':  # fit horizontally in a box of swapped sides about the same centre, then rotate
            cx, cy, hw, hh = (bx0 + bx1) / 2, (by0 + by1) / 2, (by1 - by0) / 2, (bx1 - bx0) / 2
            q = fit(t, (cx - hw, cx + hw, cy - hh, cy + hh), family, 'normal', canvas=(W, H))
            q['rotate'] = [-90, cx, cy]
        else:
            q = fit(t, (bx0, bx1, by0, by1), family, 'bold' if opt == 'bold' else 'normal', canvas=(W, H))
        out.append(dict(q, text=t, weight='bold' if opt == 'bold' else 'normal'))
    return out


def arc_d(g):
    cx, cy, r = g['arc']
    ang = lambda x, y: np.arctan2(y - cy, x - cx)
    ends = [(cx + r * np.cos(ang(x, y)), cy + r * np.sin(ang(x, y))) for x, y in g['ends']]
    (x0, y0), (x1, y1) = ends
    a0, a1, am = ang(x0, y0), ang(x1, y1), ang(*g['mid'])
    delta, dm = (a1 - a0) % (2 * np.pi), (am - a0) % (2 * np.pi)
    sweep = 1 if dm < delta else 0
    large = int((delta if sweep else 2 * np.pi - delta) > np.pi)
    return f'M{x0:.1f},{y0:.1f}A{r:.1f},{r:.1f} 0 {large} {sweep} {x1:.1f},{y1:.1f}'


def poly_d(g):
    return 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in g['poly']) + ('Z' if g['closed'] else '')


def est_d(e):
    r = e['circle'][2]
    (lx, ly), (rx, ry) = e['tangents']
    (bx0, by0), (bx1, by1) = e['bottom_left'], e['bottom_right']
    return f'M{bx0:.1f},{by0:.1f}L{lx:.1f},{ly:.1f}A{r:.1f},{r:.1f} 0 0 1 {rx:.1f},{ry:.1f}L{bx1:.1f},{by1:.1f}Z'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        json.dump(refine(), open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    G = json.load(open(PAR, encoding='utf8'))
    est = G.pop('estimated')
    G.setdefault('roads', []); G.setdefault('leaders', []); G.setdefault('labels', [])
    thick_d = ''.join(arc_d(G[k]) if 'arc' in G[k] else poly_d(G[k]) for k in THICK)
    thin_d = ''.join(poly_d(G[k]) for k in THIN)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         '<g fill="none" stroke="#000000" stroke-linejoin="miter">',
         f'<path stroke-width="4" d="{thin_d}"/>',
         f'<path stroke-width="15" d="{thick_d}"/>',
         # round caps: the visible 46 px dash is 31 px plus a 7.5 px cap at each end; each piece has its own phase,
         # as in the PNG
         *[f'<path stroke-width="15" stroke-linecap="round" stroke-dasharray="{est["dash"][0] * q["scale"] - 15:.2f} '
           f'{(est["dash"][1] - est["dash"][0]) * q["scale"] + 15:.2f}" stroke-dashoffset="{q["offset"] - 7.5:.2f}" d="{d}"/>'
           for (d, _), q in zip(est_pieces(est), est['pieces'])],
         *[f'<path stroke-width="4" stroke-dasharray="{ROAD_DASH[0]} {ROAD_DASH[1] - ROAD_DASH[0]}" '
           f'stroke-dashoffset="{r["offset"]:.2f}" d="M{r["line"][0][0]:.1f},{r["line"][0][1]:.1f}L{r["line"][1][0]:.1f},{r["line"][1][1]:.1f}"/>'
           for r in G['roads']],
         f'<path stroke-width="10" d="' + ''.join(f'M{a_[0]:.1f},{a_[1]:.1f}L{b_[0]:.1f},{b_[1]:.1f}' for a_, b_ in G['leaders']) + '"/>',
         '</g>',
         f'<path fill="#000000" d="{arrow_d()}"/>']
    for q in G['labels']:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 20 else ''
        fw = ' font-weight="bold"' if q['weight'] == 'bold' else ''
        tr = f' transform="rotate({q["rotate"][0]} {q["rotate"][1]:.1f} {q["rotate"][2]:.1f})"' if 'rotate' in q else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls}{fw}{tr} font-family="{FONT}">{q["text"]}</text>')
    o += ['</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
