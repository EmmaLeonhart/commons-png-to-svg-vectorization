# File:CompareTropicalYears.png → SVG

Rebuilt as a chart, not traced (`curves.py`, then `build.py`).
- **Curves**: the PNG plots tropical-year lengths from J. Meeus, *More Mathematical Astronomy Morsels*
  (2002), ch. 63, after Simon et al. (1994), which are polynomials in time. Each curve's function is
  recovered as the lowest-degree polynomial in t = year/1000 that fits its plotted centre line to under half
  a pixel (mean year: cubic; the four seasonal years: degree 5–6). Check against Meeus's published values
  for the year 2000: mean 365.242187 (Meeus 365.242190), March equinox 365.242369 (…374), June solstice
  365.241624 (…626), September equinox 365.242019 (…018), December solstice 365.242740 (…740).
  They are drawn as smooth paths over −6000…10000.
- **Layout** measured from the PNG: frame (129,44)–(928,443), 1000-year and 0.0001-day gridlines (#c6c3c6,
  the year-2000 line #808080), axis 365.2412–365.2433 at 19 px per 0.0001 day, background #e0e0e0, colours
  of the five series.
- **Text**: all `<text>` (German, as the PNG), Liberation Sans (Arial metrics), sizes fitted to the PNG's ink.
2.8% of pixels differ, mostly text antialiasing.
Licence: GFDL (relicensed; CC BY-SA 3.0 by the license migration), as the PNG by User:Sch.
