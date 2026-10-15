"""Rebuild File:Kamon maru ni kenkatabami.png from two Commons SVGs: the ken-katabami of
File:Japanese Crest ken Katabami.svg and the ring of File:Japanese Crest Maru ni Katabami.svg,
recoloured black on white, scaled and placed by a grid search against the PNG's ink.
Run from the repo root."""
import io, re, sys
import numpy as np, resvg_py
from PIL import Image

K = 'data_lake/downloads/kamon/'
png = np.asarray(Image.open('data_lake/downloads/order-life-arms/png/Kamon maru ni kenkatabami.png').convert('L').resize((400, 400))) < 128
ken = re.search(r'<path\s+d="([^"]+)"', open(K + 'Japanese Crest ken Katabami.svg', encoding='utf8').read()).group(1)
ring = re.search(r'd="(M 344,65[^"]+)"', open(K + 'Japanese Crest Maru ni Katabami.svg', encoding='utf8').read()).group(1)


def svg(rs, ks, dx=0, dy=0):
    # both sources are 688 px squares centred on (344, 344); scale each about that centre
    t = lambda s: f'translate({344 + dx},{344 + dy}) scale({s}) translate(-344,-344)'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 688 688">'
            f'<rect width="688" height="688" fill="#fff"/>'
            f'<path transform="{t(rs)}" fill="#000" fill-rule="evenodd" d="{ring}"/>'
            f'<path transform="{t(ks)}" fill="#000" d="{ken}"/></svg>')


def iou(s):
    im = np.asarray(Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s)))).convert('L')) < 128
    return (im & png).sum() / (im | png).sum()


best = max(((iou(svg(r, k)), r, k) for r in np.arange(0.90, 1.30, 0.02) for k in np.arange(0.60, 1.10, 0.04)))
_, r, k = best
best = max(((iou(svg(r2, k2, dx, dy)), r2, k2, dx, dy) for r2 in np.arange(r - 0.02, r + 0.021, 0.005)
            for k2 in np.arange(k - 0.04, k + 0.041, 0.01) for dx in (-6, 0, 6) for dy in (-6, 0, 6)))
print('IoU %.4f ring %.3f ken %.3f offset %d,%d' % best)
open(sys.argv[1] if len(sys.argv) > 1 else 'files/kamon-maru-ni-kenkatabami/Kamon maru ni kenkatabami.svg', 'w', encoding='utf8').write(svg(*best[1:]))
