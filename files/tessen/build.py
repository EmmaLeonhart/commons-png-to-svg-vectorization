"""Rebuild File:Tessen.png (a tessen / clematis crest) by construction, with six-fold and twelve-fold symmetry about
the disc's centre, every size measured in the PNG along rays from the centre:
  - a black disc (radius 230.75);
  - six white petals, each the lens between two circular arcs through its tip (r 224.75 on its axis), a point of its
    side (61.5 px off the axis at r 159.5) and the point where it meets its neighbour (r 140.5, 30° off its axis);
  - a black chrysanthemum of twelve petals (sectors whose tips are circles tangent to their sides, reaching r 117.5),
    parted by white radial lines (3.5 px);
  - a white ring (r 15.75-18.75) round a black centre.
Run from the repo root."""
import math

OUT = 'files/tessen/Tessen.svg'
W = H = 500
CX, CY = 250.5, 249.5
R_DISC = 230.75
TIP, SIDE, JOIN = 224.75, (61.5, 159.5), (140.5, 30)
CHRYS_TIP, GAP = 117.5, 3.5
RING_IN, RING_OUT = 15.75, 18.75


def circle3(p1, p2, p3):
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    ux = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / d
    uy = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / d
    return ux, uy, math.hypot(x1 - ux, y1 - uy)


def to_svg(x, y, rot):
    """petal-local (x right, y outward along the axis) to SVG, the axis rotated rot degrees clockwise from up"""
    t = math.radians(rot)
    return CX + x * math.cos(t) + y * math.sin(t), CY + x * math.sin(t) - y * math.cos(t)


# the right side of the top petal: a circle through the tip, the side point and the join point
jx, jy = JOIN[0] * math.sin(math.radians(JOIN[1])), JOIN[0] * math.cos(math.radians(JOIN[1]))
ux, uy, rho = circle3((0, TIP), SIDE, (jx, jy))
bottom = uy - math.sqrt(rho ** 2 - ux ** 2)  # where the two side circles cross on the axis, below the tip
petals = []
for k in range(6):
    T = to_svg(0, TIP, 60 * k)
    B = to_svg(0, bottom, 60 * k)
    petals.append(f'M{T[0]:.2f},{T[1]:.2f}A{rho:.2f},{rho:.2f} 0 0 1 {B[0]:.2f},{B[1]:.2f}'
                  f'A{rho:.2f},{rho:.2f} 0 0 1 {T[0]:.2f},{T[1]:.2f}Z')

half = math.radians(15)
tip_r = CHRYS_TIP * math.sin(half) / (1 + math.sin(half))  # tip circle tangent to the sector's sides
tip_c = CHRYS_TIP - tip_r
chrys = []
for k in range(12):
    rot = 30 * k
    a = to_svg(0, 0, rot)  # the centre
    tx, ty = tip_c * math.sin(half) * math.cos(half), tip_c * math.cos(half) ** 2  # where the tip circle meets a side
    L = to_svg(-tx, ty, rot)
    R_ = to_svg(tx, ty, rot)
    chrys.append(f'M{a[0]:.2f},{a[1]:.2f}L{L[0]:.2f},{L[1]:.2f}A{tip_r:.2f},{tip_r:.2f} 0 1 1 {R_[0]:.2f},{R_[1]:.2f}Z')
gaps = []
for k in range(12):
    p = to_svg(0, CHRYS_TIP + 2, 30 * k + 15)
    gaps.append(f'M{CX},{CY}L{p[0]:.2f},{p[1]:.2f}')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
       f'<circle cx="{CX}" cy="{CY}" r="{R_DISC}" fill="#000000"/>\n'
       f'<path fill="#ffffff" d="{"".join(petals)}"/>\n'
       f'<path fill="#000000" d="{"".join(chrys)}"/>\n'
       f'<path fill="none" stroke="#ffffff" stroke-width="{GAP}" d="{"".join(gaps)}"/>\n'
       f'<circle cx="{CX}" cy="{CY}" r="{RING_OUT}" fill="#ffffff"/>\n'
       f'<circle cx="{CX}" cy="{CY}" r="{RING_IN}" fill="#000000"/>\n</svg>\n')
open(OUT, 'w', encoding='utf8').write(svg)
print('wrote', OUT, 'side circle r %.1f, petals meet on the axis at r %.1f, chrysanthemum tip radius %.1f' % (rho, bottom, tip_r))
