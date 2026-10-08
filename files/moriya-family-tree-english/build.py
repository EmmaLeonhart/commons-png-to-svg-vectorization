"""Rebuild File:Moriya Family Tree (English).png from scratch: the 5 px lines as exact rectangles'
centre lines and every text line as real <text> for SVGTranslate. Font size and position of each
text line come from params.json (fitted to the PNG's ink boxes by scratch/fit_text_lines.py).
Run from the repo root: python files/moriya-family-tree-english/build.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Moriya Family Tree (English).svg'
PARAMS = HERE / 'params.json'
W, H = 3872, 1840
BLACK, BLUE = '#000000', '#6090dc'
LATIN = "'Gentium Plus', Gentium, 'Noto Serif', 'DejaVu Serif', serif"
CJK = "'Noto Serif CJK JP', 'Noto Serif JP', serif"
# line bands measured in the PNG (pixel indices, 5 px thick): (x0, x1, y0, y1)
HLINES = [(2260, 2970, 449, 453), (388, 1632, 466, 470), (1836, 1978, 597, 601), (1836, 1978, 613, 617),
          (750, 819, 964, 968), (750, 819, 977, 981), (3164, 3245, 989, 993), (3164, 3245, 1005, 1009)]
VLINES = [(2588, 2592, 395, 453), (1102, 1106, 420, 538), (2260, 2264, 449, 555), (2966, 2970, 449, 549),
          (388, 392, 466, 541), (1628, 1632, 466, 552), (1102, 1106, 764, 919), (388, 392, 767, 917),
          (2966, 2970, 770, 912), (783, 787, 977, 1300), (783, 787, 1530, 1633)]
# (id, text, colour, script, ink box x0, x1, y0, y1) measured in the PNG
TEXT = [
    ('minakatatomi', 'Minakatatomi (Takeminakata)', BLACK, 'latin', 499, 1734, 96, 188),
    ('moriya', 'Moriya', BLUE, 'latin', 2445, 2733, 204, 293),
    ('great-god', 'The Great God of Suwa', BLACK, 'latin', 777, 1436, 207, 261),
    ('minakatatomi-ja', '（御名方刀美命）', BLACK, 'cjk', 809, 1388, 306, 390),
    ('moriya-ja', '（洩矢神）', BLUE, 'cjk', 2433, 2747, 312, 391),
    ('moriya-morita', 'Moriya (Morita)', BLUE, 'latin', 2658, 3305, 556, 657),
    ('katakurabe', 'Katakurabe', BLACK, 'latin', 872, 1335, 558, 634),
    ('izuhayao', 'Izuhayao', BLACK, 'latin', 1443, 1808, 558, 657),
    ('tamaruhime', 'Tamaruhime', BLACK, 'latin', 1993, 2518, 558, 634),
    ('moritatsu', 'Moritatsu', BLACK, 'latin', 198, 597, 568, 634),
    ('moritatsu-ja', '（守達神）', BLACK, 'cjk', 231, 546, 667, 746),
    ('katakurabe-ja', '（片倉辺命）', BLACK, 'cjk', 890, 1293, 668, 752),
    ('tamaruhime-ja', '（多満留姫）', BLACK, 'cjk', 2060, 2463, 670, 754),
    ('izuhayao-ja', '（出速雄神）', BLACK, 'cjk', 1423, 1826, 671, 750),
    ('moriya-morita-ja', '（守宅神）', BLUE, 'cjk', 2805, 3119, 673, 752),
    ('mitsutamahime', 'Mitsutamahime', BLACK, 'latin', 71, 713, 922, 998),
    ('kodamahiko', 'Kodamahiko', BLUE, 'latin', 855, 1363, 922, 998),
    ('chikato', 'Chikatō', BLUE, 'latin', 2805, 3113, 948, 1024),
    ('urakohime', 'Urakohime', BLACK, 'latin', 3287, 3739, 948, 1024),
    ('mitsutamahime-ja', '（美津多麻比賣命）', BLACK, 'cjk', 56, 723, 1031, 1115),
    ('kodamahiko-ja', '（児玉彦命）', BLUE, 'cjk', 886, 1288, 1031, 1115),
    ('urakohime-ja', '（宇良古比賣命）', BLACK, 'cjk', 3233, 3812, 1070, 1154),
    ('chikato-ja', '（千鹿頭神）', BLUE, 'cjk', 2765, 3167, 1072, 1152),
    ('heir-1', 'Became the heir of the Moriya bloodline', BLACK, 'latin', 1066, 2034, 1134, 1192),
    ('heir-2', "as per the Suwa deity's will", BLACK, 'latin', 1066, 1716, 1202, 1260),
    ('yakushi', 'Yakushi', BLUE, 'latin', 603, 927, 1312, 1388),
    ('yakushi-ja', '（八櫛神）', BLUE, 'cjk', 611, 925, 1418, 1495),
    ('moriya-clan', 'Moriya Clan', BLUE, 'latin', 533, 1023, 1652, 1751),
]
LEFT_ALIGNED = {'heir-1', 'heir-2'}


def defaults(t):
    i, s, c, scr, x0, x1, y0, y1 = t
    size = (y1 - y0) * (1.0 if scr == 'cjk' else 1.1)
    x = x0 if i in LEFT_ALIGNED else (x0 + x1 + 1) / 2
    return dict(x=x, y=y1 - 0.1 * size, size=size, ls=0)


def main():
    params = json.loads(PARAMS.read_text(encoding='utf8')) if PARAMS.exists() else {}
    d = ' '.join([f'M{x0},{(y0 + y1 + 1) / 2} H{x1 + 1}' for x0, x1, y0, y1 in HLINES] +
                 [f'M{(x0 + x1 + 1) / 2},{y0} V{y1 + 1}' for x0, x1, y0, y1 in VLINES])
    texts = []
    for t in TEXT:
        i, s, colour, scr, *_ = t
        p = {**defaults(t), **params.get(i, {})}
        if scr == 'latin':
            p['ls'] = 0  # spacing fitted to the local fallback font would not carry over to Commons
        anchor = 'start' if i in LEFT_ALIGNED else 'middle'
        style = (f"font-family:{LATIN if scr == 'latin' else CJK};font-size:{p['size']:.1f}px;fill:{colour}"
                 + (f";letter-spacing:{p['ls']:.2f}px" if p.get('ls') else ''))
        texts.append(f'    <text id="{i}" x="{p["x"]:.1f}" y="{p["y"]:.1f}" text-anchor="{anchor}" style="{style}">'
                     f'{s.replace("&", "&amp;")}</text>')
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Moriya family tree</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <path id="lines" d="{d}" style="fill:none;stroke:{BLACK};stroke-width:5"/>
  <g id="labels">
{chr(10).join(texts)}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
