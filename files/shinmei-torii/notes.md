# Shinmei torii

- **Target:** [File:Shinmei torii.png](https://commons.wikimedia.org/wiki/File:Shinmei_torii.png), 537×354,
  by Urashimataro (2010), a derivative of Torii gate variation.svg: "Cropped, added explanatory notes".
  CC BY-SA 3.0,2.5,2.0,1.0 / GFDL.
- **Rebuilt from:** torii A (`path1062` kasagi, `path1072` and `path1048` hashira, `path1044` nuki) of
  [File:Torii gate variation.svg](https://commons.wikimedia.org/wiki/File:Torii_gate_variation.svg) by Mukai,
  CC BY-SA 3.0 / GFDL. Same licences as the original.
- **Method:** `python files/shinmei-torii/build.py`. The PNG's author moved the parts as well as
  stretching the drawing (the pillars sit nearer the ends of the kasagi), so each source path is
  scaled into its own box measured from the PNG; the transforms are baked into the path data so
  outlines stay a uniform 2 px. Colours (`#cbb99d`, black), the ground line and the three leader
  lines come from the PNG. "Shinmei torii", "kasagi", "nuki" and "hashira" are `<text>`
  (Noto Sans CJK JP bold, with letter-spacing to match the original's wider font); every ink box
  is within 2 px. Overall, 2.6% of pixels differ by more than a small threshold, mostly
  antialiasing and glyph shapes.
- **Checked:** in Chrome against the PNG.
