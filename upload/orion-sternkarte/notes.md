# File:Orion-Sternkarte.png → SVG

The PNG is a pp3 1.3 star chart (Marc Layer, 2004) in the Wikipedia style of pp3's `examples/wiki.pp3`. Rebuilt from
pp3's own data, not from the pixels (`files/orion-sternkarte/build.py`; data: pp3 1.3.3, MIT, in
`data_lake/downloads/pp3/`):

- **Projection**: azimuthal equidistant, centre RA 5.5591 h, Dec +2.715°, fitted to the PNG's stars
  (`fit_projection.py`; the four anchor stars land within 0.15 px, 126 isolated stars within 0.8 px rms).
- **Stars**: Bright Star Catalogue (stars.dat), down to magnitude 5.0 as in pp3's orion.pp3; disc radius by
  magnitude, calibrated so each half-magnitude bin's dark area matches the PNG's.
- **Constellation lines**: pp3 1.3.3's lines.dat has only 3 Orion lines; the PNG's author drew a fuller figure, so every
  pair of drawn stars that the PNG joins in green is taken as a line too (of the PNG's 2536 green px, 32 are not covered).
- **Boundaries** (Davenhall & Leggett, Orion highlighted), **grid** (every hour / 10°), **ecliptic** (J2000), all in
  wiki.pp3's colours.
- **Nebulae**: the seven the PNG shows (M 1, M 35, M 41, M 42, M 78, NGC 1746, NGC 2238). pp3 1.3's nebula filter
  can't be reproduced from 1.3.3's data, so they are listed by number.
- **Milky Way**: pp3's milkyway.dat (Mellinger panorama) contoured into bands of 8 grey levels, tinted as measured in
  the PNG.
- **Labels**: all 48 are real `<text>` (German names as in the PNG: Zwillinge, Stier, Einhorn, Großer Hund, Hase,
  Beteigeuze), placed and sized to the PNG's ink boxes. They use Arial; the original used LaTeX's Helvetica and Euler
  Greek, so the letter shapes differ slightly.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_orion-sternkarte.png`.

Licence: as the PNG, GFDL (Marc Layer, {{GFDL-user-de|migration=relicense}}, so also CC BY-SA 3.0). The pp3 data is
MIT (Torsten Bronger).
