# Devlog

## 2026-10-07

- **File:Kinai-and-Hyuga-Province-in-Japan-RA.png → SVG** (`files/kinai-hyuga/`).
  Rebuilt from File:Provinces of Japan.svg: registered against the PNG, highlighted
  provinces read from it, 19 labels as real `<text>` fitted to within 4 px. Checked
  in Chrome only, not yet in librsvg.
- Built `queue.md` from the user's PNG list: 1140 Commons files, 91 unresolved names.
- **File:Ushu Province.png → SVG** (`files/ushu-province/`). Rebuilt from File:Provinces
  of Japan-Dewa.svg with the new `tools/rebuild_locator.py` (registration plus colour
  reading, generalised from the Kinai job). 100% land/sea agreement; no text.
- `tools/rebuild_locator.py` and `tools/render_svg.py`: a reusable rebuild for locator
  maps made from the "Provinces of Japan" SVG family. Checked against Kinai: it finds the
  same seven provinces and the same transform as the hand-made build.
- `tools/triage.py`: sorted all queued files by route (triage.md).
- **File:Wakayama-geo-stub.png → SVG** (`files/wakayama-geo-stub/`) with the new
  `tools/rebuild_flagmap.py`: prefecture = land minus neighbours from Wakayama
  géolocalisation.svg (shapely), clipped Flag of Wakayama Prefecture.svg, navy outline.
  Silhouette IoU 0.946. Licence question recorded (outline source is CC BY-SA 4.0).
- `tools/render_svg.py` now sizes SVGs with mm/cm dimensions by their viewBox.
- Kagoshima-geo-stub.png: an SVG flag map already exists; noted in queue.md.
- **File:Kochi-geo-stub.png → SVG** (`files/kochi-geo-stub/`) with `tools/rebuild_flagmap.py`
  (Kochi géolocalisation.svg land minus neighbours, Flag of Kochi Prefecture.svg). IoU 0.909,
  flag agreement 99.9%. The tool now fits on a ≤500 px copy for large PNGs.

## 2026-10-08

- Finished SVGs are now staged in `upload/<slug>/` (user's rule). Kinai, Ushu, Wakayama
  and Kochi copied there.
- `tools/rebuild_flagmap.py`: solid-silhouette mode (`#rrggbb` instead of a flag), separate
  x/y scales, debris and speck removal. Renders are now transparent.
- Shadow picture of Gunma prefecture.png: attempted, parked as NEEDS-INVESTIGATION (see queue.md).
