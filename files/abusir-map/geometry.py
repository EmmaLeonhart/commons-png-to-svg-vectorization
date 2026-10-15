"""Step 1 of the Abusir map rebuild: the geometry (river, structures, causeways, north arrow, scale bar)
of File:AbusirAndAbuGurabPlan ru.svg, without its frame, labels and leader lines, registered to
File:Abusir map.png by a similarity transform (scale, shift) that minimises the chamfer distance from
the drawing to the PNG's ink. Writes files/abusir-map/geometry.json. Run from the repo root."""
import io, json, re
import numpy as np, resvg_py
from PIL import Image
from scipy import ndimage, optimize

SRC = 'data_lake/downloads/abusir-map/AbusirAndAbuGurabPlan ru.svg'
PNG = 'data_lake/downloads/abusir-map/Abusir map.png'
LEADERS = {'path3545', 'path3547', 'path3549', 'path3551', 'path3553', 'path3555', 'path3557'}

s = open(SRC, encoding='utf8').read()
layer2 = re.search(r'<g[^>]*id="layer2".*?>(.*?)</g>', s, re.S).group(1)
elems = re.findall(r'<(?:path|rect)\b.*?/>', layer2, re.S)
keep = [re.sub(r'\s(inkscape|sodipodi):[\w-]+="[^"]*"', '', e) for e in elems
        if re.search(r'\sid="([^"]+)"', e).group(1) not in LEADERS]
geom = '\n'.join(keep)

png = Image.open(PNG).convert('RGBA')
W, H = png.size
ink = np.asarray(Image.alpha_composite(Image.new('RGBA', png.size, 'white'), png).convert('L')) < 128
dist = ndimage.distance_transform_edt(~ink)


def svg(sc, tx, ty, body=geom):
    # the ru layers sit under translate(0,-68)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<g transform="translate({tx:.3f},{ty:.3f}) scale({sc:.5f}) translate(0,-68.000038)">{body}</g></svg>')


def mask(sv):
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=sv)))).convert('RGBA')
    return np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('L')) < 128


def cost(p):
    m = mask(svg(*p))
    return dist[m].mean() if m.any() else 1e9


if __name__ == '__main__':
    best = min((cost((sc, tx, ty)), sc, tx, ty) for sc in (1.0, 1.04, 1.08) for tx in (0, 10, 20) for ty in (-30, -20, -10, 0))
    r = optimize.minimize(cost, best[1:], method='Nelder-Mead', options={'xatol': 0.01, 'fatol': 1e-4, 'maxiter': 400})
    print('chamfer %.3f px  scale %.4f shift %.2f,%.2f' % (r.fun, *r.x))
    json.dump({'scale': r.x[0], 'tx': r.x[1], 'ty': r.x[2], 'chamfer': r.fun}, open('files/abusir-map/geometry.json', 'w'))
    m = mask(svg(*r.x))
    rgb = np.full((H, W, 3), 255, np.uint8)
    rgb[ink] = (150, 150, 150)
    rgb[m] = (220, 0, 0)
    Image.fromarray(rgb).save('scratch/arms/abusir_reg.png')
