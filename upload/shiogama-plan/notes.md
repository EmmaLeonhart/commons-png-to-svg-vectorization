# File:Shiogama Jinja plan.png → SVG

Built by construction (`files/shiogama-plan/build.py`), as for the Kōfukuji plan. The plan is axis-parallel lines of
two kinds:
- Dark outlines: 1 px black lines drawn anti-aliased between pixel rows, about 0.66 px of coverage. Each is measured
  at its darkness-weighted sub-pixel position.
- Light paths and stair treads: 1 px #c1c1c1 lines on the pixel grid.

Every horizontal and vertical run becomes an exact segment: 148 dark, 70 light. The two small circles at the foot of
the steps are fitted. Mean absolute pixel difference against the PNG is 0.32 (of 255).

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_shiogama-plan.png`.

Licence: CC0, as the PNG (Pel macolato).
