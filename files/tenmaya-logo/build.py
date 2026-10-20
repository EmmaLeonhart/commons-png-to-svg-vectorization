"""Rebuild File:Tenmaya logo.png (PD-textlogo) by construction. The wordmark is drawn from strokes of slightly varied
weight with round ends and rounded corners, so each letter is built from measured primitives: rounded rectangles
(per-corner radii; a radius of half the stroke makes a round cap), arches as an outer rounded shape minus an inner one,
the N's diagonal as a parallelogram, the Y's bend as two half-ellipses, and the pink stroke inside the M as a slanted
polygon. All coordinates are pixels of the 1920x446 PNG, measured from its ink. Run from the repo root."""
OUT = 'files/tenmaya-logo/Tenmaya logo.svg'
W, H = 1920, 446
GREY, PINK = '#898989', '#ee86b4'


def rr(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0):
    """rectangle with per-corner (circular) radii, as a closed path"""
    d = f'M{x0 + tl},{y0}H{x1 - tr}'
    d += f'A{tr},{tr} 0 0 1 {x1},{y0 + tr}' if tr else ''
    d += f'V{y1 - br}' + (f'A{br},{br} 0 0 1 {x1 - br},{y1}' if br else '')
    d += f'H{x0 + bl}' + (f'A{bl},{bl} 0 0 1 {x0},{y1 - bl}' if bl else '')
    d += f'V{y0 + tl}' + (f'A{tl},{tl} 0 0 1 {x0 + tl},{y0}' if tl else '')
    return d + 'Z'


def poly(*pts):
    return 'M' + ' '.join(f'{x},{y}' for x, y in pts) + 'Z'


def arch(ox0, oy0, ox1, otl, otr, ix0, iy0, ix1, itl, itr, bottom=300):
    """an arch: outer rounded top minus inner rounded top (even-odd), open at the bottom (stems added separately)"""
    return rr(ox0, oy0, ox1, bottom, otl, otr) + rr(ix0, iy0, ix1, bottom, itl, itr)


solid = []   # grey, nonzero
holes = []   # grey shapes that need even-odd (arches, the Y bend)
# T
solid += [rr(66, 10, 307, 55, 22.5, 22.5, 22.5, 22.5), rr(160, 40, 215, 431, 0, 0, 27.5, 27.5)]
# E: the stem with rounded outer corners, three bars with round right ends
solid += [rr(339, 10, 396, 432, 52, 0, 0, 52), rr(385, 10, 527, 56, 0, 23, 23, 0),
          rr(385, 179, 506, 224, 0, 22.5, 22.5, 0), rr(385, 382, 526, 432, 0, 25, 25, 0)]
# N: stems and the diagonal (left edge x = 664 + 0.29 (y - 300), right edge x = 662 + 0.29 (y - 90))
lx = lambda y: 664 + 0.29 * (y - 300)
rx = lambda y: 662 + 0.29 * (y - 90)
solid += [rr(576, 10, 623, 432, 30, 0, 24, 24), rr(716, 10, 763, 432, 24, 24, 30, 20),
          poly((lx(20), 20), (rx(20) - 8, 20), (rx(40), 40), (rx(370), 370), (728, 431), (712, 425), (lx(395), 395)),
          rr(576, 10, 640, 60, 30, 20, 0, 0)]
# M: arch (square top-left, wide top-right), stems with round ends
holes.append(arch(834, 15, 1088, 12, 85, 889, 58, 1031, 0, 38))
solid += [rr(834, 200, 889, 432, 0, 0, 27.5, 27.5), rr(1031, 200, 1088, 432, 0, 0, 29, 29)]
# A (twice): round-topped arch, crossbar, stems with round ends
for (o0, o1, i0, i1, cb0, cb1) in ((1160, 1342, 1204, 1291, 246, 293), (1663, 1848, 1706, 1792, 247, 293)):
    holes.append(arch(o0, 13, o1, 88, 88, i0, 58, i1, 40, 40))
    solid += [rr(i0 - 1, cb0, i1 + 1, cb1), rr(o0, 200, i0, 431, 0, 0, (i0 - o0) / 2, (i0 - o0) / 2),
              rr(i1, 200, o1, 431, 0, 0, (o1 - i1) / 2, (o1 - i1) / 2)]
# Y: two arms with round tops, the bend (outer half-ellipse 92x80 minus inner 40.5x28), the stem with a round end
solid += [rr(1409, 10, 1456, 222, 23.5, 23.5), rr(1537, 10, 1594, 222, 28.5, 28.5),
          rr(1472, 270, 1529, 431, 0, 0, 28.5, 28.5)]
holes.append('M1409,200V220A92,80 0 0 0 1594,220V200Z' + 'M1456,200V220A40.5,28 0 0 0 1537,220V200Z')
# the pink stroke inside the M: slanted top, small rounded foot
pink = poly((932, 124), (978, 73), (991, 72), (995, 76), (995, 428), (990, 433), (937, 433), (932, 428))

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<path fill="{GREY}" d="{"".join(solid)}"/>\n'
       + ''.join(f'<path fill="{GREY}" fill-rule="evenodd" d="{h}"/>\n' for h in holes)
       + f'<path fill="{PINK}" d="{pink}"/>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT)
