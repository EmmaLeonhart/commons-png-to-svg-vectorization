"""Rebuild File:Map-okinawa-pref.png from MLIT 国土数値情報 N03 (2024) boundaries of Okinawa Prefecture: the islands in an
equirectangular projection (x scaled by cos 25.5°) fitted to the PNG's land mask, flat green (the PNG's islands carry
relief shading from a raster render, which is not reproduced), a dark green coast on the PNG's #ceffff sea, the star at
Naha, and every label as real <text> (transcribed; English in black or blue italic, Japanese below) fitted to the PNG's
lettering. Run from the repo root."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import optimize
from shapely.geometry import shape, box
from shapely.ops import unary_union, transform as stransform

sys.path.insert(0, 'tools')
from n03_prefecture_svg import load  # noqa: E402
from fit_text import fit  # noqa: E402

PNG = 'data_lake/downloads/map-okinawa-pref/Map-okinawa-pref.png'
OUT = 'files/map-okinawa-pref/Map-okinawa-pref.svg'
PAR = 'files/map-okinawa-pref/projection.json'
SEA, LAND, COAST, BLUE = '#ceffff', '#8ddc8d', '#4d7a4d', '#0000ff'
COS = np.cos(np.radians(25.5))

im = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
H, W = im.shape[:2]
land_px = (im[..., 1] > im[..., 2] + 15) & (im[..., 1] > im[..., 0] + 10)
text_px = im.sum(2) < 300

geo = unary_union([shape(f['geometry']) for f in load(47)['features']]).intersection(box(122, 24, 129.5, 27.5))  # the map leaves out the Daito Islands
isl = [g for g in (geo.geoms if hasattr(geo, 'geoms') else [geo]) if g.area > 2e-7]


def proj(p):
    if len(p) == 3:
        p = [p[0], p[0], p[1], p[2]]
    sx, sy, tx, ty = p  # separate scales: the PNG's source map is not quite equirectangular at cos 25.5
    return lambda x, y, z=None: (np.asarray(x) * COS * sx + tx, -np.asarray(y) * sy + ty)


def raster(f):
    img = Image.new('1', (W, H), 0)
    d = ImageDraw.Draw(img)
    for g in isl:
        q = stransform(f, g)
        d.polygon(list(q.exterior.coords), fill=1)
        for r in q.interiors:
            d.polygon(list(r.coords), fill=0)
    return np.asarray(img)


def loss(p):
    m = raster(proj(p)) & ~text_px
    t = land_px & ~text_px
    return 1 - (m & t).sum() / (m | t).sum()


# (texts top to bottom, box x0, x1, y0, y1, colour, italic, size hint); a box holding two lines is split at its gap
LABELS = [(['Okinawa Prefecture'], 59, 327, 25, 45, '#000000', False), (['沖縄県'], 60, 137, 55, 80, '#000000', False),
          (['Okinawa Islands'], 568, 734, 32, 48, BLUE, True), (['沖縄諸島'], 612, 691, 55, 73, BLUE, False),
          (['Kume', '久米島'], 556, 603, 108, 143, '#000000', False), (['Naha', '那覇'], 711, 743, 116, 142, '#000000', False),
          (['Okinawa'], 802, 869, 130, 141, '#000000', False), (['Island'], 812, 859, 150, 161, '#000000', False),
          (['沖縄本島'], 809, 867, 169, 181, '#000000', False), (['Kerama Is.', '慶良間諸島'], 635, 708, 161, 189, BLUE, True),
          (['Senkaku'], 171, 237, 201, 213, '#000000', False), (['尖閣諸島'], 171, 237, 222, 236, '#000000', False),
          (['Miyako Islands'], 313, 464, 274, 289, BLUE, True), (['宮古諸島'], 349, 430, 296, 315, BLUE, False),
          (['Yaeyama Islands', '八重山諸島'], 71, 241, 324, 365, BLUE, True),
          (['Miyako', '宮古島'], 388, 441, 372, 404, '#000000', False),
          (['Yonaguni'], 31, 102, 415, 430, '#000000', False), (['与那国島'], 33, 99, 436, 449, '#000000', False),
          (['Ishigaki', '石垣島'], 237, 298, 422, 454, '#000000', False),
          (['Iriomote'], 121, 191, 430, 441, '#000000', False), (['西表島'], 134, 178, 449, 461, '#000000', False)]


def lines_of(texts, x0, x1, y0, y1, col):
    """split a two-line box at its widest empty row band and measure each line's ink box"""
    tm = (np.abs(im[y0:y1 + 1, x0:x1 + 1] - [int(col[i:i + 2], 16) for i in (1, 3, 5)]).sum(2) < 200) & \
         (im[y0:y1 + 1, x0:x1 + 1].sum(2) < 600)
    rows = np.nonzero(tm.any(1))[0]
    if len(texts) == 1:
        return [(texts[0], x0, x1, y0 + rows.min(), y0 + rows.max())]
    gaps = np.diff(rows)
    k = int(np.argmax(gaps))
    out = []
    for t, (r0, r1) in zip(texts, [(rows[0], rows[k]), (rows[k + 1], rows[-1])]):
        cols = np.nonzero(tm[r0:r1 + 1].any(0))[0]
        out.append((t, x0 + cols.min(), x0 + cols.max(), y0 + r0, y0 + r1))
    return out


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'fit':
        x0, y0, x1, y1 = geo.bounds
        ys, xs = np.nonzero(land_px)
        s = (xs.max() - xs.min()) / ((x1 - x0) * COS)
        p0 = [s, xs.min() - x0 * COS * s, ys.min() + y1 * s]
        r = optimize.minimize(loss, p0, method='Nelder-Mead', options={'maxiter': 800, 'xatol': 1e-3, 'fatol': 1e-7})
        fits = []
        for texts, a, b, c, d, col, it in LABELS:
            for t, la, lb, lc, ld in lines_of(texts, a, b, c, d, col):
                fam = 'Arial' if not any(ord(ch) > 0x3000 for ch in t) else 'MS Gothic'
                fam_full = fam + (';font-style:italic' if it and fam == 'Arial' else '')
                q = fit(t, (la, lb, lc, ld), fam_full, 'normal', canvas=(W, H))
                fits.append(dict(text=t, colour=col, italic=it and fam == 'Arial', cjk=fam != 'Arial', **q))
        json.dump({'p': list(r.x), 'labels': fits}, open(PAR, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    P = json.load(open(PAR, encoding='utf8'))
    f = proj(P['p'])
    print('land IoU %.4f' % (1 - loss(P['p'])))
    d = ''.join('M' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in r.coords) + 'Z'
                for g in isl for q in [stransform(f, g.simplify(0.0003))] for r in [q.exterior, *q.interiors])
    texts = []
    for q in P['labels']:
        fam = "'MS Gothic', 'IPAGothic', 'Noto Sans CJK JP', sans-serif" if q['cjk'] else "Arial, 'Liberation Sans', sans-serif"
        st = ' font-style="italic"' if q['italic'] else ''
        ls = f' letter-spacing="{q["ls"]}"' if 0.05 < abs(q['ls']) < 2.5 else ''  # larger fits are box errors
        texts.append(f'<text x="{q["x"]}" y="{q["y"]}" font-family="{fam}"{st} font-size="{q["size"]}"{ls} '
                     f'fill="{q["colour"]}">{q["text"]}</text>')
    nx, ny = f(127.68, 26.21)  # Naha
    star = ' '.join(f'{float(nx) + r * np.sin(np.pi * k / 5):.1f},{float(ny) - r * np.cos(np.pi * k / 5):.1f}'
                    for k, r in zip(range(10), [5.5, 2.2] * 5))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SEA}"/>',
         f'<path d="{d}" fill="{LAND}" stroke="{COAST}" stroke-width="0.8" stroke-linejoin="round"/>',
         f'<polygon points="{star}" fill="#000000"/>', *texts, '</svg>']
    open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
    print('wrote', OUT, len(isl), 'islands,', len(texts), 'labels')
