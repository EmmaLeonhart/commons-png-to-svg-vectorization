"""Rebuild File:24directions.png (24方位) from scratch. It is the same construction as
File:Ehou-direction.png (same author): concentric regular octagons divided into equal angular
sectors (24 / 12 / 8 / 16) around a centre circle, with every label as real <text>.
Run from the repo root: python files/24directions/build.py
"""
from math import cos, radians, sin
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / '24directions.svg'
W, H = 348, 350
CX, CY = 173.75, 174.9           # centre (continuous pixel coordinates), measured
RINGS = [149, 120.25, 92.75, 65.5]  # octagon apothems, outer to inner (as in Ehou-direction)
R_CENTRE = 35.5
INK = '#000000'
FONT = "'Noto Sans CJK JP', 'Noto Sans JP', sans-serif"
FS = 16
CENTRAL = 0.38 * FS  # baseline below a CJK glyph's centre

OUTER = '壬子癸丑艮寅甲卯乙辰巽巳丙午丁未坤申庚酉辛戌乾亥'  # 24 mountains from 345° clockwise
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
TRIGRAMS = '坎艮震巽離坤兌乾'
# compass labels: (text, ink box x0, x1, y0, y1) measured in the PNG
OUTSIDE = [('北', 166, 181, 3, 18), ('北東', 282, 313, 54, 69), ('東', 328, 343, 168, 183),
           ('南東', 281, 313, 282, 297), ('南', 165, 180, 329, 344), ('南西', 33, 65, 283, 298),
           ('西', 3, 18, 166, 181), ('北西', 31, 63, 54, 69)]
BASELINE_DROP = 1.5


def pt(theta, ap):
    side = round(theta / 45) * 45
    r = ap / cos(radians(theta - side))
    return CX + r * sin(radians(theta)), CY - r * cos(radians(theta))


def octagon(ap):
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in (pt(22.5 + 45 * k, ap) for k in range(8))) + 'Z'


def spokes(a_out, a_in, angles, circle=False):
    d = []
    for t in angles:
        x0, y0 = pt(t, a_out)
        x1, y1 = (CX + R_CENTRE * sin(radians(t)), CY - R_CENTRE * cos(radians(t))) if circle else pt(t, a_in)
        d.append(f'M{x0:.2f},{y0:.2f} L{x1:.2f},{y1:.2f}')
    return ' '.join(d)


def text(t, x, y, centred=False):
    return f'    <text x="{x:.1f}" y="{y + (CENTRAL if centred else 0):.1f}" text-anchor="middle">{t}</text>'


def main():
    o, m, tr, i = RINGS
    lines = ' '.join([octagon(a) for a in RINGS] + [
        spokes(o, m, [7.5 + 15 * k for k in range(24)]),
        spokes(m, tr, [15 + 30 * k for k in range(12)]),
        spokes(tr, i, [22.5 + 45 * k for k in range(8)]),
        spokes(i, None, [22.5 * k for k in range(16)], circle=True)])
    labels = [text(ch, *pt((k * 15 - 15) % 360, (o + m) / 2), centred=True) for k, ch in enumerate(OUTER)]
    labels += [text(ch, *pt(k * 30, (m + tr) / 2), centred=True) for k, ch in enumerate(BRANCHES)]
    labels += [text(ch, *pt(k * 45, (tr + i) / 2), centred=True) for k, ch in enumerate(TRIGRAMS)]
    labels.append(text('中央', CX, CY, centred=True))
    labels += [text(t, (x0 + x1 + 1) / 2, y1 + 1 - BASELINE_DROP) for t, x0, x1, y0, y1 in OUTSIDE]
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>24方位</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <path id="grid" d="{lines}" style="fill:none;stroke:{INK};stroke-width:2"/>
  <circle id="centre" cx="{CX}" cy="{CY}" r="{R_CENTRE}" style="fill:#ffffff;stroke:{INK};stroke-width:2"/>
  <g id="labels" style="font-family:{FONT};font-size:{FS}px;fill:{INK}">
{chr(10).join(labels)}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
