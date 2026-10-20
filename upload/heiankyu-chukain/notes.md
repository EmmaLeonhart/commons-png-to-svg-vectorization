# File:平安宮 中和院位置.png → SVG

A plan of the Heian Palace (平安宮, after 『日本大百科全書』 大内裏) marking the Chūwa-in (中和院). Rebuilt by
construction in `files/heiankyu-chukain/build.py`:
- The plan is axis-aligned, so every wall, gate notch and block outline is read as a rectangle from the PNG's row and
  column runs of black. The runs are at least 8 px long and merged across rows, with the labels masked out first. That
  gives 320 runs; the block outlines are 2 px wide.
- The grey precincts (内裏, 朝堂院) are a two-grey dither in the PNG. Each is one flat fill at the mean grey, #d8d8d8.
- The two leader lines are straight 2 px lines through their leftover ink.
- The labels are real `<text>` in Meiryo (IPAGothic / Noto Sans CJK JP as fallbacks), fitted to the PNG's lettering.
  They keep the PNG's own wording, including 木工内候, and 真言院 is set as three stacked characters.

Ink IoU against the PNG is 0.96. Comparison:
`Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_heiankyu-chukain.png`. Saved as
`Heian palace Chuwain.svg`; on Commons it would be File:平安宮 中和院位置.svg.

Licence: public domain, as the PNG ({{PD-self}}, Saigen Jiro).
