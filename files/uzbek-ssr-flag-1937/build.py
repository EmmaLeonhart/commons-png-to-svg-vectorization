"""Rebuild File:Flag of the Uzbek Soviet Socialist Republic(1937-1938).png: a red field with two
lines of gold text, as real <text> for SVGTranslate.
Run from the repo root: python files/uzbek-ssr-flag-1937/build.py
"""
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Flag of the Uzbek Soviet Socialist Republic (1937-1938).svg'
W, H = 752, 381
RED, GOLD = '#cd0000', '#ffd700'
FONT = "'Liberation Sans', Arial, Helvetica, sans-serif"
# (id, x, baseline y, font size, letter-spacing, text). "Ozвekistan" uses Cyrillic в as the PNG does; the
# 1930s Uzbek Latin letter is ʙ (U+0299).
LINES = [
    ('line-latin', 11.0, 52.0, 48.0, 0, 'Ozвekistan SSR'),
    ('line-cyrillic', 23.5, 109.0, 48.0, 0.6, 'Уз.С.С.Р'),
]


def main():
    texts = '\n'.join(f'    <text id="{i}" x="{x}" y="{y}" style="font-size:{fs}px'
                      + (f';letter-spacing:{ls}px' if ls else '') + f'">{t}</text>'
                      for i, x, y, fs, ls, t in LINES)
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Flag of the Uzbek SSR (1937-1938)</title>
  <rect width="{W}" height="{H}" fill="{RED}"/>
  <g id="inscription" style="font-family:{FONT};fill:{GOLD}">
{texts}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
