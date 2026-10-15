"""Rebuild File:Birth and death rate of japan 1950-2019.png as an SVG chart: the series are the published
crude rates (rates.csv, from data.py), the layout is measured from the PNG (plot frame, gridlines, legend,
colours), and all text is <text> in Carlito (metric-compatible with the PNG's Calibri, and rendered on
Commons), sized to the PNG's ink widths with Calibri's metrics. Run from the repo root."""
import csv, io
import numpy as np, resvg_py
from PIL import Image, ImageFont

PNG = 'data_lake/downloads/japan-birth-death/Birth and death rate of japan 1950-2019.png'
OUT = 'files/japan-birth-death-rate/Birth and death rate of japan 1950-2019.svg'
CAL = r'C:\Windows\Fonts\calibri.ttf'
FAMILY = "Carlito, Calibri, 'Liberation Sans', sans-serif"
W, H = 1151, 645
X0, X1, Y0, Y1 = 135, 1116, 24, 588          # plot frame (2 px black lines centred here)
x = lambda yr: X0 + (yr - 1950) * (X1 - X0) / 69
y = lambda v: Y1 - v * (Y1 - Y0) / 30
BLUE, RED, GRID, TEXT, BORDER = '#5b9bd5', '#c00000', '#bfbfbf', '#595959', '#d9d9d9'
rows = list(csv.DictReader(open('files/japan-birth-death-rate/rates.csv')))


def size_for(t, width):
    """font size whose ink width (Calibri) equals width px."""
    best = min((abs(ImageFont.truetype(CAL, s).getbbox(t, anchor='ls')[2] - ImageFont.truetype(CAL, s).getbbox(t, anchor='ls')[0] - width), s)
               for s in np.arange(14, 30, 0.05))
    return best[1]


def text(t, ink_left, ink_right, baseline, size, anchor='middle', extra=''):
    f = ImageFont.truetype(CAL, size)
    if anchor == 'middle':
        l, _, r, _ = f.getbbox(t, anchor='ms')
        tx = (ink_left + ink_right + 1) / 2 - (l + r) / 2
    elif anchor == 'end':
        tx = ink_right + 1 - f.getbbox(t, anchor='rs')[2]
    else:
        tx = ink_left - f.getbbox(t, anchor='ls')[0]
    return f'<text x="{tx:.1f}" y="{baseline:.1f}" font-size="{size:.2f}" text-anchor="{anchor}"{extra}>{t}</text>'


tick = size_for('30.0', 35)
parts = [f'<rect width="{W}" height="{H}" fill="#fff"/>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="none" stroke="{BORDER}" stroke-width="2"/>',
         '<g stroke="%s" stroke-width="2">' % GRID
         + ''.join(f'<path d="M{X0},{y(v):.1f}H{X1}"/>' for v in range(5, 30, 5))
         + ''.join(f'<path d="M{x(yr):.1f},{Y0}V{Y1}"/>' for yr in range(1960, 2011, 10)) + '</g>',
         f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" fill="none" stroke="#000" stroke-width="2"/>']
labels = []
for v in range(0, 31, 5):
    # ink of the value labels: right edge 114, digits 12 px tall centred on the gridline
    labels.append(text(f'{v:.1f}', 0, 114, y(v) + 6.5, tick, 'end'))
for yr in range(1950, 2011, 10):
    labels.append(text(str(yr), x(yr) - 20, x(yr) + 19, 615, tick))
title_size = size_for('Rates per thousands', 203)
f = ImageFont.truetype(CAL, title_size)
l, _, r, _ = f.getbbox('Rates per thousands', anchor='ms')
# rotated a quarter turn: text x runs up the page, baseline at x=58, ink centred on y=283 (as in the PNG)
labels.append(f'<text transform="translate(58,283) rotate(-90)" x="{-(l + r) / 2:.1f}" y="0" '
              f'font-size="{title_size:.2f}" text-anchor="middle">Rates per thousands</text>')
leg = size_for('Crude birth rate', 141)
labels.append(text('Crude birth rate', 959, 1099, 60, leg, 'start'))
labels.append(text('Crude death rate', 959, 1099, 113, leg, 'start'))
for col, key, ly in ((BLUE, 'crude_birth_rate', 54), (RED, 'crude_death_rate', 107)):
    pts = [(x(int(r['year'])), y(float(r[key]))) for r in rows]
    parts.append(f'<g id="{key}" stroke="{col}" fill="{col}">'
                 f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke-width="2.25" stroke-linejoin="round"/>'
                 + ''.join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="5.75" stroke="none"/>' for a, b in pts)
                 + f'<path d="M913,{ly}H955" stroke-width="2.25"/><circle cx="934" cy="{ly}" r="5.75" stroke="none"/></g>')
parts.append(f'<g font-family="{FAMILY}" fill="{TEXT}">' + ''.join(labels) + '</g>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + ''.join(parts) + '</svg>'
open(OUT, 'w', encoding='utf8').write(svg)
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[CAL], skip_system_fonts=True)))).convert('RGB')).astype(int)
diff = np.abs(o - a).max(-1) > 64
print('tick %.2f title %.2f legend %.2f  pixels differing %.4f' % (tick, title_size, leg, diff.mean()))
Image.fromarray(np.concatenate([a, o], 0).astype(np.uint8)).save('scratch/arms/bd_cmp.png')
d = np.full_like(a, 255); d[diff] = (220, 0, 0)
Image.fromarray(d.astype(np.uint8)).save('scratch/arms/bd_diff.png')
