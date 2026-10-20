# File:大洋.png → SVG

A map of Oceania (Oceania green, Southeast Asia mauve, on pale cyan sea), rebuilt by `files/taiyo-oceania/build.py`
from Natural Earth 10m land (public domain).

The PNG says it is "a variation of World Map Blank.svg", but its base cannot be a projection of real geography:
- It is centred in the Pacific: Fiji sits well inside the frame, with Tonga and Samoa east of it.
- New Zealand is drawn enlarged, at about 11 px per degree of longitude, against about 7.5 for Australia and Borneo.
- Australia is drawn fatter than it is.

So, as for other generalised maps in this project, real geography replaces it:
- equirectangular at lon_0 150°, the best of Robinson, Miller, Mercator and equirectangular;
- scales and offset fitted to the PNG's land mask with New Zealand left out (land IoU 0.71);
- each land polygon takes the colour of the nearest land in the PNG, so New Zealand and Tasmania stay green although
  the PNG draws them elsewhere;
- islets under 0.15 px² are dropped. The PNG enlarges the Micronesian atolls; at true size most are below a pixel.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_taiyo-oceania.png`. Saved as 大洋.svg.

Licence: as the PNG (CC BY 3.0, S19991002). The geometry is Natural Earth (public domain).
