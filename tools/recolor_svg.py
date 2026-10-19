"""Recolour a tincture in an existing Sodacan-style SVG with Emma's generator's own recolor()
(imported read-only), for arms whose only difference from a Commons SVG is a tincture.
usage: python tools/recolor_svg.py in.svg out.svg or:argent [src:dst ...]
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))
import generator_render  # noqa: E402,F401  (puts the generator on sys.path)
from arms.render import recolor  # noqa: E402

src, dst, *swaps = sys.argv[1:]
svg = Path(src).read_text(encoding='utf8')
for s in swaps:
    a, b = s.split(':')
    svg = recolor(svg, a, b)
Path(dst).write_text(svg, encoding='utf8')
print(f'{dst}: {", ".join(swaps)}')
