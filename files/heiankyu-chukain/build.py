"""Rebuild File:平安宮 中和院位置.png (a plan of the Heian Palace marking the Chūwa-in) by construction. The plan is
axis-aligned: every wall and block outline is a horizontal or vertical run of black pixels, so each is read as a
rectangle from the PNG's row and column runs (runs at least 8 px long, merged across consecutive rows; the labels are masked out first). The grey
precincts (内裏, 朝堂院) are dithered in two greys in the PNG; each is one flat fill at the mean grey, its region
decomposed into rectangles the same way. The two leader lines are straight lines
through their leftover ink; the labels are real <text> fitted to the PNG's lettering. Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage

PNG = 'data_lake/downloads/heiankyu-chukain/heiankyu-chukain.png'
OUT = 'files/heiankyu-chukain/Heian palace Chuwain.svg'
PAR = 'files/heiankyu-chukain/geometry.json'

a = np.asarray(Image.open(PNG).convert('L')).astype(int)
H, W = a.shape
V = 2151 / 700  # label boxes below are read off a 700 px wide view
# labels as drawn (the PNG's own wording), with a rough box (x0, x1, y0, y1) in the 700 px view
LABELS = [('宴の松原', (176, 268, 343, 369)), ('真', (276, 299, 366, 387)), ('言', (276, 299, 387, 407)),
          ('院', (276, 299, 408, 430)), ('木工内候', (243, 347, 443, 465)), ('中和院', (363, 439, 443, 465)),
          ('内裏', (411, 462, 343, 369)), ('豊楽院', (216, 285, 568, 594)), ('朝堂院', (318, 390, 568, 594))]
FONT = "'Meiryo', 'IPAGothic', 'Noto Sans CJK JP', sans-serif"


def runs(M, minlen):
    """rectangles (x0, y0, x1, y1), exclusive ends, from the row runs of M at least minlen long, merged downwards"""
    open_, done = {}, []
    for y in range(M.shape[0]):
        r = np.diff(np.r_[0, M[y].astype(np.int8), 0]); s, e = np.nonzero(r == 1)[0], np.nonzero(r == -1)[0]
        cur = {}
        for x0, x1 in zip(s.tolist(), e.tolist()):
            if x1 - x0 < minlen:
                continue
            key = next((k for k in open_ if abs(k[0] - x0) <= 2 and abs(k[1] - x1) <= 2), None)
            if key is not None:
                cur[key] = open_.pop(key)
            else:
                cur[(x0, x1)] = y
        for (x0, x1), y0 in open_.items():
            done.append((x0, y0, x1, y))
        open_ = cur
    done += [(x0, y0, x1, M.shape[0]) for (x0, x1), y0 in open_.items()]
    return done


def label_mask():
    m = np.zeros((H, W), bool)
    for _, (x0, x1, y0, y1) in LABELS:
        m[int(y0 * V):int(y1 * V), int(x0 * V):int(x1 * V)] = True
    return m


def fit(family):
    sys.path.insert(0, 'tools')
    from fit_text import fit as fit_text
    lab = label_mask()
    dark = (a < 128) & ~lab
    h = runs(dark, 8)
    v = [(y0, x0, y1, x1) for x0, y0, x1, y1 in runs(dark.T, 8)]
    # the precincts are a two-grey dither: one flat fill at its mean grey over the closed region
    m = (a > 128) & (a < 250)
    m = ndimage.binary_fill_holes(ndimage.binary_opening(ndimage.binary_closing(m, iterations=2), iterations=3))
    g = int(round(a[m & (a > 128) & (a < 250)].mean()))
    greys = {'#%02x%02x%02x' % (g, g, g): runs(m, 1)}
    # leader lines: the diagonal ink left over, each a straight 2 px line between the ends of its principal axis
    covered = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in h + v:
        covered[y0:y1, x0:x1] = True
    left = dark & ~ndimage.binary_dilation(covered, iterations=2)
    cl, n = ndimage.label(left, structure=np.ones((3, 3)))
    leaders = []
    near_label = ndimage.binary_dilation(lab, iterations=12)  # a leader stops short of its label's lettering
    for i in range(1, n + 1):
        ys, xs = np.nonzero(cl == i)
        if len(xs) < 60:
            continue
        P = np.c_[xs, ys].astype(float) + 0.5; c = P.mean(0)
        _, _, vt = np.linalg.svd(P - c, full_matrices=False); t = (P - c) @ vt[0]
        u = vt[0]
        ends = []
        for sgn, t0 in ((-1, t.min()), (1, t.max())):  # extend along the line while the PNG has ink under it
            k, gap = t0, 0
            while gap <= 12:
                k += sgn
                x, y = (c + k * u).round().astype(int)
                if not (0 <= x < W and 0 <= y < H) or near_label[y, x]:
                    break
                gap = 0 if (a[y - 1:y + 2, x - 1:x + 2] < 128).any() else gap + 1
            ends.append(c + (k - sgn * gap) * u)
        if not any(np.hypot(*(np.array(e) - ends[0])) < 20 for l in leaders for e in l):
            leaders.append([e.tolist() for e in ends])
    labels = []
    for t, (x0, x1, y0, y1) in LABELS:
        sub = (a < 128)[int(y0 * V):int(y1 * V), int(x0 * V):int(x1 * V)]
        ys, xs = np.nonzero(sub)
        bx = (int(x0 * V) + xs.min(), int(x0 * V) + xs.max(), int(y0 * V) + ys.min(), int(y0 * V) + ys.max())
        labels.append(dict(fit_text(t, bx, family, 'normal', canvas=(W, H)), text=t))
    return {'lines': h + v, 'greys': greys, 'leaders': leaders, 'labels': labels}


def rect_d(rs):
    return ''.join(f'M{x0},{y0}H{x1}V{y1}H{x0}Z' for x0, y0, x1, y1 in rs)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        json.dump(fit(sys.argv[2] if len(sys.argv) > 2 else 'MS Gothic'), open(PAR, 'w', encoding='utf8'), ensure_ascii=False)
    G = json.load(open(PAR, encoding='utf8'))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    o += [f'<path fill="{c}" d="{rect_d(rs)}"/>' for c, rs in G['greys'].items()]
    o.append(f'<path fill="#000000" d="{rect_d(G["lines"])}"/>')
    o.append('<path fill="none" stroke="#000000" stroke-width="2" d="' + ''.join(
        f'M{x0:.1f},{y0:.1f}L{x1:.1f},{y1:.1f}' for (x0, y0), (x1, y1) in G['leaders']) + '"/>')
    for q in G['labels']:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 20 else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} font-family="{FONT}">{q["text"]}</text>')
    o.append('</svg>')
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(G['lines']), 'line runs', {c: len(r) for c, r in G['greys'].items()})
