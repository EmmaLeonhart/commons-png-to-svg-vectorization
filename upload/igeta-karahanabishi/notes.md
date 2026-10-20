# File:井桁に唐花菱.png → SVG

Igeta ni karahanabishi (井桁に唐花菱), a kamon: a karahana lozenge inside a well frame. Rebuilt by construction in
`files/igeta-karahanabishi/build.py`, not traced:
- In a square (u, v) space the crest is regular. The frame is a 井 of four bars (half-spacing c, width t, half-length L),
  and its hole is a square.
- The karahana has four petals. Each is the union of a tip circle, two side-lobe circles and their hull to the centre,
  clipped to its quadrant.
- One affine map squashes the square space into the PNG's lozenge (horizontal 1859, vertical 1396 px per unit).
- The centre ring, the midribs (round caps) and the petal separators are strokes of constant width, drawn in image space
  as in the PNG.
- The handful of parameters are fitted to the PNG's white mask. The frame's IoU is 0.99, and the whole crest's is 0.97.
  The PNG's side lobes bulge slightly more toward the separators than circles allow.

Colours are the PNG's: field #00081a, figure #f3f3f2. Saved locally as `Igeta ni karahanabishi.svg`; on Commons it
would be File:井桁に唐花菱.svg. Comparison:
`Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_igeta-karahanabishi.png`.

Licence: CC BY-SA 4.0, as the PNG ({{self|cc-by-sa-4.0}}, MLFU5BrYMJ2).
