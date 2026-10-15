"""Rebuild File:Kyoto-geo-stub.png: Kyoto Prefecture's silhouette (MLIT N03, via tools/n03_prefecture_svg.py)
in the flag's purple, with the emblem group of File:Flag of Kyoto Prefecture.svg laid over it (the PNG's
emblem overflows the silhouette). The silhouette's scale, aspect and offset are fitted to the PNG's opaque
pixels, the emblem's scale and position to its yellow pixels (Nelder-Mead on IoU). Run from the repo root."""
import io, json, re
import numpy as np, resvg_py
from PIL import Image
from scipy import optimize

PNG = 'data_lake/downloads/kyoto-geo-stub/Kyoto-geo-stub.png'
N03 = 'data_lake/downloads/kyoto-geo-stub/kyoto_n03.svg'
FLAG = 'data_lake/downloads/kyoto-geo-stub/Flag of Kyoto Prefecture.svg'
OUT = 'files/kyoto-geo-stub/Kyoto-geo-stub.svg'
im = np.asarray(Image.open(PNG).convert('RGBA')).astype(int)
H, W = im.shape[:2]
opaque = im[..., 3] > 128
yellow = opaque & (im[..., 0] > 200) & (im[..., 1] > 170) & (im[..., 2] < 80)
n03 = open(N03, encoding='utf8').read()
d = re.search(r'\sd="([^"]+)"', n03).group(1)
vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', n03).group(1).split()]
flag = open(FLAG, encoding='utf8').read()
PURPLE = re.search(r'fill="(#[0-9a-fA-F]{6})"', flag).group(1)
emblem = flag[flag.index('<g transform'):flag.rindex('</svg>')]
emblem = re.sub(r'^<g transform="[^"]*">', '<g>', emblem)  # its own translate/scale replaced below


def svg(p, q, parts='both'):
    sx, ay, tx, ty = p
    es, ex, ey = q
    sil = f'<path d="{d}" fill="{PURPLE}" fill-rule="evenodd" transform="translate({tx:.2f},{ty:.2f}) scale({sx:.5f},{sx * ay:.5f}) translate({-vb[0]:.2f},{-vb[1]:.2f})"/>'
    emb = f'<g transform="translate({ex:.2f},{ey:.2f}) scale({es:.4f})">{emblem}</g>'
    body = (sil if parts != 'emblem' else '') + (emb if parts != 'silhouette' else '')
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'


def mask(s):
    r = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('RGBA')).astype(int)
    return r


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


# silhouette: start from the bounding boxes
ys, xs = np.nonzero(opaque)
s0 = (xs.max() - xs.min()) / vb[2] * 1.1
p0 = [s0, 1.0, xs.min() - vb[2] * 0.05 * s0, ys.min() - vb[3] * 0.05 * s0]
q_dummy = [1, -100, -100]
fs = lambda p: 1 - iou(mask(svg(p, q_dummy, 'silhouette'))[..., 3] > 128, opaque & ~yellow | (opaque & yellow))
r = optimize.minimize(fs, p0, method='Nelder-Mead', options={'maxiter': 600, 'xatol': 1e-3, 'fatol': 1e-5,
                      'initial_simplex': np.array([p0] + [list(np.array(p0) + dd) for dd in np.diag([s0 * 0.05, 0.05, 15, 15])])})
p = r.x
# emblem: centred on the yellow pixels, scale so its yellow matches
ys, xs = np.nonzero(yellow)
q0 = [6.0, xs.mean(), ys.mean()]
fe = lambda q: 1 - iou(lambda m: (m[..., 0] > 200) & (m[..., 1] > 170) & (m[..., 2] < 80) & (m[..., 3] > 128), None) if False else \
    1 - iou((lambda m: (m[..., 0] > 200) & (m[..., 1] > 170) & (m[..., 2] < 80) & (m[..., 3] > 128))(mask(svg(p, q, 'emblem'))), yellow)
# coarse grid over scale and position, then a fine one around the best
best = min((fe([sc, q0[1] + dx, q0[2] + dy]), sc, q0[1] + dx, q0[2] + dy)
           for sc in np.arange(20, 40.01, 2) for dx in range(-40, 41, 10) for dy in range(-40, 41, 10))
best = min((fe([sc, x, y]), sc, x, y) for sc in np.arange(best[1] - 1.5, best[1] + 1.51, 0.5)
           for x in np.arange(best[2] - 6, best[2] + 6.1, 2) for y in np.arange(best[3] - 6, best[3] + 6.1, 2))
r2 = optimize.OptimizeResult(fun=best[0], x=np.array(best[1:]))
q = r2.x
out = svg(p, q)
open(OUT, 'w', encoding='utf8').write(out)
o = mask(out)
on_white = lambda x: x[..., :3] * (x[..., 3:] / 255) + 255 * (1 - x[..., 3:] / 255)
print('silhouette IoU %.4f (aspect %.3f)  emblem IoU %.4f  pixels differing %.4f' % (
    1 - r.fun, p[1], 1 - r2.fun, (np.abs(on_white(o) - on_white(im)).max(-1) > 64).mean()))
Image.fromarray(np.concatenate([on_white(im), on_white(o)], 1).astype(np.uint8)).save('scratch/arms/kyoto_cmp.png')
