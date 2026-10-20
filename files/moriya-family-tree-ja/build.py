"""Rebuild File:Moriya Family Tree - 守矢氏系図.png: the tree's lines as the PNG's own straight runs (exact pixel
rectangles), and every name, circled number and the note as real <text> (transcribed), set vertically as one <text>
per column with one positioned <tspan> per character (no writing-mode needed). Column boxes are measured in the PNG;
characters are spaced evenly down each column. Run from the repo root."""
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/moriya-family-tree-ja/moriya-ja.png'
OUT = 'files/moriya-family-tree-ja/Moriya Family Tree - 守矢氏系図.svg'
BLACK, BLUE = '#000000', '#6680dd'
FONT = "'Noto Serif CJK JP', 'Noto Serif JP', 'IPAMincho', serif"

im = Image.open(PNG).convert('RGBA')
a = np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('RGB')).astype(int)
H, W = a.shape[:2]
ink = a.sum(2) < 600
blue_px = (a[..., 2] > 180) & (a[..., 0] < 150)
if blue_px.any():
    BLUE = '#%02x%02x%02x' % tuple(np.median(a[blue_px], 0).astype(int))

# (text, x0, x1, y0, y1, colour): one vertical column each
COLS = [('建御名方神', 247, 306, 65, 375, BLACK), ('︵諏訪大神︶', 197, 235, 132, 331, BLACK),
        ('洩矢神', 584, 642, 212, 387, BLUE), ('守達神', 118, 176, 470, 646, BLACK),
        ('片倉辺命', 248, 306, 464, 705, BLACK), ('出速雄神', 375, 434, 477, 706, BLACK),
        ('多満留姫', 523, 581, 437, 712, BLACK), ('守宅神', 635, 691, 437, 637, BLUE),
        ('千鹿頭神', 634, 690, 733, 972, BLUE), ('宇良古比売命', 762, 819, 729, 1102, BLACK),
        ('美津多麻比売命', 118, 180, 738, 1177, BLACK), ('児玉彦命', 248, 305, 796, 1039, BLUE),
        ('八櫛神', 182, 241, 1254, 1419, BLUE), ('守矢氏', 190, 241, 1563, 1750, BLUE)]
MARKS = [('①', 640, 665, 378, 403), ('②', 690, 715, 634, 659), ('③', 694, 719, 978, 1003), ('④', 296, 321, 1033, 1058),
         ('⑤', 236, 261, 1428, 1453)]
NOTE = ['大神の御言のまにまに', '千鹿頭神の跡を継いで', '祭政をつかさどる']  # right to left
NOTE_BOX = (329, 399, 918, 1161)


def column(t, x0, x1, y0, y1, col, size=None):
    n = len(t)
    size = size or (x1 - x0 + 1)
    pitch = (y1 - y0 + 1) / n
    cx = (x0 + x1 + 1) / 2
    spans = ''.join(f'<tspan x="{cx:.1f}" y="{y0 + (i + 0.5) * pitch + 0.36 * size:.1f}">{ch}</tspan>'
                    for i, ch in enumerate(t))
    return f'<text font-size="{size:.1f}" text-anchor="middle" fill="{col}">{spans}</text>'


text_mask = np.zeros(ink.shape, bool)
for _, x0, x1, y0, y1, *_ in COLS:
    text_mask[y0:y1 + 7, x0 - 2:x1 + 3] = True  # glyph tails reach a few px below the boxes
for _, x0, x1, y0, y1 in MARKS:
    text_mask[y0:y1 + 1, x0 - 2:x1 + 3] = True
nx0, nx1, ny0, ny1 = NOTE_BOX
text_mask[ny0 - 2:ny1 + 3, nx0 - 2:nx1 + 3] = True


def runs(m, L):
    out = []
    for y in range(m.shape[0]):
        r = np.concatenate([[0], m[y].astype(int), [0]]); d = np.diff(r)
        out += [(y, s, e) for s, e in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]) if e - s >= L]
    return out


cand = ink & ~text_mask
lines = np.zeros_like(cand)  # tree lines only: runs of 8 px or more, horizontal or vertical (not stray glyph ink)
for y, s, e in runs(cand, 8):
    lines[y, s:e] = True
for x, s, e in runs(cand.T, 8):
    lines[s:e, x] = True
rects = [f'M{s},{y}h{e - s}v1h{s - e}z' for y, s, e in runs(lines, 1)]
texts = [column(*c) for c in COLS]
texts += [f'<text x="{(x0 + x1 + 1) / 2:.1f}" y="{(y0 + y1 + 1) / 2 + 0.36 * (y1 - y0 + 1):.1f}" '
          f'font-size="{y1 - y0 + 1}" text-anchor="middle" fill="{BLACK}">{t}</text>' for t, x0, x1, y0, y1 in MARKS]
cw = (nx1 - nx0 + 1) / 3
note_size = cw * 0.9
longest = max(len(t) for t in NOTE)
for k, t in enumerate(NOTE):  # columns right to left, characters at the longest column's pitch
    cx0 = nx1 - (k + 1) * cw
    texts.append(column(t, cx0, cx0 + cw - 1, ny0, ny0 + (ny1 - ny0 + 1) * len(t) / longest - 1, BLACK, note_size))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n<path fill="#000000" d="{"".join(rects)}"/>\n'
       f'<g font-family="{FONT}">\n' + '\n'.join(texts) + '\n</g>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, len(rects), 'line runs,', len(texts), 'text elements; blue', BLUE)
