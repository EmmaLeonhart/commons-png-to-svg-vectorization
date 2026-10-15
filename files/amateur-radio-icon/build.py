"""Rebuild File:Amateur radio compact icon.png by construction: black-bordered yellow square,
stroked antenna (triangle, centre line, mast), the coil as a trochoid (a helix seen side-on) with a second harmonic for its lopsided loops and
the ground bars as rectangles. Bars are measured from the PNG's ink; the coil and antenna
parameters are fitted to it (scipy Nelder-Mead on ink IoU). Run from the repo root."""
import io, json, sys
import numpy as np, resvg_py
from PIL import Image
from scipy import ndimage, optimize

PNG = 'data_lake/downloads/amateur-radio-icon/Amateur radio compact icon.png'
OUT = 'files/amateur-radio-icon/Amateur radio compact icon.svg'
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
N = a.shape[0]
ink = a.sum(-1) < 3 * 128  # black (anti-aliasing is olive, half-tone)

# border thickness: first yellow pixel along the middle row
B = int(np.argmax(a[N // 2, :, 2] < 100 + 0 * a[N // 2, :, 0]) if False else np.argmax(~ink[N // 2]))
# ground bars: ink components right of x=170 that are taller than wide
lab, n = ndimage.label(ink[:, 170:N - B - 2] & ~ink[:, 170:N - B - 2].all(0)[None])
bars = []
for sl in ndimage.find_objects(lab):
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start + 170, sl[1].stop + 170
    if y1 - y0 > x1 - x0 and y1 - y0 > 10:
        bars.append((x0, y0, x1 - x0, y1 - y0))
bars.sort()
# the first bar touches the ground line, so its component starts at the cut: use its tall columns
cols = np.nonzero(ink[bars[0][1]:bars[0][1] + bars[0][3], 170:191].sum(0) > bars[0][3] * 0.8)[0] + 170
bars[0] = (int(cols.min()), bars[0][1], int(cols.max() - cols.min() + 1), bars[0][3])


def path_d(p):
    tx0, tx1, ty, ax, ay, mx, my, cx, rx, ry, y0, pitch, t0, t1, gy, sw, h2c, h2s = p
    pts = []
    for t in np.linspace(t0, t1, 160):
        pts.append((cx - rx * np.cos(t) + h2c * np.cos(2 * t) + h2s * np.sin(2 * t), y0 + pitch * t / (2 * np.pi) - ry * np.sin(t)))
    coil = 'M ' + ' L '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
    ant = f'M {tx0:.2f},{ty:.2f} H {tx1:.2f} L {ax:.2f},{ay:.2f} Z M {ax:.2f},{ty:.2f} V {my:.2f} H {mx:.2f}'
    tail = f'M {pts[-1][0]:.2f},{pts[-1][1]:.2f} L {pts[-1][0] + 4:.2f},{gy:.2f} H {bars[0][0] + 1:.2f}'
    return ant, coil, tail


def svg(p):
    sw = p[15]
    ant, coil, tail = path_d(p)
    rects = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in bars)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{N}" height="{N}" viewBox="0 0 {N} {N}">'
            f'<rect x="{B / 2}" y="{B / 2}" width="{N - B}" height="{N - B}" fill="#ffff00" stroke="#000" stroke-width="{B}"/>'
            f'<g fill="none" stroke="#000" stroke-width="{sw:.2f}" stroke-linejoin="miter">'
            f'<path d="{ant}"/><path d="{coil}" stroke-linecap="round"/><path d="{tail}"/></g>'
            f'<g fill="#000">{rects}</g></svg>')


def mask(s):
    im = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('RGB')).astype(int)
    return im.sum(-1) < 3 * 128


def loss(p):
    m = mask(svg(p))
    return 1 - (m & ink).sum() / (m | ink).sum()


if __name__ == '__main__':
    # starting values read off the PNG (pixels): triangle, apex, mast foot, coil, ground line, stroke
    p0 = np.array([77, 135, 37, 107, 82, 92, 120, 106, 28, 9, 128, 23, 0.0, 25.13, 234, 6.5, 0.0, 0.0])
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        r = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 3000, 'xatol': 0.05, 'fatol': 1e-5})
        json.dump(list(r.x), open('files/amateur-radio-icon/params.json', 'w'))
        print('fitted IoU %.4f' % (1 - r.fun))
    p = np.array(json.load(open('files/amateur-radio-icon/params.json'))) if len(sys.argv) == 1 or sys.argv[1] == 'fit' else p0
    open(OUT, 'w', encoding='utf8').write(svg(p))
    print('border', B, 'bars', bars, 'IoU %.4f' % (1 - loss(p)))
