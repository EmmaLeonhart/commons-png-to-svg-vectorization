"""Rebuild File:Oki islands in Shimane prefecture.png: its source SVG (Shimane géolocalisation
relief.svg) plus the three labels the PNG adds, as real <text> for SVGTranslate.
Run from the repo root: python files/oki-islands/build.py
"""
from pathlib import Path

HERE = Path(__file__).parent
SRC = Path('data_lake/downloads/oki-islands/Shimane géolocalisation relief.svg')
OUT = HERE / 'Oki islands in Shimane prefecture.svg'
K = 2468 / 423  # source units per PNG pixel (the PNG is the source scaled to 423 px wide)
FONT = "'Noto Sans CJK JP', 'Noto Sans JP', sans-serif"
# (id, x, baseline y, font size) in PNG pixels, fitted to the PNG's ink boxes; text
LABELS = [
    ('label-oki', 234.0, 47.0, 24.0, '隠岐諸島'),
    ('label-dogo', 376.5, 89.0, 19.6, '島後'),
    ('label-dozen', 337.5, 130.0, 19.6, '島前'),
]


def main():
    s = SRC.read_text(encoding='utf8')
    texts = ''.join(
        f'\n    <text id="{i}" x="{x * K:.1f}" y="{y * K:.1f}" style="font-size:{fs * K:.1f}px">{t}</text>'
        for i, x, y, fs, t in LABELS)
    group = (f'\n  <g id="oki-labels" style="font-family:{FONT};font-weight:normal;fill:#000000;'
             f'stroke:none">{texts}\n  </g>\n')
    i = s.rindex('</svg>')
    OUT.write_text(s[:i] + group + s[i:], encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
