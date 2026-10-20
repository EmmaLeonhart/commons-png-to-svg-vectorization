# Wakayama-geo-stub

- **Target:** [File:Wakayama-geo-stub.png](https://commons.wikimedia.org/wiki/File:Wakayama-geo-stub.png),
  321×378, a flag map for stub templates by Kzaral (2008), PD-self. Tagged `{{Convert to SVG|flag map}}`.
  The PNG was made from a raster silhouette (Shadow picture of Wakayama prefecture.png) and
  Flag of Wakayama.svg.
- **Rebuilt from:**
  - Outline: [File:Wakayama géolocalisation.svg](https://commons.wikimedia.org/wiki/File:Wakayama_g%C3%A9olocalisation.svg)
    by Flappiefh, CC BY-SA 4.0. The prefecture is computed as land `g4485` minus the
    neighbouring prefectures `g9076`, then simplified to a tolerance of 1/3000 of its extent.
  - Flag: [File:Flag of Wakayama Prefecture.svg](https://commons.wikimedia.org/wiki/File:Flag_of_Wakayama_Prefecture.svg),
    PD-ineligible. Its official colours are used, not the PNG's slightly darker navy.
- **Method:** `python tools/rebuild_flagmap.py "data_lake/downloads/wakayama-geo-stub/Wakayama-geo-stub.png"
  "data_lake/downloads/wakayama-geo-stub/Wakayama géolocalisation.svg" g4485-g9076
  "data_lake/downloads/wakayama-geo-stub/Flag of Wakayama.svg" files/wakayama-geo-stub/Wakayama-geo-stub.svg`.
  Silhouette IoU against the PNG is 0.946; the differences are the finer coastline of the
  vector source. Flag placement matches the PNG's colours on 98.3% of pixels. The navy
  outline `#1f4376` is read from the PNG.
- **Licence:** NEEDS-DECISION (user). The original is public domain, but this outline source
  is CC BY-SA 4.0, so the SVG has to be CC BY-SA 4.0 with attribution to Flappiefh. A PD
  outline source would keep it PD.
- **Text:** none.
- **Checked:** in Chrome; side-by-side in `Documents/claude-screenshots/agentic-vectorization_2026-10-07/`.
