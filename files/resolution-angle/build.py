"""Rebuild File:Resolution angle.png by construction: waves from a source S spread as alternating black and white rings
(2 px); an opaque bar ends at T straight above S. Right of the vertical through S the rings are circles about S; on the
left, rings small enough to pass under the bar continue about S, and larger ones continue in the bar's shadow as arcs
about T (radius r - |ST|, so they join at the vertical). Cyan arrows: eight short spokes around S, two long rays from
S and the diffracted ray from T; the olive vertical and arc mark the angle θ (real <text>) between the vertical and
that ray. The PNG is hand-drawn in Paint; the ring radii are the ones it shows on the vertical above S, drawn as exact
circles. Run from the repo root."""
import sys
import numpy as np

sys.path.insert(0, 'tools')
from fit_text import fit  # noqa: E402

OUT = 'files/resolution-angle/Resolution angle.svg'
W, H = 179, 120
BG, CYAN, BAR, OLIVE = '#c0c0c0', '#00ffff', '#800000', '#808000'
S = (71.5, 100.0)
T = (71.5, 61.0)
ST = S[1] - T[1]
BAR_X0, BAR_Y1 = 4.0, 66.0
# ring radii about S read on the vertical above S (the PNG's 2 px runs, centre to centre), innermost first; the
# innermost ring is black, then they alternate
RINGS = [3.5, 6.5, 10.5, 15.5, 19.5, 24.5, 28.5, 32.5, 37.5, 42.5, 48.5, 54.5, 59.5, 63.5, 69.5, 75.5]
RAYS_S = [(176.5, 85.5), (146.5, 27.5)]  # long rays from S, tips measured
RAY_T = (26.0, 23.0)  # the diffracted ray from T, tip measured
SPOKE = 18.0
THETA_R = 43.5  # the olive arc about T


def arc(c, r, a0, a1):
    """SVG arc about c from angle a0 to a1 (degrees, counterclockwise from +x, y up)"""
    p0 = (c[0] + r * np.cos(np.radians(a0)), c[1] - r * np.sin(np.radians(a0)))
    p1 = (c[0] + r * np.cos(np.radians(a1)), c[1] - r * np.sin(np.radians(a1)))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f'M{p0[0]:.2f},{p0[1]:.2f}A{r:.2f},{r:.2f} 0 {large} 0 {p1[0]:.2f},{p1[1]:.2f}'


def arrow(p, q, head=5.0):
    dx, dy = q[0] - p[0], q[1] - p[1]
    a = np.arctan2(dy, dx)
    h = ''.join(f'M{q[0]:.2f},{q[1]:.2f}L{q[0] - head * np.cos(a + s):.2f},{q[1] - head * np.sin(a + s):.2f}'
                for s in (np.radians(30), -np.radians(30)))
    return f'M{p[0]:.2f},{p[1]:.2f}L{q[0]:.2f},{q[1]:.2f}' + h


rings = {'#000000': [], '#ffffff': []}
for i, r in enumerate(RINGS):
    col = '#000000' if i % 2 == 0 else '#ffffff'
    d = arc(S, r, 0, 90)
    if r < ST:  # passes under the bar: the left quarter about S
        d += arc(S, r, 90, 180)
    elif r - ST > 0.5:  # in the bar's shadow: the left quarter about T
        d += arc(T, r - ST, 90, 180)
    rings[col].append(d)
cyan = [arrow(S, (S[0] + SPOKE * np.cos(np.radians(a)), S[1] - SPOKE * np.sin(np.radians(a)))) for a in range(0, 360, 45)]
cyan += [arrow(S, q) for q in RAYS_S] + [arrow(T, RAY_T)]
ray_ang = np.degrees(np.arctan2(T[1] - RAY_T[1], RAY_T[0] - T[0]))
q = fit('θ', (44, 53, 4, 16), "'Times New Roman'", 'normal', canvas=(W, H))
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="{BG}"/>',
     *[f'<path fill="none" stroke="{c}" stroke-width="2" d="{"".join(ds)}"/>' for c, ds in rings.items()],
     f'<rect x="{BAR_X0}" y="{T[1]}" width="{T[0] - BAR_X0}" height="{BAR_Y1 - T[1]}" fill="{BAR}"/>',
     f'<path fill="none" stroke="{OLIVE}" stroke-width="1" d="M{T[0]},{T[1]}V7{arc(T, THETA_R, 90, ray_ang)}"/>',
     f'<path fill="none" stroke="{CYAN}" stroke-width="1" stroke-linecap="round" d="{"".join(cyan)}"/>',
     f'<text x="{q["x"]}" y="{q["y"]}" font-family="\'Times New Roman\', \'Liberation Serif\', serif" '
     f'font-size="{q["size"]}" fill="#000000">θ</text>',
     '</svg>']
open(OUT, 'w', encoding='utf8').write('\n'.join(o) + '\n')
print('wrote', OUT, 'θ ray at %.1f° from the vertical' % (ray_ang - 90))
