# Kinai-and-Hyuga-Province-in-Japan-RA

- **Target:** [File:Kinai-and-Hyuga-Province-in-Japan-RA.png](https://commons.wikimedia.org/wiki/File:Kinai-and-Hyuga-Province-in-Japan-RA.png),
  1400×1400 PNG by Flora fon Esth, CC BY-SA 3.0, 2025-01-25.
- **Source rebuilt from:** [File:Provinces of Japan.svg](https://commons.wikimedia.org/wiki/File:Provinces_of_Japan.svg)
  by Ash_Crow (GFDL / CC BY-SA 3.0 migrated / CC BY 2.5). It is the PNG's own stated source.
- **Method:** rebuilt, not traced. The source SVG was registered against the PNG
  (scale 0.2335 source units per PNG pixel, offset 37.78, 432.91; 94.6% land/sea agreement).
  Each source province's colour was then read from the PNG. Highlighted provinces:
  Hyuga `g2700`, Izumo `g8791`, and Kinai `g23010` Yamashiro, `g15010` Settsu,
  `g23919` Kawachi, `g15898` Izumi, `g22122` Yamato.
- **Text:** 19 plain `<text>` elements, one per label line, with ids, no paths and no
  `textLength`, so SVGTranslate can handle them. Font is `Noto Serif CJK JP` (available on
  Commons) at weight 600 with a white halo (`paint-order:stroke`). Sizes and letter-spacing
  were fitted to the PNG's ink boxes; every label lands within 4 px.
- **Build:** `python files/kinai-hyuga/build.py` from the repo root.
- **Not yet checked:** rendering through Commons' librsvg. It was only checked in Chrome.
