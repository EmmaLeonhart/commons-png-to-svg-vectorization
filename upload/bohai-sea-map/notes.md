# File:Bohai Sea map.png → SVG

Rebuilt by `files/bohai-sea-map/build.py` from Natural Earth 10m data (public domain): land, country borders
(the Korean demarcation line only, as in the PNG) and the Huang He and Yangtze, in a Lambert conformal conic
projection fitted to the PNG (lon₀ 125.27°, standard parallels 26.9° and 42.5°; ten city dots agree to 2.4 px
RMS, land mask IoU 0.91), with the 5° graticule in the same projection. City dots at their measured positions;
every label is real `<text>` fitted to the PNG's lettering (`tools/fit_text.py`: Arial, Times New Roman italic
for the seas and rivers, Arial Narrow bold for NORTH); north arrow and scale bar measured. 5.9% of pixels differ,
mostly where Natural Earth's coast is more detailed than the PNG's generalised one; islets under 12 px² are left
out, as the PNG leaves them out.

The two derivative "SVG"s on Commons (hr, bs) only wrap the raster, and Bohai map-fr.svg is a different map, so
there was no vector source. Comparison:
`Documents\claude-screenshots\agentic-vectorization_2026-10-19\cmp_bohai-sea-map.png`.

Licence: GFDL / CC BY-SA 3.0, as the PNG (its design and labels; the geographic data is PD).
