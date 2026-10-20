# File:World map green.png → SVG

A plain green world map, rebuilt from Natural Earth 10m land (public domain) in the Robinson projection, with scales
and offset fitted to the PNG's land mask (`files/world-map-green/build.py`). It matches what the PNG did to its source
(the 2005 "A large blank world map with oceans marked in blue"):
- Antarctica is left out.
- Islands below a minimum size are dropped.
- The big lakes the PNG shows as water are cut out: Superior, Michigan, Huron and Victoria, chosen by its pixels.
- The Caspian Sea is filled in as land, as the PNG has it.
- The fill is the PNG's green, #1f6023.

Land IoU is 0.91. A small drift remains at the far north (Alaska, Chukotka), from the 2005 source map's own data.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_world-map-green.png`.

Licence: as the PNG (GFDL / CC BY-SA 3.0 / 2.5 / 2.0 / 1.0, Gaaarg). The geometry is Natural Earth (public domain).
