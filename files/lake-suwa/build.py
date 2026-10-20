"""Rebuild File:Size of Lake Suwa.png from public data. The map is plain Web Mercator; the current lake (MLIT 国土数値情報
W09 湖沼, 諏訪湖) fits the PNG's dark-blue lake at IoU 0.975 with no rotation (fit cached in projection.json):
  - land bands from the GSI 10 m DEM (地理院タイル dem, zoom 14), lightly smoothed: 765-800 m pale, 800-900 m mid,
    above 900 m dark, the thresholds read off the PNG's colours;
  - the lake of ca. 500-1000 CE: ground below 765 m (the description's level), the parts the PNG paints as lake;
  - the current lake from W09; rivers from MLIT W05 (河川), the ones the PNG draws (the most of whose course lies on its
    light-blue river pixels);
  - all labels as real <text> (Bahnschrift, a DIN face like the PNG's) fitted to the PNG's lettering, and the two
    shrine marks (torii) as beams and posts in the PNG's red.
Run from the repo root; `fit` refits the projection and the labels."""
import io, json, math, sys, zipfile
import numpy as np, shapefile
from PIL import Image, ImageDraw
from scipy import ndimage, optimize
from shapely.geometry import shape, box, LineString

sys.path.insert(0, 'tools')

PNG = 'data_lake/downloads/lake-suwa/Size of Lake Suwa.png'
OUT = 'files/lake-suwa/Size of Lake Suwa.svg'
PAR = 'files/lake-suwa/projection.json'
DEM_DIR, Z, X0, Y0, NT = 'data_lake/downloads/gsi-dem-suwa', 14, 14472, 6428, 8
PALE, MID, HIGH, ANCIENT, CURRENT, RED = '#f6f6a8', '#e4e277', '#d8d772', '#7fbdf1', '#509ad7', '#dd2011'
LEVELS = (765, 800, 900)
FAMILY = "Bahnschrift, 'DIN Alternate', 'D-DIN', 'Arial Narrow', sans-serif"
# (text, ink box x0, x1, y0, y1, colour, kind): kind w = white on lake, b = black, r = river label (blue)
LABELS = [('LAKE SUWA (CURRENT SIZE)', 243, 608, 324, 347, '#ffffff'), ('(surface elevation: 759 m)', 265, 586, 358, 381, '#ffffff'),
          ('LAKE SUWA', 621, 771, 638, 657, '#ffffff'), ('ca. 500-1000 CE', 595, 794, 672, 691, '#ffffff'),
          ('(approx. 765 m)', 600, 790, 705, 730, '#ffffff'), ('Shimosha Akimiya', 511, 706, 46, 67, '#000000'),
          ('Kamisha Honmiya', 617, 806, 970, 991, '#000000')]
RIVER_LABELS = [('Togawa', (340, 440, 40, 75)), ('Tenryū River', (0, 110, 305, 321))]  # search regions (Tenryū's
# kept off the lake-blue pixels above it)
TORII = [(487, 504, 30, 44), (758, 776, 950, 966)]  # ink boxes of the two shrine marks
# the mark's parts as fractions of its box (measured on the first): top beam, second beam, two posts
TORII_PARTS = [(-0.03, 1.03, -0.03, 0.17), (0.05, 0.95, 0.19, 0.40), (0.05, 0.23, 0.17, 1.03), (0.77, 0.95, 0.17, 1.03)]

