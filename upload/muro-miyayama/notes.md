# File:室宮山古墳 復原図.png → SVG

A reconstruction plan of the Muro Miyayama kofun (after Kimoto 1996), rebuilt by construction in
`files/muro-miyayama/build.py`, not traced:
- The mound, moat and dyke outlines are 15 px black strokes; 15.0 px of ink was measured across every outline. The round
  parts are fitted circles: the mound r 383, the moat r 517 and the dyke r 738. Every straight run is a least-squares
  line through the PNG's stroke pixels, with vertices at the intersections of neighbouring runs.
- The dyke's lower east side and south side are dashed (46 on, 14 off, continuous round the corners).
- National Route 309 is two dashed lines, 6 px wide with 24 px dashes every 41.6 px. Each is three straight runs with
  sharp bends, and each dash phase is fitted. The east line runs under the moat's west side, which hides it, as in the PNG.
- The burial chambers are rectangles 41 × 94 px with a 5.5 px stroke and round joins. Some are dashed (18 on, 6 off).
  Their centres and angles come from the principal axes of their ink.
- The north arrow is a polygon with a 41.7 px shaft and a 117 px triangular head, measured along its axis.
- The labels are real `<text>` in Meiryo (Yu Gothic / Noto Sans CJK JP as fallbacks), fitted to the PNG's lettering; the
  北 by the arrow is bold.

Ink IoU against the PNG is 0.79; the remainder is antialiasing and small differences in dash phase and glyphs.
Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_muro-miyayama.png`. Saved as
`Muro Miyayama kofun reconstruction.svg`; on Commons it would be File:室宮山古墳 復原図.svg.

Licence: public domain, as the PNG ({{PD-self}}, Saigen Jiro). The PNG's own source is credited as 木許守「室宮山古墳墳丘復原案」,
『奈良県御所市 室宮山古墳範囲確認調査報告』 (御所市教育委員会, 1996), pp. 44–45.
