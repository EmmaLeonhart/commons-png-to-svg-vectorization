# Oki islands in Shimane prefecture

- **Target:** [File:Oki islands in Shimane prefecture.png](https://commons.wikimedia.org/wiki/File:Oki_islands_in_Shimane_prefecture.png),
  423×600, 2018, CC BY-SA 4.0. A render of the source below with three Japanese labels added.
- **Rebuilt from:** [File:Shimane géolocalisation relief.svg](https://commons.wikimedia.org/wiki/File:Shimane_g%C3%A9olocalisation_relief.svg)
  by Flappiefh, CC BY-SA 4.0 (data: SRTM3, OpenStreetMap, GSI). This is the PNG's own stated source.
  The licence stays CC BY-SA 4.0, the same as the original.
- **Method:** `python files/oki-islands/build.py` appends the labels 隠岐諸島, 島後 and 島前 as `<text>`
  (font `Noto Sans CJK JP`, available on Commons) to the unchanged source. Rendered at the PNG's
  size, each label's ink box is within 1 px of the original.
- **Note:** the shaded relief is an embedded raster image inherited from the source SVG.
  Borders, coastline, graticule and all text are vector.
- **Checked:** in Chrome against the PNG. Not yet checked in librsvg.
