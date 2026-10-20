# File:断夫山古墳 周濠復原図.png → SVG

Danpusan (Danfuyama) kofun: a reconstruction of its moat (after Fukaya 2009), rebuilt by construction in
`files/danpusan/build.py`, as for the Muro Miyayama plan:
- The mound outline is 15 px. Its round part is a fitted circle, and its straight runs are least-squares lines through
  the PNG's stroke pixels; vertices are the intersections of neighbouring runs.
- The present moat (周濠(現在)) is a 4 px polygon fitted the same way.
- The estimated moat line (周濠推定線) is dashed, 15 px wide, with round caps (46 px visible dashes every 60 px). It is
  drawn as a smooth curve in the PNG, and it is made regular here: a straight bottom, and straight sides that are tangent
  to a circle over the top. The fit's median distance is 5 px, within the stroke's own width. Each of its four pieces has
  its own dash phase, as in the PNG. Over the arc the dashes drift a little, because the drawn curve's top is slightly
  flatter than a circle.
- The roads (市道, 伏見通) are 4 px dashed lines (16 on, 12 off), with phases fitted. 市道 crosses 伏見通's west side.
- The north arrow is a polygon measured along its axis (41.8 px shaft, 125 px head).
- The leader lines are 10 px.
- The labels are real `<text>` in Meiryo (Yu Gothic / Noto Sans CJK JP as fallbacks); 北 is bold, and 伏見通 is set
  rotated −90° as in the PNG.

Ink IoU against the PNG is 0.74; the remainder is mostly dash-phase offsets on the curve and antialiasing. Comparison:
`Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_danpusan.png`. Saved as
`Danpusan kofun moat reconstruction.svg`; on Commons it would be File:断夫山古墳 周濠復原図.svg.

Licence: public domain, as the PNG ({{PD-self}}, Saigen Jiro). Its source: 深谷淳「断夫山古墳の周濠」
『名古屋市見晴台考古資料館研究紀要』第11号 (2009), p. 26.
