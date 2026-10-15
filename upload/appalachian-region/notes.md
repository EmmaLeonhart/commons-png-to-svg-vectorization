# File:Appalachian region of United States.png → SVG

Rebuilt from public-domain data, not traced. Run from the repo root with `PYTHONPATH=files/appalachian-region`:
`fit.py` → `map.py` → `build.py`.

- **Geography**: US Census Bureau 2018 cartographic boundaries (states 1:20M, generalised like the PNG's
  coast; counties 1:5M), public domain. Albers conic projection (standard parallels 29.5/45.5 N, centred
  81.70 W 37.58 N) plus a similarity transform fitted to the PNG's state lines (chamfer 1.7 px).
- **The region**: which counties are Appalachian is read from the PNG itself (its white), sampled inside
  each county, plus places enclosed by members (Virginia's independent cities Bristol, Buena Vista): 425
  county-level units. This is the ARC region as of the PNG's date (2008-10-08); e.g. Barrow, Douglas and
  Heard counties, Georgia (added later), are outside it, as in the PNG.
- **Styling** measured from the PNG: states #87a4c7, region white with a 2.5 px black outline, state lines
  and frame #333.
- **Text**: all `<text>`. State names in italic small capitals (capital letters plus smaller `<tspan>`s),
  Liberation Serif (Times metrics), 10 px capitals, letter-spacing fitted per label; Maryland along its
  slant (32°); "West Virginia" in mixed case. Title, date and source in italic Liberation Sans.

Known differences: the census coastline is generalised differently around Chesapeake Bay and the Carolina
sounds. 7.3% of pixels differ, mostly coast and text antialiasing.
Licence: public domain (US Government work, as the PNG; census data public domain).
