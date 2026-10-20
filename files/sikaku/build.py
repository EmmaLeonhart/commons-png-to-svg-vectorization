"""Rebuild File:Sikaku.png (an ID-card style "qualification" icon) by construction: the rounded frame, the 1 px ruled
lines and boxes and the orange bar at the PNG's measured positions, and the person in the photo box as the original
vector art of its stated source, File:User icon 2.svg (Tango project, public domain), nested and scaled so its ink box
matches the PNG's figure. Run from the repo root."""
import io, re
import numpy as np, resvg_py
from PIL import Image

PNG = 'data_lake/downloads/sikaku/Sikaku.png'
ICON = 'data_lake/downloads/sikaku/User icon 2.svg'
OUT = 'files/sikaku/Sikaku.svg'
W, H = 386, 227
# 1 px black lines, (row, x0, x1) and (column, y0, y1), pixel indices inclusive, measured
HL = [(40, 2, 381), (58, 269, 381), (65, 273, 374), (76, 2, 271), (162, 2, 35), (167, 161, 249), (182, 273, 374),
      (215, 161, 249)]
VL = [(35, 162, 225), (161, 167, 215), (249, 167, 215), (273, 65, 182), (374, 65, 182)]
FRAME = (2, 2, 381, 225, 6)  # rounded rectangle: pixel extents and corner radius
BAR = (4, 77, 263, 108, '#ffc20e')
PHOTO = (274, 66, 373, 181)  # inside of the photo box

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
px0, py0, px1, py1 = PHOTO
sub = a[py0:py1 + 1, px0:px1 + 1]
ys, xs = np.nonzero(sub.min(2) < 235)
fig = (px0 + xs.min(), py0 + ys.min(), px0 + xs.max() + 1, py0 + ys.max() + 1)  # the figure's ink box in the PNG

icon = open(ICON, encoding='utf8').read()
icon, n = re.subn(r'<path\b[^>]*\bid="path4306"[^>]*/>', '', icon, flags=re.S)  # the drop shadow: not in the PNG
assert n == 1
body = icon[icon.index('>', icon.index('<svg')) + 1:icon.rindex('</svg>')]
body = re.sub(r'<sodipodi:namedview\b.*?(/>|</sodipodi:namedview>)', '', body, flags=re.S)
body = re.sub(r'<metadata\b.*?</metadata>', '', body, flags=re.S)
body = re.sub(r'\s(inkscape|sodipodi):[\w-]+="[^"]*"', '', body)  # editor attributes (namespaces not declared here)
r = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=icon, width=480)))).convert('RGBA')
al = np.asarray(r)[..., 3] > 60
ys, xs = np.nonzero(al)
k = 480 / 48
ib = (xs.min() / k, ys.min() / k, (xs.max() + 1) / k, (ys.max() + 1) / k)  # icon ink box in its 48-unit space
s = ((fig[2] - fig[0]) / (ib[2] - ib[0]) + (fig[3] - fig[1]) / (ib[3] - ib[1])) / 2
tx, ty = fig[0] - ib[0] * s, fig[1] - ib[1] * s

x0, y0, x1, y1, rr = FRAME
lines = (''.join(f'M{s0},{y + 0.5}H{e + 1}' for y, s0, e in HL) + ''.join(f'M{x + 0.5},{s0}V{e + 1}' for x, s0, e in VL))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       f'<rect x="{BAR[0]}" y="{BAR[1]}" width="{BAR[2] - BAR[0] + 1}" height="{BAR[3] - BAR[1] + 1}" fill="{BAR[4]}"/>\n'
       f'<rect x="{x0 + 0.5}" y="{y0 + 0.5}" width="{x1 - x0}" height="{y1 - y0}" rx="{rr}" fill="none" stroke="#000000"/>\n'
       f'<path d="{lines}" fill="none" stroke="#000000"/>\n'
       f'<g transform="translate({tx:.3f},{ty:.3f}) scale({s:.4f})">{body}</g>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, 'icon scale %.3f at (%.1f, %.1f); figure box' % (s, tx, ty), fig)
