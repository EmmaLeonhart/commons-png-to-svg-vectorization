"""Recover the five plotted functions of File:CompareTropicalYears.png: for each colour, the centre of
the curve in every pixel column where it is not covered by another curve, converted to (year, days) by
the measured axes, then the lowest-degree polynomial in t = year/1000 whose residual is under half a
pixel. The source (Meeus 2002, ch. 63, after Simon et al. 1994) gives these lengths as polynomials, so
this recovers the drawn functions rather than tracing their pixels. Writes curves.json."""
import json
import numpy as np
from PIL import Image

PNG = 'data_lake/downloads/compare-tropical-years/CompareTropicalYears.png'
a = np.asarray(Image.open(PNG).convert('RGB')).astype(int)
X0, X1, Y0, Y1 = 129, 928, 44, 443          # plot frame
year = lambda px: -6000 + (px - X0) * 16000 / (X1 - X0)
days = lambda py: 365.2412 + (Y1 - py) * 0.0001 / 19  # 19 px per 0.0001 day (labels 38 px per 0.0002)
COLOURS = {'spring': (66, 174, 66), 'autumn': (148, 81, 41), 'summer': (255, 195, 33),
           'winter': (156, 182, 206), 'mean360': (66, 65, 66)}
out = {}
for key, c in COLOURS.items():
    m = (np.abs(a - c).max(-1) < 40)
    m[:Y0 + 1] = False
    m[Y1:] = False
    xs, ys = [], []
    for x in range(X0 + 1, X1):
        col = np.nonzero(m[:, x])[0]
        if 2 <= len(col) <= 5 and np.ptp(col) <= 5:  # a clean crossing of the column, not a crowded one
            xs.append(x)
            ys.append(col.mean() + 0.5)
    xs, ys = np.array(xs), np.array(ys)
    t = np.array([year(x + 0.5) for x in xs]) / 1000
    v = np.array([days(y) for y in ys])
    for deg in range(1, 8):
        p = np.polyfit(t, v, deg)
        res_px = (np.polyval(p, t) - v) / 0.0001 * 19
        rms = float(np.sqrt((res_px ** 2).mean()))
        if rms < 0.5:
            break
    out[key] = {'coef': list(p), 'degree': deg, 'rms_px': rms, 'columns': len(xs)}
    print(key, 'degree', deg, 'rms %.2f px' % rms, 'columns', len(xs))
json.dump(out, open('files/compare-tropical-years/curves.json', 'w'), indent=1)
