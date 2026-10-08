# Kochi-geo-stub

- **Target:** [File:Kochi-geo-stub.png](https://commons.wikimedia.org/wiki/File:Kochi-geo-stub.png),
  2057×1683, a flag map for stub templates by Kzaral (2008), PD-self. Tagged `{{Convert to SVG|flag map}}`.
- **Rebuilt from:**
  - Outline: [File:Kochi géolocalisation.svg](https://commons.wikimedia.org/wiki/File:Kochi_g%C3%A9olocalisation.svg)
    by Flappiefh, CC BY-SA 4.0. The prefecture is land `g5367` minus the neighbours `g18230`.
  - Flag: [File:Flag of Kochi Prefecture.svg](https://commons.wikimedia.org/wiki/File:Flag_of_Kochi_Prefecture.svg), PD-textlogo.
- **Method:** `python tools/rebuild_flagmap.py "data_lake/downloads/kochi-geo-stub/Kochi-geo-stub.png"
  "data_lake/downloads/kochi-geo-stub/Kochi géolocalisation.svg" g5367-g18230
  "data_lake/downloads/kochi-geo-stub/Flag of Kochi.svg" files/kochi-geo-stub/Kochi-geo-stub.svg`.
  Silhouette IoU against the PNG is 0.909 (the vector coastline is more detailed). Flag placement
  matches the PNG's colours on 99.9% of pixels. There is no outline, as in the original.
- **Licence:** NEEDS-DECISION (user). Same situation as Wakayama: the outline source is
  CC BY-SA 4.0, so the SVG is CC BY-SA 4.0, while the original PNG is PD.
- **Text:** none.
- **Checked:** in Chrome; side-by-side in `Documents/claude-screenshots/agentic-vectorization_2026-10-07/`.