a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = a.shape[:2]
near = lambda c, t=30: np.abs(a - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < t

dem = np.full((NT * 256, NT * 256), np.nan)
for i in range(NT):
    for j in range(NT):
        rows = open(f'{DEM_DIR}/dem_{Z}_{X0 + i}_{Y0 + j}.txt').read().strip().split('\n')
        dem[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = [[float(c) if c != 'e' else np.nan for c in r.split(',')] for r in rows]


def merc(lon, lat):  # degrees to mosaic pixels
    n = 2 ** Z * 256
    return ((np.asarray(lon) + 180) / 360 * n - X0 * 256,
            (1 - np.arcsinh(np.tan(np.radians(np.asarray(lat)))) / np.pi) / 2 * n - Y0 * 256)


def shp(zp, stem):
    z = zipfile.ZipFile(zp)
    return shapefile.Reader(shp=io.BytesIO(z.read(stem + '.shp')), shx=io.BytesIO(z.read(stem + '.shx')),
                            dbf=io.BytesIO(z.read(stem + '.dbf')), encoding='cp932')


suwa = [shape(r.shape.__geo_interface__) for r in shp('data_lake/downloads/w09-lakes/W09-05_GML.zip', 'W09-05-g_Lake').iterShapeRecords()
        if r.record[0] == '諏訪湖'][0]
sx, sy = merc(*np.array(suwa.exterior.coords).T)
CM = (float(sx.mean()), float(sy.mean()))


def to_png(p):
    s, rot, tx, ty = p
    c, sn = math.cos(rot), math.sin(rot)
    return lambda X, Y: ((X - CM[0]) * s * c - (Y - CM[1]) * s * sn + tx, (X - CM[0]) * s * sn + (Y - CM[1]) * s * c + ty)


def fit_projection():
    cur = ndimage.binary_closing(near(CURRENT), iterations=4) | near(CURRENT)  # the white label counts as lake

    def loss(p):
        f = to_png(p)
        img = Image.new('1', (W, H), 0)
        ImageDraw.Draw(img).polygon(list(zip(*f(sx, sy))), fill=1)
        m = np.asarray(img)
        return 1 - (m & cur).sum() / (m | cur).sum()
    ys, xs = np.nonzero(cur)
    s0 = (xs.max() - xs.min()) / (sx.max() - sx.min())
    best = min((loss([s0 * k, r, xs.mean(), ys.mean()]), [s0 * k, r, xs.mean(), ys.mean()])
               for k in (0.9, 1, 1.1) for r in np.radians(np.arange(-20, 21, 5)))
    r = optimize.minimize(loss, best[1], method='Nelder-Mead', options={'maxiter': 2000, 'xatol': 1e-4, 'fatol': 1e-8})
    print('current lake IoU %.4f' % (1 - r.fun))
    return list(r.x)


def fit_labels():
    from fit_text import fit
    out = []
    for t, x0, x1, y0, y1, col in LABELS:
        q = fit(t, (x0, x1, y0, y1), 'Bahnschrift', 'normal', canvas=(W, H))
        out.append(dict(text=t, colour=col, **{k: q[k] for k in ('x', 'y', 'size', 'ls')}))
    lab = near('#519ad7', 12) & ~ndimage.binary_dilation(near(CURRENT, 12) & ~near('#519ad7', 2), iterations=0)
    for t, (x0, x1, y0, y1) in RIVER_LABELS:
        m = np.zeros_like(lab); m[y0:y1, x0:x1] = near('#519ad7', 12)[y0:y1, x0:x1]
        m = ndimage.binary_opening(m, np.ones((1, 1)))
        ys, xs = np.nonzero(m)
        q = fit(t, (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())), 'Bahnschrift', 'normal', canvas=(W, H))
        out.append(dict(text=t, colour='#519ad7', **{k: q[k] for k in ('x', 'y', 'size', 'ls')}))
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        json.dump({'p': fit_projection(), 'labels': fit_labels()}, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    s, rot, tx, ty = P['p']
    f = to_png(P['p'])
    # the DEM sampled on the PNG's pixel grid (with a margin so contours close outside the frame)
    M = 4
    py, px = np.mgrid[-M:H + M, -M:W + M] + 0.5
    c, sn = math.cos(rot), math.sin(rot)
    u, v = (px - tx) / s, (py - ty) / s
    X, Y = u * c + v * sn + CM[0], -u * sn + v * c + CM[1]
    E = ndimage.gaussian_filter(ndimage.map_coordinates(np.nan_to_num(dem, nan=759.0), [Y - 0.5, X - 0.5], order=1), 2.0)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon

    def band_d(mask_lo):
        cs = plt.contourf(px[0], py[:, 0], E, levels=[mask_lo, 1e9])
        d = []
        for path in cs.get_paths():
            for poly in path.to_polygons():
                if len(poly) > 3:
                    q = Polygon(poly).simplify(0.4)
                    if not q.is_empty:
                        d.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in q.exterior.coords[:-1]) + 'Z')
        plt.close('all')
        return ''.join(d)
    # the old lake: ground below 765 m, the components the PNG paints as lake
    low = E[M:-M, M:-M] < LEVELS[0]
    lab, n = ndimage.label(low)
    paint = near(ANCIENT, 12) | near(CURRENT, 12) | (a.min(2) > 235)
    keep = [i for i in range(1, n + 1) if (paint & (lab == i)).sum() > 0.5 * (lab == i).sum() and (lab == i).sum() > 50]
    old = np.isin(lab, keep)
    cs = plt.contourf(np.arange(W) + 0.5, np.arange(H) + 0.5, ndimage.gaussian_filter(old.astype(float), 1.0), levels=[0.5, 2])
    old_d = ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in Polygon(poly).simplify(0.4).exterior.coords[:-1]) + 'Z'
                    for path in cs.get_paths() for poly in path.to_polygons() if len(poly) > 3)
    plt.close('all')
    cur_d = 'M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(*f(sx, sy))) + 'Z'
    # rivers: W05 streams whose projected course lies mostly on the PNG's light-blue river pixels (on land)
    river_px = ndimage.binary_dilation(near(ANCIENT, 40) & ~ndimage.binary_erosion(near(ANCIENT, 12), iterations=3), iterations=2)
    rd = shp('data_lake/downloads/w05-rivers/W05-08_20_GML.zip', 'W05-08_20-g_Stream')
    rivers = []
    for r in rd.iterShapeRecords():
        g = shape(r.shape.__geo_interface__)
        if not g.intersects(box(138.0, 35.97, 138.16, 36.10)):
            continue
        xs, ys = f(*merc(*np.array(g.coords).T))
        ln = LineString(zip(xs, ys))
        pts = [ln.interpolate(t) for t in np.linspace(0, ln.length, max(2, int(ln.length / 2)))]
        inside = [(int(p.x), int(p.y)) for p in pts if 0 <= p.x < W and 0 <= p.y < H and not old[int(p.y), int(p.x)]]
        if len(inside) > 10 and np.mean([river_px[y, x] for x, y in inside]) > 0.6:
            rivers.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys)))
    texts = []
    for q in P['labels']:
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 3 else ''
        texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} fill="{q["colour"]}">{q["text"]}</text>')
    torii = []
    for x0, x1, y0, y1 in TORII:  # drawn as shapes: the ⛩ glyph in common fonts is an outline, the PNG's mark is solid
        w, h = x1 - x0 + 1, y1 - y0 + 1
        torii += [f'M{x0 + a0 * w:.2f},{y0 + b0 * h:.2f}H{x0 + a1 * w:.2f}V{y0 + b1 * h:.2f}H{x0 + a0 * w:.2f}Z'
                  for a0, a1, b0, b1 in TORII_PARTS]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{PALE}"/>',
         f'<path fill="{MID}" fill-rule="evenodd" d="{band_d(LEVELS[1])}"/>',
         f'<path fill="{HIGH}" fill-rule="evenodd" d="{band_d(LEVELS[2])}"/>',
         f'<path fill="none" stroke="{ANCIENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="{"".join(rivers)}"/>',
         f'<path fill="{ANCIENT}" fill-rule="evenodd" d="{old_d}"/>',
         f'<path fill="{CURRENT}" d="{cur_d}"/>',
         f'<path fill="{RED}" d="{"".join(torii)}"/>',
         f'<g font-family="{FAMILY}">', *texts, '</g>', '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(rivers), 'river lines,', len(keep), 'old-lake parts')
