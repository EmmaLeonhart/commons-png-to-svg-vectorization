"""Rebuild the Yamanashi district locator maps (File:Yamanashi Koma-gun.png, File:Yamanashi Yamanashi-gun.png; both cut
from Yamanashi-pref.png, Template:Japan map) from MLIT 国土数値情報 N03: current (2024) municipalities of Yamanashi
white with black borders, the neighbouring prefectures grey, prefecture borders red, the Meiji-era district yellow:
the union of its 1920 municipalities (N03 1920, when the districts of 1878 still stood; Koma = 北・中・南巨摩郡,
Yamanashi = 東・西山梨郡), with the grey line the PNG draws where the old district edge cuts a current municipality;
the larger W09 lakes of Yamanashi (the Fuji Five Lakes; the PNG shows no others) in cyan with a blue rim, as is
the sea (Sagami Bay, at the bottom-right edge); the legend (現在 / 明治期 / 郡役所) constructed, its labels real <text>. Equirectangular
projection fitted to the PNG's Yamanashi land mask. Run from the repo root: build.py SLUG [fit], SLUG koma or
yamanashi."""
import io, json, sys, zipfile
import numpy as np, shapefile
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

SLUG = sys.argv[1]
NAME = {'koma': 'Yamanashi Koma-gun', 'yamanashi': 'Yamanashi Yamanashi-gun'}[SLUG]
GUN = {'koma': ('北巨摩郡', '中巨摩郡', '南巨摩郡'), 'yamanashi': ('東山梨郡', '西山梨郡')}[SLUG]
PNG = f'data_lake/downloads/yamanashi-{SLUG}-gun/{NAME}.png'
OUT = f'files/yamanashi-gun/{NAME}.svg'
PAR = f'files/yamanashi-gun/{SLUG}.json'
WHITE, GREY, LEG, YELLOW, PEACH, GREEN, RED, OLD = '#ffffff', '#d2d2d2', '#dedede', '#ffff00', '#ffd48e', '#00ff00', '#fe0000', '#c0c0c0'
LAKE, RIM = '#64fefe', '#0000ff'
COS = np.cos(np.radians(35.6))
VIEW = box(137.8, 34.8, 139.8, 36.4)
LEGEND = (119, 110, 171, 144)

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
near = lambda c, t=12: np.abs(im - [int(c[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < t
in_legend = np.zeros((H, W), bool)
in_legend[LEGEND[1]:LEGEND[3] + 1, LEGEND[0]:LEGEND[2] + 1] = True
yellow_px = near(YELLOW) & ~in_legend
pref_px = (near(WHITE) | yellow_px | near(OLD) | near(LAKE, 20) | near(RIM)) & ~in_legend
known = ~(near('#000000', 60) | near(RED, 30) | in_legend)


def shp(z, base, enc='cp932'):
    return shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), shx=io.BytesIO(z.read(base + '.shx')),
                            dbf=io.BytesIO(z.read(base + '.dbf')), encoding=enc)


def load(path, base, enc='cp932'):
    out = {}
    for sr in shp(zipfile.ZipFile(path), base, enc).iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(VIEW):
            out.setdefault((*sr.record[:4], sr.record[-1]), []).append(g.intersection(VIEW))
    return {k: unary_union(v).buffer(0) for k, v in out.items()}


now = {}
for c in ('19', '10', '11', '13', '14', '20', '22'):
    now.update({(c, *k): g for k, g in load(f'data_lake/downloads/n03/N03-20240101_{c}_GML.zip', f'N03-20240101_{c}', 'utf8').items()})
old = load('data_lake/downloads/n03/1920/N03-200101_19_GML.zip', 'N03-200101_19-g_AdministrativeBoundary')
prefs = {c: unary_union([g for k, g in now.items() if k[0] == c]) for c in ('19', '10', '11', '13', '14', '20', '22')}
yam = prefs['19']
lk = shp(zipfile.ZipFile('data_lake/downloads/w09-lakes/W09-05_GML.zip'), 'W09-05-g_Lake')
lakes = unary_union([g for g in (shape(r.shape.__geo_interface__).buffer(0) for r in lk.iterShapeRecords())
                     if yam.contains(g.centroid) and g.area > 4e-5])


def proj(p):
    sx, sy, tx, ty = p
    return lambda x, y, z=None: (np.asarray(x) * COS * sx + tx, -np.asarray(y) * sy + ty)


def polys(g):
    return [q for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon' and not q.is_empty]


def raster(g, f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for q in polys(stransform(f, g)):
        d.polygon(list(q.exterior.coords), fill=1)
        for rr in q.interiors:
            d.polygon(list(rr.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(yam, proj(p))
    return 1 - ((m & pref_px) & known).sum() / ((m | pref_px) & known).sum()


def d_of(g, f):
    return ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in rr.coords) + 'Z'
                   for q in polys(stransform(f, g)) for rr in [q.exterior, *q.interiors])


def line_d(g, f):
    out = []
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.geom_type == 'LineString':
            out.append('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in stransform(f, q).coords))
        elif hasattr(q, 'geoms'):
            out.append(line_d(q, f))
    return ''.join(out)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'fit':
        ys, xs = np.nonzero(pref_px)
        b = yam.bounds
        sx = (xs.max() - xs.min()) / ((b[2] - b[0]) * COS)
        sy = (ys.max() - ys.min()) / (b[3] - b[1])
        p0 = [sx, sy, xs.min() - b[0] * COS * sx, ys.min() + b[3] * sy]
        r = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 1500, 'xatol': 1e-3, 'fatol': 1e-7})
        f = proj(r.x)
        rows = []
        bk = near('#000000', 60)
        for t, (a, c) in zip(['現在', '明治期', '郡役所'], [(111, 121), (122, 132), (133, 143)]):
            yy, xx = np.nonzero(bk[a:c + 1, 137:LEGEND[2]])
            rows.append(fit(t, (137 + xx.min(), 137 + xx.max(), a + yy.min(), a + yy.max()), 'MS Gothic', 'normal',
                            canvas=(W, H)))
        json.dump({'p': list(r.x), 'iou': 1 - r.fun, 'legend': rows},
                  open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    f = proj(P['p'])
    print('Yamanashi IoU %.4f' % P['iou'])
    # the old district, trimmed to the current prefecture outline (the 1920 data is drawn less finely)
    yellow = unary_union([g for k, g in old.items() if k[2] in GUN]).buffer(0).intersection(yam).buffer(0)
    m = raster(yellow, f) & (yellow_px | near(WHITE))
    print('%d municipalities of 1920; yellow agreement %.3f' % (sum(k[2] in GUN for k in old), (m & yellow_px).sum() / ((m | yellow_px) & (yellow_px | near(WHITE))).sum()))
    borders = unary_union([g.boundary for k, g in now.items()])
    pref_b = unary_union([prefs[a].boundary.intersection(prefs[b].buffer(0.001))
                          for a in prefs for b in prefs if a < b])
    old_edge = yellow.boundary.intersection(yam.buffer(-0.002))
    lx0, ly0, lx1, ly1 = LEGEND
    leg = [f'<rect x="{lx0}" y="{ly0}" width="{lx1 - lx0 + 1}" height="{ly1 - ly0 + 1}" fill="{LEG}"/>',
           f'<rect x="121" y="113" width="13" height="7" fill="{GREEN}"/>',
           f'<rect x="121" y="124" width="13" height="7" fill="{PEACH}"/>',
           f'<path fill="{YELLOW}" d="M121,124h5l3,7h-8z"/>',
           f'<circle cx="127.5" cy="139.5" r="2.2" fill="none" stroke="#ff0000" stroke-width="1"/>']
    for t, q in zip(['現在', '明治期', '郡役所'], P['legend']):
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 3 else ''
        leg.append(f'<text x="{q["x"]}" y="{q["y"]}" font-size="{q["size"]}"{ls} '
                   "font-family=\"'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif\">" + t + '</text>')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{LAKE}"/>',
         f'<path fill="{GREY}" d="{d_of(unary_union(list(prefs.values())), f)}"/>',
         f'<path fill="{WHITE}" d="{d_of(yam, f)}"/>',
         f'<path fill="{YELLOW}" d="{d_of(yellow, f)}"/>',
         f'<path fill="none" stroke="{OLD}" stroke-width="1" d="{line_d(old_edge, f)}"/>',
         f'<path fill="none" stroke="#000000" stroke-width="0.8" d="{line_d(borders, f)}"/>',
         f'<path fill="none" stroke="{RED}" stroke-width="1" d="{line_d(pref_b, f)}"/>',
         f'<path fill="{LAKE}" stroke="{RIM}" stroke-width="0.8" stroke-linejoin="round" d="{d_of(lakes, f)}"/>',
         f'<path fill="none" stroke="{RIM}" stroke-width="1" d="{line_d(unary_union(list(prefs.values())).boundary.intersection(box(*VIEW.bounds).buffer(-0.01)), f)}"/>',
         *leg, '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT)
