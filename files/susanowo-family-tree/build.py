"""Rebuild File:Susanowo family tree.png from scratch: the genealogy lines as exact 1 px segments
(extracted as straight horizontal/vertical runs from the PNG, which was drawn in MS Paint) and
every name as real vertical <text> for SVGTranslate.
Run from the repo root: python files/susanowo-family-tree/build.py
"""
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Susanowo family tree.svg'
W, H = 444, 817
RED, BLUE, BLACK = '#ff0000', '#0000ff', '#000000'
FONT = "'Noto Sans CJK JP', 'Noto Sans JP', 'MS Gothic', sans-serif"
FS, NOTE_FS = 16, 12
TOP = 0.5  # glyph ink starts this far below the start of a vertical line of text (fitted)

# names: (colour, bold, text, ink box x0, x1, y0); two-column names list right column first
NAMES = [
    (RED, 0, '伊邪那美神', 122, 137, 5), (BLUE, 0, '伊邪那岐神', 389, 404, 6),
    (BLUE, 0, '大山津見神', 211, 226, 37), (BLUE, 1, '建速須佐之男命', 388, 404, 149),
    (RED, 0, '櫛名田比売', 195, 210, 164), (RED, 0, '神大市比売', 273, 288, 200),
    (BLUE, 0, '八島士奴美神', 235, 250, 242), (RED, 0, '木花知流比売', 145, 160, 243),
    (BLUE, 0, '淤迦美神', 112, 127, 325), (RED, 0, '宇迦之御魂神', 282, 297, 340),
    (BLUE, 1, '大年神', 315, 331, 340), (RED, 0, '多岐都比売命', 352, 367, 340),
    (RED, 0, '市寸島比売命', 386, 401, 340), (RED, 0, '多紀理毘売命', 420, 435, 340),
    (BLUE, 0, ('布波能母遅', '久奴須奴神'), 172, 204, 404), (RED, 0, '日河比売', 112, 127, 418),
    (BLUE, 0, '布怒豆怒神', 40, 55, 490), (BLUE, 0, ('深淵之水', '夜礼花神'), 131, 163, 506),
    (RED, 0, ('天之都度', '閇知泥神'), 71, 103, 507), (BLUE, 0, '刺国大神', 10, 25, 575),
    (BLUE, 0, '淤美豆奴神', 110, 125, 588), (RED, 0, '布帝耳神', 40, 55, 597),
    (BLUE, 0, '天之冬衣神', 76, 91, 670), (RED, 0, '刺国若比売', 11, 26, 672),
    (RED, 0, '須勢理毘売命', 335, 350, 715), (BLUE, 1, '大国主神', 44, 60, 749),
]
NOTES = [('禊', 402, 413, 110, 121), ('誓約', 401, 426, 288, 299), ('（宗像三神）', 362, 428, 321, 332)]
# straight runs in pixel indices: horizontal (y, x0, x1), vertical (x, y0, y1); double lines are pairs
HLINES = [(19, 141, 386), (23, 141, 386), (124, 151, 280), (170, 212, 385), (174, 212, 385),
          (220, 292, 384), (224, 292, 384), (258, 342, 384), (276, 166, 230), (280, 166, 230),
          (326, 287, 322), (442, 130, 168), (446, 130, 168), (535, 106, 129), (539, 106, 129),
          (624, 58, 107), (628, 58, 107), (705, 28, 72), (709, 28, 72), (781, 64, 331), (785, 64, 331)]
VLINES = [(17, 639, 667), (47, 572, 590), (51, 709, 745), (83, 628, 667), (116, 539, 584),
          (119, 389, 412), (148, 446, 502), (151, 124, 238), (186, 280, 398), (217, 23, 34),
          (218, 117, 124), (243, 174, 235), (287, 326, 334), (307, 224, 326), (322, 326, 335),
          (342, 258, 707), (395, 264, 314), (396, 91, 144)]
# x 201: solid, dotted (1 px on, 1 px off), solid; x 280: hops over the double line at y 170/174
SPECIAL = [
    '<path d="M201.5,125 V130 M201.5,151 V163"/>',
    '<path d="M201.5,131 V150" style="stroke-dasharray:1,1"/>',
    '<path d="M280.5,125 V163 A 9,10 0 0 1 279.5,183 V198"/>',
]


def main():
    lines = ' '.join([f'M{x0},{y + 0.5} H{x1 + 1}' for y, x0, x1 in HLINES] +
                     [f'M{x + 0.5},{y0} V{y1 + 1}' for x, y0, y1 in VLINES])
    names = []
    for colour, bold, t, x0, x1, y0 in NAMES:
        style = f'fill:{colour}' + (';font-weight:bold' if bold else '')
        if isinstance(t, tuple):  # two columns, right one first
            xr, xl = x1 + 1 - FS / 2, x0 + FS / 2
            body = (f'<tspan x="{xr:.1f}" y="{y0 - TOP:.1f}">{t[0]}</tspan>'
                    f'<tspan x="{xl:.1f}" y="{y0 - TOP:.1f}">{t[1]}</tspan>')
            names.append(f'    <text writing-mode="tb" style="{style}">{body}</text>')
        else:
            names.append(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{y0 - TOP:.1f}" writing-mode="tb" '
                         f'style="{style}">{t}</text>')
    notes = '\n'.join(f'    <text x="{(x0 + x1 + 1) / 2:.1f}" y="{y1 + 1:.1f}" text-anchor="middle">{t}</text>'
                      for t, x0, x1, y0, y1 in NOTES)
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>スサノオの系図 (Family tree of Susanowo)</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <g id="lines" style="fill:none;stroke:{BLACK};stroke-width:1">
    <path d="{lines}"/>
    {chr(10).join('    ' + p for p in SPECIAL).strip()}
  </g>
  <g id="names" style="font-family:{FONT};font-size:{FS}px">
{chr(10).join(names)}
  </g>
  <g id="notes" style="font-family:{FONT};font-size:{NOTE_FS}px;fill:{BLACK}">
{notes}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
