"""Rebuild File:Shinmei torii.png: torii A of File:Torii gate variation.svg, stretched as in
the PNG, with its labels as real <text> for SVGTranslate.
Run from the repo root: python files/shinmei-torii/build.py
"""
from pathlib import Path

import svgelements as se

HERE = Path(__file__).parent
SRC = Path('data_lake/downloads/shinmei-torii/Torii gate variation.svg')
OUT = HERE / 'Shinmei torii.svg'
W, H = 537, 354
# Torii A of the source, but the PNG's author moved the parts (pillars nearer the ends of the
# kasagi), so each part is fitted to its own box in the PNG: source path -> PNG interior box
# (x0, x1, y0, y1) measured from the PNG's tan areas.
PARTS = {
    'path1062': (81, 384, 65, 82),     # kasagi
    'path1072': (109, 126, 75, 327),   # hashira, left
    'path1048': (339, 356, 75, 327),   # hashira, right
    'path1044': (130, 335, 114, 131),  # nuki
}
HALF = 1.0  # half the outline width: the outline is centred on each edge
WOOD, INK = '#cbb99d', '#000000'
FONT = "'Noto Sans CJK JP', 'Noto Sans JP', sans-serif"
# (id, x, baseline y, font size, letter-spacing, text); fitted to the PNG's ink boxes
TEXTS = [
    ('title', 29.5, 38.0, 22.0, 1.33, 'Shinmei torii'),
    ('label-kasagi', 438.0, 76.0, 14.0, 0.8, 'kasagi'),
    ('label-nuki', 427.0, 131.0, 14.0, 0.3, 'nuki'),
    ('label-hashira', 418.0, 207.0, 14.0, 0.8, 'hashira'),
]
LEADERS = [(392, 423, 71.5), (365, 414, 125.5), (364, 402, 202.5)]


def main():
    svg = se.SVG.parse(str(SRC), reify=True)
    els = {e.id: e for e in svg.elements() if getattr(e, 'id', None) in PARTS}
    paths = []
    for pid, (x0, x1, y0, y1) in PARTS.items():
        bx0, by0, bx1, by1 = els[pid].bbox()
        ex0, ex1, ey0, ey1 = x0 - HALF, x1 + 1 + HALF, y0 - HALF, y1 + 1 + HALF
        sx, sy = (ex1 - ex0) / (bx1 - bx0), (ey1 - ey0) / (by1 - by0)
        p = se.Path(els[pid]) * se.Matrix(sx, 0, 0, sy, ex0 - bx0 * sx, ey0 - by0 * sy)
        p.reify()
        paths.append(f'    <path id="{pid}" d="{p.d()}"/>')
    texts = '\n'.join(f'    <text id="{i}" x="{x}" y="{y}" style="font-size:{fs}px;letter-spacing:{ls}px">{t}</text>'
                      for i, x, y, fs, ls, t in TEXTS)
    leaders = '\n'.join(f'    <path d="M{x0},{y} H{x1}"/>' for x0, x1, y in LEADERS)
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Shinmei torii</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <g id="torii" style="fill:{WOOD};stroke:{INK};stroke-width:2;stroke-linejoin:miter">
{chr(10).join(paths)}
  </g>
  <path id="ground" d="M42,329 H424" style="fill:none;stroke:{INK};stroke-width:2"/>
  <g id="leaders" style="fill:none;stroke:{INK};stroke-width:2">
{leaders}
  </g>
  <g id="labels" style="font-family:{FONT};font-weight:bold;fill:{INK}">
{texts}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
