"""Rebuild File:Fukuchiyama Toyuke-daijinja map.png by construction: the line work from the PNG's measured straight
runs (every horizontal and vertical run of black, merged into 1 px rectangles, dashes included), and every label as
real <text>, transcribed by reading the PNG, with each character placed at its measured cell (one <text> per label,
one positioned <tspan> per character, so vertical labels need no writing-mode support). Run from the repo root."""
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/fukuchiyama-toyuke-map/Fukuchiyama Toyuke-daijinja map.png'
OUT = 'files/fukuchiyama-toyuke-map/Fukuchiyama Toyuke-daijinja map.svg'
FONT = "'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif"

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
blk = a.sum(2) < 384


def runs(m, L):
    out = []
    for y in range(m.shape[0]):
        r = np.concatenate([[0], m[y].astype(int), [0]])
        d = np.diff(r)
        for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            if e - s >= L:
                out.append((y, s, e))
    return out


# labels: (text, vertical?, rough box x0, x1, y0, y1); the ink inside the box gives the exact cells
V, Hz = True, False
LABELS = [('月宮', V, 140, 178, 30, 105), ('風宮', V, 740, 778, 30, 105), ('本宮', V, 500, 545, 180, 250),
          ('多賀之宮', V, 300, 345, 305, 395), ('土之宮', V, 700, 745, 315, 385),
          ('竈原神社', V, 234, 252, 12, 120), ('種木神社', V, 254, 273, 12, 120), ('瀧之神社', V, 275, 293, 12, 120),
          ('東羅神社', V, 295, 313, 12, 120), ('かまはら', V, 230, 256, 125, 205), ('○', Hz, 346, 368, 56, 80),
          ('龍燈の杉', V, 346, 368, 88, 160), ('金刀比羅神社', V, 412, 445, 12, 120),
          ('篷戸神社', V, 535, 553, 12, 120), ('神南神社', V, 555, 573, 12, 120), ('鹿嶋神社', V, 575, 593, 12, 120),
          ('繁昌神社', V, 595, 613, 12, 120), ('御幸神社', Hz, 18, 104, 414, 434)]
for names, x0, x1, ys in [('知恵 鏡作 大若 御釼 和幣 榊森 若宮 蜂須 天田', 26, 103, [187 + 19 * i for i in range(9)]),
                          ('横河 青榊 保浪 平岡 礒之 甲之 小篠', 936, 1013, [168 + 19 * i for i in range(7)]),
                          ('白鬚 福徳', 936, 1013, [358, 377]), ('南野 榊原 姫若', 926, 1003, [396, 415, 434]),
                          ('椿本 祓戸 日吉', 916, 993, [454, 472, 491]), ('酒造 保養 岩崎', 906, 983, [511, 529, 548])]:
    for n, y in zip(names.split(), ys):
        LABELS.append((n + '神社', Hz, x0, x1, y - 8, y + 8))

# text ink = black inside a label box that is not part of a long straight run (a cell border); inside the big
# labels, which sit well inside their frames, all ink is text (their characters have long straight strokes)
BIG = {'月宮', '風宮', '本宮', '多賀之宮', '土之宮', '御幸神社'}
lines = np.zeros_like(blk)
for y, s, e in runs(blk, 14):
    lines[y, s:e] = True
for x, s, e in runs(blk.T, 14):
    lines[s:e, x] = True
small_box, big_box = np.zeros_like(blk), np.zeros_like(blk)
for t, _, x0, x1, y0, y1 in LABELS:
    (big_box if t in BIG else small_box)[y0:y1, x0:x1] = True
lines &= ~big_box
text_ink = blk & (big_box | (small_box & ~lines))


def label_svg(t, vert, x0, x1, y0, y1):
    m = text_ink[y0:y1, x0:x1]
    ys, xs = np.nonzero(m)
    bx0, bx1, by0, by1 = x0 + xs.min(), x0 + xs.max() + 1, y0 + ys.min(), y0 + ys.max() + 1
    n = len(t)
    if vert:
        size = bx1 - bx0 + 1
        pitch = (by1 - by0) / n
        cells = [((bx0 + bx1) / 2, by0 + (i + 0.5) * pitch) for i in range(n)]
    else:
        size = by1 - by0 + 1
        pitch = (bx1 - bx0) / n
        cells = [(bx0 + (i + 0.5) * pitch, (by0 + by1) / 2) for i in range(n)]
    size = max(size, 12)
    spans = ''.join(f'<tspan x="{cx:.1f}" y="{cy + 0.38 * size:.1f}">{c}</tspan>' for c, (cx, cy) in zip(t, cells))
    return f'<text font-size="{size}" text-anchor="middle">{spans}</text>'


# line work: the long runs, plus short runs outside the text (dashes), each as a 1 px rectangle path
lw = blk & ~text_ink
rects, left = [], lw.copy()
for y, s, e in runs(lw, 2):           # horizontal runs first
    rects.append(f'M{s},{y}h{e - s}v1h{s - e}z')
    left[y, s:e] = False
vert_only = [f'M{x},{s}h1v{e - s}h-1z' for x, s, e in runs(left.T, 1)]  # the rest as vertical runs
out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       f'<path fill="#000000" d="{"".join(rects + vert_only)}"/>\n'
       f'<g font-family="{FONT}" fill="#000000">\n' + '\n'.join(label_svg(*L) for L in LABELS) + '\n</g>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(out)
print('wrote', OUT, len(LABELS), 'labels')
