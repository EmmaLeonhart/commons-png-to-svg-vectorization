"""Fit straight-edged polygons to one colour of a flat pictogram (road signs, icons made only of straight
edges): the colour mask is turned into exact pixel-square geometry (shapely), then simplified with
Douglas-Peucker so each polygon is reduced to its real corners. Meant only for shapes that are straight-
edged polygons by construction; freeform shapes are out of scope (that would be tracing).
usage (as a module): polygons(mask, tol=1.0, min_area=20) -> list of shapely Polygons; to_path_d(polys)
"""
import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union


def polygons(mask, tol=1.0, min_area=20):
    boxes = []
    for y in range(mask.shape[0]):
        r = np.nonzero(mask[y])[0]
        if len(r) == 0:
            continue
        for q in np.split(r, np.where(np.diff(r) > 1)[0] + 1):
            boxes.append(box(q[0], y, q[-1] + 1, y + 1))
    geom = unary_union(boxes)
    parts = list(geom.geoms) if hasattr(geom, 'geoms') else [geom]
    out = []
    for p in parts:
        if p.area < min_area:
            continue
        s = p.simplify(tol, preserve_topology=True)
        out.append(s)
    return out


def to_path_d(polys, nd=2):
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)[:-1]
            d.append('M' + ' L'.join(f'{x:.{nd}f},{y:.{nd}f}' for x, y in c) + 'Z')
    return ' '.join(d)


def vertex_count(polys):
    return sum(len(p.exterior.coords) - 1 + sum(len(i.coords) - 1 for i in p.interiors) for p in polys)
