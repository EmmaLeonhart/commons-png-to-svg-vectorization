"""Fit File:Orion-Sternkarte.png's pp3 projection: match bright stars of pp3's stars.dat to the PNG's black star discs under
several azimuthal projections. Result (2026-10-19): azimuthal equidistant, centre RA 5.5591 h, Dec +2.715, 506.67 px/rad,
rotation ~0, anchors rms 0.15 px. Run from the repo root."""
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

PNG = 'data_lake/downloads/orion-sternkarte/Orion-Sternkarte.png'
import io, zipfile
Z = zipfile.ZipFile('data_lake/downloads/pp3/pp3-1.3.3-win.zip')
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
black = a.sum(2) < 150
lab, n = ndimage.label(black)
blobs = []
for i, sl in enumerate(ndimage.find_objects(lab), 1):
    m = lab[sl] == i
    ys, xs = np.nonzero(m)
    blobs.append((xs.mean() + sl[1].start + 0.5, ys.mean() + sl[0].start + 0.5, m.sum()))
blobs = np.array(blobs)
L = Z.read('pp3-1.3.3-win/stars.dat').decode('latin1').split('\n')
stars = []
for k in range(0, len(L) - 3, 4):
    f = L[k].split()
    stars.append((int(f[0]), int(f[1]), float(f[2]), float(f[3]), float(f[4]), L[k + 1], L[k + 2]))
hr = {s[1]: s for s in stars}
ANCH = {2061: (143, 186), 1713: (233, 326), 2491: (37, 403), 1457: (316, 105)}


def proj(p, ra, dec, kind):
    ra0, dec0, s, rot, cx, cy = p
    l = np.radians((ra - ra0) * 15); d = np.radians(dec); d0 = np.radians(dec0)
    cosc = np.sin(d0) * np.sin(d) + np.cos(d0) * np.cos(d) * np.cos(l)
    x = np.cos(d) * np.sin(l); y = np.cos(d0) * np.sin(d) - np.sin(d0) * np.cos(d) * np.cos(l)
    c = np.arccos(np.clip(cosc, -1, 1))
    k = {'stereo': 2 / (1 + cosc), 'gnomonic': 1 / cosc, 'equidist': np.where(c > 0, c / np.sin(c), 1),
         'ortho': np.ones_like(c)}[kind]
    x, y = -x * k, y * k
    r = np.radians(rot)
    return cx + s * (x * np.cos(r) - y * np.sin(r)), cy - s * (x * np.sin(r) + y * np.cos(r))


def nearest_blob(x, y):
    d = np.hypot(blobs[:, 0] - x, blobs[:, 1] - y)
    return blobs[np.argmin(d)]


anch = {h: nearest_blob(*xy) for h, xy in ANCH.items()}
bright = [s for s in stars if s[4] < 4.6 and 3.5 < s[2] < 7.2 and -32 < s[3] < 32]
for kind in ('stereo', 'gnomonic', 'equidist', 'ortho'):
    def loss_a(p):
        return sum(((np.array(proj(p, hr[h][2], hr[h][3], kind)) - b[:2]) ** 2).sum() for h, b in anch.items())
    r = optimize.minimize(loss_a, [5.6, 0, 600, 0, W / 2, H / 2], method='Nelder-Mead', options={'maxiter': 20000, 'xatol': 1e-6, 'fatol': 1e-9})

    def loss_all(p):
        tot = 0
        for s in bright:
            x, y = proj(p, s[2], s[3], kind)
            if 3 < x < W - 3 and 3 < y < H - 3:
                tot += min(np.hypot(blobs[:, 0] - x, blobs[:, 1] - y).min(), 4) ** 2
        return tot
    r2 = optimize.minimize(loss_all, r.x, method='Nelder-Mead', options={'maxiter': 20000, 'xatol': 1e-6, 'fatol': 1e-9})
    print(kind, 'anchors rms %.2f' % np.sqrt(loss_a(r.x) / 4), 'all %.1f' % loss_all(r2.x), np.round(r2.x, 4))
