# File:The Letter "i" in Different European Languages.png → SVG

Built from the PNG's stated source, File:Blank map of Europe cropped.svg (`files/letter-i/build.py`; current revision —
the PNG was painted in Paint over a 2017 render of it):
- **Frame:** the map is framed to the PNG, with scale and offset fitted on the land masks (IoU 0.91).
- **Countries:** each country is filled with the colour the PNG paints it, by majority vote of the PNG's palette
  colours under the country. Countries it leaves unpainted get its grey, and its land and lake greys are matched.
- **Wales:** the PNG paints Wales apart from the rest of the UK, but the map doesn't divide the UK. So Wales comes from
  Natural Earth 10m admin-1 (the Welsh units, public domain). It is projected in Lambert azimuthal equal-area and
  fitted to the map's own UK outline (IoU 0.94, `files/letter-i/fit_wales.py`), then placed beside the UK in the same
  coordinate space.
- **Labels:** the IPA labels are real `<text>` in Calibri, fitted to the PNG's lettering.

7% of pixels differ by more than a trace. That is mostly lakes the PNG shades grey, and border details that changed
in the map since 2017.

**Filename:** Windows cannot store `"` in a filename, so the file here is
`The Letter i in Different European Languages.svg`. On Commons, use the title with the quotes.

Comparison: `Documents\claude-screenshots\agentic-vectorization_2026-10-20\cmp_letter-i.png`.

Licence: CC BY-SA 2.5, as the PNG. The base map is CC BY-SA too, and Natural Earth is public domain.
