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
- **Flag of the Kingdom of Württemberg (1806 - 1816).png** (three stripes; only the two antialiased boundary rows
  differ) and **G01/G05/G10/G50/G100.png** (green bars, pixel-identical) → SVG. Staged in upload/.
- `tools/render_svg.py`: URL-encodes the file name (non-ASCII names rendered blank).
- **File:EdinburghTramsGeneric.png → SVG**: disc + four fitted bands with the PNG's stacking; IoU 0.92–0.999 per
  colour. Staged in upload/.
- **File:Former Ensign of Myanmar Air Force.png → SVG**: its source SVG with the field recoloured, 0.14% of pixels
  differ. Staged in upload/.
- **File:Istanbul public transport - Nostaljik Tramvay symbol.png → SVG**: disc + "NT" text, ink box exact.
  15 woodblock/line-art figure drawings marked NOT REBUILDABLE; Indonesian Marine Corps flag parked
  (source emblem's lettering is paths).
- **File:Indonesian Road Sign d9a.png → SVG** with the new `tools/fit_polygons.py` (corner-fitting for straight-edged
  pictograms): 0.92% of pixels differ, 1.4 KB. INTENT records the assumption. Staged in upload/.
- Japan ferry sign.png: File:Japanese road sign (Ferry).svg is the same official sign; moved to "Already vectorized".
- **File:Japanese flag during the Kenmu Restoration.png → SVG**: Imperial Seal chrysanthemum (recoloured) on a measured
  nobori banner; 0.9% of pixels differ. Staged in upload/.
- **File:Kitakatsuragi District in Nara prefecture Ja.png → SVG**: the 2008 revision of Map of Nara Prefecture Ja.svg with
  the district's four municipal paths recoloured; 1.8% of pixels differ. Staged in upload/.
- **File:Gongen Zukuri.png → SVG**: axis rectangles, merged exact line segments, 66 pillar circles; 0.39% of pixels differ.
  Staged in upload/.
- **NO IMAGE YET square.png, NO IMAGE YET.png, L14 C.png → SVG**: text images rebuilt as fitted `<text>` with the new
  `tools/fit_text.py` (size, letter-spacing and start position from the ink box; padded canvas so trial text is never
  clipped). 5 kamon marked NOT REBUILDABLE; 7 script samples added to the script-specimen decision. Staged in upload/.

## 2026-10-15

- **Coats of arms for order.life** (Emma's inochi-no-michikyo queue item of 2026-10-14). New tools:
  `person_arms.py` (Wikidata P94 for the 60,067 order.life people with a Wikidata item: 1,805 have arms,
  230 raster), `arms_triage.py` (110 distinct PNG/GIF files: vector versions, blazons), `fetch_arms_png.py`,
  `generator_render.py` (Emma's Sodacan generator imported read-only; records reused Commons drawings and
  what it could not draw), `arms_compare.py` (tincture agreement by hue class + silhouette IoU against the
  PNG), `build_arms.py` (batch from `files/arms/arms.json`, notes.md per file with sources and licences).
- **23 arms rebuilt from their blazons and staged in upload/arms-*/**: Arpad, Aubigny, Basset, Bigod,
  Buornonville, Cardona, Clare, Clifford, County of Portugal, Ely (Geoffrey de Burgo), FitzHamon, Longespée,
  Mandeville, Meissen, Mowbray (2), Neville, Percy (2), Rabenswalde, St John, Wildgraf Dhaun, Woodville.
  Checked by eye side by side with each PNG; tincture agreement 0.67–0.90 (lion drawings and shield shape
  differ by design: Sodacan's style).
- 14 more blocked on generator gaps (cross patonce, mascles, 'in pale', 'counterchanged', charges between
  a bend or chevron): `files/arms/generator-gaps.md`.
- **7 Garter stall-plate shields** (Audley, Mohun, Devereux, Herbert, Rhys ap Thomas, Cherleton, John Neville)
  rebuilt the same way (shield only; `box` in arms.json crops the PNG's shield). 30 arms staged in total.
  6 more added to generator-gaps.md.
- **File:Mon-Imperial.png → SVG** (Imperial Seal SVG on flat red, gold IoU 0.967) and **File:Kamon maru ni
  kenkatabami.png → SVG** (Mukai's ken-katabami and ring SVGs recoloured and fitted, IoU 0.925). Staged in upload/.
- **File:Takamatsu no miya.png → SVG**: the crest group cut out of the Prince Takamatsu collar SVG, recoloured
  black and white, fitted (ink IoU 0.854, same crest drawn with slightly wider separations). Staged in upload/.
- JPG arms triaged (63 files: mostly seals and manuscript paintings). **4 rebuilt from blazons** (Bigod modern,
  Ataíde, Avarna, Giffone); 34 order.life arms staged from the generator in all.
- Quartered Garter plates: **Percy, 4th Earl of Northumberland** rebuilt (Percy quartering Lucy); Hastings
  (orle of martlets) and untinctured Swedish arms added to generator-gaps.md. `files/arms/person_arms_status.tsv`:
  where each of the 1,805 order.life people with arms has an SVG.
- **Achievement shields** (shield only, upright): Hohenberg, Rischach, Saffenburg, Žegligović rebuilt. Wildgraf
  Dhaun un-staged: accepted earlier, but its lion's crown is not drawn (missed by eye the first time); it and
  Everstein, Falkenstein, Wittelsbach-Bavaria, Barbosa are logged in generator-gaps.md.
- **Hvide** rebuilt (barry azure and or, a dove argent); Cabrera-Urgell and Cromwell logged as generator gaps;
  Ichinoseki Myoga marked not rebuildable (freeform kamon, no vector of this design).
- Template:Coat of arms PNGs from the main list (29) downloaded to `data_lake/downloads/commons-coa/` and
  looked at: ten are seals or manuscript paintings, several modern emblems with lettering. Mallorca, Remich and
  St Petersburg tried through the generator: all three hit gaps (castle, crown, sceptre), logged.
- **File:45 record.png → SVG**: its Open Clip Art source SVG (public domain), downloaded once openclipart.org was
  back; only the root size fixed to match its viewBox. 0.014% of pixels differ. Staged in upload/.
- **File:Abusir map.png → SVG** (`files/abusir-map/`): geometry from the Russian redrawing
  AbusirAndAbuGurabPlan ru.svg, registered and adjusted element by element; 36 English labels as DejaVu Sans
  `<text>`, leader lines fitted to leftover ink, north arrow measured, necropolis ellipse fitted. CC BY-SA 3.0.
  Staged in upload/. DejaVu fonts downloaded to `data_lake/downloads/fonts/dejavu/` for fitting text.
- Bohai Sea map: its SVG derivatives embed the raster, so they are no vector source (queue note).
- Aomori Tsugaru-block.png: built from MLIT N03 municipal boundaries of 2000-10-01 (pyshp for the old
  shapefiles; data in `data_lake/downloads/n03/2000/`), projection fitted (chamfer 2.1 px). Not staged: the PNG's
  generalised drawing differs from real geography; joined the Abkhazia/Gunma decision in INTENT.md.
- **File:Agency for Cultural Affairs Organizational chart 20230327.png → SVG** (`files/aca-org-chart/`): boxes,
  connectors and the grey Tokyo-office area measured exactly from the aliased PNG; 61 labels as Liberation Sans
  `<text>` (Aptos is not on Commons). CC0. Staged in upload/.
- **File:Birth and death rate of japan 1950-2019.png → SVG** (`files/japan-birth-death-rate/`): chart rebuilt from
  the published crude rates (en.wikipedia vital-statistics table, IPSS/Statistics Bureau) on the PNG's measured
  layout; text as Carlito `<text>`. 1.25% of pixels differ. Staged in upload/.
- **File:Appalachian region of United States.png → SVG** (`files/appalachian-region/`): census 2018 boundaries in a
  fitted Albers projection; Appalachian counties read from the PNG's colours (the 2008 ARC region, 425 units);
  letter-spaced italic small-capital state names as `<text>`. Public domain. Staged in upload/.
- **File:CompareTropicalYears.png → SVG** (`files/compare-tropical-years/`): the five tropical-year curves recovered as
  polynomials (residual < 0.5 px; their year-2000 values agree with Meeus to 5e-6 day), layout measured, German text
  as `<text>`. Staged in upload/.
- Revenue-Marine ensigns (6) marked not rebuildable (canton eagles have no vector source); Bonji letters (14) filed
  under the script-specimen decision.
- **File:Excerpt tree.png → SVG** (`files/excerpt-tree/`): rounded boxes, shaft-and-head arrows and white Arial-metric
  `<text>` labels, all measured; transparent background kept. Staged in upload/.
- Flag of the Sri Lankan Army: BLOCKED-ON-EXTERNAL (no vector of the army badge on Commons).
- **File:East Asia Cutout Projection.png → SVG**: the 2009 revision of East Asia (orthographic projection).svg with a
  viewBox on the crop window (found by cross-correlation); 0.02% of pixels differ. Staged in upload/.
- `tools/render_svg.py`: waits for Chrome's screenshot to land before deleting its page (Chrome had started returning
  first, so renders silently produced nothing).
- Flags of California (1924), King of Korea, Mexican Maritime SAR: not rebuildable (painted/photo art); South African
  Army (1966) and UAE Navy: blocked on badges with no vector; Category-diagram: NEEDS-DECISION (curve fitting).
- **File:COL-city icon.png → SVG**: Ciudad.svg with the Colombian flag's bands in its buildings, white sky and building
  outlines as in the PNG; 3.4% of pixels differ. Staged in upload/.
- `tools/render_svg.py` deletes the old output before rendering, so the wait added today cannot take a stale image
  for a new render (it did once, on the COL icon's first try; East Asia's renders were all new files).
- **File:Cricket no pic.png → SVG** (a 154×1 white placeholder: one rectangle, pixel-identical) and **File:Ch-1422a.png →
  SVG** (corner-fitted pennant and cross, 0.44% of pixels differ). Staged in upload/. Ecovia and Gaelic Games logos
  marked not rebuildable.
- **File:DPM icon.png → SVG**: corner-fitted car on the measured square, grey band; 0.5% of pixels differ. Staged.
- **File:Kagoshima-geo-stub.png → SVG**: N03 outline (limited to the islands the PNG shows) filled with the prefecture
  flag via `tools/rebuild_flagmap.py`; silhouette IoU 0.853, flag agreement 0.977. Staged in upload/.
- **File:Kyoto-geo-stub.png → SVG**: N03 silhouette (IoU 0.971) with the prefecture flag's emblem fitted over it;
  2.2% of pixels differ. Staged in upload/.
- **File:Map Icon - Hotel.png → SVG**: circles, rotated bar, half disc and rounded rectangles, measured; per-region
  alpha reproduced with masks; 0.45% of pixels differ. Staged. Minor edit (screenshot), Mouse icon (freehand cable),
  Naval jack 1975–1976 (own snake drawing) marked; Matsuura-gun and Nara Toichi-gun joined the Japan-map decision.
- **File:Kongo Cosmogram - blank.png → SVG**: ellipses, cross and arrowed arcs fitted as primitives; 6 px strokes.
  Staged in upload/.
- **R01/R05/R10/R50.png → SVG** (single-colour #f8057b bars, pixel-identical) and **Null.png → SVG** (one transparent
  pixel: an empty 1×1 SVG). Staged in upload/. O-dot.png (letter o͘) filed under the script-specimen decision.
- Triaged: 6 Notifications screenshots and 5 other UI screenshots, 2 planetarium screenshots, the Panam Sports wordmark,
  the chef's hat (freehand): not rebuildable.

## 2026-10-19

- Committed the 31 TransJakarta icons and roundels the 2026-10-15 session built but never committed
  (`tools/transjakarta_icons.py`); not yet reviewed or taken off the queue.
- Queue item 1 (arms waiting on the generator): checked, generator still at 8d8ab870 (local and origin), so
  still blocked. The call: an item blocked on an outside signal stays at the top and is re-checked each tick;
  the tick goes on to the next item rather than idling.
- **File:Andechs-Wappen.png → SVG** (`files/arms/andechs/`): blazon settled as *Azure, in chief a lion passant
  and in base an eagle displayed argent*. Sodacan's Wappen Andechs 2.svg (same arms, gold charges) recoloured
  or→argent with the generator's own `recolor()` (new `tools/recolor_svg.py`); the generator cannot lay out the
  blazon itself. Staged in `upload/arms-andechs/`; 2 order.life people now rebuilt.
- Arms needs-investigation item finished and removed from the queue:
  - Stosch, Imereti (Geo imereti.JPG) and Sir John Grey's Garter plate already have SVGs of the same arms on
    Commons (CoA Kaunitz Family.svg, whose description names the Stosch family; Kingdom of Imereti coat of
    arms.svg; Coat of Arms of Sir John Grey (1387-1439)...svg): recorded as vector-exists.
  - Jaqeli and Scheibenberg: blazons settled and both moved to the generator gaps (no ram-with-banner
    drawing; firs, hammer-and-pick saltire and charged roundel not drawn). Rows added to generator-gaps.md.
  - **File:Maruni-Toshi no Monji.jpg → SVG** (`files/maruni-toshi-no-monji/`): measured ring, 利 as `<text>` in
    Noto Serif CJK JP Black. The call: Commons has no brush CJK face, and the vector-text rule outweighs
    matching the brush strokes, so the typeset face is used (IoU 0.80). Staged in upload/.
- Three queue items closed by a call, not by work:
  - The 72 raster-original arms (seals, manuscript paintings): left as they are. INTENT.md already puts
    drawing new arms out of scope here (the generator's job); the question stays open for Emma in INTENT.md.
  - Uploading to Commons: not done. Publishing is Emma's call; it stays an open question in INTENT.md, not a
    queue item the loop can work.
  - "Then: the Template:Coat of arms PNGs in the main list": a pointer to items already in the main list; removed.
- **File:1bc1a.png → SVG** (`files/1bc1a/`): Duployan letter N as `<text>` in Noto Sans Duployan, fitted to the
  ink box by the new `tools/glyph_specimen.py` (for the other script specimens too). The call on the
  script-specimen question: text, per the vector-text rule, accepting a fallback box if Commons lacks the font.
  Staged in upload/.
- File:5th century Korea.png: not rebuildable without tracing. No vector source on Commons (the author, Asieon,
  uploads only PNGs of this series). The coast could come from boundary data, but the map's content is its
  hand-drawn kingdom borders (Goguryeo's northern line, the Baekje/Silla/Gaya borders), which no dataset holds;
  recovering them would be tracing. Source PNG kept in `data_lake/downloads/5th-century-korea/`.
- **File:Abkhazia stub.png → SVG** (`files/abkhazia-stub/`): the call on the hand-drawn-geography question is
  correct geography (tracing the stylised outline is not wanted). The OSM ∩ Natural Earth outline from
  2026-10-13, now with the outline stroked to the PNG's ~8 px line; IoU 0.92. ODbL (OSM). Staged in upload/.
- **File:ADLaM.png → SVG** (`files/adlam/`): the word Adlam in Adlam script as one `<text>` run in Noto Sans
  Adlam Bold; IoU 0.84. `tools/glyph_specimen.py` now fits from the shaped render (needed for joined,
  right-to-left scripts); 1bc1a re-checked, same result. Staged in upload/.
- **File:Ahom rendering.png → SVG** (`files/ahom-rendering/`): Ahom BA + medial RA as `<text>` in Noto Serif
  Ahom (formerly Noto Sans Ahom, both named in font-family); IoU 0.88. Staged in upload/.
- **File:Amateur radio compact icon.png → SVG** (`files/amateur-radio-icon/`): the call on the coil is a regular
  helix (pitch fixed to the measured 22.5 px, rest fitted) rather than fitting curves to the hand-drawn loops;
  ink IoU 0.89 (was 0.86 with a free fit, which squeezed the pitch). Staged in upload/.
- **File:Aomori Tsugaru-block.png → SVG** (`files/aomori-tsugaru-block/`): same call as Abkhazia, real geography;
  the N03 2000 build from 2026-10-13 staged in upload/ with notes (CC BY 4.0, MLIT credit).
- File:Aplodontia rufa distribution map.png: not rebuildable without tracing. The base map has a vector source
  (BlankMap-USA-states-Canada-provinces), but the content is the soft-edged green range painted by hand from
  the 2008 IUCN map; IUCN range polygons are not freely licensed, and USGS GAP ranges (PD) cover the US only
  and are drawn by watershed, so they would be a different map. No vector range map on Commons. PNG kept in
  `data_lake/downloads/aplodontia-rufa-map/`.
- File:ATC DASH Bus Logo 2025.png: not rebuildable without tracing. A wordmark in custom overlapping lettering
  (the D's bowl and the S are freeform curves, not a typeface); no vector on Commons, and dashbus.com serves
  only PNGs (word-logo-blue.png, bus-logo-full-color.png). Same as the Ecovia logo. PNG kept in
  `data_lake/downloads/atc-dash-logo/`.
- File:Atsuta Hongu oyobi Setsu-Matsu-sha no Zu.png: not rebuildable without tracing (reversing last tick's
  plan). Its palette is Office's default theme, so it was drawn as Office shapes: the buildings, plots and
  straight roads could be constructed, but the moat, pond, sea and curved road bends are freehand freeform
  curves (crop checked), and with no vector source those can only be traced; same call as the Korea map.
  A partial construction would only be worth doing if Emma accepts curve fitting (the Category-diagram question).
- File:Aviacionavion.png: not rebuildable, a raster original. The airplane is a cut-out photograph (a
  Turkmenistan Airlines 757 by Adrian Pingstone) inside a drawn blue ring; only the ring is constructible.
- **File:Bali Ba.png → SVG** (`files/bali-ba/`): Balinese BA as `<text>` in Noto Serif Balinese; same letter, the
  PNG's face is hand-styled (IoU 0.37). Staged in upload/.
- **File:Bamum King Njoya (4).png → SVG** (`files/bamum-king-njoya-4/`): Njoya's name in Noto Sans Bamum `<text>`,
  letters identified by glyph matching, per-character x positions; IoU 0.979. Staged in upload/.
- Blasó de Mallorca.png: re-checked; still blocked on the generator (unchanged at 8d8ab870). No Commons SVG
  shows the same arms (Palma's and the Kingdom of Majorca's add sea, palms or a lozenge), so it stays and the
  tick moves on; noted on its queue line.
- File:Blue Ridge Parkway shield.png: not rebuildable without tracing. The frame and lettering are constructible,
  but the sign's content is the hand-drawn tree, mountain and road (freeform, with soft scan edges); no vector
  version on Commons.
- File:BodhGayaCetiya silhouette.png: not rebuildable without tracing. The stepped base and towers are straight
  runs, but the finials, onion domes and the curved flanks of the central tower are freeform outlines; fitting
  them would be tracing (same rule as the chef's hat). No vector on Commons.
- **File:Bohai Sea map.png → SVG** (`files/bohai-sea-map/`): Natural Earth 10m land, borders and rivers in a
  Lambert conformal conic fitted to ten city dots (2.4 px RMS) and the land mask (IoU 0.91); graticule, dots,
  labels as fitted `<text>`, north arrow and scale bar. 5.9% of pixels differ. Staged in upload/. Natural Earth
  borders, rivers and lakes added to `data_lake/downloads/natural-earth/`.
- **File:Bonji-I.png → SVG** (`files/bonji-i/`): Siddham I as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.30). Staged.
- **File:Bonji-Ii.png → SVG** (`files/bonji-ii/`): Siddham Ii as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.42). Staged.
- **File:BonjiA.png → SVG** (`files/bonjia/`): Siddham A as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.58). Staged.
- **File:BonjiBra.png → SVG** (`files/bonjibra/`): Siddham Bra as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.36). Staged.
- **File:BonjiCa.png → SVG** (`files/bonjica/`): Siddham Ca as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.54). Staged.
- **File:BonjiHaammaam.png → SVG** (`files/bonjihaammaam/`): Siddham hāṃmmāṃ as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.38). Staged.
- **File:BonjiMa.png → SVG** (`files/bonjima/`): Siddham Ma as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.27). Staged.
- **File:BonjiNr.png → SVG** (`files/bonjinr/`): Siddham Nṛ as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.37). Staged.
- **File:BonjiPr.png → SVG** (`files/bonjipr/`): Siddham Pṛ as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.25). Staged.
- **File:BonjiVa.png → SVG** (`files/bonjiva/`): Siddham Va as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.69). Staged.
- **File:BonjiVaa.png → SVG** (`files/bonjivaa/`): Siddham Vā as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.65). Staged.
- **File:BonjiVai.png → SVG** (`files/bonjivai/`): Siddham Vai as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.54). Staged.
- **File:BonjiYam.png → SVG** (`files/bonjiyam/`): Siddham Yaṃ as `<text>` in Noto Sans Siddham (typeset vs. brush, IoU 0.22). Staged.
- File:Category-diagram.png: not rebuildable without tracing (the call on its curve-fitting question). It is a crop
  of a 2007 catgraph (tools.wikimedia.de/~dapete/catgraph, long gone) whose edges run off the canvas to nodes not
  shown, so the source graph cannot be recovered and a fresh Graphviz layout of the visible part would be a
  different picture; fitting curves to the drawn splines is tracing.
- **File:Cherokee Lowercase.png → SVG** (`files/cherokee-lowercase/`): the described text in Noto Sans Cherokee
  as `<text>` on white. Staged in upload/.
- File:Cross of Herat - Psalter Pahlavi Inscription.png: not rebuildable for now. As vector text it needs the
  inscription's Unicode text, and none is available (not in the description, the Psalter Pahlavi article or
  elsewhere on-wiki). Recovering it by beam-search glyph matching failed (best IoU 0.43): the PNG is not set in
  Noto Sans Psalter Pahlavi (its strokes are heavier and rounder). Guessing would publish wrong text; tracing the
  glyphs would break the vector-text rule. A published transcription of the Herat cross would unblock it.
- File:Dakiine.png: not rebuildable without tracing. The 抱き稲 crest is an organic drawing (curved leaves and
  grain heads; from kamon.website), the class INTENT.md already sets aside as tracing-only; no SVG of it on Commons.
- File:Deir el Bahari-map.png: not rebuildable without tracing. A scanned temple plan (soft grey edges, hundreds
  of irregular column dots, walls of uneven width); only the numerals could be constructed. No vector version.
- File:DiscussionTools Show new comment 2022 en.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals').
- File:Dolmen in Japan and Jeju.png: not rebuildable, a raster original: a screenshot of the PAX SAPIENTICA app
  (window title bar and menus, raster land-cover tiles, dolmen sprites).
- File:Dravidische Sprachen.png: not rebuildable without tracing. Hand-drawn language areas (copied from a 1992
  atlas, per its description) over a raster relief base from demis.nl; Dravidian map.svg on Commons is a different
  map with other sources and classes.
- File:Eastern Europe (Robinson projection).png: in progress. `files/eastern-europe-robinson/build.py` registers
  the 2011-01-03 revision of BlankMap-World6.svg (CSS-classed countries, rendered as an index image with crisp
  edges) against the PNG and colours the 21 green countries; 3.2% of pixels differ. Two fixes left (light-grey
  units from other CSS rules, border width), noted on the queue line.
- **File:Eastern Europe (Robinson projection).png → SVG** (`files/eastern-europe-robinson/`): finished. All land
  classes (coastxx, limitxx, antxx too) in the PNG's grey, borders widened to ~2 px; 3.65% of pixels differ.
  Staged in upload/.
- File:EcoviaLogo.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: a wordmark in custom lettering with a freeform leaf; no vector logo on Commons
- File:Enabling Visual Editor.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Ensign of the United States Revenue-Marine (1799).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Ensign of the United States Revenue-Marine (1815).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Ensign of the United States Revenue-Marine (1836).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Ensign of the United States Revenue-Marine (1841).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Ensign of the United States Revenue-Marine (1867).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Ensign of the United States Revenue-Marine (1868).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 16 stripes are trivial, but each canton eagle is a freeform drawing with no vector source (searched Commons 2026-10-15; the USCG ensign SVG's eagle is a different design)
- File:Family crest hanawachigai.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the notched flower is freeform. File:Japanese Crest Hana Wachigai.svg is a different (inverted) design, not its vector version.
- File:Flag of California (1924–1953).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the 1924 bear is a shaded, photo-like drawing (not the modern flag's bear); the star, stripe and lettering alone could be built
- **File:Flag of the Indonesian Marine Corps.png → SVG** (`files/indonesian-marine-corps-flag/`): measured field and
  frame, Korps Marinir.svg emblem registered and recoloured; its black path split into subpaths coloured per the
  flag (svgelements' own subpath output loses the current point, so they are rewritten with absolute commands).
  The call on the lettering: kept as the emblem's outlines (reused artwork, not text set here). 2.41% of pixels
  differ. Staged in upload/.
- File:Flag of the Japan Air Self-Defense Force (1955-1957).png: not rebuildable without tracing (the call on its
  emblem question). Its emblem is an older, different design (smaller eagle, solid wing band, star ring) from
  Sodacan's JASDF emblem SVG; substituting that would misrepresent the 1955 flag, and the older drawing has no
  vector source.
- File:Flag of the King of Korea (1856–1871).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: a painted dragon among clouds
- File:Flag of the Mexican Maritime Search and Rescue.png: removed from the queue; already triaged as NOT REBUILDABLE: the emblem contains a photograph (boat at sea)
- Royal Moroccan Air Force and South African Army (1966–1973) flags: still blocked (no vector badges; Commons
  re-searched for the Moroccan one: rank insignia only). They stay; the tick moved on.
- **File:Fukuchiyama Toyuke-daijinja map.png → SVG** (`files/fukuchiyama-toyuke-map/`): exact straight-run line work
  and 45 transcribed labels as `<text>` with per-character cells; 1.7% of pixels differ. One reading (篷戸 vs 蓬戸)
  flagged in notes.md. Staged in upload/.
- File:GaelicGamesProjectLogo.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: freehand hurleys and ball (only the circles are geometric)
- File:Gion Daimyojin.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Daishogun.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Hyobi.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Ooban.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Saikei.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Saisatsu.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Taion.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Taisai.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:God of Toshitoku.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- **File:Greater Macedonia.png → SVG** (`files/greater-macedonia/`): Natural Earth land and borders in an LCC fitted to
  the PNG (central meridian found by search: 9.6°E), the Macedonia region from North Macedonia, Blagoevgrad and
  Greek municipalities (geoBoundaries, CC BY 4.0). 4.7% of pixels differ. Staged in upload/.
- File:Hakusan Myori Daigongen.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:Harisainyo.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- **File:Harushima Iki.png → SVG** (`files/harushima-iki/`): Iki City from N03 2024, Harushima located via OSM and
  filled red, labels as `<text>`. The PNG is schematic, so real geography differs visibly (land IoU 0.76); same
  call as Abkhazia/Aomori. N03 Nagasaki (42) downloaded. Staged in upload/.
- **File:Higashimuro District Map.png → SVG** (`files/higashimuro-district-map/`): N03 2006 municipalities, Higashimuro
  in magenta, labels as `<text>`; 7.1% of pixels differ. Staged in upload/.
- Emma, 2026-10-19 (relayed in chat): finish up, double-check, zip everything for her to upload, and do no more
  vectorizations until 20:00. Queue paused until then.
- Pre-upload check (Emma asked for everything finished and double-checked): new `tools/check_upload.py` checks every
  folder in upload/ for an SVG and notes.md, that each SVG parses and renders non-blank, and that nothing holds stray
  control characters. 169 SVGs, 0 problems after copying 43 missing notes.md files over from files/ (East Asia
  Cutout and Oki islands crash resvg but render in Chrome). The 31 TransJakarta icons from 2026-10-15 reviewed
  against their PNGs (all match) and taken off the queue; six roundels (2A 4D 5C 5D 6A 9A) were never built and
  stay queued.
- Upload package for Emma: `tools/package_upload.py` writes all 169 SVGs flat, each named after the file it replaces
  and carrying a licence comment (CC BY-SA 4.0, the original file, author and licence from the Commons API, and data
  credits), plus LICENSE.txt. One licence fits all: the sources are PD/CC0/free use, CC BY 2.5–4.0, CC BY-SA 2.5–4.0,
  GFDL+CC BY-SA, MLIT terms (CC BY 4.0 compatible), geoBoundaries CC BY 4.0, and OSM (produced work). East Asia
  Cutout's PNG is GFDL-only, but the SVG comes from its CC BY-SA source SVG. Saved as
  Documents/commons-upload_2026-10-19(.zip).
- WoodvilleArms.svg fixed (Emma: "this one is not good"): the canton stopped 6 px short of the fess, leaving a white
  line; it now joins the fess, as in the PNG. Generator gap recorded. Upload package rebuilt.
- Tarot (Emma, 2026-10-19: download Category:Vectorized_Tarot_by_Immanuelle and make them "much more efficient",
  separate folder, "merging really close color things"): 79 public-domain SVGs (276 MB) in
  `data_lake/downloads/tarot/`. New `tools/optimize_traced_svg.py` merges colours within CIELAB ΔE 6 in place
  (e.g. Wands14: 7,741 colours -> 271), then svgo 3.3.2 (`tools/svgo.tarot.config.js`, 0.1 px precision) compacts
  structure and paths. Output in `tarot/` with the original names: 75 MB (-73%), PSNR 31-41 dB against the
  originals, at most 0.67% of pixels off by >48 (sub-pixel shifts of Inkscape-added outlines). Integer precision
  was tried and rejected (27 dB, visible). Per-card numbers in `tarot/report.txt`. First tool version rebuilt the
  document and ignored Inkscape transforms; replaced by the in-place version.
- Pause ended at 20:00; queue resumed (checked at 20:21).
- File:Historical expanse of Ainu.png: already vectorized on Commons. Its own page lists File:Historical expanse of
  the Ainu.svg as the other version: the same content (attested and suspected Ainu ranges, toponym dots) redrawn in
  another projection with a legend. The PNG's own drawing could only be reproduced by tracing its hand-drawn ranges,
  so it is recorded rather than redone.
- File:Icona catastrofi.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:Idioma osetio.png: not rebuildable without tracing. The Caucasus base could come from Natural Earth, but the
  map's content is the hand-painted Ossetian-speaking areas (freehand minority patches; the page is tagged "map
  datasource missing"), which only tracing would reproduce.
- File:Ikushimatarushimajinja.png: not rebuildable without tracing. The shrine crest is two mitsudomoe flanking a
  standing kaji leaf; Commons has tomoe SVGs, but its kaji SVGs are other designs (rounded lobes where this leaf is
  pointed and serrated), and the leaf is organic artwork that only tracing would reproduce.
- **File:Indigenous of Asia.png → SVG** (`files/indigenous-of-asia/`): Pahawh Hmong sentence as `<text>` in Noto Sans
  Pahawh Hmong, letters identified by glyph matching; `tools/glyph_specimen.py` now takes fallback fonts (the full
  stop is DejaVu Sans). Staged in upload/.
- **File:Itsukushima-island.png → SVG** (`files/itsukushima-island/`): N03 2000 municipalities of Hiroshima and
  Yamaguchi (real geography, as for the other Japan map.png crops), Itsukushima green, 17 transcribed labels as
  `<text>`, leaders and underlines from the PNG's pixel runs; land IoU 0.83. Staged in upload/.
- File:Izuna Gongen.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- **File:Japan Chubu Region large.png → SVG** (`files/japan-chubu-region/`): Natural Earth prefectures in a fitted LCC
  (IoU 0.89), Chūbu dark green, southern Kurils pink, Okinawa and Sakishima refitted into the measured inset.
  Staged in upload/. The same build serves the other "Japan … Region large" PNGs if they come up (change CHUBU).
- **File:Japan large.png → SVG** (`files/japan-large/`): new `tools/japan_region_map.py` (the Chubu build with the
  inset frame, highlighted prefectures and Kurils as parameters); land IoU 0.87; Amami Ōshima falls off the canvas at
  its true position (the PNG moves it). Staged in upload/.
- **File:Kaikatennou oujintennou.png → SVG** (`files/kaikatennou-oujintennou/`): family tree via `tools/rebuild_tree.py`;
  its vertical connectors are anti-aliased, so `verticals.py` measures them into the spec as exact lines. 13 names as
  `<text>`. Staged in upload/.
- File:Kajikimen (鹿食免).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- File:Kashikodokoro Jogyosha and Ohaguruma 04.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: woodblock / line-art figure drawing (flat colours, but freeform art).
- **File:Kata jangangjangang.png → SVG** (`files/kata-jangangjangang/`): Makasar JA NGA JA NGA as `<text>` in Noto Serif
  Makasar, stretched 1.53× to the PNG's wide monoline letters (IoU 0.26; a different typeface). Staged in upload/.
- File:Katana (common shema).png: not rebuildable without tracing. The labels and leader lines could be constructed, but
  the sword and scabbard are a shaded painted illustration; File:Katana diagram.svg on Commons vectorises a different
  diagram.
- **File:KAWI LETTER OM.png → SVG** (`files/kawi-letter-om/`): Kawi O + candrabindu as `<text>` in Noto Sans Kawi,
  IoU 0.973. Staged in upload/. Licence OFL, as the PNG (note for the upload package: OFL, not CC BY-SA).
- **File:Kharosthi font rendering sample.png → SVG** (`files/kharosthi-font-rendering-sample/`): the described Unicode
  text as `<text>` in Noto Sans Kharoshthi; same text, different font's stacking (IoU 0.15). Staged in upload/.
- **File:Kolkata bus.png → SVG** (`files/kolkata-bus/`): constructed from measured rectangles, rounded rectangles and the
  roof polygon; 0.6% of pixels differ. Staged in upload/.
- File:Koshiate (Sword Hangers).png: not rebuildable, a raster original (an Edo-period woodblock illustration from a
  1735 book; freeform line art).
- **File:Koshur in Sharada Script.png → SVG** (`files/koshur-in-sharada/`): Kashmiri "Koshur" in Sharada as `<text>` in
  Noto Sans Sharada (the PNG's own font); IoU 0.85. Staged in upload/.
- **File:Kounoke kamon.png → SVG** (`files/kounoke-kamon/`): octagonal ring (fitted octagon + 58 px round offset) and
  three bands on one fitted sine wave; IoU 0.98. Staged in upload/.
- **File:Kōfukuji plan.png → SVG** (`files/kofukuji-plan/`): anti-aliased 1 px plan lines measured at sub-pixel positions
  as exact segments, two fitted octagons, the triangle; staged in upload/. (The download lost the macron in its file
  name in the shell; renamed with Python.)
- **File:LFW2008 2403.png → SVG** (`files/lfw2008-2403/`): Tangut U+173C7 as `<text>` in Noto Serif Tangut (Noto's glyph
  design, not the dictionary's; IoU 0.32). Staged in upload/.
- **File:Linear B Sample.png → SVG** (`files/linear-b-sample/`): the described au-ke-wa in Noto Sans Linear B, on white.
  Staged in upload/.
- **File:Lontara script.png → SVG** (`files/lontara-script/`): "Basa Ugi" in Noto Sans Buginese as `<text>`. Staged in
  upload/.
- **File:Malayalam Om.png → SVG** (`files/malayalam-om/`): ഓം as `<text>` in Noto Sans Malayalam (IoU 0.59). Staged in
  upload/.
- File:Manual tab only - visual editor - citations.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Map Kumano Kodo (ja).png: not rebuildable without tracing. The coast could come from boundary data, but the map's
  content is the pilgrimage routes drawn by hand as schematic coloured lines; same call as the Korea and Ossetian maps.
- File:Map Kumano Kodo.png: not rebuildable without tracing; the English-labelled twin of Map Kumano Kodo (ja).png (same
  hand-drawn routes).
- File:Map of Suwa Shrine, Kamisha Honmiya (English).png: not rebuildable without tracing. Buildings and labels could
  be constructed, but the river, the contour lines and the curved roads are freehand curves; no SVG of it or its
  Japanese original on Commons.
- **File:Map-okinawa-pref.png → SVG** (`files/map-okinawa-pref/`): N03 Okinawa islands fitted to six island positions
  (separate x/y scales; the PNG's source is not quite equirectangular), flat green (relief shading not reproduced),
  27 labels as `<text>`. Staged in upload/.
- File:Maru ni Sasa Rindō inverted.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: kamon with freeform organic motifs.
- File:Marunimitsukashiwa.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: kamon with freeform organic motifs.
- File:Marunitsurukashiwa.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: kamon with freeform organic motifs.
- **File:Matsuura-gun.png → SVG** (`files/matsuura-gun/`): N03 2000 municipalities of four prefectures fitted to four
  landmarks; Meiji-era Matsuura District chosen by name (its 2000 towns and the cities made from it), since colour
  voting missed Goto towns. Staged in upload/.
- File:Megamihōri-no-in (売神祝印) seal imprint.png: not rebuildable without tracing. The seal-script characters were
  drawn freehand from a photograph of the seal; as `<text>` they would become ordinary glyphs, which loses the seal
  script the image is about, and no seal-script font is available on Commons.
- File:Melanesian Cultural Area.png: not rebuildable without tracing (the call on its open question). The base map and
  labels could be rebuilt, but the map's content is the hand-drawn cultural-area blob with no data source; same call
  as the Korea, Ossetian and Kumano maps.
- File:Micronesian Cultural Area.png: not rebuildable without tracing; the twin of the Melanesian map (hand-drawn region).
- File:Midtown line GO logo.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: 62 px two-colour pixel art with curved parts (rounded roof, oval lamps); not a Material Design train icon (compared 2026-10-15, files in data_lake/downloads/batch4/)
- File:Minor edit.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki editor with an annotation; a raster original (move to 'Likely raster originals')
- File:Mitsu Zaru inverted.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: kamon with freeform organic motifs.
- **File:Modre symbol Omkara.png → SVG** (`files/modre-symbol-omkara/`): Balinese okara + ulu candra as `<text>` in Noto
  Serif Balinese (best of eight encoding/font tries). Staged in upload/.
- File:Mon- Izumo taisha.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: kamon with freeform organic motifs.
- **File:Moriya Family Tree - 守矢氏系図.png → SVG** (`files/moriya-family-tree-ja/`): lines as the PNG's runs, 14 vertical
  name columns, ①–⑤ and the note as transcribed `<text>`. Staged in upload/.
- File:Moromi.png: already vectorized on Commons. It is a 200 px render of File:Africa (orthographic projection).svg
  (3.8% of pixels differ, from later border updates in the SVG); recorded rather than redone.
- File:Mouse icon vector.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the body is a stroked rounded shape, but the cable is a freehand curve
- **File:Nagashima Iki.png → SVG** (`files/nagashima-iki/`): the Harushima Iki build with Nagashima (OSM position) in red
  and its label. Staged in upload/.
- File:Nagikama.png: not rebuildable without tracing (freehand outline drawings of three nagikama blades).
- File:Nakano Inugoya dog shelters 1696.png: not rebuildable, a raster original (a scanned woodblock-style illustration
  from a 1928 book).
- **File:Name muhammad in sylheti nagari.png → SVG** (`files/name-muhammad-sylheti-nagari/`): the name in Noto Sans
  Syloti Nagri as `<text>`, IoU 0.96. Staged in upload/.
- File:Nara Toichi-gun.png: not rebuildable without tracing. Unlike Matsuura-gun, the yellow Meiji-era Toichi District
  is a strip that cuts across modern municipalities (parts of Kashihara and Sakurai); no dataset holds Meiji village
  boundaries, so the highlighted area could only be traced.
- File:Naval jack of the United States (1975–1976).png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: the shaded rattlesnake is its own drawing; the vector jacks on Commons (1776–1777, 2002–2019) have different snakes. Using the 2002–2019 SVG's snake would change the design: NEEDS-DECISION (user) if wanted
- File:NaviMumbaiMetro-Logo.png: not rebuildable without tracing. Custom "nmm" lettering and freeform swooshes (only the
  "NAVI MUMBAI METRO" caption could be text); Commons has only other PNGs of the logo.
- File:Nbfr logo.png: removed from the queue; already triaged as NOT REBUILDABLE without tracing: a freehand brush mark (badminton federation logo, 107×51)
- File:Neulicht.Botein.P1162773.png: not rebuildable, a raster original (a photograph of the crescent Moon and Botein).
- **File:New Tai Lue script sample.png → SVG** (`files/new-tai-lue-script-sample/`): ten glyphs identified by matching
  and an eye check (one corrected to vowel sign AY), set as `<text>` in Noto Sans New Tai Lue. Staged in upload/.
- File:NoDVDcover copy.png: not rebuildable, a raster original (a photographed, desaturated DVD case; only the "No cover
  available" overlay is text).
- File:Nonotonoto.png: not rebuildable for now (as Cross of Herat). A Marchen rendering sample with no text in its
  description; brute-force matching of every base + subjoined letter (+ vowel) against Noto Sans Marchen reached only
  IoU 0.77 and none of the top readings looks right by eye: the PNG uses another, blockier font. Guessing would publish
  wrong text; the Unicode text from the uploader would unblock it.
- File:North Texas Stacked Wordmark.png: not rebuildable without tracing. Custom athletic lettering; Commons' University
  of North Texas wordmark.svg is the separate "UNT" mark.
- File:Notifications - Email received - January 2016.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Notifications - Failed Mention - August 2016.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Notifications - First milestone - August 2016.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Notifications - Successful Mention - August 2016.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Notifications - Welcome - January 2016.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- File:Notifications - Wikidata connection.png: removed from the queue; already triaged as NOT REBUILDABLE: a screenshot of the wiki interface (raster original; belongs with 'Likely raster originals')
- **File:O-dot.png → SVG** (`files/o-dot/`): o͘ O͘ as `<text>` in Noto Serif (has U+0358), sized so the dotted capital
  fits the canvas. Staged in upload/.
- **File:Ogham Sample.png → SVG** (`files/ogham-sample/`): the described ENABARR in Noto Sans Ogham, on white. Staged.
- **File:Old Persian mi.png → SVG** (`files/old-persian-mi/`): 𐎷 as `<text>` in Noto Sans Old Persian (solid wedges where
  the PNG outlines them). Staged in upload/.
- 2026-10-19 23:24 — File:Om in Cham script.png → SVG: ꨅꩌ as text in Noto Sans Cham (IoU 0.942); staged in upload/om-cham/.
