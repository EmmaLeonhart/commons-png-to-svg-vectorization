# File:W-asia.png → SVG

A locator map of Western Asia, rebuilt from Natural Earth 10m admin-1 data, merged per country (public domain)
(`files/w-asia/build.py`):
- **Projection:** equirectangular, fitted to the PNG's land mask.
- **Colours:** the PNG's colours: green for Turkey, the Caucasus, Cyprus, the Levant, Iraq, Iran and the Arabian
  Peninsula states; light green for Sinai; grey for other land; white for sea and borders.

The PNG's coastlines are generalised by hand, so real geography only overlays it at land IoU 0.87; Mercator fits
worse. As with the other hand-drawn maps, the real outlines replace the drawn ones. The green countries are read off
the PNG rather than voted, because the loose fit makes a pixel vote unreliable.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_w-asia.png`.

Licence: public domain, as the PNG (PD-self) and Natural Earth.
