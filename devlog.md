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
- `tools/same_name_svg.py`: 157 queued PNGs have a same-named SVG on Commons (e.g.
  EnglandSurrey.svg). With the 206 whose pages already point to a vector version, 251
  files moved to "Already vectorized on Commons" in queue.md; 886 remain to vectorize.
- Shadow picture batch (41 prefectures queued): Natural Earth rebuild via
  `tools/batch_shadow.py`. 13 matched at IoU >= 0.93 but are visibly smoother than the
  originals, so none were accepted; all parked in queue.md with their scores, drafts in
  scratch/shadow/. A detailed boundary source is needed (INTENT open question).
- **Shadow pictures → SVG from MLIT N03** (`tools/n03_prefecture_svg.py`, `tools/batch_shadow.py`):
  Aichi, Aomori, Chiba, Fukuoka, Fukushima, Gifu (IoU 0.945–0.981), staged in upload/.
  The batch was stopped by Claude Code after 10 of 41 because the machine ran low on memory;
  the other 31 are still queued. Ehime, Fukui, Gunma, Hiroshima fell below 0.93.
- **File:Oki islands in Shimane prefecture.png → SVG** (`files/oki-islands/`): source relief SVG
  plus three `<text>` labels, each within 1 px of the original. Staged in upload/.
- **File:Nigeria Rivers State map.png → SVG** (`files/nigeria-rivers-state/`): from the 2010-02-11
  revision of Nigeria location map.svg; Rivers State cut from the land along borders and rivers
  (the PNG was flood-filled), red-area IoU 0.943. Staged in upload/.
- `tools/rebuild_locator.py`: `--units-layer` mode (units = a layer's paths by id, minimal edit);
  dark saturated colours are no longer mistaken for text.
- Location map Ryukyu Islands.png marked NOT REBUILDABLE (raster topographic relief).
- **File:Shinmei torii.png → SVG** (`files/shinmei-torii/`): torii A of Torii gate variation.svg,
  each part fitted to its own box in the PNG; title, three labels as `<text>`. Staged in upload/.
- Melanesian / Micronesian Cultural Area.png: NEEDS-DECISION recorded (hand-drawn region blob).
