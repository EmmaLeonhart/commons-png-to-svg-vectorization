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
- `tools/render_match.py`: renders each linked SVG at the PNG's size. Silver-service-star.png and
  Tamil distribution.png are plain renders of existing SVGs; moved to "Already vectorized".
  King of Na gold seal face.png marked NOT REBUILDABLE (photograph).
- MTLogo2.png: same artwork as File:MTLogo1.svg (aligned diff 2.6); moved to "Already vectorized".
  `tools/render_match.py` gained an alignment step; its re-run over near misses was stopped by
  Claude Code for low memory and has not been restarted.
- Cause of the two low-memory stops: my own processes. `render_match` alignment rendered SVGs at
  native size (thousands of px) and built full float64 arrays per candidate; a leftover python
  process held 8.3 GB. Fixed (render ~2x PNG size, ≤300 px comparison grid, float32). The
  shadow batch's fitting (`rebuild_flagmap` on full-size grids) is a likely contributor too.
  Neither job has been restarted; they wait for the user's go-ahead.
- Flag of the United States (23px).png: a deliberate pixel-hinted icon of the existing SVG; moved
  to "Already vectorized". 大洋.png parked (its stated base, World Map Blank.svg, is Robinson in
  both revisions and does not match). `rebuild_locator`: identity viewBox allowed; colour snapping
  only to colours the base actually uses; dark near-grey text filter tightened.
- **File:Flag of the Uzbek Soviet Socialist Republic(1937-1938).png → SVG**
  (`files/uzbek-ssr-flag-1937/`): red field and two `<text>` lines; 0.58% of pixels differ.
- **File:Flag of the Uzbek Soviet Socialist Republic(1927-1929).png → SVG**
  (`files/uzbek-ssr-flag-1927/`): red field, two RTL Arabic-script `<text>` lines and one Cyrillic.
  The Arabic transcription should be confirmed by a reader before upload.
- **File:Cube NoEdges RGBfaces 64px.png → SVG** (three polygons; 84/4096 edge pixels differ) and
  **File:Blank 50px.png → SVG** (one white rect, pixel-identical). Staged in upload/.
- Flag of the JASDF (1955-1957): NEEDS-DECISION (its emblem is an older, simpler drawing than the
  available SVG). Flag of the King of Joseon (1876): NOT REBUILDABLE (dragon artwork).
- `tools/render_svg.py`: sizes SVGs without width/height by their viewBox.
- **File:Ehou-direction.png → SVG** (`files/ehou-direction/`): drawn from measured geometry
  (octagon rings in equal angular sectors, centre circle, highlighted cells, arrows) with all 70
  labels as `<text>`. 9.9% of pixels differ (glyph shapes). Staged in upload/.
- **File:Susanowo family tree.png → SVG** (`files/susanowo-family-tree/`): exact 1 px line segments,
  dotted line and hop, 26 names as vertical `<text>` (ink boxes within 1 px). librsvg's vertical
  text still to be checked. Family crest hanawachigai.png marked NOT REBUILDABLE (freeform flower).
- **File:Ohokuninushi family tree.png → SVG** with the new `tools/rebuild_tree.py` (line art →
  exact segments, dots → circles, names from a JSON spec as vertical `<text>`): black-pixel IoU 0.991,
  36 names. Staged in upload/.
- **File:Emperor family tree0.png → SVG** (`files/emperor-family-tree0/`): `rebuild_tree.py` now also
  extracts 45° and dotted runs, several line colours (the grey 国津神系/天津神系 divider) and takes masks
  and hand-made extras (a hop arc). 23 names, 6 notes. Staged in upload/.
- **File:Moriya Family Tree (English).png → SVG** (`files/moriya-family-tree-english/`): 19 exact 5 px
  lines and 28 `<text>` lines fitted to the PNG's ink boxes (new `scratch/fit_text_lines.py`).
  Staged in upload/.
- `tools/visual_triage.py`: colour-complexity check of every remaining file's thumbnail. queue.md now
  lists flat graphics first, then mixed images; photo-like images and screenshots moved to a
  "Likely raster originals" section for review (not traced, not deleted).
- **File:24directions.png → SVG** (`files/24directions/`): the Ehou-direction construction re-measured;
  53 `<text>` labels. Staged in upload/.
- **File:Bangkok Monorail Logo.png → SVG** (three rounded squares, radii from mask area; 0.54% differ) and
  **File:23 Graz.png → SVG** (rounded badge + "(23)" text). Staged in upload/.
- **File:Blackpool Transport simple logo.png → SVG**: two stroked primitives (tower polyline, base arc),
  IoU 0.88. Staged in upload/.
- **File:Arms of Bahrain.png → SVG** (`files/arms-of-bahrain/`): shield path from the 2008 Emblem of Bahrain.svg
  revision, measured five-point chief, 0.62% of pixels differ. Staged in upload/.
- `tools/render_svg.py`: physical units (mm, cm, in, pt) convert at 96 dpi instead of falling back to the
  viewBox.
- Abkhazia stub.png: Natural Earth and OSM (relation 1152720 ∩ NE land) outlines both match at IoU 0.93
  but not its stylised drawing; NEEDS-DECISION recorded. New `tools/geojson_region_svg.py`;
  `ne_prefecture_svg.py` takes any admin-1 region. Script-specimen images: NEEDS-DECISION recorded.
