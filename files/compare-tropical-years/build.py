"""Rebuild File:CompareTropicalYears.png as an SVG chart: the five curves are the polynomials of
curves.json drawn as smooth paths, the layout (frame, grid, legend, colours) is measured from the PNG,
and all text is <text> in Liberation Sans (Arial metrics), sizes fitted to the PNG's ink widths.
Run from the repo root after curves.py."""
import io, json
import numpy as np, resvg_py
from PIL import Image, ImageFont

PNG = 'data_lake/downloads/compare-tropical-years/CompareTropicalYears.png'
OUT = 'files/compare-tropical-years/CompareTropicalYears.svg'
ARIAL = r'C:\Windows\Fonts\arial.ttf'
FAMILY = "'Liberation Sans', Arial, Helvetica, sans-serif"
W, H = 967, 587
X0, X1, Y0, Y1 = 129, 928, 44, 443
px = lambda yr: X0 + (yr + 6000) * (X1 - X0) / 16000
py = lambda d: Y1 - (d - 365.2412) * 19 / 0.0001  # frame top is 365.2433
C = json.load(open('files/compare-tropical-years/curves.json'))
COL = {'spring': '#42ae42', 'autumn': '#945129', 'summer': '#ffc321', 'winter': '#9cb6ce', 'mean360': '#424142'}
TXT = '#404040'


def fit_size(t, width):
    return min((abs(ImageFont.truetype(ARIAL, s).getbbox(t, anchor='ls')[2] - ImageFont.truetype(ARIAL, s).getbbox(t, anchor='ls')[0] - width), s)
               for s in np.arange(8, 24, 0.05))[1]


def text(t, x0, x1, base, size, anchor='start', extra=''):
    f = ImageFont.truetype(ARIAL, size)
    if anchor == 'start':
        x = x0 - f.getbbox(t, anchor='ls')[0]
    elif anchor == 'end':
        x = x1 + 1 - f.getbbox(t, anchor='rs')[2]
    else:
        l, _, r, _ = f.getbbox(t, anchor='ms')
        x = (x0 + x1 + 1) / 2 - (l + r) / 2
    return f'<text x="{x:.1f}" y="{base:.1f}" font-size="{size:.2f}" text-anchor="{anchor}"{extra}>{t}</text>'


p = ['<rect width="%d" height="%d" fill="#e0e0e0"/>' % (W, H),
     f'<rect x="{X0 + 0.5}" y="{Y0 + 0.5}" width="{X1 - X0}" height="{Y1 - Y0}" fill="#fff" stroke="#c6c3c6"/>',
     '<g stroke="#c6c3c6">'
     + ''.join(f'<path d="M{int(px(yr) + 0.5)}.5,{Y0}V{Y1}"/>' for yr in range(-5000, 10000, 1000) if yr != 2000)
     + ''.join(f'<path d="M{X0},{int(py(365.2412 + k * 0.0001) + 0.5)}.5H{X1}"/>' for k in range(1, 21)) + '</g>',
     f'<path d="M{int(px(2000) + 0.5)}.5,{Y0}V{Y1}" stroke="#808080"/>']
# x positions of the PNG's gridlines are whole pixels; .5 puts the 1 px line on that pixel column
for key in ('spring', 'autumn', 'summer', 'winter', 'mean360'):
    yrs = np.linspace(-6000, 10000, 161)
    v = np.polyval(C[key]['coef'], yrs / 1000)
    d = 'M' + ' L'.join(f'{px(y):.1f},{py(d):.1f}' for y, d in zip(yrs, v))
    p.append(f'<path id="{key}" d="{d}" fill="none" stroke="{COL[key]}" stroke-width="2.5" stroke-linejoin="round"/>')

t = []
t.append(text('Länge des tropischen Jahres nach verschiedenen Definitionen', 268, 788, 37, fit_size('Länge des tropischen Jahres nach verschiedenen Definitionen', 521), 'middle'))
tick = fit_size('365.2412', 52)
for k in range(11):
    t.append(text(f'{365.2412 + 0.0002 * k:.4f}', 0, 123, py(365.2412 + 0.0002 * k) + 5, tick, 'end'))
for k in range(9):
    yr = -6000 + 2000 * k
    t.append(text(str(yr), px(yr) - 15, px(yr) + 15, 467, tick, 'middle'))
t.append(text('Jahr', 515, 549, 492, fit_size('Jahr', 35), 'middle'))
ys = fit_size('Jahreslänge in Ephemeridentagen', 286)
f = ImageFont.truetype(ARIAL, ys)
l, _, r, _ = f.getbbox('Jahreslänge in Ephemeridentagen', anchor='ms')
t.append(f'<text transform="translate(44,242.5) rotate(-90)" x="{-(l + r) / 2:.1f}" y="0" font-size="{ys:.2f}" '
         f'text-anchor="middle">Jahreslänge in Ephemeridentagen</text>')
leg = fit_size('von Frühlingsäquinoktium zu Frühlingsäquinoktium', 290)
legend = [('spring', 160, 512, 'von Frühlingsäquinoktium zu Frühlingsäquinoktium', 208),
          ('autumn', 611, 512, 'von Herbstäquinoktium zu Herbstäquinoktium', 659),
          ('summer', 160, 535, 'von Sommersonnwende zu Sommersonnwende', 208),
          ('winter', 611, 535, 'von Wintersonnwende zu Wintersonnwende', 659),
          ('mean360', 611, 558, '360°- Definition', 659)]
for key, sx, sy, label, tx in legend:
    p.append(f'<path d="M{sx},{sy + 0.5}H{sx + 41}" stroke="{COL[key]}" stroke-width="3"/>')
    t.append(text(label, tx, tx, sy + 5, leg, 'start'))
p.append(f'<g font-family="{FAMILY}" fill="{TXT}">' + ''.join(t) + '</g>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + ''.join(p) + '</svg>'
open(OUT, 'w', encoding='utf8').write(svg)
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
o = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[ARIAL], skip_system_fonts=True)))).convert('RGB')).astype(int)
diff = np.abs(o - a).max(-1) > 64
print('tick %.2f legend %.2f ytitle %.2f  pixels differing %.4f' % (tick, leg, ys, diff.mean()))
Image.fromarray(np.concatenate([a, o], 0).astype(np.uint8)).save('scratch/arms/cty_cmp.png')
d = np.full_like(a, 255); d[diff] = (220, 0, 0)
Image.fromarray(d.astype(np.uint8)).save('scratch/arms/cty_diff.png')
