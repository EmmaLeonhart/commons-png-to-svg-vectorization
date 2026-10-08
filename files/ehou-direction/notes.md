# Ehou-direction (恵方の方位)

- **Target:** [File:Ehou-direction.png](https://commons.wikimedia.org/wiki/File:Ehou-direction.png), 468×436,
  "恵方の方位。自作。" from ja.wikipedia, GFDL-ja (migration=relicense).
- **Rebuilt from scratch.** No vector source exists, and the figure is a geometric construction, so it is
  drawn directly from measured parameters (not traced):
  - centre (233.8, 217.9); regular octagons with apothems 149, 120.25, 92.75, 65.5 and a central
    circle of r 36.3, measured from the 2 px lines;
  - equal angular sectors: 24 × 15° in the outer ring (boundaries at 7.5° + 15k; the measured
    side fractions 0.31–0.34 match tan 7.5°/tan 22.5° = 0.318), 12 × 30° in the middle ring
    (boundaries at 15° + 30k; measured 0.62–0.65 vs 0.647), 8 trigram cells, and 16 spokes in the
    inner zone;
  - the highlighted cells 壬, 甲, 丙, 庚 in `#ffabab`, and four 5 px round-capped arrows with 40° heads.
- **Text:** all 70 labels are `<text>`: 24 mountains (壬子癸…亥), 12 branches, 8 trigrams, 中央, the
  16 compass points and the four year notes (丁・壬の年 etc.). The label order follows the
  traditional sequence and matches the PNG. Ring labels are centred in their cells with explicit
  baselines (no `dominant-baseline`, for librsvg). Font `Noto Sans CJK JP` 16 px; the original
  used a bitmap UI font, so glyph shapes differ and the ・ in the year notes is a little wider.
- **Check:** 9.9% of pixels differ, mostly glyph shapes and antialiasing.
- **Licence:** GFDL-ja / relicensed as in the original; the uploader should carry the original's tags.
