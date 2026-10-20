"""Rebuild File:The Condensed Lifetime Chronologies of Yamato Takeru and Miyazuhime.png by construction: the reign bands
(a darker label column and a lighter field each, at the PNG's measured rows and colours), white fades at the top and
bottom (linear, as measured), the two lifetime bars as hexagons, and every label as real <text>: the emperors and
reign lengths and the four dated notes fitted to the PNG's lettering (tools/fit_text.py, Meiryo Bold), the two names set
vertically in the bars one character per measured glyph box. Run from the repo root; `fit` refits the labels."""
import json, sys
import numpy as np
from PIL import Image

sys.path.insert(0, 'tools')

PNG = 'data_lake/downloads/yamato-takeru-chron/The Condensed Lifetime Chronologies of Yamato Takeru and Miyazuhime.png'
OUT = 'files/yamato-takeru-chron/The Condensed Lifetime Chronologies of Yamato Takeru and Miyazuhime.svg'
PAR = 'files/yamato-takeru-chron/labels.json'
W, H = 739, 1103
X0, XC, X1 = 13.5, 136.5, 725  # chart left, label column edge, chart right
PEACH, BEIGE, BLUE_L, BLUE_F = '#fdd1af', '#fef2d9', '#adceed', '#d4e5f6'
BANDS = [(0, 84.5, PEACH, BEIGE), (84.5, 519.5, BLUE_L, BLUE_F), (519.5, 955.5, PEACH, BEIGE), (955.5, 1021.5, BLUE_L, BLUE_F),
         (1021.5, H, PEACH, BEIGE)]
FADE_TOP, FADE_BOTTOM = (20, 53), (1053, 1085)
ORANGE, NAVY = '#d55125', '#1a3f6c'
BARS = [((173, 244, 179, 395, 15), '#069edb'), ((282, 353, 266, 984, 15), '#f15966')]  # x0, x1, tip y0, tip y1, point depth
# (text, ink box, colour)
LABELS = [('垂仁天皇', (29, 118, 47, 67), ORANGE), ('景行天皇', (30, 118, 277, 297), NAVY), ('(60年)', (49, 98, 309, 326), NAVY),
          ('成務天皇', (30, 118, 713, 733), ORANGE), ('(60年)', (49, 98, 745, 762), ORANGE),
          ('仲哀天皇', (29, 118, 964, 984), NAVY), ('(15年)', (49, 98, 995, 1012), NAVY), ('応神天皇', (29, 118, 1038, 1058), ORANGE)]
NOTES = [('●40年 - 日本武尊の東征開始', '●43年 - 草薙御剣の創祀', (386, 664, 365, 406)),
         ('●元年 - 熱田神宮の創建', '●4年 - 氷上姉子神社の創建', (386, 652, 950, 996))]
VERTICAL = [('日本武尊', 0), ('宮簀媛命', 1)]  # text, bar index
FONT = "Meiryo, 'Hiragino Sans', 'Noto Sans CJK JP', 'Yu Gothic', sans-serif"

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)


def fit_labels():
    from fit_text import fit
    out = []
    for t, box, col in LABELS:
        out.append(dict(text=t, colour=col, **{k: fit(t, box, 'Meiryo', 'bold', canvas=(W, H))[k] for k in ('x', 'y', 'size', 'ls')}))
    black = a.max(2) < 90
    for l1, l2, (x0, x1, y0, y1) in NOTES:  # split each block at its blank row band
        rows = np.nonzero(black[y0:y1 + 1, x0:x1 + 1].any(1))[0]
        k = int(np.argmax(np.diff(rows)))
        for t, (r0, r1) in zip((l1, l2), ((rows[0], rows[k]), (rows[k + 1], rows[-1]))):
            cols = np.nonzero(black[y0 + r0:y0 + r1 + 1, x0:x1 + 1].any(0))[0]
            box = (x0 + int(cols.min()), x0 + int(cols.max()), y0 + int(r0), y0 + int(r1))
            out.append(dict(text=t, colour='#000000', **{k2: fit(t, box, 'Meiryo', 'bold', canvas=(W, H))[k2] for k2 in ('x', 'y', 'size', 'ls')}))
    return out


def vertical(t, bar):
    """one tspan per character at its measured box (white ink inside the bar)"""
    x0, x1, y0, y1, _ = BARS[bar][0]
    white = a[y0:y1, x0:x1].min(2) > 230
    rows = white.any(1)
    runs, y = [], 0
    while y < len(rows):
        if rows[y]:
            s = y
            while y < len(rows) and rows[y]:
                y += 1
            runs.append((s, y - 1))
        else:
            y += 1
    # merge runs into as many glyphs as the text has (glyph parts can leave gaps)
    while len(runs) > len(t):
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = int(np.argmin(gaps))
        runs[i:i + 2] = [(runs[i][0], runs[i + 1][1])]
    size = float(np.median([e - s + 1 for s, e in runs])) / 0.88
    cx = (x0 + x1 + 1) / 2
    spans = ''.join(f'<tspan x="{cx:.1f}" y="{y0 + e + 1 - 0.04 * size:.1f}">{ch}</tspan>' for ch, (s, e) in zip(t, runs))
    return f'<text font-size="{size:.1f}" font-weight="bold" text-anchor="middle" fill="#ffffff">{spans}</text>'


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        json.dump(fit_labels(), open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><linearGradient id="ft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="1"/>'
         '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         '<linearGradient id="fb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    for y0, y1, left, right in BANDS:
        o += [f'<rect x="{X0}" y="{y0}" width="{XC - X0}" height="{y1 - y0}" fill="{left}"/>',
              f'<rect x="{XC}" y="{y0}" width="{X1 - XC}" height="{y1 - y0}" fill="{right}"/>']
    o += [f'<rect x="0" y="0" width="{W}" height="{FADE_TOP[0]}" fill="#ffffff"/>',
          f'<rect x="0" y="{FADE_TOP[0]}" width="{W}" height="{FADE_TOP[1] - FADE_TOP[0]}" fill="url(#ft)"/>',
          f'<rect x="0" y="{FADE_BOTTOM[0]}" width="{W}" height="{FADE_BOTTOM[1] - FADE_BOTTOM[0]}" fill="url(#fb)"/>',
          f'<rect x="0" y="{FADE_BOTTOM[1]}" width="{W}" height="{H - FADE_BOTTOM[1]}" fill="#ffffff"/>']
    for (x0, x1, t0, t1, dp), col in BARS:
        xa, xb, xm = x0, x1 + 1, (x0 + x1 + 1) / 2
        o.append(f'<path fill="{col}" d="M{xm},{t0 - 0.5}L{xb},{t0 + dp}V{t1 - dp + 1}L{xm},{t1 + 1.5}L{xa},{t1 - dp + 1}V{t0 + dp}Z"/>')
    o.append(f'<g font-family="{FONT}">')
    for q in P:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 3 else ''
        o.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}" font-weight="bold"{ls} fill="{q["colour"]}">{q["text"]}</text>')
    o += [vertical(t, b) for t, b in VERTICAL]
    o += ['</g>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
