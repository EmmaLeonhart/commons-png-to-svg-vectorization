# File:Abusir map.png → SVG

Rebuilt, not traced. Steps (run from the repo root, in order):
`python files/abusir-map/geometry.py`, `PYTHONPATH=files/abusir-map python files/abusir-map/refine.py`,
`python files/abusir-map/build.py`.

- **Structures, causeways, river, scale bar** from [[:File:AbusirAndAbuGurabPlan ru.svg]] (CC BY-SA 3.0, a
  Russian redrawing of this PNG): registered to the PNG (scale 1.014, chamfer 3.5 px), then each element
  shifted by up to a few pixels and its stroke width scaled to the PNG's (`elements.json`). The river is
  set to the PNG's 3 px; its line is the ru file's smooth curve, where the PNG's is jagged.
- **Necropolis area**: an ellipse fitted to the PNG's grey (#8a8484) loop.
- **North arrow**: measured from the PNG.
- **Labels**: 36 lines of real `<text>` in DejaVu Sans (the font Commons renders), size 14.5 for the body
  labels from their ink widths, the place names and small labels sized on their own; each stacked label
  centred and spaced 19 px as in the PNG.
- **Leader lines**: straight segments fitted to the ink left after everything else, kept only where they
  touch a label (3.5 px); the Sahure leader, mostly inside its pyramid, measured by hand.

Known differences: the Unfinished Pyramid's inner outline follows the ru drawing, not the PNG's; the
causeways are the ru file's double lines, thinner than the PNG's; the river is smooth.
Licence: CC BY-SA 3.0 (from the ru SVG; the PNG itself is public domain). Credit: User:Markh (PNG) and the
author of AbusirAndAbuGurabPlan ru.svg.
