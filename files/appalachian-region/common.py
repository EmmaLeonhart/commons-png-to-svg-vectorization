"""Shared pieces for the Appalachian region rebuild: census 2018 cartographic boundaries (PD, US Census
Bureau, 1:5M), an Albers conic projection followed by a similarity transform onto the PNG's pixels, and
SVG path output."""
import io, zipfile
import numpy as np, resvg_py, shapefile
from PIL import Image
from shapely.geometry import shape, box
from shapely import affinity

PNG = 'data_lake/downloads/appalachian-region/Appalachian region of United States.png'
W, H = 570, 585
VIEW = box(-93.5, 29.0, -71.0, 45.5)
FIPS_SKIP = {'02', '15', '60', '66', '69', '72', '78'}


def read(name):
    z = zipfile.ZipFile(f'data_lake/downloads/census/{name}.zip')
    r = shapefile.Reader(shp=io.BytesIO(z.read(name + '.shp')), shx=io.BytesIO(z.read(name + '.shx')),
                         dbf=io.BytesIO(z.read(name + '.dbf')))
    out = []
    for sr in r.iterShapeRecords():
        rec = sr.record.as_dict()
        if rec['STATEFP'] in FIPS_SKIP:
            continue
        g = shape(sr.shape.__geo_interface__)
        if g.intersects(VIEW):
            out.append((rec, g))
    return out


def albers(lon0, lat0, lat1=29.5, lat2=45.5):
    p = np.radians
    n = (np.sin(p(lat1)) + np.sin(p(lat2))) / 2
    C = np.cos(p(lat1)) ** 2 + 2 * n * np.sin(p(lat1))
    rho0 = np.sqrt(C - 2 * n * np.sin(p(lat0))) / n

    def f(lon, lat):
        rho = np.sqrt(C - 2 * n * np.sin(p(lat))) / n
        th = n * p(lon - lon0)
        return rho * np.sin(th), rho0 - rho * np.cos(th)
    return f


def projector(params):
    lon0, lat0, s, rot, tx, ty = params
    f = albers(lon0, lat0)
    c, si = np.cos(np.radians(rot)), np.sin(np.radians(rot))

    def proj(lon, lat):
        x, y = f(np.asarray(lon), np.asarray(lat))
        X = s * (c * x - si * y) + tx
        Y = -s * (si * x + c * y) + ty
        return X, Y
    return proj


def path(geom, proj, tol=0.0):
    if tol:
        geom = geom.simplify(tol, preserve_topology=True)
    parts = []

    def ring(coords, close):
        xy = np.asarray(coords)
        X, Y = proj(xy[:, 0], xy[:, 1])
        return 'M' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in zip(X, Y)) + ('Z' if close else '')
    for g in getattr(geom, 'geoms', [geom]):
        if g.geom_type == 'Polygon':
            parts.append(ring(g.exterior.coords, True))
            parts += [ring(i.coords, True) for i in g.interiors]
        elif g.geom_type in ('LineString', 'LinearRing'):
            parts.append(ring(g.coords, False))
        elif hasattr(g, 'geoms'):
            parts.append(path(g, proj))
    return ''.join(parts)


def render(svg, fonts=None):
    im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=fonts or [])))).convert('RGBA')
    return np.asarray(Image.alpha_composite(Image.new('RGBA', im.size, 'white'), im).convert('RGB')).astype(int)
