"""Rebuild File:Ehou-direction.png (恵方の方位) from scratch: concentric regular octagons divided
into equal angular sectors (24 / 12 / 8 / 16), four highlighted cells, four arrows and all labels
as real <text> for SVGTranslate. Every dimension is measured from the PNG (see notes.md).
Run from the repo root: python files/ehou-direction/build.py
"""
from math import cos, radians, sin
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'Ehou-direction.svg'
W, H = 468, 436
CX, CY = 233.8, 217.9          # centre (continuous pixel coordinates)
RINGS = [149, 120.25, 92.75, 65.5]  # octagon apothems, outer to inner
R_CENTRE = 36.3
LINE, PINK = '#000000', '#ffabab'
FONT = "'Noto Sans CJK JP', 'Noto Sans JP', sans-serif"
FS = 16
CENTRAL = 0.38 * FS  # baseline below a CJK glyph's centre (em box: ascent .88, descent .12)

OUTER = '壬子癸丑艮寅甲卯乙辰巽巳丙午丁未坤申庚酉辛戌乾亥'  # 24 mountains, from 345° (壬) clockwise
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'                      # 12 branches, from 0° clockwise
TRIGRAMS = '坎艮震巽離坤兌乾'                              # 8 trigrams, from 0° clockwise
PINK_CELLS = ['壬', '甲', '丙', '庚']
# compass and annotation labels: (text, ink box x0, x1, y0, y1) measured in the PNG
OUTSIDE = [
    ('北', 226, 241, 46, 61), ('北北東', 288, 335, 48, 63), ('北東', 342, 373, 97, 112),
    ('東北東', 387, 434, 144, 159), ('東', 388, 403, 211, 226), ('東南東', 387, 434, 274, 289),
    ('南東', 341, 373, 325, 340), ('南南東', 290, 337, 371, 386), ('南', 225, 240, 372, 387),
    ('南南西', 130, 177, 373, 388), ('南西', 93, 125, 326, 341), ('西南西', 35, 82, 284, 299),
    ('西', 63, 78, 209, 224), ('西北西', 34, 81, 146, 161), ('北西', 91, 123, 97, 112),
    ('北北西', 131, 178, 45, 60),
    ('丁・壬の年', 148, 219, 7, 22), ('甲・己の年', 393, 463, 183, 198),
    ('乙・庚の年', 5, 75, 239, 254), ('丙・辛・戊・癸の年', 246, 365, 415, 430),
]
BASELINE_DROP = 1.5  # baseline sits this far above the ink box bottom (fitted)
# arrows: start (at the highlighted cell) and tip, in continuous pixel coordinates
ARROWS = [((194.0, 66.0), (181.0, 28.5)), ((385.0, 178.0), (432.7, 164.8)),
          ((80.0, 261.0), (26.8, 274.2)), ((274.0, 372.0), (283.5, 406.5))]
HEAD_LEN, HEAD_ANGLE, ARROW_W = 15, 40, 5


def pt(theta, ap):
    """Point on the octagon of apothem ap in direction theta (degrees clockwise from north)."""
    side = round(theta / 45) * 45
    r = ap / cos(radians(theta - side))
    return CX + r * sin(radians(theta)), CY - r * cos(radians(theta))


def octagon(ap):
    pts = [pt(22.5 + 45 * k, ap) for k in range(8)]
    return 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + 'Z'


def spokes(a_out, a_in, angles, circle=False):
    d = []
    for t in angles:
        x0, y0 = pt(t, a_out)
        x1, y1 = (CX + R_CENTRE * sin(radians(t)), CY - R_CENTRE * cos(radians(t))) if circle else pt(t, a_in)
        d.append(f'M{x0:.2f},{y0:.2f} L{x1:.2f},{y1:.2f}')
    return ' '.join(d)


def text(t, x, y, anchor='middle', centred=False):
    y = y + CENTRAL if centred else y
    return f'    <text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{t}</text>'


def main():
    o, m, tr, i = RINGS
    parts = []
    # highlighted cells of the outer ring
    for ch in PINK_CELLS:
        c = (OUTER.index(ch) * 15 - 15) % 360
        a0, a1 = c - 7.5, c + 7.5
        poly = [pt(a0, o), pt(a1, o), pt(a1, m), pt(a0, m)]
        parts.append(f'    <path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in poly)}Z" fill="{PINK}"/>')
    lines = ' '.join([octagon(a) for a in RINGS] + [
        spokes(o, m, [7.5 + 15 * k for k in range(24)]),
        spokes(m, tr, [15 + 30 * k for k in range(12)]),
        spokes(tr, i, [22.5 + 45 * k for k in range(8)]),
        spokes(i, None, [22.5 * k for k in range(16)], circle=True)])
    labels = []
    for k, ch in enumerate(OUTER):
        labels.append(text(ch, *pt((k * 15 - 15) % 360, (o + m) / 2), centred=True))
    for k, ch in enumerate(BRANCHES):
        labels.append(text(ch, *pt(k * 30, (m + tr) / 2), centred=True))
    for k, ch in enumerate(TRIGRAMS):
        labels.append(text(ch, *pt(k * 45, (tr + i) / 2), centred=True))
    labels.append(text('中央', CX, CY, centred=True))
    ring_labels = '\n'.join(labels)
    outside = '\n'.join(text(t, (x0 + x1 + 1) / 2, y1 + 1 - BASELINE_DROP) for t, x0, x1, y0, y1 in OUTSIDE)
    arrows = []
    for (sx, sy), (px, py) in ARROWS:
        ux, uy = sx - px, sy - py
        n = (ux * ux + uy * uy) ** 0.5
        ux, uy = ux / n, uy / n
        arms = []
        for s in (1, -1):
            a = radians(s * HEAD_ANGLE)
            arms.append((px + HEAD_LEN * (ux * cos(a) - uy * sin(a)), py + HEAD_LEN * (ux * sin(a) + uy * cos(a))))
        arrows.append(f'    <path d="M{sx:.1f},{sy:.1f} L{px:.1f},{py:.1f} M{arms[0][0]:.1f},{arms[0][1]:.1f} '
                      f'L{px:.1f},{py:.1f} L{arms[1][0]:.1f},{arms[1][1]:.1f}"/>')
    OUT.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>恵方の方位</title>
  <rect width="{W}" height="{H}" fill="#ffffff"/>
  <g id="highlighted-cells">
{chr(10).join(parts)}
  </g>
  <path id="grid" d="{lines}" style="fill:none;stroke:{LINE};stroke-width:2"/>
  <circle id="centre" cx="{CX}" cy="{CY}" r="{R_CENTRE}" style="fill:#ffffff;stroke:{LINE};stroke-width:2"/>
  <g id="arrows" style="fill:none;stroke:{PINK};stroke-width:{ARROW_W};stroke-linecap:round;stroke-linejoin:round">
{chr(10).join(arrows)}
  </g>
  <g id="ring-labels" style="font-family:{FONT};font-size:{FS}px;fill:{LINE}">
{ring_labels}
  </g>
  <g id="labels" style="font-family:{FONT};font-size:{FS}px;fill:{LINE}">
{outside}
  </g>
</svg>
''', encoding='utf8')
    print(OUT)


if __name__ == '__main__':
    main()
