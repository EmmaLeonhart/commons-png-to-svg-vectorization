"""Rebuild File:Arms of Bahrain.png ("coat of arms of Bahrain minus the mantling") from the 2008 revision
of File:Emblem of Bahrain.svg: its shield outline, scaled to the PNG, with the five-point white chief the
derivative drew across the full width (the 2008 emblem's own chief is partly hidden by the mantling).
Run from the repo root: python files/arms-of-bahrain/build.py
"""
from pathlib import Path

import svgelements as se
from lxml import etree

HERE = Path(__file__).parent
SRC = Path('data_lake/downloads/arms-of-bahrain/Emblem of Bahrain (2008-02-04 revision).svg')
OUT = HERE / 'Arms of Bahrain.svg'
W, H = 1107, 1238
BOX = (1, 1106, 0, 1237)  # opaque extent of the PNG: x0, x1, y0, y1
RED, WHITE, INK = '#ce1126', '#ffffff', '#000000'
OUTLINE = 3
# chief: red tips at y 111, white tips at y 282.5, every 222.75 px (measured in the PNG)
RED_TIPS = [218.5, 441.5, 664.5, 887.5]
WHITE_TIPS = [107.5, 330.5, 553, 776, 998.5]


def shield_path():
    """The top-level red path of the 2008 emblem (the shield). Only the viewBox scales it, and its box is
    fitted to the PNG anyway, so its raw path data is used."""
    root = etree.parse(str(SRC)).getroot()
    ns = '{http://www.w3.org/2000/svg}'
    layer = root.find(f'.//{ns}g[@id="Layer_x0020_1"]')
    el = next(c for c in layer if c.tag == ns + 'path')
    p = se.Path(el.get('d'))
    p.reify()
    return p


def main():
    p = shield_path()
    x0, y0, x1, y1 = p.bbox()
    bx0, bx1, by0, by1 = BOX
    sx, sy = (bx1 - bx0 - OUTLINE) / (x1 - x0), (by1 - by0 - OUTLINE) / (y1 - y0)
    p = p * se.Matrix(sx, 0, 0, sy, bx0 + OUTLINE / 2 - x0 * sx, by0 + OUTLINE / 2 - y0 * sy)
    p.reify()
    d = p.d()
    zig = [(0, 117)] + [pt for i in range(5) for pt in [(WHITE_TIPS[i], 282.5)] + ([(RED_TIPS[i], 111)] if i < 4 else [])] + [(W, 117)]
    chief = f'M0,0 H{W} ' + ' '.join(f'L{x},{y}' for x, y in reversed(zig)) + ' Z'
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>Arms of Bahrain</title>
  <defs><clipPath id="shield"><path d="{d}"/></clipPath></defs>
  <path id="field" d="{d}" fill="{RED}"/>
  <path id="chief" d="{chief}" fill="{WHITE}" clip-path="url(#shield)"/>
  <path id="outline" d="{d}" fill="none" stroke="{INK}" stroke-width="{OUTLINE}"/>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
