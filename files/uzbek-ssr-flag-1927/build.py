"""Rebuild File:Flag of the Uzbek Soviet Socialist Republic(1927-1929).png: a red field with three
lines of gold text (Uzbek in Arabic script, Russian in Cyrillic, Uzbek in Arabic script), as
real <text> for SVGTranslate. The Arabic-script lines are right-to-left, anchored at their
right edge. Run from the repo root: python files/uzbek-ssr-flag-1927/build.py
"""
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Flag of the Uzbek Soviet Socialist Republic (1927-1929).svg'
W, H = 752, 381
RED, GOLD = '#cd0000', '#ffd700'
FONT = "'Liberation Sans', Arial, 'DejaVu Sans', sans-serif"
# (id, x, baseline y, font size, letter-spacing, direction, text); for rtl lines x is the right edge.
# The PNG drew the Arabic script with a fallback font of its own, so those lines are matched
# by width and baseline rather than glyph height.
LINES = [
    ('line-arabic-1', 215.5, 53.0, 49.7, 0, 'rtl', 'أوز.ئـ.شـ.جـ.'),
    ('line-cyrillic', 23.5, 101.0, 48.0, 0.6, 'ltr', 'Уз.С.С.Р'),
    ('line-arabic-2', 203.5, 162.0, 49.3, 0, 'rtl', 'جـ.شـ.ا.اوز.'),
]


def main():
    texts = []
    for i, x, y, fs, ls, d, t in LINES:
        style = f'font-size:{fs}px' + (f';letter-spacing:{ls}px' if ls else '')
        attrs = f' direction="{d}" text-anchor="start"' if d == 'rtl' else ''
        texts.append(f'    <text id="{i}" x="{x}" y="{y}"{attrs} style="{style}">{t}</text>')
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Flag of the Uzbek SSR (1927-1929)</title>
  <rect width="{W}" height="{H}" fill="{RED}"/>
  <g id="inscription" style="font-family:{FONT};fill:{GOLD}">
{chr(10).join(texts)}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
