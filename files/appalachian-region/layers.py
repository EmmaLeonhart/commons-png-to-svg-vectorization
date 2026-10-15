"""Map layers (no text): states in the PNG's blue, the Appalachian counties (members.json) white with the
region's thick black outline, state lines #333, all clipped to the map frame. Imported by build.py."""
import json
from shapely.geometry import Polygon
from shapely.ops import unary_union
import common as C

P = json.load(open('files/appalachian-region/projection.json'))
proj = C.projector(P)
members = set(json.load(open('files/appalachian-region/members.json')))
counties = C.read('cb_2018_us_county_5m')
states = C.read('cb_2018_us_state_20m')  # generalised coast, as the PNG
region = unary_union([g for rec, g in counties if rec['GEOID'] in members]).buffer(0.0005).buffer(-0.0005)
land = unary_union([g for _, g in states])
state_lines = unary_union([g.boundary for _, g in states]).intersection(land.buffer(-0.01))
TOL = 0.004


def layers():
    return (f'<clipPath id="map"><rect x="0.5" y="33.5" width="569" height="536"/></clipPath>'
            f'<g clip-path="url(#map)">'
            f'<path id="states" d="{C.path(land, proj, TOL)}" fill="#87a4c7"/>'
            f'<path id="appalachia" d="{C.path(region, proj, TOL)}" fill="#fff"/>'
            f'<path id="state-lines" d="{C.path(state_lines, proj, TOL)}" fill="none" stroke="#333" stroke-width="1"/>'
            f'<path id="region-outline" d="{C.path(region, proj, TOL)}" fill="none" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>'
            f'</g><rect x="0.5" y="33.5" width="569" height="536" fill="none" stroke="#333" stroke-width="1"/>')


if __name__ == '__main__':
    import numpy as np
    from PIL import Image
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{C.W}" height="{C.H}"><rect width="{C.W}" height="{C.H}" fill="#fff"/>{layers()}</svg>'
    o = C.render(svg)
    a = np.asarray(Image.open(C.PNG).convert('RGB')).astype(int)
    print('pixels differing %.4f' % (np.abs(o - a).max(-1) > 64).mean())
    Image.fromarray(np.concatenate([a, o], 1).astype(np.uint8)).save('scratch/arms/app_layers.png')
